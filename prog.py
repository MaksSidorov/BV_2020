import sys
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
        self.btn.resize(200 ,50)
        self.btn.clicked.connect(self.run)

    def run(self):
        fname = QFileDialog.getOpenFileName(self, 'Выбрать файл',
                                            '', "Excel файл(*.xlsx)")[0]
        data = make_data(fname)
        result = make_predict(data)


            



if __name__ == '__main__':
    app = QApplication(sys.argv)
    prog = Prog()
    prog.show()
    sys.exit(app.exec())