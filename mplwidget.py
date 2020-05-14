from PyQt5 import QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import (NavigationToolbar2QT as NavigationToolbar)
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import pandas
from datetime import timedelta
    

# the central widget of the graphical output window. The class of the widget is set in qt designer.
class MplWidget(QtWidgets.QWidget):    
    def __init__(self, parent = None):
        QtWidgets.QWidget.__init__(self, parent)
        self.canvas = FigureCanvas(Figure(figsize = (10,10)))
        self.data = None
        vertical_layout = QtWidgets.QVBoxLayout() 
        vertical_layout.addWidget(self.canvas)
        self.pandasDataCathegory = None
        self.pandasDataPerson = None
        self.pandasDataAmountInTime = None
        self.firstPlotting = None
        self.setLayout(vertical_layout)

    def pandasConvert(self, data, index):
        """Convert data into pandas data frame. Groups data by the selected index.
        Used for the bar charts.
        """
        if data:
            items = pandas.DataFrame(data, columns =['cathegory', 'person', 'date', 'amount', 'id'])
            new_items = items.set_index(index)
            itemsGrouped = new_items.groupby(level=0).sum()
            return itemsGrouped

    def pandasConvertDateChart(self, data, index):
        """Converts data into pandas dataframe. The data are used for the chart depicting expenses for the cathegories in time.
        Resulting chart depicts increase of the expenses for particular cathegories in week intervals.
        """
        if data:
            items = pandas.DataFrame(data, columns =['cathegory', 'person', 'date', 'amount', 'id'])
            items['date'] = pandas.to_datetime(items['date'], dayfirst=True)

            items_sorted = items.sort_values(by='date')
            dates = self.listOfDates(items_sorted)
            cathegories = items['cathegory'].unique().tolist()
            #firstDay = dates[0]
            ExpensesInTimeForCathegories = {}
            totalSum = 0
            for cathegory in cathegories:
                ExpensesInTimeForCathegories[cathegory] = [totalSum]
                for index, week in enumerate(dates):
                    try: nextDate = index + 1
                    except IndexError:
                        break
                    for _, row in items_sorted.iterrows():
                        date = row[2]
                        amount = row[3]
                        cathegoryInData = row[0]
                        if cathegoryInData == cathegory:
                            if week < date <= dates[nextDate]:
                                totalSum += amount
                    try:
                        ExpensesInTimeForCathegories[cathegory].append(totalSum)
                    except IndexError:
                        pass
                totalSum = 0
            
            dates.append(dates[-1] + timedelta(days=7))
            df = pandas.DataFrame(ExpensesInTimeForCathegories, index=dates)
            
            return df
    
    def listOfDates(self, data):
        """Return list of dates used in the time chart. The dates have week interval."""
        listOfWeeks = []
        firstEntry = data['date'][data.index[0]] - timedelta(days=7)
        lastEntry = data['date'][data.index[-1]] + timedelta(days=7)
        while firstEntry <= lastEntry:
            listOfWeeks.append(firstEntry)
            firstEntry = firstEntry + timedelta(days=7)
        return listOfWeeks

    def getListOfCathegories(self, data):
        """returns list of the cathegories."""
        return data.date.unique()

    def plotCharts(self):
        """Plot charts."""
        self.pandasDataPerson.plot.barh(y='amount', ax=self.canvas.axes2, fontsize=8, title='Purchases for particular persons', legend=False)
        self.canvas.axes2.set_xlabel('amount (kč)', fontsize=10)
        self.canvas.axes2.set_ylabel('')
        self.pandasDataCathegory.plot.barh(y='amount', ax=self.canvas.axes1, fontsize=8, title='Purchases for particular cathegories', legend=False)
        self.canvas.axes1.set_xlabel('amount (kč)', fontsize=10)
        self.canvas.axes1.set_ylabel('')
        self.pandasDataAmountInTime.plot.area(ax=self.canvas.axes3, fontsize=8, title='Time graph of expences for particular cathegories')
        self.canvas.axes3.legend(fontsize=8)
        self.canvas.axes3.set_ylabel('amount (kč)', fontsize=10)
        self.canvas.axes3.set_xlabel('date', fontsize=10)

    def firstPlot(self):
        """Set grid and axes position in the grid. Plot charts."""
        gs = GridSpec(2, 2)
        gs.update(wspace=0.25, hspace=0.5)
        self.canvas.axes1 = self.canvas.figure.add_subplot(gs[0, 0])
        self.canvas.axes2 = self.canvas.figure.add_subplot(gs[0, 1])
        self.canvas.axes3 = self.canvas.figure.add_subplot(gs[1, :])
        self.plotCharts()
        plt.tight_layout()


    def subsequentPlot(self):
        """Used to redraw charts."""
        self.canvas.axes1.clear()
        self.canvas.axes2.clear()
        self.canvas.axes3.clear()
        self.plotCharts()
        self.canvas.axes1.figure.canvas.draw()
        self.canvas.axes2.figure.canvas.draw()
        self.canvas.axes3.figure.canvas.draw()


    