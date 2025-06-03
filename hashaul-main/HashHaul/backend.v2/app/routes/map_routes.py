# app/routes/map_routes.py
from flask import Blueprint, request, jsonify, g
from app.models.usuario_model import Usuario
from app.models.viaje_model import Viaje
from app.models.ruta_model import Ruta
from app.models.checkpoint_model import Checkpoint
from app.models.incidente_model import Incidente
from datetime import datetime
from extensions import db
from app.routes.auth_middleware import token_required

map_bp = Blueprint('map', __name__, url_prefix='/api')



@map_bp.route('/conductor/<int:user_id>/viajes/proximos', methods=['GET'])
@token_required
def get_viajes_proximos(user_id):
    try:
       
        print(f" Debug - g object: {dir(g)}")
        print(f" Debug - hasattr current_user: {hasattr(g, 'current_user')}")
        if hasattr(g, 'current_user'):
            print(f" Debug - current_user: {g.current_user}")
        else:
            print(" g.current_user no existe")

        # Verificar headers de la petición
        print(f" Debug - Headers: {dict(request.headers)}")

        # Verificar que g.current_user existe
        if not hasattr(g, 'current_user') or not g.current_user:
            return jsonify({
                'success': False,
                'error': 'Usuario no autenticado'
            }), 401

        # Verificar permisos
        if g.current_user.id != user_id and g.current_user.rol not in ['administrador', 'supervisor']:
            return jsonify({
                'success': False,
                'error': 'No tienes permisos para acceder a estos datos'
            }), 403

       
        viajes = Viaje.query.filter(
            Viaje.usuario_id == user_id,
            Viaje.estado.in_(['pendiente', 'en_curso'])
        ).order_by(Viaje.fecha_registro.desc()).all()

        viajes_data = []
        for viaje in viajes:
            viaje_dict = viaje.to_dict()
            viaje_dict['origen'] = viaje.rutas[0].origen if viaje.rutas else None
            viaje_dict['destino'] = viaje.rutas[0].destino if viaje.rutas else None
            viajes_data.append(viaje_dict)

        return jsonify(viajes_data), 200

    except Exception as e:
        print(f" Error obteniendo viajes próximos: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Error al obtener viajes próximos: {str(e)}'
        }), 500



@map_bp.route('/conductor/<int:user_id>/viajes/historial', methods=['GET'])
@token_required
def get_viajes_historial(user_id):
   
    try:
        
        if not hasattr(g, 'current_user') or not g.current_user:
            return jsonify({
                'success': False,
                'error': 'Usuario no autenticado'
            }), 401

        # Verificar que el usuario actual puede acceder a estos datos
        if g.current_user.id != user_id and g.current_user.rol not in ['administrador', 'supervisor']:
            return jsonify({
                'success': False,
                'error': 'No tienes permisos para acceder a estos datos'
            }), 403

        # Obtener viajes completados del conductor
        viajes = Viaje.query.filter(
            Viaje.usuario_id == user_id,
            Viaje.estado == 'completado'
        ).order_by(Viaje.fecha_fin.desc()).all()

        viajes_data = []
        for viaje in viajes:
            viaje_dict = viaje.to_dict()
            # Agregar información adicional
            viaje_dict['origen'] = viaje.rutas[0].origen if viaje.rutas else None
            viaje_dict['destino'] = viaje.rutas[0].destino if viaje.rutas else None
            viajes_data.append(viaje_dict)

        return jsonify(viajes_data), 200

    except Exception as e:
        print(f" Error obteniendo historial de viajes: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Error al obtener historial de viajes: {str(e)}'
        }), 500


