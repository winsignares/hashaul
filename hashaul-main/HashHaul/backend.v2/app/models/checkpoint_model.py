
from extensions import db
from datetime import datetime

class Checkpoint(db.Model):
    __tablename__ = 'checkpoints'
    
    id = db.Column(db.Integer, primary_key=True)
    direccion = db.Column(db.String(255), nullable=False)
    latitud = db.Column(db.Float, nullable=False)
    longitud = db.Column(db.Float, nullable=False)
    estado = db.Column(db.String(20), nullable=False, default="pendiente") 
    hash = db.Column(db.String(255), nullable=False)
    blockchain_tx_hash = db.Column(db.String(255), nullable=True)
    timestamp_alcanzado = db.Column(db.DateTime, nullable=True)
    orden = db.Column(db.Integer, nullable=False)  
    

    ruta_id = db.Column(db.Integer, db.ForeignKey('rutas.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    

    incidentes = db.relationship('Incidente', backref='checkpoint', cascade='all, delete', passive_deletes=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'direccion': self.direccion,
            'latitud': self.latitud,
            'longitud': self.longitud,
            'estado': self.estado,
            'hash': self.hash,
            'blockchain_tx_hash': self.blockchain_tx_hash,
            'timestamp_alcanzado': self.timestamp_alcanzado.isoformat() if self.timestamp_alcanzado else None,
            'orden': self.orden,
            'ruta_id': self.ruta_id
        }
    
    def __repr__(self):
        return f'<Checkpoint {self.id} - {self.direccion}>'