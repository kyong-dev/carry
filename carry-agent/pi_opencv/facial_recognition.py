# import the necessary packages
import cv2
import os
import argparse
from imutils import paths
import face_recognition
import pickle
from imutils.video import VideoStream
import imutils
import time

class FacialRecognition:

    def __init__(self):
        self.foundPerson = False
        self.detectedPerson = ""

    def capture(self, name, user_id):
        """
        # USAGE
        # With default parameter of user/id
        #       python3 01_capture.py -n default_user
        # OR specifying the dataset and user/id
        #       python3 02_capture.py -i dataset -n default_user

        ## Acknowledgement
        ## This code is adapted from:
        ## https://www.hackster.io/mjrobot/real-time-face-recognition-an-end-to-end-project-a1082
        """
        # construct the argument parser and parse the arguments
        # ap = argparse.ArgumentParser()
        # ap.add_argument("-n", "--name", required = True,
        #     help="The name/id of this person you are recording")
        # ap.add_argument("-i", "--dataset", default = "dataset",
        #     help="path to input directory of faces + images")
        # args = vars(ap.parse_args())

        # use name as folder name
        # name = args["name"]
        name = name
        folder = "pi_opencv/dataset/{}".format(user_id)

        # Create a new folder for the new name
        if not os.path.exists(folder):
            os.makedirs(folder)

        # Start the camera
        cam = cv2.VideoCapture(0)
        # Set video width
        cam.set(3, 640)
        # Set video height
        cam.set(4, 480)
        # Get the pre-built classifier that had been trained on 3 million faces
        face_detector = cv2.CascadeClassifier("pi_opencv/haarcascade_frontalface_default.xml")

        img_counter = 0
        while img_counter <= 10:
            key = input("Press q to quit or ENTER to continue: ")
            if key == "q":
                break
            
            ret, frame = cam.read()
            if not ret:
                break
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_detector.detectMultiScale(gray, 1.3, 5)

            if(len(faces) == 0):
                print("No face detected, please try again")
                continue
            
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                img_name = "{}/{:04}.jpg".format(folder, img_counter)
                cv2.imwrite(img_name, frame[y : y + h, x : x + w])
                print("{} written!".format(img_name))
                img_counter += 1

        cam.release()
    
    def encode(self):
        """
        # USAGE
        # With default parameters
        #         python3 02_encode.py
        # OR specifying the dataset, encodings and detection method
        #         python3 02_encode.py -i dataset -e encodings.pickle -d hog

        ## Acknowledgement
        ## This code is adapted from:
        ## https://www.pyimagesearch.com/2018/06/18/face-recognition-with-opencv-python-and-deep-learning/
        """

        # construct the argument parser and parse the arguments
        ap = argparse.ArgumentParser()
        ap.add_argument("-i", "--dataset", default = "pi_opencv/dataset",
            help="path to input directory of faces + images")
        ap.add_argument("-e", "--encodings", default = "pi_opencv/encodings.pickle",
            help="path to serialized db of facial encodings")
        ap.add_argument("-d", "--detection-method", type = str, default = "hog",
            help="face detection model to use: either `hog` or `cnn`")
        args = vars(ap.parse_args())

        # grab the paths to the input images in our dataset
        print("[INFO] quantifying faces...")
        imagePaths = list(paths.list_images(args["dataset"]))
        print(imagePaths)

        # initialize the list of known encodings and known names
        knownEncodings = []
        knownNames = []

        # loop over the image paths
        for (i, imagePath) in enumerate(imagePaths):
            # extract the person name from the image path
            print("[INFO] processing image {}/{}".format(i + 1, len(imagePaths)))
            name = imagePath.split(os.path.sep)[-2]

            # load the input image and convert it from RGB (OpenCV ordering)
            # to dlib ordering (RGB)
            image = cv2.imread(imagePath)
            rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            # detect the (x, y)-coordinates of the bounding boxes
            # corresponding to each face in the input image
            boxes = face_recognition.face_locations(rgb, model = args["detection_method"])

            # compute the facial embedding for the face
            encodings = face_recognition.face_encodings(rgb, boxes)
            
            # loop over the encodings
            for encoding in encodings:
                # add each encoding + name to our set of known names and encodings
                knownEncodings.append(encoding)
                knownNames.append(name)

        # dump the facial encodings + names to disk
        print("[INFO] serializing encodings...")
        data = { "encodings": knownEncodings, "names": knownNames }

        with open(args["encodings"], "wb") as f:
            f.write(pickle.dumps(data))

    def recognise(self):
        """
        # USAGE
        # With default parameters
        #     python3 03_recognise.py
        # OR specifying the encodings, screen resolution
        #     python3 03_recognise.py -e encodings.pickle -r 240

        ## Acknowledgement
        ## This code is adapted from:
        ## https://www.pyimagesearch.com/2018/06/18/face-recognition-with-opencv-python-and-deep-learning/
        """

        # construct the argument parser and parse the arguments
        ap = argparse.ArgumentParser()
        ap.add_argument("-e", "--encodings", default="pi_opencv/encodings.pickle",
        help="path to serialized db of facial encodings")
        ap.add_argument("-r", "--resolution", type=int, default=240,
            help="Resolution of the video feed")
        ap.add_argument("-d", "--detection-method", type=str, default="hog",
            help="face detection model to use: either `hog` or `cnn`")
        args = vars(ap.parse_args())

        # load the known faces and embeddings
        print("[INFO] loading encodings...")
        data = pickle.loads(open(args["encodings"], "rb").read())

        # initialize the video stream and then allow the camera sensor to warm up
        print("[INFO] starting video stream...")
        vs = VideoStream(src = 0).start()
        time.sleep(2.0)

        # loop over frames from the video file stream
        while True:
            # grab the frame from the threaded video stream
            frame = vs.read()
            
            # convert the input frame from BGR to RGB then resize it to have
            # a width of 750px (to speedup processing)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            rgb = imutils.resize(frame, width = args["resolution"])

            # detect the (x, y)-coordinates of the bounding boxes
            # corresponding to each face in the input frame, then compute
            # the facial embeddings for each face
            boxes = face_recognition.face_locations(rgb, model = args["detection_method"])
            encodings = face_recognition.face_encodings(rgb, boxes)
            names = []

            # loop over the facial embeddings
            for encoding in encodings:
                # attempt to match each face in the input image to our known
                # encodings
                matches = face_recognition.compare_faces(data["encodings"], encoding)
                name = "Unknown"

                # check to see if we have found a match
                if True in matches:
                    self.foundPerson = True
                    # find the indexes of all matched faces then initialize a
                    # dictionary to count the total number of times each face
                    # was matched
                    matchedIdxs = [i for (i, b) in enumerate(matches) if b]
                    counts = {}

                    # loop over the matched indexes and maintain a count for
                    # each recognized face face
                    for i in matchedIdxs:
                        name = data["names"][i]
                        counts[name] = counts.get(name, 0) + 1

                    # determine the recognized face with the largest number
                    # of votes (note: in the event of an unlikely tie Python
                    # will select first entry in the dictionary)
                    name = max(counts, key = counts.get)

                # update the list of names
                names.append(name)

        # loop over the recognized faces
            for name in names:
                # print to console, identified person
                print("Person found: {}".format(name))
                self.detectedPerson = format(name)
                # Set a flag to sleep the cam for fixed time
                # time.sleep(3.0)
            vs.stop()
            if self.foundPerson:
                return self.foundPerson, self.detectedPerson
            else:
                return None
        # do a bit of cleanup
        vs.stop()
