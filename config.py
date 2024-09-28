from dotenv import load_dotenv
load_dotenv()
from flask import Flask
import os
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_restful import Api,Resource
from flask import request,make_response,jsonify
from sqlalchemy import MetaData
from flask_sqlalchemy import SQLAlchemy
from flask_swagger_uig import get_swaggerui_blueprint
from flask_cors import CORS


app = Flask(__name__)
CORS(app)


app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')

""" app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db' """
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.getenv('SECRET_KEY') 

db = SQLAlchemy()
migrate = Migrate(app,db)
bcrypt = Bcrypt(app)
api= Api(app)

db.init_app(app)



SWAGGER_URL = '/api/docs'  # URL for exposing Swagger UI (without trailing '/')
API_URL = '/static/swagger.json'  # Our API url (can of course be a local resource)


# Call factory function to create our blueprint
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,  # Swagger UI static files will be mapped to '{SWAGGER_URL}/dist/'
    API_URL,
    config={  # Swagger UI config overrides
        'app_name': "Test application"
    }
)
app.register_blueprint(swaggerui_blueprint)
