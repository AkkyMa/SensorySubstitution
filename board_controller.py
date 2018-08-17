from tkinter import *
from PIL import Image, ImageFont, ImageDraw, ImageTk
from threading import Timer
import pickle
import selector
import struct
import time
from constansts import *
import os
from os import path
from math import ceil
from tkinter import messagebox
from data_translator import DataTranslator
from alphabet_manager import AlphabetManager


class Segment14Frame(Frame):
    """Controller for 14 segment board"""

    MODE_VALUE_TEXTSENDER = 1
    MODE_VALUE_SEGMENTSELECTOR = 2

    OUTPUT_TYPE_LETTER_UPDATE = 1
    OUTPUT_TYPE_ELECTRIC_PARAMETER = 2

    alphabet = [
        0b0000000000000001,
        0b0000000000000010,
        0b0000000000000100,
        0b0000000000001000,
        0b0000000000010000,
        0b0000000000100000,
        0b0000000001000000,
        0b0000000010000000,
        0b0000000100000000,
        0b0000001000000000,
        0b0000010000000000,
        0b0000100000000000,
        0b0001000000000000,
        0b0010000000000000,
        0b0100000000000000,
        0b1000000000000000,
        0b0000000000000000,
        0b0000000000000000,
        0b0000000000000000,
        0b0000000000000000,
        0b0000000000000000,
        0b0000000000000000,
        0b0000000000000000,
        0b0000000000000000,
        0b0001001011001001,
        0b0001010111000000,
        0b0001001011111001,
        0b0000000011100011,
        0b0000010100110000,
        0b0001001011001000,
        0b0011101000000000,
        0b0001011100000000,
        0b0000000000000000,  #
        0b0000000000000110,  # !
        0b0000001000100000,  # "
        0b0001001011001110,  # #
        0b0001001011101101,  # $
        0b0000110000100100,  # %
        0b0010001101011101,  # &
        0b0000010000000000,  # '
        0b0010010000000000,  # (
        0b0000100100000000,  # )
        0b0011111111000000,  # *
        0b0001001011000000,  # +
        0b0000100000000000,  # ,
        0b0000000011000000,  # -
        0b0000000000000000,  # .
        0b0000110000000000,  # /
        0b0000110000111111,  # 0
        0b0000000000000110,  # 1
        0b0000000011011011,  # 2
        0b0000000010001111,  # 3
        0b0000000011100110,  # 4
        0b0000000011101101,  # 5
        0b0000000011111101,  # 6
        0b0000000000000111,  # 7
        0b0000000011111111,  # 8
        0b0000000011101111,  # 9
        0b0001001000000000,  # :
        0b0000101000000000,  # ;
        0b0010010000000000,  # <
        0b0000000011001000,  # =
        0b0000100100000000,  # >
        0b0001000010000011,  # ?
        0b0000001010111011,  # @
        0b0000000011110111,  # A
        0b0001001010001111,  # B
        0b0000000000111001,  # C
        0b0001001000001111,  # D
        0b0000000011111001,  # E
        0b0000000001110001,  # F
        0b0000000010111101,  # G
        0b0000000011110110,  # H
        0b0001001000000000,  # I
        0b0000000000011110,  # J
        0b0010010001110000,  # K
        0b0000000000111000,  # L
        0b0000010100110110,  # M
        0b0010000100110110,  # N
        0b0000000000111111,  # O
        0b0000000011110011,  # P
        0b0010000000111111,  # Q
        0b0010000011110011,  # R
        0b0000000011101101,  # S
        0b0001001000000001,  # T
        0b0000000000111110,  # U
        0b0000110000110000,  # V
        0b0010100000110110,  # W
        0b0010110100000000,  # X
        0b0001010100000000,  # Y
        0b0000110000001001,  # Z
        0b0000000000111001,  # [
        0b0010000100000000,  #
        0b0000000000001111,  # ]
        0b0000110000000011,  # ^
        0b0000000000001000,  # _
        0b0000000100000000,  # `
        0b0001000001011000,  # a
        0b0010000001111000,  # b
        0b0000000011011000,  # c
        0b0000100010001110,  # d
        0b0000100001011000,  # e
        0b0000000001110001,  # f
        0b0000010010001110,  # g
        0b0001000001110000,  # h
        0b0001000000000000,  # i
        0b0000000000001110,  # j
        0b0011011000000000,  # k
        0b0000000000110000,  # l
        0b0001000011010100,  # m
        0b0001000001010000,  # n
        0b0000000011011100,  # o
        0b0000000101110000,  # p
        0b0000010010000110,  # q
        0b0000000001010000,  # r
        0b0010000010001000,  # s
        0b0000000001111000,  # t
        0b0000000000011100,  # u
        0b0010000000000100,  # v
        0b0010100000010100,  # w
        0b0010100011000000,  # x
        0b0010000000001100,  # y
        0b0000100001001000,  # z
        0b0000100101001001,  # {
        0b0001001000000000,  # |
        0b0010010010001001,  # }
        0b0000010100100000,  # ~
        0b0011111111111111]

    def __init__(self, serial, master=None, cnf={}, **kw):
        """
        :param serial: instance of object serial.Serial
        """
        super().__init__(master, cnf, **kw)
        self.serial = serial
        self.current_code = 0
        self.font14 = ImageFont.truetype('Segment14.otf', 64)
        self.segmentSelector_current_code = 0

        Label(self, text="Data transfer", font=header_font).grid(row=1, column=1)
        radiobutton_frame = Frame(self)
        radiobutton_frame.grid(row=2, column=1, pady=5)
        self.mode_var = IntVar()
        self.mode_var.set(self.MODE_VALUE_TEXTSENDER)
        Radiobutton(radiobutton_frame, text="Text sender", font=radiobutton_font, variable=self.mode_var,
                    value=self.MODE_VALUE_TEXTSENDER, command=self._on_radiobutton_clicked).grid(row=1, column=1)
        Radiobutton(radiobutton_frame, text="Segment selector", font=radiobutton_font, variable=self.mode_var,
                    value=self.MODE_VALUE_SEGMENTSELECTOR, command=self._on_radiobutton_clicked).grid(row=1, column=2)

        self.textSender_frame = Frame(self)
        self.textSender_frame.grid(row=3, column=1, pady=10)
        self.textSender_frame.grid_remove()
        textSender_input_frame = Frame(self.textSender_frame)
        textSender_input_frame.grid(row=1, column=1, padx=10)
        self.textSender_entry = Entry(textSender_input_frame, font=entry_font, width=20)
        self.textSender_entry.grid(row=1, column=1)
        self.counter = 0
        textSender_textManipulators_frame = Frame(textSender_input_frame)
        textSender_textManipulators_frame.grid(row=2, column=1, pady=(10, 0))
        Button(textSender_textManipulators_frame, text='<', font=button_font, width=9, command=self._update_counter(-1))\
            .grid(row=1, column=1)
        Button(textSender_textManipulators_frame, text='>', font=button_font, width=9, command=self._update_counter(1))\
            .grid(row=1, column=2)
        textSender_button_frame = Frame(self.textSender_frame)
        textSender_button_frame.grid(row=1, column=2, padx=(50, 0))
        Button(textSender_button_frame, text="Send", font=button_font, width=8,
               command=self._on_textSender_send_clicked).grid(row=1, column=1)
        Button(textSender_button_frame, text="Stop", font=button_font, width=8,
               command=self._on_stop_clicked).grid(row=2, column=1)
        self.letter_model = Label(self.textSender_frame)
        self.letter_model.grid(row=2, column=1, pady=10)

        self.segmentSelector_frame = Frame(self)
        self.segmentSelector_frame.grid(row=3, column=1, pady=10)
        self.segmentSelector_frame.grid_remove()
        self.selector = selector.Segment14(self.segmentSelector_frame, width=200, height=200)
        self.selector.grid(row=1, column=1)
        segmentSelector_button_frame = Frame(self.segmentSelector_frame)
        segmentSelector_button_frame.grid(row=1, column=2, padx=(20, 0))
        Button(segmentSelector_button_frame, text="Send", font=button_font, width=8,
               command=self._on_segmentSelector_send_clicked).grid(row=1, column=1)
        Button(segmentSelector_button_frame, text="Cancel", font=button_font, width=8,
               command=self._on_segmentSelector_cancel_clicked).grid(row=2, column=1)
        Button(segmentSelector_button_frame, text="Stop", font=button_font, width=8,
               command=self._on_stop_clicked).grid(row=3, column=1)

        electric_frame = Frame(self)
        electric_frame.grid(row=4, column=1, pady=10)
        electric_enter_frame = Frame(electric_frame)
        electric_enter_frame.grid(row=1, column=1)
        Label(electric_enter_frame, text="Frequency:", font=text_font).grid(row=1, column=1)
        Label(electric_enter_frame, text="Duty ratio:", font=text_font).grid(row=2, column=1)
        self.freq_entry = Entry(electric_enter_frame, font=entry_font, width=12)
        self.freq_entry.grid(row=1, column=2, padx=20)
        self.duty_entry = Entry(electric_enter_frame, font=entry_font, width=12)
        self.duty_entry.grid(row=2, column=2, padx=20)
        Button(electric_frame, text="Set", font=button_font, width=8, height=2, command=self._on_electric_set_clicked)\
            .grid(row=1, column=2)

        self._on_radiobutton_clicked()
        file = open(r'segment14_params.pkl', 'rb')
        freq = pickle.load(file)
        duty = pickle.load(file)
        file.close()
        self.freq_entry.insert(0, freq)
        self.duty_entry.insert(0, duty)
        Timer(2, self._on_electric_set_clicked).start()

    def set_serial(self, serial):
        """Set new instance of serial.Serial in case of necessity"""
        self.serial = serial

    def _on_radiobutton_clicked(self):
        value = self.mode_var.get()
        if value is self.MODE_VALUE_TEXTSENDER:
            self.segmentSelector_frame.grid_remove()
            self.textSender_frame.grid()
        elif value is self.MODE_VALUE_SEGMENTSELECTOR:
            self.textSender_frame.grid_remove()
            self.segmentSelector_frame.grid()

    def _on_textSender_send_clicked(self):
        """Send bytes via serial port
            First byte is mode, the rest is letter code"""

        self._highlight_input()
        letter = self.textSender_entry.get()[self.counter]
        letter_code = self.alphabet[ord(letter)]
        self.serial.write(bytes([self.OUTPUT_TYPE_LETTER_UPDATE, *struct.pack('>H', letter_code)]))

    def _on_segmentSelector_send_clicked(self):
        """Send bytes via serial port
            First byte is mode, the rest is letter code"""
        letter_code = self.selector.get_segments_code()
        self.serial.write(bytes([self.OUTPUT_TYPE_LETTER_UPDATE, *struct.pack('>H', letter_code)]))
        self.segmentSelector_current_code = letter_code

    def _on_segmentSelector_cancel_clicked(self):
        self.selector.set_segments_code(self.segmentSelector_current_code)

    def _on_stop_clicked(self):
        self.serial.write(bytes([self.OUTPUT_TYPE_LETTER_UPDATE, *struct.pack('>H', 0)]))
        self.segmentSelector_current_code = 0

    def _on_electric_set_clicked(self):
        freq = float(self.freq_entry.get())
        duty = float(self.duty_entry.get())
        self.serial.write(bytes([self.OUTPUT_TYPE_ELECTRIC_PARAMETER, *struct.pack('>ff', freq, duty)]))
        file = open(r'segment14_params.pkl', 'wb')
        pickle.dump(freq, file)
        pickle.dump(duty, file)
        file.close()

    def _update_counter(self, delta):
        """Handle a walk through input string

        Set new counter that indicates the current character to be sent

        :param delta: the integer indicating how user wants to change the focus character
        :return:
        """
        def f():
            text = self.textSender_entry.get()
            counter = self.counter + delta
            if len(text) > 0:
                if 0 <= counter < len(text):
                    self.counter = counter
                    self._highlight_input()
                else:
                    self.counter = 0
                    self._highlight_input()
        return f

    def _highlight_input(self):
        """Highlight the focus character in the input string

        :return:
        """
        text = self.textSender_entry.get()
        if 0 <= self.counter < len(text):
            text = text.lower()
            text = text[:self.counter] + text[self.counter].upper() + text[self.counter + 1:]
            self.textSender_entry.delete(0, END)
            self.textSender_entry.insert(0, text)
            width, height = self.font14.getsize(text[self.counter].upper())
            image = Image.new("RGBA", (width, height), color=(0, 0, 0, 0))
            draw = ImageDraw.Draw(image)
            draw.text((0, 0), text[self.counter].upper(), font=self.font14, fill="black")
            self._photoimage = ImageTk.PhotoImage(image)
            self.letter_model.config(image=self._photoimage)
        else:
            self.counter = 0
            self._highlight_input()

