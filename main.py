from tkinter import *
import subprocess
from serial import Serial
import board_controller

header_font = (None, 20)
text_font = (None, 12)
entry_font = (None, 12)
radiobutton_font = (None, 12)
button_font = (None, 12)

class ConnectionFrame(Frame):

    BOARD_VALUE_SEGMENT14 = 1
    BOARD_VALUE_SEGMENT25 = 2

    board_names = {
        BOARD_VALUE_SEGMENT14: "14 segment board",
        BOARD_VALUE_SEGMENT25: "25 segment board"
    }

    def __init__(self, master, cnf={}, **kw):
        super().__init__(master, cnf, **kw)

        self.connecting_frame = Frame(self)
        self.connecting_frame.grid(row=1, column=1, padx=10, pady=10)
        Label(self.connecting_frame, text="Connection", font=header_font).grid(row=1)
        connecting_radiobutton_frame = Frame(self.connecting_frame)
        connecting_radiobutton_frame.grid(row=2, pady=10)
        self.board_var = IntVar()
        self.board_var.set(self.BOARD_VALUE_SEGMENT14)
        for i in self.board_names:
            Radiobutton(connecting_radiobutton_frame, text=self.board_names[i], variable=self.board_var, value=i,
                        font=radiobutton_font).pack()
        connecting_internal_frame = Frame(self.connecting_frame)
        connecting_internal_frame.grid(row=3, pady=(10, 0))
        self.listbox = Listbox(connecting_internal_frame, width=35, selectmode=SINGLE)
        self.listbox.grid(row=1, column=1)
        connecting_button_frame = Frame(connecting_internal_frame)
        connecting_button_frame.grid(row=1, column=2, padx=(15, 0))
        Button(connecting_button_frame, text="Connect", font=button_font, width=12,
               command=self.on_connect_clicked).grid(row=1)
        Button(connecting_button_frame, text="Search", font=button_font, width=12,
               command=self.on_search_clicked).grid(row=2)
        self.on_search_clicked()

        self.connect_control_frame = Frame(self)
        self.connect_control_frame.grid(row=1, column=1, padx=10, pady=10)
        self.connect_control_frame.grid_remove()
        self.connect_control_message = Message(self.connect_control_frame, font=text_font, width=200)
        self.connect_control_message.grid(row=1, column=1)
        connect_control_button_frame = Frame(self.connect_control_frame)
        connect_control_button_frame.grid(row=1, column=2, padx=(10, 0))
        Button(connect_control_button_frame, text="Reconnect", font=button_font, width=10,
               command=self.on_reconnect_clicked).grid(row=1, column=1)
        Button(connect_control_button_frame, text="Disconnect", font=button_font, width=10,
               command=self.on_disconnect_clicked).grid(row=2, column=1)

    def on_connect_clicked(self):
        self.port = self.listbox.get(ACTIVE)
        self.serial = Serial(self.port)
        self.connect_control_message['text'] = "Connected to " + self.port + " as to " + self.board_names[
            self.board_var.get()]
        self.connecting_frame.grid_remove()
        self.connect_control_frame.grid()
        value = self.board_var.get()
        if value is self.BOARD_VALUE_SEGMENT14:
            self.board_control_frame = board_controller.Segment14Frame(self.serial, self)
        elif value is self.BOARD_VALUE_SEGMENT25:
            self.board_control_frame = board_controller.CircleSegmentsOnTransistors(self.serial, 5, 5, self)
        self.board_control_frame.grid(row=2, column=1, padx=10, pady=10)

    def on_search_clicked(self):
        self.listbox.delete(0, END)
        port_strings = subprocess.check_output(['python', '-m', 'serial.tools.list_ports']).decode(
            'utf-8').strip().split()
        for i in range(len(port_strings)):
            self.listbox.insert(i, port_strings[i])

    def on_reconnect_clicked(self):
        self.serial.close()
        self.serial = Serial(self.port)
        self.board_control_frame.set_serial(self.serial)

    def on_disconnect_clicked(self):
        self.serial.close()
        self.board_control_frame.destroy()
        self.connect_control_frame.grid_remove()
        self.connecting_frame.grid()

root = Tk()
ConnectionFrame(root).grid(row=1, column=1)
root.mainloop()