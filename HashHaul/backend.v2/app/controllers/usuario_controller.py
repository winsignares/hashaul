from flask import request, jsonify
from app.models.usuario_model import Usuario
from app.database.db import db


def obtener_usuarios():
    usuarios = Usuario.query.all()
    return jsonify([{
        "id": u.id,
        "nombre": u.nombre,
        "correo": u.correo,
        "telefono": u.telefono,
        "rol": u.rol
    } for u in usuarios]), 200

def obtener_usuario(id):
    usuario = Usuario.query.get(id)
    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404

    return jsonify({
        "id": usuario.id,
        "nombre": usuario.nombre,
        "correo": usuario.correo,
        "telefono": usuario.telefono,
        "rol": usuario.rol
    }), 200

def crear_usuario():
    data = request.get_json()
    nombre = data.get("nombre")
    correo = data.get("correo")
    contraseña = data.get("contraseña")
    telefono = data.get("telefono")
    rol = data.get("rol", "conductor")  # por defecto "conductor"

    if not all([nombre, correo, contraseña]):
        return jsonify({"error": "Nombre, correo y contraseña son obligatorios"}), 400

    nuevo_usuario = Usuario(
        nombre=nombre,
        correo=correo,
        contraseña=contraseña,
        telefono=telefono,
        rol=rol
    )
    db.session.add(nuevo_usuario)
    db.session.commit()

    return jsonify({"mensaje": "Usuario creado correctamente", "id": nuevo_usuario.id}), 201

def actualizar_usuario(id):
    usuario = Usuario.query.get(id)
    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404

    data = request.get_json()
    usuario.nombre = data.get("nombre", usuario.nombre)
    usuario.correo = data.get("correo", usuario.correo)
    usuario.contraseña = data.get("contraseña", usuario.contraseña)
    usuario.telefono = data.get("telefono", usuario.telefono)
    usuario.rol = data.get("rol", usuario.rol)

    db.session.commit()

    return jsonify({"mensaje": "Usuario actualizado correctamente"}), 200


def eliminar_usuario(id):
    usuario = Usuario.query.get(id)
    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404

    db.session.delete(usuario)
    db.session.commit()

    return jsonify({"mensaje": "Usuario eliminado correctamente"}), 200
