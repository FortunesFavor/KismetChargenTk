import Tkinter
# import Tix
import ttk

from kisgen.model import info_keys, keys, DEFAULT, Character
from kisgen.tkutil import Menu, Item


class DataBinder(object):
    def __init__(self, root, filename=DEFAULT):
        self.root = root
        self.vars = {}
        self.load(filename)

    def __setitem__(self, name, value):
        realname = keys[name]
        self.vars[realname] = v = Tkinter.StringVar(self.root, name=realname)
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


class KisInfo(ttk.Frame):
    _fields = tuple((k, ttk.Entry) for k in info_keys)

    def make_fields(self):
        for idx, (label, field) in enumerate(self._fields):
            Label = ttk.Label(self, text=label)
            Field = field(self)
            self.data_fields[label] = Field
            Label.grid(column=0, row=idx, sticky='E')
            Field.grid(column=1, row=idx, sticky='EW')

    def __init__(self, parent, data_fields, **kw):
        ttk.Frame.__init__(self, parent, **kw)
        self.data_fields = data_fields

        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)

        self.make_fields()


class KisMain(Tkinter.Tk):
    def __init__(self, *args, **kwargs):
        Tkinter.Tk.__init__(self, *args, **kwargs)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.binder = DataBinder(self)
        self.notebook = ttk.Notebook(self)
        self.notebook.grid(column=0, row=0, sticky="NEWS")
        self.info = KisInfo(self.notebook, self.binder)
        self.notebook.add(self.info, text="Character Information")
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
