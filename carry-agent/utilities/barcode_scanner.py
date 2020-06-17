# USAGE
# python3 barcode_scanner_console.py

## Acknowledgement
## This code is adapted from:
## https://www.pyimagesearch.com/2018/05/21/an-opencv-barcode-and-qr-code-scanner-with-zbar/
## pip3 install pyzbar

# import the necessary packages
from imutils.video import VideoStream
from pyzbar import pyzbar
import datetime
import imutils
import time
import cv2



class BarcodeScanner:

	def __init__(self):
		self.detectedBarcode = False

	def getEngineer(self, qrString):
		"""
		Extracts the details of the engineer from the QR code string

		Args:
			qrString string: the original string that generated the QR code

		Returns:
			Multiple return values: returns the id, name, email, username and account type
		"""
		engineerDetails = []
		stringArray = qrString.split(", ")

		for x in stringArray:
			detailArray = x.split(": ")
			engineerDetails.append(detailArray[1].strip("\'\")"))

		userId = engineerDetails[0]
		username = engineerDetails[1]
		email = engineerDetails[2]
		firstname = engineerDetails[3]
		lastname = engineerDetails[4]
		auth = engineerDetails[5]

		return userId, username, email, firstname, lastname, auth
		
		
	def scanBarcode(self):
		"""
		Scans QR code using USB camera attached to the raspberry pi

		Returns:
			function: returns the details of the engineer
		"""
		# initialize the video stream and allow the camera sensor to warm up
		print("[INFO] scanning for barcodes...")
		vs = VideoStream(src = 0).start()
		time.sleep(2.0)

		found = set()

		# loop over the frames from the video stream
		while self.detectedBarcode is not True:
			# grab the frame from the threaded video stream and resize it to
			# have a maximum width of 400 pixels
			frame = vs.read()
			frame = imutils.resize(frame, width = 400)

			# find the barcodes in the frame and decode each of the barcodes
			barcodes = pyzbar.decode(frame)

			# loop over the detected barcodes
			for barcode in barcodes:
				# the barcode data is a bytes object so we convert it to a string
				barcodeData = barcode.data.decode("utf-8")
				barcodeType = barcode.type

				# if the barcode text has not been seen before print it and update the set
				if barcodeData not in found:
					# print("[FOUND] Type: {}, Data: {}".format(barcodeType, barcodeData))
					found.add(barcodeData)
					self.detectedBarcode = True
					self.qrCodeString = barcodeData
			
			# wait a little before scanning again
			time.sleep(1)

		# close the output CSV file do a bit of cleanup
		# print("[INFO] cleaning up...")
		vs.stop()
		return self.getEngineer(self.qrCodeString)
		

