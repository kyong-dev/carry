import requests
import json
import os
from flask import url_for, redirect, request, render_template
from datetime import datetime
from carry import app, db
from flask_admin.contrib.sqla import ModelView
from flask_admin import BaseView, expose, Admin, AdminIndexView
from flask_admin.menu import MenuLink
from flask_login import current_user, login_required
from carry.models import User, Car, Booking, Log, Report, CarSchema
from carry.database_utils import DatabaseUtils
from markupsafe import Markup
from flask_admin.form import SecureForm
from wtforms.validators import DataRequired, Regexp, Email, NumberRange
import speech_recognition as sr
import subprocess
from flask_googlemaps import Map
import pyqrcode
import png


class UserView(ModelView):
    """
        Default Flask-Admin Model View for User

        this gives you a set of fully featured CRUD views for your model:
        • A list view, with support for searching, sorting, filtering, and deleting records.
        • A create view for adding new records.
        • An edit view for updating existing records.
        • An optional, read-only details view.

        Form Validation by using WTF-form
    """

    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('login', next=request.url))

    can_view_details = True

    # CSRF Protection
    form_base_class = SecureForm
    column_list = ('id', 'username', 'email', 'firstname',
                   'lastname', 'profile_url', 'location', 'auth')
    column_searchable_list = ['id', 'username',
                              'email', 'firstname', 'lastname']
    # Form Validation
    form_args = dict(
        username=dict(validators=[DataRequired(), Regexp('^\w+$')]),
        email=dict(validators=[DataRequired(), Email()]),
        firstname=dict(validators=[DataRequired(), Regexp('^[\w\s]+$')]),
        lastname=dict(validators=[DataRequired(), Regexp('^[\w\s]+$')]),
        profile_url=dict(validators=[DataRequired(), Regexp('^\w+\.+\w+$')]),
        location=dict(validators=[DataRequired(), Regexp('^[\w\s]+$')]),
        auth=dict(validators=[DataRequired(), Regexp('^\w+$')]),
    )


class CarView(ModelView):
    """
        Default Flask-Admin Model View for Car

        this gives you a set of fully featured CRUD views for your model:
        • A list view, with support for searching, sorting, filtering, and deleting records.
        • A create view for adding new records.
        • An edit view for updating existing records.
        • An optional, read-only details view.

        Form Validation by using WTF-form
    """

    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('login', next=request.url))

    can_view_details = True

    # CSRF Protection
    form_base_class = SecureForm
    column_list = ('id', 'make', 'body_type', 'colour', 'seats', 'cost',
                   'address', 'suburb', 'state', 'postcode', 'lat', 'lng', 'img_url', 'Report')
    column_searchable_list = ['id', 'make', 'body_type', 'colour',
                              'seats', 'cost', 'address', 'suburb', 'state', 'postcode']
    # Form Validation
    form_args = dict(
        make=dict(validators=[DataRequired(), Regexp('^[\w\s]+$')]),
        body_type=dict(validators=[DataRequired(), Regexp('^[\w\s]+$')]),
        colour=dict(validators=[DataRequired(), Regexp('^\w+$')]),
        seats=dict(validators=[DataRequired(), NumberRange(
            min=2, max=13, message='Number between 2-13')]),
        cost=dict(validators=[DataRequired(), NumberRange(
            min=1, max=20, message='Number between 1-20')]),
        address=dict(validators=[DataRequired()]),
        suburb=dict(validators=[DataRequired(), Regexp('^[\w\s]+')]),
        state=dict(validators=[DataRequired(), Regexp('^[\w\s]+')]),
        postcode=dict(validators=[DataRequired(), Regexp(
            '^[0-9]{4}$', message='Invalid Postcode')]),
        img_url=dict(validators=[DataRequired(), Regexp('^\w+\.+\w+$')]),
    )

    def render(self, template, **kwargs):
        """
        using extra js in render method allow use
        url_for that itself requires an app context
        """
        self.extra_js = [url_for("static", filename="js/admin.js")]

        template = 'admin/list_car.html'
        return super(CarView, self).render(template, **kwargs)

    def _report(view, context, model, name):
        """
        Add Report buttons for each car row
        """
        _html = '''
            <Button onclick="report({car_id})">Report</button
        '''.format(car_id=model.id)

        return Markup(_html)

    column_formatters = {
        'Report': _report
    }