class CircleSegmentsOnTransistors(Frame):
    """General controller for boards with circle segments on transistors"""

    MODE_SEGMENTSELECTOR = 1
    MODE_TEXTSENDER = 2

    OUTPUT_TYPE_STOP = 1
    OUTPUT_TYPE_SINGLE_SYMBOL = 2
    OUTPUT_TYPE_TEXT_START = 3
    OUTPUT_TYPE_NEXT_SYMBOL = 4

    INPUT_TYPE_CONFIRMATION = 10

    def __init__(self, serial, horizontal_segments, vertical_segments, master=None, cnf={}, **kw):
        super().__init__(master, cnf, **kw)
        self._lines = horizontal_segments
        self._segments_in_line = vertical_segments
        self._segments = horizontal_segments * vertical_segments
        self._foldername_alphabet = "alphabet/CircleSegmentsOnTransistors_" + str(horizontal_segments) + "x" + str(vertical_segments)
        self._filename_segmentSelector = "CircleSegmentsOnTransistors_" + str(horizontal_segments) + "x" + str(vertical_segments) + "_selector_params.pkl"
        self._filename_textSender = "CircleSegmentsOnTransistors_" + str(horizontal_segments) + "x" + str(vertical_segments) + "_text_params.pkl"

        Label(self, text="Data transfer", font=header_font).grid(row=1, column=1)
        radiobutton_frame = Frame(self, pady=10)
        radiobutton_frame.grid(row=2, column=1)
        self._mode_var = IntVar()
        self._mode_var.set(self.MODE_TEXTSENDER)
        Radiobutton(radiobutton_frame, text="Text sender", font=radiobutton_font,
                    variable=self._mode_var, value=self.MODE_TEXTSENDER, command=self._on_radiobutton_click).pack()
        Radiobutton(radiobutton_frame, text="Segment selector", font=radiobutton_font,
                    variable=self._mode_var, value=self.MODE_SEGMENTSELECTOR, command=self._on_radiobutton_click).pack(pady=(10, 0))

        self._segmentSelector_frame = Frame(self)
        self._segmentSelector_frame.grid(row=3, column=1, padx=10, pady=10)
        self._segmentSelector_frame.grid_remove()
        self._selector = selector.CircleSegmentsDisablableLines(self._lines, self._segments_in_line, self._segmentSelector_frame, height=300)
        self._current_letters_code = self._selector.get_segments_code()
        self._current_lines_code = self._selector.get_lines_code
        self._selector.on_click_callback = self._segmentSelector_cancel_button_update
        self._selector.grid(row=1, column=1)
        segmentSelector_button_frame = Frame(self._segmentSelector_frame)
        segmentSelector_button_frame.grid(row=1, column=2, padx=(10, 0))
        Button(segmentSelector_button_frame, text="Send", font=button_font, width=9,
            command=self._on_segmentSelector_send_clicked).grid(row=1, column=1)
        self._segmentSelector_cancel_button = Button(segmentSelector_button_frame, text="Cancel", font=button_font, width=9,
            command=self._on_segmentSelector_cancel_clicked)
        self._segmentSelector_cancel_button.grid(row=2, column=1)
        Button(segmentSelector_button_frame, text="Stop", font=button_font, width=9,
            command=self._on_segmentSelector_stop_clicked).grid(row=3, column=1)
        self._segmentSelector_delay_frame = Frame(self._segmentSelector_frame)
        self._segmentSelector_delay_frame.grid(row=2, column=1, pady=10)
        self._segmentSelector_delay_entry = Entry(self._segmentSelector_delay_frame, font=text_font, width=10)
        self._segmentSelector_delay_entry.pack(side=LEFT)
        Label(self._segmentSelector_delay_frame, text="ms line work time", font=text_font).pack(side=RIGHT)
        if not path.exists(self._filename_segmentSelector):
            file = open(self._filename_segmentSelector, 'wb')
            pickle.dump(100, file)
            file.close()
        self._segmentSelector_cancel_button_update()
        file = open(self._filename_segmentSelector, 'rb')
        self._segmentSelector_delay_entry.insert(0, pickle.load(file))
        file.close()

        self._textSender_frame = Frame(self)
        self._textSender_frame.grid(row=3, column=1, padx=10, pady=10)

        self._alphabet_manager = AlphabetManager(selector.CircleSegments, (self._lines, self._segments_in_line),
                        master=self._textSender_frame, files_folder=self._foldername_alphabet)
        self._alphabet_manager.callback_alphabet_changed = self._update_alphabet
        self._alphabet_manager.grid(row=1, columnspan=2)

        self._textSender_text = Text(self._textSender_frame, font=small_entry_font, width=40, height=10)
        self._textSender_text.grid(row=2, column=1)

        textSender_right_button_frame = Frame(self._textSender_frame)
        textSender_right_button_frame.grid(row=2, column=2, padx=(10, 0))
        self._textSender_start_button = Button(textSender_right_button_frame, text="Start", font=button_font,
                                               command=self._on_textSender_start_clicked)
        self._textSender_start_button.pack(fill=BOTH, pady=2)
        self._textSender_resume_button = Button(textSender_right_button_frame, text="Resume", font=button_font,
                                                command=self._on_textSender_resume_clicked)
        self._textSender_resume_button.pack(fill=BOTH, pady=2)
        self._textSender_pause_button = Button(textSender_right_button_frame, text="Pause", font=button_font,
                                               command=self._on_textSender_pause_clicked)
        self._textSender_pause_button.pack(fill=BOTH, pady=2)
        self._textSender_stop_button = Button(textSender_right_button_frame, text="Stop", font=button_font,
                                              command=self._on_textSender_stop_clicked)
        self._textSender_stop_button.pack(fill=BOTH, pady=2)

        textSender_bottom_button_frame = Frame(self._textSender_frame)
        textSender_bottom_button_frame.grid(row=3, column=1, pady=5)
        self._textSender_left_button = Button(textSender_bottom_button_frame, width=10, text="<", font=button_font,
                                              command=self._on_textSender_left_clicked)
        self._textSender_left_button.grid(row=0, column=1)
        self._textSender_right_button = Button(textSender_bottom_button_frame, width=10, text=">", font=button_font,
                                               command=self._on_textSender_right_clicked)
        self._textSender_right_button.grid(row=0, column=3)
        self._textSender_send_button = Button(textSender_bottom_button_frame, width=8, text="Send", font=button_font,
                                              command=self._on_textSender_send_clicked)
        self._textSender_send_button.grid(row=0, column=2, padx=2)

        self._textSender_info_frame = Frame(self._textSender_frame)
        self._textSender_info_frame.grid(row=4, column=1, pady=(10, 0))
        self._textSender_params_frame = Frame(self._textSender_info_frame)
        self._textSender_params_frame.grid(row=1, column=1)
        Message(self._textSender_params_frame, text="line change delay(ms):", font=text_font, width=100, justify=CENTER).pack()
        self._textSender_delay_string = StringVar()
        self._textSender_delay_string.trace('w', lambda *args: self._textSender_expected_time_update())
        self._textSender_delay_entry = Entry(self._textSender_params_frame, font=entry_font, width=12,
                                             textvariable=self._textSender_delay_string)
        self._textSender_delay_entry.pack()
        Message(self._textSender_params_frame, text="line repeat times:", font=text_font, width=100, justify=CENTER).pack()
        self._textSender_repeat_string = StringVar()
        self._textSender_repeat_string.trace('w', lambda *args: self._textSender_expected_time_update())
        self._textSender_repeat_entry = Entry(self._textSender_params_frame, font=entry_font, width=12,
                                              textvariable=self._textSender_repeat_string)
        self._textSender_repeat_entry.pack()
        Message(self._textSender_params_frame, text="Expected letter time(sec):", font=entry_font, width=110, justify=CENTER).pack()
        self._textSender_letter_time_label = Label(self._textSender_params_frame, font=entry_font, width=12)
        self._textSender_letter_time_label.pack()
        self._check_lines_var = IntVar()
        self._check_lines_var.set(1)
        self._textSender_lines_checkbutton = Checkbutton(self._textSender_info_frame, text="Check lines",
                                                         font=checkbutton_font, variable=self._check_lines_var)
        self._textSender_lines_checkbutton.grid(row=2, column=1)
        self._textSender_segments = selector.CircleSegments(self._lines, self._segments_in_line,
                                    self._textSender_info_frame, width=200, segment_size_coefficient=0.5, clickable=False)
        self._textSender_segments.grid(row=1, column=2, padx=10)
        self._textSender_lines = selector.Arrows(self._lines, master=self._textSender_info_frame, width=200,
                                                 segment_size_coefficient=0.55, clickable=True)
        self._textSender_lines.callback_after_click = lambda *args: self._textSender_expected_time_update()
        self._textSender_lines.grid(row=2, column=2, pady=(10, 0))
        self._textSender_params_read()
        self._textSender_frame.grid_remove()

        self._current_symbol_index = -1
        self._translator = None
        self._update_alphabet()

        self._on_radiobutton_click()
        self.set_serial(serial)
        self._translation_stop()

    def set_serial(self, serial):
        """Set new instance of serial.Serial in case of necessity"""
        self._serial = serial

    def _on_radiobutton_click(self):
        value = self._mode_var.get()
        if value == self.MODE_TEXTSENDER:
            self._segmentSelector_frame.grid_remove()
            self._textSender_frame.grid()
        else:
            self._textSender_frame.grid_remove()
            self._segmentSelector_frame.grid()

    def _translation_start(self, data, params):
        delay, repeat, line_code = params[0], params[1], params[2]
        letter_delay = self._get_letter_delay(params)
        self._translator = DataTranslator(self._serial, data, letter_delay/1000,
                                          bytes([*struct.pack('>b', self.INPUT_TYPE_CONFIRMATION)]))
        self._translator.callback_data_changed = lambda: self._update_current_symbol()
        self._translator.callback_translation_done = lambda: self._translation_stop()
        self._serial.write(bytes([self.OUTPUT_TYPE_TEXT_START, *struct.pack('>h', delay), *struct.pack('>h', repeat),
                                  *self._int_to_bytes(line_code, self._lines)]))
        self._translator.start()
        self._textSender_text['state'] = DISABLED
        self._textSender_resume_button['state'] = DISABLED
        self._textSender_pause_button['state'] = ACTIVE
        self._textSender_left_button['state'] = DISABLED
        self._textSender_send_button['state'] = DISABLED
        self._textSender_right_button['state'] = DISABLED
        self._textSender_delay_entry['state'] = DISABLED
        self._textSender_repeat_entry['state'] = DISABLED

    def _translation_stop(self):
        self._textSender_text['state'] = NORMAL
        self._textSender_resume_button['state'] = DISABLED
        self._textSender_pause_button['state'] = DISABLED
        self._textSender_left_button['state'] = ACTIVE
        self._textSender_send_button['state'] = ACTIVE
        self._textSender_right_button['state'] = ACTIVE
        self._textSender_delay_entry['state'] = NORMAL
        self._textSender_repeat_entry['state'] = NORMAL
        self._current_symbol_index = -1
        self._update_current_symbol_info()

    def _on_textSender_start_clicked(self):
        params = self._textSender_get_params()
        delay, repeat, line_code = params[0], params[1], params[2]
        if delay > 30000:
            messagebox.showwarning("Too high delay", "Please use values less than 30000")
            return
        text = self._textSender_text.get('1.0', END).rstrip()
        text = text.replace('\n', ' ')
        need_symbols = set()
        for s in text:
            if s not in self._alphabet:
                need_symbols.add(s)
        if len(need_symbols) != 0:
            answer = messagebox.askyesno("Undefined symbols", "Define required symbols now?")
            if answer is True:
                self._alphabet_manager.ask_add_symbols(need_symbols)
            return
        if self._check_lines_var.get() is 1:
            result = self._check_lines(text, line_code)
            if result is False:
                answer = messagebox.askyesno("Required lines disabled", "One or more lines required for translation"
                                             "given message with given alphabet is disabled. Translate message anyway?")
                if answer is False:
                    return
        if self._count_lines(line_code) < 2:
            messagebox.showinfo("Not enough lines", "Number of lines must be two or more")
            return
        if self._translator is not None and self._translator.is_alive():
            self._on_textSender_stop_clicked()
        data = [(bytes([*struct.pack('>b', self.OUTPUT_TYPE_NEXT_SYMBOL)]) +
                 self._int_to_bytes(self._alphabet[s], self._segments)) for s in text]
        self._textSender_params_write(params)
        self._translation_start(data, params)

    def _on_textSender_resume_clicked(self):
        self._translator.resume_translation()
        self._textSender_resume_button['state'] = DISABLED
        self._textSender_pause_button['state'] = ACTIVE
        self._textSender_left_button['state'] = DISABLED
        self._textSender_right_button['state'] = DISABLED

    def _on_textSender_pause_clicked(self):
        self._translator.pause_translation()
        self._textSender_resume_button['state'] = ACTIVE
        self._textSender_pause_button['state'] = DISABLED
        self._textSender_left_button['state'] = ACTIVE
        self._textSender_right_button['state'] = ACTIVE

    def _on_textSender_stop_clicked(self):
        if self._translator is not None and self._translator.is_alive():
            self._translator.cancel_translation()
        self._serial.write(bytes([*struct.pack('>b', self.OUTPUT_TYPE_STOP)]))

    def _on_textSender_send_clicked(self):
        if self._current_symbol_index == -1:
            messagebox.showinfo("Select symbol", "Please select symbol that you want send")
            return
        delay, repeat, line_code = self._textSender_get_params()
        if delay > 30000:
            messagebox.showwarning("High delay", "Please use delay under 30000 ms")
            return
        symbol = self._textSender_text.get('1.'+str(self._current_symbol_index), '1.'+str(self._current_symbol_index+1))
        letter_code = self._int_to_bytes(self._alphabet[symbol], self._segments)
        line_code = self._int_to_bytes(self._textSender_lines.get_segments_code(), self._lines)
        self._serial.write(bytes([self.OUTPUT_TYPE_SINGLE_SYMBOL, *struct.pack('>h', delay)]) + letter_code + line_code)

    def _on_textSender_left_clicked(self):
        self._current_symbol_index -= 1
        if self._current_symbol_index < -1:
            self._current_symbol_index = self._textSender_text.count('1.0', END)[0] - 2
        if self._translator is not None and self._translator.is_alive():
            self._translator.set_index(self._current_symbol_index)
        self._update_current_symbol_info()

    def _on_textSender_right_clicked(self):
        self._current_symbol_index += 1
        if self._current_symbol_index > self._textSender_text.count('1.0', END)[0] - 2:
            self._current_symbol_index = -1
        if self._translator is not None and self._translator.is_alive():
            self._translator.set_index(self._current_symbol_index)
        self._update_current_symbol_info()

    def _check_lines(self, text, line_code):
        letters = set()
        for s in text:
            letters.add(s)
        lines = list()
        while line_code != 0:
            lines.append(line_code & 1)
            line_code >>= 1
        for s in letters:
            letter_code = self._alphabet[s]
            for c in range(self._segments):
                # Here logical operation "not implies"
                if not ((letter_code >> c & 1) or lines[c % self._lines]):
                    return False
        return True

    def _get_letter_delay(self, params=None):
        if params is None:
            params = self._textSender_get_params()
        delay, repeat, line_code = params[0], params[1], params[2]
        lines = self._count_lines(line_code)
        return delay * lines * repeat

    def _count_lines(self, line_code):
        lines = 0
        while line_code != 0:
            lines += line_code & 1
            line_code >>= 1
        return lines

    def _on_segmentSelector_send_clicked(self):
        delay = getint(self._segmentSelector_delay_entry.get())
        if delay > 30000:
            messagebox.showwarning("High delay", "Please use delay under 30000 ms")
            return
        line_code = self._selector.get_lines_code()
        letter_code = self._selector.get_segments_code()
        line_send_code = self._int_to_bytes(line_code, self._lines)
        letter_send_code = self._int_to_bytes(letter_code, self._segments)
        send_code = bytes([self.OUTPUT_TYPE_SINGLE_SYMBOL, *struct.pack('>h', delay)]) + \
                    letter_send_code + line_send_code
        self._serial.write(send_code)
        self._current_line_code = line_code
        self._current_letter_code = letter_code
        self._segmentSelector_cancel_button_update()

    def _on_segmentSelector_stop_clicked(self):
        self._serial.write(self.OUTPUT_TYPE_STOP)
        self._current_letter_code = 0
        self._segmentSelector_cancel_button_update()

    def _segmentSelector_cancel_button_update(self):
        letter_code = self._selector.get_segments_code()
        line_code = self._selector.get_lines_code()
        if letter_code == self._current_letters_code and line_code == self._current_lines_code:
            self._segmentSelector_cancel_button['state'] = DISABLED
        else:
            self._segmentSelector_cancel_button['state'] = ACTIVE

    def _on_segmentSelector_cancel_clicked(self):
        self._selector.set_lines_code(self._current_lines_code)
        self._selector.set_segments_code(self._current_letter_code)
        self._segmentSelector_cancel_button_update()

    def _update_current_symbol(self):
        self._current_symbol_index = self._translator.get_index()
        self._update_current_symbol_info()

    def _update_alphabet(self):
        self._alphabet = self._alphabet_manager.get_alphabet()

    def _update_current_symbol_info(self):
        self._textSender_text.tag_delete('selection')
        if self._current_symbol_index != -1:
            self._textSender_text.tag_add('selection', '1.'+str(self._current_symbol_index))
            self._textSender_text.tag_config('selection', foreground='red')
            current_symbol = self._textSender_text.get('1.'+str(self._current_symbol_index), '1.'+str(self._current_symbol_index+1))
            self._textSender_segments.set_segments_code(self._alphabet[current_symbol])
        else:
            self._textSender_segments.set_default()

    def _textSender_get_params(self):
        delay = getint(self._textSender_delay_entry.get())
        repeat = getint(self._textSender_repeat_entry.get())
        line_code = self._textSender_lines.get_segments_code()
        return delay, repeat, line_code

    def _textSender_expected_time_update(self, params=None):
        try:
            if params is None:
                params = self._textSender_get_params()
            letter_delay = self._get_letter_delay(params)
            self._textSender_letter_time_label['text'] = str(letter_delay/1000)
        except:
            pass

    def _on_close(self):
        if self._translator is not None and self._translator.is_alive():
            self._translator.cancel_translation()
        self._serial(bytes([*struct.pack('>b', self.OUTPUT_TYPE_STOP)]))

    def _textSender_params_read(self):
        try:
            file = open(self._filename_textSender, 'rb')
            delay = pickle.load(file)
            repeat = pickle.load(file)
            line_code = pickle.load(file)
            file.close()
        except EOFError:
            file.close()
            os.remove(self._filename_textSender)
            delay = 50
            repeat = 10
            line_code = self._textSender_lines.get_segments_code()
        except FileNotFoundError:
            delay = 50
            repeat = 10
            line_code = self._textSender_lines.get_segments_code()
        self._textSender_delay_entry.delete(0, END)
        self._textSender_delay_entry.insert(0, str(delay))
        self._textSender_repeat_entry.delete(0, END)
        self._textSender_repeat_entry.insert(0, str(repeat))
        self._textSender_lines.set_segments_code(line_code)
        self._textSender_expected_time_update((delay, repeat, line_code))

    def _textSender_params_write(self, params=None):
        if params is None:
            params = self._textSender_get_params()
        delay, repeat, line_code = params[0], params[1], params[2]
        file = open(self._filename_textSender, 'wb')
        pickle.dump(delay, file)
        pickle.dump(repeat, file)
        pickle.dump(line_code, file)
        file.close()

    def _int_to_bytes(self, i, bit_size):
        return i.to_bytes(ceil(bit_size/8), 'big')
