import os
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), ".env")
load_dotenv(dotenv_path)

SK = os.environ.get("SECRET_KEY")
SALT = os.environ.get("SALT")
API_KEY = os.environ.get("API_KEY")
