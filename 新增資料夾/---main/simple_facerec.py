import face_recognition
import cv2
import os
import glob
import numpy as np
#此為人臉識別的套件庫 拿來import用 調整人臉識別的速度和靈敏度以及函數運作在這裡調
class SimpleFacerec:
    def __init__(self):
        self.known_face_encodings = []
        self.known_face_names = []
        self.unknown_count = 1
        # 調整resize可以調整辨識速度
        self.frame_resizing = 0.25
        self.face_Sensitivity= 0.5
    def load_encoding_images(self, images_path):
        """
        Load encoding images from path
        :param images_path:
        :return:
        """
        # Load Images
        images_path = glob.glob(os.path.join(images_path, "*.*"))

        print("{} encoding images found.".format(len(images_path)))

        #讀入圖片和解碼圖片
        for img_path in images_path:
            img = cv2.imread(img_path)
            if img is None:
                print(f"Warning: Image at {img_path} could not be loaded.")
                continue
            rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_img)
           
           
            # Get the filename only from the initial file path.
            basename = os.path.basename(img_path)
            (filename, ext) = os.path.splitext(basename)
            # Get encoding
            img_encoding = face_recognition.face_encodings(rgb_img)[0]

            # Store file name and file encoding
            self.known_face_encodings.append(img_encoding)
            self.known_face_names.append(filename)
        print("Encoding images loaded")
    def remove_encoding_images(self, images_path):
        #移除沒有人臉的檔案
        """
        Load encoding images from path
        :param images_path:
        :return:
        """
        # 載入圖片
        images_path = glob.glob(os.path.join(images_path, "*.*"))

        print("{} encoding images found.".format(len(images_path)))

        # Store image encoding and names
        for img_path in images_path:
            img = cv2.imread(img_path)
            if img is None:
                print(f"Warning: Image at {img_path} could not be loaded.")
                continue
            rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_img)
            face_encodings = face_recognition.face_encodings(rgb_img, face_locations)
            #移除沒有臉的檔案
            if len(face_encodings) == 0:
                print(f"No faces found in image {img_path}.")
                os.remove(img_path)
                continue

    def detect_known_faces(self, frame):
        #偵測沒有已知臉的檔案
        small_frame = cv2.resize(frame, (0, 0), fx=self.frame_resizing, fy=self.frame_resizing)
        # Find all the faces and face encodings in the current frame of video
        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        face_names = []
        for face_encoding in face_encodings:
            # See if the face is a match for the known face(s)
            matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding,self.face_Sensitivity)#調整靈敏度
            name = "Unknown"

            # # If a match was found in known_face_encodings, just use the first one.
            # if True in matches:
            #     first_match_index = matches.index(True)
            #     name = known_face_names[first_match_index]

            # Or instead, use the known face with the smallest distance to the new face
            face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)#最小距離的索引
            if matches[best_match_index]:
                name = self.known_face_names[best_match_index]
            self.unknown_count+= 1
            
            face_names.append(name)
            #寫入未知人臉的檔案
            if name == "Unknown" and len(face_locations)>0:
                cv2.imwrite("C:/Users/USER/Desktop/program/opencv/source code/images/unknown"+str(self.unknown_count)+".jpg",frame)
                self.face_Sensitivity=0.5
                self.unknown_count+=1
        # Convert to numpy array to adjust coordinates with frame resizing quickly
        face_locations = np.array(face_locations)
        face_locations = face_locations / self.frame_resizing
        return face_locations.astype(int), face_names
    
    def refilename(self, images_path):
        #偵側有臉的檔案後重新為這個人臉命名
        images_path = glob.glob(os.path.join(images_path, "*.*"))
        for img_path in images_path:
            img = cv2.imread(img_path)
            if img is None:
                print(f"Warning: Image at {img_path} could not be loaded.")
                continue
            rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_img)
            face_encodings = face_recognition.face_encodings(rgb_img, face_locations)
            # Skip files with no faces
            if len(face_encodings) == 0:
                print(f"No faces found in image {img_path}.")
                os.remove(img_path)
                continue

            # Get the filename only from the initial file path.
            basename = os.path.basename(img_path)
            (filename, ext) = os.path.splitext(basename)

            if "unknown" in filename:
                new_filename = input("Please enter the detected face name: ")
                new_path = os.path.join(os.path.dirname(img_path), f"{new_filename}{ext}")
                os.rename(img_path, new_path)
                print(f"Renamed {img_path} to {new_path}")