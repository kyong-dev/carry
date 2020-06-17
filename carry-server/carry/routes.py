import os
import secrets
import requests
# from PIL import Image
from flask import render_template, url_for, flash, redirect, request, make_response, jsonify
from carry import app, db, bcrypt
from carry.forms import RegistrationForm, LoginForm, UpdateAccountForm, BookingForm, NewBookingForm
from carry.models import User, Car, Booking, CarSchema
from flask_login import login_user, current_user, logout_user, login_required
from flask_googlemaps import Map
from sqlalchemy_filters import apply_filters
from datetime import date, datetime, timedelta
from carry.database_utils import DatabaseUtils

"""
.. module:: Routing Methods

.. note::
    These methods are routing methods for Flask Navigation
"""

# to see the full request and response objects
# set logging level to DEBUG
import logging
logging.getLogger('flask_assistant').setLevel(logging.DEBUG)

@app.route("/")
def index():
    """Landing Page."""
    return render_template('index.html', title='Home')


@app.route("/home", methods=['GET', 'POST'])
@login_required
def home():
    """Find Car Page."""
    form = BookingForm()
    if (request.args.get('search') != None):
        search_input = request.args.get('search', type=str)
        start_datetime = request.args.get(
            'start_date') + " " + request.args.get('start_time') + ":00"
        end_datetime = request.args.get(
            'end_date') + " " + request.args.get('end_time') + ":00"
        # Get all cars
        cars = DatabaseUtils().getAllCars(db, search_input)
        # Get all booked cars during the period
        bookedCars = DatabaseUtils().getBookedCars(db, start_datetime, end_datetime)

        # remove booked cars from all cars to show only available cars
        for booked in bookedCars:
            cars.remove(booked)

    else:
        today = date.today()
        tommorow = today + timedelta(1)
        currentTime = datetime.now().time().hour
        # return render_template('home.html', title='Find Car')

        if currentTime < 21:
            return redirect(url_for('home', title='Find Car', search='', start_date=today, start_time=(currentTime + 1) % 24, end_date=today, end_time=((currentTime + 3) % 24)))
        elif currentTime < 23:
            return redirect(url_for('home', title='Find Car', search='', start_date=today, start_time=(currentTime + 1) % 24, end_date=tommorow, end_time=((currentTime + 3) % 24)))
        else:
            return redirect(url_for('home', title='Find Car', search='', start_date=tommorow, start_time=(currentTime + 1) % 24, end_date=tommorow, end_time=((currentTime + 3) % 24)))

    map = getMap()

    # ToJSON
    cars_schema = CarSchema(many=True)
    car_list = cars_schema.dump(cars)
    bookedCars = cars_schema.dump(bookedCars)
    return render_template('home.html', title='Find Car', map=map, car_list=car_list, bookedCars=bookedCars, form=form)


@app.route("/register/", methods=['GET', 'POST'])
def register():
    """User Registration Page."""
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        # Store a new user in the database
        user = DatabaseUtils().register(db, form.username.data, form.email.data,
                                        hashed_password, form.firstname.data, form.lastname.data)
        login_user(user)
        flash('Your account has been created! You are now logged in', 'success')
        return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login/", methods=['GET', 'POST'])
