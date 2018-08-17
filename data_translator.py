from threading import Thread
from time import time
import struct
from constansts import *


class DataTranslator(Thread):
    """Class for delayed data transferring by parts via serial port"""
    def __init__(self, serial, data, delay=0, confirmation=None, confirmationTimeout=1):
        """
        :param serial: instance of class serial.Serial
        :param data: list of data portions. Each element send by serial.write()
        :param delay: delay between data transfers
        :param confirmation: data which board return after reading given data. Left it None if check is not necessary
        """
        super().__init__()

        self._serial = serial
        self._data = data
        self._delay = delay
        self._confirm = confirmation
        self._confirm_timeout = confirmationTimeout

        self._index = -1
        self._need_pause = False
        self._need_stop = False

    def run(self):
        self._last_time = 0
        while True:
            if self._need_stop is True:
                break
            if self._need_pause is True:
                continue
            if time() - self._last_time >= self._delay:
                self._index += 1
                if self._index >= len(self._data):
                    break
                self._serial.write(self._data[self._index])
                if self._confirm is not None:
                    result = bytes()
                    wait_start = time()
                    while len(result) == 0:
                        if time() - wait_start > self._confirm_timeout:
                            raise TimeoutError("Confirmation from board time limit exceeded")
                        result = self._serial.read_all()
                    if result != self._confirm:
                        raise Exception("Wrong confirmation information sent by board")
                self._last_time = time()
                self.callback_data_changed()
        self.callback_translation_done()

    def set_index(self, index):
        if index < 0 or index >= len(self._data):
            raise ValueError("Index " + str(index) + " out of range")

        self._index = index

    def get_index(self):
        return self._index

    def resume_translation(self):
        self._need_pause = False

    def pause_translation(self):
        self._need_pause = True

    def cancel_translation(self):
        self._need_stop = True

    def callback_data_changed(self):
        """Calls when next data portion sent to serial port"""
        pass

    def callback_translation_done(self):
        """Calls when data transferring done"""
        pass