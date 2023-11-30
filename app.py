import sys
import os
import typing
from PyQt6 import QtGui
from PyQt6.QtGui import QCursor
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt, QPointF, QPoint

import webbrowser

import yaml

import random

import csv
from datetime import datetime

words = []  # 0
kana = []  # 1
romaji = []  # 3
english = []  # 3
audio = []  # 14

day = round(datetime.now().timestamp() / 86400) * 4
print(day)


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    # try:
    #     # PyInstaller creates a temp folder and stores path in _MEIPASS
    #     base_path = sys._MEIPASS + "/resources"
    # except Exception:
    #     base_path = os.path.abspath(".")

    # return os.path.join(base_path, relative_path)
    # broken atm, fix later
    return relative_path


with open(resource_path("words.csv"), "r", encoding="utf-8") as f:
    reader = csv.reader(f, delimiter=",", quotechar='"')
    next(reader)
    for row in reader:
        words.append(row[0])
        kana.append(row[1])
        romaji.append(row[2])
        english.append(row[3])
        audio.append(row[14])


def getWordOfTheDay(window_index: int) -> dict:
    # get the word from the day
    available_words = len(words)
    random.seed(day + window_index)
    word_index = random.randrange(0, available_words - 1)

    return {
        "word": words[word_index],
        "kana": kana[word_index],
        "romaji": romaji[word_index],
        "english": english[word_index],
        "audio": audio[word_index],
    }


class VerticalLayout:
    ycount = 0

    def addWidget(self, widget: QLabel, stretch: int = 0):
        widget.move(0, self.ycount)
        widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.ycount += widget.height() + stretch


def getDefaultFrameConfig():
    r = random.Random()
    return {
        "size": [300, 250],
        "font": "Yu Mincho",
        "english_font": "Arial",
        "main_text_colour": "250, 250, 250, 240",
        "second_text_colour": "190, 190, 190, 240",
        "lock_colour": "20, 20, 20, 100",
        "unlock_colour": "50, 50, 50, 100",
        "position": [10, 50],
        "lookat": 0,
        "id": r.randrange(1, 1000000),
    }


def ensureFrameProperties(fcg: dict):
    copy = fcg.copy()
    default = getDefaultFrameConfig()
    for prop in default:
        if prop not in fcg:
            copy[prop] = default[prop]
    return copy


def inheritFrameConfig(fcg):
    new = getDefaultFrameConfig()
    inherit_properties = [
        "size",
        "font",
        "english_font",
        "main_text_colour",
        "second_text_colour",
        "lock_colour",
        "unlock_colour",
    ]
    for prop in inherit_properties:
        if prop in fcg:
            new[prop] = fcg[prop]
    return new


class Config:
    frames: typing.List[dict]

    def default():
        return Config([getDefaultFrameConfig()])

    def __init__(self, frames):
        self.frames = frames

    def exists(file: str):
        return os.path.isfile(file)

    def loadFromFile(file: str):
        if not os.path.isfile(file):
            Config.default().saveToFile(file)
        l = []
        with open(file, "r") as configfile:
            return Config.fromList(yaml.safe_load(configfile))

    def saveToFile(self, file: str):
        with open(file, "w") as configfile:
            yaml.dump(self.asList(), configfile)

    def asList(self):
        l = []
        for frame in self.frames:
            l.append(frame)
        return l

    def fromList(o):
        l = []
        for frame in o:
            l.append(ensureFrameProperties(frame))
        return Config(l)


