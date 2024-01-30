import serial
from dotenv import load_dotenv
import os
import sys

load_dotenv()
comPort = os.getenv("comPort")
baudRate = os.getenv("baudRate")

class Calibration:
    def __init__(self):
        self.center_reference = None
        self.side_limits = None

    def run_calibration(self):
        self.center_reference = self.get_center_reference_from_arduino()
        self.side_limits = self.get_side_limits_from_arduino()

    def get_center_reference_from_arduino(self):
        
        if not self.check_serial_connection():
            command = f"get_center_reference\n"
            arduino = serial.Serial(comPort, baudRate, timeout=1)
            arduino.write(command.encode())
            self.center_reference = arduino.readline().decode().strip()
            print(f"Center reference: {self.center_reference}")
        else:
            print("Serial connection already open")
        arduino.close()

    def get_side_limits_from_arduino(self):
        if not self.check_serial_connection():
            command = f"get_side_limits\n"
            arduino = serial.Serial(comPort, baudRate, timeout=1)
            arduino.write(command.encode())
            side_limits_str = arduino.readline().decode().strip()
            left_limit, right_limit = map(int, side_limits_str.split())
            self.side_limits = (left_limit, right_limit)
            print(f"Side limits: {self.side_limits}")
        else:
            print("Serial connection already open")
        arduino.close()
