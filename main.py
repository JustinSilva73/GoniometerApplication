#Purpose: Holds a lot of the main functions of the Control Panel and the Run Options panel plus the run thread

import sys

# Assuming your main.py is in a directory that has Backend and Frontend as subdirectories
sys.path.append('./Backend')
sys.path.append('./Frontend')

from PyQt5 import QtWidgets, QtCore, QtGui
from ControlPanel import Ui_ControlPanelWindow
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QLineEdit, QMainWindow, QLabel
from RunPopUp import Ui_RunOptionsDialog
from ModeRun import run_manager  
from PyQt5.QtGui import QPixmap
from Connection import StartingRunChecks
from UserTextUpdate import log_signal, angle_text
from PyQt5.QtCore import QThread, pyqtSignal

#This is for grabbing those files from the imported_files.txt file that holds all the paths for past imported files
def get_file_paths(self):
        try:
            with open('imported_files.txt', 'r') as file:
                return [line.strip() for line in file if line.strip()]
        except FileNotFoundError:
            print("imported_files.txt not found.")
            return []

#The start button in the run options dialog that will start the run thread for any mode 
def handle_start_button_click(run_options_dialog, control_panel_app):
    run_type_str = None
    if run_options_dialog.ui.radioButtonSteps.isChecked():
        run_type_str = 'Steps'
    elif run_options_dialog.ui.radioButtonFiles.isChecked():
        run_type_str = 'Files'
    elif run_options_dialog.ui.radioButtonAxisControl.isChecked():
        run_type_str = 'Axis Control'
    elif run_options_dialog.ui.radioButtonIndefinite.isChecked():
        run_type_str = 'Indefinite'

    if run_type_str is None:
        QtWidgets.QMessageBox.warning(run_options_dialog, "Warning", "Please select a run type.")
        return
    
    #Grabs the needed parts and connects the log + angle to check if run thread aloready running
    log_display = control_panel_app.logDisplay
    selected_files = run_options_dialog.selectedFilePaths
    steps = int(run_options_dialog.ui.lineEditSteps.text())
    offset = int(run_options_dialog.ui.lineEditOffset.text())
    if not control_panel_app.run_thread or not run_manager.runCheck:
        run_thread = RunThread(run_manager, run_type_str, log_display, run_options_dialog, selected_files, steps, offset)
        control_panel_app.run_thread = run_thread
        run_options_dialog.close()
        run_thread.run()
        
    
    else:
        QtWidgets.QMessageBox.warning(run_options_dialog, "Warning", "Another process is already running.")

      
from PyQt5.QtCore import QThread

#The run thread that will run the mode selected in the run options dialog
class RunThread(QThread):    
    axis_control_signal = pyqtSignal(int)
    
    def __init__(self, run_manager, run_type_str, log_display, run_options_dialog, selected_files, steps, offset):
        super().__init__()
        self.run_manager = run_manager
        self.run_type_str = run_type_str
        self.log_display = log_display
        self.run_options_dialog = run_options_dialog
        self.selected_files = selected_files
        self.steps = steps
        self.offset = offset
        self.axis_control_signal.connect(self.run_manager.axis_control)

    #Runs the mode selected in the run options dialog
    def run(self):
        if not self.run_manager.isCalibrated():
            QtWidgets.QMessageBox.warning(self.run_options_dialog, "Warning", "Motors need calibration.")
            run_manager.runCheck = False
            return
        run_manager.runCheck = True
        self.run_manager.start_run_type(self.run_type_str, self.log_display, self.run_options_dialog, self.selected_files, self.steps, self.offset)
        run_manager.runCheck = False



