from app.database.db import db
from app.models.usuario_model import Usuario
from app.models.camion_model import Camion
from app.models.viaje_model import Viaje
from app.models.ruta_model import Ruta
from app.models.checkpoint_model import Checkpoint
from app.models.incidente_model import Incidente
from main import app

with app.app_context():
    # Limpiar datos anteriores por si acaso
    db.session.query(Incidente).delete()
    db.session.query(Checkpoint).delete()
    db.session.query(Ruta).delete()
    db.session.query(Viaje).delete()
    db.session.query(Camion).delete()
    db.session.query(Usuario).delete()

    # Crear usuario y camión
    usuario = Usuario(nombre="Luis Díaz", correo="luis@example.com", contraseña="1234")
    camion = Camion(placa="ABC123", modelo="Ford Blindado")
    db.session.add_all([usuario, camion])
    db.session.commit()

    # Crear viaje
    viaje = Viaje(usuario_id=usuario.id, camion_id=camion.id)
    db.session.add(viaje)
    db.session.commit()

    # Crear ruta
    ruta = Ruta(viaje_id=viaje.id)
    db.session.add(ruta)
    db.session.commit()

    # Crear checkpoints
    cp1 = Checkpoint(direccion="Banco Central", latitud=14.5995, longitud=120.9842, estado="pendiente", ruta_id=ruta.id)
    cp2 = Checkpoint(direccion="Banco Norte", latitud=14.6500, longitud=121.0200, estado="pendiente", ruta_id=ruta.id)
    cp3 = Checkpoint(direccion="Banco Sur", latitud=14.5500, longitud=121.0000, estado="pendiente", ruta_id=ruta.id)
    db.session.add_all([cp1, cp2, cp3])
    db.session.commit()

    # Registrar incidente en el segundo checkpoint
    incidente = Incidente(descripcion="Intento de asalto frustrado", checkpoint_id=cp2.id)
    db.session.add(incidente)
    db.session.commit()

    print("✅ Datos insertados correctamente.")
