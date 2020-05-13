from PyQt5 import uic, QtGui
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt

from datetime import date

import glob, os

from controller import TrackerCtrl

from  matplotlib.backends.backend_qt5agg  import  (NavigationToolbar2QT  as  NavigationToolbar)



class InitialWindow(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi("initial_dialog.ui",self)
        self.setWindowTitle("Initiate project")
        #self.open()
        #self.setModal(True)
        #self.show()

        btnOpen = self.btnOpenProject
        btnNew = self.btnNewProject
        btnOpen.clicked.connect(self.accept)
        btnNew.clicked.connect(self.reject)
        #self.findProjectsInFolder()
        self._model = ModelProjects()
        self.listView.setModel(self._model)
        self.selectedItem = self.listView.currentIndex()
        print(self.selectedItem.row())
    

        

    #def closeFunction(self):
        #self.accept()
        #print('zavri okno')
    
    #def findProjectsInFolder(self):
        #print(glob.glob('*.sqlite'))





class MyWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__()
        self.windowUi = 'view.ui'

        self.dialogUi = 'dialog.ui'
        self.dialogRemove = 'dialogRemoveAll.ui'
        self.dialogPerson = self.newDialog(self.dialogUi, 'New person')
        self.dialogCathegory = self.newDialog(self.dialogUi, 'New cathegory')
        self.dialogPersonRemove = self.newDialog(self.dialogUi, 'Remove person')
        self.dialogCathegoryRemove = self.newDialog(self.dialogUi, 'Remove cathegory')
        self.dialogRemoveAll = self.newDialog(self.dialogRemove, 'Remove all')

        self.projectName = None


        self.loadWindowUi()
        self.setWindowTitle('Expense Tracker') ##############################################
        self.show()

        self.dialogNewProject = QtWidgets.QDialog()
        uic.loadUi("dialog_NewProject.ui",self.dialogNewProject)

        self.initialDialog = InitialWindow()
        self.openInitialDialog(self.initialDialog, self.dialogNewProject) ############




        self.dateAdd.setCalendarPopup(True)
        self.dateAdd.setDate(date.today())
        self.dateFilterFrom.setCalendarPopup(True)
        self.dateFilterFrom.setDate(date.today()) 
        self.dateFilterTo.setCalendarPopup(True)
        self.dateFilterTo.setDate(date.today())

        self.graphicalOutput = MatplotlibWidget()

        
        
        #self.graphicalOutput.widget = MplWidget()

    def setTitle(self, projectName):
        if projectName:
            if projectName.endswith('.sqlite'):
                projectName = projectName[:-7]
            self.setWindowTitle('Expense Tracker - ' + projectName)
        else:
            self.setWindowTitle('Expense Tracker')

    def showMessageBox(self, text):
        msgBox = QtWidgets.QMessageBox()
        msgBox.setText(text)
        msgBox.exec()

    def newProjectCheckName(self, newProject):
        existingProjects = glob.glob('*.sqlite')
        for project in existingProjects:
            if newProject == os.path.splitext(project)[0]:
                return False
    
        return True

    def openNewProject(self):
        self.window = MyWindow()
        self.window.show()
        self.ctrl = TrackerCtrl(view=self.window)
        self.close()


    

    def openInitialDialog(self, dialog, dialogNewProject): #########################
        #dialog.setModal(True)
        print('spusten initial dialog')
        selectedItemIndex = self.initialDialog.listView.currentIndex().row()
        print(selectedItemIndex)
        while selectedItemIndex == -1:
            result = dialog.exec()
            if result == QtWidgets.QDialog.Rejected:
                resultNewProject = dialogNewProject.exec()
                if resultNewProject == QtWidgets.QDialog.Rejected:
                    self.dialogNewProject.lineEdit.clear()
                else:
                    inputText = self.dialogNewProject.lineEdit.text()
                    if self.newProjectCheckName(inputText):
                        self.projectName = inputText + '.sqlite'
                        self.setTitle(inputText)
                        self.initialDialog.listView.setCurrentIndex(QtCore.QModelIndex())
                        self.dialogNewProject.lineEdit.clear()
                        #self.initialDialog._model.layoutChanged.emit()
                        #self.initialDialog._model._data = self.initialDialog._model.findProjectsInFolder()
                        #self.initialDialog._model.layoutChanged.emit()
                        break
                    else:
                        self.dialogNewProject.lineEdit.clear()
                        self.showMessageBox("The project already exists.")
            else:
                #self.projectName = 'tracker.sqlite'
                selectedItemIndex = self.initialDialog.listView.currentIndex().row()
                if selectedItemIndex == -1:
                    self.showMessageBox("No project has been selected.")
                else:
                    self.projectName = self.initialDialog._model._data[selectedItemIndex]
                    self.setTitle(self.projectName)
                    self.initialDialog.listView.setCurrentIndex(QtCore.QModelIndex())
                    #self.initialDialog._model.layoutChanged.emit()
                    #self.initialDialog._model._data = self.initialDialog._model.findProjectsInFolder()
                    #self.initialDialog._model.layoutChanged.emit()



   
    def newDialog(self, filePath, title):
        """Load dialog window from a file."""
        dialog = QtWidgets.QDialog(self)
        with open(filePath) as f:
            uic.loadUi(f, dialog)
        dialog.setWindowTitle(title)
        return dialog

    def loadWindowUi(self):
        """Load window"""
        with open(self.windowUi) as f:
            uic.loadUi(f, self)






class ModelProjects(QtCore.QAbstractListModel):
    def __init__(self):
        super(ModelProjects, self).__init__()
        self._data = self.findProjectsInFolder()

    def data(self, index, role):
        if role == Qt.DisplayRole:
            return self._data[index.row()]

    def rowCount(self, index):
        """The length of the outer list."""
        return len(self._data)

    def findProjectsInFolder(self):
        return glob.glob('*.sqlite')





class  MatplotlibWidget(QtWidgets.QMainWindow):
    
    def  __init__(self):
        
        QtWidgets.QWidget.__init__ (self)

        uic.loadUi("graphics.ui",self)
        self.setCentralWidget(self.MplWidget)
        self.setWindowTitle("Graphical output")

        self.addToolBar(NavigationToolbar(self.MplWidget.canvas, self))
        #self.addToolBar(QtCore.Qt.BottomToolBarArea, NavigationToolbar(self.MplWidget.canvas, self))

