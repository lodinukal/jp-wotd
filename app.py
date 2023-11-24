import sys
import os
import typing
from PyQt5 import QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QPoint

import configparser
from pyquery import PyQuery as pq
import requests

from datetime import datetime

headers = {
    "User-Agent": "My User Agent 1.0",
    "Referer": "https://www.google.com/",
    "Accept": "text/html",
    "Accept-Language": "en-US",
    "Accept-Encoding": "gzip",
}

selectors = {
    "japanese_wtd_selector": 'div[class="r101-wotd-widget__section--first"] > div[class="r101-wotd-widget__word-row"] > div[class="r101-wotd-widget__word"]',
    "japanese_wtd_kana_selector": 'div[class="r101-wotd-widget__additional-row"] > div[class="r101-wotd-widget__additional-field kana"]',
    "japanese_wtd_romaji_selector": 'div[class="r101-wotd-widget__additional-row"] > div[class="r101-wotd-widget__additional-field romaji"]',
    "japanese_wtd_english_selector": 'div[class="r101-wotd-widget__section--first"] > div[class="r101-wotd-widget__english"]',
    "japanese_wtd_audio_selector": 'div[class="r101-wotd-widget__audio r101-audio-player--a js-audio-player"]',
    "japanese_wtd_class_selector": 'div[class="r101-wotd-widget__class"]',
    "japanese_wtd_example_selector": 'div[class="r101-wotd-widget__section"] > div',
    "japanese_wtd_example_kana_selector": 'div[class="r101-wotd-widget__section"] > div[class="r101-wotd-widget__additional-field kana"]',
    "japanese_wtd_example_romaji_selector": 'div[class="r101-wotd-widget__section"] > div[class="r101-wotd-widget__additional-field romaji"]',
    "japanese_wtd_example_english_selector": 'div[class="r101-wotd-widget__section"] > div[class="r101-wotd-widget__english"]',
    "japanese_wtd_example_audio_selector": 'div[class="r101-wotd-widget__section"] > div[class="r101-wotd-widget__word-row"] > div[class="r101-wotd-widget__audio r101-audio-player--a js-audio-player"]',
    "japanese_wtd_date": 'button[class="r101-wotd-widget__date-picker js-wotd-widget-picker"]',
}


def getWordOfTheDay(timestamp: None | float) -> dict:
    url = "https://www.japanesepod101.com/japanese-phrases/"
    if timestamp:
        # convert from timestamp to date mmddyyyy
        dt = datetime.fromtimestamp(timestamp)
        url += dt.strftime("%m%d%Y")
        print(url)

    try:
        r = requests.get(url, headers=headers)
        html = r.text
        d = pq(html)
        word = d(selectors["japanese_wtd_selector"]).text()
        kana = d(selectors["japanese_wtd_kana_selector"]).text()
        romaji = d(selectors["japanese_wtd_romaji_selector"]).text()
        english = d(selectors["japanese_wtd_english_selector"]).text()
        audio = d(selectors["japanese_wtd_audio_selector"]).attr("data-audio")

        return {
            "word": word,
            "kana": kana,
            "romaji": romaji,
            "english": english,
            "audio": audio,
        }
    except Exception as e:
        print(e)

    # doesnt normally run here, as the site returns its own information
    return {
        "word": "none",
        "kana": "none",
        "romaji": "none",
        "english": "none",
        "audio": "none",
    }


class VerticalLayout:
    ycount = 0

    def addWidget(self, widget: QWidget, stretch: int = 0):
        widget.move(0, self.ycount)
        widget.setAlignment(Qt.AlignCenter)
        self.ycount += widget.height() + stretch


