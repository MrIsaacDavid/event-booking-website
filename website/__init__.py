#this folder makes the website folder a python package
from flask import Flask # imports the Flask class.
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager


db = SQLAlchemy()
DB_NAME = "event"
KEY='nsbcsdnmbnasbdnfjsdfjd1234567890'

#create a function which be called by main.py to run the application
def create_app():
    app=Flask(__name__) #creates a Flask web server.

    app.config['SECRET_KEY'] = KEY
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:*3Wangari4#!@localhost/' + DB_NAME
    # Replace 'username' and 'password' with your MySQL credentials
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    from .views import views 
    from .auth import auth


    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    
    from .models import User,Event, Booking
    
    with app.app_context():
        db.create_all()

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def user_loader(user_id):
        user = User.query.filter_by(id=user_id).first()
        if user:
            return user
        return None

    return app

def create_database(app):
    if not path.exists(path.join('website' + DB_NAME)):
        with app.app_context():
            db.init_app(app)
            db.create_all()
        print('Created Database!')


