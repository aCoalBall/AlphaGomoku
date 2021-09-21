from gomoku import *
from PyQt5.QtWidgets import *
import sys
from GUI import *
import os



def main() :
    os.chdir(os.path.abspath(os.path.dirname(sys.argv[0])))
    app = QApplication(sys.argv)
    ex = GomokuWindow()
    sys.exit(app.exec_())


if __name__ == '__main__' :
    main()