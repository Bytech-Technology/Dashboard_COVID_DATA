from PyQt5 import QtCore
from PyQt5.QtCore import Qt
import pandas as pd

class PandasModel(QtCore.QAbstractTableModel):
    def __init__(self, df=pd.DataFrame(), parent=None):
        super().__init__(parent)
        self._df = df.copy()

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            return str(self._df.columns[section])
        else:
            return str(self._df.index[section])

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        value = self._df.iloc[index.row(), index.column()]
        if role == Qt.DisplayRole:
            return str(value)
        if role == Qt.TextAlignmentRole:
            return int(Qt.AlignCenter | Qt.AlignVCenter)
        
        return None

    def rowCount(self, parent=None):
        return len(self._df.index)

    def columnCount(self, parent=None):
        return len(self._df.columns)
