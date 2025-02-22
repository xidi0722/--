import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout

class MyApp(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.bta = QPushButton("Save", self)  # Save 按鈕
        self.bta.clicked.connect(self.save_action)

        self.btb = QPushButton("Play", self)  # Play 按鈕
        self.btb.clicked.connect(self.play_action)

        layout.addWidget(self.bta)
        layout.addWidget(self.btb)

        self.setLayout(layout)
        self.setWindowTitle("Simple UI")
        self.setGeometry(100, 100, 300, 200)

    def save_action(self):
        print("Save button clicked!")

    def play_action(self):
        print("Play button clicked!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())
