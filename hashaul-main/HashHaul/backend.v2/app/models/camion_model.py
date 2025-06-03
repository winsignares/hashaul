
from extensions import db

class Camion(db.Model):
    __tablename__ = 'camiones'
    
    id = db.Column(db.Integer, primary_key=True)
    placa = db.Column(db.String(20), unique=True, nullable=False)
    modelo = db.Column(db.String(100), nullable=False)
    marca = db.Column(db.String(50))
    año = db.Column(db.Integer)
    capacidad_kg = db.Column(db.Float)
    estado = db.Column(db.String(20), default='disponible') 
    

    viajes = db.relationship('Viaje', backref='camion', cascade='all, delete', passive_deletes=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'placa': self.placa,
            'modelo': self.modelo,
            'marca': self.marca,
            'año': self.año,
            'capacidad_kg': self.capacidad_kg,
            'estado': self.estado
        }
    
    def __repr__(self):
        return f'<Camion {self.placa}>'