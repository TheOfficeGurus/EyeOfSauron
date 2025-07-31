from flask import Flask

def register_blueprints(app: Flask):
    """
    Registra todos los blueprints de la aplicación
    """
    # Importar blueprints
    from backend.routes.auth import auth_bp
    from backend.routes.server import app_win_bp
    
    # Registrar blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(app_win_bp)
    
    # Blueprint para rutas de salud/status
    # from app.routes.health import health_bp
    # app.register_blueprint(health_bp)