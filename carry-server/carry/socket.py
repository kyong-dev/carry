import socket
import json
from Crypto.Cipher import XOR
import base64
from sqlalchemy_filters import apply_filters
from carry.models import User, Booking, Log
from carry import db, bcrypt
import sys
import time
from carry.database_utils import DatabaseUtils
from datetime import datetime


"""
.. module:: Socket Methods

.. note::
    These methods are connecting to Agent Pis via UDP socket
"""

# Socket
UDP_IP = "0.0.0.0"
UDP_PORT = 5001
bufferSize = 1024

# Shared key between MP and APs
key = 'mOJGpG5HjCFQV7n0'


def background_thread():
    """Background Thread which runs to receive messages from Agent Pis"""
    UDPServerSocket = socket.socket(
        family=socket.AF_INET, type=socket.SOCK_DGRAM)
    UDPServerSocket.bind((UDP_IP, UDP_PORT))
    print(" * UDP server up and listening")

    while (True):
        bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
        message = bytesAddressPair[0]
        address = bytesAddressPair[1]
        receivedJsonString = message.decode()
        receivedJson = json.loads(receivedJsonString)
        clientIP = "Client IP Address:{}".format(address)
        print(address)
        print(clientIP)
        request = receivedJson["request"]
        print(receivedJson)
        if(request == "login"):
            # Decrypt the received encrypted password
            password = decrypt(key, receivedJson["password"].encode())
            user_credential(UDPServerSocket, address,
                            receivedJson["username"], password, receivedJson["car_id"])
        elif(request == "booking_id"):
            sendBookingID(UDPServerSocket, address,
                          request, receivedJson["user_id"], receivedJson["car_id"])
        elif(request == "report"):
            completeTask(UDPServerSocket, address,
                         request, receivedJson["user_id"], receivedJson["car_id"])
        elif(request == "getAllMacAddr"):
            getAllMacAddr(UDPServerSocket, address, request)
        elif(request == "registerMacAddr"):
            registerMacAddr(UDPServerSocket, address,
                         request, receivedJson["user_id"], receivedJson["macAddr"])
        elif(request == "loginWithBluetooth"):
            loginWithBluetooth(UDPServerSocket, address, request, receivedJson["macAddr"])
        elif(request == "lock" or request == "unlock" or request == "return"):
            statusUpdate(UDPServerSocket, address,
                         request, receivedJson["user_id"], receivedJson["car_id"], receivedJson["booking_id"], receivedJson["lat"], receivedJson["lng"], receivedJson["datetime"])
        else:
            msgFromServer = {"status": "Fail", "message": "Invalid Request"}
            sendJson(UDPServerSocket, address, msgFromServer)
            return True
        db.session.commit()


def user_credential(UDPServerSocket, address, username, password, car_id):
    """A function for validating user inputs from Agent Pis"""
    user = DatabaseUtils().findUser(db, username)
    if user == None:
        msgFromServer = {"login": False, "message": "User Not Found. Please try again.",
                         "user_id": None, "user_auth": None, "booking_id": None}
    else:
        if user.auth == "engineer":
            msgFromServer = {"login": True, "message": "Login Successful",
                                    "user_id": user.id, "user_auth": user.auth, "booking_id": None}
        else:
            if bcrypt.check_password_hash(user.password, password) == False:
                msgFromServer = {
                    "login": False, "message": "Wrong Password. Please try again.", "user_id": None, "booking_id": None}
            else:
                booking = DatabaseUtils().getCurrentBooking(db, user.id, car_id, datetime.now())
                if booking:
                    msgFromServer = {"login": True, "message": "Login Successful",
                                    "user_id": user.id, "user_auth": None, "booking_id": booking.id}
                    # start booking session
                else:
                    msgFromServer = {
                        "login": False, "message": "No Session Found. Booking Required", "user_id": None, "booking_id": None}
    sendJson(UDPServerSocket, address, msgFromServer)
    return True


