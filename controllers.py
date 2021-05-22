from fastapi import FastAPI
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import cognitive_face as CF
from starlette.templating import Jinja2Templates
from starlette.requests import Request
# <snippet_imports>
import asyncio
import io
import glob
import os
import sys
import time
import uuid
import requests
from urllib.parse import urlparse
import pathlib
from io import BytesIO
# To install this module, run:
# python -m pip install Pillow
from PIL import Image, ImageDraw, ImageFont
from azure.cognitiveservices.vision.face import FaceClient
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.face.models import TrainingStatusType, Person
from functions import getAge, getRectangle
# </snippet_imports>
from IPython.display import display_jpeg
import db
from models import User, Photo

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

# new テンプレート関連の設定 (jinja2)
templates = Jinja2Templates(directory="templates")
jinja_env = templates.env  # Jinja2.Environment : filterやglobalの設定用



KEY = '6d4ad97e91f54a02b359b2ef151254c7'
ENDPOINT = 'https://rikuface.cognitiveservices.azure.com/'
#IMAGE_BASE_URL = 'https://csdx.blob.core.windows.net/resources/Face/Images/'
PERSON_GROUP_ID = str(uuid.uuid4())
TARGET_PERSON_GROUP_ID = str(uuid.uuid4())




face_client = FaceClient(ENDPOINT, CognitiveServicesCredentials(KEY))
print('-----------------------------')
print()
print('DETECT FACES')
print()
personAges = []
for I in range(4):
    image_path = pathlib.Path("./static/rikukaroes/cutted_zuck" + str(I) + ".JPG")
    image_name = os.path.basename(image_path)
    image_data = open(image_path, 'rb')
    detected_faces = face_client.face.detect_with_stream(image_data,
                        return_face_landmarks=True,
                        return_face_attributes=['accessories','age','emotion','gender','glasses','hair','makeup','smile'],
                        detection_model='detection_01')

    if not detected_faces:
        raise Exception('No face detected from image {}'.format(image_name))

    print('Detected face ID from', image_name, ':')
    for face in detected_faces: print (face.face_id)
    print()

    first_image_face_ID = detected_faces[0].face_id

    image_data = Image.open(image_path)
    drawing = ImageDraw.Draw(image_data)
    font = ImageFont.truetype('/Library/Fonts/Arial\ Unicode.ttf/Arial', 30)

    for face in detected_faces:
        drawing.rectangle(getRectangle(face), outline='Blue', width = 3)
        drawing.text(getAge(face), "Age:" + str(face.face_attributes.age),align = 'Left',  fill = 'Red', font=font)

    personAges.append(face.face_attributes.age)
    #image_data.show()
    image_data.save(os.path.join('./static/rikuAngles/', "rikuAngle" + str(I) + ".JPG"))

print(personAges)
a = 0
for i in personAges:
    a += i
estimate_age = int(a/len(personAges))


print('Person group:', PERSON_GROUP_ID)
face_client.person_group.create(person_group_id=PERSON_GROUP_ID, name=PERSON_GROUP_ID)

# Define woman friend
riku = face_client.person_group_person.create(PERSON_GROUP_ID, "Riku")
# land = face_client.person_group_person.create(PERSON_GROUP_ID, "Land")

photopath = pathlib.Path("./static/rikuAngles/")
# Find all jpeg images of friends in working directory
riku_images = [file for file in photopath.glob("r*.JPG")]
# land_images = [file for file in pathlib.Path("./rikukaroes/rikuAngles/*.JPG") if file.startswith("l")]


# Add to a riku person
for image in riku_images:
    r = open(image, 'r+b')
    face_client.person_group_person.add_face_from_stream(PERSON_GROUP_ID,riku.person_id, r)
    print(str(image))

# Add to a land person
# for image in land_images:
#     l = open(image, 'r+b')
#     face_client.person_group_person.add_face_from_stream(PERSON_GROUP_ID, land.person_id, l)

print()
print('Training the person group...')
# Train the person group
face_client.person_group.train(PERSON_GROUP_ID)

while (True):
    training_status = face_client.person_group.get_training_status(PERSON_GROUP_ID)
    print("Training status: {}.".format(training_status.status))
    print()
    if (training_status.status is TrainingStatusType.succeeded):
        break
    elif (training_status.status is TrainingStatusType.failed):
        face_client.person_group.delete(person_group_id=PERSON_GROUP_ID)
        sys.exit('Training the person group has failed.')
    time.sleep(5)


test_stream = pathlib.Path("./static/testphotos/")
test_image_array = test_stream.glob("*.jpg")
test_image_array = pathlib.Path("./static/testphotos/旅行.jpg")
test_image_array = pathlib.Path("./static/testphotos/13957286285367.jpg")
print(test_image_array)

test_data = open(test_image_array, 'r+b')

# print('Pausing for 60 seconds to avoid triggering rate limit on free account...')
# time.sleep (60)

# Detect faces
face_ids = []
# We use detection model 3 to get better performance.
faces = face_client.face.detect_with_stream(test_data, detection_model='detection_03')
for face in faces:
    face_ids.append(face.face_id)

confidence = "0"
results = face_client.face.identify(face_ids, PERSON_GROUP_ID)
print('Identifying faces in {}'.format(os.path.basename(image.name)))
if not results:
    print('No person identified in the person group for faces from {}.'.format(os.path.basename(image.name)))
for person in results:
    if len(person.candidates) > 0:
        print('Person for face ID {} is identified in {} with a confidence of {}.'.format(person.face_id, os.path.basename(image.name), person.candidates[0].confidence)) # Get topmost confidence score
        confidence = str(person.candidates[0].confidence)
    else:
        print('No person identified for face ID {} in {}.'.format(person.face_id, os.path.basename(image.name)))



def index(request: Request):
    # ユーザとタスクを取得
    # とりあえず今はadminユーザのみ取得
    user = db.session.query(User).filter(User.username == 'admin').first()
    photos = db.session.query(Photo).all()
    db.session.close()
 
    return templates.TemplateResponse('index.html',
                                      {'request': request,
                                       'user': user,
                                       'photos': photos,
                                       'age':estimate_age})

#img_path = "./static/rikuAngles/rikuAngle0.JPG"
img_paths = ["./static/rikuAngles/rikuAngle{}.JPG".format(str(i)) for i in range(6)]

def rectangles(request: Request):
    return templates.TemplateResponse('rectangles.html',
                                        {'request':request,
                                        'imgs':img_paths,
                                        'confidence':confidence,
                                        })