class Frame(QWidget):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.load()

    def load(self):
        self.locked = True

        self.move(self.config["position"][0], self.config["position"][1])
        self.setFixedSize(self.config["size"][0], self.config["size"][1])
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnBottomHint
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.background = QFrame(self)
        self.background.setStyleSheet("background-color: rgba(0, 0, 0, 0);")
        self.background.setFixedSize(self.config["size"][0], self.config["size"][1])

        self.fnt = QtGui.QFont(self.config["font"], 30, 15)
        self.fnt.setStyleStrategy(QtGui.QFont.StyleStrategy.PreferQuality)
        self.fntlight = QtGui.QFont(self.config["font"], 15, 10)
        self.fntlight.setStyleStrategy(QtGui.QFont.StyleStrategy.PreferQuality)

        self.engfnt = QtGui.QFont(self.config["english_font"], 30, 15)
        self.engfnt.setStyleStrategy(QtGui.QFont.StyleStrategy.PreferQuality)
        self.engfntlight = QtGui.QFont(self.config["english_font"], 15, 10)
        self.engfntlight.setStyleStrategy(QtGui.QFont.StyleStrategy.PreferQuality)

        vl = VerticalLayout()

        self.progress = QProgressBar(self.background)
        self.progress.setFixedSize(self.config["size"][0], 3)
        self.progress.setValue(1)
        self.progress.setTextVisible(False)
        self.progress.setMaximum(4)
        self.progress.setVisible(False)

        vl.addWidget(self.progress, 5)

        self.ttl = QLabel(self.background)
        self.ttl.setText("今日の単語")
        self.ttl.setFont(self.fntlight)
        self.ttl.setFixedSize(self.config["size"][0], 30)

        vl.addWidget(self.ttl, 5)

        self.word = QLabel(self.background)
        self.word.setText("座席")
        self.word.setFont(self.fnt)
        self.word.setFixedSize(self.config["size"][0], 50)

        vl.addWidget(self.word, 0)

        self.kana = QLabel(self.background)
        self.kana.setText("ざせき")
        self.kana.setFont(self.fntlight)
        self.kana.setFixedSize(self.config["size"][0], 30)

        vl.addWidget(self.kana, 0)

        # self.romaji = QLabel(self.background)
        # self.romaji.setText("zaseki")
        # self.romaji.setFont(self.fntlight)
        # self.romaji.setFixedSize(self.config["size"][0], 30)

        # vl.addWidget(self.romaji, 0)

        self.english = QLabel(self.background)
        self.english.setText("seat")
        self.english.setFont(self.engfntlight)
        self.english.setFixedSize(self.config["size"][0], 30)

        vl.addWidget(self.english, 5)

        self.computeStyles()
        self.loadedonce = True
        self.updateText()

    def updateText(self):
        wotd = getWordOfTheDay(self.config["id"] + self.config["lookat"])
        self.word.setText(wotd["word"])
        self.kana.setText(wotd["kana"])
        # self.romaji.setText(wotd["romaji"])
        self.english.setText(wotd["english"])

    def reload(self, config):
        self.config = config

        self.move(self.config["position"][0], self.config["position"][1])
        self.setFixedSize(self.config["size"][0], self.config["size"][1])

        self.background.setFixedSize(self.config["size"][0], self.config["size"][1])

        self.fnt = QtGui.QFont(self.config["font"], 30, 15)
        self.fnt.setStyleStrategy(QtGui.QFont.StyleStrategy.PreferQuality)
        self.fntlight = QtGui.QFont(self.config["font"], 15, 10)
        self.fntlight.setStyleStrategy(QtGui.QFont.StyleStrategy.PreferQuality)

        self.engfnt = QtGui.QFont(self.config["english_font"], 30, 15)
        self.engfnt.setStyleStrategy(QtGui.QFont.StyleStrategy.PreferQuality)
        self.engfntlight = QtGui.QFont(self.config["english_font"], 15, 10)
        self.engfntlight.setStyleStrategy(QtGui.QFont.StyleStrategy.PreferQuality)

        self.ttl.setFont(self.fntlight)
        self.ttl.setFixedSize(config["size"][0], 30)
        self.word.setFont(self.fnt)
        self.word.setFixedSize(config["size"][0], 50)
        self.kana.setFont(self.fntlight)
        self.kana.setFixedSize(config["size"][0], 30)
        # self.romaji.setFont(self.fntlight)
        # self.romaji.setFixedSize(config["size"][0], 30)
        self.english.setFont(self.engfntlight)
        self.english.setFixedSize(config["size"][0], 30)

        self.computeStyles()
        self.updateText()

    def mousePressEvent(self, event):
        if self.locked:
            return
        self.oldPos = event.globalPosition()

    def mouseDoubleClickEvent(self, a0) -> None:
        webbrowser.open("https://jisho.org/search/" + self.word.text())

    def mouseMoveEvent(self, event):
        if self.locked:
            return
        delta = QPointF(event.globalPosition() - self.oldPos)
        self.move(int(self.x() + delta.x()), int(self.y() + delta.y()))
        self.oldPos = event.globalPosition()

    def keyPressEvent(self, a0: QtGui.QKeyEvent | None) -> None:
        if a0:
            if a0.key() == Qt.Key.Key_Escape:
                self.app.quit()
            if (
                a0.key() == Qt.Key.Key_L
                and a0.modifiers() == Qt.KeyboardModifier.ControlModifier
            ):
                self.setlock(not self.locked)
            if (
                a0.key() == Qt.Key.Key_R
                and a0.modifiers() == Qt.KeyboardModifier.ControlModifier
            ):
                self.app.reloadWindows()
            if (
                a0.key() == Qt.Key.Key_N
                and a0.modifiers() == Qt.KeyboardModifier.ControlModifier
            ):
                self.app.newWindow(self.config, QCursor.pos())
            if (
                a0.key() == Qt.Key.Key_W
                and a0.modifiers() == Qt.KeyboardModifier.ControlModifier
            ):
                self.app.deleteWindow(self.config["id"])
            if a0.key() == Qt.Key.Key_E:
                self.config["lookat"] = (self.config["lookat"] + 1) % 4
                self.progress.setValue(self.config["lookat"] + 1)
                self.updateText()
            if a0.key() == Qt.Key.Key_Q:
                self.config["lookat"] = (self.config["lookat"] - 1) % 4
                self.progress.setValue(self.config["lookat"] + 1)
                self.updateText()

    def moveEvent(self, a0: QtGui.QMoveEvent | None) -> None:
        self.config["position"] = [self.x(), self.y()]

    def setlock(self, lock: bool):
        self.locked = lock
        self.computeStyles()

    def computeStyles(self):
        style = ""
        if self.locked:
            style += f"background-color: rgba({self.config['lock_colour']});"
        else:
            style += f"background-color: rgba({self.config['unlock_colour']});"
        self.background.setStyleSheet(style)

        style = ""
        style += f"color: rgba({self.config['main_text_colour']});"
        style += f"background-color: transparent;"
        self.word.setStyleSheet(style)

        style = ""
        style += f"color: rgba({self.config['second_text_colour']});"
        style += f"background-color: transparent;"
        self.ttl.setStyleSheet(style)
        self.kana.setStyleSheet(style)
        # self.romaji.setStyleSheet(style)
        self.english.setStyleSheet(style)

        style = ""
        style += f"QProgressBar {{background-color: rgba(1, 1, 1, 255);}}"
        style += f"QProgressBar::chunk {{background-color: rgba({self.config['second_text_colour']});}}"
        self.progress.setStyleSheet(style)


