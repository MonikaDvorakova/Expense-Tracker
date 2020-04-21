from PyQt5 import QtWidgets

from matplotlib.backends.backend_qt5agg import FigureCanvas

from matplotlib.figure import Figure

from matplotlib.backends.backend_qt5agg import (NavigationToolbar2QT as NavigationToolbar)
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import pandas
from datetime import timedelta

    
class MplWidget(QtWidgets.QWidget):    
    def __init__(self, parent = None):
        QtWidgets.QWidget.__init__(self, parent)
        self.canvas = FigureCanvas(Figure(figsize = (10,10)))
        self.data = None
        #toolbar = NavigationToolbar(self.canvas, self)
        vertical_layout = QtWidgets.QVBoxLayout() 
        vertical_layout.addWidget(self.canvas)
        #vertical_layout.addWidget(toolbar)
        self.pandasDataCathegory = None
        self.pandasDataPerson = None
        self.pandasDataAmountInTime = None
        self.firstPlotting = None

        self.setLayout(vertical_layout)


        """df = pandas.DataFrame({'mass': [0.330, 4.87 , 5.97],
                   'radius': [2439.7, 6051.8, 6378.1]},
                  index=['Mercury', 'Venus', 'Earth'])
        plot = df.plot.pie(y='mass', figsize=(5, 5))"""





        labels = 'Frogs', 'Hogs', 'Dogs', 'Logs'
        sizes = [15, 30, 45, 10]
        explode = (0, 0.1, 0, 0)  # only "explode" the 2nd slice (i.e. 'Hogs')

        #fig1, ax1 = plt.subplots()
        #self.canvas.axes1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
        #shadow=True, startangle=90)
        #self.canvas.axes1.axis('equal')
        #self.canvas.axes1.pie(x='cathegory', y='amount', figsize=(5, 5))




    
    def pandasConvert(self, data, index):
        if data:
            items = pandas.DataFrame(data, columns =['cathegory', 'person', 'date', 'amount'])
            new_items = items.set_index(index)
            itemsGrouped = new_items.groupby(level=0).sum()

            #self.pandasData.plot.pie(x='cathegory', y='amount', figsize=(5, 5))
            return itemsGrouped

    def pandasConvertDateChart(self, data, index):
        if data:
            items = pandas.DataFrame(data, columns =['cathegory', 'person', 'date', 'amount'])
            items['date'] = pandas.to_datetime(items['date'], dayfirst=True)
            #new_items = items.set_index(index)

            items_sorted = items.sort_values(by='date')
            dates = self.listOfDates(items_sorted)
            cathegories = items['cathegory'].unique().tolist()
            firstDay = dates[0]
            vyslednySlovnik = {}
            soucet = 0
            for cathegory in cathegories:
                vyslednySlovnik[cathegory] = [soucet]
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
                                soucet += amount
                    try:
                        vyslednySlovnik[cathegory].append(soucet)
                    except IndexError:
                        pass
                soucet = 0
            
            #df = pandas.DataFrame(vyslednySlovnik, index=pandas.date_range(start=dates[0], end=dates[-1] + timedelta(days=7), freq='7D'))
            dates.append(dates[-1] + timedelta(days=7))
            df = pandas.DataFrame(vyslednySlovnik, index=dates)
            print(df)
            print(vyslednySlovnik)
            # budu prochazet radky.zajima me kategorie, potom me zajima datum, to porovnam, jestli je mezi dvemi hodnotami
            
            print(type(items_sorted['date'][1]))
            return df
    
            """    df = pd.DataFrame({
                'sales': [3, 2, 3, 9, 10, 6],
                'signups': [5, 5, 6, 12, 14, 13],
                'visits': [20, 42, 28, 62, 81, 50],
            }, index=pd.date_range(start='2018/01/01', end='2018/07/01',
                                freq='M'))
            ax = df.plot.area()"""


    def listOfDates(self, data):
        listOfWeeks = []
        firstEntry = data['date'][data.index[0]] - timedelta(days=7)
        lastEntry = data['date'][data.index[-1]] + timedelta(days=7)
        while firstEntry <= lastEntry:
            listOfWeeks.append(firstEntry)
            firstEntry = firstEntry + timedelta(days=7)
        return listOfWeeks

    def getListOfCathegories(self, data):
        return data.date.unique()




    ### je potreba udelat groupby a secist hodnoty amount pro ednotlive kategorie. Vysledna tabulka se pak pouzije pro vykresleni


    def plotPandasCathegory(self):
        return self.pandasDataCathegory.plot.pie(y='amount', ax=self.canvas.axes3, autopct='%.0f%%', shadow=True, startangle=60) # vraci axes

    def plotPandasPerson(self):
        return self.pandasDataPerson.plot.pie(y='amount', ax=self.canvas.axes1, autopct='%.0f%%', shadow=True, startangle=60) # vraci axes

        #autopct='%.0f%%', shadow=True, startangle=60

    def firstPlot(self):
        gs = GridSpec(2, 2)
        gs.update(wspace=0.25, hspace=0.5)
        self.canvas.axes1 = self.canvas.figure.add_subplot(gs[0, 0])
        self.canvas.axes2 = self.canvas.figure.add_subplot(gs[0, 1])
        self.canvas.axes3 = self.canvas.figure.add_subplot(gs[1, :])
        #self.pandasDataCathegory.plot.pie(y='amount', ax=self.canvas.axes3, autopct='%.0f%%', shadow=True, startangle=60, fontsize=8)
        #self.pandasDataPerson.plot.pie(y='amount', ax=self.canvas.axes1, autopct='%.0f%%', shadow=True, startangle=60, fontsize=8)
        #self.canvas.axes1.get_legend().remove()
        #self.canvas.axes1.legend(loc=3, labels=self.pandasDataPerson.index, fontsize=8)
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

        plt.tight_layout()


    def subsequentPlot(self):
        self.canvas.axes1.clear()
        self.canvas.axes2.clear()
        self.canvas.axes3.clear()
        
        #self.canvas.axes1.figure.canvas.draw()
        #self.canvas.axes2.figure.canvas.draw()
        #self.canvas.axes3.figure.canvas.draw()

        #self.pandasDataCathegory.plot.pie(y='amount', ax=self.canvas.axes3, autopct='%.0f%%', shadow=True, startangle=60)
        #self.pandasDataPerson.plot.pie(y='amount', ax=self.canvas.axes1, autopct='%.0f%%', shadow=True, startangle=60)
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
        self.canvas.axes1.figure.canvas.draw()
        self.canvas.axes2.figure.canvas.draw()
        self.canvas.axes3.figure.canvas.draw()


    