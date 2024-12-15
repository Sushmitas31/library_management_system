from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_jwt_extended import JWTManager
from config import Config  

app = Flask(__name__)
app.config.from_object(Config) 

db = SQLAlchemy(app)
ma = Marshmallow(app)
jwt = JWTManager(app)

from app.routes import admin, user
app.register_blueprint(admin.bp)
app.register_blueprint(user.bp)
