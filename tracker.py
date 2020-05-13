from controller import TrackerCtrl
from tracker_windows import MyWindow

#from PyQt5 import uic, QtGui
from PyQt5 import QtWidgets, QtCore
#from PyQt5.QtCore import Qt
#from functools import partial
#import sqlite3
#from sqlite3 import Error
#from datetime import date, timedelta, datetime
#import matplotlib.pyplot as plt
#from  matplotlib.backends.backend_qt5agg  import  FigureCanvas

#from  matplotlib.backends.backend_qt5agg  import  (NavigationToolbar2QT  as  NavigationToolbar)

#from  matplotlib.figure  import  Figure

#import  numpy  as  np 
#import  random
#import glob, os
#import pandas



ERROR_MSG = 'ERROR'



        
    # Zkusit dat vytvoreni ctrl do initialwindow, pak by se vytvoril ctrl pro kazde nove okno. V miste, kde davam hodnotu projectName.
    # potom by se automaticky vytvoril ctrl pro kazde otevrene okno. 


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

