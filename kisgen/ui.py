import Tkinter
# import Tix
import ttk

from kisgen.model import info_keys, keys


class DataBinder(object):
    def __init__(self, root, data):
        self.root = root
        self.vars = {}
        self.load(data)

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

    def load(self, data):
        self.source = data
        tmp = dict.fromkeys(keys.values())
        tmp.update(data)
        for k, v in tmp.items():
            if k in self.vars:
                self.vars[k].set(v)


class KisInfo(ttk.LabelFrame):
    _fields = tuple((k, ttk.Entry) for k in info_keys)

    def make_fields(self):
        for idx, (label, field) in enumerate(self._fields):
            Label = ttk.Label(self, text=label)
            Field = field(self)
            self.data_fields[label] = Field
            Label.grid(column=0, row=idx, sticky='E')
            Field.grid(column=1, row=idx, sticky='EW')

    def __init__(self, parent, data_fields, **kw):
        ttk.LabelFrame.__init__(self, parent, **kw)
        self.data_fields = data_fields
        self.config(text="Character Information")

        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)

        self.make_fields()


if __name__ == '__main__':
    root = Tkinter.Tk()
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    df = dict()
    db = DataBinder(root, df)
    KisInfo(root, db).grid(column=0, row=0, sticky="NEWS")
    root.mainloop()
    from pprint import pprint
    pprint(df)
