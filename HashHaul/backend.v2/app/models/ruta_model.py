from app.database.db import db

class Ruta(db.Model):
    __tablename__ = 'rutas'
    id = db.Column(db.Integer, primary_key=True)
    viaje_id = db.Column(db.Integer, db.ForeignKey('viajes.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)

    checkpoints = db.relationship('Checkpoint', backref='ruta', cascade='all, delete', passive_deletes=True)
