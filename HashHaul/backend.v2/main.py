from flask import Flask
from flask_cors import CORS
from app.database.db import init_db, db
from app.routes.index_routes import index_bp
from app.routes.auth_routes import auth_bp
from app.routes.perfil_routes import perfil_bp
from app.routes.camion_routes import camion_bp
from app.routes.viaje_routes import viaje_bp
from app.routes.checkpoint_routes import checkpoint_bp
from app.routes.incidente_routes import incidente_bp
from app.routes.usuario_routes import usuario_bp
from app.routes.ruta_routes import ruta_bp
from app.routes.admin_routes import admin_bp
from app.routes.blockchain_routes import blockchain_bp


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:1234@localhost/rutas_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

CORS(app)
init_db(app)
with app.app_context():
    from app.models.usuario_model import Usuario
    from app.models.camion_model import Camion
    from app.models.viaje_model import Viaje
    from app.models.ruta_model import Ruta
    from app.models.checkpoint_model import Checkpoint
    from app.models.incidente_model import Incidente
    db.create_all()

app.register_blueprint(index_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(perfil_bp)
app.register_blueprint(camion_bp)
app.register_blueprint(viaje_bp)
app.register_blueprint(checkpoint_bp)
app.register_blueprint(incidente_bp)
app.register_blueprint(usuario_bp)
app.register_blueprint(ruta_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(blockchain_bp, url_prefix="/blockchain")





if __name__ == '__main__':
    app.run(debug=True)
