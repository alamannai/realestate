from flask import Flask
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from config import Config

# Initialize extensions (without app context)
mongo = PyMongo()
bcrypt = Bcrypt()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(Config)
    
    # Initialize extensions with app
    mongo.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    CORS(app, origins=Config.CORS_ORIGINS)
    
    # Import and register blueprints
    from routes.auth import auth_bp
    from routes.profile import profile_bp
    from routes.items import items_bp
    from routes.messages import messages_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(profile_bp, url_prefix='/api')
    app.register_blueprint(items_bp, url_prefix='/api')
    app.register_blueprint(messages_bp, url_prefix='/api')
    
    return app

# Create app instance
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)