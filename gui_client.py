from PyQt5.QtCore import QDateTime, Qt, QTimer, QRect, QRectF, QPoint, QPropertyAnimation, pyqtProperty, QObject, QUrl
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget, QTableWidgetItem)
from PyQt5.QtGui import QFont, QPainter, QPainterPath, QPixmap, QPen, QColor, QBrush, QPalette
from PyQt5.QtMultimedia import QSound, QMediaContent, QMediaPlayer

# local imports from shell client
from shell_client import alarm_state, monitor_states, set_alarm, latests


class Room(QWidget):
    def __init__(self):
        super().__init__()
        self.closedLeft = True
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

        self.update = False
        # self.alarmSound = QSound("alarmSound.mp3")

        self.originalPalette = QApplication.palette()
        self.setFixedSize(900, 600)

        titleLabel = QLabel("IoT Security System")
        titleLabel.setFont(QFont("Arial", 16))  # , QFont.Bold

        self.createTopLeftRoom()
        self.createTopRightGroupBox()
        self.createBottomLeftTabWidget()
        self.createBottomRightTabWidget()
        self.createProgressBar()

        topLayout = QHBoxLayout()
        topLayout.addWidget(titleLabel)
        topLayout.addStretch(1)

        mainLayout = QGridLayout()
        mainLayout.addLayout(topLayout, 0, 0, 1, 2)
        mainLayout.addWidget(self.topLeftRoom, 1, 0)
        mainLayout.addWidget(self.topRightGroupBox, 1, 1)
        mainLayout.addWidget(self.bottomLeftTabWidget, 2, 0)
        mainLayout.addWidget(self.bottomRightTabWidget, 2, 1)
        mainLayout.addWidget(self.progressBar, 3, 0, 1, 2)
        mainLayout.setRowStretch(1, 1)
        mainLayout.setRowStretch(2, 1)
        mainLayout.setColumnStretch(0, 1)
        mainLayout.setColumnStretch(1, 1)
        self.setLayout(mainLayout)

        self.setWindowTitle("IoT Sec Sys")
        QApplication.setStyle(QStyleFactory.create('Fusion'))

        self.updateNow()

    def updateUI(self):
        curVal = self.progressBar.value()
        maxVal = self.progressBar.maximum()
        self.progressBar.setValue(curVal + 1)

        if curVal >= 1000 or self.update:
            self.progressBar.setValue(0)
            self.update = False
            # this code is hardcoded to the two monitor example
            # as the GUI needs it hardcoded for drawing anyway
            failures = monitor_states()
            print("Failures: " + str(failures))
            alarm = alarm_state()
            print("Alarm on: " + str(alarm))

            m1_occurrences = 0
            m2_occurrences = 0
            for (monitor, source) in failures:
                if monitor == '1':
                    m1_occurrences += 1
                    self.topLeftRoom.closedLeft = False
                if monitor == '2':
                    m2_occurrences += 1
                    self.topLeftRoom.closedRight = False
            if m1_occurrences == 0:
                self.topLeftRoom.closedLeft = True
            if m2_occurrences == 0:
                self.topLeftRoom.closedRight = True

            if (m1_occurrences or m2_occurrences) and alarm:
                # play sound and blinking text
                self.topRightGroupBox.findChildren(QLabel)[0].setText("Breach detected!")
                self.topRightGroupBox.findChildren(QLabel)[0].setStyleSheet('color: red')
                # self.alarmSound.play()
            elif (m1_occurrences or m2_occurrences) and not alarm:
                self.topRightGroupBox.findChildren(QLabel)[0].setText("Entry detected!")
                self.topRightGroupBox.findChildren(QLabel)[0].setStyleSheet('color: orange')
            else:
                self.topRightGroupBox.findChildren(QLabel)[0].setText("All good.")
                self.topRightGroupBox.findChildren(QLabel)[0].setStyleSheet('color: green')

            if not alarm:
                self.topRightGroupBox.findChildren(QCheckBox)[0].setChecked(True)
            else:
                self.topRightGroupBox.findChildren(QCheckBox)[0].setChecked(False)

            table1 = self.bottomLeftTabWidget.currentWidget().findChildren(QTableWidget)[0]
            row = 0
            for result in latests('1'):
                table1.setItem(row, 0, QTableWidgetItem(result[0]))
                table1.setItem(row, 1, QTableWidgetItem(result[1]))
                table1.setItem(row, 2, QTableWidgetItem(str(result[2])))
                table1.setItem(row, 3, QTableWidgetItem(str(result[3])))
                row += 1

            table2 = self.bottomRightTabWidget.currentWidget().findChildren(QTableWidget)[0]
            row = 0
            for result in latests('2'):
                table2.setItem(row, 0, QTableWidgetItem(result[0]))
                table2.setItem(row, 1, QTableWidgetItem(result[1]))
                table2.setItem(row, 2, QTableWidgetItem(str(result[2])))
                table2.setItem(row, 3, QTableWidgetItem(str(result[3])))
                row += 1

            # needs to call update to draw lines
            self.topLeftRoom.update()

    def updateNow(self):
        self.update = True
        self.updateUI()

    def toggleAlarmFunction(self):
        if self.topRightGroupBox.findChildren(QCheckBox)[0].isChecked():
            set_alarm(False)
        else:
            set_alarm(True)
        self.updateNow()

    def createTopLeftRoom(self):
        self.topLeftRoom = Room()
        # self.topLeftRoom.closedRight = False

    def createTopRightGroupBox(self):
        self.topRightGroupBox = QGroupBox("Controls")

        defaultPushButton = QPushButton("Update now")
        defaultPushButton.setDefault(True)
        defaultPushButton.clicked.connect(self.updateNow)

        disableAlarmCheckBox = QCheckBox("&Disable alarm")
        if not alarm_state():
            disableAlarmCheckBox.setChecked(True)
        disableAlarmCheckBox.clicked.connect(self.toggleAlarmFunction)

        disableSoundCheckBox = QCheckBox("&Disable sound")
        # disableSoundCheckBox.clicked.connect(self.toggleSoundFunction)

        warningLabel = QLabel()
        newfont = QFont("Arial", 32)  # , QFont.Bold
        warningLabel.setFont(newfont)

        layout = QVBoxLayout()
        layout.addWidget(disableAlarmCheckBox)
        layout.addWidget(disableSoundCheckBox)
        layout.addWidget(defaultPushButton)
        layout.addWidget(warningLabel)
        layout.addStretch(1)
        self.topRightGroupBox.setLayout(layout)

    def createBottomLeftTabWidget(self):
        self.bottomLeftTabWidget = QTabWidget()
        self.bottomLeftTabWidget.setSizePolicy(QSizePolicy.Preferred,
                QSizePolicy.Ignored)

        tab1 = QWidget()
        tableWidget = QTableWidget(10, 4)
        tableWidget.setEditTriggers(QTableWidget.NoEditTriggers)
        tab1hbox = QHBoxLayout()
        tab1hbox.setContentsMargins(5, 5, 5, 5)
        tab1hbox.addWidget(tableWidget)
        tab1.setLayout(tab1hbox)

        self.bottomLeftTabWidget.addTab(tab1, "Monitor &1")

    def createBottomRightTabWidget(self):
        self.bottomRightTabWidget = QTabWidget()
        self.bottomRightTabWidget.setSizePolicy(QSizePolicy.Preferred,
                QSizePolicy.Ignored)

        tab2 = QWidget()
        tableWidget = QTableWidget(10, 4)
        tableWidget.setEditTriggers(QTableWidget.NoEditTriggers)
        tab2hbox = QHBoxLayout()
        tab2hbox.setContentsMargins(5, 5, 5, 5)
        tab2hbox.addWidget(tableWidget)
        tab2.setLayout(tab2hbox)

        self.bottomRightTabWidget.addTab(tab2, "Monitor &2")

    def createProgressBar(self):
        self.progressBar = QProgressBar()
        self.progressBar.setRange(0, 1000)
        self.progressBar.setValue(0)

        timer = QTimer(self)
        timer.timeout.connect(self.updateUI)
        timer.start(10)


if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)
    gallery = WidgetGallery()
    gallery.show()
    sys.exit(app.exec_())
