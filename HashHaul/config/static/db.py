from Flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

app = Flask(__name__)

user = "root"
password = "admin"
nombrecontainer = "mysql_container"
namedb = "flaskdb"

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{user}:{password}@{nombrecontainer}/{namedb}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key= "ingeweb"

db = SQLAlchemy(app)
ma = Marshmallow(app)