class BookingView(ModelView):
    """
        Default Flask-Admin Model View for Booking

        this gives you a set of fully featured CRUD views for your model:
        • A list view, with support for searching, sorting, filtering, and deleting records.
        • A create view for adding new records.
        • An edit view for updating existing records.
        • An optional, read-only details view.

        Form Validation by using WTF-form
    """

    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('login', next=request.url))

    can_view_details = True

    # CSRF Protection
    form_base_class = SecureForm
    column_list = ('id', 'reference', 'user_id', 'car_id', 'total_cost', 'start_datetime',
                   'end_datetime', 'booking_datetime', 'started', 'finished', 'cancelled')
    column_searchable_list = ['reference', 'user_id',
                              'car_id', 'started', 'finished', 'cancelled']

    # Form Validation
    form_args = dict(
        reference=dict(validators=[DataRequired(), Regexp('^\d+$')]),
        user_id=dict(validators=[DataRequired()]),
        car_id=dict(validators=[DataRequired()]),
        total_cost=dict(validators=[DataRequired(), NumberRange(min=1)]),
        duration=dict(validators=[DataRequired(), NumberRange(min=1)]),
    )


class LogView(ModelView):
    """
        Default Flask-Admin Model View for Log

        this gives you a set of fully featured CRUD views for your model:
        • A list view, with support for searching, sorting, filtering, and deleting records.
        • A create view for adding new records.
        • An edit view for updating existing records.
        • An optional, read-only details view.

        Form Validation by using WTF-form
    """

    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('login', next=request.url))

    can_view_details = True

    # CSRF Protection
    form_base_class = SecureForm

    column_list = ('id', 'booking_id',
                   'lat', 'lng', 'status', 'datetime')
    column_searchable_list = ['user_id', 'lat', 'lng', 'status']

    # Form Validation
    form_args = dict(
        user_id=dict(validators=[DataRequired()]),
        car_id=dict(validators=[DataRequired()]),
        booking_id=dict(validators=[DataRequired()]),
        lat=dict(validators=[DataRequired()]),
        lng=dict(validators=[DataRequired()]),
        status=dict(validators=[DataRequired(), Regexp('^\w+$')]),
    )


class ReportView(ModelView):
    """
        Default Flask-Admin Model View for Report

        this gives you a set of fully featured CRUD views for your model:
        • A list view, with support for searching, sorting, filtering, and deleting records.
        • A create view for adding new records.
        • An edit view for updating existing records.
        • An optional, read-only details view.

        Form Validation by using WTF-form
    """

    def is_accessible(self):
        """check if the user is logged in"""
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        """redirect to login page if user doesn't have access"""
        return redirect(url_for('login', next=request.url))

    # enable view details
    can_view_details = True

    # CSRF Protection
    form_base_class = SecureForm
    can_create = False  # disable model creation
    can_delete = False  # disable model deletion
    column_list = ('id', 'car_id', 'detail', 'reported_datetime',
                   'completed', 'user_id', 'completed_datetime', 'Map', 'Direct')
    column_labels = {
        'reported_datetime': 'reported',
        'completed_datetime': 'completed',
        'user_id': 'done by (user_id)',
    }
    column_searchable_list = ['car_id', 'detail', 'completed']

    def render(self, template, **kwargs):
        """
        using extra js in render method allow use
        url_for that itself requires an app context
        """
        # self.extra_js = [url_for("static", filename="js/admin.js")]

        return super(ReportView, self).render(template, **kwargs)

    def _direct(view, context, model, name):
        """
        Add Direct buttons for each report row. This allows the user to direct to the location using google map
        """
        _html1 = '''
            <Button onclick="window.location.href = 'https://www.google.com/maps?saddr=My+Location&daddr={lat}, {lng}';">Get Direction</button
        '''.format(lat=model.reported.lat, lng=model.reported.lng)

        return Markup(_html1)

    def _map(view, context, model, name):
        """
        Add Map buttons for each car row to display map
        """
        report_url = url_for('map')
        _html2 = '''
            <form id="mapForm" action="{report_url}" method="POST">
                <input id="lat" type="hidden" name="lat" value={lat} />
                <input id="lng" type="hidden" name="lng" value={lng} />
                <input id="make" type="hidden" name="make" value="{make}" />
                <Button>See Map</button>
            </form
        '''.format(report_url=report_url, lat=model.reported.lat, lng=model.reported.lng, make=model.reported.make)

        return Markup(_html2)

    column_formatters = {
        'Direct': _direct,
        'Map': _map,
    }

    form_args = dict(
        car_id=dict(validators=[DataRequired()]),
        detail=dict(validators=[DataRequired(), Regexp('^[\w\s]+$')]),
        completed=dict(validators=[DataRequired()]),
        datetime=dict(validators=[DataRequired()]),
    )


