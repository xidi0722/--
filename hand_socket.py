# finger_execute.py（Pi 端整合版）
import subprocess
import cv2
import mediapipe as mp
import socket
import threading
import time
import os

# --- 全域旗標，控制是否開啟攝影機偵測 ---
camera_enabled = False

# Mediapipe Hands 相關設定
mp_hands   = mp.solutions.hands
mp_draw    = mp.solutions.drawing_utils
hands      = mp_hands.Hands(static_image_mode=False,
                            max_num_hands=2,
                            min_detection_confidence=0.7,
                            min_tracking_confidence=0.7)
tipIds     = [4, 8, 12, 16, 20]

def control_server(host='0.0.0.0', port=54231):
    """
    專門負責接收 'camera 1' / 'camera 0' 指令，
    根據這個指令打開或關閉偵測。
    """
    global camera_enabled
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((host, port))
    srv.listen(1)
    print(f"[Control] Listening on {port} for camera commands...")
    while True:
        conn, addr = srv.accept()
        with conn:
            data = conn.recv(1024).decode('utf-8').strip()
            if data == 'camera 1':
                camera_enabled = True
                print("[Control] Camera enabled")
            elif data == 'camera 0':
                camera_enabled = False
                print("[Control] Camera disabled")
            else:
                print(f"[Control] Unknown command: {data}")

def gesture_server(host='0.0.0.0', port=54230):
    """
    原本的手勢伺服器：拍照->偵測->傳 count。
    當 camera_enabled=False 時，跳過拍照偵測，CPU 休息。
    """
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((host, port))
    srv.listen(1)
    print(f"[Gesture] Listening on {port} for client...")
    conn, addr = srv.accept()
    print(f"[Gesture] Client connected: {addr}")

    try:
        while True:
            # 如果攝影機沒打開，就休息一下
            if not camera_enabled:
                time.sleep(0.1)
                continue

            # 拍一張靜態圖
            subprocess.run([
                "libcamera-still", "-n", "-t", "1",
                "-o", "frame.jpg", "--width", "640", "--height", "480"
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            img = cv2.imread("frame.jpg")
            if img is None:
                continue

            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            results = hands.process(img_rgb)

            if results.multi_hand_landmarks:
                h, w, _ = img.shape
                for hand_no, lm in enumerate(results.multi_hand_landmarks):
                    mp_draw.draw_landmarks(img, lm, mp_hands.HAND_CONNECTIONS)

                    # 轉成 (id, x_px, y_px)
                    lmList = [(idx,
                               int(pt.x * w),
                               int(pt.y * h))
                              for idx, pt in enumerate(lm.landmark)]
                    # 判斷左右手
                    label = results.multi_handedness[hand_no].classification[0].label
                    label = "Right" if label=="Left" else "Left"

                    # 計算總張手指
                    fingers = []
                    # 拇指
                    if label == "Right":
                        fingers.append(1 if lmList[tipIds[0]][1] > lmList[tipIds[0]-1][1] else 0)
                    else:
                        fingers.append(1 if lmList[tipIds[0]][1] < lmList[tipIds[0]-1][1] else 0)
                    # 其他四指
                    for i in range(1,5):
                        fingers.append(1 if lmList[tipIds[i]][2] < lmList[tipIds[i]-2][2] else 0)

                    totalFingers = sum(fingers)
                    # 傳送到 client
                    try:
                        conn.sendall(f"{totalFingers}\n".encode('utf-8'))
                    except BrokenPipeError:
                        print("[Gesture] Client disconnected, exiting.")
                        return

            # 顯示視窗（可選）
            cv2.imshow("MediaPipe Hands", img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        hands.close()
        conn.close()
        srv.close()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    # 分別啟動兩個 Thread
    t_ctrl = threading.Thread(target=control_server, daemon=True)
    t_ctrl.start()
    # 主線程執行手勢伺服器
    gesture_server()
