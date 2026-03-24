import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('MYSQL_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MONGO_URI = os.getenv('MONGO_URI')          
    