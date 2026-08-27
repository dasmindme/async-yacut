import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI", "sqlite:///db.sqlite3")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DISK_TOKEN = os.getenv("DISK_TOKEN", "")

    YADISK_MKDIR = os.getenv("YADISK_MKDIR", "0") == "1"