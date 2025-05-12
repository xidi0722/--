# finger_execute.py
import socket
import time
import os
import subprocess
import webbrowser
import json

CONFIG_FILE = 'config.json'

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {str(i): "" for i in range(1, 6)}

def finger_execute(mapping):
    """
    持續重試連線，連上後監聽 socket
    連續收到同一個手勢數字 3 次時，就根據 mapping 執行對應動作
    """
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while True:
        try:
            client.connect(('100.105.82.116', 54230))
            print(" 已連上手勢伺服器 100.105.82.116:54230")
            break
        except Exception as e:
            print(f"連線失敗，5 秒後重試… ({e})")
            time.sleep(5)

    last = None
    consec = 0

    with client.makefile('r') as rf:
        for line in rf:
            try:
                count = int(line.strip())
            except ValueError:
                continue

            if count == last:
                consec += 1
            else:
                last = count
                consec = 1

            if consec == 3:
                cmd = mapping.get(str(count), "")
                if cmd:
                    if cmd.lower().startswith(("http://", "https://")):
                        webbrowser.open(cmd)
                        print(f"[Action] 開啟網址：{cmd}")
                    elif os.path.exists(cmd):
                        os.startfile(cmd)
                        print(f"[Action] 啟動程式：{cmd}")
                    else:
                        subprocess.Popen(cmd, shell=True)
                        print(f"[Action] 執行指令：{cmd}")
                else:
                    print(f"[Warning] finger{count} 尚未設定動作")
            print(f"[Info] 收到 {count}（連續 {consec} 次）")

if __name__ == "__main__":
    mapping = load_config()
    finger_execute(mapping)
