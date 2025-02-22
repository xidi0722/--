# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'motor.ui'
##
## Created by: Qt User Interface Compiler version 6.7.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QLabel, QPushButton, QSizePolicy,
    QSlider, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(400, 300)
        self.Slider = QSlider(Form)
        self.Slider.setObjectName(u"Slider")
        self.Slider.setGeometry(QRect(40, 210, 241, 16))
        self.Slider.setOrientation(Qt.Orientation.Horizontal)
        self.angle = QLabel(Form)
        self.angle.setObjectName(u"angle")
        self.angle.setGeometry(QRect(60, 170, 81, 41))
        self.label_2 = QLabel(Form)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(150, 30, 231, 41))
        self.angel_num = QLabel(Form)
        self.angel_num.setObjectName(u"angel_num")
        self.angel_num.setGeometry(QRect(140, 180, 71, 21))
        self.Button1 = QPushButton(Form)
        self.Button1.setObjectName(u"Button1")
        self.Button1.setGeometry(QRect(60, 140, 75, 24))

        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.angle.setText(QCoreApplication.translate("Form", u"motor angle :", None))
        self.label_2.setText(QCoreApplication.translate("Form", u"\u8235\u6a5f\u6e2c\u8a66", None))
        self.angel_num.setText(QCoreApplication.translate("Form", u"0", None))
        self.Button1.setText(QCoreApplication.translate("Form", u"start", None))
    # retranslateUi

