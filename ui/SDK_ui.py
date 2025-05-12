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
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QSizePolicy, QSlider, QVBoxLayout,
    QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(950, 600)
        self.actionpage = QAction(Form)
        self.actionpage.setObjectName(u"actionpage")
        self.actionpage.setMenuRole(QAction.MenuRole.NoRole)
        self.widget = QWidget(Form)
        self.widget.setObjectName(u"widget")
        self.widget.setGeometry(QRect(10, 80, 271, 41))
        self.Panda3DContainer = QWidget(Form)
        self.Panda3DContainer.setObjectName(u"Panda3DContainer")
        self.Panda3DContainer.setGeometry(QRect(330, 0, 281, 281))
        self.expression_label = QLabel(Form)
        self.expression_label.setObjectName(u"expression_label")
        self.expression_label.setGeometry(QRect(630, 110, 131, 161))
        self.verticalLayoutWidget = QWidget(Form)
        self.verticalLayoutWidget.setObjectName(u"verticalLayoutWidget")
        self.verticalLayoutWidget.setGeometry(QRect(20, 300, 151, 261))
        self.verticalLayout = QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.store_button = QPushButton(self.verticalLayoutWidget)
        self.store_button.setObjectName(u"store_button")

        self.verticalLayout.addWidget(self.store_button)

        self.reset_button = QPushButton(self.verticalLayoutWidget)
        self.reset_button.setObjectName(u"reset_button")

        self.verticalLayout.addWidget(self.reset_button)

        self.store_file = QPushButton(self.verticalLayoutWidget)
        self.store_file.setObjectName(u"store_file")

        self.verticalLayout.addWidget(self.store_file)

        self.play_button = QPushButton(self.verticalLayoutWidget)
        self.play_button.setObjectName(u"play_button")

        self.verticalLayout.addWidget(self.play_button)

        self.play_file = QPushButton(self.verticalLayoutWidget)
        self.play_file.setObjectName(u"play_file")

        self.verticalLayout.addWidget(self.play_file)

        self.verticalLayoutWidget_2 = QWidget(Form)
        self.verticalLayoutWidget_2.setObjectName(u"verticalLayoutWidget_2")
        self.verticalLayoutWidget_2.setGeometry(QRect(20, 60, 281, 211))
        self.verticalLayout_2 = QVBoxLayout(self.verticalLayoutWidget_2)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label = QLabel(self.verticalLayoutWidget_2)
        self.label.setObjectName(u"label")

        self.horizontalLayout.addWidget(self.label)

        self.label_5 = QLabel(self.verticalLayoutWidget_2)
        self.label_5.setObjectName(u"label_5")

        self.horizontalLayout.addWidget(self.label_5)

        self.Slider1 = QSlider(self.verticalLayoutWidget_2)
        self.Slider1.setObjectName(u"Slider1")
        self.Slider1.setOrientation(Qt.Orientation.Horizontal)

        self.horizontalLayout.addWidget(self.Slider1)

        self.label_6 = QLabel(self.verticalLayoutWidget_2)
        self.label_6.setObjectName(u"label_6")

        self.horizontalLayout.addWidget(self.label_6)


        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.label_3 = QLabel(self.verticalLayoutWidget_2)
        self.label_3.setObjectName(u"label_3")

        self.horizontalLayout_5.addWidget(self.label_3)

        self.label_9 = QLabel(self.verticalLayoutWidget_2)
        self.label_9.setObjectName(u"label_9")

        self.horizontalLayout_5.addWidget(self.label_9)

        self.Slider3 = QSlider(self.verticalLayoutWidget_2)
        self.Slider3.setObjectName(u"Slider3")
        self.Slider3.setOrientation(Qt.Orientation.Horizontal)

        self.horizontalLayout_5.addWidget(self.Slider3)

        self.label_11 = QLabel(self.verticalLayoutWidget_2)
        self.label_11.setObjectName(u"label_11")

        self.horizontalLayout_5.addWidget(self.label_11)


        self.verticalLayout_2.addLayout(self.horizontalLayout_5)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label_2 = QLabel(self.verticalLayoutWidget_2)
        self.label_2.setObjectName(u"label_2")

        self.horizontalLayout_3.addWidget(self.label_2)

        self.label_7 = QLabel(self.verticalLayoutWidget_2)
        self.label_7.setObjectName(u"label_7")

        self.horizontalLayout_3.addWidget(self.label_7)

        self.Slider2 = QSlider(self.verticalLayoutWidget_2)
        self.Slider2.setObjectName(u"Slider2")
        self.Slider2.setOrientation(Qt.Orientation.Horizontal)

        self.horizontalLayout_3.addWidget(self.Slider2)

        self.label_8 = QLabel(self.verticalLayoutWidget_2)
        self.label_8.setObjectName(u"label_8")

        self.horizontalLayout_3.addWidget(self.label_8)


        self.verticalLayout_2.addLayout(self.horizontalLayout_3)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.label_16 = QLabel(self.verticalLayoutWidget_2)
        self.label_16.setObjectName(u"label_16")

        self.horizontalLayout_6.addWidget(self.label_16)

        self.label_17 = QLabel(self.verticalLayoutWidget_2)
        self.label_17.setObjectName(u"label_17")

        self.horizontalLayout_6.addWidget(self.label_17)

        self.Slider4 = QSlider(self.verticalLayoutWidget_2)
        self.Slider4.setObjectName(u"Slider4")
        self.Slider4.setOrientation(Qt.Orientation.Horizontal)

        self.horizontalLayout_6.addWidget(self.Slider4)

        self.label_18 = QLabel(self.verticalLayoutWidget_2)
        self.label_18.setObjectName(u"label_18")

        self.horizontalLayout_6.addWidget(self.label_18)


        self.verticalLayout_2.addLayout(self.horizontalLayout_6)

        self.Slider_num1 = QLabel(Form)
        self.Slider_num1.setObjectName(u"Slider_num1")
        self.Slider_num1.setGeometry(QRect(180, 50, 53, 16))
        self.Slider_num2 = QLabel(Form)
        self.Slider_num2.setObjectName(u"Slider_num2")
        self.Slider_num2.setGeometry(QRect(180, 100, 53, 16))
        self.Slider_num3 = QLabel(Form)
        self.Slider_num3.setObjectName(u"Slider_num3")
        self.Slider_num3.setGeometry(QRect(180, 160, 53, 16))
        self.Slider_num4 = QLabel(Form)
        self.Slider_num4.setObjectName(u"Slider_num4")
        self.Slider_num4.setGeometry(QRect(180, 210, 53, 16))
        self.horizontalLayoutWidget_2 = QWidget(Form)
        self.horizontalLayoutWidget_2.setObjectName(u"horizontalLayoutWidget_2")
        self.horizontalLayoutWidget_2.setGeometry(QRect(200, 290, 721, 261))
        self.capturedImagesLayout = QHBoxLayout(self.horizontalLayoutWidget_2)
        self.capturedImagesLayout.setObjectName(u"capturedImagesLayout")
        self.capturedImagesLayout.setContentsMargins(0, 0, 0, 0)
        self.capturedImagesScrollArea = QScrollArea(self.horizontalLayoutWidget_2)
        self.capturedImagesScrollArea.setObjectName(u"capturedImagesScrollArea")
        self.capturedImagesScrollArea.setWidgetResizable(True)
        self.scrollwidget = QWidget()
        self.scrollwidget.setObjectName(u"scrollwidget")
        self.scrollwidget.setGeometry(QRect(0, 0, 717, 257))
        self.scrollAreaWidgetContents = QWidget(self.scrollwidget)
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(30, 30, 671, 191))
        self.capturedImagesScrollArea.setWidget(self.scrollwidget)

        self.capturedImagesLayout.addWidget(self.capturedImagesScrollArea)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.actionpage.setText(QCoreApplication.translate("Form", u"page", None))
        self.expression_label.setText("")
        self.store_button.setText(QCoreApplication.translate("Form", u"store", None))
        self.reset_button.setText(QCoreApplication.translate("Form", u"reset", None))
        self.store_file.setText(QCoreApplication.translate("Form", u"save_file", None))
        self.play_button.setText(QCoreApplication.translate("Form", u"Play", None))
        self.play_file.setText(QCoreApplication.translate("Form", u"play_file", None))
        self.label.setText(QCoreApplication.translate("Form", u"HEAD   ", None))
        self.label_5.setText(QCoreApplication.translate("Form", u"-90", None))
        self.label_6.setText(QCoreApplication.translate("Form", u"90", None))
        self.label_3.setText(QCoreApplication.translate("Form", u"LEFT      ", None))
        self.label_9.setText(QCoreApplication.translate("Form", u"-90", None))
        self.label_11.setText(QCoreApplication.translate("Form", u"90", None))
        self.label_2.setText(QCoreApplication.translate("Form", u"BODY   ", None))
        self.label_7.setText(QCoreApplication.translate("Form", u"-90", None))
        self.label_8.setText(QCoreApplication.translate("Form", u"90", None))
        self.label_16.setText(QCoreApplication.translate("Form", u"RIGHT   ", None))
        self.label_17.setText(QCoreApplication.translate("Form", u"-90", None))
        self.label_18.setText(QCoreApplication.translate("Form", u"90", None))
        self.Slider_num1.setText(QCoreApplication.translate("Form", u" 0", None))
        self.Slider_num2.setText(QCoreApplication.translate("Form", u" 0", None))
        self.Slider_num3.setText(QCoreApplication.translate("Form", u" 0", None))
        self.Slider_num4.setText(QCoreApplication.translate("Form", u" 0", None))
    # retranslateUi

