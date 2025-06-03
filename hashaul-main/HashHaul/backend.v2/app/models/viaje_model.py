
from extensions import db
from datetime import datetime

class Viaje(db.Model):
    __tablename__ = 'viajes'
    
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True, nullable=False)  
    estado = db.Column(db.String(20), nullable=False, default='pendiente')  
    fecha_inicio = db.Column(db.DateTime, nullable=True)
    fecha_fin = db.Column(db.DateTime, nullable=True)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    observaciones = db.Column(db.Text, nullable=True)
    
   
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    camion_id = db.Column(db.Integer, db.ForeignKey('camiones.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    

    rutas = db.relationship('Ruta', backref='viaje', cascade='all, delete', passive_deletes=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'codigo': self.codigo,
            'estado': self.estado,
            'fecha_inicio': self.fecha_inicio.isoformat() if self.fecha_inicio else None,
            'fecha_fin': self.fecha_fin.isoformat() if self.fecha_fin else None,
            'fecha_registro': self.fecha_registro.isoformat() if self.fecha_registro else None,
            'observaciones': self.observaciones,
            'usuario_id': self.usuario_id,
            'camion_id': self.camion_id,
            'conductor': self.conductor.nombre if self.conductor else None,
            'camion_placa': self.camion.placa if self.camion else None
        }
    
    def __repr__(self):
        return f'<Viaje {self.codigo} - {self.estado}>'