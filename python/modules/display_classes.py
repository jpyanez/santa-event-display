from . import QtCore, QtGui, QtWidgets
from . import figureLayouts
from . import array, append,  unique

class ComboTextBox(QtWidgets.QFrame):
    def __init__(self, parent):
        QtWidgets.QFrame.__init__(self, parent)
        comboLayout = QtWidgets.QHBoxLayout()
        comboLayout.setContentsMargins(0, 0, 0, 0)
        comboLayout.setSpacing(4)
        self.colors = [QtGui.QColor('#C0C0C0'), QtGui.QColor('#FFFFFF')]
        self.comboBox = QtWidgets.QComboBox(parent)
        self.textBox  = QtWidgets.QLineEdit(parent)
        self.textBox.setText('2')
        self.textBox.setEnabled(True)
        self.textBox.setPlaceholderText('Auto count or manual strings')

        self.defaultItems = ['Auto', 'Manual']
        selectorItems  = self.defaultItems + list(figureLayouts.keys())

        for oneItem in selectorItems:
            self.comboBox.addItem(oneItem)
        
        self.comboBox.activated[str].connect(self.comboChanged)

        comboLayout.addWidget(QtWidgets.QLabel('Layout:'))
        comboLayout.addWidget(self.comboBox)
        comboLayout.addWidget(self.textBox)
        self.setLayout(comboLayout)

        
    def comboChanged(self, text):
        if text in self.defaultItems:
            self.textBox.setEnabled(True)
        else:
            self.textBox.setEnabled(False)

    
    def selectedItem(self):
        return [self.comboBox.currentText(), self.textBox.text()]



class CheckboxScroll(QtWidgets.QScrollArea):
    def __init__(self, parent):
        QtWidgets.QScrollArea.__init__(self, parent)
        self.updateItems(['Open a file to start'], [])
        self.setMinimumHeight(210)

    def updateItems(self, itemsList, previousList, selectedItems=None, mainItem=None):
        itemsBox = QtWidgets.QFrame()
        itemsLayout = QtWidgets.QGridLayout()
        itemsLayout.setSpacing(1)
        #itemsLayout.setAlignment(QtCore.Qt.AlignVCenter)
        #itemsLayout.setAlignment(QtCore.Qt.AlignBottom)

        previous_states = {}
        if len(previousList) > 0:
            oldCbItem = self.cbItem
            oldRadioItem = self.radioItem
            for j in range(0, len(previousList)):
                previous_states[previousList[j]] = (oldCbItem[j].isChecked(), oldRadioItem[j].isChecked())

        self.cbItem = []
        self.radioItem = []
        self.radioGroup = QtWidgets.QButtonGroup(self)
        self.radioGroup.setExclusive(True)
        i = 0
        if selectedItems is None:
            selectedItems = []

        for itemName in itemsList:
            self.cbItem.append(QtWidgets.QCheckBox(itemName, self))
            self.radioItem.append(QtWidgets.QRadioButton('', self))
            self.radioGroup.addButton(self.radioItem[-1])

            checked = False
            radio_checked = False
            if itemName in selectedItems:
                checked = True
            elif itemName in previous_states:
                checked = previous_states[itemName][0]

            if itemName == mainItem:
                radio_checked = True
            elif itemName in previous_states:
                radio_checked = previous_states[itemName][1]

            self.cbItem[-1].setChecked(checked)
            self.radioItem[-1].setChecked(radio_checked)

            self.radioItem[-1].clicked[bool].connect(self.radioActivatesCheckbox)
            self.cbItem[-1].clicked[bool].connect(self.checkboxActivatesRadio)
            itemsLayout.addWidget(self.radioItem[-1], i, 0)
            itemsLayout.addWidget(self.cbItem[-1], i, 1)
            i += 1
        itemsBox.setLayout(itemsLayout)
        self.setWidget(itemsBox)

    def radioActivatesCheckbox(self, state): 
        # If i want to re-draw automatically, I could put it here. Call re-draw as soon as I click or un-click
        for i in range(0, len(self.radioItem)):
            if self.radioItem[i].isChecked():
                break
        if not self.cbItem[i].isChecked():
            self.cbItem[i].toggle()

    def checkboxActivatesRadio(self, state):
        for i in range(0, len(self.radioItem)):
            if self.cbItem[i].isChecked():
                number = i
            if self.radioItem[i].isChecked():
                break
        try:
            self.radioItem[number].toggle()
        except:
            None
        

    def checkAllItems(self, itemsList):
        series_on = []
        for i in range(0, len(itemsList)):
            if self.cbItem[i].isChecked():
                series_on.append(itemsList[i])
        return series_on

    def getMainSeries(self, itemsList):
        for i in range(0, len(itemsList)):
            if self.radioItem[i].isChecked():
                return itemsList[i]
        return None

def textToArray(ftext):
    new_array = array([])
    failed = False
    ftext = str(ftext)
    ftext = ftext.replace(' ','')
    comma_split = ftext.split(',')
    for one_expr in comma_split:
        dash_split = one_expr.split('-')
        if len(dash_split) == 1:
            new_array = append(new_array, int(dash_split[0]))
        elif len(dash_split) == 2:
            dash_split[0] = int(dash_split[0])
            dash_split[1] = int(dash_split[1])
            if dash_split[1] >= dash_split[0]:
                new_array = append(new_array, range(dash_split[0], dash_split[1]+1))
            else:
                failed = True
        else:
            failed = True
    
    if failed:
        return [-1]

    new_array = unique(new_array)
    new_array.sort()
    if new_array.max() > 86 or new_array.min() < 1:
        failed = True
    if failed:
        return [-1]
    return new_array

