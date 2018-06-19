import sys
import os

from PIL import Image
from PIL import ImageQt

from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import pyqtSlot, QObject, Qt
from PyQt5.QtGui import QIcon, QFontDatabase
from PyQt5.QtWidgets import QWidget, QApplication, QDesktopWidget, QStyleFactory
from PyQt5.QtWidgets import QLabel, QPushButton, QVBoxLayout, QHBoxLayout

from QtImageViewer import QtImageViewer # pylint: disable=E0401

from hqbot import answerbot_v2 as answerbot
from hqbot import question

class HQGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.min_width = 750

        self.init_ui()

    def init_ui(self):
        width = 1000
        height = 850

        w_percent = (self.min_width / float(width))
        h_size = int((float(height) * float(w_percent)))

        self.resize(width, height)
        self.setMinimumSize(self.min_width, h_size)
        self.center()

        self.setWindowTitle('HQ Trivia Bot')
        self.setWindowIcon(QIcon(os.path.join(self.base_path, "Data", "robot.png")))

        hbox = QHBoxLayout()
        vbox = QVBoxLayout()

        self.viewer = QtImageViewer()
        self.viewer.aspectRatioMode = QtCore.Qt.KeepAspectRatio
        self.viewer.canZoom = False
        self.viewer.canPan = False

        question_label = QLabel()
        question_label.setObjectName('questionLabel')
        question_label.setText('Question:')
        question_label.setAlignment(Qt.AlignCenter)

        self.question_holder = QLabel()
        self.question_holder.setObjectName('questionHolder')
        self.question_holder.setText('Lorem Ipsum?')
        self.question_holder.setAlignment(Qt.AlignCenter)

        choices_label = QLabel()
        choices_label.setObjectName('choicesLabel')
        choices_label.setText('Choices:')
        choices_label.setAlignment(Qt.AlignCenter)

        # Choices
        self.choice_one = QLabel()
        self.choice_one.setText("1.")
        self.choice_one.setAlignment(Qt.AlignCenter)

        self.choice_two = QLabel()
        self.choice_two.setText("2.")
        self.choice_two.setAlignment(Qt.AlignCenter)

        self.choice_three = QLabel()
        self.choice_three.setText("3.")
        self.choice_three.setAlignment(Qt.AlignCenter)

        # Buttons
        screenshot_btn = QPushButton('Screenshot', self)
        screenshot_btn.setObjectName('screenshotBtn')
        screenshot_btn.clicked.connect(self.screenshot_click)

        quit_btn = QPushButton('Quit', self)
        quit_btn.setObjectName('quitBtn')
        quit_btn.clicked.connect(self.close)

        # Image Viewer
        vbox.addWidget(self.viewer)

        # Question Label
        vbox.addWidget(question_label)

        # Question Holder
        vbox.addWidget(self.question_holder)
        vbox.addSpacing(50)

        # Choice Label
        vbox.addWidget(choices_label)

        # Choices
        vbox.addWidget(self.choice_one)
        vbox.addWidget(self.choice_two)
        vbox.addWidget(self.choice_three)
        vbox.addSpacing(10)

        # Buttons
        hbox.addWidget(screenshot_btn)
        hbox.addWidget(quit_btn)
        vbox.addLayout(hbox)

        self.setLayout(vbox)
        self.show()

    def center(self):
        # geometry of the main window
        qr = self.frameGeometry()

        # center point of screen
        cp = QDesktopWidget().availableGeometry().center()

        # move rectangle's center point to screen's center point
        qr.moveCenter(cp)

        # top left of rectangle becomes top left of window centering it
        self.move(qr.topLeft())

    def question_text(self, text):
        self.question_holder.setText(text)

    def choice_text(self, choices):
        if len(choices) != 3:
            return
        self.choice_one.setText(choices[0])
        self.choice_two.setText(choices[1])
        self.choice_three.setText(choices[2])

    def highlight_choice(self, correct):
        pass

    @pyqtSlot()
    def screenshot_click(self):
        # #20BF55 Green Color
        # #ED1C24 Red Color
        print("Running")
        image = answerbot.grab_screen()
        image = answerbot.preprocess_img(image)

        self.viewer.setImage(
            QtGui.QPixmap.fromImage(ImageQt.ImageQt(image))
        )
        self.viewer.show()

        text = answerbot.get_text()
        ques, options = question.parse(text)

        if '?' in ques:
            self.question_text(ques)
            self.choice_text(options)
        else:
            self.question_text("No question was found. Try running again.")


def get_palette():
    palette = QtGui.QPalette()
    palette.setColor(QtGui.QPalette.Window, QtGui.QColor(239, 239, 239))
    palette.setColor(QtGui.QPalette.WindowText, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.Base, QtGui.QColor(15, 15, 15))
    palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(53, 53, 53))
    palette.setColor(QtGui.QPalette.ToolTipBase, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.ToolTipText, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.Text, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.Button, QtGui.QColor(8, 178, 227))
    palette.setColor(QtGui.QPalette.ButtonText, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.BrightText, QtCore.Qt.red)

    palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(142, 45, 197).lighter())
    palette.setColor(QtGui.QPalette.HighlightedText, QtCore.Qt.black)
    return palette


if __name__ == "__main__":
    base_path = os.path.dirname(os.path.abspath(__file__))
    style_path = os.path.join(base_path, 'content', 'stylesheets')
    fonts_path = os.path.join(base_path, 'content', 'fonts')

    app = QApplication(sys.argv)

    database = QFontDatabase()
    database.addApplicationFont(os.path.join(fonts_path, 'Cornerstone.ttf'))
    database.addApplicationFont(os.path.join(fonts_path, 'Roboto-Light.ttf'))
    database.addApplicationFont(os.path.join(fonts_path, 'Roboto-Medium.ttf'))

    with open(os.path.join(style_path, 'app.qss')) as stylesheet:
        app.setStyleSheet(stylesheet.read())
        stylesheet.close()

    app.setStyle(QStyleFactory().create("Fusion"))
    app.setPalette(get_palette())

    gui = HQGUI()
    sys.exit(app.exec_())
