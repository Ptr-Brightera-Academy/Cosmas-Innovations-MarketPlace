from market import app
from flask import Flask
from dotenv import load_dotenv
import os

load_dotenv() 
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)