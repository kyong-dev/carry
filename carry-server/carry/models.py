from datetime import datetime
from carry import app, db, login_manager, ma
from flask_login import UserMixin
from flask import jsonify
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from flask_admin.contrib.sqla import ModelView
from flask_admin import BaseView, expose, Admin, AdminIndexView


"""
.. module:: Database Model Classes
"""
# Decorator for reloading the user from the user_id in the session


@login_manager.user_loader
def load_user(user_id):
    """ Decorator for reloading the user from the user_id in the session
    :param user_id: Primary key of User
    :type user_id: int, essential
    :return User Object where id = user_id
    :rtype: dictionary
    """
    return User.query.get(user_id)


class User(db.Model, UserMixin):
    """ User Database Model

    Each user in the database will be assigned a unique id value, which is a primary key. 

    .. note::

        Username and Email should be unique.

    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(60), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    firstname = db.Column(db.String(20), nullable=True)
    lastname = db.Column(db.String(20), nullable=True)
    profile_url = db.Column(
        db.String(20), nullable=True, default='default.jpg')
    location = db.Column(db.String(20), nullable=True, default='melbourne')
    auth = db.Column(db.String(20), nullable=True, default='user')
    registered = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow)
    macAddr = db.Column(db.String(60), unique=True, nullable=True)
    bookings = db.relationship('Booking', backref='rentBy', lazy=True)
    logs = db.relationship('Log', backref='logs', lazy=True)
    reports = db.relationship('Report', backref='reports', lazy=True)

    def __repr__(self):
        return f"User('{self.email}', '{self.firstname}', '{self.lastname}')"

class Car(db.Model):
    """ Car Database Model

    Each car in the database will be assigned a unique id value, which is a primary key. 

    """
    id = db.Column(db.Integer, primary_key=True)
    make = db.Column(db.String(20), nullable=False)
    body_type = db.Column(db.String(20), nullable=False)
    colour = db.Column(db.String(20), nullable=False)
    seats = db.Column(db.Integer, nullable=False)
    cost = db.Column(db.Float, nullable=False)
    address = db.Column(db.String(120), nullable=False)
    suburb = db.Column(db.String(20), nullable=False)
    state = db.Column(db.String(20), nullable=False)
    postcode = db.Column(db.String(20), nullable=False)
    lat = db.Column(db.Float, nullable=False)
    lng = db.Column(db.Float, nullable=False)
    img_url = db.Column(db.String(20), nullable=True, default='car.png')
    bookings = db.relationship('Booking', backref='rented', lazy=True)
    logs = db.relationship('Log', backref='logged', lazy=True)
    reports = db.relationship('Report', backref='reported', lazy='dynamic')


class Booking(db.Model):
    """ Booking Database Model

    Each booking in the database will be assigned a unique id value, which is a primary key. 

    .. note::

        Reference should be unique.
        Booking Model has user_id and car_id fields which are foreign keys.

    """
    id = db.Column(db.Integer, primary_key=True)
    reference = db.Column(db.String(60), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    car_id = db.Column(db.Integer, db.ForeignKey('car.id'), nullable=False)
    total_cost = db.Column(db.Float, nullable=False)
    start_datetime = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow)
    end_datetime = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow)
    booking_datetime = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow)
    duration = db.Column(db.Integer, nullable=False)
    calendar_eid = db.Column(db.String(120), nullable=True)
    started = db.Column(db.Boolean, nullable=False, default=False)
    finished = db.Column(db.Boolean, nullable=False, default=False)
    cancelled = db.Column(db.Boolean, nullable=False, default=False)
    logs = db.relationship('Log', backref='has', lazy=True)

    def __repr__(self):
        return f"Booking('{self.id}', '{self.user_id}', '{self.car_id}', '{self.start_datetime}', '{self.end_datetime}', '{self.booking_datetime}', '{self.total_cost}', '{self.started}', '{self.cancelled}', '{self.finished}')"


class Log(db.Model):
    """ Log Database Model

    Each Log in the database will be assigned a unique id value, which is a primary key. 

    .. note::

        Log Model has user_id, car_id and booking_id fields which are foreign keys.

    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    car_id = db.Column(db.Integer, db.ForeignKey('car.id'), nullable=False)
    booking_id = db.Column(db.Integer, db.ForeignKey(
        'booking.id'), nullable=False)
    lat = db.Column(db.Float, nullable=False)
    lng = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=False)
    datetime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class Report(db.Model):
    """ Report Database Model

    Each Report in the database will be assigned a unique id value, which is a primary key. 

    .. note::

        Report Model has user_id and car_id fields which are foreign key.

    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    car_id = db.Column(db.Integer, db.ForeignKey('car.id'), nullable=False)
    detail = db.Column(db.String(120), nullable=False)
    taken = db.Column(db.Boolean, nullable=False, default=False)
    completed = db.Column(db.Boolean, nullable=False, default=False)
    reported_datetime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    completed_datetime = db.Column(db.DateTime, nullable=True)

class CarSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Car


from carry import admin_routes