# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'button.ui'
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
from PySide6.QtWidgets import (QApplication, QPushButton, QSizePolicy, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(496, 385)
        self.Button_A = QPushButton(Form)
        self.Button_A.setObjectName(u"Button_A")
        self.Button_A.setGeometry(QRect(80, 110, 131, 101))
        self.Button_B = QPushButton(Form)
        self.Button_B.setObjectName(u"Button_B")
        self.Button_B.setGeometry(QRect(280, 110, 131, 101))

        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.Button_A.setText(QCoreApplication.translate("Form", u"ButtonA", None))
        self.Button_B.setText(QCoreApplication.translate("Form", u"ButtonB", None))
    # retranslateUi

