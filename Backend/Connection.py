import sys
import serial
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMessageBox

class StartingRunChecks:
    def __init__(self, log_display_widget, com_port, baud_rate):
        self.log_display = log_display_widget
        self.com_port = com_port
        self.baud_rate = baud_rate

    def check_serial_connection(self):
        try:
            with serial.Serial(self.com_port, self.baud_rate, timeout=1) as ser:
                if ser.isOpen():
                    self.log_display.appendPlainText(f"Connected successfully to {self.com_port} at {self.baud_rate} baud.")
                    return True
                else:
                    self.log_display.appendPlainText(f"Failed to open serial port {self.com_port}.")
                    return False
        except serial.SerialException as e:
            # Handle the exception and append to logDisplay
            self.log_display.appendPlainText(f"Serial connection failed: {e}")
            QtWidgets.QMessageBox.critical(None, "Serial Connection Error", f"Could not open serial port {self.com_port}: {e}")