from PyQt5 import uic, QtWidgets, QtCore
import sys
import pyqtgraph as pg
import cv2
import time
from imutils import video
import copy

from faceapi.detector import FaceDetector
from faceapi.add_face import AddFaceDialog
from faceapi.recog import FaceRecog


class MainWnd(QtWidgets.QMainWindow):
    def __init__(self, video, face_detector, face_recog):
        super(MainWnd, self).__init__()
        self.video = video
        self.face_detector = face_detector
        self.face_recog = face_recog
        uic.loadUi("./resource/ui/mainwnd.ui", self)
        self.videoWidget = self.findChild(QtWidgets.QWidget, 'video_widget')
        self.graphView = pg.GraphicsView(self.videoWidget)
        img = self.video.read()
        self.setFixedSize(img.shape[1], img.shape[0] + 30)
        self.videoWidget.setFixedSize(img.shape[1], img.shape[0])
        self.graphView.setFixedSize(img.shape[1], img.shape[0])
        self.vis = pg.ImageItem(axisOrder='row-major')
        self.graphView.addItem(self.vis)
        self.lastUpdate = pg.ptime.time()
        self.avgFps = 0.0
        self.scale = 4

        self.enable_recog = False

        self.addFaceBtn = self.findChild(QtWidgets.QPushButton,
                                         'add_face_btn')
        self.addFaceBtn.clicked.connect(self.onAddFaceBtnClicked)
        self.addFaceBtn.setEnabled(False)
        self.enableRecogCk = self.findChild(QtWidgets.QCheckBox,
                                            'enable_recog_checkBox')
        self.enableRecogCk.stateChanged.connect(self.onRecogCkChanged)
        self.detectSpeed = self.findChild(QtWidgets.QLabel, 'detect_label')
        self.recogSpeed = self.findChild(QtWidgets.QLabel, 'recog_label')
        self.FPS = self.findChild(QtWidgets.QLabel, 'fps_label')

    def onRecogCkChanged(self):
        self.enable_recog = self.enableRecogCk.isChecked()

    def addNewFace(self, img, face_name, face_location):
        self.face_recog.add_new_face(img, face_name, face_location)

    def onAddFaceBtnClicked(self):
        afd = AddFaceDialog(self.current_frame,
                            self.current_face_location,
                            self)
        afd.show()

    def run(self):
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(0)

    def update(self):
        img = self.video.read()
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        rgb_frame = cv2.resize(img, (0, 0), fx=1/self.scale, fy=1/self.scale)

        t = time.time()
        face_locations = self.face_detector.run(rgb_frame)
        self.detectSpeed.setText("Detect: {:.2f}".format((time.time()-t)*1000))

        for i in range(len(face_locations)):
            (top, right, bottom, left) = face_locations[i]
            face_locations[i] = (top*self.scale, right*self.scale,
                                 bottom*self.scale, left * self.scale)

        if len(face_locations) == 1 and not self.enable_recog:
            self.current_frame = img.copy()
            self.current_face_location = copy.deepcopy(face_locations[0])
            self.addFaceBtn.setEnabled(True)
        else:
            self.addFaceBtn.setEnabled(False)

        face_names = [""] * len(face_locations)
        if self.enable_recog and len(face_locations) > 0:
            t = time.time()
            face_names = self.face_recog.run(img, face_locations)
            self.recogSpeed.setText("Recog: {:.2f}".format((time.time()-t)*1000))

        frame = img
        # Loop through each face in this frame of video
        for face_location, face_name in zip(face_locations, face_names):
            (top, right, bottom, left) = face_location
            # Draw a box around the face
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

            # Draw a label with a name below the face
            if face_name:
                cv2.rectangle(frame, (right, top - 15),
                              (left, top + 5), (0, 0, 255), cv2.FILLED)
                cv2.putText(frame, face_name, (right, top),
                            cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)

        self.vis.setImage(frame)
        # FPS
        now = pg.ptime.time()
        fps = 1.0 / (now - self.lastUpdate)
        self.lastUpdate = now
        self.avgFps = self.avgFps * 0.8 + fps * 0.2
        self.FPS.setText("FPS: {:.2f}".format(self.avgFps))


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    detector = FaceDetector("./known_face", "dlib", "hog")
    recog = FaceRecog("./known_face")
    video_src = 0
    video = video.VideoStream(video_src)
    window = MainWnd(video, detector, recog)
    window.show()
    video.start()
    window.run()
    app.exec_()
    video.stop()
    window.timer.stop()
