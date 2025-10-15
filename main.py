import sys
from PyQt5 import QtWidgets
from utils.helpers import load_data, CSV_PATH
from ui.window import BentoWindow

if __name__ == '__main__':
    path = CSV_PATH
    if len(sys.argv) > 1:
        path = sys.argv[1]
    df = load_data(path)
    app = QtWidgets.QApplication(sys.argv)
    win = BentoWindow(df)
    win.show()
    sys.exit(app.exec_())
