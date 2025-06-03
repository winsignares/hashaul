# Importamos librerías necesarias para manejar rutas, datos y modelos
from flask import Blueprint, request, jsonify, g
from app.models.usuario_model import Usuario
from app.models.viaje_model import Viaje
from app.models.incidente_model import Incidente
from app.models.checkpoint_model import Checkpoint  
from datetime import datetime
from extensions import db
from app.routes.auth_middleware import token_required

# Creamos un blueprint para agrupar las rutas del dashboard
dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/api/dashboard')

# Ruta para obtener todos los viajes completados
@dashboard_bp.route('/viajes_completos', methods=['GET'])
@token_required
def get_viajes():
    try:
        # Verificamos si el usuario está autenticado
        if not hasattr(g, 'current_user') or not g.current_user:
            return jsonify({'success': False, 'error': 'Usuario no autenticado'}), 401

        # Obtenemos todos los viajes completados
        query = Viaje.query.filter(Viaje.estado == 'completado')

        # Si no es un administrador, solo ve sus propios viajes
        if g.current_user.rol not in ['administrador', 'supervisor', 'admin']:
            query = query.filter(Viaje.usuario_id == g.current_user.id)

        # Ordenamos los viajes por fecha
        viajes = query.order_by(Viaje.fecha_registro.desc()).all()

        # Formateamos los datos de cada viaje
        viajes_data = []
        for viaje in viajes:
            viaje_dict = {
                'id': viaje.id,
                'codigo': getattr(viaje, 'codigo', None),
                'estado': viaje.estado,
                'usuario_id': viaje.usuario_id,
                'origen': getattr(viaje, 'origen', None),
                'destino': getattr(viaje, 'destino', None),
                'fecha_inicio': viaje.fecha_inicio.isoformat() if viaje.fecha_inicio else None,
                'fecha_fin': viaje.fecha_fin.isoformat() if viaje.fecha_fin else None,
                'conductor': viaje.conductor.nombre if viaje.conductor else None,
                'camion_id': getattr(viaje, 'camion_id', None),
                'camion_placa': getattr(viaje, 'camion_placa', None)
            }

            # Si el viaje tiene rutas asociadas, las agregamos
            if hasattr(viaje, 'rutas'):
                viaje_dict['rutas'] = []
                for ruta in viaje.rutas:
                    ruta_info = ruta.to_dict() if hasattr(ruta, 'to_dict') else {
                        'id': ruta.id,
                        'nombre': getattr(ruta, 'nombre', None),
                        'distancia_total': getattr(ruta, 'distancia_km', None),
                        'tiempo_estimado': ruta.tiempo_estimado_hrs * 60 if ruta.tiempo_estimado_hrs else None
                    }
                    viaje_dict['rutas'].append(ruta_info)

            viajes_data.append(viaje_dict)

        # Respondemos con los datos
        return jsonify({
            'success': True,
            'data': viajes_data,
            'message': f'Se encontraron {len(viajes_data)} viajes completados para {g.current_user.nombre} ({g.current_user.rol})'
        }), 200

    except Exception as e:
        print(f"Error obteniendo viajes completados: {str(e)}")
        return jsonify({'success': False, 'error': f'Error al obtener viajes completados: {str(e)}'}), 500

# Ruta para obtener estadísticas de viajes de un usuario
@dashboard_bp.route('/estadisticas', methods=['GET'])
@token_required
def get_estadisticas():
    try:
        # Verificamos si el usuario está autenticado y obtenemos su ID
        if hasattr(g, 'current_user') and g.current_user:
            usuario_id = g.current_user.id
            usuario_nombre = g.current_user.nombre
        else:
            # Intentamos obtener el token del encabezado manualmente
            token = None
            if 'Authorization' in request.headers:
                auth_header = request.headers['Authorization']
                token = auth_header.split(" ")[1]
            
            if not token:
                return jsonify({'error': 'Token faltante'}), 401
            
            # Decodificamos el token para obtener el usuario
            import jwt
            import os
            data = jwt.decode(token, os.getenv('SECRET_KEY', 'HaShHaUl_2024_$ecr3t_K3y'), algorithms=['HS256'])
            usuario_id = data['user_id']
            current_user = Usuario.query.get(usuario_id)
            usuario_nombre = current_user.nombre if current_user else 'Usuario'

        # Consultamos estadísticas del usuario
        total_viajes = Viaje.query.filter_by(usuario_id=usuario_id).count()
        viajes_completados = Viaje.query.filter_by(usuario_id=usuario_id, estado='completado').count()
        viajes_pendientes = Viaje.query.filter_by(usuario_id=usuario_id, estado='pendiente').count()
        viajes_en_curso = Viaje.query.filter_by(usuario_id=usuario_id, estado='en_curso').count()

        return jsonify({
            'success': True,
            'data': {
                'total_viajes': total_viajes,
                'viajes_completados': viajes_completados,
                'viajes_pendientes': viajes_pendientes,
                'viajes_en_curso': viajes_en_curso,
                'usuario_actual': usuario_nombre,
                'usuario_id': usuario_id
            },
            'message': f'Estadísticas para {usuario_nombre}'
        }), 200

    except Exception as e:
        print(f"Error en estadísticas: {str(e)}")
        return jsonify({'success': False, 'error': f'Error al obtener estadísticas: {str(e)}'}), 500

