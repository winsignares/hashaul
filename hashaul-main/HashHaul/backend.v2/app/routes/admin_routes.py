
from flask import Blueprint, request, jsonify
from app.models.usuario_model import Usuario
from app.models.camion_model import Camion  
from app.models.viaje_model import Viaje
from app.models.ruta_model import Ruta
from app.models.checkpoint_model import Checkpoint
from app.models.incidente_model import Incidente
from datetime import datetime
from app.routes.auth_routes import token_required
from extensions import db
from functools import wraps

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

def admin_required(f):
    
    @wraps(f)
    @token_required
    def decorated(current_user, *args, **kwargs):
        print(f" Admin check - Usuario: {current_user.nombre}, Rol: {current_user.rol}")
        if current_user.rol not in ['administrador', 'supervisor', 'admin']:
            return jsonify({'error': 'Permisos insuficientes'}), 403
        return f(current_user, *args, **kwargs)
    return decorated


@admin_bp.route('/usuarios', methods=['GET'])
@admin_required
def get_usuarios(current_user):
    
    print(" GET /usuarios - Listando usuarios")
    try:
        usuarios = Usuario.query.all()
        return jsonify([{
            'id': u.id,
            'nombre': u.nombre,
            'correo': u.correo,
            'telefono': u.telefono,
            'rol': u.rol,
            'activo': u.activo,
            'fecha_registro': u.fecha_registro.isoformat() if u.fecha_registro else None
        } for u in usuarios]), 200
    except Exception as e:
        print(f" Error en get_usuarios: {str(e)}")
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/usuarios', methods=['POST'])
@admin_required
def create_usuario(current_user):
   
    print(" POST /usuarios - Creando usuario")
    try:
        data = request.get_json()
        print(f" Datos recibidos: {data}")
        
        if Usuario.query.filter_by(correo=data.get('correo')).first():
            return jsonify({'error': 'El correo ya está registrado'}), 409
        
        nuevo_usuario = Usuario(
            nombre=data.get('nombre'),
            correo=data.get('correo'),
            telefono=data.get('telefono'),
            rol=data.get('rol', 'conductor')
        )
        nuevo_usuario.set_password(data.get('contraseña'))
        
        db.session.add(nuevo_usuario)
        db.session.commit()
        print(" Usuario creado exitosamente")
        
        return jsonify({
            'mensaje': 'Usuario creado exitosamente',
            'id': nuevo_usuario.id
        }), 201
    except Exception as e:
        print(f" Error creando usuario: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/usuarios/<int:id>', methods=['GET'])
@admin_required
def get_usuario_by_id(current_user, id):
    """Obtener usuario por ID"""
    print(f" GET /usuarios/{id} - Obteniendo usuario específico")
    try:
        usuario = Usuario.query.get_or_404(id)
        return jsonify({
            'id': usuario.id,
            'nombre': usuario.nombre,
            'correo': usuario.correo,
            'telefono': usuario.telefono,
            'rol': usuario.rol,
            'activo': usuario.activo,
            'fecha_registro': usuario.fecha_registro.isoformat() if usuario.fecha_registro else None
        }), 200
    except Exception as e:
        print(f" Error en get_usuario: {str(e)}")
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/usuarios/<int:id>', methods=['PUT'])
@admin_required
def update_usuario(current_user, id):
    """Actualizar usuario"""
    print(f" PUT /usuarios/{id} - Actualizando usuario")
    try:
        usuario = Usuario.query.get_or_404(id)
        data = request.get_json()
        print(f" Datos para actualizar: {data}")
        
        if 'nombre' in data:
            usuario.nombre = data['nombre']
        if 'telefono' in data:
            usuario.telefono = data['telefono']
        if 'rol' in data:
            usuario.rol = data['rol']
        if 'contraseña' in data and data['contraseña']:
            usuario.set_password(data['contraseña'])
        
        db.session.commit()
        print(" Usuario actualizado exitosamente")
        return jsonify({'mensaje': 'Usuario actualizado exitosamente'}), 200
    except Exception as e:
        print(f" Error actualizando usuario: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/usuarios/<int:id>', methods=['DELETE'])
@admin_required
def delete_usuario(current_user, id):
   
    print(f" DELETE /usuarios/{id} - Eliminando usuario")
    try:
        usuario = Usuario.query.get_or_404(id)
        print(f" Usuario encontrado: {usuario.nombre}")
        
        if usuario.id == current_user.id:
            return jsonify({'error': 'No puedes eliminar tu propio usuario'}), 400
        
        db.session.delete(usuario)
        db.session.commit()
        print(" Usuario eliminado exitosamente")
        return jsonify({'mensaje': 'Usuario eliminado exitosamente'}), 200
    except Exception as e:
        print(f" Error eliminando usuario: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/camiones', methods=['GET'])
@admin_required
def get_camiones(current_user):
    """Obtener lista de camiones"""
    print(" GET /camiones - Listando camiones")
    try:
        camiones = Camion.query.all()
        return jsonify([{
            'id': c.id,
            'placa': c.placa,
            'modelo': c.modelo,
            'marca': c.marca,
            'año': c.año,
            'capacidad_kg': c.capacidad_kg,
        } for c in camiones]), 200
    except Exception as e:
        print(f" Error en get_camiones: {str(e)}")
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/camiones', methods=['POST'])
@admin_required
def create_camion(current_user):
    """Crear nuevo camión"""
    print(" POST /camiones - Creando camión")
    try:
        data = request.get_json()
        print(f" Datos recibidos: {data}")
        
        placa = data.get('placa')
        modelo = data.get('modelo')
        marca = data.get('marca')
        año = data.get('año')
        capacidad_kg = data.get('capacidad_kg')

        if not placa or not modelo or not marca or not año or not capacidad_kg:
            return jsonify({'error': 'Faltan campos obligatorios'}), 400
        
        if Camion.query.filter_by(placa=placa).first():
            return jsonify({'error': 'Ya existe un camión con esa placa'}), 409

        try:
            capacidad_kg = float(capacidad_kg)
        except ValueError:
            return jsonify({'error': 'capacidad_kg debe ser un número'}), 400
        
        nuevo_camion = Camion(
            placa=placa,
            modelo=modelo,
            marca=marca,
            año=año,
            capacidad_kg=capacidad_kg
        )
        db.session.add(nuevo_camion)
        db.session.commit()
        print(" Camión creado exitosamente")

        return jsonify({
            'mensaje': 'Camión creado exitosamente',
            'camion': {
                'id': nuevo_camion.id,
                'placa': nuevo_camion.placa,
                'modelo': nuevo_camion.modelo,
                'marca': nuevo_camion.marca,
                'año': nuevo_camion.año,
                'capacidad_kg': nuevo_camion.capacidad_kg
            }
        }), 201

    except Exception as e:
        print(f" Error creando camión: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/camiones/<int:id>', methods=['GET'])
@admin_required
def get_camion_by_id(current_user, id):
  
    print(f" GET /camiones/{id} - Obteniendo camión específico")
    try:
        camion = Camion.query.get_or_404(id)
        return jsonify({
            'id': camion.id,
            'placa': camion.placa,
            'modelo': camion.modelo,
            'marca': camion.marca,
            'año': camion.año,
            'capacidad_kg': camion.capacidad_kg,
        }), 200
    except Exception as e:
        print(f" Error en get_camion: {str(e)}")
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/camiones/<int:id>', methods=['PUT'])
@admin_required
def update_camion(current_user, id):

    print(f" PUT /camiones/{id} - Actualizando camión")
    try:
        camion = Camion.query.get_or_404(id)
        data = request.get_json()
        print(f" Datos para actualizar: {data}")
        
        if 'placa' in data:
            existing = Camion.query.filter_by(placa=data['placa']).first()
            if existing and existing.id != camion.id:
                return jsonify({'error': 'Ya existe un camión con esa placa'}), 409
            camion.placa = data['placa']
        if 'modelo' in data:
            camion.modelo = data['modelo']
        if 'marca' in data:
            camion.marca = data['marca']
        if 'año' in data:
            camion.año = data['año']
        if 'capacidad_kg' in data:
            camion.capacidad_kg = float(data['capacidad_kg'])
        
        db.session.commit()
        print(" Camión actualizado exitosamente")
        return jsonify({'mensaje': 'Camión actualizado exitosamente'}), 200
    except Exception as e:
        print(f" Error actualizando camión: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/camiones/<int:id>', methods=['DELETE'])
@admin_required
def delete_camion(current_user, id):
   
    print(f" DELETE /camiones/{id} - Eliminando camión")
    try:
        camion = Camion.query.get_or_404(id)
        print(f" Camión encontrado: {camion.placa}")
        
        db.session.delete(camion)
        db.session.commit()
        print(" Camión eliminado exitosamente")
        return jsonify({'mensaje': 'Camión eliminado exitosamente'}), 200
    except Exception as e:
        print(f" Error eliminando camión: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/viajes', methods=['GET'])
@admin_required
def get_viajes(current_user):
    print(" GET /viajes - Listando viajes")
    try:
        viajes = Viaje.query.all()
        return jsonify([v.to_dict() for v in viajes]), 200
    except Exception as e:
        print(f" Error en get_viajes: {str(e)}")
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/viajes', methods=['POST'])
@admin_required
def create_viaje(current_user):
    print(" POST /viajes - Creando viaje")
    try:
        data = request.get_json()
        print(f" Datos recibidos: {data}")

        codigo = data.get('codigo')
        estado = data.get('estado', 'pendiente')
        fecha_inicio_str = data.get('fecha_inicio')
        fecha_fin_str = data.get('fecha_fin')
        observaciones = data.get('observaciones')
        usuario_id = data.get('usuario_id')
        camion_id = data.get('camion_id')

        if not codigo or not usuario_id or not camion_id:
            return jsonify({'error': 'Faltan campos obligatorios: codigo, usuario_id o camion_id'}), 400

        if Viaje.query.filter_by(codigo=codigo).first():
            return jsonify({'error': 'El código del viaje ya existe'}), 409

        usuario = Usuario.query.get(usuario_id)
        if not usuario:
            return jsonify({'error': 'Usuario no encontrado'}), 404

        camion = Camion.query.get(camion_id)
        if not camion:
            return jsonify({'error': 'Camión no encontrado'}), 404

        fecha_inicio = None
        fecha_fin = None

        if fecha_inicio_str:
            try:
                fecha_inicio = datetime.fromisoformat(fecha_inicio_str)
            except ValueError:
                return jsonify({'error': 'fecha_inicio debe estar en formato ISO'}), 400

        if fecha_fin_str:
            try:
                fecha_fin = datetime.fromisoformat(fecha_fin_str)
            except ValueError:
                return jsonify({'error': 'fecha_fin debe estar en formato ISO'}), 400

        nuevo_viaje = Viaje(
            codigo=codigo,
            estado=estado,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            observaciones=observaciones,
            usuario_id=usuario_id,
            camion_id=camion_id
        )

        db.session.add(nuevo_viaje)
        db.session.commit()
        print(" Viaje creado exitosamente")

        return jsonify({
            'mensaje': 'Viaje creado exitosamente',
            'viaje': nuevo_viaje.to_dict()
        }), 201

    except Exception as e:
        print(f" Error creando viaje: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/viajes/<int:id>', methods=['GET'])
@admin_required
def get_viaje_by_id(current_user, id):
 
    print(f" GET /viajes/{id} - Obteniendo viaje específico")
    try:
        viaje = Viaje.query.get_or_404(id)
        return jsonify(viaje.to_dict()), 200
    except Exception as e:
        print(f" Error en get_viaje: {str(e)}")
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/viajes/<int:id>', methods=['PUT'])
@admin_required
def update_viaje(current_user, id):
    
    print(f" PUT /viajes/{id} - Actualizando viaje")
    try:
        viaje = Viaje.query.get_or_404(id)
        data = request.get_json()
        print(f" Datos para actualizar: {data}")
        
        if 'codigo' in data:
            existing = Viaje.query.filter_by(codigo=data['codigo']).first()
            if existing and existing.id != viaje.id:
                return jsonify({'error': 'El código del viaje ya existe'}), 409
            viaje.codigo = data['codigo']
        
        if 'estado' in data:
            viaje.estado = data['estado']
        if 'observaciones' in data:
            viaje.observaciones = data['observaciones']
        if 'usuario_id' in data:
            if not Usuario.query.get(data['usuario_id']):
                return jsonify({'error': 'Usuario no encontrado'}), 404
            viaje.usuario_id = data['usuario_id']
        if 'camion_id' in data:
            if not Camion.query.get(data['camion_id']):
                return jsonify({'error': 'Camión no encontrado'}), 404
            viaje.camion_id = data['camion_id']
        
        if 'fecha_inicio' in data and data['fecha_inicio']:
            try:
                viaje.fecha_inicio = datetime.fromisoformat(data['fecha_inicio'])
            except ValueError:
                return jsonify({'error': 'fecha_inicio debe estar en formato ISO'}), 400
        
        if 'fecha_fin' in data and data['fecha_fin']:
            try:
                viaje.fecha_fin = datetime.fromisoformat(data['fecha_fin'])
            except ValueError:
                return jsonify({'error': 'fecha_fin debe estar en formato ISO'}), 400
        
        db.session.commit()
        print(" Viaje actualizado exitosamente")
        return jsonify({'mensaje': 'Viaje actualizado exitosamente'}), 200
    except Exception as e:
        print(f" Error actualizando viaje: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/viajes/<int:id>', methods=['DELETE'])
@admin_required
def delete_viaje(current_user, id):
    
    print(f" DELETE /viajes/{id} - Eliminando viaje")
    try:
        viaje = Viaje.query.get_or_404(id)
        print(f" Viaje encontrado: {viaje.codigo}")
        
        db.session.delete(viaje)
        db.session.commit()
        print(" Viaje eliminado exitosamente")
        return jsonify({'mensaje': 'Viaje eliminado exitosamente'}), 200
    except Exception as e:
        print(f" Error eliminando viaje: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/rutas', methods=['GET'])
@admin_required
def get_rutas(current_user):
    
    try:
        rutas = Ruta.query.all()
        return jsonify([ruta.to_dict() for ruta in rutas]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/rutas/<int:id>', methods=['GET'])
@admin_required
def get_ruta(current_user, id):
   
    try:
        ruta = Ruta.query.get_or_404(id)
        return jsonify(ruta.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/rutas', methods=['POST'])
@admin_required
def create_ruta(current_user):
    
    try:
        data = request.get_json()

        nombre = data.get('nombre')
        origen = data.get('origen')
        destino = data.get('destino')
        distancia_km = data.get('distancia_km')
        tiempo_estimado_hrs = data.get('tiempo_estimado_hrs')
        viaje_id = data.get('viaje_id')
        checkpoints_data = data.get('checkpoints', [])  

        if not nombre or not origen or not destino or not viaje_id:
            return jsonify({'error': 'Faltan campos obligatorios: nombre, origen, destino, viaje_id'}), 400
        
        
        viaje = Viaje.query.get(viaje_id)
        if not viaje:
            return jsonify({'error': 'Viaje no encontrado'}), 404

        nueva_ruta = Ruta(
            nombre=nombre,
            origen=origen,
            destino=destino,
            distancia_km=distancia_km,
            tiempo_estimado_hrs=tiempo_estimado_hrs,
            viaje_id=viaje_id
        )
        
        db.session.add(nueva_ruta)
        db.session.flush() 

        for idx, cp_data in enumerate(checkpoints_data):
            cp = Checkpoint(
                nombre=cp_data.get('nombre'),
                direccion=cp_data.get('direccion'),
                orden=idx + 1,
                ruta_id=nueva_ruta.id
            )
            db.session.add(cp)

        db.session.commit()

        return jsonify({
            'mensaje': 'Ruta creada exitosamente',
            'ruta': nueva_ruta.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/rutas/<int:id>', methods=['PUT'])
@admin_required
def update_ruta(current_user, id):
    """Actualizar ruta"""
    try:
        ruta = Ruta.query.get_or_404(id)
        data = request.get_json()
        
        if 'nombre' in data:
            ruta.nombre = data['nombre']
        if 'origen' in data:
            ruta.origen = data['origen']
        if 'destino' in data:
            ruta.destino = data['destino']
        if 'distancia_km' in data:
            ruta.distancia_km = data['distancia_km']
        if 'tiempo_estimado_hrs' in data:
            ruta.tiempo_estimado_hrs = data['tiempo_estimado_hrs']
        if 'viaje_id' in data:
            if not Viaje.query.get(data['viaje_id']):
                return jsonify({'error': 'Viaje no encontrado'}), 404
            ruta.viaje_id = data['viaje_id']
        
        db.session.commit()
        return jsonify({'mensaje': 'Ruta actualizada exitosamente'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/rutas/<int:id>', methods=['DELETE'])
@admin_required
def delete_ruta(current_user, id):
   
    try:
        ruta = Ruta.query.get_or_404(id)
        db.session.delete(ruta)
        db.session.commit()
        return jsonify({'mensaje': 'Ruta eliminada exitosamente'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/checkpoints', methods=['GET'])
@admin_required
def get_checkpoints(current_user):
    ruta_id = request.args.get('ruta_id')
    try:
        if ruta_id:
            checkpoints = Checkpoint.query.filter_by(ruta_id=ruta_id).order_by(Checkpoint.orden).all()
        else:
            checkpoints = Checkpoint.query.order_by(Checkpoint.ruta_id, Checkpoint.orden).all()
        return jsonify([cp.to_dict() for cp in checkpoints]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/checkpoints/<int:checkpoint_id>', methods=['GET'])
@admin_required
def get_checkpoint_by_id(current_user, checkpoint_id):
    try:
        cp = Checkpoint.query.get_or_404(checkpoint_id)
        return jsonify(cp.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/checkpoints', methods=['POST'])
@admin_required
def create_checkpoint(current_user):
    try:
        data = request.get_json()

        direccion = data.get('direccion')
        latitud = data.get('latitud')
        longitud = data.get('longitud')
        estado = data.get('estado', 'pendiente')
        hash_val = data.get('hash')
        blockchain_tx_hash = data.get('blockchain_tx_hash', None)
        orden = data.get('orden')
        ruta_id = data.get('ruta_id')

       
        if not direccion or latitud is None or longitud is None or not hash_val or orden is None or not ruta_id:
            return jsonify({'error': 'Faltan campos obligatorios: direccion, latitud, longitud, hash, orden, ruta_id'}), 400

        ruta = Ruta.query.get(ruta_id)
        if not ruta:
            return jsonify({'error': 'Ruta no encontrada'}), 404

        nuevo_cp = Checkpoint(
            direccion=direccion,
            latitud=latitud,
            longitud=longitud,
            estado=estado,
            hash=hash_val,
            blockchain_tx_hash=blockchain_tx_hash,
            orden=orden,
            ruta_id=ruta_id
        )

        db.session.add(nuevo_cp)
        db.session.commit()

        return jsonify({'mensaje': 'Checkpoint creado', 'checkpoint': nuevo_cp.to_dict()}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/checkpoints/<int:checkpoint_id>', methods=['PUT'])
@admin_required
def update_checkpoint(current_user, checkpoint_id):
    """Actualizar checkpoint"""
    try:
        checkpoint = Checkpoint.query.get_or_404(checkpoint_id)
        data = request.get_json()
        
        if 'direccion' in data:
            checkpoint.direccion = data['direccion']
        if 'latitud' in data:
            checkpoint.latitud = data['latitud']
        if 'longitud' in data:
            checkpoint.longitud = data['longitud']
        if 'estado' in data:
            checkpoint.estado = data['estado']
        if 'hash' in data:
            checkpoint.hash = data['hash']
        if 'blockchain_tx_hash' in data:
            checkpoint.blockchain_tx_hash = data['blockchain_tx_hash']
        if 'orden' in data:
            checkpoint.orden = data['orden']
        if 'ruta_id' in data:
            if not Ruta.query.get(data['ruta_id']):
                return jsonify({'error': 'Ruta no encontrada'}), 404
            checkpoint.ruta_id = data['ruta_id']
        
        db.session.commit()
        return jsonify({'mensaje': 'Checkpoint actualizado exitosamente'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/checkpoints/<int:checkpoint_id>', methods=['DELETE'])
@admin_required
def delete_checkpoint(current_user, checkpoint_id):
    """Eliminar checkpoint"""
    try:
        checkpoint = Checkpoint.query.get_or_404(checkpoint_id)
        db.session.delete(checkpoint)
        db.session.commit()
        return jsonify({'mensaje': 'Checkpoint eliminado exitosamente'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/incidentes', methods=['GET'])
@admin_required
def get_incidentes(current_user):
    checkpoint_id = request.args.get('checkpoint_id')
    try:
        if checkpoint_id:
            incidentes = Incidente.query.filter_by(checkpoint_id=checkpoint_id).order_by(Incidente.timestamp.desc()).all()
        else:
            incidentes = Incidente.query.order_by(Incidente.timestamp.desc()).all()
        return jsonify([inc.to_dict() for inc in incidentes]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/incidentes/<int:incidente_id>', methods=['GET'])
@admin_required
def get_incidente_by_id(current_user, incidente_id):
    try:
        incidente = Incidente.query.get_or_404(incidente_id)
        return jsonify(incidente.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/incidentes', methods=['POST'])
@admin_required
def create_incidente(current_user):
    try:
        data = request.get_json()

        descripcion = data.get('descripcion')
        tipo = data.get('tipo')
        gravedad = data.get('gravedad', 'baja')
        resuelto = data.get('resuelto', False)
        checkpoint_id = data.get('checkpoint_id')
        usuario_id = data.get('usuario_id', None)

  
        if not descripcion or not tipo or not checkpoint_id:
            return jsonify({'error': 'Faltan campos obligatorios: descripcion, tipo, checkpoint_id'}), 400

       
        checkpoint = Checkpoint.query.get(checkpoint_id)
        if not checkpoint:
            return jsonify({'error': 'Checkpoint no encontrado'}), 404

        
        if usuario_id:
            usuario = Usuario.query.get(usuario_id)
            if not usuario:
                return jsonify({'error': 'Usuario no encontrado'}), 404

        nuevo_incidente = Incidente(
            descripcion=descripcion,
            tipo=tipo,
            gravedad=gravedad,
            resuelto=resuelto,
            checkpoint_id=checkpoint_id,
            usuario_id=usuario_id
        )

        db.session.add(nuevo_incidente)
        db.session.commit()

        return jsonify({'mensaje': 'Incidente creado', 'incidente': nuevo_incidente.to_dict()}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/incidentes/<int:incidente_id>', methods=['PUT'])
@admin_required
def update_incidente(current_user, incidente_id):
    """Actualizar incidente"""
    try:
        incidente = Incidente.query.get_or_404(incidente_id)
        data = request.get_json()
        
        if 'descripcion' in data:
            incidente.descripcion = data['descripcion']
        if 'tipo' in data:
            incidente.tipo = data['tipo']
        if 'gravedad' in data:
            incidente.gravedad = data['gravedad']
        if 'resuelto' in data:
            incidente.resuelto = data['resuelto']
        if 'checkpoint_id' in data:
            if not Checkpoint.query.get(data['checkpoint_id']):
                return jsonify({'error': 'Checkpoint no encontrado'}), 404
            incidente.checkpoint_id = data['checkpoint_id']
        if 'usuario_id' in data:
            if data['usuario_id'] and not Usuario.query.get(data['usuario_id']):
                return jsonify({'error': 'Usuario no encontrado'}), 404
            incidente.usuario_id = data['usuario_id']
        
        db.session.commit()
        return jsonify({'mensaje': 'Incidente actualizado exitosamente'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/incidentes/<int:incidente_id>', methods=['DELETE'])
@admin_required
def delete_incidente(current_user, incidente_id):

    try:
        incidente = Incidente.query.get_or_404(incidente_id)
        db.session.delete(incidente)
        db.session.commit()
        return jsonify({'mensaje': 'Incidente eliminado exitosamente'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

def register_admin_routes(app):
    app.register_blueprint(admin_bp)


@admin_bp.route('/incidentes/<int:incidente_id>/resolver', methods=['PUT'])
@admin_required
def resolver_incidente(current_user, incidente_id):
   
    print(f" PUT /admin/incidentes/{incidente_id}/resolver - Resolviendo incidente")
    try:
        # Buscar el incidente
        incidente = Incidente.query.get(incidente_id)
        if not incidente:
            return jsonify({
                'error': f'No se encontró el incidente con ID {incidente_id}'
            }), 404

        print(f" Incidente encontrado: {incidente.id} - Estado actual: resuelto={incidente.resuelto}")

        # Marcar como resuelto
        incidente.resuelto = True
        db.session.commit()
        
        print(f" Incidente {incidente_id} marcado como resuelto exitosamente")

        return jsonify({
            'mensaje': 'Incidente marcado como resuelto exitosamente'
        }), 200

    except Exception as e:
        db.session.rollback()
        print(f"❌ Error resolviendo incidente: {str(e)}")
        return jsonify({'error': f'Error al resolver el incidente: {str(e)}'}), 500