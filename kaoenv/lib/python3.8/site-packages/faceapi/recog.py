from . import face_recognition as faceapi
import numpy as np
import os
import cv2
import hashlib
import glob


def save_new_face(known_face_dir, face_name, face_location, img):
    img_dir = os.path.join(known_face_dir, face_name)
    if not os.path.exists(img_dir):
        os.mkdir(img_dir)
    print(face_location)
    top, right, bottom, left = face_location
    if right < left:
        left, right = right, left
    print(img.shape)
    print(bottom-top, right-left)
    clip_img = img[top:bottom, left:right].copy()
    img_name = os.path.join(img_dir,
                            hashlib.md5(clip_img).hexdigest() + ".jpg")
    print("add new face with {} {}".format(clip_img.shape, img_name))

    if not os.path.exists(img_name):
        path = str(img_dir) + "/*.jpg"
        list_of_files = glob.glob(path)
        if len(list_of_files) > 5:
            # remove youngest file
            youngest_file = min(list_of_files, key=os.path.getctime)
            os.remove(youngest_file)

        # bgr_img = cv2.cvtColor(clip_img, cv2.COLOR_RGB2BGR)
        cv2.imwrite(img_name, clip_img)
    else:
        print("{} already exists".format(img_name))
    return img_name


def load_face_encodings(known_face_dir):
    known_face_encodings = []
    known_face_names = []

    for root, dirs, files in os.walk(known_face_dir):
        for f in files:
            face_name = root.split(os.sep)[-1]
            img_file = os.path.join(root, f)
            img = faceapi.load_image_file(img_file)
            print(0, img.shape[1], img.shape[0], 0)
            encodings = faceapi.face_encodings(img, [(0, img.shape[1], img.shape[0], 0)])
            assert len(encodings) == 1
            if len(encodings) == 1:
                known_face_encodings.append(encodings[0])
                known_face_names.append(face_name)
    return known_face_encodings, known_face_names


class FaceRecog():
    def __init__(self, known_face_dir, state_dict=None, threshold=0.4):
        self.known_face_dir = known_face_dir
        self.tolerance = threshold
        face_encoding_names = load_face_encodings(known_face_dir)
        self.known_face_encodings = face_encoding_names[0]
        self.known_face_names = face_encoding_names[1]

    def add_new_face(self, img, face_name, face_location, save=True):
        encodings = faceapi.face_encodings(img, [face_location])
        if len(encodings) < 1:
            # raise(ValueError("no face detected"))
            print("No face detected")
            return
        face_encoding = encodings[0]
        self.known_face_names.append(face_name)
        self.known_face_encodings.append(face_encoding)
        # save image on disk
        if save:
            if not os.path.exists(self.known_face_dir):
                os.mkdir(self.known_face_dir)
            save_new_face(self.known_face_dir, face_name, face_location, img)

    def run(self, rgb_frame, face_locations):
        face_encodings = faceapi.face_encodings(rgb_frame, face_locations)
        names = []
        for face_encoding in face_encodings:
            face_distances = faceapi.face_distance(self.known_face_encodings,
                                                   face_encoding)
            name = "Unknown"
            if len(face_distances) >= 1:
                best_match_index = np.argmin(face_distances)
                if face_distances[best_match_index] < self.tolerance:
                    name = self.known_face_names[best_match_index]
                else:
                    print(face_distances[best_match_index], self.tolerance)
                names.append(name)
        return names
