import Tkinter
import Tix
import ttk

from functools import partial

from kisgen.model import info_keys, keys, DEFAULT, Character, stat_keys
from kisgen.tkutil import Menu, Item


class DataBinder(object):
    def __init__(self, root, filename=DEFAULT):
        self.root = root
        self.vars = {}
        self.load(filename)

    def __setitem__(self, name, value):
        realname = keys[name]
        self.vars[realname] = v = Tkinter.StringVar(self.root, name=realname)
        if isinstance(value, Tix.Control):
            value.config(variable=v)
        else:
            value.config(textvariable=v)
        self._trace(v)

    def _trace(self, sv):
        sv.trace(
            mode='w',
            callback=(lambda name, i, m: self.update(name, sv))
        )

    def update(self, name, sv):
        self.source[name] = sv.get()

    def load(self, filename=DEFAULT):
        self.source = Character.loadfile(filename)
        tmp = dict.fromkeys(keys.values())
        tmp.update(self.source)
        for k, v in tmp.items():
            if k in self.vars:
                self.vars[k].set(v)


class KisFrame(ttk.Frame):
    _fields = None

    def __init__(self, parent, binder, **kw):
        ttk.Frame.__init__(self, parent, **kw)
        self.binder = binder
        self.col_conf()
        self.make_fields()

    def col_conf(self):
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)

    def grid_field(self, idx, label, field):
        label.grid(column=0, row=idx, sticky='E')
        field.grid(column=1, row=idx, sticky='EW')

    def make_fields(self):
        if self._fields is None:
            raise TypeError()

        for idx, (label, field) in enumerate(self._fields):
            Label = ttk.Label(self, text=label)
            Field = field(self)
            self.binder[label] = Field
            self.grid_field(idx, Label, Field)


class KisInfo(KisFrame):
    _fields = tuple((k, ttk.Entry) for k in info_keys)


class KisStat(KisFrame):
    _fields = tuple(
        (k, partial(
            Tix.Control,
            integer=True,
            min=0,
            max=5,
        )) for k in stat_keys
    )

    def col_conf(self):
        for col in xrange(8):
            self.columnconfigure(col, weight=0 if col % 2 == 0 else 1)

    def grid_field(self, idx, label, field):
        lcol = idx * 2
        fcol = lcol + 1
        label.grid(column=lcol, row=0, sticky='E')
        field.grid(column=fcol, row=0, sticky='EW')


class KisBook(ttk.Notebook):
    def __init__(self, master, binder, **kw):
        ttk.Notebook.__init__(self, master=master, **kw)
        self.binder = binder
        self.infopage = KisInfo(self, self.binder)
        self.add(self.infopage, text="Character Information")
        self.statpage = KisStat(self, self.binder)
        self.add(self.statpage, text="Stats")


class KisMain(Tix.Tk):
    def __init__(self, *args, **kwargs):
        Tix.Tk.__init__(self, *args, **kwargs)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.binder = DataBinder(self)
        self.notebook = KisBook(self, self.binder)
        self.notebook.grid(column=0, row=0, sticky="NEWS")
        menu_def = Menu(
            None,
            Menu(
                'File',
                Item('New'),
                Item('Open...'),
                Item('Save'),
                Item('Save As...'),
                Menu(
                    'Export',
                    Item('Text'),
                    Item('PDF'),
                ),
                Item('Exit'),
            )
        )
        self.menu = menu_def.build(self)


if __name__ == '__main__':
    root = KisMain()
    root.mainloop()
