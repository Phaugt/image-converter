import pathlib
from PyQt5 import uic
from easysettings import EasySettings
from PyQt5.QtWidgets import (QApplication, qApp, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QFileDialog, QMainWindow,
                            QMessageBox, QWidget, QMenuBar, QStatusBar, QAction, QRadioButton)
from PyQt5.QtCore import QFile , Qt
from PyQt5.QtGui import QIcon, QPixmap
import sys, os, subprocess
from pathlib import Path
from PIL import Image


def resource_path(relative_path):
    """used by pyinstaller to see the relative path"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath('.'), relative_path)

guifile = resource_path("./gui/main.ui")
logo = resource_path("./gui/logo.png")
userfold = str(pathlib.Path.home())
config = EasySettings(userfold+"/imageconverter.conf")
configGui = resource_path("./gui/config.ui")

try:
    saveLocation = config.get("saveLocation")
    saveAs = config.get("saveFormat")
    if saveLocation or saveAs == "":
        saveLocation = userfold+'/Pictures/'
        config.set("saveLocation", str(saveLocation))
        config.set("saveFormat", 'jpeg')
        config.save()
except FileNotFoundError:
    pass

class GUI(QMainWindow):
    """main window used by the application"""
    def __init__(self):
        super(GUI, self).__init__()
        UIFile = QFile(guifile)
        UIFile.open(QFile.ReadOnly)
        uic.loadUi(UIFile, self)
        UIFile.close()

        self.c = Config()
        self.c.reloadSettings()

        self.setAcceptDrops(True)

        self.image.setAlignment(Qt.AlignCenter)
        self.image.setText('\n\n Drop image file here! \n\n')
        self.image.setStyleSheet('''
            QLabel{
                border: 4px dashed #aaa;
            }
            ''')
        self.btnconvertImage.clicked.connect(self.convertImage)
        self.btnselectImage.clicked.connect(self.selectImageFile)
        self.btnopenFolder.clicked.connect(self.openSavedFolder)

        
        self.actSetting.triggered.connect(self.showSettings)
        self.actAbout.triggered.connect(self.showAbout)
        
        self.actExit.triggered.connect(qApp.quit)

        menubar = self.menuBar()
        menubar.setNativeMenuBar(False)

    def informationMessage(self,message):
        """send message to messagebox"""
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Warning)
        msgBox.setText(message)
        msgBox.exec()
        
    def showSettings(self):
        """call the settings widget"""
        self.c.show()

    def showAbout(self):
        """show information in a qmsbox"""
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Information)
        text1 = '.image converter converts the most image formats to .jpeg format.'
        text2 = 'the program is made by: \nPatrik Hauguth\nhttps://github.com/Phaugt'
        msgBox.setText(text1+'\n'+'\n'+text2)
        msgBox.exec()

    def dragEnterEvent(self, event):
        """accept the drag to window if it contains an image"""
        if event.mimeData().hasImage:
            event.accept()
        else:
            event.ignore()
 
    def dragMoveEvent(self, event):
        """accept the drag to window if it contains an image"""
        if event.mimeData().hasImage:
            event.accept()
        else:
            event.ignore()
 
    def dropEvent(self, event):
        """accept image when dropped into window"""
        if event.mimeData().hasImage:
            event.setDropAction(Qt.CopyAction)
            file_path = event.mimeData().urls()[0].toLocalFile()
            self.set_image(file_path)
            self.folderLocation.setText(file_path)
 
            event.accept()
        else:
            event.ignore()
 
    def set_image(self, file_path):
        """set the image as pixmap in the label and scale it """
        pixmap = QPixmap(file_path)
        scaled = pixmap.scaled(631,390,Qt.KeepAspectRatio)
        self.image.setPixmap(scaled)


    def convertImage(self):
        """convert the image to specified format and location """
        saveAs = config.get("saveFormat")
        saveLocation = config.get("saveLocation")
        fileExt = str(Path(self.folderLocation.text()).suffix)
        try:
            if fileExt.upper() == '.HEIC':
                fileName = str(Path(self.folderLocation.text()))
                newName = str(Path(self.folderLocation.text()).stem)
                saveAsNew = saveLocation+newName+".jpeg"
                script = 'sips -s format jpeg '+"'"+str(fileName)+"'"+' --out '+"'"+str(saveAsNew)+"'"
                os.system(script)
            else:
                image = Image.open(self.folderLocation.text())
                fileName = str(Path(self.folderLocation.text()).stem)
                image = image.convert('RGB')
                image.save(saveLocation+fileName+"."+saveAs, saveAs)
        except Exception:
            self.informationMessage("Image could not be converted to .jpeg!")
            
    def selectImageFile(self):
        """if user does not want to drag and drop file"""
        fileName = QFileDialog.getOpenFileName()
        if fileName:
            self.set_image(fileName[0])
            self.folderLocation.setText(fileName[0])

    
    def openSavedFolder(self):
        """open the folder where the output is saved"""
        sfl = config.get("saveLocation")
        subprocess.check_call(['open', '--', sfl])

class Config(QWidget):
    """Config window - called from menubar"""
    def __init__(self):
        super().__init__()
        UIFile = QFile(configGui)
        UIFile.open(QFile.ReadOnly)
        uic.loadUi(UIFile, self)
        UIFile.close()

        self.newFolderPath.setText(config.get("saveLocation"))
        self.saveExit.clicked.connect(self.saveExitConfig)
        self.save.clicked.connect(self.saveConfig)
        self.changeOutputFolder.clicked.connect(self.changeSavedFolder)

        self.formatJpeg.toggled.connect(self.pickSaveFormat)
    
    def reloadSettings(self):
        """reload settings"""
        try:
            saveLocation = config.get("saveLocation")
            saveAs = config.get("saveFormat")
            if saveAs == 'jpeg':
                self.formatJpeg.setChecked(True)
            else:
                pass
        except FileNotFoundError:
            pass

    def saveConfig(self):
        """save the current settings to config"""
        newPath = self.newFolderPath.text()
        config.set("saveLocation", str(newPath))
        config.save()
        self.reloadSettings()

    def pickSaveFormat(self):
        """save choice from radio button into config"""
        try:
            if self.formatJpeg.isChecked():
                config.set("saveFormat",'jpeg')
                config.save()
            else:
                pass
        except Exception:
            pass


    def saveExitConfig(self):
        """save the current settings to config and exit"""
        newPath = self.newFolderPath.text()
        config.set("saveLocation", str(newPath))
        config.save()
        self.reloadSettings()
        self.close()

    def changeSavedFolder(self):
        """change the folder for the output"""
        sfl = QFileDialog()
        sfl.setFileMode(QFileDialog.Directory)
        foldName = sfl.getExistingDirectory()
        fixfoldName = foldName + "/"
        if fixfoldName:
            self.newFolderPath.setText(fixfoldName)

app = QApplication(sys.argv)
app.setWindowIcon(QIcon(logo))
window = GUI()
window.show()
app.exec_()
