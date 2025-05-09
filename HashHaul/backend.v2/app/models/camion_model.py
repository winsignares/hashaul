from app.database.db import db

class Camion(db.Model):
    __tablename__ = 'camiones'
    id = db.Column(db.Integer, primary_key=True)
    placa = db.Column(db.String(20), unique=True, nullable=False)
    modelo = db.Column(db.String(100), nullable=False)

    viajes = db.relationship('Viaje', backref='camion', cascade='all, delete', passive_deletes=True)
