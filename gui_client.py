from PyQt5.QtCore import QDateTime, Qt, QTimer, QRect, QRectF, QPoint
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget)
from PyQt5.QtGui import QFont, QPainter, QPainterPath, QPixmap, QPen, QColor, QBrush


class Room(QWidget):
    def __init__(self):
        super().__init__()
        self.closedLeft = False
        self.closedRight = True

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        if self.closedLeft:
            self.drawClosedLeft(event, qp)
        else:
            self.drawOpenLeft(event, qp)
        if self.closedRight:
            self.drawClosedRight(event, qp)
        else:
            self.drawOpenRight(event, qp)
        self.drawRoom(event, qp)
        qp.end()

    def drawClosedLeft(self, event, qp):
        pen = QPen()
        pen.setWidth(3)
        pen.setColor(QColor(128, 250, 25, 255))
        pen.setStyle(Qt.DotLine)
        qp.setPen(pen)

        qp.drawLine(QPoint(30, 80), QPoint(100, 80))

    def drawClosedRight(self, event, qp):
        pen = QPen()
        pen.setWidth(3)
        pen.setColor(QColor(128, 250, 25, 255))
        pen.setStyle(Qt.DotLine)
        qp.setPen(pen)

        qp.drawLine(QPoint(280, 80), QPoint(350, 80))

    def drawOpenLeft(self, event, qp):
        pen = QPen()
        pen.setWidth(3)
        pen.setColor(QColor(250, 128, 25, 255))
        pen.setStyle(Qt.DotLine)
        qp.setPen(pen)

        qp.drawLine(QPoint(30, 80), QPoint(80, 50))

    def drawOpenRight(self, event, qp):
        pen = QPen()
        pen.setWidth(3)
        pen.setColor(QColor(250, 128, 25, 255))
        pen.setStyle(Qt.DotLine)
        qp.setPen(pen)

        qp.drawLine(QPoint(300, 50), QPoint(350, 80))

    def drawRoom(self, event, qp):
        pen = QPen()
        pen.setWidth(3)

        pen.setColor(QColor(0, 0, 0, 255))
        pen.setStyle(Qt.SolidLine)
        qp.setPen(pen)

        qp.drawLine(QPoint(30, 30), QPoint(30, 220))
        qp.drawLine(QPoint(30, 220), QPoint(350, 220))
        qp.drawLine(QPoint(350, 30), QPoint(350, 220))

        qp.drawLine(QPoint(100, 80), QPoint(100, 30))
        qp.drawLine(QPoint(100, 30), QPoint(280, 30))
        qp.drawLine(QPoint(280, 80), QPoint(280, 30))


class WidgetGallery(QDialog):
    def __init__(self, parent=None):
        super(WidgetGallery, self).__init__(parent)

        self.originalPalette = QApplication.palette()
        self.setFixedSize(800, 600)

        titleLabel = QLabel("IoT Security System")
        titleLabel.setFont(QFont("Arial", 16))  # , QFont.Bold

        disableAlarmCheckBox = QCheckBox("&Disable alarm")
        disableSoundCheckBox = QCheckBox("&Disable sound")

        self.createTopLeftRoom()
        self.createTopRightGroupBox()
        self.createBottomLeftTabWidget()
        self.createProgressBar()

        topLayout = QHBoxLayout()
        topLayout.addWidget(titleLabel)
        topLayout.addStretch(1)
        topLayout.addWidget(disableAlarmCheckBox)
        topLayout.addWidget(disableSoundCheckBox)

        mainLayout = QGridLayout()
        mainLayout.addLayout(topLayout, 0, 0, 1, 2)
        mainLayout.addWidget(self.topLeftRoom, 1, 0)
        mainLayout.addWidget(self.topRightGroupBox, 1, 1)
        mainLayout.addWidget(self.bottomLeftTabWidget, 2, 0, 1, 2)
        mainLayout.addWidget(self.progressBar, 3, 0, 1, 2)
        mainLayout.setRowStretch(1, 1)
        mainLayout.setRowStretch(2, 1)
        mainLayout.setColumnStretch(0, 1)
        mainLayout.setColumnStretch(1, 1)
        self.setLayout(mainLayout)

        self.setWindowTitle("IoT Sec Sys")
        QApplication.setStyle(QStyleFactory.create('Fusion'))

    def updateUI(self):
        curVal = self.progressBar.value()
        maxVal = self.progressBar.maximum()
        self.progressBar.setValue(curVal + (maxVal - curVal) / 100)
        if curVal > 200:
            self.topLeftRoom.closedLeft = True
            self.topLeftRoom.update()

    def createTopLeftRoom(self):
        self.topLeftRoom = Room()
        # self.topLeftRoom.closedRight = False

    def createTopRightGroupBox(self):
        self.topRightGroupBox = QGroupBox("Controls")

        defaultPushButton = QPushButton("Update Data")
        defaultPushButton.setDefault(True)
        defaultPushButton.clicked.connect(self.updateUI)

        layout = QVBoxLayout()
        layout.addWidget(defaultPushButton)
        layout.addStretch(1)
        self.topRightGroupBox.setLayout(layout)

    def createBottomLeftTabWidget(self):
        self.bottomLeftTabWidget = QTabWidget()
        self.bottomLeftTabWidget.setSizePolicy(QSizePolicy.Preferred,
                QSizePolicy.Ignored)

        tab1 = QWidget()
        tableWidget = QTableWidget(10, 10)
        tableWidget.setEditTriggers(QTableWidget.NoEditTriggers)
        tab1hbox = QHBoxLayout()
        tab1hbox.setContentsMargins(5, 5, 5, 5)
        tab1hbox.addWidget(tableWidget)
        tab1.setLayout(tab1hbox)

        tab2 = QWidget()
        tableWidget = QTableWidget(10, 10)
        tableWidget.setEditTriggers(QTableWidget.NoEditTriggers)
        tab2hbox = QHBoxLayout()
        tab2hbox.setContentsMargins(5, 5, 5, 5)
        tab2hbox.addWidget(tableWidget)
        tab2.setLayout(tab2hbox)

        self.bottomLeftTabWidget.addTab(tab1, "Monitor &1")
        self.bottomLeftTabWidget.addTab(tab2, "Monitor &2")

    def createProgressBar(self):
        self.progressBar = QProgressBar()
        self.progressBar.setRange(0, 10000)
        self.progressBar.setValue(0)

        timer = QTimer(self)
        timer.timeout.connect(self.updateUI)
        timer.start(1000)


if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)
    gallery = WidgetGallery()
    gallery.show()
    sys.exit(app.exec_())
