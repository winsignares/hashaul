from functools import wraps
from flask import request, jsonify, g, current_app
import jwt
import os
from app.models.usuario_model import Usuario

# Decorador para verificar que el token JWT sea válido antes de acceder a una ruta protegida
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # Obtener el token desde el encabezado Authorization
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]

        if not token:
            return jsonify({'success': False, 'error': 'Token no proporcionado'}), 401

        try:
            # Decodificamos el token usando la clave secreta
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])

            # Buscamos el usuario por ID en el token
            current_user = Usuario.query.get(data['user_id'])
            if not current_user:
                return jsonify({'success': False, 'error': 'Usuario no encontrado'}), 404

            # Guardamos el usuario actual en el objeto global `g`
            g.current_user = current_user

        except jwt.ExpiredSignatureError:
            return jsonify({'success': False, 'error': 'Token expirado'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'success': False, 'error': 'Token inválido'}), 401
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

        # Si todo está bien, ejecutamos la función original
        return f(*args, **kwargs)

    return decorated

# Decorador para permitir solo a usuarios con rol 'administrador' o 'supervisor'
def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not hasattr(g, 'current_user') or g.current_user.rol not in ['administrador', 'supervisor']:
            return jsonify({'error': 'Permisos de administrador requeridos'}), 403
        return f(*args, **kwargs)
    return decorated

# Decorador para permitir acceso a conductores autenticados o administradores
def conductor_or_admin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not hasattr(g, 'current_user'):
            return jsonify({'error': 'Autenticación requerida'}), 401
        return f(*args, **kwargs)
    return decorated
