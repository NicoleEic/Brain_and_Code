import os
import pandas as pd
from pandas import ExcelWriter
from random import shuffle
import pdb
try:
    import Tkinter as Tk
except ImportError:
    import tkinter as Tk
import tkFont
import tkMessageBox
from xpinyin import Pinyin
from tkinter.filedialog import askopenfilename
from cjklib.reading import ReadingFactory
import unicodedata
import sys
import math
import webbrowser

pd.options.mode.chained_assignment = None  # default='warn'


def to_tone_number(s):
    table = {0x304: ord('1'), 0x301: ord('2'), 0x30c: ord('3'), 0x300: ord('4')}
    return unicodedata.normalize('NFD', s).translate(table)

class NTrain(Tk.Tk):
    def __init__(self, *args, **kwargs):
        Tk.Tk.__init__(self, *args, **kwargs)
        self.title("Ntrain")
        # place window in the center
        self.eval('tk::PlaceWindow %s center' % self.winfo_pathname(self.winfo_id()))
        self._default_font = tkFont.nametofont("TkDefaultFont")
        self._default_font.configure(size=30)
        # define default dataset
        self._defaultfile = 'chinese100.xlsx'

        # load default filename into label
        basename = os.path.basename(self._defaultfile)
        self._filename_value = Tk.StringVar()
        self._sett_fn_label = Tk.Entry(textvariable=self._filename_value, font=self._default_font, width=12)
        self._filename_value.set(basename)
        self._sett_fn_label.grid(row=1, column=0, sticky=Tk.W)

        # button to browse for datafile
        self.browse = Tk.Button(self, text="Browse", command=self._get_file)
        self.browse.grid(row=1, column=1, sticky=Tk.W)

        # OK button to start game
        self._reset_button = Tk.Button(text="Reset", command=self._reset_list)
        self._reset_button.grid(row=1, column=2)

        # label
        self._sett_label = Tk.Label(text="Number of Cards:")
        self._sett_label.grid(row=2, column=0, sticky=Tk.E)

        # entry field for number of cards
        entryText = Tk.StringVar()
        self._sett_entry = Tk.Entry(textvariable=entryText, font=self._default_font, width=3)
        entryText.set("30")
        self._sett_entry.grid(row=2, column=1, sticky=Tk.W)
        self._sett_entry.focus_set()

        # reverse option
        self._radio_val = Tk.IntVar()
        self._radio1 = Tk.Radiobutton(text="Ch to E", variable=self._radio_val, value=1)
        self._radio1.grid(row=4, column=0)
        self._radio2 = Tk.Radiobutton(text="E to Ch", variable=self._radio_val, value=2)
        self._radio2.grid(row=4, column=1)
        self._radio_val.set(1)

        # OK button to start game
        self._sett_button = Tk.Button(text="OK", command=self._start_game)
        self._sett_button.grid(columnspan=3)

        # Bind return key to start game
        self.bind('<Return>', self._start_game)

        self._p = Pinyin()
        self._f = ReadingFactory()

    def _get_file(self):
        # open dialogue to chose datafile
        my_file = askopenfilename()
        # update label to show filename in gui
        self._filename_value.set(os.path.basename(my_file))

    def _start_game(self, *args):
        # get filname
        self._datafile = os.path.dirname(self._defaultfile) + os.sep + self._filename_value.get()

        # get number of cards
        self._n_cards = int(self._sett_entry.get())
        # remove previous gui components
        self._sett_fn_label.destroy()
        self.browse.destroy()
        self._reset_button.destroy()
        self._sett_label.destroy()
        self._sett_entry.destroy()
        self._sett_button.destroy()
        self._radio1.destroy()
        self._radio2.destroy()

        self._save_reminder = 0
        # load in data file
        try:
            self._vocTot = pd.read_excel(self._datafile)
        except:
            tkMessageBox.showinfo("Error", "File not found!", icon='warning')
            self._restart()

        # get indices of all filled cards
        #pdb.set_trace()
        filled_idx = self._vocTot[self._vocTot['Learned'] == 0].index.tolist()
        del filled_idx[0]
        # shuffle indices
        self._renew_index(filled_idx)
        # setup new gui
        self._setup_game_gui()
        # start with first question
        self._show_next_question()

    def _setup_game_gui(self):
        # label for Question
        #self._label_value = Tk.StringVar()
        #self._label = Tk.Label(textvariable=self._label_value)
        #self._label.grid(row=1, column=2)

        # label for chinese symbols
        #self._C_label_value = Tk.StringVar()
        #self._C_label = Tk.Label(textvariable=self._C_label_value)
        #self._C_label.grid(row=2, column=2)
        self.C_labels = []
        self.Q_labels = []

        # label for correct solution
        self._sol_label_value = Tk.StringVar()
        self._sol_label = Tk.Label(textvariable=self._sol_label_value)
        self._sol_label.grid(row=3, column=2)

        # entry field for answer
        self._entry_value = Tk.StringVar()
        self._entry = Tk.Entry(textvariable=self._entry_value, font=self._default_font)
        self._entry.grid(row=4, column=2)
        self._entry.focus_set()
        self.bind('<Return>', self._check_answer)

        # Check button
        self._check_button = Tk.Button(text="Check", command=self._check_answer)
        self._check_button.grid(row=1, column=1, sticky=Tk.W)

        # Save button
        self._save_button = Tk.Button(text="Save", command=self._save)
        self._save_button.grid(row=2, column=1, sticky=Tk.W)

        # Next button
        self._next_button = Tk.Button(text="Next", command=self._show_next_question)
        self._next_button.grid(row=3, column=1, sticky=Tk.W)

        # New button
        self._new_button = Tk.Button(text="New", command=self._restart)
        self._new_button.grid(row=4, column=1, sticky=Tk.W)

        # translate field
        self._tr_value = Tk.StringVar()
        self._tr = Tk.Entry(textvariable=self._tr_value, font=self._default_font)
        self._tr.grid(row=5, column=2)

        self._tr_button = Tk.Button(text="E-C", command=self._translate)
        self._tr_button.grid(row=5, column=1, sticky=Tk.W)

        # initialize list of wrong cards
        self._wrong_indices = []
        # initialize current index
        self._no = 0

    def _renew_index(self, indices):
        # pdb.set_trace()
        # TODO: catch too many cards chosen as input
        shuffle(indices)
        # take the first n cards
        self._indices = indices[0:self._n_cards]

    def _show_next_question(self):
        try:
            #pdb.set_trace()
            # get the next index in the list
            self._no = self._indices.pop(0)

            # empty entry field
            self._entry_value.set("")
            # empty Q and C labels
            for i in self.C_labels:
                i.destroy()
            for i in self.Q_labels:
                i.destroy()
            i = 1
            self.C_labels = []
            self.Q_labels = []

            # loop over Chinese characters
            for char in self._vocTot.C[self._no]:
                my_pinyin = self._p.get_pinyin(char, ' ', show_tone_marks=True)
                self.C_labels.append(Tk.Label(text=char))
                self.C_labels[-1].grid(row=2, column=i + 1)
                to_tone = (to_tone_number(my_pinyin))
                if "1" in to_tone:
                    self.C_labels[-1].config(fg='red')
                elif "2" in to_tone:
                    self.C_labels[-1].config(fg='green')
                elif "3" in to_tone:
                    self.C_labels[-1].config(fg='blue')
                elif "4" in to_tone:
                        self.C_labels[-1].config(fg='purple')
                else:
                    self.C_labels[-1].config(fg='grey')
                if self._radio_val.get() == 1:
                    self.Q_labels.append(Tk.Label(text=my_pinyin))
                    self.Q_labels[-1].grid(row=1, column=i + 1)
                i += 1

            if self._radio_val.get() == 1:
                self._curr_ans = self._vocTot.E[self._no].encode('utf-8')
            elif self._radio_val.get() == 2:
                #pdb.set_trace()
                try:
                    my_english = self._vocTot.E_long[self._no].encode('utf-8')
                except:
                    my_english = self._vocTot.E[self._no].encode('utf-8')
                self.Q_labels.append(Tk.Label(text=my_english))
                self.Q_labels[-1].grid(row=1, column=2, columnspan=i - 1)
                self._curr_ans = self._p.get_pinyin(self._vocTot.C[self._no], ' ', show_tone_marks=True)

            self._entry.grid(row=4, column=2, columnspan=i - 1)

            # set real_correct to default value of yes
            self._real_correct = 1
        except IndexError:
            # start new round, when no card in list left
            self._new_round()

    def _check_answer(self, *args):

        # derive input
        answer = self._entry_value.get().strip().lower()

        # convert numbers, if provided, to pinjin tone mark
        tone = 0
        if any(char.isdigit() for char in answer):
            tone = 1
            answer = self._f.convert(answer, 'Pinyin', 'Pinyin', sourceOptions={'toneMarkType': 'numbers'}).encode('utf-8')

        # derive expected answer
        # ask for English word
        if self._radio_val.get() == 1:
            answer_to_check = self._curr_ans.encode('utf-8').lower()
        # ask for Chinese word
        elif self._radio_val.get() == 2:
            # pinyin with tone marks
            if tone == 1:
                answer_to_check = self._p.get_pinyin(self._vocTot.C[self._no], ' ', show_tone_marks=True).encode('utf-8').lower()
            # pinyin without tone marks
            else:
                answer_to_check = self._p.get_pinyin(self._vocTot.C[self._no], ' ', show_tone_marks=False).encode('utf-8').lower()

        # check if answer is correct
        if answer == answer_to_check:
            # if correct: move to 'learned' columns
            # move columns if card was correct on first attempt
            if self._real_correct:
                self._vocTot.Learned[self._no] = 1
                self._save_reminder = 1

            self._sol_label_value.set("")
            # if correct, go on to next card
            self._show_next_question()
        else:
            # if wrong:
            self._real_correct = 0
            # store index in list of wrong cards
            self._wrong_indices.append(self._no)
            # display correct answer
            self._sol_label_value.set(self._curr_ans)
            self._sol_label.grid(row=3, column=2, columnspan=len(self.C_labels))
            # clear entry field
            self._entry_value.set("")

    def _new_round(self):
        #pdb.set_trace()
        # if wrong cards still left, start new round
        if self._wrong_indices:
            # empty all display fields
            self._sol_label_value.set("New round!")
            self._renew_index(self._wrong_indices)
            # clear list of wrong indices
            self._wrong_indices = []
            # start new round with the next question
            self._show_next_question()
        else:
            # if no wrong cards left, finish the session
            self._exit()

    def _reset_list(self):
        self._datafile = os.path.dirname(self._defaultfile) + os.sep + self._filename_value.get()
        my_file = pd.read_excel(self._datafile)
        my_file['Learned'] = 0
        writer = ExcelWriter(self._datafile)
        my_file.to_excel(writer, 'Sheet1', index=False)
        writer.save()

    def _exit(self):
        try:
            self._save()
        except:
            self._sol_label_value.set("Didn't work?!")
            return
        self._sol_label_value.set("")
        self._entry_value.set("")
        self._sol_label_value.set("Done!")
        self._check_button['state'] = 'disabled'
        self._save_button['state'] = 'disabled'
        self.unbind('<Return>')
        self._next_button['state'] = 'disabled'

    def _save(self, *args):
        writer = ExcelWriter(self._datafile)
        self._vocTot.to_excel(writer, 'Sheet1', index=False)
        writer.save()
        self._sol_label_value.set("Saved!")
        self._sol_label.grid(row=3, column=2, columnspan=len(self.C_labels))
        self._save_reminder = 0

    def _restart(self):
        if self._save_reminder:
            result = tkMessageBox.askquestion("Warning", "Save before exiting?")
            if result == 'yes':
                try:
                    self._save()
                except:
                    self._sol_label_value.set("Didn't work?!")
                    return
        python = sys.executable
        os.execl(python, python, * sys.argv)

    def _translate(self):
        to_translate = self._tr_value.get()
        if isinstance(to_translate, unicode):
            #pdb.set_trace() # doesn't work
            url = 'https://translate.google.com/#zh-CN/en/' + to_translate
        else:
            to_translate = to_translate.replace(' ', '%20')
            url = 'https://translate.google.com/#en/zh-CN/' + to_translate
        webbrowser.open(url)



def callback():
    if tkMessageBox.askokcancel("Quit", "Do you really wish to quit? \nUnsaved changes may be lost."):
        root.destroy()

if __name__ == "__main__":
    root = NTrain()
    root.protocol("WM_DELETE_WINDOW", callback)
    root.mainloop()