# Ruta para obtener todos los viajes pendientes
@dashboard_bp.route('/viajes_pendientes', methods=['GET'])
@token_required
def get_viajes_pendientes():
    try:
        # Verificamos si el usuario está autenticado
        if not hasattr(g, 'current_user') or not g.current_user:
            return jsonify({'success': False, 'error': 'Usuario no autenticado'}), 401

        # Obtenemos los viajes que no están completados
        query = Viaje.query.filter(Viaje.estado != 'completado')

        # Si el usuario no es administrador, filtramos por su ID
        if g.current_user.rol not in ['administrador', 'supervisor', 'admin']:
            query = query.filter_by(usuario_id=g.current_user.id)

        # Obtenemos los viajes ordenados por fecha
        viajes = query.order_by(Viaje.fecha_registro.desc()).all()
        viajes_data = []

        # Formateamos los datos
        for viaje in viajes:
            viaje_dict = viaje.to_dict() if hasattr(viaje, 'to_dict') else {
                'id': viaje.id,
                'estado': viaje.estado,
                'usuario_id': viaje.usuario_id,
                'codigo': getattr(viaje, 'codigo', None),
                'origen': getattr(viaje, 'origen', None),
                'destino': getattr(viaje, 'destino', None),
                'fecha_inicio': viaje.fecha_inicio.isoformat() if viaje.fecha_inicio else None,
                'fecha_fin': viaje.fecha_fin.isoformat() if viaje.fecha_fin else None,
                'conductor': viaje.conductor.nombre if viaje.conductor else None,
                'camion_id': getattr(viaje, 'camion_id', None),
                'camion_placa': getattr(viaje, 'camion_placa', None)
            }
            viajes_data.append(viaje_dict)

        # Preparamos mensaje con información del usuario
        user_info = f"({g.current_user.rol})" if g.current_user.rol in ['administrador', 'supervisor', 'admin'] else f"(conductor: {g.current_user.nombre})"

        return jsonify({
            'success': True,
            'data': viajes_data,
            'message': f'Se encontraron {len(viajes_data)} viajes pendientes {user_info}'
        }), 200

    except Exception as e:
        print(f"Error obteniendo viajes pendientes: {str(e)}")
        return jsonify({'success': False, 'error': f'Error al obtener viajes pendientes: {str(e)}'}), 500

# Ruta para crear un incidente asociado a un checkpoint y a un usuario
@dashboard_bp.route('/incidentes', methods=['POST'])
@token_required
def crear_incidente():
    try:
        # Obtenemos los datos del cuerpo de la solicitud
        data = request.get_json()

        if not data:
            return jsonify({'success': False, 'error': 'No se enviaron datos'}), 400

        descripcion = data.get('descripcion')
        tipo = data.get('tipo')
        checkpoint_id = data.get('checkpoint_id')

        # Validamos campos requeridos
        if not descripcion or not tipo:
            return jsonify({'success': False, 'error': 'Los campos descripcion y tipo son requeridos'}), 400

        # Validamos el tipo de incidente
        tipos_validos = ['retraso', 'accidente', 'desvio', 'otro']
        if tipo not in tipos_validos:
            return jsonify({'success': False, 'error': f'Tipo inválido. Tipos válidos: {", ".join(tipos_validos)}'}), 400

        # Validamos que el checkpoint exista
        if checkpoint_id:
            checkpoint = Checkpoint.query.get(checkpoint_id)
            if not checkpoint:
                return jsonify({'success': False, 'error': f'No se encontró el checkpoint con ID {checkpoint_id}'}), 404

        # Obtenemos el ID del usuario actual
        usuario_id = None
        if hasattr(g, 'current_user') and g.current_user:
            usuario_id = getattr(g.current_user, 'id', None)

        # Creamos el nuevo incidente
        nuevo_incidente = Incidente(
            descripcion=descripcion,
            tipo=tipo,
            gravedad=data.get('gravedad', 'baja'),  # Valor por defecto: baja
            checkpoint_id=checkpoint_id,
            usuario_id=usuario_id,
            timestamp=datetime.now()
        )

        # Guardamos el incidente en la base de datos
        db.session.add(nuevo_incidente)
        db.session.commit()

        return jsonify({
            'success': True,
            'data': {
                'id': nuevo_incidente.id,
                'descripcion': nuevo_incidente.descripcion,
                'tipo': nuevo_incidente.tipo,
                'gravedad': nuevo_incidente.gravedad,
                'timestamp': nuevo_incidente.timestamp.isoformat()
            },
            'message': 'Incidente creado exitosamente'
        }), 201

    except Exception as e:
        db.session.rollback()
        print(f"Error completo al crear incidente: {str(e)}")
        return jsonify({'success': False, 'error': f'Error al crear el incidente: {str(e)}'}), 500


