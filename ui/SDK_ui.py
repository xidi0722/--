# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'SDK.ui'
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
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QSizePolicy,
    QSlider, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(581, 425)
        self.Slider3 = QSlider(Form)
        self.Slider3.setObjectName(u"Slider3")
        self.Slider3.setGeometry(QRect(80, 150, 160, 16))
        self.Slider3.setOrientation(Qt.Orientation.Horizontal)
        self.Slider4 = QSlider(Form)
        self.Slider4.setObjectName(u"Slider4")
        self.Slider4.setGeometry(QRect(80, 210, 160, 16))
        self.Slider4.setOrientation(Qt.Orientation.Horizontal)
        self.Slider2 = QSlider(Form)
        self.Slider2.setObjectName(u"Slider2")
        self.Slider2.setGeometry(QRect(80, 100, 160, 16))
        self.Slider2.setOrientation(Qt.Orientation.Horizontal)
        self.label_2 = QLabel(Form)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(10, 100, 53, 16))
        self.label_3 = QLabel(Form)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(10, 150, 53, 16))
        self.label_4 = QLabel(Form)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setGeometry(QRect(10, 210, 53, 16))
        self.label_7 = QLabel(Form)
        self.label_7.setObjectName(u"label_7")
        self.label_7.setGeometry(QRect(60, 100, 41, 16))
        self.label_8 = QLabel(Form)
        self.label_8.setObjectName(u"label_8")
        self.label_8.setGeometry(QRect(250, 100, 53, 16))
        self.label_9 = QLabel(Form)
        self.label_9.setObjectName(u"label_9")
        self.label_9.setGeometry(QRect(250, 150, 53, 16))
        self.label_10 = QLabel(Form)
        self.label_10.setObjectName(u"label_10")
        self.label_10.setGeometry(QRect(250, 210, 53, 16))
        self.label_11 = QLabel(Form)
        self.label_11.setObjectName(u"label_11")
        self.label_11.setGeometry(QRect(60, 150, 41, 16))
        self.label_12 = QLabel(Form)
        self.label_12.setObjectName(u"label_12")
        self.label_12.setGeometry(QRect(60, 210, 41, 16))
        self.widget = QWidget(Form)
        self.widget.setObjectName(u"widget")
        self.widget.setGeometry(QRect(10, 40, 271, 41))
        self.horizontalLayoutWidget = QWidget(self.widget)
        self.horizontalLayoutWidget.setObjectName(u"horizontalLayoutWidget")
        self.horizontalLayoutWidget.setGeometry(QRect(0, -20, 261, 80))
        self.horizontalLayout = QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.label = QLabel(self.horizontalLayoutWidget)
        self.label.setObjectName(u"label")

        self.horizontalLayout.addWidget(self.label)

        self.label_5 = QLabel(self.horizontalLayoutWidget)
        self.label_5.setObjectName(u"label_5")

        self.horizontalLayout.addWidget(self.label_5)

        self.Slider1 = QSlider(self.horizontalLayoutWidget)
        self.Slider1.setObjectName(u"Slider1")
        self.Slider1.setOrientation(Qt.Orientation.Horizontal)

        self.horizontalLayout.addWidget(self.Slider1)

        self.label_6 = QLabel(self.horizontalLayoutWidget)
        self.label_6.setObjectName(u"label_6")

        self.horizontalLayout.addWidget(self.label_6)

        self.Slider_num1 = QLabel(Form)
        self.Slider_num1.setObjectName(u"Slider_num1")
        self.Slider_num1.setGeometry(QRect(160, 20, 53, 16))
        self.Slider_num2 = QLabel(Form)
        self.Slider_num2.setObjectName(u"Slider_num2")
        self.Slider_num2.setGeometry(QRect(80, 80, 53, 16))
        self.Slider_num3 = QLabel(Form)
        self.Slider_num3.setObjectName(u"Slider_num3")
        self.Slider_num3.setGeometry(QRect(80, 130, 53, 16))
        self.Slider_num4 = QLabel(Form)
        self.Slider_num4.setObjectName(u"Slider_num4")
        self.Slider_num4.setGeometry(QRect(80, 190, 53, 16))
        self.Panda3DContainer = QWidget(Form)
        self.Panda3DContainer.setObjectName(u"Panda3DContainer")
        self.Panda3DContainer.setGeometry(QRect(290, 30, 261, 251))
        self.widget.raise_()
        self.Slider3.raise_()
        self.Slider4.raise_()
        self.Slider2.raise_()
        self.label_2.raise_()
        self.label_3.raise_()
        self.label_4.raise_()
        self.label_7.raise_()
        self.label_8.raise_()
        self.label_9.raise_()
        self.label_10.raise_()
        self.label_11.raise_()
        self.label_12.raise_()
        self.Slider_num1.raise_()
        self.Slider_num2.raise_()
        self.Slider_num3.raise_()
        self.Slider_num4.raise_()
        self.Panda3DContainer.raise_()

        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.label_2.setText(QCoreApplication.translate("Form", u"BODY", None))
        self.label_3.setText(QCoreApplication.translate("Form", u"LEFT", None))
        self.label_4.setText(QCoreApplication.translate("Form", u"RIGHT", None))
        self.label_7.setText(QCoreApplication.translate("Form", u"0", None))
        self.label_8.setText(QCoreApplication.translate("Form", u"180", None))
        self.label_9.setText(QCoreApplication.translate("Form", u"180", None))
        self.label_10.setText(QCoreApplication.translate("Form", u"180", None))
        self.label_11.setText(QCoreApplication.translate("Form", u"0", None))
        self.label_12.setText(QCoreApplication.translate("Form", u"0", None))
        self.label.setText(QCoreApplication.translate("Form", u"HEAD   ", None))
        self.label_5.setText(QCoreApplication.translate("Form", u"0  ", None))
        self.label_6.setText(QCoreApplication.translate("Form", u"180", None))
        self.Slider_num1.setText(QCoreApplication.translate("Form", u"90", None))
        self.Slider_num2.setText(QCoreApplication.translate("Form", u"0", None))
        self.Slider_num3.setText(QCoreApplication.translate("Form", u"0", None))
        self.Slider_num4.setText(QCoreApplication.translate("Form", u"0", None))
    # retranslateUi

