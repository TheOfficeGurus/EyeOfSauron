import hashlib
import os

class Config:
    # SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret'
    # SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///app.db'
    # JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret'
    # JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 hora
    ##############################
    #testing values
    ##############################
    SECRET_KEY="4_v3c35_h4y_qu3_t0m4r_d3c1510n35..."
    _KEY_ = hashlib.sha256(SECRET_KEY.encode()).digest()