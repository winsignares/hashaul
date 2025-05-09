from app.database.db import db

class Viaje(db.Model):
    __tablename__ = 'viajes'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    camion_id = db.Column(db.Integer, db.ForeignKey('camiones.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    estado = db.Column(db.String(20), nullable=False)  # 'pendiente', 'en curso', 'completado'

    rutas = db.relationship('Ruta', backref='viaje', cascade='all, delete', passive_deletes=True)
