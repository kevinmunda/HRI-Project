import cv2
import os
import numpy as np
import face_recognition
import glob
from cv2 import *
from global_ import flagDict

IMAGES_PATH = './Tablet/static/Photos'
MAX_DISTANCE = 0.5  # increase to make recognition less strict, decrease to make more strict


# VARIOUS
def resetFlags(flagDict):
    for key in flagDict.keys():
        if key == 'name' or key == 'surname':
            continue
        else:
            flagDict[key] = False
    flagDict['interactionFlag'] = True


def readDatabase():
    database = {}
    with open("database.txt", "r") as f:
        lines = f.readlines()
    for line in lines:
        line = line.strip("\n")
        data = line.split("#")
        key = data[0]+data[1]
        database[key] = {
            "name": data[0],
            "surname": data[1],
            "photoPath": data[2],
            "lastOrder": data[3]
        }
    return database


def searchOrder(database, key):
    lastOrder = database[key]['lastOrder']
    return lastOrder


def readMenu():
    menu = []
    with open('menu.txt', 'r') as f:
        lines = f.readlines()
    for line in lines:
        line = line.strip("\n")
        menu.append(line)
    return menu


# FACE REGISTRATION
def streamVideo():
    camera = VideoCapture(0)
    while True:
        # Capture frame-by-frame
        ret, frame = camera.read()
        if not ret:
            break
        else:
            ret, buffer = imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

            if flagDict['photoTakenFlag']:
                flagDict['photoTakenFlag'] = False
                img_name = 'Tablet/static/current_photo.jpg'
                if os.path.exists(img_name):
                    os.remove(img_name)
                imwrite(img_name, frame)
    camera.release()
    destroyAllWindows()


def insertUser(flagDict):
    # Add user data to the database
    old_path = "Tablet/static/current_photo.jpg"
    new_path = "Tablet/static/Photos/" + flagDict['name'] + '-' + flagDict['surname'] + ".jpg"
    # Delete old photo if already exists
    if os.path.exists(new_path):
        os.remove(new_path)
    # Move the photo to the specific folder
    os.rename(old_path, new_path)
    # Remove the current photo if exists
    if os.path.exists(old_path):
        os.remove(old_path)

    user_data = flagDict['name'] + "#" + flagDict['surname'] + "#" + new_path + "#" + "None"
    with open("database.txt", "r") as f:
        lines = f.readlines()
    # Remove existent data if the user registers himself again
    with open("database.txt", "w") as f:
        for line in lines:
            line = line.strip("\n")
            data = line.split('#')
            if data[0] != flagDict['name'] and data[1] != flagDict['surname']:
                f.write(line + "\n")

    f = open("database.txt", "a")
    f.write(user_data + "\n")
    f.close()


# FACE RECOGNITION
def get_face_embeddings_from_image(image, convert_to_rgb=False):
    """
    Take a raw image and run both the face detection and face embedding model on it
    """
    # Convert from BGR to RGB if needed:
    if convert_to_rgb:
        image = image[:, :, ::-1]
    # Run face detection model to find face locations
    face_locations = face_recognition.face_locations(image)
    # Run the embedding model to get face embeddings for the supplied locations
    face_encodings = face_recognition.face_encodings(image, face_locations)

    return face_locations, face_encodings


def setup_database():
    """
    Load reference images and create a database of their face encodings
    """
    imgDatabase = {}
    for filename in glob.glob(os.path.join(IMAGES_PATH, '*.jpg')):
        # Load image
        image_rgb = face_recognition.load_image_file(filename)
        # Use the name in the filename as the identity key
        identity = os.path.splitext(os.path.basename(filename))[0]
        # Get face encoding and link it to the identity
        locations, encodings = get_face_embeddings_from_image(image_rgb)
        imgDatabase[identity] = encodings[0]

    return imgDatabase


def paint_detected_face_on_image(faces, identity, frame):
    """
    Paint a rectangle around the face and write the name
    """
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.rectangle(frame, (x, y + h), (x + w + 10, y + h + 35), (0, 128, 0), cv2.FILLED)
        cv2.putText(frame, identity, (x, y + h + 35), cv2.FONT_HERSHEY_DUPLEX, 1.0, (255, 255, 255), 2)


def streamVideoRec():
    camera = VideoCapture(0)

    cascPath = "./haarcascade_frontalface_default.xml"
    faceCascade = CascadeClassifier(cascPath)

    # Create database of known images
    imgDatabase = setup_database()

    # Face recognition library uses keys and values of the database separately
    known_face_encodings = list(imgDatabase.values())
    known_face_names = list(imgDatabase.keys())

    while camera.isOpened():
        # Grab a single frame of video
        ret, frame = camera.read()
        gray = cvtColor(frame, COLOR_BGR2GRAY)
        if not ret:
            break

        if not flagDict['faceMatchedFlag']:
            identity = "No-Match"
            # Run detection and embedding models
            face_locations, face_encodings = get_face_embeddings_from_image(frame, convert_to_rgb=True)
            # Loop through each face in this frame and see if there's a match
            for location, face_encoding in zip(face_locations, face_encodings):
                # Get distances from this encoding to those of all reference images
                distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                # Select the closest match (smallest distance) if it's below the threshold value
                if any(np.array(distances <= MAX_DISTANCE)):
                    best_match_idx = np.argmin(distances)
                    identity = known_face_names[best_match_idx]
                    user_data = identity.split('-')
                    flagDict['name'] = user_data[0]
                    flagDict['surname'] = user_data[1]
                    flagDict['faceMatchedFlag'] = True
                else:
                    identity = "No-Match"

        faces = faceCascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30),
            flags=cv2.CASCADE_SCALE_IMAGE
        )

        # Show recognition info on the image
        paint_detected_face_on_image(faces, identity, frame)
        # Show image
        ret, buffer = imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    camera.release()
    destroyAllWindows()


# ORDER
def updateDatabase(name, surname, lastOrder):
    with open('database.txt', 'r') as f:
        lines = f.readlines()
    with open('database.txt', 'w') as f:
        for line in lines:
            line = line.strip("\n")
            data = line.split("#")
            if (data[0] != name and data[1] != surname)\
                    or (data[0] != name and data[1] == surname):
                f.write(line + "\n")
            else:
                tmp_name = data[0]
                tmp_surname = data[1]
                tmp_path = data[2]
                user_data = tmp_name + "#" + tmp_surname + "#" + tmp_path + "#" + lastOrder
                f.write(user_data + "\n")
