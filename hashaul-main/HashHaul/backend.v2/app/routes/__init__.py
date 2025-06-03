
from flask import Flask

def register_routes(app: Flask):
    
    

    from app.routes.auth_routes import auth_bp
    from app.routes.admin_routes import admin_bp
    from app.routes.dashboard_routes import dashboard_bp
    from app.routes.map_routes import map_bp
    
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(map_bp)
    
    