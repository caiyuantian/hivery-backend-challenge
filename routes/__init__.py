from flask import Flask, render_template
import config
import os
from db import mysql
from routes import upload
from routes.api import v1


#obtain parent folder and then get template folder
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
template_dir = os.path.join(template_dir, 'templates')

app = Flask(__name__, template_folder=template_dir)

#Retrieve config from config.py, e.g mssql config
app.config.from_object(config)

mysql.init_app(app)

app.register_blueprint(upload.mod)
app.register_blueprint(v1.mod)

# default welcome page
@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')