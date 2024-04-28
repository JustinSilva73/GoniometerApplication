# Purpose: This file is used to create signals for updating the user interface. This file is used to update the angle text and the log text in the user interface.
# Its just more efficient instead of passing the instance around expecially with the thread too
# Import these where needing to output to log or the angle which is only set up for pitch at the moment
# Some areas from earlier on before threading might still be passing in the log instance so those could be cleaned up but they do still work

from PyQt5 import QtCore

class LogSignal(QtCore.QObject):
    append_log = QtCore.pyqtSignal(str)
    def output_log(self, log):
        self.append_log.emit(log)

class AngleText(QtCore.QObject):
    append_angle = QtCore.pyqtSignal(str)
    def output_angle(self, angle):
        self.append_angle.emit(angle)

angle_text = AngleText()
log_signal = LogSignal()
