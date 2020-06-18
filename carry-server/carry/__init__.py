from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import pymysql
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_googlemaps import GoogleMaps
from flask_admin import Admin, AdminIndexView, expose
from os import environ 


app = Flask(__name__)
# create a secret key to protect against CROSS-SITE REQUEST, FORGE ATTACK
app.config['SECRET_KEY'] = 'b18cb76716d7a2a5a9ea7d5a9e582d08'
# Google Cloud SQL Connection through Unix Socket
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://' + environ.get(
    'DATABASE_ID') + ':' + environ.get('DATABASE_PASSWORD') + '@34.87.247.250:3306/carshare'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)
ma = Marshmallow(app)

bcrypt = Bcrypt(app)
# To manage session
login_manager = LoginManager(app)
# To use login_required
login_manager.login_view = 'login'
# To redirect users back to the page that users were trying to access
login_manager.login_message_category = 'info'

app.config['GOOGLEMAPS_KEY'] = "GOOGLEMAP_API_KEY"
GoogleMaps(app)

# set optional bootswatch theme
app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'

from carry import admin_routes
from carry import socket
from carry import routes
from carry import fetch