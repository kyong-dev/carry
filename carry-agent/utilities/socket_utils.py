#!/usr/bin/env python3
# Documentation: https://docs.python.org/3/library/struct.html
import socket
import json
import struct
import datetime
import select

HOST = '127.0.0.1'
bufferSize = 1024

class SocketUtils:
    """
    Class contains the methods used to send and receive data through sockets to communicate with MP.
    """
    def __init__(self):
        """
        Init function that is called when the SocketUtils class is instantialized.
        This function will set the class variables PORT and ADDRESS which will be used 
        to communicate with the master pi via sockets.
        """
        self.PORT = 5001
        self.ADDRESS = (HOST, self.PORT)

    def setPort(self, new_port):
        """
        This function will change the port number and subsequently, the address that will
        be used in the socket connection.

        Arguments:
            new_port {integer} -- The new port number that the socket connection should be made on.
        """
        self.PORT = new_port
        self.ADDRESS = (HOST, self.PORT)

    def sendJson(self, socket, object):
        """
        Function that will be used to send an object as JSON to the socket that is passed into the 
        function as the second parameter.

        Arguments:
            socket {socket} -- The socket endpoint that the object will be sent to
            object {[type]} -- The object to be sent through
        """
        jsonString = json.dumps(object)
        data = jsonString.encode("utf-8")
        socket.sendto(data, self.ADDRESS)

    def recvFile(self, socket):
        """
        This function will be used to receive a file sent back from the server

        Arguments:
            socket {socket} -- The socket endpoint that the data will be received from

        Returns:
            File -- The file sent back from the server
        """
        data, address = socket.recvfrom(bufferSize)
        return data

    def recvJson(self, socket):
        """
        This function will be used to receive a message sent back from the server
        as a JSON object

        Arguments:
            socket {socket} -- The socket endpoint that the server sends the message from

        Returns:
           Dictionary -- JSON object loaded as a python dictionary or list after JSON object is deserialized.
        """
        msgFromServer = socket.recvfrom(bufferSize)
        msg = msgFromServer[0].decode()
        receivedJson = json.loads(msg)
        return receivedJson

    def sendData(self, inputJson):
        """
        This function is used to send data to the server and it will also receive the response back from the
        server as well. This function will call the functions sendJson and recvJson to send and receive data.

        Arguments:
            inputJson {Dictionary} -- The data that will be sent to the server

        Returns:
            [Dictionary] -- The message received from the server as a JSON object
        """
        jsonString = json.dumps(inputJson)
        data = jsonString.encode("utf-8")
        jsonLength = struct.pack("!i", len(data))

        UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.sendJson(UDPClientSocket, inputJson)

        while(True):
            receivedJsonObject = self.recvJson(UDPClientSocket)
            return receivedJsonObject

    def getFile(self, inputJson):
        """
        

        Arguments:
            inputJson {[type]} -- [description]

        Returns:
            [type] -- [description]
        """
        jsonString = json.dumps(inputJson)
        data = jsonString.encode("utf-8")
        jsonLength = struct.pack("!i", len(data))

        UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.sendJson(UDPClientSocket, inputJson)
        timeout = 3
        while(True):
            receivedFileObject = self.recvFile(UDPClientSocket)
            file_name = "pi_opencv/encodings.pickle"
            f = open(file_name, 'wb')
            while True:
                ready = select.select([UDPClientSocket], [], [], timeout)
                if ready[0]:
                    data, addr = UDPClientSocket.recvfrom(1024)
                    f.write(data)
                else:
                    print("Received")
                    f.close()
                    break
            return data

    def sendLoginInput(self, username, password, car_id, lat, lng):
        """
        This function is called when the user opts to log in using their credentials. 
        It will create a python dictionary and send the data that is passed in as 
        arguments to the function sendData

        Arguments:
            username {String} -- The username that the user inputs when logging in
            password {String} -- The password that the user inputs when logging in
            car_id {int} -- The id of the car that the agent pi is modelling
            lat {float} -- The approximate latitude of the agent pi
            lng {float} -- The approximate longitude of the agent pi

        Returns:
            Dictionary -- The message that the server sends back after after receiving the message from this function.
        """
        inputJson = {
            "request": "login",
            "username": username,
            "password": password,
            "car_id": car_id,
            "datetime": str(datetime.datetime.now()),
            "lat": lat,
            "lng": lng,
        }
        return self.sendData(inputJson)

    def sendRequest(self, status, car_id, user_id, booking_id, lat, lng):
        """
        Function that is used to send a request to the server. This function will be used to
        unlock the car, lock the car or returning the car at the end of the booking.

        Arguments:
            status {String} -- Used to indicate the type of request to the server. Status will be 
                either "lock", "unlock" or "return"
            car_id {integer} -- The id of the car that the agent pi is modelling
            user_id {integer} -- The id of the user that is logged into the agent pi
            booking_id {integer} -- The id of the booking associated with this car and this user
            lat {float} -- Approximate latitude of the agent pi
            lng {float} -- Approximate longitude of the agent pi

        Returns:
            Dictionary -- The message that the server sends back after receiving message from this function.
        """
        inputJson = {
            "request": status,
            "car_id": car_id,
            "user_id": user_id,
            "booking_id": booking_id,
            "datetime": str(datetime.datetime.now()),
            "lat": lat,
            "lng": lng,
        }
        return self.sendData(inputJson)

    def sendUserID(self, user_id, car_id):
        """
        Sends the id of the user logged into the agent pi and the id of the car that the agent is modelling.

        Arguments:
            user_id {integer} -- The id of the user that is logged into the agent pi
            car_id {integer} -- The id of the car that the agent is modelling

        Returns:
            Dictionary -- The message that the server sends back after receiving message from this function.
        """
        inputJson= {
            "request": "booking_id",
            "user_id": user_id,
            "car_id": car_id
        }
        return self.sendData(inputJson)

    def sendAgentNumber(self, agentNumber):
        """
        Sends the car id that the agent is modelling to the server

        Arguments:
            agentNumber {integer} -- Id of the car the agent is modelling

        Returns:
            file -- The file send from the server after receiving message from this function
        """
        inputJson = {
            "request": "opencv",
            "car_id": agentNumber,
            "datetime": str(datetime.datetime.now()),
        }
        return self.getFile(inputJson)

    def registerMacAddr(self, user_id, macAddr):
        """
        Sends the id of the engineer logged into the agent pi and the mac address that the engineer wants to register.

        Arguments:
            user_id {integer} -- The id of the engineer that is logged into the agent pi
            macAddr {string} -- The mac address of the engineer's phone

        Returns:
            Dictionary -- The message that the server sends back after receiving message from this function.
        """
        inputJson= {
            "request": "registerMacAddr",
            "user_id": user_id,
            "macAddr": macAddr
        }
        return self.sendData(inputJson)
