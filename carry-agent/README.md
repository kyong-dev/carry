# Agent

## How to install

- Opencv must be installed before running the program.

#### Clone the project
```
$ git clone https://github.com/s3634359/carry-agent
$ cd carshare-agentpi
```

#### Virtualevn
```
$ source venv/bin/activate
```

#### Install packages in requirements.txt
```
$ pip3 install -r requirements
```

#### Run
```
$ python3 main.py
```

### Sphinx
```
$ python3 sphinx.py
```

#### Make html
```
$ cd docs
$ make clean
$ sphinx-apidoc -o source ..
$ make html
```

#### Open the html in browser
```
$ cd docs
$ firefox build/html/index.html &
```

#### Create a pdf file
```
$ cd docs
$ sphinx-build -b rinoh source _build/rinoh
```

### Unittest
Test
```
$ python3 -m unittest test_agent.py
```


# OpenCV
To use opencv for facial recognition the following steps need to occur:

1. Install opencv as directed in installation.txt
[installation.txt](https://github.com/s3634359/carry-agent/tree/master/pi_opencv/installation.txt)

2. After successfully installing opencv and the extra python packages that are mentioned:
    Connect a USB Camera to the raspberry pi and run the first file to capture images to be used
    - facial_recognition.capture(name, user_id)

3. The encode.py file will not run properly unless you update the paths to the facial recognition models
    a. Open /home/pi/.local/lib/python3.7/site-packages/face_recognition/api.py

    b. Comment the following lines out:
        
        1. pose_predictor_68_point = dlib.shape_predictor(predictor_68_point_model)
        
        2. pose_predictor_5_point = dlib.shape_predictor(predictor_5_point_model)
        
        3. face_encoder = dlib.face_recognition_model_v1(face_recognition_model)

    c. Replace these lines with the following lines respectively:

        1. pose_predictor_68_point = dlib.shape_predictor("pi_opencv/facial_recognition_models/shape_predictor_68_face_landmarks.dat")
    
        2. pose_predictor_5_point = dlib.shape_predictor("pi_opencv/facial_recognition_models/shape_predictor_5_face_landmarks.dat")
    
        3. face_encoder = dlib.face_recognition_model_v1("pi_opencv/facial_recognition_models/dlib_face_recognition_resnet_model_v1.dat")

The file paths for the facial recognition models are respective to the python file you are running (agent.py in this case )

4. After completing the steps above, provided that you have enough images in your dataset, you can use encode to
encode the images and generate the corresponding encodings.pickle
    - facial_recognition.encode()

5. After successfully encoding the images, you can run recognise.py to recognise a user with the USB camera.
    - facial_recognition.recognise()

sudo apt-get install wireless-tools