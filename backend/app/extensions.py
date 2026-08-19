from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_bcrypt import Bcrypt

# Initialize Flask extensions (not yet bound to app)
db = SQLAlchemy()
jwt = JWTManager()
cors = CORS()
bcrypt = Bcrypt()
