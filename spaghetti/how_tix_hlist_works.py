import Tkinter
import ttk
import Tix
import collections

attrs = collections.OrderedDict((
    ('Body', 'body'),
    ('Reflexes', 'reflexes'),
    ('Wits', 'wits'),
    ('Persona', 'persona'),
))

Skill = collections.namedtuple('Skill', 'name var')


class KisStat(ttk.Frame):
    def __init__(self, master, **kw):
        ttk.Frame.__init__(self, master, **kw)
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=0)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=0)

        self.skilltree = sk = Tix.HList(
            self,
            columns=2,
            separator='\x7F',
            indent=18,
        )
        sk.grid(column=0, row=0, columnspan=3, sticky='NEWS')
        sksc = ttk.Scrollbar(self, orient='vertical')
        sksc.grid(column=3, row=0, sticky='WNS')
        sk['yscrollcommand'] = sksc.set
        sksc['command'] = sk.yview

        self.attrs = collections.OrderedDict(
            (k, Tkinter.IntVar(sk)) for k in attrs
        )
        self.skills = collections.defaultdict(collections.OrderedDict)

        self.sk_add_attr = Tkinter.StringVar(self)
        as_attr = ttk.Combobox(
            self,
            textvariable=self.sk_add_attr,
            values=attrs.keys(),
            state='readonly',
            width=(max(len(x) for x in attrs) + 1),
        )
        as_attr.grid(column=0, row=1, sticky='EW')
        as_attr.current(0)

        self.sk_add_skill = Tkinter.StringVar(self)
        as_name = ttk.Entry(self, textvariable=self.sk_add_skill)
        as_name.grid(column=1, row=1, sticky='EW')

        as_add = ttk.Button(self, text='Add', width=4, command=self.add_button)
        as_add.grid(column=2, row=1, sticky='EW')

        for k, v in self.attrs.items():
            self.add_item(k, v)

    def add_item(self, path, var):
        control = Tix.Control(self.skilltree, variable=var)
        self.skilltree.add(path, text=path.split('\x7F')[-1])
        self.skilltree.item_create(
            path, col=1, itemtype='window', window=control,
        )

    def add_button(self):
        attr = self.sk_add_attr.get()
        name = self.sk_add_skill.get()
        self.add_skill(attr, name)

    def add_skill(self, attr, name):
        path = '%s\x7F%s' % (attr, name)
        v = Tkinter.IntVar(self.skilltree)
        self.skills[attr][name] = v
        self.add_item(path, v)


root = Tix.Tk()
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

# bskill1var = Tkinter.IntVar(hl, value=2)
# bskill1 = Tix.Control(hl, variable=bskill1var)
# hl.add('body/bskill1', text='Lift/Carry/Haul')
# hl.item_create('body/bskill1', col=1, itemtype='window', window=bskill1)
# hl.grid(sticky='NEWS')

ks = KisStat(root)
ks.grid(sticky='NEWS')
root.mainloop()