@map_bp.route('/conductor/checkpoints/<int:checkpoint_id>/incidentes', methods=['POST'])
@token_required
def reportar_incidente_checkpoint(checkpoint_id):

    try:
        # Verificar que el checkpoint existe
        checkpoint = Checkpoint.query.get(checkpoint_id)
        if not checkpoint:
            return jsonify({
                'success': False,
                'error': f'No se encontró el checkpoint con ID {checkpoint_id}'
            }), 404

        # Obtener datos del request
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No se enviaron datos'
            }), 400

        # Validar campos requeridos
        descripcion = data.get('descripcion')
        tipo = data.get('tipo')
        gravedad = data.get('gravedad', 'baja')

        if not descripcion or not tipo:
            return jsonify({
                'success': False,
                'error': 'Los campos descripcion y tipo son requeridos'
            }), 400

        # Validar tipos válidos
        tipos_validos = ['accidente', 'mecanico', 'clima', 'trafico', 'otro']
        if tipo not in tipos_validos:
            return jsonify({
                'success': False,
                'error': f'Tipo de incidente inválido. Tipos válidos: {", ".join(tipos_validos)}'
            }), 400

        # Validar gravedad válida
        gravedades_validas = ['baja', 'media', 'alta', 'critica']
        if gravedad not in gravedades_validas:
            return jsonify({
                'success': False,
                'error': f'Gravedad inválida. Gravedades válidas: {", ".join(gravedades_validas)}'
            }), 400

        # Crear el incidente
        nuevo_incidente = Incidente(
            descripcion=descripcion,
            tipo=tipo,
            gravedad=gravedad,
            checkpoint_id=checkpoint_id,
            usuario_id=g.current_user.id,
            timestamp=datetime.utcnow(),
            resuelto=False
        )

        db.session.add(nuevo_incidente)
        db.session.commit()

        return jsonify({
            'success': True,
            'data': nuevo_incidente.to_dict(),
            'message': 'Incidente reportado exitosamente'
        }), 201

    except Exception as e:
        db.session.rollback()
        print(f" Error reportando incidente: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Error al reportar el incidente: {str(e)}'
        }), 500




@map_bp.route('/admin/rutas', methods=['GET'])
@token_required
def get_all_rutas():
   
    try:
        # Verificar permisos de administrador
        if g.current_user.rol not in ['administrador', 'supervisor']:
            return jsonify({
                'success': False,
                'error': 'No tienes permisos de administrador'
            }), 403

        # Obtener todas las rutas
        rutas = Ruta.query.order_by(Ruta.fecha_registro.desc()).all()

        rutas_data = []
        for ruta in rutas:
            ruta_dict = ruta.to_dict()
            # Agregar información adicional del viaje
            if ruta.viaje:
                ruta_dict['viaje_codigo'] = ruta.viaje.codigo
                ruta_dict['viaje_estado'] = ruta.viaje.estado
                ruta_dict['conductor_nombre'] = ruta.viaje.conductor.nombre if ruta.viaje.conductor else None
            # Agregar información de si la ruta está activa
            ruta_dict['activa'] = ruta.viaje.estado in ['pendiente', 'en_curso'] if ruta.viaje else False
            # Mapear campos para compatibilidad con el frontend
            ruta_dict['distancia_total'] = ruta.distancia_km
            ruta_dict['tiempo_estimado'] = ruta.tiempo_estimado_hrs * 60 if ruta.tiempo_estimado_hrs else None  # Convertir a minutos
            rutas_data.append(ruta_dict)

        return jsonify(rutas_data), 200

    except Exception as e:
        print(f"❌ Error obteniendo rutas: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Error al obtener rutas: {str(e)}'
        }), 500


@map_bp.route('/admin/checkpoints', methods=['GET'])
@token_required
def get_all_checkpoints():
   
    try:
       
        if g.current_user.rol not in ['administrador', 'supervisor']:
            return jsonify({
                'success': False,
                'error': 'No tienes permisos de administrador'
            }), 403

     
        checkpoints = Checkpoint.query.order_by(Checkpoint.ruta_id, Checkpoint.orden).all()

        checkpoints_data = []
        for checkpoint in checkpoints:
            checkpoint_dict = checkpoint.to_dict()
         
            checkpoint_dict['hash_local'] = checkpoint.hash
            checkpoint_dict['tiempo_estimado_llegada'] = None  
            checkpoint_dict['tiempo_real_llegada'] = checkpoint.timestamp_alcanzado
     
            if checkpoint.estado == 'alcanzado':
                checkpoint_dict['estado'] = 'completado'
            elif checkpoint.estado == 'pendiente':
                checkpoint_dict['estado'] = 'pendiente'
            elif checkpoint.estado == 'saltado':
                checkpoint_dict['estado'] = 'saltado'
            
            checkpoints_data.append(checkpoint_dict)

        return jsonify(checkpoints_data), 200

    except Exception as e:
        print(f" Error obteniendo checkpoints: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Error al obtener checkpoints: {str(e)}'
        }), 500


