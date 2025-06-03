
from extensions import db
from datetime import datetime

class Ruta(db.Model):
    __tablename__ = 'rutas'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    origen = db.Column(db.String(255), nullable=False)
    destino = db.Column(db.String(255), nullable=False)
    distancia_km = db.Column(db.Float)
    tiempo_estimado_hrs = db.Column(db.Float)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
  
    viaje_id = db.Column(db.Integer, db.ForeignKey('viajes.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    

    checkpoints = db.relationship('Checkpoint', backref='ruta', cascade='all, delete', passive_deletes=True, order_by='Checkpoint.orden')
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'origen': self.origen,
            'destino': self.destino,
            'distancia_km': self.distancia_km,
            'tiempo_estimado_hrs': self.tiempo_estimado_hrs,
            'fecha_registro': self.fecha_registro.isoformat() if self.fecha_registro else None,
            'viaje_id': self.viaje_id,
            'checkpoints': [cp.to_dict() for cp in self.checkpoints]
        }
    
    def __repr__(self):
        return f'<Ruta {self.id} - {self.origen} a {self.destino}>'