class RunOptionsDialog(QtWidgets.QDialog):
    def __init__(self, control_panel_app, parent=None, importedFiles=None):
        super(RunOptionsDialog, self).__init__(parent)  # Ensure parent is QWidget or None
        self.ui = Ui_RunOptionsDialog()
        self.ui.setupUi(self)
        self.applyStylingRunOptions()
        self.control_panel_app = control_panel_app  # Reference to ControlPanelApp
        self.selectedFilePaths = []  
        self.importedFiles = importedFiles  # Store the imported files
        print("Run Options Dialog initialized.")
        self.ui.checkBoxAllFiles.stateChanged.connect(self.toggle_all_files_selection)
        
    #Initializes the file list in the run options dialog when launch
    def initialize_file_list(self):
        self.ui.fileListWidget.clear()  # Clear the list initially
        for file_path in self.importedFiles:
            item = QtWidgets.QListWidgetItem(QtCore.QFileInfo(file_path).fileName())
            item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
            item.setCheckState(QtCore.Qt.Unchecked)
            self.ui.fileListWidget.addItem(item)
        self.ui.fileListWidget.itemChanged.connect(self.handleFileSelectionChanged)

    #Toggles all files in the file list in the run options dialog
    def toggle_all_files_selection(self, state):
        all_checked = state == QtCore.Qt.Checked
        for index in range(self.ui.fileListWidget.count()):
            item = self.ui.fileListWidget.item(index)
            item.setCheckState(QtCore.Qt.Checked if all_checked else QtCore.Qt.Unchecked)

    #Handles the file selection in the file list in the run options dialog
    def handleFileSelectionChanged(self, item):
        file_name = item.text()
        file_path_found = False
        for file_path in self.importedFiles:
            if QtCore.QFileInfo(file_path).fileName() == file_name:
                file_path_found = True
                if item.checkState() == QtCore.Qt.Checked:
                    if file_path not in self.selectedFilePaths:
                        self.selectedFilePaths.append(file_path)
                elif item.checkState() == QtCore.Qt.Unchecked:
                    if file_path in self.selectedFilePaths:
                        self.selectedFilePaths.remove(file_path)
                break
        if not file_path_found:
            print(f"No matching file path found for: {file_name}")

    def applyStylingRunOptions(self):
        try:
            with open('Frontend/RunPopUpStyle.css', 'r') as f:
                style = f.read()
                self.setStyleSheet(style)
                print("Stylesheet applied successfully.")
        except Exception as e:
            print("Error applying stylesheet:", e)
    

