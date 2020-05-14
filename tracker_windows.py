from PyQt5 import uic, QtGui
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt
from datetime import date
import glob, os
from  matplotlib.backends.backend_qt5agg  import  (NavigationToolbar2QT  as  NavigationToolbar)
from controller import TrackerCtrl
from data_models import ModelProjects


class InitialWindow(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi("initial_dialog.ui",self)
        self.setWindowTitle("Initiate project")
        btnOpen = self.btnOpenProject
        btnNew = self.btnNewProject
        btnOpen.clicked.connect(self.accept)
        btnNew.clicked.connect(self.reject)
        self._model = ModelProjects()
        self.listView.setModel(self._model)
        self.selectedItem = self.listView.currentIndex()
    

class MyWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__()
        self.windowUi = 'view.ui'

        self.loadWindowUi()
        self.setWindowTitle('Expense Tracker')
        self.show()

        self.projectName = None

        self.dialogUi = 'dialog.ui'
        self.dialogRemove = 'dialogRemoveAll.ui'
        self.dialogPerson = self.newDialog(self.dialogUi, 'New person')
        self.dialogCathegory = self.newDialog(self.dialogUi, 'New cathegory')
        self.dialogPersonRemove = self.newDialog(self.dialogUi, 'Remove person')
        self.dialogCathegoryRemove = self.newDialog(self.dialogUi, 'Remove cathegory')
        self.dialogRemoveAll = self.newDialog(self.dialogRemove, 'Remove all')
        self.dialogNewProject = QtWidgets.QDialog()
        uic.loadUi("dialog_NewProject.ui",self.dialogNewProject)
        self.initialDialog = InitialWindow()
        self.openInitialDialog(self.initialDialog, self.dialogNewProject)

        self.dateAdd.setCalendarPopup(True)
        self.dateAdd.setDate(date.today())
        self.dateFilterFrom.setCalendarPopup(True)
        self.dateFilterFrom.setDate(date.today()) 
        self.dateFilterTo.setCalendarPopup(True)
        self.dateFilterTo.setDate(date.today())

        self.graphicalOutput = MatplotlibWidget()

    def setTitle(self, projectName):
        """Sets format of the main window: Expense Tracker - 'name of the project'."""
        if projectName:
            if projectName.endswith('.sqlite'):
                projectName = projectName[:-7]
            self.setWindowTitle('Expense Tracker - ' + projectName)
        else:
            self.setWindowTitle('Expense Tracker')

    def showMessageBox(self, text):
        """Show messagebox with defined text."""
        msgBox = QtWidgets.QMessageBox()
        msgBox.setText(text)
        msgBox.exec()

    def newProjectCheckName(self, newProject):
        """Ckecks if name of the new project already exists."""
        existingProjects = glob.glob('*.sqlite')
        for project in existingProjects:
            if newProject == os.path.splitext(project)[0]:
                return False
        return True

    def openNewProject(self):
        """Opens new main window."""
        self.window = MyWindow()
        self.window.show()
        self.ctrl = TrackerCtrl(view=self.window)
        self.close()

    def openInitialDialog(self, dialog, dialogNewProject):
        """Opens initial dialog, which is diplayed at the beggining of the program
        and after clicking on button for opening of the projects. Either existing 
        project is selected or new project is created.
        """
        selectedItemIndex = self.initialDialog.listView.currentIndex().row()
        while selectedItemIndex == -1: # no project selected
            result = dialog.exec()
            if result == QtWidgets.QDialog.Rejected:
                resultNewProject = dialogNewProject.exec()
                if resultNewProject == QtWidgets.QDialog.Rejected:
                    self.dialogNewProject.lineEdit.clear()
                else:
                    inputText = self.dialogNewProject.lineEdit.text()
                    if inputText:
                        if self.newProjectCheckName(inputText):
                            self.projectName = inputText + '.sqlite'
                            self.setTitle(inputText)
                            #self.initialDialog.listView.setCurrentIndex(QtCore.QModelIndex())
                            self.dialogNewProject.lineEdit.clear()
                            break
                        else:
                            self.dialogNewProject.lineEdit.clear()
                            self.showMessageBox("The project already exists.")
                    else:
                        self.showMessageBox("Write a name of the new project.")
            else:
                selectedItemIndex = self.initialDialog.listView.currentIndex().row()
                if selectedItemIndex == -1:
                    self.showMessageBox("No project has been selected.")
                else:
                    self.projectName = self.initialDialog._model._data[selectedItemIndex]
                    self.setTitle(self.projectName)
                    #self.initialDialog.listView.setCurrentIndex(QtCore.QModelIndex())

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


class  MatplotlibWidget(QtWidgets.QMainWindow):
    """Window for graphical output."""
    def  __init__(self):
        QtWidgets.QWidget.__init__ (self)
        uic.loadUi("graphics.ui",self)
        self.setCentralWidget(self.MplWidget)
        self.setWindowTitle("Graphical output")
        self.addToolBar(NavigationToolbar(self.MplWidget.canvas, self))