@map_bp.route('/admin/checkpoints/<int:checkpoint_id>', methods=['PUT'])
@token_required
def update_checkpoint(checkpoint_id):
    """
    Actualiza un checkpoint específico
    """
    try:
        print(f"🔍 UPDATE CHECKPOINT - ID: {checkpoint_id}")
        print(f"🔍 Usuario actual: {g.current_user}")
        print(f"🔍 Usuario ID: {g.current_user.id}")
        print(f"🔍 Usuario rol: {g.current_user.rol}")
        
        # Verificar que el checkpoint existe
        checkpoint = Checkpoint.query.get(checkpoint_id)
        if not checkpoint:
            return jsonify({
                'success': False,
                'error': f'No se encontró el checkpoint con ID {checkpoint_id}'
            }), 404

        print(f"🔍 Checkpoint encontrado: {checkpoint.id}")
        print(f"🔍 Checkpoint ruta_id: {checkpoint.ruta_id}")
        
        # Obtener información de la ruta y viaje
        ruta = checkpoint.ruta
        viaje = ruta.viaje if ruta else None
        
        print(f"🔍 Ruta: {ruta}")
        print(f"🔍 Viaje: {viaje}")
        if viaje:
            print(f"🔍 Viaje ID: {viaje.id}")
            print(f"🔍 Viaje usuario_id: {viaje.usuario_id}")
            print(f"🔍 ¿Es el conductor del viaje?: {viaje.usuario_id == g.current_user.id}")
        
        # Debug de la condición de permisos
        es_admin = g.current_user.rol in ['administrador', 'supervisor']
        es_conductor_del_viaje = viaje and viaje.usuario_id == g.current_user.id
        
        print(f"🔍 ¿Es admin/supervisor?: {es_admin}")
        print(f"🔍 ¿Es conductor del viaje?: {es_conductor_del_viaje}")
        print(f"🔍 ¿Tiene permisos?: {es_admin or es_conductor_del_viaje}")
        
        # Verificar permisos
        if not es_admin and not es_conductor_del_viaje:
            print("❌ ACCESO DENEGADO - No tiene permisos")
            return jsonify({
                'success': False,
                'error': f'No tienes permisos para actualizar este checkpoint. Rol: {g.current_user.rol}, Usuario ID: {g.current_user.id}, Viaje Usuario: {viaje.usuario_id if viaje else "N/A"}'
            }), 403

        print("✅ PERMISOS VERIFICADOS - Continuando con la actualización")
        
        # Obtener datos del request
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No se enviaron datos para actualizar'
            }), 400

        print(f"🔍 Datos recibidos: {data}")
        
        # Actualizar el estado del checkpoint
        if 'estado' in data:
            estado = data['estado']
            print(f"🔍 Actualizando estado a: {estado}")
            
            if estado == 'completado':
                checkpoint.estado = 'alcanzado'
                checkpoint.timestamp_alcanzado = datetime.utcnow()
            elif estado == 'pendiente':
                checkpoint.estado = 'pendiente'
                checkpoint.timestamp_alcanzado = None
            elif estado == 'saltado':
                checkpoint.estado = 'saltado'
                checkpoint.timestamp_alcanzado = datetime.utcnow()

        if 'tiempo_real_llegada' in data and data['tiempo_real_llegada']:
            try:
                checkpoint.timestamp_alcanzado = datetime.fromisoformat(data['tiempo_real_llegada'].replace('Z', '+00:00'))
            except ValueError:
                checkpoint.timestamp_alcanzado = datetime.utcnow()

        # Guardar cambios
        db.session.commit()
        print("✅ Checkpoint actualizado exitosamente")

        # Preparar respuesta
        checkpoint_dict = checkpoint.to_dict()
        checkpoint_dict['hash_local'] = checkpoint.hash
        checkpoint_dict['tiempo_real_llegada'] = checkpoint.timestamp_alcanzado
        if checkpoint.estado == 'alcanzado':
            checkpoint_dict['estado'] = 'completado'

        return jsonify({
            'success': True,
            'data': checkpoint_dict,
            'message': 'Checkpoint actualizado exitosamente'
        }), 200

    except Exception as e:
        db.session.rollback()
        print(f"❌ Error actualizando checkpoint: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Error al actualizar el checkpoint: {str(e)}'
        }), 500

