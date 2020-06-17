from flask import request, make_response, jsonify
from carry import app, db
from carry.models import Booking
from flask_login import login_required
from carry.database_utils import DatabaseUtils

"""
.. module:: Fetch Methods

.. note::
    These methods are getting data from Front End
"""
@app.route("/booking/detail/event", methods=['POST'])
@login_required
def booking_detail_event():
    """Add a calendar event id to the existing booking if the user adds an event to Google Calendar."""
    req = request.get_json()
    # add Calendar event id to the existing booking
    DatabaseUtils().addCalendarEventId(db, req['description'], req['id'])
    res = make_response(jsonify(req), 200)
    return res


@app.route("/my_bookings/cancel", methods=['POST'])
@login_required
def my_bookings_cancel():
    """Cancel a booking by a user request."""
    req = request.get_json()
    DatabaseUtils().cancelBooking(db, req['id'])
    res = make_response(jsonify(req), 200)
    return res
