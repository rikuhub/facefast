from . import face_recognition
import cv2


class FaceDetector():
    def __init__(self,
                 known_face_dir=None,
                 method="dlib",
                 dlib_method="hog",
                 tol=0.8, scale=2):
        self.known_face_dir = known_face_dir
        self.dlib_method = dlib_method
        self.tol = 0.8
        self.scale = 2
        if method == "dlib":
            self.real_run = self.run_dlib
        else:
            self.real_run = self.run_retina
            import sys
            sys.path.append("../3rdparty/")
            sys.path.append("../3rdparty/retinaface/")
            from retinaface.infer import RetinaFaceDetector
            import torch
            device = "cuda:0" if torch.cuda.is_available() else "cpu"
            state_dict = "../3rdparty/retinaface/checkpoints/final_retinalface.pth"
            self.detector = RetinaFaceDetector(device=device, state_dict=state_dict)

    def run(self, rgb_frame):
        scale_rgb_frame = cv2.resize(rgb_frame, (0, 0),
                                     fx=1/self.scale, fy=1/self.scale)
        face_locations = self.real_run(scale_rgb_frame)
        for i in range(len(face_locations)):
            (top, right, bottom, left) = face_locations[i]
            face_locations[i] = (top*self.scale, right*self.scale,
                                 bottom*self.scale, left * self.scale)
        return face_locations

    def run_dlib(self, rgb_frame):
        return face_recognition.face_locations(rgb_frame, 1, self.dlib_method)

    def run_retina(self, rgb_frame):
        bboxs = self.detector.run(rgb_frame)
        rcs = []
        for box in bboxs:
            x = int(box[0])
            y = int(box[1])
            w = int(box[2]) - int(box[0])
            h = int(box[3]) - int(box[1])
            conf = box[4]
            if conf > self.tol and x >= 0 and y >= 0:
                rcs.append([y, x, y+h, x+w])
        return rcs
