from carry.models import User, Car, Booking, Log, Report, CarSchema
from flask_login import current_user
from datetime import datetime, timedelta
from sqlalchemy_filters import apply_filters
from sqlalchemy import extract, func


class DatabaseUtils:
    """Database Class

    .. note::

        This class only contains methods for database connection.
    """

    def getUser(self, db, user_id):
        """A function for getting user by searching user_id

        :param db: Database
        :type db: Database object, essential
        :param user_id: User ID
        :type user_id: int, essential
        :return: User object if succesfully found, `None` otherwise
        :rtype: dictionary

        """
        user = User.query.filter_by(id=user_id).first()
        if user:
            return user
        else:
            return None

    def findUser(self, db, username):
        """A function for finding user by searching username or user email

        :param db: Database
        :type db: Database object, essential
        :param username: Username / User email
        :type username: string, essential
        :return: User object if succesfully found, `None` otherwise
        :rtype: dictionary

        """
        filter_spec = [
            {'or': [
                {'model': 'User', 'field': 'email', 'op': '==',
                 'value': username},
                {'model': 'User', 'field': 'username', 'op': '==',
                 'value': username},
            ]
            }
        ]
        filtered_query = apply_filters(db.session.query(User), filter_spec)
        user = filtered_query.first()
        if user:
            return user
        else:
            return None

    def createNewCar(self, db, make, body_type, colour, seats, cost, address, suburb, state, postcode, lat, lng):
        """A function for creating a new car object in the database

        :param db: Database
        :type db: Database object, essential
        :param make: Car Make
        :type make: string, essential
        :param body_type: Car Body_type
        :type body_type: string, essential
        :param colour: Car Colour
        :type colour: string, essential
        :param seats: No. Car Seats
        :type seats: int, essential
        :param cost: Car Hourly Cost
        :type cost: float, essential
        :param address: Car Address
        :type address: String, essential
        :param suburb: Suburb
        :type suburb: String, essential
        :param state: State
        :type state: String, essential
        :param postcode: Postcode
        :type postcode: String, essential
        :param lat: Latitude
        :type lat: float, essential
        :param lng: Longitude
        :type lng: float, essential
        :return: Car object if succesfully created, `None` otherwise
        :rtype: dictionary

        """
        car = Car(make=make, body_type=body_type, colour=colour, seats=seats, cost=cost,
                  address=address, suburb=suburb, state=state, postcode=postcode, lat=lat, lng=lng)
        db.session.add(car)
        try:
            db.session.commit()
        except:
            db.session.rollback()
            db.session.flush()
            return None
        return car

    def getCar(self, db, car_id):
        """A function for getting car by searching car_id

        :param db: Database
        :type db: Database object, essential
        :param car_id: Car ID
        :type car_id: int, essential
        :return: Car object if succesfully found, `None` otherwise
        :rtype: dictionary

        """
        car = Car.query.filter_by(id=car_id).first()
        if car:
            return car
        else:
            return None

    def getBooking(self, db, booking_id):
        """A function for getting booking by searching booking_id

        :param db: Database
        :type db: Database object, essential
        :param booking_id: Booking ID
        :type booking_id: int, essential
        :return: Booking object if succesfully found, `None` otherwise
        :rtype: dictionary

        """
        booking = Booking.query.filter_by(id=booking_id).first()
        if booking:
            return booking
        else:
            return None

    def register(self, db, username, email, hashed_password, firstname, lastname):
        """A function for registering a new user in the database

        :param db: Database
        :type db: Database object, essential
        :param username: Username
        :type username: string, essential
        :param email: User Email
        :type email: string, essential
        :param hashed_password: Hashed Password
        :type hashed_password: string, essential
        :param firstname: Firstname
        :type firstname: string, essential
        :param lastname: Lastname
        :type lastname: string, essential
        :return: User object if succesfully created, `None` otherwise
        :rtype: dictionary

        """
        user = User(username=username, email=email,
                    password=hashed_password, firstname=firstname, lastname=lastname)
        db.session.add(user)
        try:
            db.session.commit()
        except:
            db.session.rollback()
            db.session.flush()
            return None
        return user

    def updateProfile(self, db, profile_url, firstname, lastname, location):
        """A function for updating an existing user profile in the database

        :param db: Database
        :type db: Database object, essential
        :param profile_url: Profile URL
        :type profile_url: string, optional
        :param firstname: Firstname
        :type firstname: string, essential
        :param lastname: Lastname
        :type lastname: string, essential
        :param location: Location
        :type location: string, essential
        :return: User object if succesfully created, `None` otherwise
        :rtype: dictionary

        """
        if profile_url:
            current_user.profile_url = profile_url
        current_user.firstname = firstname
        current_user.lastname = lastname
        current_user.location = location
        try:
            db.session.commit()
        except:
            db.session.rollback()
            db.session.flush()
            return None
        return current_user

    def getAllCars(self, db, search_input):
        """A function for getting cars by searching features

        :param db: Database
        :type db: Database object, essential
        :param search_input: Search Input
        :type search_input: string, essential
        :return: List of Car if succesfully found, an empty list otherwise
        :rtype: list of dictionary

        """
        filter_spec = [{
            'or': [
                {'model': 'Car', 'field': 'id', 'op': 'like',
                    'value': '%'+search_input+'%'},
                {'model': 'Car', 'field': 'make', 'op': 'like',
                    'value': '%'+search_input+'%'},
                {'model': 'Car', 'field': 'body_type',
                    'op': 'like', 'value': '%'+search_input+'%'},
                {'model': 'Car', 'field': 'colour',
                    'op': 'like', 'value': '%'+search_input+'%'},
                {'model': 'Car', 'field': 'seats',
                    'op': 'like', 'value': '%'+search_input+'%'},
                {'model': 'Car', 'field': 'cost',
                    'op': 'like', 'value': '%'+search_input+'%'},
            ]},
        ]
        filtered_query = apply_filters(
            db.session.query(Car), filter_spec)
        cars = filtered_query.all()
        if cars:
            return cars
        else:
            return []

    def getBookedCars(self, db, start_datetime, end_datetime):
        """A function for getting booked cars by searching start_datetime and end_datetime

        :param db: Database
        :type db: Database object, essential
        :param start_datetime: Start Datetime
        :type start_datetime: datetime, essential
        :param end_datetime: End Datetime
        :type end_datetime: datetime, essential
        :return: List of Booked Car if succesfully found,  an empty list otherwise
        :rtype: list of dictionary

        """
        filter_spec = [
            {'or': [
                {'and': [
                    {'model': 'Booking', 'field': 'start_datetime', 'op': '<=',
                        'value': start_datetime},
                    {'model': 'Booking', 'field': 'end_datetime', 'op': '>',
                        'value': start_datetime},
                    {'model': 'Booking', 'field': 'finished', 'op': '==',
                        'value': False},
                    {'model': 'Booking', 'field': 'cancelled', 'op': '==',
                        'value': False},
                ]},
                {'and': [
                    {'model': 'Booking', 'field': 'start_datetime', 'op': '<',
                        'value': end_datetime},
                    {'model': 'Booking', 'field': 'end_datetime', 'op': '>=',
                        'value': end_datetime},
                    {'model': 'Booking', 'field': 'finished', 'op': '==',
                        'value': False},
                    {'model': 'Booking', 'field': 'cancelled', 'op': '==',
                        'value': False},
                ]},
                {'and': [
                    {'model': 'Booking', 'field': 'start_datetime', 'op': '>',
                        'value': start_datetime},
                    {'model': 'Booking', 'field': 'end_datetime', 'op': '<',
                        'value': end_datetime},
                    {'model': 'Booking', 'field': 'finished', 'op': '==',
                        'value': False},
                    {'model': 'Booking', 'field': 'cancelled', 'op': '==',
                        'value': False},
                ]},
            ]}
        ]
        filtered_query = apply_filters(db.session.query(
            Car).join(Booking), filter_spec)
        bookedCars = filtered_query.all()

        if bookedCars:
            return bookedCars
        else:
            return []

    def getMyBookings(self, db, user_id):
        """A function for getting all bookings made by an user

        :param db: Database
        :type db: Database object, essential
        :param user_id: User ID
        :type user_id: int, essential
        :return: List of Bookings if succesfully found, an empty list otherwise
        :rtype: list of dictionary

        """
        filter_spec = [
            {'model': 'Booking', 'field': 'user_id', 'op': '==',
             'value': user_id}
        ]
        filtered_query = apply_filters(
            db.session.query(Booking, Car).join(Car).order_by(Booking.start_datetime), filter_spec)
        bookings = filtered_query.all()
        if bookings:
            return bookings
        else:
            return []

    def getMyPastBookings(self, db, user_id, now):
        """A function for getting all past bookings which are cancelled or finished made by an user

        :param db: Database
        :type db: Database object, essential
        :param user_id: User ID
        :type user_id: int, essential
        :param now: Current Datetime
        :type now: datetime, essential
        :return: List of Past Bookings if succesfully found, an empty list otherwise
        :rtype: list of dictionary

        """

        filter_spec = [
            {'and': [
                {'model': 'Booking', 'field': 'user_id', 'op': '==',
                 'value': user_id},
                {'or': [
                    {'model': 'Booking', 'field': 'finished', 'op': '==',
                     'value': True},
                    {'model': 'Booking', 'field': 'cancelled', 'op': '==',
                     'value': True},
                    {'model': 'Booking', 'field': 'end_datetime', 'op': '<',
                     'value': now}
                ]}
            ]
            }
        ]
        filtered_query = apply_filters(
            db.session.query(Booking, Car).join(Car).order_by(Booking.start_datetime), filter_spec)
        past_bookings = filtered_query.all()
        if past_bookings:
            # If booking has not been finished successfully, change the status of the booking to cancelled
            for booking in past_bookings:
                if booking.Booking.cancelled == False and booking.Booking.finished == False and booking.Booking.started == False:
                    unSuccessfulBooking = Booking.query.filter_by(
                        id=booking.Booking.id).first()
                    unSuccessfulBooking.cancelled = True
                    db.session.commit()

            return past_bookings
        else:
            return []

    def newBooking(self, db, reference, user_id, car_id, start_datetime, end_datetime, booking_datetime, duration, total_cost):
        """A function for creating a new booking object in the database

        :param db: Database
        :type db: Database object, essential
        :param user_id: User ID
        :type user_id: int, essential
        :param car_id: Car ID
        :type car_id: int, essential
        :param start_datetime: Booking Start Datetime
        :type start_datetime: datetime, essential
        :param end_datetime: Booking End Datetime
        :type end_datetime: datetime, essential
        :param booking_datetime: Booking Made Datetime
        :type booking_datetime: datetime, essential
        :param duration: Booking Duration
        :type duration: int, essential
        :param total_cost: Booking Total Cost
        :type total_cost: float, essential
        :return: Booking Object
        :rtype: dictionary

        """
        booking = Booking(reference=reference, user_id=user_id, car_id=car_id, total_cost=total_cost, start_datetime=start_datetime,
                          end_datetime=end_datetime, booking_datetime=booking_datetime, duration=duration)
        filter_spec = [
            {'and': [
                {'model': 'Booking', 'field': 'user_id', 'op': '==',
                 'value': user_id},
                {'model': 'Booking', 'field': 'car_id', 'op': '==',
                 'value': car_id},
                {'model': 'Booking', 'field': 'start_datetime', 'op': '==',
                 'value': start_datetime},
                {'model': 'Booking', 'field': 'end_datetime', 'op': '==',
                 'value': end_datetime},
                {'model': 'Booking', 'field': 'cancelled', 'op': '==',
                 'value': False},
                {'model': 'Booking', 'field': 'finished', 'op': '==',
                 'value': False},
            ]
            }
        ]
        filtered_query = apply_filters(
            db.session.query(Booking), filter_spec)
        exists = filtered_query.first()
        if exists:
            return exists
        else:
            db.session.add(booking)
            db.session.commit()
        return booking

    def addCalendarEventId(self, db, booking_id, eid):
        """A function for adding a Google Calendar Event ID

        :param db: Database
        :type db: Database object, essential
        :param booking_id: Booking ID
        :type booking_id: int, essential
        :param eid: Google Calendar Event ID
        :type eid: int, essential
        :return: Booking Object
        :rtype: dictionary

        """
        booking = Booking.query.filter_by(id=booking_id).first()
        booking.calendar_eid = eid
        db.session.commit()
        return booking

    def cancelBooking(self, db, booking_id):
        """A function for cancelling a booking

        :param db: Database
        :type db: Database object, essential
        :param booking_id: Booking ID
        :type booking_id: int, essential
        :return: Booking Object
        :rtype: dictionary

        """
        booking = self.getBooking(db, booking_id)
        booking.cancelled = True
        booking.calendar_eid = None
        db.session.commit()
        return booking

    def getCurrentBooking(self, db, user_id, car_id, now):
        """A function for getting a current booking assigned to specific car and user

        :param db: Database
        :type db: Database object, essential
        :param user_id: User ID
        :type user_id: int, essential
        :param car_id: Car ID
        :type car_id: int, essential
        :param now: Current Datetime
        :type now: datetime, essential
        :return: Booking if succesfully found, None otherwise
        :rtype: list of dictionary

        """

        filter_spec = [
            {'and': [
                {'model': 'Booking', 'field': 'user_id', 'op': '==',
                 'value': user_id},
                {'model': 'Booking', 'field': 'finished', 'op': '==',
                 'value': False},
                {'model': 'Booking', 'field': 'cancelled', 'op': '==',
                 'value': False},
                {'model': 'Booking', 'field': 'car_id', 'op': '==',
                 'value': car_id},
                {'model': 'Booking', 'field': 'start_datetime', 'op': '<',
                 'value': now},
                {'model': 'Booking', 'field': 'end_datetime', 'op': '>',
                 'value': now}
            ]
            }
        ]
        filtered_query = apply_filters(
            db.session.query(Booking), filter_spec)
        booking = filtered_query.first()
        if booking:
            return booking
        else:
            return []

    def logging(self, db, user_id, car_id, booking_id, lat, lng, status, datetime):
        """A function for logging user activities

        :param db: Database
        :type db: Database object, essential
        :param user_id: User ID
        :type user_id: int, essential
        :param car_id: Car ID
        :type car_id: int, essential
        :param booking_id: Booking ID
        :type booking_id: int, essential
        :param lat: Latitude
        :type lat: float, essential
        :param lng: Longitude
        :type lng: float, essential
        :param status: Car Status
        :type status: string, essential
        :param datetime: Current Datetime
        :type datetime: datetime, essential
        :return: Log object if succesfully created, `None` otherwise
        :rtype: dictionary

        """
        log = Log(user_id=user_id, car_id=car_id, booking_id=booking_id, lat=lat,
                  lng=lng, status=status, datetime=datetime)
        db.session.add(log)
        try:
            db.session.commit()
        except:
            db.session.rollback()
            db.session.flush()
            return None
        return log

    def getAllRecentBookings(self, db):
        """A function for getting all recent bookings

        :param db: Database
        :type db: Database object, essential
        :return: Bookings if succesfully found, None otherwise
        :rtype: list of dictionary

        """
        bookings = Booking.query.filter(Booking.booking_datetime >= datetime.today() - timedelta(days=30),
                                        Booking.cancelled == False).all()
        return bookings

    def getAllPastBookings(self, db):
        """A function for getting all past bookings

        :param db: Database
        :type db: Database object, essential
        :return: Bookings if succesfully found, an empty list otherwise
        :rtype: list of dictionary

        """
        bookings = Booking.query.filter(Booking.booking_datetime >= datetime.today() - timedelta(days=60),
                                        Booking.booking_datetime < datetime.today() - timedelta(days=30),
                                        Booking.cancelled == False).all()
        if bookings:
            return bookings
        else:
            return []

    def getTodayBookings(self, db):
        """A function for getting today's bookings

        :param db: Database
        :type db: Database object, essential
        :return: Bookings if succesfully found, an empty list otherwise
        :rtype: list of dictionary

        """
        bookings = Booking.query.filter(Booking.booking_datetime >= datetime.today() - timedelta(days=1),
                                        Booking.booking_datetime <= datetime.today(),
                                        Booking.cancelled == False).all()
        if bookings:
            return bookings
        else:
            return []

    def getYesterdayBookings(self, db):
        """A function for getting yesterday's bookings

        :param db: Database
        :type db: Database object, essential
        :return: Bookings if succesfully found, an empty list otherwise
        :rtype: list of dictionary

        """
        bookings = Booking.query.filter(Booking.booking_datetime >= datetime.today() - timedelta(days=2),
                                        Booking.booking_datetime < datetime.today() - timedelta(days=1),
                                        Booking.cancelled == False).all()
        if bookings:
            return bookings
        else:
            return []

    def getAllRecentUsers(self, db):
        """A function for obtaining recent user (registered in 7 days) list

        :param db: Database
        :type db: Database object, essential
        :return: Users if succesfully found, an empty list otherwise
        :rtype: list of dictionary

        """
        users = User.query.filter(
            User.registered >= datetime.today() - timedelta(days=7)).all()
        if users:
            return users
        else:
            return []

    def getAllPastUsers(self, db):
        """A function for obtaining past user (registered in 7 - 14 days) list

        :param db: Database
        :type db: Database object, essential
        :return: Users if succesfully found, an empty list otherwise
        :rtype: list of dictionary

        """
        users = User.query.filter(User.registered >= datetime.today() - timedelta(days=14),
                                  User.registered < datetime.today() - timedelta(days=7)).all()
        if users:
            return users
        else:
            return []

    def getSalesList(self, db):
        """A function for obtaining list of sales

        :param db: Database
        :type db: Database object, essential
        :return: Sales list if succesfully found, an empty list otherwise
        :rtype: list of dictionary

        """
        today = datetime.now()
        month = int(today.month)

        sales = []
        for i in range(6):
            total = 0
            year = datetime.now().year
            month -= 1
            if(month <= 0):
                month += 12
                year -= 1

            bookings = db.session.query(Booking).filter(Booking.cancelled == False).filter(extract('year', Booking.booking_datetime) == year).filter(
                extract('month', Booking.booking_datetime) == month).all()

            for booking in bookings:
                total += booking.total_cost

            sales.insert(0, total)
            if i == 0:
                sales.insert(0, total)

        if sales:
            return sales
        else:
            return []

    def getBookingList(self, db):
        """A function for obtaining booking list

        :param db: Database
        :type db: Database object, essential
        :return: Monthly number of booking list for the last 6 months
        :rtype: list of integer

        """
        today = datetime.now()
        month = int(today.month)

        booking_list = []
        for i in range(6):
            year = datetime.now().year
            month -= 1
            if(month <= 0):
                month += 12
                year -= 1

            bookings = db.session.query(Booking).filter(Booking.cancelled == False).filter(extract('year', Booking.booking_datetime) == year).filter(
                extract('month', Booking.booking_datetime) == month).all()

            booking_list.insert(0, len(bookings))

        return booking_list

    def getProfitPerCarList(self, db):
        """A function for obtaining the profit per car list

        :param db: Database
        :type db: Database object, essential
        :return: Total Revenue Per Car
        :rtype: list of dictionary

        """
        car_profit_list = db.session.query(Car.make, func.sum(Booking.total_cost).label("total_cost")).join(Car).group_by(
            Car.id).all()
        return car_profit_list

    def getCancellationRates(self, db):
        """A function for obtaining cancellation rates

        :param db: Database
        :type db: Database object, essential
        :return: Total number of booking, cancellation and cancellation Rate
        :rtype: list of dictionary

        """
        today = datetime.now()
        months = ['January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December']
        month = int(today.month)
        cancellationRates = []

        for i in range(6):
            year = datetime.now().year
            month -= 1
            if(month == 0):
                month += 12
                year -= 1

            bookings = db.session.query(Booking).filter(Booking.cancelled == False).filter(extract('year', Booking.booking_datetime) == year).filter(
                extract('month', Booking.booking_datetime) == month).all()

            cancelledBookings = db.session.query(Booking).filter(Booking.cancelled == True).filter(extract('year', Booking.booking_datetime) == year).filter(
                extract('month', Booking.booking_datetime) == month).all()

            rate = 0

            if (len(bookings) > 0 and len(cancelledBookings) > 0):
                rate = len(cancelledBookings) / len(bookings) * 100
                cancellationRates.append({'month': months[month-1], 'total': len(
                    bookings), 'cancel': len(cancelledBookings), 'rate': rate})
            elif (len(bookings) == 0):
                cancellationRates.append(
                    {'month': months[month-1], 'total': 0, 'cancel': 0, 'rate': 0})
            elif (len(cancelledBookings) == 0):
                cancellationRates.append(
                    {'month': months[month-1], 'total': len(bookings), 'cancel': 0, 'rate': 0})
            else:
                cancellationRates.append({'month': months[month-1], 'total': len(
                    bookings), 'cancel': len(cancelledBookings), 'rate': rate})

        return cancellationRates

    def newReport(self, db, car_id, detail):
        """A function for creating a new report

        :param db: Database
        :type db: Database object, essential
        :param car_id: Car ID
        :type car_id: int, essential
        :return: Report object which is just created
        :rtype: dictionary

        """
        report = Report(car_id=car_id, detail=detail,
                        reported_datetime=datetime.now(), completed_datetime=None)
        db.session.add(report)
        try:
            db.session.commit()
        except:
            db.session.rollback()
            db.session.flush()
            return None
        return report

    def completeReport(self, db, report_id, user_id):
        """A function for completing a report

        :param db: Database
        :type db: Database object, essential
        :param report_id: Report ID
        :type report_id: int, essential
        :param user_id: User ID
        :type user_id: int, essential
        :return: Report object which is just completed
        :rtype: dictionary

        """
        report = Report.query.filter_by(id=report_id).first()

        report.user_id = user_id
        report.completed = True
        report.completed_datetime = datetime.now()

        try:
            db.session.commit()
        except:
            db.session.rollback()
            db.session.flush()
            return None
        return report

    def getReports(self, db, car_id):
        """A function for retrieving reports for specific car

        :param db: Database
        :type db: Database object, essential
        :param car_id: Car ID
        :type car_id: int, essential
        :return: Report object which is just completed
        :rtype: dictionary
        
        """  
        reports = db.session.query(Report).filter(Report.completed == False).filter(Report.car_id == car_id).all()

        if reports:
            return reports
        else:
            return []

    def updateMacAddr(self, db, user_id, macAddr):
        """A function for updating mac address for engineers

        :param db: Database
        :type db: Database object, essential
        :param user_id: User ID
        :type user_id: int, essential
        :param macAddr: Mac Address
        :type macAddr: String, essential
        :return: User object which is just updated
        :rtype: dictionary

        """
        user = User.query.filter_by(id=user_id).first()
        user.macAddr = macAddr

        try:
            db.session.commit()
        except:
            db.session.rollback()
            db.session.flush()
            return None
        return user

    def getAllEngineers(self, db):
        """A function for getting all engineers

        :param db: Database
        :type db: Database object, essential
        :return: An array of Engineer objects
        :rtype: Array

        """
        engineers = User.query.filter_by(auth="engineer").all()
        return engineers

    def loginWithBluetooth(self, db, macAddr):
        engineer = User.query.filter_by(macAddr=macAddr).first()
        if engineer:
            return engineer
        else:
            return None
