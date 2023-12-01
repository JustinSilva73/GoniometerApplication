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

def get_file_paths(self):
        try:
            with open('imported_files.txt', 'r') as file:
                return [line.strip() for line in file if line.strip()]
        except FileNotFoundError:
            print("imported_files.txt not found.")
            return []

def handle_start_button_click(run_options_dialog):
    # Determine the run type based on the selected radio button
    run_type_str = None
    if run_options_dialog.ui.radioButtonSteps.isChecked():
        run_type_str = 'Steps'
    elif run_options_dialog.ui.radioButtonFiles.isChecked():
        run_type_str = 'Files'
    elif run_options_dialog.ui.radioButtonAxisControl.isChecked():
        run_type_str = 'Axis Control'

    if run_type_str is None:
        QtWidgets.QMessageBox.warning(run_options_dialog, "Warning", "Please select a run type.")
        return

    log_display = run_options_dialog.parent().logDisplay
    log_display.appendPlainText(f"Mode selected: {run_type_str}")

    # Retrieve selected files if 'Files' run type is selected
    selected_files = run_options_dialog.selectedFilePaths if run_type_str == 'Files' else None

    run_manager.start_run_type(run_type_str, log_display, run_options_dialog, selected_files)

        
    
class RunOptionsDialog(QtWidgets.QDialog):
    def __init__(self, parent=None, importedFiles=None):
        super(RunOptionsDialog, self).__init__(parent)
        self.ui = Ui_RunOptionsDialog()
        self.ui.setupUi(self)
        self.applyStylingRunOptions()
        self.ui.pushButtonStart.clicked.connect(lambda: handle_start_button_click(self))
        self.selectedFilePaths = []  
        self.importedFiles = importedFiles  # Store the imported files


    def handleFileSelectionChanged(self, item):
        print("handleFileSelectionChanged called")
        file_name = item.text()
        print(f"File name from item: {file_name}")

        file_path_found = False
        for file_path in self.importedFiles:
            if QtCore.QFileInfo(file_path).fileName() == file_name:
                file_path_found = True
                if item.checkState() == QtCore.Qt.Checked:
                    print(f"Selected file path: {file_path}")
                    if file_path not in self.selectedFilePaths:
                        self.selectedFilePaths.append(file_path)
                        print(f"Added to selectedFilePaths: {file_path}")
                elif item.checkState() == QtCore.Qt.Unchecked:
                    if file_path in self.selectedFilePaths:
                        self.selectedFilePaths.remove(file_path)
                        print(f"Removed from selectedFilePaths: {file_path}")
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
        self.importedFiles = []  # This will store the file paths
        self.load_file_paths()
        self.populate_file_management_list()
        self.setFocusPolicy(Qt.StrongFocus)
        logo_image = QPixmap('Assets/Logo.jpg')

        # Set the pixmap to the existing logoLabel
        # Assuming 'logo_image' is a QPixmap object
        scaled_logo = logo_image.scaled(self.logoLabel.width(), self.logoLabel.height(), QtCore.Qt.KeepAspectRatio)
        self.logoLabel.setPixmap(scaled_logo)
        # Get the screen resolution
        screen = QtWidgets.QApplication.primaryScreen()
        rect = screen.availableGeometry()

        # Calculate half the screen size and convert them to integers
        width = int(rect.width() * 0.5)
        height = int(rect.height() * 0.5)

        # Set the window size
        self.resize(width, height)

        # Optionally center the window
        self.move(rect.center() - self.rect().center())
        screen_height = self.screen().size().height()
        font_size = screen_height * 0.02  # Example: 2% of screen height
        self.runButton.clicked.connect(self.show_run_options)
        self.importButton.clicked.connect(self.import_csv_files)
        self.stopButton.clicked.connect(self.handle_stop_button_click)  # Assuming you have a stopButton



    def keyPressEvent(self, event):
        current_run_type = run_manager.get_run_type()
        if hasattr(current_run_type, 'run_type_id') and current_run_type.run_type_id == 'Axis Control':
            if not run_manager.ser or not run_manager.ser.isOpen():
                print("Serial connection not open. Please press Start.")
                return

            if event.key() == QtCore.Qt.Key_Left:
                print("key pressed left")
                current_run_type.adjust_angle(-10)
            elif event.key() == QtCore.Qt.Key_Right:
                print("key pressed right")
                current_run_type.adjust_angle(10)



    def populate_file_management_list(self):
        self.fileList.clear()
        for file_path in self.importedFiles:
            file_name = QtCore.QFileInfo(file_path).fileName()
            list_widget_item = QtWidgets.QListWidgetItem(file_name)
            list_widget_item.setData(QtCore.Qt.UserRole, file_path)

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
            remove_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))  # Changes the cursor to a pointer
            remove_button.clicked.connect(lambda checked, i=list_widget_item: self.remove_file(i))

            file_layout.addWidget(remove_button, 0)  # The 0 here ensures that the button does not expand

            file_widget.setLayout(file_layout)
            list_widget_item.setSizeHint(file_widget.sizeHint())
            self.fileList.addItem(list_widget_item)
            self.fileList.setItemWidget(list_widget_item, file_widget)
        


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
        if hasattr(self, 'run_options_dialog'):
            self.run_options_dialog.ui.fileListWidget.clear()
            for file_path in self.importedFiles:
                item = QtWidgets.QListWidgetItem(QtCore.QFileInfo(file_path).fileName())
                item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
                item.setCheckState(QtCore.Qt.Unchecked)
                self.run_options_dialog.ui.fileListWidget.addItem(item)


    def save_file_paths(self):
        try:
            with open('imported_files.txt', 'w') as f:
                for file_path in self.importedFiles:
                    f.write(f"{file_path}\n")
            print("File paths saved successfully.")
        except Exception as e:
            print("Error saving file paths:", e)



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

    def load_file_paths(self):
        try:
            with open('imported_files.txt', 'r') as f:
                self.importedFiles = [line.strip() for line in f.readlines()]
        except FileNotFoundError:
            print("No previously imported files found.")

    def show_run_options(self):
        if hasattr(self, 'run_options_dialog'):
            self.run_options_dialog.ui.fileListWidget.itemChanged.disconnect()
        self.run_options_dialog = RunOptionsDialog(self, self.importedFiles)
        self.run_options_dialog.ui.fileListWidget.clear()

        for file_path in self.importedFiles:
            item = QtWidgets.QListWidgetItem(QtCore.QFileInfo(file_path).fileName())
            item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
            item.setCheckState(QtCore.Qt.Unchecked)
            self.run_options_dialog.ui.fileListWidget.addItem(item)
            # Connect the itemChanged signal to handleFileSelectionChanged
            self.run_options_dialog.ui.fileListWidget.itemChanged.connect(self.run_options_dialog.handleFileSelectionChanged)
        self.run_options_dialog.show()

    def handle_stop_button_click(self):
        run_manager.close_serial_connection()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = ControlPanelApp()
    mainWindow.show()
    sys.exit(app.exec_())




    #self.fileListWidget = QtWidgets.QListWidget(self.groupBoxFiles)
    #self.fileListWidget.setObjectName("fileListWidget")
    #self.verticalLayoutFiles.addWidget(self.fileListWidget)