class CarryView(BaseView):
    """
       Flask-Admin Custom Menu for going back to the customer website
    """
    @expose('/')
    def index(self):
        return redirect(url_for('home'))


class LogoutView(BaseView):
    """
       Flask-Admin Custom Menu for logging out
    """
    @expose('/')
    def index(self):
        return redirect(url_for('logout'))


class QRCodeView(BaseView):
    """
       Flask-Admin Custom Menu for QR code
    """
    @expose('/')
    def index(self):
        print()
        profile_string = "{id: %s, username: '%s', email: '%s', firstname: '%s', lastname: '%s', auth: '%s')" % (
            current_user.id, current_user.username, current_user.email, current_user.firstname, current_user.lastname, current_user.auth)
        # Generate QR code
        url = pyqrcode.create(profile_string)
        url_path = "carry/static/image/qrcode/%s.png" % (current_user.id)
        # Create and save the png file naming "myqr.png"
        url.png(url_path, scale=6)
        return self.render('admin/qr_code.html')


class SearchView(BaseView):
    """
       Flask-Admin Custom Menu for searching cars
    """
    @expose('/')
    def index(self):
        search = speakToSearch()
        return redirect(url_for('car.index_view', search=search))


class MyHomeView(AdminIndexView):
    """
       Flask-Admin Custom Index View for dashboard page
    """
    @expose('/')
    @login_required
    def index(self):
        """
        Retieve all the useful data to draw diagrams and graphs
        """
        recentBookings = DatabaseUtils().getAllRecentBookings(db)
        pastBookings = DatabaseUtils().getAllPastBookings(db)
        booking_comparison = compare(len(recentBookings), len(pastBookings))

        recentUsers = DatabaseUtils().getAllRecentUsers(db)
        pastUsers = DatabaseUtils().getAllPastUsers(db)
        user_comparison = compare(len(recentUsers), len(pastUsers))

        todaySales = getSales(DatabaseUtils().getTodayBookings(db))
        yesterdaySales = getSales(DatabaseUtils().getYesterdayBookings(db))
        sales_comparison = compare(todaySales, yesterdaySales)

        recentDuration = getDuration(recentBookings)
        pastDuration = getDuration(pastBookings)
        duration_comparison = compare(recentDuration, pastDuration)

        sales_list = DatabaseUtils().getSalesList(db)
        booking_list = DatabaseUtils().getBookingList(db)

        cancel_list = DatabaseUtils().getCancellationRates(db)
        car_profit_list = DatabaseUtils().getProfitPerCarList(db)
        return self.render('admin/index.html', bookings=recentBookings, users=recentUsers,
                           sales=todaySales, duration=recentDuration, booking_comparison=booking_comparison, user_comparison=user_comparison,
                           sales_comparison=sales_comparison, duration_comparison=duration_comparison, sales_list=sales_list, booking_list=booking_list,
                           cancel_list=cancel_list, car_profit_list=car_profit_list)


