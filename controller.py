from datetime import date, timedelta, datetime

import sqlite3
from sqlite3 import Error

from PyQt5 import QtWidgets, QtCore

from data_models import MyModel

import pandas



# 
#  Create a Controller class to connect the GUI and the model
class TrackerCtrl():
    """MyWindow Controller class."""
    def __init__(self, view):
        self._view = view
        self.connection = self.create_connection(self._view.projectName)
        self.queryCreateTableCathegory = """
                                            CREATE TABLE IF NOT EXISTS cathegory
                                            (id INTEGER PRIMARY KEY AUTOINCREMENT,
                                            name TEXT NOT NULL)
                                        """
        self.queryCreateTablePerson =  """
                                            CREATE TABLE IF NOT EXISTS person
                                            (id INTEGER PRIMARY KEY AUTOINCREMENT,
                                            name TEXT NOT NULL)
                                        """
        self.queryCreateTablePurchase = """
                                        CREATE TABLE IF NOT EXISTS purchase
                                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                                         amount INTEGER,
                                         date DATE,
                                         id_cathegory INTEGER,
                                         id_person INTEGER,
                                         FOREIGN KEY(id_cathegory) REFERENCES cathegory(id)
                                         FOREIGN KEY(id_person) REFERENCES person(id))
                                        """
        self.queryModel = """SELECT C.name, Pe.name, P.date, P.amount, P.id FROM purchase P 
                             INNER JOIN person Pe ON P.id_person=Pe.id
                             INNER JOIN cathegory C ON P.id_cathegory=C.id
                            """ 

        self.queryDatabase(self.connection, self.queryCreateTableCathegory, ())
        #self.addAllToTable(self.connection, 'cathegory')
        self.queryDatabase(self.connection, self.queryCreateTablePerson, ())
        #self.addAllToTable(self.connection, 'person')
        self.queryDatabase(self.connection, self.queryCreateTablePurchase, ())

        self._model = MyModel()
        self.ModelData(self.connection, self.queryModel, ()) 
        self.header = self._view.tableView.horizontalHeader()
        self.header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch) # Columns are stretched according to the widget width
        self._view.tableView.setHorizontalHeader (self.header)
        self._viewTable = self._view.tableView
        self._viewTable.setModel(self._model)
        self._viewTable.hideColumn(4)
        self._viewTable.setSelectionBehavior(QtWidgets.QTableView.SelectRows) #When clicked inside the table, whole row is selected

        self.filterDateFrom = None ##############################################
        self.filterDateTo = None
        self.filterCathegory = None
        self.filterPerson = None
        self.setTotalAmount()


        self._view.dateFilterFrom.setDate(self.setFilterDateFrom(self._model._data)) ######################################
        #self.setFilterDateFrom(self._model._data)#############################
        # Connect signals and slots
        self._connectSignals()

        self.queryAddPerson = """INSERT INTO person (name) VALUES (?)"""
        self.queryAddCathegory = """INSERT INTO cathegory (name) VALUES (?)"""
        self.queryRemovePerson = """DELETE FROM person WHERE name = (?)"""
        self.queryRemoveCathegory = """DELETE FROM cathegory WHERE name = (?)"""

        self.fillDropBox(self.connection, 'cathegory', self._view.boxCathegory)
        self.fillDropBox(self.connection, 'person', self._view.boxPerson)
        self.fillDropBoxFilter(self.connection, 'cathegory', self._view.boxCathegoryFilter)
        self.fillDropBoxFilter(self.connection, 'person', self._view.boxPersonFilter)

        self.MplWidget = self._view.graphicalOutput.MplWidget


    # potrebuji funkci, ktera vypise vybranou polozku z tabulky (jeji index), napr po kliknuti na filter button.
    # Zjistit, jak vypadaji data, ktera jdou do model, pripadne je upravit tak, aby tam slo i ID. ID ale pak nechci aby se zobrazovalo ve view

    def deleteItem(self):
        selectedRowIndex = self._view.tableView.currentIndex().row()
        if selectedRowIndex == -1:
            self.showMessageBox('Select an item to be deleted!')
            return
        result = self._view.dialogRemoveAll.exec()
        if result == QtWidgets.QDialog.Rejected:
            return
        query = """DELETE FROM purchase WHERE id = (?)"""
        selectedItemID = self._model._data[selectedRowIndex][4]
        print(self._model._data[selectedRowIndex])
        del self._model._data[selectedRowIndex]
        self.queryDatabase(self.connection, query, (selectedItemID,))
        if not self._model._data:
            self._model._data = [('','','','', '')]
        self._model.layoutChanged.emit()
        self._view.dateFilterFrom.setDate(self.setFilterDateFrom(self._model._data))
        self.setTotalAmount()
        print(selectedRowIndex)

        # musim to take odstranit z dat v modelu, nejenom z databaze. To se zde neprojevi
        
        #print(self._model._data[self._view.tableView.currentIndex().row()][4])
        #self.initialDialog.listView.currentIndex().row()
        ## pokud neni nic vybrano, tak vrati id posledniho prvku ze seznamu
        # pripojit to k soucasnemu remove all

    
    def setFilterDateFrom(self, data):
        """Prevest data na pandas a pak najit minimalni hodnotu pomoci nsmallest nebo min."""
        if data != [('', '', '', '', '')]:
            items = pandas.DataFrame(data, columns =['cathegory', 'person', 'date', 'amount', 'id'])
            items['date'] = pandas.to_datetime(items['date'], dayfirst=True)
            new_items = items.set_index('date')
            minimal_date = new_items.index.min()
            print(minimal_date)
            return minimal_date
        else:
            dateFrom = datetime.today()
            return dateFrom



    def create_connection(self, path):
        """Connect to the sqlite3 database"""
        connection = None
        try:
            connection = sqlite3.connect(path)
            print("Connection to SQLite DB successful")
        except Error as e:
            print(f"The error '{e}' occurred")
        return connection

    def queryDatabase(self, connection, query, param):
        """Query database."""
        cursor = connection.cursor()
        try:
            cursor.execute(query, param)
            connection.commit()
            print("Query executed successfully")
        except Error as e:
            print(f"The error '{e}' occurred")
    
    def showMessageBox(self, text):
        msgBox = QtWidgets.QMessageBox()
        msgBox.setText(text)
        msgBox.exec()
    
    '''def addAllToTable(self, connection, table):
        """Add all to tables (used fo table Cathegory and Person)"""
        cursor = connection.cursor()
        query = f'INSERT INTO {table} (name) VALUES ("all")'
        try:
            cursor.execute(query)
            connection.commit()
            print("Query executed successfully")
        except Error as e:
            print(f"The error '{e}' occurred")'''

    def select_query(self, connection, query, param):
        """"Is used in all queries which returns something"""
        cursor = connection.cursor()
        result = None
        try:
            cursor.execute(query, param)
            result = cursor.fetchall()
            return result
        except Error as e:
            print(f"The error '{e}' occurred")

    def setTotalAmount(self):
        """Calculate the total amount of visible purchase"""
        totalAmount = self._model.countAmount(self._model._data)
        totalAmountLabel = self._view.totalSum
        totalAmountLabel.setText(self.TotalAmountText(totalAmount))

    def TotalAmountText(self, totalAmount):
        """Create string which is seen in totalSum label"""
        return f'{totalAmount} kč'

    def convertDateInData(self,data):
        """Change formate of the date in the data. New format is used in the view"""
        for index, row in enumerate(data):
            list_from_tuple = list(row)
            list_from_tuple[2] = datetime.strptime(list_from_tuple[2], '%Y-%m-%d').strftime('%d.%m.%Y')
            newTuple = tuple(list_from_tuple)
            data[index] = newTuple
        return data

    def ModelData(self, connection, query, param): 
        """Ask database and hand data to the model"""
        dataEmpty = [('','','','', '')]
        result = self.select_query(connection, query, param)
        if result:
            data = self.convertDateInData(result)
            self._model._data = data
            connection.commit()
        else:
            self._model._data = dataEmpty
        self._model.layoutChanged.emit()

    def notItemInDatabase(self, newItem, table, connection):
        """Return false if an item is already in the table.
        It is used for addPerson and addCathegory button.
        We want to add only unic values"""
        query = f'SELECT name FROM {table}'
        result = self.select_query(connection, query, ())
        for row in result:
                if row[0] == newItem:
                    return False
        return True

    def fillDropBox(self, connection, table, box):
        """Set items of the dropbox"""
        box.clear()
        query = f'SELECT DISTINCT name FROM {table}'
        result = self.select_query(connection, query, ())
        for row in result:
            box.addItem(row[0])

    def fillDropBoxFilter(self, connection, table, box):
        """Set items of the dropbox.
        It add '-' at the begining of the list"""
        box.clear()
        query = f'SELECT DISTINCT name FROM {table}'
        result = self.select_query(connection, query, ())
        box.addItem('-')
        for row in result:
            box.addItem(row[0])

    def findIdOfItem(self, connection, query, item):
        """Return id of person or cathegory from the table.
        The id is then used to find purchase from the table purchase"""
        param = (item,)
        cursor = connection.cursor()
        result = None
        try:
            cursor.execute(query, param)
            result = cursor.fetchall()
            print(result)
            return result
        except Error as e:
            print(f"The error '{e}' occurred")
    
    def resetAddPurchase(self):
        self._view.amount.setText('')
        self._view.boxCathegory.setCurrentIndex(0)
        self._view.boxPerson.setCurrentIndex(0)
        self._view.dateAdd.setDate(datetime.today())

    def _buttonClick(self):
        """It inserts new purchase into the database purchase"""
        try:
            amountText = int(self._view.amount.text())
    
        except ValueError:
            self.showMessageBox("Write the price of the purchase as whole number")
        else:
            boxCathegory = self._view.boxCathegory.currentText() # pokud je ''
            boxPerson = self._view.boxPerson.currentText() # pokud je ''
            dateAdd = self._view.dateAdd.date()
            dateString = dateAdd.toString('yyyy-MM-dd')
            queryPerson = """SELECT id FROM person WHERE name = (?)"""
            queryCathegory = """SELECT id FROM cathegory WHERE name = (?)"""
            if boxPerson and boxCathegory:
                idPerson = int(self.findIdOfItem(self.connection, queryPerson, boxPerson)[0][0])
                idCathegory = int(self.findIdOfItem(self.connection, queryCathegory, boxCathegory)[0][0])
                query = """INSERT INTO purchase (amount, date, id_cathegory, id_person) VALUES (?, ?, ?, ?)"""
                param = (amountText, dateString, idCathegory, idPerson,)
                self.queryDatabase(self.connection, query, param)
                self.ModelData(self.connection, self.queryModel, ())
                self._model.layoutChanged.emit()
                self._viewTable.hideColumn(4)
                self.setTotalAmount()
                self.resetAddPurchase()
                self._view.dateFilterFrom.setDate(self.setFilterDateFrom(self._model._data))
            elif boxPerson:
                self.showMessageBox("Select cathegory")
            elif boxCathegory:
                self.showMessageBox("Select person")
            else:
                self.showMessageBox("Select cathegory and person")


    def btnFilterClick(self):
        """"It filters the data from the purchase table for the viewTable"""
        query = None
        param = None
        queryPerCat = """
                    SELECT C.name, Pe.name, P.date, P.amount, P.id FROM purchase P
                    INNER JOIN person Pe ON P.id_person=Pe.id
                    INNER JOIN cathegory C ON P.id_cathegory=C.id
                    WHERE P.date BETWEEN (?) AND (?)
                    AND Pe.name=(?)
                    AND c.name=(?)
                """ 
        queryCathegory = """
                    SELECT C.name, Pe.name, P.date, P.amount, P.id FROM purchase P
                    INNER JOIN person Pe ON P.id_person=Pe.id
                    INNER JOIN cathegory C ON P.id_cathegory=C.id
                    WHERE P.date BETWEEN (?) AND (?)
                    AND c.name=(?)
                """ 
        queryPerson = """
                    SELECT C.name, Pe.name, P.date, P.amount, P.id FROM purchase P
                    INNER JOIN person Pe ON P.id_person=Pe.id
                    INNER JOIN cathegory C ON P.id_cathegory=C.id
                    WHERE P.date BETWEEN (?) AND (?)
                    AND Pe.name=(?)
                """ 
        queryDates = """
                    SELECT C.name, Pe.name, P.date as date, P.amount, P.id FROM purchase P
                    INNER JOIN person Pe ON P.id_person=Pe.id
                    INNER JOIN cathegory C ON P.id_cathegory=C.id
                    WHERE p.date BETWEEN (?) AND (?)
                """
        self.filterCathegory = self._view.boxCathegoryFilter.currentText()
        self.filterPerson = self._view.boxPersonFilter.currentText()
        self.filterDateFrom = self._view.dateFilterFrom.date().toString('yyyy-MM-dd')
        self.filterDateTo = self._view.dateFilterTo.date().toString('yyyy-MM-dd')
        if self.filterCathegory == '-' and self.filterPerson == '-':
            query = queryDates
            param = (self.filterDateFrom, self.filterDateTo,)
            self.ModelData(self.connection, query, param)
        elif self.filterPerson == '-':
            query = queryCathegory
            param = (self.filterDateFrom, self.filterDateTo, self.filterCathegory,)
            self.ModelData(self.connection, query, param)
        elif self.filterCathegory == '-':
            query = queryPerson
            param = (self.filterDateFrom, self.filterDateTo, self.filterPerson,)
            self.ModelData(self.connection, query, param)
        else:
            query = queryPerCat
            param = (self.filterDateFrom, self.filterDateTo, self.filterPerson, self.filterCathegory)
            self.ModelData(self.connection, query, param) ##################
        self.setTotalAmount()
 
    def dialogExecutionAdd(self, dialogWindow, queryDatabase, table, box1, box2):
        """It adds new item into the table(person/cathegory), if not already there.
        It refreshes the items of dropboxes. It is used in openDialog() method
        """
        result = dialogWindow.exec()
        inputText = dialogWindow.dialogInputName.text()
        if result == QtWidgets.QDialog.Rejected:
            dialogWindow.dialogInputName.clear()
            return
        if self.notItemInDatabase(inputText, table, self.connection):
            self.queryDatabase(self.connection, queryDatabase, (inputText,))
        else:
            self.showMessageBox("The selected name already exists.")
        dialogWindow.dialogInputName.clear()
        self.fillDropBox(self.connection, table, box1)
        self.fillDropBoxFilter(self.connection, table, box2)


    def openProject(self):
        pass

    def dialogExecutionRemove(self, dialogWindow, queryDatabase, table, box1, box2): #########################
        """It removes an item from the table(person/cathegory), if it is there.
        It refreshes the items of dropboxes. It is used in openDialog() method
        """
        result = dialogWindow.exec()
        inputText = dialogWindow.dialogInputName.text()
        if result == QtWidgets.QDialog.Rejected:
            dialogWindow.dialogInputName.clear()
            return
        if not self.notItemInDatabase(inputText, table, self.connection):
            self.queryDatabase(self.connection, queryDatabase, (inputText,))
        dialogWindow.dialogInputName.clear()
        self.fillDropBox(self.connection, table, box1)
        self.fillDropBoxFilter(self.connection, table, box2)

    '''def dialogExecutionRemoveAll(self, table1, table2, boxes): ##########################################################################
        """It removes all items from the tables cathegory and person"""
        result = self._view.dialogRemoveAll.exec()
        query1 = f'DELETE FROM {table1}'
        query2 = f'DELETE FROM {table2}'
        if result == QtWidgets.QDialog.Rejected:
            return
        cursor = self.connection.cursor()
        try:
            cursor.execute(query1)
            cursor.execute(query2)
            self.addAllToTable(self.connection, table1)
            self.addAllToTable(self.connection, table2)
            self.connection.commit()
            print("Query executed successfully")
        except Error as e:
            print(f"The error '{e}' occurred")
        for box in boxes:
            box.clear()'''

    def openDialog(self):
        """Depending on pressed button from toolbar, it opens dialog window, which serves
        for adding or removing items from the tables.
        """
        pressedBtn = self._view.sender().text()

        if  pressedBtn == 'new cathegory':
            self.dialogExecutionAdd(self._view.dialogCathegory, self.queryAddCathegory, 'cathegory', self._view.boxCathegory, self._view.boxCathegoryFilter)
        
        elif  pressedBtn == 'new person':
            self.dialogExecutionAdd(self._view.dialogPerson, self.queryAddPerson, 'person', self._view.boxPerson, self._view.boxPersonFilter)

        elif pressedBtn == 'open project':
            #####################
            # potreba vytvorit funkci, ktera nastavi zacatek a zavola se pokazde, kdyz se vytvori novy projekt v ramci kliknuti na tento cudlik.
            # potreba vytvorit tabulky. Otazka, zda neni jednodussi to rozdelit. Vytvorit novy ctrl
            self._view.openNewProject()
            #self._view.projectName = None
            #self._view.initialDialog._model._data = self._view.initialDialog._model.findProjectsInFolder()
            #self._view.openInitialDialog(self._view.initialDialog, self._view.dialogNewProject)
            #self.connection = self.create_connection(self._view.projectName)
            #self.ModelData(self.connection, self.queryModel, ())
            ##########################################################
            #self.dialogExecutionRemove(self._view.dialogPersonRemove, self.queryRemovePerson, 'person', self._view.boxPerson, self._view.boxPersonFilter)
        
        #elif pressedBtn == 'delete item':
            #self.dialogExecutionRemove(self._view.dialogCathegoryRemove, self.queryRemoveCathegory, 'cathegory', self._view.boxCathegory, self._view.boxCathegoryFilter)

        elif pressedBtn == 'delete item':
            self.deleteItem()
    
    def setDateTo(self):
        """It ensures that the dates from and to are valid.
        The date to has to be greater than from."""
        dateTo = self._view.dateFilterTo.date()
        dateFrom = self._view.dateFilterFrom.date()
        if dateFrom > dateTo:
            self._view.dateFilterTo.setDate(dateFrom.addDays(1))
    
    def setDateFrom(self):
        """It ensures that the dates from and to are valid.
        The date from has to be lesser than to."""
        dateTo = self._view.dateFilterTo.date()
        dateFrom = self._view.dateFilterFrom.date()
        if dateFrom > dateTo:
            self._view.dateFilterFrom.setDate(dateTo.addDays(-1))
    
    def sortedBy(self):
        """It returns a tuple of the parameters used for sorting.
        By what it is sorted and ASC/DESC"""
        if self._view.amountASC.isChecked():
            return ('P.amount', 'ASC')
        elif self._view.amountDESC.isChecked():
            return ('P.amount', 'DESC')
        elif self._view.dateASC.isChecked():
            return ('P.date', 'ASC')
        elif self._view.dateDESC.isChecked():
            return ('P.date', 'DESC')

    def sort(self):
        """It sorts the items displayed in the tableView.
        The items can be sorted either by price or by date."""
        try:
            sortedBy, sorting = self. sortedBy()
        except TypeError:
            pass
        else:
            queryAll = ('SELECT C.name, Pe.name, P.date, P.amount, P.id '
                        'FROM purchase P '
                        'INNER JOIN person Pe ON P.id_person=Pe.id '
                        'INNER JOIN cathegory C ON P.id_cathegory=C.id ' 
                        'ORDER BY {} {}'.format(sortedBy, sorting))
            queryPC = ('SELECT C.name, Pe.name, P.date, P.amount, P.id FROM purchase P '
                        'INNER JOIN person Pe ON P.id_person=Pe.id '
                        'INNER JOIN cathegory C ON P.id_cathegory=C.id '
                        'WHERE P.date BETWEEN (?) AND (?) '
                        'AND Pe.name=(?) '
                        'AND c.name=(?) '
                        'ORDER BY {} {}'.format(sortedBy, sorting))
            queryCathegory = ('SELECT C.name, Pe.name, P.date, P.amount, P.id FROM purchase P '
                            'INNER JOIN person Pe ON P.id_person=Pe.id '
                            'INNER JOIN cathegory C ON P.id_cathegory=C.id '
                            'WHERE P.date BETWEEN (?) AND (?) '
                            'AND c.name=(?) '
                            'ORDER BY {} {}'.format(sortedBy, sorting))
            queryPerson = ('SELECT C.name, Pe.name, P.date, P.amount, P.id FROM purchase P '
                        'INNER JOIN person Pe ON P.id_person=Pe.id '
                        'INNER JOIN cathegory C ON P.id_cathegory=C.id '
                        'WHERE P.date BETWEEN (?) AND (?) '
                        'AND Pe.name=(?) '
                        'ORDER BY {} {}'.format(sortedBy, sorting))
            queryDates = ('SELECT C.name, Pe.name, P.date as date, P.amount, P.id FROM purchase P '
                        'INNER JOIN person Pe ON P.id_person=Pe.id '
                        'INNER JOIN cathegory C ON P.id_cathegory=C.id '
                        'WHERE p.date BETWEEN (?) AND (?) '
                        'ORDER BY {} {}'.format(sortedBy, sorting))
            
            if not self.filterDateFrom and not self.filterDateTo:
                param = ()
                self.ModelData(self.connection, queryAll, param)
            else:
                if self.filterCathegory == '-' and self.filterPerson == '-':
                    query = queryDates
                    param = (self.filterDateFrom, self.filterDateTo,)
                    self.ModelData(self.connection, query, param)
                elif self.filterPerson == '-':
                    query = queryCathegory
                    param = (self.filterDateFrom, self.filterDateTo, self.filterCathegory,)
                    self.ModelData(self.connection, query, param)
                elif self.filterCathegory == '-':
                    query = queryPerson
                    param = (self.filterDateFrom, self.filterDateTo, self.filterPerson,)
                    self.ModelData(self.connection, query, param)
                else:
                    query = queryPC
                    param = (self.filterDateFrom, self.filterDateTo, self.filterPerson, self.filterCathegory)
                    self.ModelData(self.connection, query, param)

    def showGraphics(self):
        if len(self._model._data) > 1: ### toto ulozit nekam nahoru do promenne, aby se dalo menit jen na jednom miste
            self.MplWidget.pandasDataCathegory = self.MplWidget.pandasConvert(self._model._data, 'cathegory')
            self.MplWidget.pandasDataPerson = self.MplWidget.pandasConvert(self._model._data, 'person')
            self.MplWidget.pandasDataAmountInTime = self.MplWidget.pandasConvertDateChart(self._model._data, 'date') #####################
            if self.MplWidget.firstPlotting:
                self.MplWidget.subsequentPlot()
            else:
                self.MplWidget.firstPlot()
                self.MplWidget.firstPlotting = True

            self._view.graphicalOutput.show()
            print(self.MplWidget.pandasDataCathegory)
        else:
            self.showMessageBox('Not enough data in the database!')

    def _connectSignals(self):
        """It finds buttons and it joins them with respective plots"""
        btnGraphics = self._view.BtnGraphics
        btn = self._view.pushButton
        dateEditFrom = self._view.dateFilterFrom
        dateEditTo = self._view.dateFilterTo
        btnFilter = self._view.btnFilter
        btnAddPerson = self._view.actionnew_person
        btnAddCathegory = self._view.actionnew_cathegory
        #btnRemoveCathegory = self._view.actionremove_cathegory #####################
        btnRemovePerson = self._view.actionremove_person
        btnRemoveAll = self._view.actionremove_all
        btnSort = self._view.btnSort
        btnAddPerson.triggered.connect(self.openDialog)
        btnAddCathegory.triggered.connect(self.openDialog)
        btnRemovePerson.triggered.connect(self.openDialog)
        #openDialogForNewProject = lambda x, y, func: func(x, y)
        #btnRemoveCathegory.triggered.connect(openDialogForNewProject(self._view.initialDialog, self._view.dialogNewProject, self._view.openInitialDialog))
        #btnRemoveCathegory.triggered.connect(lambda x,y, func: func(x, y))(self._view.initialDialog, self._view.dialogNewProject, self._view.openInitialDialog) ##################
        btnRemoveAll.triggered.connect(self.openDialog)
        btn.clicked.connect(self._buttonClick)
        btnFilter.clicked.connect(self.btnFilterClick)
        dateEditFrom.dateChanged.connect(self.setDateTo)
        dateEditTo.dateChanged.connect(self.setDateFrom)
        btnSort.clicked.connect(self.sort)
        btnGraphics.clicked.connect(self.showGraphics)