import multiprocessing


class SendeventProcess(multiprocessing.Process):
    def __init__(self, resultQueue):
        self.resultQueue = resultQueue
        multiprocessing.Process.__init__(self)
        self.start()

    def run(self):
        self.resultQueue.put((1, 2))


if __name__ == "__main__":
    # On Windows calling this function is necessary.
    # On Linux/OSX it does nothing.
    # multiprocessing.freeze_support()
    # resultQueue = multiprocessing.Queue()
    # SendeventProcess(resultQueue)
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    config = Config.loadFromFile("config.yaml")
    app.config = config

    windows = []

    def newWindow(inherit: dict, qp: QPoint):
        fcg = inheritFrameConfig(inherit)
        fcg["position"] = [qp.x(), qp.y()]
        config.frames.append(fcg)
        window = Frame(fcg)
        window.app = app
        window.show()
        windows.append(window)

    def deleteWindow(id: int):
        for i in range(len(config.frames)):
            if config.frames[i].id == id:
                config.frames.pop(i)
                break
        for i in range(len(windows)):
            if windows[i].config["id"] == id:
                windows[i].close()
                windows.pop(i)
                break

    def reloadWindows():
        config = Config.loadFromFile("config.yaml")
        app.config = config
        for i in range(len(windows)):
            windows[i].reload(config.frames[i])

    app.newWindow = newWindow
    app.deleteWindow = deleteWindow
    app.reloadWindows = reloadWindows

    for frame in config.frames:
        window = Frame(frame)
        window.app = app
        window.show()
        windows.append(window)

    icon = QtGui.QIcon("icon.png")

    tray = QSystemTrayIcon()
    tray.setIcon(icon)
    tray.setVisible(True)

    menu = QMenu()
    action_exit = QWidgetAction(menu)
    action_exit.setText("Exit")
    action_exit.triggered.connect(app.quit)
    menu.addAction(action_exit)

    action_config = QWidgetAction(menu)
    action_config.setText("Config")
    action_config.triggered.connect(lambda: webbrowser.open("."))
    menu.addAction(action_config)

    tray.setContextMenu(menu)

    rc = app.exec()
    app.config.saveToFile("config.yaml")

    sys.exit(rc)

# print(yaml.safe_dump(Config.default().asObject()))