@map_bp.route('/admin/checkpoints/<int:checkpoint_id>', methods=['GET'])
@token_required
def get_checkpoint_detail(checkpoint_id):
   
    try:
        checkpoint = Checkpoint.query.get(checkpoint_id)
        if not checkpoint:
            return jsonify({
                'success': False,
                'error': f'No se encontró el checkpoint con ID {checkpoint_id}'
            }), 404

        ruta = checkpoint.ruta
        viaje = ruta.viaje if ruta else None
        
        if (g.current_user.rol not in ['administrador', 'supervisor'] and 
            (not viaje or viaje.usuario_id != g.current_user.id)):
            return jsonify({
                'success': False,
                'error': 'No tienes permisos para ver este checkpoint'
            }), 403

        checkpoint_dict = checkpoint.to_dict()
     
        checkpoint_dict['hash_local'] = checkpoint.hash
        checkpoint_dict['tiempo_real_llegada'] = checkpoint.timestamp_alcanzado
        if checkpoint.estado == 'alcanzado':
            checkpoint_dict['estado'] = 'completado'

   
        checkpoint_dict['incidentes'] = [inc.to_dict() for inc in checkpoint.incidentes]

        return jsonify({
            'success': True,
            'data': checkpoint_dict
        }), 200

    except Exception as e:
        print(f" Error obteniendo detalle del checkpoint: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Error al obtener detalle del checkpoint: {str(e)}'
        }), 500




@map_bp.route('/rutas/<int:ruta_id>/checkpoints', methods=['GET'])
@token_required
def get_checkpoints_by_ruta(ruta_id):
    
    try:
      
        ruta = Ruta.query.get(ruta_id)
        if not ruta:
            return jsonify({
                'success': False,
                'error': f'No se encontró la ruta con ID {ruta_id}'
            }), 404

  
        viaje = ruta.viaje
        if (g.current_user.rol not in ['administrador', 'supervisor'] and 
            (not viaje or viaje.usuario_id != g.current_user.id)):
            return jsonify({
                'success': False,
                'error': 'No tienes permisos para ver esta ruta'
            }), 403

    
        checkpoints = Checkpoint.query.filter_by(ruta_id=ruta_id).order_by(Checkpoint.orden).all()

        checkpoints_data = []
        for checkpoint in checkpoints:
            checkpoint_dict = checkpoint.to_dict()
          
            checkpoint_dict['hash_local'] = checkpoint.hash
            checkpoint_dict['tiempo_real_llegada'] = checkpoint.timestamp_alcanzado
            if checkpoint.estado == 'alcanzado':
                checkpoint_dict['estado'] = 'completado'
            checkpoints_data.append(checkpoint_dict)

        return jsonify(checkpoints_data), 200

    except Exception as e:
        print(f" Error obteniendo checkpoints de la ruta: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Error al obtener checkpoints de la ruta: {str(e)}'
        }), 500


@map_bp.route('/incidentes', methods=['GET'])
@token_required
def get_incidentes_map():
    
    try:
   
        checkpoint_id = request.args.get('checkpoint_id')
        ruta_id = request.args.get('ruta_id')
        solo_no_resueltos = request.args.get('solo_no_resueltos', 'false').lower() == 'true'

   
        query = Incidente.query

        if checkpoint_id:
            query = query.filter_by(checkpoint_id=checkpoint_id)
        
        if ruta_id:
           
            checkpoints_ids = [cp.id for cp in Checkpoint.query.filter_by(ruta_id=ruta_id).all()]
            query = query.filter(Incidente.checkpoint_id.in_(checkpoints_ids))

        if solo_no_resueltos:
            query = query.filter_by(resuelto=False)

        if g.current_user.rol not in ['administrador', 'supervisor']:
            query = query.filter_by(usuario_id=g.current_user.id)

        incidentes = query.order_by(Incidente.timestamp.desc()).all()
        incidentes_data = [inc.to_dict() for inc in incidentes]

        return jsonify(incidentes_data), 200

    except Exception as e:
        print(f"❌ Error obteniendo incidentes: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Error al obtener incidentes: {str(e)}'
        }), 500
    
