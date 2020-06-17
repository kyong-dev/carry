#!/usr/bin/env python3
# Documentation: https://docs.python.org/3/library/socket.html

import socket
import json
import sqlite3
import sys
import getpass
import googlemaps
from pi_opencv.facial_recognition import FacialRecognition
from utilities.socket_utils import SocketUtils
from utilities.barcode_scanner import BarcodeScanner
from Crypto.Cipher import XOR
import base64
import requests
from utilities.btle_unlock import BluetoothUnlock
from utilities.btle_delegate import ScanDelegate, ScanDelegateTracking
from bluepy.btle import Scanner

DB_NAME = "agent.db"
AGENT_NUMBER = 1
gmaps = googlemaps.Client(key='AIzaSyA1h5KTHKlyU2WUAO5xONKZZ50zijczn5Y')

# Encryption Key
key = 'mOJGpG5HjCFQV7n0'


class Agent:
    SESSION_BOOKING_ID = None
    SESSION_USER_AUTH = None
    SESSION_USER_ID = None

    def __init__(self):
        """ 
        Init function that will be called when the Agent class is instancialized. This function
        will create FacialRecognition and SocketUtils objects so that their class methods can be used
        by the agent.
        """
        self.socket_utils = SocketUtils()
        self.facial_recognition = FacialRecognition()
        self.loggedIn = False
        self.barcode_scanner = BarcodeScanner()
        jsonobj = self.socket_utils.sendData({"request": "getAllMacAddr"})
        self.saved_devices = []

        for addr in jsonobj['macAddr']:
            #print("Device: " + addr + " found.")
            self.saved_devices.append(addr)

    def loginWithFacialRecognition(self):
        """ 
        This function will be called when the user opts to log in using facial recognition inside of the run function.
        """
        recognisedFace, foundPerson = self.facial_recognition.recognise()
        if recognisedFace:
            getBookingID = self.socket_utils.sendUserID(int(foundPerson), AGENT_NUMBER)
            if getBookingID['booking_id']:
                self.SESSION_BOOKING_ID = getBookingID['booking_id']
                self.SESSION_USER_ID = int(foundPerson)
                self.loggedIn = True
                self.display_login_menu(str(getBookingID['name']))
            else:
                print("This car is not allocated to you. A booking is required.")
                print()

    def loginWithCredentials(self):
        """
        Function that will be called when the user opts to log in using their credentials. The user will be prompted
        to input their username or email address, followed by their password. The input by the user will be sent to
        the master pi which will validate the credentials and check if the account that matches the input has a valid 
        booking. 
        
        If there is a valid booking, then the user will be logged into the system and display_login_menu will 
        be called. 
        If the user inputs invalid credentials, or if the credentials are correct but there is no valid booking, then 
        the appropriate corresponding message will be displayed to the user, and they will be able to try and log in again.
        """
        username = input("Enter username / email address: ")
        password = getpass.getpass("Enter password: ")
        # Encrypt Password
        encryptedPassword = self.encrypt(key, password).decode()
        location = self.getLocation()
        lat = location['location']['lat']
        lng = location['location']['lng'] 
        print()

        successfulLogin = self.socket_utils.sendLoginInput(username, encryptedPassword, AGENT_NUMBER, lat, lng)
        if successfulLogin['login']:
            self.loggedIn = True
            self.SESSION_BOOKING_ID = successfulLogin['booking_id']
            self.SESSION_USER_AUTH = successfulLogin['user_auth']
            self.SESSION_USER_ID = successfulLogin['user_id']
            print(successfulLogin['message'])
            self.display_login_menu(username)
        else:
            print()
            print(successfulLogin['message'])
            print()

    def getLocation(self):
        """
        Function to get the approximate location of the agent pi
        Returns:
            method -- Calls the gmaps api to geolocate the agent pi
        """
        return gmaps.geolocate()

    def display_login_menu(self, user):
        """
        Function that will be called when the user successfully logs in to the agent pi. The user will be presented with 
        5 different options. From this menu, the user can unlock the car, lock the car, register for facial recognition, 
        return the car or log out of the agent pi.
        Arguments:
            user {String} -- The name of the user that is logged into the agent pi
        """
        while self.loggedIn:
            if (self.SESSION_USER_AUTH == 'engineer'):
                print("You have logged in as an engineer.")
                print("1. Unlock Car and access engineer functions")
                print("2. Register bluetooth device for automatic login")
                print("0. Logout")

                text = input("Select an option: ")
                print()
                if text == "1":
                    self.display_engineer_menu()
                elif text == "2" and self.SESSION_USER_AUTH:
                    btle_unlock = BluetoothUnlock(self.saved_devices)
                    if btle_unlock.scanDevices():
                        saved_devices = btle_unlock.getSavedDevices()

                        self.socket_utils.registerMacAddr(self.SESSION_USER_ID, saved_devices[-1])
                        self.display_engineer_menu()
                    else:
                        print("!! - Selected device not found in range - !!")

                    #res = self.socket_utils.registerMacAddr(self.SESSION_USER_ID, macAddr)
                    #print(res['message'])
                    print()
                elif text == "0":
                    self.loggedIn = False
                    break

            else:
                print("Welcome " + user) 
                print("1. Unlock Car")
                print("2. Lock Car")
                if (self.SESSION_USER_AUTH == 'engineer'):
                    print("3. Register Mac Address")
                else:
                    print("3. Register for facial recognition")
                if (self.SESSION_BOOKING_ID != None):
                    print("4. Return Car")
                print("0. Logout")
                print()

                text = input("Select an option: ")
                print()

                location = self.getLocation()
                lat = location['location']['lat']
                lng = location['location']['lng'] 

                if text == "1":
                    res = self.socket_utils.sendRequest('unlock', AGENT_NUMBER, self.SESSION_USER_ID, self.SESSION_BOOKING_ID, lat, lng)
                    print(res['message'])
                    print()
                elif text == "2":
                    res = self.socket_utils.sendRequest('lock', AGENT_NUMBER, self.SESSION_USER_ID, self.SESSION_BOOKING_ID, lat, lng)
                    print(res['message'])
                    print()
                elif text == "3" and self.SESSION_USER_AUTH == None:
                    self.facial_recognition.capture(user, self.SESSION_USER_ID)
                    self.facial_recognition.encode()
                elif text == "4" and self.SESSION_BOOKING_ID != None:
                    res = self.socket_utils.sendRequest('return', AGENT_NUMBER, self.SESSION_USER_ID, self.SESSION_BOOKING_ID, lat, lng)
                    self.SESSION_USER_ID = None
                    self.SESSION_BOOKING_ID = None
                    print(res['message'])
                    print()
                    self.loggedIn = False
                elif text == "0":
                    self.loggedIn = False
                    break

    def encrypt(self, key, plaintext):
        """
        Encrypts the password that the user inputs
        Arguments:
            key {String} -- Key that will be used to encrypt the plaintext
            plaintext {String} -- The input of the user that will be encrypted
        Returns:
            String -- The encrypted password
        """
        cipher = XOR.new(key)
        return base64.b64encode(cipher.encrypt(plaintext))

    def display_engineer_menu(self):
        print("The car has been unlocked. ")
        print("Please scan QR code to continue")
        print("1. Scan QR Code")
        print("0. Logout")
        print()

        text = input("Select an option: ")
        
        if text == "1":
            userId, username, email, firstname, lastname, auth = self.barcode_scanner.scanBarcode()
            # userId, username, email, firstname, lastname, auth = "1","2","3","4","5", "6"
            print()
            print("Welcome " + firstname)
            print("Here are your details: ")
            print("Id: " + userId)
            print("Email: " + email)
            print("First Name: " + firstname)
            print("Last Name: " + lastname)
            print("Account Type: " + auth)
            print()

            print("Would you like to update the report status?")
            print()
            secondText = input("Select an option (Y/N): ")
            if secondText.lower() == "y":
                inputJson = {
                    "request": "report",
                    "car_id" : AGENT_NUMBER,
                    "user_id": userId
                }
                res = self.socket_utils.sendData(inputJson)
                print()
                print("The car report status of this car has been updated.")
                print()
            elif secondText.lower() == "n":
                print()
                print("Logging out now.")
                self.loggedIn = False
                print()
        elif text == "0":
            self.loggedIn = False
            return

        print()

    def run(self):
        """
        This function will present the first menu that the user will be able to see. When this function is run the 
        user will be able to log into the agent pi either by inputting their credentials or by using facial recognition.
        In order to log in using facial recognition, the user needs to log in with their credentials first and then
        registering for facial recognition once logged into the system.
        """
        while(not self.loggedIn):
            btle_unlock = BluetoothUnlock(self.saved_devices)
            scanTracker = Scanner().withDelegate(ScanDelegateTracking())
            if btle_unlock.trackSaved(scanTracker):
                print("Engineer mac address detected. Automatically logged in.")
                self.display_engineer_menu()

            print("1. Login using user credentials")
            print("2. Login using facial recognition")
            print("0. Quit")

            print()

            text = input("Select an option: ")
            print()

            if text == "1":
                # Master pi
                self.loginWithCredentials()
            elif text == "2":
                try:
                    self.loginWithFacialRecognition()
                except FileNotFoundError:
                    print("No such file or directory: encodings.pickle")
                    print("Not enough data for facial recognition. Please login using your credentials first")
                    print()
                    continue
            elif text == "3":
                self.display_engineer_menu()

            elif(text == "0"):
                print("Goodbye.")
                print()
                break