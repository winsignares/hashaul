from marshmallow import Schema, fields

class UsuarioLoginSchema(Schema):
    correo = fields.Email(required=True)
    contraseña = fields.String(required=True)

class UsuarioResponseSchema(Schema):
    id = fields.Int()
    nombre = fields.Str()
    correo = fields.Email()
