import sys
import os
import json
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QListWidget, QListWidgetItem, QFileDialog, QMenu, QToolTip
from PyQt5.QtCore import Qt

# 設定基底目錄
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# 指定存放 JSON 檔案的資料夾，並檢查如果不存在就建立
JSON_DIR = os.path.join(BASE_DIR, "action_json")
if not os.path.exists(JSON_DIR):
    os.makedirs(JSON_DIR)
# 將持久化檔案存放在 action_json 資料夾中
PERSISTENT_FILE = os.path.join(JSON_DIR, "persistent_files.json")
ACTION_FOLDER = os.path.join(BASE_DIR, "action_folder")
if not os.path.exists(ACTION_FOLDER):
    os.makedirs(ACTION_FOLDER)

class CustomDropdown(QWidget):
    def __init__(self, options, label_text="請選擇:", identifier="default", persistent_file=None, parent=None):
        """
        identifier 用來區分不同下拉選單的最後選取檔案
        persistent_file 用來指定此下拉選單新增選項的存放檔案，不提供則採用全域預設值
        """
        super().__init__(parent)
        self.options = options
        self.identifier = identifier
        # 如果有指定 persistent_file 就使用它，否則使用全域預設的 PERSISTENT_FILE
        self.persistent_file = persistent_file if persistent_file else PERSISTENT_FILE
        
        # 每個下拉選單使用獨立的最後選取檔案
        self.last_selection_file = os.path.join(JSON_DIR, f"last_selection_{self.identifier}.json")
        
        # 讀取已儲存的新增檔案路徑
        self.persistent_options = self.loadPersistentOptions()
        
        # 將預設選項與持久化選項合併，統一格式為 (顯示文字, 完整路徑)
        self.all_options = []
        for opt in self.options:
            if isinstance(opt, tuple):
                self.all_options.append(opt)
            else:
                self.all_options.append((opt, opt))
        for file_path in self.persistent_options:
            display_name = os.path.basename(file_path)
            self.all_options.append((display_name, file_path))
        
        # 預設選項，先以 all_options 的第一個作為預設
        if self.all_options:
            first = self.all_options[0]
            self.current_selection = first[1]  # 取得完整路徑
            first_display = first[0]
        else:
            self.current_selection = ""
            first_display = ""
        
        # 如果有先前儲存的最後選取值，則更新 current_selection 與按鈕顯示
        last = self.loadLastSelection()
        if last:
            self.current_selection = last
            for display_text, file_path in self.all_options:
                if file_path == last:
                    first_display = display_text
                    break
            else:
                first_display = os.path.basename(last)
        
        # 建立水平佈局，設定邊距與間距
        h_layout = QHBoxLayout()
        h_layout.setContentsMargins(30, 30, 30, 30)
        h_layout.setSpacing(10)
        
        # 建立並加入 label
        self.label = QLabel(label_text, self)
        font_label = self.label.font()
        font_label.setPointSize(14)
        self.label.setFont(font_label)
        h_layout.addWidget(self.label)
        
        # 建立按鈕並設定固定寬度與高度
        self.button = QPushButton(first_display, self)
        self.button.setFixedWidth(750)
        self.button.setFixedHeight(50)
        font_button = self.button.font()
        font_button.setPointSize(14)
        self.button.setFont(font_button)
        h_layout.addWidget(self.button)
        self.button.clicked.connect(self.showPopup)
        
        # 設定自訂元件的主要佈局
        self.setLayout(h_layout)
        
        # 建立下拉選項列表，作為彈出視窗
        self.listWidget = QListWidget()
        for display_text, file_path in self.all_options:
            item = QListWidgetItem(display_text, self.listWidget)
            item.setData(Qt.UserRole, file_path)
        # 永遠保留最後一項為「新增選項」
        self.new_item = QListWidgetItem("新增選項", self.listWidget)
        self.listWidget.itemClicked.connect(self.onItemClicked)
        self.listWidget.setWindowFlags(Qt.Popup)
        
        # 設定右鍵選單 (僅對持久化項目提供刪除功能)
        self.listWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.listWidget.customContextMenuRequested.connect(self.onCustomContextMenu)
    
    def loadPersistentOptions(self):
        """讀取已儲存的檔案路徑，回傳路徑列表"""
        if os.path.exists(self.persistent_file):
            try:
                with open(self.persistent_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, list):
                    return data
            except Exception as e:
                print("讀取持久化檔案失敗:", e)
        return []
    
    def savePersistentOptions(self):
        """儲存目前的持久化檔案路徑列表"""
        try:
            with open(self.persistent_file, "w", encoding="utf-8") as f:
                json.dump(self.persistent_options, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print("儲存持久化檔案失敗:", e)
    
    def loadLastSelection(self):
        """讀取最後選取的檔案路徑"""
        if os.path.exists(self.last_selection_file):
            try:
                with open(self.last_selection_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, str):
                    return data
            except Exception as e:
                print("讀取最後選取檔案失敗:", e)
        return None
    
    def saveLastSelection(self):
        """儲存目前的最後選取檔案路徑"""
        try:
            with open(self.last_selection_file, "w", encoding="utf-8") as f:
                json.dump(self.current_selection, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print("儲存最後選取檔案失敗:", e)
    
    def showPopup(self):
        if self.listWidget.isVisible():
            self.listWidget.hide()
            return
        # 使下拉列表寬度與按鈕一致
        self.listWidget.setFixedWidth(self.button.width())
        # 將下拉列表定位在按鈕下方
        pos = self.button.mapToGlobal(self.button.rect().bottomLeft())
        self.listWidget.move(pos)
        self.listWidget.show()
        self.listWidget.setFocus()
    
    def onItemClicked(self, item):
        if item.text() == "新增選項":
            # 指定從 ACTION_FOLDER 開始選擇檔案
            file_name, _ = QFileDialog.getOpenFileName(self, "選擇檔案", ACTION_FOLDER, "All Files (*);;Text Files (*.txt)")
            if file_name:
                display_name = os.path.basename(file_name)
                self.current_selection = file_name  # 儲存完整路徑
                self.button.setText(display_name)
                new_item = QListWidgetItem(display_name)
                new_item.setData(Qt.UserRole, file_name)
                insert_index = self.listWidget.count() - 1  # 在「新增選項」前插入
                self.listWidget.insertItem(insert_index, new_item)
                if file_name not in self.persistent_options:
                    self.persistent_options.append(file_name)
                    self.savePersistentOptions()
                self.saveLastSelection()
                print("選擇檔案的完整路徑:", file_name)
        else:
            stored_path = item.data(Qt.UserRole)
            if stored_path:
                self.current_selection = stored_path
            else:
                self.current_selection = item.text()
            self.button.setText(item.text())
            self.saveLastSelection()
            print("選擇預設項目的完整路徑:", self.current_selection)
        self.listWidget.hide()
    
    def onCustomContextMenu(self, pos):
        item = self.listWidget.itemAt(pos)
        if not item:
            return
        if item.text() == "新增選項":
            return
        file_path = item.data(Qt.UserRole)
        if file_path not in self.persistent_options:
            QToolTip.showText(self.listWidget.viewport().mapToGlobal(pos), "預設選項無法刪除", self.listWidget)
            return
    
        menu = QMenu()
        delete_action = menu.addAction("刪除")
        action = menu.exec_(self.listWidget.viewport().mapToGlobal(pos))
        if action == delete_action:
            self.persistent_options.remove(file_path)
            self.savePersistentOptions()
            row = self.listWidget.row(item)
            self.listWidget.takeItem(row)
            print("已刪除檔案:", file_path)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = QWidget()
    window.setWindowTitle("自訂下拉選單範例")
    
    default_options = [
        ("預設動作1", r"C:\path\to\file1.txt"),
        ("預設動作2", r"C:\path\to\file2.txt"),
        ("預設動作3", r"C:\path\to\file3.txt"),
        ("預設動作4", r"C:\path\to\file4.txt")
    ]
    
    main_layout = QVBoxLayout(window)
    main_layout.setContentsMargins(20, 20, 20, 20)
    
    # 第一個下拉選單，使用原有的 persistent_file (預設值)
    dropdown1 = CustomDropdown(default_options, label_text="開機", identifier="dropdown1")
    # 第二個下拉選單，使用原有的 persistent_file (預設值)
    dropdown2 = CustomDropdown(default_options, label_text="關機", identifier="dropdown2")
    # 第三個下拉選單，指定一個不同的 persistent_file，與前兩個獨立
    dropdown3 = CustomDropdown(default_options, label_text="自訂動作", identifier="dropdown3",
                               persistent_file=os.path.join(JSON_DIR, "persistent_files_dropdown3.json"))
    
    main_layout.addWidget(dropdown1, alignment=Qt.AlignCenter)
    main_layout.addWidget(dropdown2, alignment=Qt.AlignCenter)
    main_layout.addWidget(dropdown3, alignment=Qt.AlignCenter)
    
    window.show()
    sys.exit(app.exec_())