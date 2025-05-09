from app.database.db import db

class Checkpoint(db.Model):
    __tablename__ = 'checkpoints'
    id = db.Column(db.Integer, primary_key=True)
    direccion = db.Column(db.String(255), nullable=False)
    latitud = db.Column(db.Float, nullable=False)
    longitud = db.Column(db.Float, nullable=False)
    estado = db.Column(db.String(20), nullable=False, default="pendiente")
    hash = db.Column(db.String(255), nullable=False)
    blockchain_tx_hash = db.Column(db.String(255), nullable=True)

    ruta_id = db.Column(db.Integer, db.ForeignKey('rutas.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)

    incidentes = db.relationship('Incidente', backref='checkpoint', cascade='all, delete', passive_deletes=True)
