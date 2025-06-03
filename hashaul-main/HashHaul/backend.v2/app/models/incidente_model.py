
from extensions import db
from datetime import datetime

class Incidente(db.Model):
    __tablename__ = 'incidentes'
    
    id = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.String(500), nullable=False)
    tipo = db.Column(db.String(50), nullable=False) 
    gravedad = db.Column(db.String(20), default='baja')  
    timestamp = db.Column(db.DateTime, server_default=db.func.now())
    resuelto = db.Column(db.Boolean, default=False)
    

    checkpoint_id = db.Column(db.Integer, db.ForeignKey('checkpoints.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='SET NULL', onupdate='CASCADE'), nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'descripcion': self.descripcion,
            'tipo': self.tipo,
            'gravedad': self.gravedad,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'resuelto': self.resuelto,
            'checkpoint_id': self.checkpoint_id,
            'usuario_id': self.usuario_id
        }
    
    def __repr__(self):
        return f'<Incidente {self.id} - {self.tipo}>'