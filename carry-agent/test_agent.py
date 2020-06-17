import unittest
from agent import Agent
import socket
import json
import datetime

localIP = "127.0.0.1"
testPort = 20001
bufferSize = 1024

class TestAgent(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """
        Set up function that will be called once before any of the tests start. It will create an agent object,
        change the default port number for socket communication and also set up the test server to communicate 
        with the test agent.
        """
        cls.test_agent = Agent()
        cls.test_agent.socket_utils.setPort(testPort)

        cls.UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        cls.UDPServerSocket.bind((localIP, testPort))

    def test_logged_in_state_upon_startup(self):
        """
        Test that the class variable of test agent is set to false when it is instantialized.
        """
        new_agent = Agent()
        self.assertFalse(new_agent.loggedIn)

    def test_change_agent_port(self):
        """
        Test to make sure that the port that the socket communication will occur on is set properly after being changed.
        """
        self.assertEqual(self.test_agent.socket_utils.PORT, testPort)
        self.assertEqual(self.test_agent.socket_utils.ADDRESS, (localIP, testPort))

    def test_send_and_receive_json_through_socket(self):
        """
        Test that will create an object, send it to the test server as JSON and receive a message back from the
        server as JSON. The sent message and the received message will be verified to ensure that the functions 
        are behaving as intended.
        """
        username = "test-john"
        password = "password"
        car_id = 2
        lat = -145.02
        lng = 33.04

        testJson = {
            "request": "login",
            "username": username,
            "password": password,
            "car_id": car_id,
            "datetime": str(datetime.datetime.now()),
            "lat": lat,
            "lng": lng
        }

        self.test_agent.socket_utils.sendJson(self.UDPServerSocket, testJson)

        bytesAddressPair = self.UDPServerSocket.recvfrom(bufferSize)
        message = bytesAddressPair[0]
        address = bytesAddressPair[1]
        receivedJsonString = message.decode()
        receivedJson = json.loads(receivedJsonString)

        self.assertEqual(receivedJson, testJson)

        msgFromServer = {"test-json": "received",
                         "time-received": str(datetime.datetime.now())}
        data = json.dumps(msgFromServer)
        bytesToSend = data.encode("utf-8")

        self.UDPServerSocket.sendto(bytesToSend, address)

        self.assertEqual(self.test_agent.socket_utils.recvJson(self.UDPServerSocket), msgFromServer)

    def test_encrypt_password(self):
        key = 'mOJGpG5HjCFQV7n0'
        plaintext_pw = "password"

        encrypted_pw = self.test_agent.encrypt(key, plaintext_pw).decode()
        self.assertNotEqual(encrypted_pw, plaintext_pw)

if __name__ == '__main__':
    unittest.main()