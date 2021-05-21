from fastapi import FastAPI
from fastapi.responses import HTMLResponse
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
import db
from models import User, Photo

app = FastAPI()

# new テンプレート関連の設定 (jinja2)
templates = Jinja2Templates(directory="templates")
jinja_env = templates.env  # Jinja2.Environment : filterやglobalの設定用



KEY = '6d4ad97e91f54a02b359b2ef151254c7'
ENDPOINT = 'https://rikuface.cognitiveservices.azure.com/'


#IMAGE_BASE_URL = 'https://csdx.blob.core.windows.net/resources/Face/Images/'
PERSON_GROUP_ID = str(uuid.uuid4()) # assign a random ID (or name it anything)
TARGET_PERSON_GROUP_ID = str(uuid.uuid4()) # assign a random ID (or name it anything)
face_client = FaceClient(ENDPOINT, CognitiveServicesCredentials(KEY))
print('-----------------------------')
print()
print('DETECT FACES')
print()
personAges = []
photodatas = []
for I in range(4):
    image_path = pathlib.Path("./rikukaroes/cutted_zuck" + str(I) + ".JPG")
    image_name = os.path.basename(image_path)
    image_data = open(image_path, 'rb')
    detected_faces = face_client.face.detect_with_stream(image_data,
                        return_face_landmarks=True,
                        return_face_attributes=['accessories','age','emotion','gender','glasses','hair','makeup','smile'],
                        detection_model='detection_01')

    if not detected_faces:
        raise Exception('No face detected from image {}'.format(mage_name))

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
    photodatas.append(image_data)
    image_data.save(os.path.join('./rikuAngles/', "rikuAngle" + str(I) + ".JPG"))

print(personAges)
a = 0
for i in personAges:
    a += i
estimate_age = a/len(personAges)

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
# def index(request: Request):
#     return templates.TemplateResponse('index.html', {'request': request, 'age':estimate_age, "photos":photodatas})

