import cv2
from simple_facerec import SimpleFacerec

#流程:打開鏡頭偵測人臉有未知的人臉就跳出並抓取這個人臉 再次啟動時可以命名上次偵測的未知人臉
#如果是已知的人臉則會框住並挑出命名的名字

#載入和編譯每張圖片
class face_rec(SimpleFacerec):
    def __init__(self):
        super().__init__()
        #移除資料庫中未知人臉的檔案
        self.remove_encoding_images("images/")
        #將有人臉但名字為Unkown的檔案重新命名人臉
        self.refilename("images/")
        #載入和編譯圖片
        self.load_encoding_images("images/")
        
    def face(self):
        cap = cv2.VideoCapture(0)
        while True:
            ret,m_frame = cap.read()
            #左右翻轉
            frame=cv2.flip(m_frame,1)
            # 偵測臉部 
            face_locations, face_names = self.detect_known_faces(frame)

            for face_loc, name in zip(face_locations, face_names):
                #臉的位置
                y1, x2, y2, x1 = face_loc[0], face_loc[1], face_loc[2], face_loc[3]
                cv2.putText(frame, name,(x1, y1 - 10), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 200), 2)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 200), 4)
            #偵測到未知的人臉後跳出
            if "Unknown" in face_names:
                break
            #顯示影片流
            cv2.imshow("Frame", frame)
            if cv2.waitKey(1) == ord('q'):
                break
        #移除人臉
        self.remove_encoding_images("images/")
        cap.release()
        cv2.destroyAllWindows()
