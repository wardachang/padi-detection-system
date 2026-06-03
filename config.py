import os
from datetime import timedelta

class Config:
    # Saat server di-run ulang, session lama otomatis tidak valid
    SECRET_KEY = os.environ.get("SECRET_KEY") or os.urandom(24)

    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:@localhost/padi_db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SESSION_PERMANENT = False
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    REMEMBER_COOKIE_DURATION = timedelta(seconds=0)