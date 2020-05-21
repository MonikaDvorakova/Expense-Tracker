from controller import TrackerCtrl
from tracker_windows import MyWindow
from PyQt5 import QtWidgets


def main():
    app = QtWidgets.QApplication([])
    window = MyWindow()
    if window.projectName:
        crtl = TrackerCtrl(view=window)

    return app.exec()


main()