def sendBookingID(UDPServerSocket, address, request, user_id, car_id):
    """A function for sending a booking id if there is current booking for specific user and car"""
    user = DatabaseUtils().getUser(db, int(user_id))
    booking = DatabaseUtils().getCurrentBooking(db, user_id, car_id, datetime.now())
    if (booking):
        msgFromServer = {
            "booking_id": booking.id,
            "name": user.firstname,
        }
    else:
        msgFromServer = {"booking_id": None}

    sendJson(UDPServerSocket, address, msgFromServer)
    return True


def completeTask(UDPServerSocket, address, request, user_id, car_id):
    """A function for completing a task"""
    reports = DatabaseUtils().getReports(db, car_id)

    if reports != []:
        for report in reports:
            report = DatabaseUtils().completeReport(db, report.id, user_id)

        msg = "Report #%s has been successfully completed" % (report.id)
        msgFromServer = {
            "message": msg
        }
    else:
        msgFromServer = {"message": "No issue is found with the car"}

    sendJson(UDPServerSocket, address, msgFromServer)
    return True


def registerMacAddr(UDPServerSocket, address, request, user_id, macAddr):
    """A function for registering mac address for engieneers"""
    user = DatabaseUtils().updateMacAddr(db, user_id, macAddr)

    if user != None:
        msg = "Mac Address has been successfully updated for User #%s" % (user.id)
        msgFromServer = {
            "message": msg
        }
    else:
        msgFromServer = {"message": "Error"}

    sendJson(UDPServerSocket, address, msgFromServer)
    return True


def getAllMacAddr(UDPServerSocket, address, request):
    """A function for getting all mac addresses for scanning"""
    engineers = DatabaseUtils().getAllEngineers(db)
    macAddrs = []
    for engineer in engineers:
        if engineer.macAddr != None:
            macAddrs.append(engineer.macAddr)
    msgFromServer = {"message": "Mac Addresses in the database", "macAddr": macAddrs}

    sendJson(UDPServerSocket, address, msgFromServer)
    return True


def loginWithBluetooth(UDPServerSocket, address, request, macAddr):
    """A function for logging in with bluetooth"""
    engineer = DatabaseUtils().loginWithBluetooth(db, macAddr)
    if engineer:
        msgFromServer = {"login": True, "message": "Login Successful",
                         "user_id": engineer.id, "user_auth": engineer.auth, "booking_id": None}
    else:
        msgFromServer = {"login": False, "message": "User Not Found. Register your mac address first.",
                         "user_id": None, "user_auth": None, "booking_id": None}
    sendJson(UDPServerSocket, address, msgFromServer)
    return True


def decrypt(key, ciphertext):
    """A function for decryption with shared key between Agent Pis and Master Pi"""
    cipher = XOR.new(key)
    return cipher.decrypt(base64.b64decode(ciphertext))


def statusUpdate(UDPServerSocket, address, request, user_id, car_id, booking_id, lat, lng, datetime):
    """A function for storing user activities in the database"""
    booking = Booking.query.filter_by(id=booking_id).first()
    msg = ""
    if(booking):
        if request == "unlock":
            if (not booking.started):
                booking.started = True
                msg = "Your Session has been started. Status Updated."
            else:
                msg = "Car Unlocked."
        elif request == "return":
            if (not booking.finished):
                booking.finished = True
                msg = "Your Session has been finished. Status Updated."
        elif request == "lock":
            msg = "Car Locked."
        else:
            print("Invalid Request")
            return False

        DatabaseUtils().logging(db, user_id, car_id, booking_id, lat, lng, request, datetime)
    else: 
        if request == "unlock":
            msg = "Engineer Unlock"
        elif request == "lock":
            msg = "Engineer Lock"

    msgFromServer = {"status": request, "message": msg}
    sendJson(UDPServerSocket, address, msgFromServer)
    return True

def sendJson(UDPServerSocket, address, msgFromServer):
    """A function for sending json data to Agent pi"""
    data = json.dumps(msgFromServer)
    bytesToSend = data.encode("utf-8")
    # Sending a reply to client
    UDPServerSocket.sendto(bytesToSend, address)
    return True
