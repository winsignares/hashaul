from app.database.db import db

class Incidente(db.Model):
    __tablename__ = 'incidentes'
    id = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.String(500), nullable=False)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())
    checkpoint_id = db.Column(db.Integer, db.ForeignKey('checkpoints.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