def compare(new, old):
    """ A method for comparing two figures and return the percentage of the difference"""
    if old != 0 and new != 0:
        if (new > old):
            return new/old * 100
        else:
            return - (new/old * 100)
    elif old == 0 and new != 0:
        return new * 100
    elif new == 0 and old != 0:
        return - (old * 100)
    else:
        return 0


def getSales(bookings):
    """ A method for getting total revenue of bookings being input"""
    total = 0

    for booking in bookings:
        total += booking.total_cost

    return total


def getDuration(bookings):
    """ A method for getting total duration of bookings being input"""
    total = 0
    for booking in bookings:
        total += booking.duration

    return total


def send_notification_via_pushbullet(title, body, url):
    """ Sending notification via pushbullet."""
    data_send = {"type": "note", "title": title, "body": body, "url": url}

    resp = requests.post('https://api.pushbullet.com/v2/pushes', data=json.dumps(data_send),
                         headers={'Authorization': 'Bearer ' + os.environ.get('PUSHBULLET_API_ACCESS_TOKEN'),
                                  'Content-Type': 'application/json'})
    if resp.status_code != 200:
        raise Exception('Something wrong')
    else:
        return True


def speakToSearch():
    """ A method for voice recognition to search """
    # To test searching without the microphone uncomment this line of code
    # return input("Enter the first name to search for: ")

    # Set the device ID of the mic that we specifically want to use to avoid ambiguity
    for i, microphone_name in enumerate(sr.Microphone.list_microphone_names()):
        if(microphone_name == "default"):
            device_id = i
            break

    # obtain audio from the microphone
    r = sr.Recognizer()
    with sr.Microphone(device_index=device_id) as source:
        # clear console of errors
        subprocess.run("clear")

        # wait for a second to let the recognizer adjust the
        # energy threshold based on the surrounding noise level
        r.adjust_for_ambient_noise(source)

        print("Say something to search for.")
        try:
            audio = r.listen(source, timeout=2.2)
        except sr.WaitTimeoutError:
            return None

    # recognize speech using Google Speech Recognition
    search = None
    try:
        # for testing purposes, we're just using the default API key
        # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
        # instead of `r.recognize_google(audio)`
        search = r.recognize_google(audio)
    except(sr.UnknownValueError, sr.RequestError):
        pass
    finally:
        return search


@app.route("/admin/report/new", methods=['GET', 'POST'])
@login_required
def report():
    """ A http request page to creating a new report"""
    if (request.method == "POST"):
        report = DatabaseUtils().newReport(
            db, request.form.get('car_id'), request.form.get('detail'))
        message = "New issue has been reported."
        url = "http://localhost:5000/admin/report/details/?id={}&url=%2Fadmin%2Freport%2F".format(
            report.id)
        send_notification_via_pushbullet("Report", message, url)
    return redirect(url_for('report.index_view'))


@app.route("/admin/car/search")
@login_required
def search():
    """ A http request page to search a car"""
    search = speakToSearch()
    print(search)
    return redirect(url_for('car.index_view', search=search))


@app.route("/admin/car/map", methods=['GET', 'POST'])
@login_required
def map():
    """ Car location map page"""
    latitude = request.form.get('lat')
    longitude = request.form.get('lng')
    make = request.form.get('make')
    print(make)
    map = Map(
        identifier="map",
        lat=latitude,
        lng=longitude,
        zoom=15,
        style="height:800px;width:800px;margin:0;",
        markers=[(latitude, longitude)],
    )
    return render_template('admin/car_map.html', title='Map', map=map, make=make)


admin = Admin(app, index_view=MyHomeView(
    name="Dashboard"), template_mode='bootstrap3')

admin.add_view(UserView(model=User, session=db.session))
admin.add_view(CarView(model=Car, session=db.session))
admin.add_view(BookingView(model=Booking, session=db.session))
admin.add_view(LogView(model=Log, session=db.session))
admin.add_view(ReportView(model=Report, session=db.session))
admin.add_view(CarryView(name="Carry"))
admin.add_view(SearchView(name="Quick Search"))
admin.add_view(QRCodeView(name="QR Code"))
admin.add_view(LogoutView(name="Logout"))
