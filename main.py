from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog
from PyQt5 import uic , QtCore
from PyQt5.QtCore import Qt, QTimer
import sys
import icons.icons_rc
from os.path import expanduser
import ntpath
# import rag file
from rag_sys import RAGSystem

class Rag(QMainWindow):
    def __init__(self):
        super(Rag, self).__init__()
        uic.loadUi('./Ui.ui', self)

        # remove windows title bar
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)

        # set main background transparent
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # button clicks on top bar
        # minimize window
        self.btnMinus.clicked.connect(self.showMinimized)
        # Close window
        self.btnClose.clicked.connect(self.close)

        # upload btn func
        self.btnSelect.clicked.connect(self.upload)
        self.btnStart.clicked.connect(self.RunRag)

        self.file = ''

    def path_leaf(self,path):
        head, tail = ntpath.split(path)
        return tail or ntpath.basename(head)

    def upload(self):
        try:
            # Create custom QFileDialog
            dialog = QFileDialog.getOpenFileNames(self, caption='Select PDF files', directory = expanduser("~"), filter='PDF File (*.pdf)')
            # Show dialog and get selected file
            filenames = [self.path_leaf(path) for path in dialog[0]]
            if len(dialog[0]) > 0:
                self.file = dialog[0]
                self.lblFile.setText(',,,'.join(filenames))
            else:
                self.file = ''
                self.lblFile = ''
        except Exception as e:
            print(e)


    def RunRag(self):
        try:
            filePaths = self.file
            if len(filePaths) > 0 and self.txtPrompt.text() != '':
                 self.txtResult.setText('')
                 self.txtResult.setText('App is running please wait for the answer')
                 QTimer.singleShot(1000, lambda: self.GetResult(filePaths))

            else:
                self.txtResult.setText("Select The PDF file and Fill the Prompt box")
        except Exception as e:
            print(e)

    def GetResult(self,path):
        try:
            rag_system = RAGSystem(file_path=path)
            result = rag_system.ask(self.txtPrompt.text())
            self.txtResult.setText(result["answer"])
        except Exception as e:
            print(e)

    # main window drag funcs
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.offset = event.pos()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.offset is not None and event.buttons() == QtCore.Qt.LeftButton:
            self.move(self.pos() + event.pos() - self.offset)
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.offset = None
        super().mouseReleaseEvent(event)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    UIWindow = Rag()
    UIWindow.show()
    app.exec_()