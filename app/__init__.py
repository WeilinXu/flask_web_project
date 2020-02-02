import os
import sys

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin	# helpful for login

prefix = 'sqlite:////'

app = Flask(__name__)

# configurations
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(app.root_path, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'dev'	# required for flash

# initialize database
db = SQLAlchemy(app)

# initialize login manager
login_manager = LoginManager(app)

# not allow seeing some part of html without login
login_manager.login_view = 'login'
# login_manager.login_message = 'Your custom message'

