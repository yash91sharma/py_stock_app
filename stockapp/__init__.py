from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from stockapp import stock_fc
from flask_mail import Mail
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('secret_key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info' #bootstrap class like success
_user_view = 'home'
_stock_list = stock_fc.get_stock_list(['All'])
_n_days = 365
_color_pallet = ['#379683','#8EE4AF','#24305E','#A8D0E6','#5C2018','#D4A59A','#F3D250','#99842f','#ffb366']
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('email_username')
app.config['MAIL_PASSWORD'] = os.environ.get('email_password')
mail = Mail(app)

from stockapp import routes