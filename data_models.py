from PyQt5 import uic, QtGui
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt


class MyModel(QtCore.QAbstractTableModel):
    def __init__(self):
        super(MyModel, self).__init__()
        self._data = [('','','','', '')]

    def countAmount(self, data):
        """Calculates the total price of all items in the data"""
        totalAmount = 0
        try:
            for row in data:
                listData = list(row)
                totalAmount += int(listData[3])
            return totalAmount
        except ValueError:
            return totalAmount

    
    def createListOfIndexes(self):
        """Used for creation of the header"""
        rows = len(self._data)
        list_indexes = []
        for index in range (rows):
            list_indexes.append(index+1)
        return list_indexes

    
    def data(self, index, role):
        if role == Qt.DisplayRole:
            return self._data[index.row()][index.column()]
        if role == QtCore.Qt.TextAlignmentRole and index.column() == 3:
            return QtCore.Qt.AlignRight
        if role == QtCore.Qt.FontRole and index.column() == 3:
            font = QtGui.QFont()
            font.setBold(True)
            return font
        if role == QtCore.Qt.ForegroundRole and index.column() == 3:
            return QtGui.QColor(Qt.red)


            
    #def data(self, index, role=QtCore.Qt.DisplayRole):
        #if role == QtCore.Qt.TextAlignmentRole and index.column() == 3:
             #return QtCore.Qt.AlignHCenter
        #return super(MyModel, self).data(index, role)

    def rowCount(self, index):
        """The length of the outer list."""
        return len(self._data)

    def columnCount(self, index):
        """The length of the tuples"""
        print(self._data)
        return len(self._data[0])

    def headerData(self, section, orientation, role):
        # section is the index of the column/row.
        columns = ['Cathegory', 'Person', 'Date', 'Amount', 'ID']
        listIndexes = self.createListOfIndexes()
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(columns[section])
            if orientation == Qt.Vertical:
                return str(listIndexes[section])


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