import tkinter as tk
from tkinter import simpledialog
from tkinter import *
from tkinter import messagebox
from constansts import *
from itertools import chain


class AlphabetGenerator(simpledialog.Dialog):

    """Window for generating new and editing old symbols in alphabet
    Alphabet is dictionary in form {'letter' : code}
    """

    class _QuerySymbol(simpledialog._QueryDialog):
        """
        Internal class for asking a symbol when user want add or search it
        """
        def validate(self):
            string = self.entry.get()
            if len(string) is 1:
                return 1
            else:
                messagebox.showwarning("Wrong value",
                                       "Please enter one symbol",
                                       parent=self)
                return 0

        def apply(self):
            self.result = self.entry.get()

    def __init__(self, Selector, selector_args=tuple(), selector_kwds=dict(),
                 need_symbols=list(), exist_symbols=dict(),
                 parent=None, title='Alphabet Generator'):
        """
        :param Selector: selector class which will be used for generating symbols
        :param selector_args: arguments for creating selector
        :param selector_kwds: keyword arguments for creating selector
        :param need_symbols: undefined symbols which need to generate
        :param exist_symbols: defined symbols which can be edited
        """

        if parent is None:
            parent = tk._default_root

        # For symbols instead of list probably should be used something like Ordered List. But it seems there is no such
        # container in Python standard library
        self._symbols = list()
        self._symbols.extend(need_symbols)
        self._symbols.extend(exist_symbols.keys())
        self._symbols = sorted(self._symbols)
        self._codes = exist_symbols.copy()
        if len(self._symbols):
            self._cur_index = 0
        else:
            self._cur_index = None

        self._Selector = Selector
        self._sel_args = selector_args
        self._sel_kwds = selector_kwds
        super().__init__(parent, title)

    def body(self, master):
        #I think you've got a wrong door
        upper_frame = Frame(master)
        upper_frame.grid(row=1, column=1, pady=5)
        Button(upper_frame, text='<', font=header_font, width=3, command=self._on_arrowleft_click).grid(row=0, column=1)
        self._symbol_label = Label(upper_frame, font=header_font, width=4)
        self._symbol_label.grid(row=0, column=2, padx=15)
        Button(upper_frame, text='>', font=header_font, width=3, command=self._on_arrowright_click).grid(row=0, column=3)
        self._sel_kwds['master'] = master
        self._selector = self._Selector(*self._sel_args, **self._sel_kwds)
        self._selector.callback_after_click = lambda x: self._update_apply_button()
        self._selector.grid(row=2, column=1)
        right_frame = Frame(master)
        right_frame.grid(row=2, column=2, padx=10)
        Label(right_frame, text="Status:", font=header_font).pack()
        self._status_label = Label(right_frame, font=header_font, width=9)
        self._status_label.pack()
        self._index_label = Label(right_frame, font=text_font)
        self._index_label.pack()
        self._fullness_label = Label(right_frame, font=text_font)
        self._fullness_label.pack()
        Button(right_frame, text="Add", font=button_font, command=self._on_add_click).pack(fill=X, pady=2)
        Button(right_frame, text="Search", font=button_font, command=self._on_search_click).pack(fill=X, pady=2)
        Button(right_frame, text="Next undefined", font=button_font, command=self._on_nextundef_click).pack(fill=X, pady=2)
        self._apply_button = Button(right_frame, text="Apply", font=button_font, command=self._on_apply_click)
        self._apply_button.pack(fill=X, pady=2)
        Button(right_frame, text="Delete", font=button_font, command=self._on_delete_click).pack(fill=X, pady=2)
        self._update_symbol_info()

    def apply(self):
        self.result = self._codes

    def validate(self):
        if len(self._codes) == len(self._symbols):
            return 1
        else:
            answer = messagebox.askokcancel("Not full alphabet",
                                         "Selector code set not for all symbols. Return only defined symbols?")
            if answer:
                return 1
            else:
                return 0

    def _update_symbol_info(self):
        if self._cur_index is not None:
            cur_symbol = self._symbols[self._cur_index]
            self._symbol_label['text'] = '"' + cur_symbol + '"'
            if cur_symbol in self._codes:
                self._selector.set_segments_code(self._codes[cur_symbol])
                self._status_label.config(text="Defined", fg='green')
            else:
                self._selector.set_default()
                self._status_label.config(text="Undefined", fg='red')
        else:
            self._symbol_label['text'] = 'None'
            self._selector.set_default()
            self._status_label.config(text="None", fg='black')
        index = 0 if self._cur_index is None else self._cur_index + 1
        self._index_label['text'] = "Index: " + str(index) + " / " + str(len(self._symbols))
        self._fullness_label['text'] = "Fullness: " + str(len(self._codes)) + " / " + str(len(self._symbols))
        self._update_apply_button()

    def _update_apply_button(self):
        if self._cur_index is not None:
            symbol = self._symbols[self._cur_index]
            if symbol in self._codes:
                if self._selector.get_segments_code() == self._codes[symbol]:
                    self._apply_button['state'] = DISABLED
                else:
                    self._apply_button['state'] = ACTIVE
            else:
                self._apply_button['state'] = ACTIVE

    def _asksymbol(self):
        query = self._QuerySymbol("Symbol", "Enter a symbol", parent=self)
        return query.result

    def _on_arrowleft_click(self):
        if self._cur_index is not None:
            self._cur_index -= 1
            if self._cur_index < 0:
                self._cur_index = len(self._symbols) - 1
            self._update_symbol_info()

    def _on_arrowright_click(self):
        if self._cur_index is not None:
            self._cur_index += 1
            if self._cur_index >= len(self._symbols):
                self._cur_index = 0
            self._update_symbol_info()

    def _on_add_click(self):
        symbol = self._asksymbol()
        if symbol is not None:
            self._symbols.append(symbol)
            self._symbols = sorted(self._symbols)
            self._cur_index = self._symbols.index(symbol)
            self._update_symbol_info()

    def _on_search_click(self):
        symbol = self._asksymbol()
        try:
            self._cur_index = self._symbols.index(symbol)
        except ValueError:
            messagebox.showinfo("Not found", "Given symbol not in alphabet", parent=self)
        self._update_symbol_info()

    def _on_nextundef_click(self):
        for i in chain(range(self._cur_index + 1, len(self._symbols)), range(0, self._cur_index)):
            if self._symbols[i] not in self._codes:
                self._cur_index = i
                self._update_symbol_info()
                return
        messagebox.showinfo("Not found", "There is no more undefined symbols")

    def _on_apply_click(self):
        symbol = self._symbols[self._cur_index]
        self._codes[symbol] = self._selector.get_segments_code()
        self._update_symbol_info()

    def _on_delete_click(self):
        symbol = self._symbols[self._cur_index]
        del self._symbols[self._cur_index]
        if symbol in self._codes:
            del self._codes[symbol]
        if len(self._symbols) is not 0:
            if self._cur_index >= len(self._symbols):
                self._cur_index = 0
        else:
            self._cur_index = None
        self._update_symbol_info()