class ControlPanelApp(QtWidgets.QWidget, Ui_ControlPanelWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.applyStyling()
        self.importedFiles = []
        self.load_file_paths()
        self.populate_file_management_list()
        self.setFocusPolicy(Qt.StrongFocus)
        self.run_thread = None  # Initialize to None to avoid multiple thread instances
        self.run_options_dialog = None  # Initialize to None to manage single instance
        print("Control Panel App initialized.")
        logo_image = QPixmap('Assets/Logo.jpg')
        scaled_logo = logo_image.scaled(self.logoLabel.width(), self.logoLabel.height(), QtCore.Qt.KeepAspectRatio)
        self.logoLabel.setPixmap(scaled_logo)
        screen = QtWidgets.QApplication.primaryScreen()
        rect = screen.availableGeometry()
        self.resize(int(rect.width() * 0.55), int(rect.height() * 0.5))
        self.move(rect.center() - self.rect().center())

        self.runButton.clicked.connect(self.show_run_options)
        self.importButton.clicked.connect(self.import_csv_files)
        self.stopButton.clicked.connect(self.handle_stop_button_click)
        self.pauseButton.clicked.connect(self.handle_pause_button_click)
        self.calButton.clicked.connect(self.handle_calibrate_button_click)
        self.homeButton.clicked.connect(self.handle_home_button_click)
        self.fileList.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.fileList.setAcceptDrops(True)
        self.fileList.setDragEnabled(True)
        self.fileList.setDefaultDropAction(QtCore.Qt.MoveAction)
        self.fileList.model().rowsMoved.connect(self.onRowsMoved)

        #Attaches the log and angle text to the log signal and angle text signal
        log_signal.append_log.connect(self.append_to_log_display)
        angle_text.append_angle.connect(self.append_to_angle_display)


    def append_to_log_display(self, message):
        try:
            self.logDisplay.appendPlainText(message)
        except Exception as e:
            # Log the error or show a message box
            print(f"Error updating log display: {str(e)}")

    def append_to_angle_display(self, message):
        try:
            self.pitchEdit.setText(message)
        except Exception as e:
            # Log the error or show a message box
            print(f"Error updating angle display: {str(e)}")


    #Axis Control Key press left and right arrow
    def keyPressEvent(self, event):
        if event.key() != QtCore.Qt.Key_Left and event.key() != QtCore.Qt.Key_Right:
            return 
        if event.key() == QtCore.Qt.Key_Left:
            print("key pressed left")
            self.run_thread.axis_control_signal.emit(-5)
        elif event.key() == QtCore.Qt.Key_Right:
            print("key pressed right")
            self.run_thread.axis_control_signal.emit(5)


    #Populates the file management list in the control panel
    def populate_file_management_list(self):
        self.fileList.clear()
        for file_path in self.importedFiles:
            file_name = QtCore.QFileInfo(file_path).fileName()
            list_widget_item = QtWidgets.QListWidgetItem(file_name)
            list_widget_item.setData(QtCore.Qt.UserRole, file_path)
            self.fileList.addItem(list_widget_item)

            # Create the widget to display the file name and remove button
            file_widget = QtWidgets.QWidget()
            file_layout = QtWidgets.QHBoxLayout(file_widget)
            file_layout.setContentsMargins(10, 10, 10, 10)

            # Create and add the label for the file name
            label = QtWidgets.QLabel(file_name)
            file_layout.addWidget(label, 1)

            # Create and add the 'X' button
            remove_button = QtWidgets.QPushButton()
            remove_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            remove_button.setObjectName("removeButton")
            remove_button.setText("✕")
            remove_button.setFlat(True)
            remove_button.clicked.connect(lambda checked, item=list_widget_item: self.remove_file(item))

            file_layout.addWidget(remove_button, 0)

            file_widget.setLayout(file_layout)
            list_widget_item.setSizeHint(file_widget.sizeHint())

            # Add the list item and its associated widget to the file list
            self.fileList.addItem(list_widget_item)
            self.fileList.setItemWidget(list_widget_item, file_widget)

           
    #Imports the CSV files into the control panel       
    def import_csv_files(self):
        # Open file dialog to select CSV files
        options = QtWidgets.QFileDialog.Options()
        files, _ = QtWidgets.QFileDialog.getOpenFileNames(
            self, 
            "Import CSV files", 
            "", 
            "CSV Files (*.csv)", 
            options=options
        )
        for file in files:
            # Assuming this is part of a function within your UI class
            self.importedFiles.append(file)  # Add the full path to the list

            file_name = QtCore.QFileInfo(file).fileName()
            list_widget_item = QtWidgets.QListWidgetItem(self.fileList)

            file_widget = QtWidgets.QWidget()
            file_layout = QtWidgets.QHBoxLayout(file_widget)
            file_layout.setContentsMargins(10, 10, 10, 10)  # Add some padding

            # Create and add the label for the file name
            label = QtWidgets.QLabel(file_name)
            file_layout.addWidget(label, 1)  # The 1 ensures the label takes up the available space, pushing the button right

            # Create and add the 'X' button
            remove_button = QtWidgets.QPushButton()
            remove_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))  # Changes the cursor to a pointer
            remove_button.setObjectName("removeButton")
            remove_button.setText("✕")  # Unicode character for multiplication sign (commonly used as close or remove button)
            remove_button.setFlat(True)  # This will remove the button styling
            remove_button.clicked.connect(lambda checked, i=list_widget_item: self.remove_file(i))

            file_layout.addWidget(remove_button, 0)  # The 0 here ensures that the button does not expand

            file_widget.setLayout(file_layout)
            list_widget_item.setSizeHint(file_widget.sizeHint())
            self.fileList.addItem(list_widget_item)
            self.fileList.setItemWidget(list_widget_item, file_widget)
        
        self.save_file_paths()

    #Removes the file from the control panel with the X button
    def remove_file(self, item):
        # Get the file name from the item
        file_name = self.fileList.itemWidget(item).findChild(QtWidgets.QLabel).text()

        # Remove the item from the QListWidget
        row = self.fileList.row(item)
        self.fileList.takeItem(row)

        # Find and remove the file path from the importedFiles list
        for file_path in self.importedFiles:
            if QtCore.QFileInfo(file_path).fileName() == file_name:
                self.importedFiles.remove(file_path)
                break

        # Update the imported_files.txt file
        self.save_file_paths()

        # If the run options dialog is open, update its file list
        if self.run_options_dialog and hasattr(self.run_options_dialog, 'ui'):
            self.run_options_dialog.ui.fileListWidget.clear()
            for file_path in self.importedFiles:
                item = QtWidgets.QListWidgetItem(QtCore.QFileInfo(file_path).fileName())
                item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
                item.setCheckState(QtCore.Qt.Unchecked)
                self.run_options_dialog.ui.fileListWidget.addItem(item)


    #Saves the file paths to the imported_files.txt file
    def save_file_paths(self):
        try:
            with open('imported_files.txt', 'w') as f:
                for file_path in self.importedFiles:
                    f.write(f"{file_path}\n")
            print("File paths saved successfully.")
        except Exception as e:
            print("Error saving file paths:", e)


    #Applies the styling to the control panel
    def applyStyling(self):
        try:
            with open('Frontend/MainPageStyle.css', 'r') as f:
                style = f.read()
                self.setStyleSheet(style)
                print("Stylesheet applied successfully.")  # Debugging line
        except Exception as e:
            print("Error applying stylesheet:", e)

    
    def closeEvent(self, event):
        self.save_file_paths()
        super().closeEvent(event)

    #Loads the file paths from the imported_files.txt file
    def load_file_paths(self):
        try:
            with open('imported_files.txt', 'r') as f:
                self.importedFiles = [line.strip() for line in f.readlines()]
        except FileNotFoundError:
            print("No previously imported files found.")

    #Shows the run options dialog when run pressed on control panel
    def show_run_options(self):
        if not self.run_options_dialog:
            self.run_options_dialog = RunOptionsDialog(control_panel_app=self, parent=self, importedFiles=self.importedFiles)
            self.run_options_dialog.ui.pushButtonStart.clicked.connect(
                lambda: handle_start_button_click(self.run_options_dialog, self)
            )
        self.run_options_dialog.ui.fileListWidget.clear()  # Clear the existing items first
        for file_path in self.importedFiles:
            item = QtWidgets.QListWidgetItem(QtCore.QFileInfo(file_path).fileName())
            item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
            item.setCheckState(QtCore.Qt.Unchecked)
            self.run_options_dialog.ui.fileListWidget.addItem(item)
        self.run_options_dialog.ui.fileListWidget.itemChanged.connect(self.run_options_dialog.handleFileSelectionChanged)
        self.run_options_dialog.show()

    #Handles the pause button click
    def handle_pause_button_click(self):
        if not run_manager.pause:
            run_manager.pause = True
            self.pauseButton.setText("Resume")
        else:
            run_manager.pause = False
            self.pauseButton.setText("Pause")

    #Handles the stop button click
    def handle_stop_button_click(self):
        if self.run_thread and run_manager.runCheck:
            run_manager.runCheck = False

            log_signal.append_log.emit("Run stopped.")
            self.run_thread.terminate()  # Safely handle thread termination
        
        else:
            log_signal.append_log.emit("Run stopped.")
            run_manager.stop_run()
    
    #Handles the calibrate button click
    def handle_calibrate_button_click(self):
        run_manager.calibrateMotors()

    #Handles the home button click
    def handle_home_button_click(self):
        run_manager.homeMotors()

    #Handles the rows moved in the file list
    def onRowsMoved(self, parent, start, end, destination, row):
        moved_items = self.importedFiles[start:end+1]
        del self.importedFiles[start:end+1]
        if row < start:
            for item in reversed(moved_items):
                self.importedFiles.insert(row, item)
        else:
            for item in moved_items:
                self.importedFiles.insert(row, item)
        self.save_file_paths()


    #Updates the imported files order when rows are moved in the file list
    def updateImportedFilesOrder(self):
        self.importedFiles = []
        for index in range(self.fileList.count()):
            item = self.fileList.item(index)
            file_path = item.data(QtCore.Qt.UserRole)
            if file_path is None:
                print(f"Error: No file path found for item at index {index}. This should not happen.")
            else:
                self.importedFiles.append(file_path)
        self.save_file_paths()
        print(f"Updated file paths: {self.importedFiles}")



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = ControlPanelApp()
    mainWindow.show()
    sys.exit(app.exec_())




    #ALL OF THIS IS PUT INTO RUNPOPUP.PY
    #When it wipes it loses these necessary lines 
    #The three below can go at the bottom of 

    #self.fileListWidget = QtWidgets.QListWidget(self.groupBoxFiles)
    #self.fileListWidget.setObjectName("fileListWidget")
    #self.verticalLayoutFiles.addWidget(self.fileListWidget)
    

    #in place of QLineEdit in runpupup dialog for Offset
    #self.lineEditOffset = QtWidgets.QLineEdit(RunOptionsDialog)
    #self.lineEditOffset.setAlignment(QtCore.Qt.AlignCenter)
    #self.lineEditOffset.setValidator(QtGui.QIntValidator())  # Correctly instantiate the QIntValidator
    #self.lineEditOffset.setObjectName("lineEditOffset")
    # ... rest of your code ...

    #in place of QLineEdit in runpupup dialog for Steps
    #self.lineEditSteps = QtWidgets.QLineEdit(RunOptionsDialog)
    #self.lineEditSteps.setAlignment(QtCore.Qt.AlignCenter)
    #self.lineEditSteps.setValidator(QtGui.QIntValidator())  # Correctly instantiate the QIntValidator
    #self.lineEditSteps.setObjectName("lineEditSteps")