@map_bp.route('/conductor/<int:user_id>/rutas', methods=['GET'])
@token_required
def get_conductor_rutas(user_id):
    
    try:
        # Verificamos autenticación y permisos
        if not hasattr(g, 'current_user') or not g.current_user:
            return jsonify({'success': False, 'error': 'Usuario no autenticado'}), 401

        if g.current_user.id != user_id and g.current_user.rol not in ['administrador', 'supervisor']:
            return jsonify({'success': False, 'error': 'No tienes permisos para acceder a estos datos'}), 403

        # Obtenemos todos los viajes del conductor (activos e históricos)
        viajes = Viaje.query.filter(
            Viaje.usuario_id == user_id
        ).all()

        # Extraemos todas las rutas de estos viajes
        rutas_data = []
        for viaje in viajes:
            for ruta in viaje.rutas:
                ruta_dict = ruta.to_dict()
                # Agregamos información del viaje
                ruta_dict['viaje_codigo'] = viaje.codigo
                ruta_dict['viaje_estado'] = viaje.estado
                ruta_dict['viaje_id'] = viaje.id
                
                # Determinamos si la ruta está activa
                ruta_dict['activa'] = viaje.estado in ['pendiente', 'en_curso']
                
                # Agregamos información adicional de la ruta
                ruta_dict['distancia_total'] = ruta.distancia_km
                ruta_dict['tiempo_estimado'] = ruta.tiempo_estimado_hrs * 60 if ruta.tiempo_estimado_hrs else None
                
                rutas_data.append(ruta_dict)

        # Ordenamos por fecha de registro descendente
        rutas_data.sort(key=lambda x: x.get('fecha_registro', ''), reverse=True)

        return jsonify(rutas_data), 200

    except Exception as e:
        return jsonify({'success': False, 'error': f'Error al obtener rutas del conductor: {str(e)}'}), 500
    


@map_bp.route('/conductor/checkpoints/<int:checkpoint_id>/completar', methods=['PUT'])
@token_required
def marcar_checkpoint_completado(checkpoint_id):
   
    try:
        print(f" MARCAR CHECKPOINT COMPLETADO - ID: {checkpoint_id}")
        print(f" Usuario: {g.current_user.id} - {g.current_user.rol}")
        
        
        checkpoint = Checkpoint.query.get(checkpoint_id)
        if not checkpoint:
            return jsonify({
                'success': False,
                'error': f'No se encontró el checkpoint con ID {checkpoint_id}'
            }), 404

        print(f"Checkpoint encontrado: {checkpoint.id} - Estado actual: {checkpoint.estado}")
        
        # Obtener datos del request
        data = request.get_json()
        if not data:
            data = {}  # Permitir request vacío
        
        print(f" Datos recibidos: {data}")
        
        # Actualizar el checkpoint a completado
        checkpoint.estado = 'alcanzado'
        checkpoint.timestamp_alcanzado = datetime.utcnow()
        
        # Si se proporciona un tiempo específico, usarlo
        if 'tiempo_real_llegada' in data and data['tiempo_real_llegada']:
            try:
                checkpoint.timestamp_alcanzado = datetime.fromisoformat(
                    data['tiempo_real_llegada'].replace('Z', '+00:00')
                )
            except ValueError:
                # Si hay error en el formato, usar tiempo actual
                checkpoint.timestamp_alcanzado = datetime.utcnow()

        # Guardar cambios
        db.session.commit()
        print(f" Checkpoint {checkpoint_id} marcado como completado por usuario {g.current_user.id}")

        # Preparar respuesta
        checkpoint_dict = checkpoint.to_dict()
        checkpoint_dict['hash_local'] = checkpoint.hash
        checkpoint_dict['tiempo_real_llegada'] = checkpoint.timestamp_alcanzado
        checkpoint_dict['estado'] = 'completado'  # Para el frontend

        return jsonify({
            'success': True,
            'data': checkpoint_dict,
            'message': 'Checkpoint marcado como completado exitosamente'
        }), 200

    except Exception as e:
        db.session.rollback()
        print(f" Error marcando checkpoint como completado: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Error al marcar checkpoint como completado: {str(e)}'
        }), 500