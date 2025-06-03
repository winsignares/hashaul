
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db 
class Usuario(db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(100), unique=True, nullable=False)
    contraseña_hash = db.Column(db.String(255), nullable=False)
    telefono = db.Column(db.String(20))
    rol = db.Column(db.String(50), default='conductor')
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    activo = db.Column(db.Boolean, default=True)
    

    viajes = db.relationship('Viaje', backref='conductor', lazy=True)
    incidentes = db.relationship('Incidente', backref='reportado_por', lazy=True)
    
    def set_password(self, contraseña):
        self.contraseña_hash = generate_password_hash(contraseña)
    
    def check_password(self, contraseña):
        return check_password_hash(self.contraseña_hash, contraseña)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'correo': self.correo,
            'telefono': self.telefono,
            'rol': self.rol,
            'fecha_registro': self.fecha_registro.isoformat(),
            'activo': self.activo
        }
    
    def __repr__(self):
        return f'<Usuario {self.nombre}>'