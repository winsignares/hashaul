from flask import Flask, render_template
from flask_cors import CORS
from dotenv import load_dotenv
import os
import time
from extensions import db, migrate


load_dotenv()

def create_app():
    app = Flask(__name__,
                static_folder='config/static',
                template_folder='config/templates')


    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'HaShHaUl_2024_$ecr3t_K3y')
    
  
    database_url = os.getenv('DATABASE_URL', 'mysql+pymysql://root:Julper86@localhost/hash_haul_db')
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

   
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'connect_args': {"charset": "utf8mb4"}
    }

  
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app, origins=['*']) 

    
    from app.routes import register_routes
    register_routes(app)

   
    print(" RUTAS REGISTRADAS:")
    for rule in app.url_map.iter_rules():
        print(f"   {rule.methods} {rule.rule}")
    
 
    conductor_routes = [rule for rule in app.url_map.iter_rules() if 'conductor' in rule.rule]
    print(f" RUTAS DE CONDUCTOR ENCONTRADAS: {len(conductor_routes)}")
    for route in conductor_routes:
        print(f"   ✅ {route.methods} {route.rule}")


    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/dashboard')
    def dashboard():
        return render_template('Dashboard.html')

    @app.route('/admin')
    def admin():
        return render_template('Admin.html')

    @app.route('/map')
    def map_view():
        return render_template('Map.html')

   
    @app.route('/health')
    def health():
        return {
            "status": "healthy",
            "message": " Hash Haul funcionando en Docker!",
            "database": "conectada" if db else "no conectada"
        }

  
    @app.route('/test')
    def test():
        return {
            "message": " Hash Haul API funcionando en Docker!",
            "status": "success",
            "database": "conectada" if db else "no conectada"
        }

    return app

def wait_for_db():
    """Esperar a que la base de datos esté disponible"""
    max_retries = 30
    retry_count = 0
    
    while retry_count < max_retries:
        try:
           
            from app.models.usuario_model import Usuario
            db.create_all()
            print(" Conexión a base de datos establecida")
            return True
        except Exception as e:
            retry_count += 1
            print(f" Esperando base de datos... intento {retry_count}/{max_retries}")
            print(f"   Error: {str(e)}")
            time.sleep(2)
    
    print(" No se pudo conectar a la base de datos después de 30 intentos")
    return False

app = create_app()

if __name__ == '__main__':
    print(" Iniciando Hash Haul en Docker...")

    with app.app_context():
        
        if wait_for_db():
            try:
             
                from app.models.usuario_model import Usuario
                from app.models.camion_model import Camion
                from app.models.viaje_model import Viaje
                from app.models.ruta_model import Ruta
                from app.models.checkpoint_model import Checkpoint
                from app.models.incidente_model import Incidente
                
                db.create_all()
                print(" Base de datos inicializada correctamente")
            except Exception as e:
                print(f" Error con base de datos: {e}")
        else:
            print(" No se pudo inicializar la base de datos")

    print(" Servidor: http://localhost:5000")
    print(" API Test: http://localhost:5000/test")
    print(" Health Check: http://localhost:5000/health")
    
   
    app.run(host='0.0.0.0', port=5000, debug=False)