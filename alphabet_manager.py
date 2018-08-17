from tkinter import *
from tkinter.simpledialog import Dialog
from tkinter import simpledialog
from tkinter import messagebox
import os
import os.path as path
import pickle as pick
from glob import glob
from constansts import *
from alphabet_generator import AlphabetGenerator


_extension = ".alphabet"

def _filename_to_name(filename):
    return path.splitext(path.split(filename)[1])[0]

def _name_to_filename(name, folder):
    return path.join(folder, name + _extension)

class AlphabetManager(Frame):

    """Widget for managing alphabets
    Alphabet is dictionary in form {'letter' : code}
    """

    class _AlphabetSelector(Dialog):

        """Internal class used for choosing alphabets from given folder"""

        def __init__(self, parent, folder, title='Select alphabet'):
            self._folder = folder

            super().__init__(parent, title)

        def body(self, master):
            self._listbox = Listbox(master)
            self._listbox.pack(side=LEFT)
            self._button_frame = Frame(master)
            self._button_frame.pack(side=RIGHT, padx=10)
            Button(master, text="Add", font=button_font, command=self._on_add_click).pack(fill=BOTH, pady=5)
            Button(master, text="Delete", font=button_font, command=self._on_delete_click).pack(fill=BOTH, pady=5)
            self._update_listbox()

        def apply(self):
            self.result = self._get_current_filename()

        def _on_add_click(self):
            name = simpledialog.askstring("Alphabet name", "Enter name of a new alphabet")
            if name is not None:
                filename = _name_to_filename(name, self._folder)
                if not path.exists(filename):
                    file = open(filename, 'wb')
                    pick.dump(dict(), file)
                    file.close()
                    self._update_listbox()
                else:
                    messagebox.showwarning("Alphabet duplicate", "Alphabet with name " + name + " already created")

        def _on_delete_click(self):
            filename = self._get_current_filename()
            name = _filename_to_name(filename)
            answer = messagebox.askyesno("Confirmation", "Do you really want to delete " + '"'+name+'"')
            if answer is True:
                os.remove(filename)
                self._update_listbox()

        def _get_current_filename(self):
            name = self._listbox.get(ACTIVE)
            filename = _name_to_filename(name, self._folder)
            return filename

        def _update_listbox(self):
            self._listbox.delete(0, END)
            filenames = glob(path.join(self._folder, '*.alphabet'))
            for filename in filenames:
                name = _filename_to_name(filename)
                self._listbox.insert(END, name)

    def __init__(self, Selector, selector_args=list(), selector_kwds=dict(),  master=None, files_folder='',
                 default_alphabet_name="Default alphabet", cnf={}, **kw):
        """
        :param Selector: selector using in case of necessity edit or add symbols to alphabet
        :param selector_args: arguments for selector creating
        :param selector_kwds: keyword arguments for selector creating
        :param files_folder: folder in project where files of alphabet will be stored.
               By default it stores right in project folder.
        :param default_alphabet_name: Name of alphabet that will be generated if in given folder will be no alphabets.
        """

        self._Selector = Selector
        self._selector_args = selector_args
        self._selector_kwds = selector_kwds
        self._master = master
        self._folder = files_folder

        if not path.exists(files_folder):
            os.makedirs(files_folder)

        info_filename = path.join(self._folder, 'info')
        if path.exists(info_filename):
            info_file = open(info_filename, 'rb')
            self._alphabet_filename = pick.load(info_file)
            info_file.close()
        else:
            files = glob(path.join(self._folder, '*.alphabet'))
            if len(files) > 0:
                self._alphabet_filename = files[0]
            else:
                self._alphabet_filename = path.join(self._folder, default_alphabet_name + '.alphabet')
                file = open(self._alphabet_filename, 'wb')
                pick.dump(dict(), file)
                file.close()

        super().__init__(master, cnf, **kw)

        info_frame = Frame(self)
        info_frame.pack(side=LEFT, padx=10)
        self.info_name_label = Label(info_frame, font=header_font)
        self.info_name_label.pack(pady=5)
        self.info_symbol_label = Label(info_frame, font=text_font)
        self.info_symbol_label.pack(pady=5)
        button_frame = Frame(self)
        button_frame.pack(side=RIGHT, padx=10)
        Button(button_frame, text="Change", font=button_font, command=self._on_change_click).pack(fill=BOTH, pady=5)
        Button(button_frame, text="Edit", font=button_font, command=self._on_edit_click).pack(fill=BOTH, pady=5)

        self._read_alphabet()
        self._update_alphabet_info()

    def ask_add_symbols(self, symbols):
        gen = AlphabetGenerator(self._Selector, self._selector_args, self._selector_kwds, need_symbols=symbols)
        result = gen.result
        if result is not None:
            self._alphabet.update(result)
            self._write_alphabet()
            self._update_alphabet_info()
            self.callback_alphabet_changed()

    def get_alphabet(self):
        """
        :return: instacne of dict which in form {'letter' : code}
        """
        return self._alphabet.copy()

    def callback_alphabet_changed(self):
        pass

    def _on_change_click(self):
        selector = self._AlphabetSelector(self, self._folder)
        result = selector.result
        if result is not None:
            self._alphabet_filename = result
            self._read_alphabet()
            self._update_alphabet_info()
            self.callback_alphabet_changed()

    def _on_edit_click(self):
        gen = AlphabetGenerator(self._Selector, self._selector_args, self._selector_kwds, exist_symbols=self._alphabet)
        result = gen.result
        if result is not None:
            self._alphabet = result
            self._write_alphabet()
            self._update_alphabet_info()
            self.callback_alphabet_changed()

    def _update_alphabet_info(self):
        name = _filename_to_name(self._alphabet_filename)
        self.info_name_label['text'] = name
        self.info_symbol_label['text'] = str(len(self._alphabet)) + " symbols in alphabet"

    def _read_alphabet(self):
        file = open(self._alphabet_filename, 'rb')
        self._alphabet = pick.load(file)
        file.close()

    def _write_alphabet(self):
        file = open(self._alphabet_filename, 'wb')
        pick.dump(self._alphabet, file)
        file.close()
