from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from dotenv import load_dotenv
import os


load_dotenv()


db = SQLAlchemy()
migrate = Migrate()

def create_app():

    app = Flask(__name__, 
                static_folder='../config/static',
                template_folder='../config/templates')
    

    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'HaShHaUl_2024_$ecr3t_K3y')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'mysql+pymysql://root:Julper86@localhost/hash_haul_db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    

    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app, origins=['http://localhost:5000', 'http://127.0.0.1:5000'])
    

    from app.routes import register_routes
    register_routes(app)
    
    return app