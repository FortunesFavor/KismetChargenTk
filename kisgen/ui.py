import Tkinter
import Tix
import ttk


class KisInfo(ttk.Frame):
    _aspects = (
        'Ambition',
        'Background',
        'Conviction',
        'Disadvantage',
        'Exceptional Skill',
        'Foe',
        'Gear',
        'Help',
        'Inferior Skill',
    )

    def __init__(self, parent, aspects=None, **kw):
        ttk.Frame.__init__(self, parent, **kw)
        self.aspects = aspects if aspects is not None else self._aspects
        self.fields = dict()

        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=0)
        self.columnconfigure(3, weight=1)

        # Name field
        name_label = ttk.Label(self, text="Name")
        name_label.grid(column=0, row=0, sticky="E")
        self.fields['Name'] = name = ttk.Entry(self)
        name.grid(column=1, row=0, sticky="EW")

        # Concept field
        con_label = ttk.Label(self, text="Concept")
        con_label.grid(column=0, row=1, sticky="E")
        self.fields['Concept'] = con = ttk.Entry(self)
        con.grid(column=1, row=1, sticky="EW")

        # Age field
        age_label = ttk.Label(self, text="Age")
        age_label.grid(column=0, row=2, sticky="E")
        self.fields['Age'] = age = Tix.Control(
            self, step=1, min=1, integer=True,
        )
        age.grid(column=1, row=2, sticky="W")

        # Description field
        desc_label = ttk.Label(self, text="Description")
        desc_label.grid(column=0, row=3, sticky="E")
        desc = Tkinter.Text(self, wrap='word', height=1, width=1)
        desc.grid(column=1, row=3, rowspan=4, sticky="NEWS")
        self.fields['Description'] = desc

        # Level field
        level_label = ttk.Label(self, text="Level")
        level_label.grid(column=0, row=7, sticky="E")
        self.fields['Level'] = level = Tix.Control(
            self, step=1, min=1, max=20, integer=True,
        )
        level.grid(column=1, row=7, sticky="W")

        # Armor field
        # armor_label = ttk.Label(self, text="Armored")
        # armor_label.grid(column=0, row=8)
        self.fields['Armor'] = armor = ttk.Checkbutton(
            self,
            text="Has Armor",
        )
        armor.grid(column=1, row=8, sticky="W")

        for idx, aspect in enumerate(self.aspects):
            a = '%s Aspect' % (aspect,)
            ttk.Label(self, text=a).grid(column=2, row=idx, sticky="E")
            self.fields[a] = f = ttk.Entry(self)
            f.grid(column=3, row=idx, sticky="EW")


if __name__ == '__main__':
    root = Tix.Tk()
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    KisInfo(root).grid(column=0, row=0, sticky="NEWS")
    root.mainloop()
