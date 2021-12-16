# Flask related basic imports
from flask import Flask
from flask import render_template
from flask import url_for
from flask import redirect
from flask import send_from_directory
from flask import abort
from flask import flash

# security features WSGI
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash

# Database handling
from flask_sqlalchemy import SQLAlchemy

# Login management
from flask_login import UserMixin
from flask_login import login_user
from flask_login import logout_user
from flask_login import LoginManager
from flask_login import login_required
from flask_login import current_user

# form handling
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms import PasswordField
from wtforms import SubmitField
from wtforms.validators import Email
from wtforms.validators import DataRequired
from wtforms.validators import URL

from wallpaperscraft.main import *
from random import choice
from os import scandir
import json

flask_app = Flask(__name__)

flask_app.secret_key = b"fsdjfapisds345678)(/&% "
flask_app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///users.db'
flask_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
flask_app.config["UPLOAD_FOLDER"] = "./static/files"

flask_db = SQLAlchemy(app=flask_app)

LM = LoginManager()
LM.init_app(app=flask_app)

# initial Image
image = web_image('nature', "1920x1080")


portfolio_images = './static/static_images/'
descriptions_path = './Descriptions.json'
portfolio_path = '../'
def get_project_cards():
    projects = [item.name for item in scandir(portfolio_path)]
    images_path = [item.path for item in scandir(portfolio_images) if ".jpg" in item.name]
    project_images = []
    for img in images_path:
        for project in projects:
            if project in img:
                project_images.append(img)

    print(project_images)
    with open(descriptions_path, "r") as descriptions_file:
        descriptions = json.load(descriptions_file)
        descriptions = {key: {"descriptions":value} for key, value in descriptions.items()}
        descriptions_full = {}
        for key, path in zip(descriptions.keys(), project_images):
            descriptions[key]["path"] = path

    return descriptions




class User(flask_db.Model):
    id = flask_db.Column(flask_db.Integer, primary_key=True)
    email = flask_db.Column(flask_db.String(100), unique=True)
    password = flask_db.Column(flask_db.String(100))
    name = flask_db.Column(flask_db.String(100))

    def __repr__(self):
        return f"User: {self.name}: {self.id}"


# creating form for user to register and login

class RegisterForm(FlaskForm):
    name = StringField(label="Name", validators=[DataRequired()])
    email = StringField(label="Email", validators=[DataRequired()])
    password = PasswordField(label="Password", validators=[DataRequired()])


class LoginForm(FlaskForm):
    email = StringField(label="Email", validators=[DataRequired()])
    password = PasswordField(label="Password", validators=[DataRequired()])


@LM.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@flask_app.route('/')
def home():
    print(image)
    print(get_project_cards())
    return render_template("index.html", image=image, descriptions = get_project_cards())


@flask_app.route("/register", methods=["GET", "POST"])
def register():
    register_form = RegisterForm()

    if register_form.validate_on_submit():
        print(F"New user trying to register")
        email = register_form.email.data
        password = register_form.password.data
        name = register_form.name.data
        print(f"data:\n{email}\n{name}")
        if User.query.filter_by(email=email):
            flash(f"That email:\n{email}\nalready exists, try logging in instead")
            return redirect(url_for("login"))
        else:
            hashed_password = generate_password_hash(password=password,
                                                     method="pbkdf2:sha256:3",
                                                     salt_length=8)
            new_user = User(email=email,
                            password=hashed_password,
                            name=name)
            flask_db.session.add(new_user)
            flask_db.session.commit()
            return redirect(url_for("home"))
    return render_template("register.html", form=register_form)


@flask_app.route('/login', methods=["GET", "POST"])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        email = login_form.email.data
        password = login_form.password.data
        is_user = User.query.filter_by(email=email)
        if is_user is None:
            flash(f"That email:\n{email}\ndoes not exist try again please")
            return redirect(url_for("login"))
        elif not check_password_hash(pwhash=is_user.password, password=password):
            flash(f"The password you entered is incorrect, please try again.")
            return redirect(url_for("login"))
        else:
            login_user(is_user)
            return redirect(url_for("home"))
    return render_template("login.html", form=login_form)


@flask_app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))


@flask_app.route("/about")
def about():
    return "<h1>Hello this will be the about page<h1/>"


@flask_app.route("/contact")
def contact():
    return "<h1>Hello this is where you will contact me<h1/>"


# Initial random image


if __name__ == "__main__":
    flask_app.run(debug=True, port=5000)