class Config:
    size = (300, 250)
    font = "Noto Sans JP"
    main_text_colour = "250, 250, 250, 240"
    second_text_colour = "190, 190, 190, 240"
    lock_colour = "20, 20, 20, 100"
    unlock_colour = "50, 50, 50, 100"

    position = (1584, 50)

    def default():
        return Config(
            Config.size,
            Config.font,
            Config.main_text_colour,
            Config.second_text_colour,
            Config.lock_colour,
            Config.unlock_colour,
            Config.position,
        )

    def __init__(self, size, font, mtc, stc, lc, uc, pos):
        self.size = size
        self.font = font
        self.main_text_colour = mtc
        self.second_text_colour = stc
        self.lock_colour = lc
        self.unlock_colour = uc
        self.position = pos

    def exists(file: str):
        return os.path.isfile(file)

    def loadFromFile(file: str):
        if not os.path.isfile(file):
            Config.default().saveToFile(file)
            return Config.default()
        config = configparser.ConfigParser()
        config.read(file)

        size = tuple(map(int, config["DEFAULT"]["size"].split(",")))
        font = config["DEFAULT"]["font"]
        mtc = config["DEFAULT"]["main_text_colour"]
        stc = config["DEFAULT"]["second_text_colour"]
        lc = config["DEFAULT"]["lock_colour"]
        uc = config["DEFAULT"]["unlock_colour"]
        pos = (None, None)
        if config["DEFAULT"]["position"] != "None,None":
            pos = tuple(map(int, config["DEFAULT"]["position"].split(",")))

        return Config(size, font, mtc, stc, lc, uc, pos)

    def saveToFile(self, file: str):
        config = configparser.ConfigParser()
        config["DEFAULT"] = {
            "size": f"{self.size[0]},{self.size[1]}",
            "font": self.font,
            "main_text_colour": self.main_text_colour,
            "second_text_colour": self.second_text_colour,
            "lock_colour": self.lock_colour,
            "unlock_colour": self.unlock_colour,
            "position": f"{self.position[0]},{self.position[1]}",
        }

        with open(file, "w") as configfile:
            config.write(configfile)


class MyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.loadedonce = False
        self.load()

    def load(self):
        first_load = not self.loadedonce
        self.locked = True
        self.config = Config.loadFromFile("config.ini")

        self.setWindowTitle("Japanese Word Of The Day")
        if self.config.position[0] != None:
            self.move(self.config.position[0], self.config.position[1])
        self.setFixedSize(self.config.size[0], self.config.size[1])
        self.setStyleSheet("QMainWindow{border: 1px solid #1b1c1f}")
        self.setWindowFlags(Qt.WindowStaysOnBottomHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setWindowFlag(Qt.Tool)

        self.background = QFrame(self) if first_load else self.background
        self.background.setFixedSize(self.config.size[0], self.config.size[1])

        self.fnt = (
            QtGui.QFont(self.config.font, 30, QtGui.QFont.Bold)
            if first_load
            else self.fnt
        )
        self.fntlight = (
            QtGui.QFont(self.config.font, 15, QtGui.QFont.Normal)
            if first_load
            else self.fntlight
        )
        self.fntlight.setStyleStrategy(QtGui.QFont.PreferQuality)

        vl = VerticalLayout()

        self.title = QLabel(self.background) if first_load else self.title
        self.title.setText("今日の単語")
        self.title.setFont(self.fntlight)
        self.title.setFixedSize(self.config.size[0], 30)

        vl.addWidget(self.title, 5)

        self.word = QLabel(self.background) if first_load else self.word
        self.word.setText("座席")
        self.word.setFont(self.fnt)
        self.word.setFixedSize(self.config.size[0], 50)

        vl.addWidget(self.word, 0)

        self.kana = QLabel(self.background) if first_load else self.kana
        self.kana.setText("ざせき")
        self.kana.setFont(self.fntlight)
        self.kana.setFixedSize(self.config.size[0], 30)

        vl.addWidget(self.kana, 0)

        self.romaji = QLabel(self.background) if first_load else self.romaji
        self.romaji.setText("zaseki")
        self.romaji.setFont(self.fntlight)
        self.romaji.setFixedSize(self.config.size[0], 30)

        vl.addWidget(self.romaji, 0)

        self.english = QLabel(self.background) if first_load else self.english
        self.english.setText("seat")
        self.english.setFont(self.fntlight)
        self.english.setFixedSize(self.config.size[0], 30)

        vl.addWidget(self.english, 5)

        self.computeStyles()
        self.loadedonce = True
        self.setText()

    def setText(self):
        wotd = getWordOfTheDay(datetime.now().timestamp())
        self.word.setText(wotd["word"])
        self.kana.setText(wotd["kana"])
        self.romaji.setText(wotd["romaji"])
        self.english.setText(wotd["english"])

    def reload(self):
        config = Config.loadFromFile("config.ini")
        self.setFixedSize(config.size[0], config.size[1])
        self.background.setFixedSize(config.size[0], config.size[1])
        if config.position[0] != None:
            self.move(config.position[0], config.position[1])

        self.fnt = QtGui.QFont(config.font, 30, QtGui.QFont.Bold)
        self.fntlight = QtGui.QFont(config.font, 15, QtGui.QFont.Normal)
        self.fntlight.setStyleStrategy(QtGui.QFont.PreferQuality)

        self.title.setFont(self.fntlight)
        self.title.setFixedSize(config.size[0], 30)
        self.word.setFont(self.fnt)
        self.word.setFixedSize(config.size[0], 50)
        self.kana.setFont(self.fntlight)
        self.kana.setFixedSize(config.size[0], 30)
        self.romaji.setFont(self.fntlight)
        self.romaji.setFixedSize(config.size[0], 30)
        self.english.setFont(self.fntlight)
        self.english.setFixedSize(config.size[0], 30)

        self.config.size = config.size
        self.config.font = config.font
        self.config.main_text_colour = config.main_text_colour
        self.config.second_text_colour = config.second_text_colour
        self.config.lock_colour = config.lock_colour
        self.config.unlock_colour = config.unlock_colour
        self.config.position = config.position

        self.computeStyles()
        self.setText()

    def mousePressEvent(self, event):
        if self.locked:
            return
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        if self.locked:
            return
        delta = QPoint(event.globalPos() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()

    def keyPressEvent(self, a0: QtGui.QKeyEvent | None) -> None:
        if a0:
            if a0.key() == Qt.Key_Escape:
                self.app.quit()
            if a0.key() == Qt.Key_L and a0.modifiers() == Qt.ControlModifier:
                self.setlock(not self.locked)
            if a0.key() == Qt.Key_R and a0.modifiers() == Qt.ControlModifier:
                self.reload()

    def moveEvent(self, a0: QtGui.QMoveEvent | None) -> None:
        self.config.position = (self.x(), self.y())

    def setlock(self, lock: bool):
        self.locked = lock
        self.computeStyles()

    def computeStyles(self):
        style = ""
        if self.locked:
            style += f"background-color: rgba({self.config.lock_colour});"
        else:
            style += f"background-color: rgba({self.config.unlock_colour});"
        self.background.setStyleSheet(style)

        style = ""
        style += f"color: rgba({self.config.main_text_colour});"
        style += f"background-color: transparent;"
        self.word.setStyleSheet(style)

        style = ""
        style += f"color: rgba({self.config.second_text_colour});"
        style += f"background-color: transparent;"
        self.title.setStyleSheet(style)
        self.kana.setStyleSheet(style)
        self.romaji.setStyleSheet(style)
        self.english.setStyleSheet(style)


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
    multiprocessing.freeze_support()
    resultQueue = multiprocessing.Queue()
    SendeventProcess(resultQueue)
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    window = MyApp()
    window.app = app
    window.show()

    icon = QtGui.QIcon("icon.png")

    tray = QSystemTrayIcon()
    tray.setIcon(icon)
    tray.setVisible(True)

    menu = QMenu()
    action = QAction("Exit")
    action.triggered.connect(app.quit)
    menu.addAction(action)

    tray.setContextMenu(menu)

    rc = app.exec_()

    window.config.saveToFile("config.ini")

    sys.exit(rc)
