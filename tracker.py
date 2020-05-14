from controller import TrackerCtrl
from tracker_windows import MyWindow
from PyQt5 import QtWidgets


def main():
    app = QtWidgets.QApplication([])
    window = MyWindow()
    def createTracker():
        return TrackerCtrl(view=window)
    btnPerson = window.btnSort
    btnPerson.clicked.connect(createTracker)
    if window.projectName:
        crtl = TrackerCtrl(view=window)

    return app.exec()


main()

