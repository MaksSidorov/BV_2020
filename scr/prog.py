import sys
import pandas as pd
import csv
from PyQt5 import QtGui, QtCore
from PyQt5 import QtWidgets
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from functions import *


class Prog(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(0, 0, 1000, 700)
        self.setWindowTitle('Износ валков')
        self.tableWidget = QTableWidget(self)
        self.tableWidget.resize(300, 450)
        self.tableWidget.move(50, 20)
        self.tableWidget.setColumnCount(2)
        self.tableWidget.setHorizontalHeaderLabels(['id валка', 'Полученный износ'])
        self.tableWidget.resizeColumnsToContents()
        self.btn = QPushButton('Выбрать файл', self)
        self.btn.move(750, 20)
        self.btn.resize(200, 50)
        self.btn.clicked.connect(self.run)

    def run(self):
        fname = QFileDialog.getOpenFileName(self, 'Выбрать файл',
                                            '', "CSV файл(*.csv)")[0]
        result = make_predict(pd.read_csv(fname))
        self.tableWidget.clear()
        self.tableWidget.setColumnCount(2)
        self.tableWidget.setHorizontalHeaderLabels(['id валка', 'Полученный износ'])
        self.tableWidget.setRowCount(0)
        self.tableWidget.resize(300, 450)
        result.sort(key=lambda x: x[1], reverse=True)
        for i, row in enumerate(result):
            self.tableWidget.setRowCount(self.tableWidget.rowCount() + 1)
            for j, elem in enumerate(row):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(elem)))
        self.tableWidget.resizeColumnsToContents()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    prog = Prog()
    prog.show()
    sys.exit(app.exec())
