from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from datetime import datetime




class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)
    venue = db.Column(db.String(200), nullable=False)
    bookings = db.relationship('Booking', backref='event_relation', lazy=True)

    def __init__(self, name, date,venue):
        self.name = name
        self.date = date
        self.venue = venue

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)

    
    user= db.relationship('User', backref=db.backref('user_bookings', lazy=True))
    event = db.relationship('Event', backref=db.backref('event_bookings', lazy=True))


    def __init__(self, user_id, event_id):
        self.user_id = user_id
        self.event_id = event_id

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    bookings=db.relationship('Booking')
    is_admin = db.Column(db.Boolean, default=False)


      
    def __init__(self, email, password,first_name):
        self.email = email
        self.password = password
        self.first_name=first_name
