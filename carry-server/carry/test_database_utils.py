from carry import app, db
import pymysql
import unittest
from datetime import datetime
from carry.database_utils import DatabaseUtils
from carry.admin_routes import send_notification_via_pushbullet

# python3 -m unittest carry/test_database_utils.py


class TestDatabaseUtils(unittest.TestCase):
    """This testcase is created by subclassing unittest.TestCase

    .. note::

        To run this test class, enter this command in the project directory.

        $ python3 -m unittest carry/test_database_utils.py
    """
    @classmethod
    def setUpClass(self):
        """A class method called before tests in an individual class are run.

        setUpClass is called with the class as the only argument and must be decorated as a classmethod()
        """
        # new cloud configuration for testing
        app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://home:1234@34.87.247.250:3306/test'
        db.create_all()
        self.app = app.test_client()

    @classmethod
    def tearDownClass(self):
        """A class method called after tests in an individual class have run.

        tearDownClass is called with the class as the only argument and must be decorated as a classmethod():
        """
        db.session.remove()
        db.drop_all()

    def test_database_a(self):
        """A test method if database configuration is set to the test database"""
        self.assertEqual(app.config['SQLALCHEMY_DATABASE_URI'],
                         'mysql+pymysql://home:1234@34.87.247.250:3306/test')

    def test_database_b_registerUser(self):
        """A test method for user registration"""
        user = DatabaseUtils().register(db, 'testuser', 'test@email.com',
                                        'QDn38DK398FKS', 'test', 'user')
        self.assertTrue(user)

    def test_database_d_findUser(self):
        """A test method for finding user"""
        user = DatabaseUtils().findUser(db, 'testuser')
        self.assertTrue(user)

    def test_database_e_getUser(self):
        """A test method for getting user"""
        user = DatabaseUtils().getUser(db, 1)
        self.assertTrue(user)

    def test_database_f_dupliUser(self):
        """A test method for validating duplicate user"""
        user = DatabaseUtils().register(db, 'testuser', 'test@email.com',
                                        'QDn38DK398FKS', 'test', 'user')
        self.assertFalse(user)

    def test_database_g_createCar(self):
        """A test method for creating a new car"""
        car = DatabaseUtils().createNewCar(db, 'Kia Carnival', 'Minivan', 'Black', 7,
                                           5.3, '159 Grey St', 'East Melbourne', 'VIC', '3002', -37.811930, 144.984460)
        self.assertTrue(car)

    def test_database_h_getCar(self):
        """A test method for getting car"""
        car = DatabaseUtils().getCar(db, 1)
        self.assertTrue(car)

    def test_database_i_searchCar(self):
        """A test method for searching car details"""
        cars = DatabaseUtils().getAllCars(db, 'Kia')
        self.assertTrue(cars)

    def test_database_j_newBooking(self):
        """A test method for creating a new booking"""
        booking = DatabaseUtils().newBooking(db, "200502019239201", 1, 1, datetime(
            2020, 5, 20, 15, 0, 0), datetime(2020, 5, 20, 17, 0, 0), datetime.now(), 2, 14.90)
        self.assertTrue(booking)

    def test_database_k_addCalendarBooking(self):
        """A test method for adding calendar event id to the existing booking"""
        DatabaseUtils().addCalendarEventId(db, 1, 'AKEN834DKEN291KDJF')
        booking = DatabaseUtils().getBooking(db, 1)
        self.assertEqual(booking.calendar_eid, 'AKEN834DKEN291KDJF')

    def test_database_l_getMyBookings(self):
        """A test method for getting all bookings by the user"""
        bookings = DatabaseUtils().getMyBookings(db, 1)
        self.assertTrue(bookings)

    def test_database_m_getBookedCar(self):
        """A test method for getting booked car during the period"""
        cars = DatabaseUtils().getBookedCars(db, datetime(
            2020, 5, 20, 15, 0, 0), datetime(2020, 5, 20, 17, 0, 0))
        self.assertTrue(cars)

    def test_database_n_cancelBooking(self):
        """A test method for cancelling the booking"""
        booking = DatabaseUtils().cancelBooking(db, 1)
        self.assertTrue(booking.cancelled)

    def test_database_o_getMyPastBookings(self):
        """A test method for getting past bookings"""
        bookings = DatabaseUtils().getMyPastBookings(db, 1, datetime.now())
        self.assertTrue(bookings)

    def test_database_p_getCurrentBooking(self):
        """A test method for getting current booking allocated to specific car and user"""
        bookings = DatabaseUtils().getCurrentBooking(db, 1, 1, datetime.now())
        self.assertFalse(bookings)

    def test_database_q_logging(self):
        """A test method for getting current booking allocated to specific car and user"""
        log = DatabaseUtils().logging(db, 1, 1, 1, -13.00, 14.65, 'unlock', datetime.now())
        self.assertTrue(log)

    def test_database_r_getAllRecentBookings(self):
        """A test method for getting recent booking upto 30 days ago)"""
        bookings = DatabaseUtils().getAllRecentBookings(db)
        self.assertEqual(bookings, [])

    def test_database_s_getAllPastBookings(self):
        """A test method for getting past booking (between 30 - 60 days ago)"""
        bookings = DatabaseUtils().getAllRecentBookings(db)
        self.assertEqual(bookings, [])

    def test_database_t_getTodayBookings(self):
        """A test method for getting booking being made today"""
        bookings = DatabaseUtils().getTodayBookings(db)
        self.assertEqual(bookings, [])

    def test_database_u_getYesterdayBookings(self):
        """A test method for getting booking being made yesterday"""
        bookings = DatabaseUtils().getYesterdayBookings(db)
        self.assertEqual(bookings, [])

    def test_database_v_getAllRecentUsers(self):
        """A test method for getting users registered in 7 days"""
        users = DatabaseUtils().getAllRecentUsers(db)
        self.assertTrue(users)

    def test_database_w_getAllPastUsers(self):
        """A test method for getting users registered (7 - 14 days ago)"""
        users = DatabaseUtils().getAllPastUsers(db)
        self.assertEqual(users, [])

    def test_database_x_getSalesList(self):
        """A test method for getting monthly sales from bookings for 6 months"""
        sales = DatabaseUtils().getSalesList(db)
        self.assertTrue(sales)

    def test_database_y_getBookingList(self):
        """A test method for getting number of bookings monthly for 6 months"""
        booking_list = DatabaseUtils().getBookingList(db)
        self.assertTrue(booking_list)

    def test_database_z_getCancellationRates(self):
        """A test method for getting total number of bookings, cancellation on a monthly basis"""
        booking = DatabaseUtils().getCancellationRates(db)
        self.assertTrue(booking)

    def test_database_za_newReport(self):
        """A test method for creating a new report"""
        report = DatabaseUtils().newReport(db, 1, "test deatil")
        self.assertTrue(report)

    def test_database_zb_completeReport(self):
        """A test method for completing report"""
        report = DatabaseUtils().completeReport(db, 1, 1)
        self.assertTrue(report.completed)

    def test_database_zc_updateMacAddr(self):
        engineer = DatabaseUtils().register(db, 'testengineer', 'engineer@email.com',
                                            'QDnDsDK398FKS', 'test', 'en')
        engineer.auth = "engineer"
        db.session.commit()
        DatabaseUtils().updateMacAddr(db, engineer.id, "d3:23:b5:12:00:2a")
        self.assertTrue(engineer.macAddr)

    def test_database_zd_getAllEngineers(self):
        """A test method for getting all engineers"""
        engineers = DatabaseUtils().getAllEngineers(db)
        self.assertTrue(engineers)

    def test_database_ze_loginWithBluetooth(self):
        """A test method for logging in with bluetooth"""
        engineer = DatabaseUtils().loginWithBluetooth(db, "d3:23:b5:12:00:2a")
        self.assertTrue(engineer)

    def test_route_1_logout(self):
        """ a method which checks if logout works properly.

        Returns:
            Boolean

        >>> follow_redirects=True
        return True if it redirects successfully
        return False if not.
        """
        return self.app.get(
            '/logout',
            follow_redirects=True
        )

    def test_route_2_login(self):
        """ a method which checks if logout works properly.

        Returns:
            Boolean

        >>> follow_redirects=True
        return True if it redirects successfully
        return False if not.
        """
        return self.app.get(
            '/login',
            follow_redirects=True
        )

    def test_route_3_index(self):
        """ a method which checks if index page works properly.

        Returns:
            Boolean

        >>> follow_redirects=True
        return True if it redirects successfully
        return False if not.
        """
        return self.app.get(
            '/',
            follow_redirects=True
        )

    def test_route_4_register(self):
        """ a method which checks if registration page works properly.

        Returns:
            Boolean

        >>> follow_redirects=True
        return True if it redirects successfully
        return False if not.
        """
        return self.app.get(
            '/',
            follow_redirects=True
        )

    def test_route_5_home(self):
        """ a method which checks if find car page works properly.

        Returns:
            Boolean

        >>> follow_redirects=True
        return True if it redirects successfully
        return False if not.
        """
        return self.app.get(
            '/home',
            follow_redirects=True
        )

    def test_route_6_profile(self):
        """ a method which checks if profile page works properly.

        Returns:
            Boolean

        >>> follow_redirects=True
        return True if it redirects successfully
        return False if not.
        """
        return self.app.get(
            '/profile',
            follow_redirects=True
        )

    def test_route_7_booking(self):
        """ a method which checks if booking page works properly.

        Returns:
            Boolean

        >>> follow_redirects=True
        return True if it redirects successfully
        return False if not.
        """
        return self.app.get(
            '/booking',
            follow_redirects=True
        )

    def test_route_8_booking_detail(self):
        """ a method which checks if booking detail page works properly.

        Returns:
            Boolean

        >>> follow_redirects=True
        return True if it redirects successfully
        return False if not.
        """
        return self.app.get(
            '/booking/detail',
            follow_redirects=True
        )

    def test_route_9_my_bookings(self):
        """ a method which checks if mybookings page works properly.

        Returns:
            Boolean

        >>> follow_redirects=True
        return True if it redirects successfully
        return False if not.
        """
        return self.app.get(
            '/my_bookings',
            follow_redirects=True
        )

    def test_route_10_admin(self):
        """ a method which checks if admin dashboard page works properly.

        Returns:
            Boolean

        >>> follow_redirects=True
        return True if it redirects successfully
        return False if not.
        """
        return self.app.get(
            '/admin',
            follow_redirects=True
        )

    def test_route_11_admin_user(self):
        """ a method which checks if admin user page works properly.

        Returns:
            Boolean

        >>> follow_redirects=True
        return True if it redirects successfully
        return False if not.
        """
        return self.app.get(
            '/admin/user',
            follow_redirects=True
        )

    def test_route_12_admin_car(self):
        """ a method which checks if admin car page works properly.

        Returns:
            Boolean

        >>> follow_redirects=True
        return True if it redirects successfully
        return False if not.
        """
        return self.app.get(
            '/admin/car',
            follow_redirects=True
        )

    def test_route_13_admin_log(self):
        """ a method which checks if admin log page works properly.

        Returns:
            Boolean

        >>> follow_redirects=True
        return True if it redirects successfully
        return False if not.
        """
        return self.app.get(
            '/admin/log',
            follow_redirects=True
        )

    def test_route_14_admin_report(self):
        """ a method which checks if admin log page works properly.

        Returns:
            Boolean

        >>> follow_redirects=True
        return True if it redirects successfully
        return False if not.
        """
        return self.app.get(
            '/admin/report',
            follow_redirects=True
        )

    def test_route_15_admin_(self):
        """ a method which checks if admin log page works properly.

        Returns:
            Boolean

        >>> follow_redirects=True
        return True if it redirects successfully
        return False if not.
        """
        return self.app.get(
            '/admin/report',
            follow_redirects=True
        )

    def test_pushbullet(self):
        """ a method which checks if pushbullet works properly.

        Returns:
            Boolean

        >>> follow_redirects=True
        return True if it redirects successfully
        return False if not.
        """
        return send_notification_via_pushbullet("test title", "test body", "test URL")


if __name__ == '__main__':
    loader = unittest.TestLoader()
    loader.sortTestMethodsUsing = None
    unittest.main(testLoader=loader)