def login():
    """User Login Page."""
    # [...]
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        # Find user from database
        user = DatabaseUtils().findUser(db, form.username.data)
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            flash('You are now logged in', 'success')
            if user.auth == "user":
                # Redirect back to the page
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('home'))
            elif user.auth == "manager":
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect("/admin/", code=302)
            elif user.auth == "admin":
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect("/admin/user", code=302)
            else:
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect("/admin/report", code=302)
        elif user == None:
            flash('Login Unsuccessful. User Not Found', 'danger')
        else:
            flash('Login Unsuccessful. Please check email and password.', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout/")
def logout():
    """User Logout Page."""
    logout_user()
    flash('Successfully logged out!', 'success')
    return redirect(url_for('login'))


@app.route("/profile/", methods=['GET', 'POST'])
@login_required
def profile():
    """User Profile Page."""
    form = UpdateAccountForm()
    if form.validate_on_submit():
        profile_url = None
        if form.profile_url.data:
            profile_url = save_picture(form.profile_url.data)
        # Updata user profile in the database
        DatabaseUtils().updateProfile(db, profile_url, form.firstname.data,
                                      form.lastname.data, form.location.data)
        flash('Your account has been updated!', 'success')
        return redirect(url_for('profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.firstname.data = current_user.firstname
        form.lastname.data = current_user.lastname
        form.location.data = current_user.location
    profile_url = url_for(
        'static', filename='image/profile/' + current_user.profile_url)
    return render_template('profile.html', title='Profile', profile_url=profile_url, form=form)


@app.route("/booking", methods=['GET', 'POST'])
@login_required
def new_booking():
    """New Booking Page."""
    # when finalising the booking
    form = BookingForm()
    if (request.method == 'POST'):
        newForm = NewBookingForm()
        # get detailed map

        car = DatabaseUtils().getCar(db, form.car_id.data)
        map = getDetailedMap(car)

        start_datetime = datetime.strptime(
            form.start_datetime.data, '%Y-%m-%d %H:%M:%S')
        end_datetime = datetime.strptime(
            form.end_datetime.data, '%Y-%m-%d %H:%M:%S')
        duration = form.duration.data
        return render_template('booking.html', title='New Booking', form=newForm, car=car,
                               start_datetime=start_datetime, end_datetime=end_datetime, duration=duration, map=map)
    else:
        return redirect(url_for('home', title='Find Car'))
    # car = Car.query.filter_by(id=data.car_id).first()
    # return render_template('booking.html', title='New Booking', car=car, form=form)


@app.route("/booking/detail", methods=['GET', 'POST'])
@login_required
def booking_detail():
    """New Booking Detail Page."""
    if (request.method == 'POST'):
        form = NewBookingForm()
        car = Car.query.filter_by(id=form.car_id.data).first()
        start_datetime = datetime.strptime(
            form.start_datetime.data, '%Y-%m-%d %H:%M:%S')
        end_datetime = datetime.strptime(
            form.end_datetime.data, '%Y-%m-%d %H:%M:%S')
        booking_datetime = datetime.now()
        # calculate duration and total cost from server side
        duration = int(form.duration.data)
        total_cost = duration * car.cost
        reference = datetime.strftime(booking_datetime, '%y%m%d%H%M%s')
        reference = reference + \
            f'{current_user.id}{form.car_id.data}{round(total_cost)}{duration}'

        # Store new booking in the database
        booking = DatabaseUtils().newBooking(db, reference, current_user.id, car.id,
                                              start_datetime, end_datetime, booking_datetime, duration, total_cost)

        return render_template('booking_detail.html', title='Booking Detail', booking=booking, car=car)
    else:
        return redirect(url_for('home', title='Find Car'))


@app.route("/my_bookings", methods=['GET', 'POST'])
@login_required
def my_bookings():
    """My Bookings Page."""
    myBookings = DatabaseUtils().getMyBookings(db, current_user.id)
    # valid_bookings = DatabaseUtils().getMyCurrentBookings(current_user.id)
    past_bookings = DatabaseUtils().getMyPastBookings(db, current_user.id, datetime.now())

    for booking in past_bookings:
        myBookings.remove(booking)

    valid_bookings = myBookings

    return render_template('my_bookings.html', title='My Bookings', valid_bookings=valid_bookings, past_bookings=past_bookings)


def save_picture(picture):
    """A Method for saving a picture from user input"""
    # Generate a random filename for profile pictures
    random_hex = secrets.token_hex(8)
    _, file_ext = os.path.splitext(picture.filename)
    picture_filename = random_hex + file_ext
    picture_path = os.path.join(
        app.root_path, 'static/image/profile', picture_filename)

    # output_size = (125, 125)
    # resized_image = Image.open(picture)
    # rezised_image.thumbnail(output_size)

    picture.save(picture_path)
    return picture_filename


def getMap():
    """A Method for creating a Google map"""
    latitude = -37.814730
    longitude = 144.965900
    map = Map(
        identifier="map",
        lat=latitude,
        lng=longitude,
        zoom=13,
        maptype="TERRAIN",
        style={
            'height': '500px;',
            'width': '100%;',
        },
    )
    return map


def getDetailedMap(car):
    """A Method for creating a detailed Google map"""
    map = Map(
        identifier="map",
        lat=car.lat,
        lng=car.lng,
        zoom=17,
        fullscreen_control=False,
        rotate_control=False,
        scale_control=False,
        streetview_control=False,
        zoom_control=False,
        maptype_control=False,
        scroll_wheel=False,
        collapsible=False,
        style="width: 100%;",
        markers=[
            {
                'icon': 'http://maps.google.com/mapfiles/ms/icons/orange-dot.png',
                'lat': car.lat,
                'lng': car.lng,
                'infobox': "<b>" + car.make + "</b>"
            },
        ],
    )
    return map
