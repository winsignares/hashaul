from flask import request, jsonify
from app.models.usuario_model import Usuario
from app.schemas.usuario_schema import UsuarioLoginSchema, UsuarioResponseSchema
from app.database.db import db

login_schema = UsuarioLoginSchema()
response_schema = UsuarioResponseSchema()

def login():
    datos = request.get_json()
    errores = login_schema.validate(datos)
    if errores:
        return jsonify({"error": errores}), 400

    correo = datos["correo"]
    contraseña = datos["contraseña"]

    usuario = Usuario.query.filter_by(correo=correo, contraseña=contraseña).first()

    if usuario:
        return response_schema.dump(usuario), 200
    else:
        return jsonify({"error": "Correo o contraseña incorrectos"}), 401
