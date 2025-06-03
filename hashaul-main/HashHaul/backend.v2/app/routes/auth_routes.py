from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.usuario_model import Usuario
from extensions import db
import jwt
from datetime import datetime, timedelta
from functools import wraps

# Blueprint para las rutas de autenticación
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# Función para crear un token JWT válido por 24 horas
def create_token(user_id, secret_key):
    return jwt.encode({
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(hours=24)
    }, secret_key, algorithm="HS256")

# Decorador para proteger rutas que requieren autenticación mediante token
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        from flask import current_app
        token = None
        
        # Obtener el token desde el header Authorization
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                if auth_header.startswith('Bearer '):
                    token = auth_header.split(' ')[1]
                else:
                    token = auth_header
            except IndexError:
                return jsonify({'error': 'Formato de token inválido'}), 401

        if not token:
            return jsonify({'error': 'Token faltante'}), 401

        try:
            # Decodificamos el token y obtenemos el usuario
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = Usuario.query.filter_by(id=data['user_id']).first()
            if not current_user:
                return jsonify({'error': 'Usuario no encontrado'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expirado'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Token inválido'}), 401

        # Pasamos el usuario autenticado a la función protegida
        return f(current_user, *args, **kwargs)
    return decorated

# Ruta para registrar un nuevo usuario
@auth_bp.route('/register', methods=['POST'])
def register():
    """Ruta para registrar un nuevo usuario"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No se enviaron datos"}), 400

        nombre = data.get("nombre")
        correo = data.get("correo")
        contraseña = data.get("contraseña")
        telefono = data.get("telefono")
        rol = data.get("rol", "conductor")  # Por defecto, el rol será 'conductor'

        if not all([nombre, correo, contraseña]):
            return jsonify({"error": "Nombre, correo y contraseña son obligatorios"}), 400

        # Verificar si el correo ya está registrado
        if Usuario.query.filter_by(correo=correo).first():
            return jsonify({"error": "El correo ya está registrado"}), 409

        # Crear el nuevo usuario
        nuevo_usuario = Usuario(
            nombre=nombre,
            correo=correo,
            contraseña_hash=generate_password_hash(contraseña),
            telefono=telefono,
            rol=rol
        )
        
        db.session.add(nuevo_usuario)
        db.session.commit()

        return jsonify({
            "mensaje": "Usuario registrado exitosamente",
            "usuario": {
                "id": nuevo_usuario.id,
                "nombre": nuevo_usuario.nombre,
                "correo": nuevo_usuario.correo,
                "rol": nuevo_usuario.rol
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error interno: {str(e)}"}), 500

# Ruta para iniciar sesión y generar un token
@auth_bp.route('/login', methods=['POST'])
def login():
    """Ruta para iniciar sesión y obtener token JWT"""
    try:
        from flask import current_app
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No se enviaron datos"}), 400

        correo = data.get("correo")
        contraseña = data.get("contraseña")

        if not correo or not contraseña:
            return jsonify({"error": "Correo y contraseña son obligatorios"}), 400

        # Buscar al usuario por correo
        usuario = Usuario.query.filter_by(correo=correo).first()

        # Verificar contraseña y generar token
        if usuario and check_password_hash(usuario.contraseña_hash, contraseña):
            token = create_token(usuario.id, current_app.config['SECRET_KEY'])

            return jsonify({
                "mensaje": "Login exitoso",
                "token": token,
                "usuario": {
                    "id": usuario.id,
                    "nombre": usuario.nombre,
                    "correo": usuario.correo,
                    "rol": usuario.rol
                }
            }), 200
        else:
            return jsonify({"error": "Credenciales incorrectas"}), 401

    except Exception as e:
        return jsonify({"error": f"Error interno: {str(e)}"}), 500

# Ruta protegida para verificar si el token es válido
@auth_bp.route('/verify', methods=['GET'])
@token_required
def verify(current_user):
    """Ruta para verificar si el token es válido y retornar datos del usuario"""
    return jsonify({
        "status": "valid",
        "message": "Token válido",
        "usuario": {
            "id": current_user.id,
            "nombre": current_user.nombre,
            "correo": current_user.correo,
            "rol": current_user.rol
        }
    }), 200
