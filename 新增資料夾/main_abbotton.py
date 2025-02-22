import sys
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication,QDialog
from PyQt5.uic import loadUi
import RPi.GPIO as gpio

led = 26

gpio.setmode(gpio.BCM)
gpio.setwarnings(False)
gpio.setup(led,gpio.OUT)

class HMI(QDialog):
    def __int__(self):
        super(ui,self).__init__()
        loadUi('ab_botton.ui',self)
        
        self.setWindowTitle('HMI System')
        self.bta.clicke.connect(self.on_off)
    @pyqtSlot()
    def on_off(self):
        if gpio.input(led):
            gpio.output(led,gpio.LOW)
            self.bta.setText('OFF')
            self.status.setText('LED Status is OFF')
        else:
            gpio.output(led,gpio.HIGH)
            self.bta.setText('ON')
            self.status.setText('LED status is ON')
app=QApplication(sys.argv)
widget=HMI()
widget.show()
sys.exit(app.exec())