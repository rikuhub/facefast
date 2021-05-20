from PyQt5 import uic, QtWidgets, QtGui
import sys
import cv2
import numpy as np
import copy


class AddFaceDialog(QtWidgets.QDialog):
    def __init__(self, cvImg, face_location, parent=None):
        super(AddFaceDialog, self).__init__(parent)
        uic.loadUi("./resource/ui/add_face.ui", self)
        self.cvImg = np.copy(cvImg)
        self.image = self.findChild(QtWidgets.QLabel, "image_label")
        cvImgFace = np.copy(self.cvImg)
        self.face_location = copy.deepcopy(face_location)
        (top, right, bottom, left) = self.face_location
        # Draw a box around the face
        cv2.rectangle(cvImgFace,
                      (left, top), (right, bottom), (0, 0, 255), 1)

        height, width, channel = cvImg.shape
        bytesPerLine = 3 * width
        qImg = QtGui.QImage(cvImgFace.data, width, height,
                            bytesPerLine, QtGui.QImage.Format_RGB888)
        self.image.setPixmap(QtGui.QPixmap(qImg))
        self.addFaceBtn = self.findChild(QtWidgets.QPushButton,
                                         'add_face_btn')
        self.faceNameLe = self.findChild(QtWidgets.QLineEdit,
                                         'face_name_lineEdit')
        self.addFaceBtn.clicked.connect(self.onAddFaceBtnClicked)
        self.addFaceBtn.setEnabled(False)
        self.faceNameLe.textChanged.connect(self.onfaceNameLeChanged)

    def onfaceNameLeChanged(self):
        self.addFaceBtn.setEnabled(not (not self.faceNameLe.text()))

    def onAddFaceBtnClicked(self):
        if self.parent():
            self.parent().addNewFace(self.cvImg, self.faceNameLe.text(),
                                     self.face_location)
        self.close()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    img = cv2.imread("obama.jpg")
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    addFaceDiglog = AddFaceDialog(img, (10, 30, 50, 90))
    addFaceDiglog.show()
    app.exec_()
