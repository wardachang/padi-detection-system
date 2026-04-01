import os

class Config:
    SECRET_KEY = "WARDA_SECRET_KEY"

    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:@localhost/padi_db"

    SQLALCHEMY_TRACK_MODIFICATIONS = False