# facefast
faceAPIとfastAPIのコラボレーション企画（予定）💦

##前提##
1. cascade_pathを通すこと
  これがないと顔をくり抜いてくれまてん😅

ちょっとメモっとく
旧 main.py

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import cognitive_face as CF
import cv2
import matplotlib.pyplot as plt

app = FastAPI()


KEY = '7e88a2ccefdf4c41be4a8c2bac9d67cd'
BASE_URL = 'https://japaneast.api.cognitive.microsoft.com/face/v1.0'

CF.Key.set(KEY)
CF.BaseUrl.set(BASE_URL)

# imgurl = "https://res.cloudinary.com/hr5vydnrm/image/upload/v1616602255/vxbiyx9lz8nr1enqorps.jpg"
# faces = CF.face.detect(imgurl, attributes='emotion')

# print(faces)

cap = cv2.VideoCapture(0)
cascade_path = "../../opencv/data/haarcascades/haarcascade_frontalface_alt.xml"


@app.get("/", response_class=HTMLResponse)
def read_root():
    show = ""
    while True:
        ret, im = cap.read()

        # ここからのコードを変えながら、微調整するとオリジナルになると思います。
        cascade = cv2.CascadeClassifier(cascade_path)
        img_gray = cv2.cvtColor(im, cv2.COLOR_RGB2GRAY)
        faces = cascade.detectMultiScale(
            img_gray, scaleFactor=1.1, minNeighbors=1, minSize=(80, 80))  # minNeighborsは人数
        print(faces)

        if len(faces) > 0:
            for (x, y, w, h) in faces:
                cv2.rectangle(im, (x, y), (x+w, y+h), (255, 0, 0), 2)

        img = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)

        show = plt.imshow(img)

        blur = cv2.GaussianBlur(im, (0, 0), 1)
        cv2.imshow('camera capture', blur)
        key = cv2.waitKey(10)
        # カメラはESCキーで終了できるように。
        if key == 27:
            break
    
    html = """
    <html>
    <body>
    <h1>uvicorn main:app --reload</h1>
    </body>
    </html>
    """
# 一旦画像削除の命令
    cap.release()
# カメラが立ち上がっているので、全てのウィンドウを閉じる
    cv2.destroyAllWindows()
    return show
