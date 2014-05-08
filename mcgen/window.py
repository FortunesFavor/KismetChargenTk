from __future__ import print_function, absolute_import
from six.moves import tkinter
from six.moves import tkinter_ttk as ttk


class VarStump(object):
    '''
    All this does is store a value, and provide get and set methods.  This is
    possibly the most unpythonic code ever written, but it is here to match the
    Tkinter *Var API.
    '''
    def __init__(self, value):
        self.value = value

    def get(self):
        return self.value

    def set(self, value):
        self.value = value


class DataTracker(object):
    def __init__(self, reset=None, load=None):
        self.reset_method = reset
        self.load_method = load
        self._data = {}

    def register(self, key, varobj):
        self._data[key] = varobj

    def unregister(self, key):
        if key in self._data:
            del self._data[key]

    def collect(self):
        out = {}
        for key, var in self._data:
            out[key] = var.get()
        return out


class Skill(object):
    def __init__(self, parent, ability, name, level):
        self.parent = parent
        self.ability = ttk.Label(parent.skill_frame, text=ability)
        self.name = ttk.Label(parent.skill_frame, text=name)
        self.level = tkinter.IntVar(value=int(level))
        self.field = self._level_field()
        self.button = self._del_button()

    def _level_field(self):
        field = tkinter.Spinbox(
            self.parent.skill_frame,
            from_=0,
            to=10,
            increment=1,
            textvariable=self.level,
        )
        return field

    def _del(self):
        self.parent.remove_skill(self)
        self.destroy()

    def _del_button(self):
        button = ttk.Button(
            self.parent.skill_frame, text="Delete", command=self._del
        )
        return button

    def insert(self, row):
        self.ability.grid(column=0, row=row)
        self.name.grid(column=1, row=row)
        self.field.grid(column=2, row=row)
        self.button.grid(column=3, row=row)

    def remove(self):
        self.ability.grid_forget()
        self.name.grid_forget()
        self.field.grid_forget()
        self.button.grid_forget()

    def destroy(self):
        self.ability.destroy()
        self.name.destroy()
        self.field.destroy()
        self.button.destroy()


class MainWindow(ttk.Frame, object):
    def __init__(self, **kwargs):
        self.root = tkinter.Tk()
        self.root.title("Character Manager")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.mainloop = self.root.mainloop
        ttk.Frame.__init__(self, master=self.root, **kwargs)
        self.grid(column=0, row=0, sticky=tkinter.NSEW)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)
        self['padding'] = 5
        self._skills = []
        self.make_menu()

        # Top left frame
        self.aspect_frame = ttk.LabelFrame(self, text="Concept and Aspects")
        self.aspect_frame.grid(column=0, row=0, sticky=tkinter.NSEW)
        self.aspect_frame.columnconfigure(0, weight=0)
        self.aspect_frame.columnconfigure(1, weight=1)
        row = self.make_charname(parent=self.aspect_frame, row=0)
        row = self.make_concept(parent=self.aspect_frame, row=row)
        row = self.make_aspects(parent=self.aspect_frame, row=row)

        # Top right frame
        self.ability_frame = ttk.LabelFrame(self, text="Level and Abilities")
        self.ability_frame.grid(column=1, row=0, sticky=tkinter.NSEW)
        self.ability_frame.columnconfigure(0, weight=0)
        self.ability_frame.columnconfigure(1, weight=1)
        row = self.make_level(parent=self.ability_frame, row=0)
        row = self.make_abilities(parent=self.ability_frame, row=row)

        # middle frame
        self.skill_frame = ttk.LabelFrame(self, text="Skills")
        self.skill_frame.grid(
            column=0, row=1, columnspan=2, sticky=tkinter.NSEW,
        )
        self.skill_frame.columnconfigure(1, weight=1)
        self.make_skill_addsub(self.skill_frame)

        # bottom frame
        self.stunt_frame = ttk.LabelFrame(self, text="Powers/Stunts")
        self.stunt_frame.grid(
            column=0, row=2, columnspan=2, sticky=tkinter.NSEW,
        )
        ttk.Label(self.stunt_frame, text='BAR!').grid(column=0, row=0)

    def add_skill(self):
        ability = self._as_ability.get()
        name = self._as_name.get()
        level = int(self._as_level.get())
        if not name and not ability:
            return
        self._as_ability.set('')
        self._as_name.set('')
        self._as_level.set(0)
        newskill = Skill(self, ability, name, level)
        self._clear_skills()
        self._skills.append(newskill)
        self._render_skills()

    def remove_skill(self, skill):
        if skill in self._skills:
            self._clear_skills()
            self._skills.remove(skill)
            self._render_skills()

    def _clear_skills(self):
        for skill in self._skills:
            skill.remove()

    def _render_skills(self):
        for row, skill in enumerate(
            sorted(self._skills, key=lambda x: x.ability),
            start=1,
        ):
            skill.insert(row)

    def make_skill_addsub(self, parent=None, row=999):
        parent = self if parent is None else parent
        self._as_ability = ability = tkinter.StringVar()
        ability_select = ttk.Combobox(
            parent, textvariable=ability, state='readonly',
        )
        ability_select['values'] = ['Body', 'Reflexes', 'Wits', 'Persona']
        ability_select.grid(column=0, row=row, sticky=tkinter.E)
        ability_label = ttk.Label(parent, text="Root Ability")
        ability_label.grid(column=0, row=0, sticky=tkinter.EW)
        self._as_name = skillname = tkinter.StringVar()
        skillname_field = ttk.Entry(parent, textvariable=skillname)
        skillname_field.grid(column=1, row=row, sticky=tkinter.EW)
        skillname_label = ttk.Label(parent, text='Skill Name')
        skillname_label.grid(column=1, row=0, sticky=tkinter.EW)
        self._as_level = skilllev = tkinter.IntVar(value=0)
        skilllev_field = tkinter.Spinbox(
            parent, from_=0, to=10, increment=1, textvariable=skilllev,
        )
        skilllev_field.grid(column=2, row=row, sticky=tkinter.W)
        skilllev_label = ttk.Label(parent, text="Skill Level")
        skilllev_label.grid(column=2, row=0, sticky=tkinter.EW)
        add_button = ttk.Button(parent, text='Add', command=self.add_skill)
        add_button.grid(column=3, row=row)

    def make_charname(self, parent=None, row=0):
        parent = self if parent is None else parent
        self.name_label = ttk.Label(parent, text="Character Name:")
        self.name_label.grid(column=0, row=row, sticky=tkinter.E)
        self.name = tkinter.StringVar()
        self.name_field = ttk.Entry(parent, textvariable=self.name)
        self.name_field.grid(column=1, row=row, sticky=tkinter.EW)
        return row+1

    def make_concept(self, parent=None, row=0):
        parent = self if parent is None else parent
        self.concept_label = ttk.Label(parent, text="High Concept:")
        self.concept_label.grid(column=0, row=row, sticky=tkinter.E)
        self.concept = tkinter.StringVar()
        self.concept_field = ttk.Entry(parent, textvariable=self.concept)
        self.concept_field.grid(column=1, row=row, sticky=tkinter.EW)
        return row+1

    def make_aspects(self, parent=None, row=0):
        parent = self if parent is None else parent
        aspects = [
            'Ambition',
            'Background',
            'Conviction',
            'Disadvantage',
            'Exceptional Skill',
            'Foe',
            'Gear',
            'Help',
            'Inferior Skill',
        ]
        for row, aspect in enumerate(aspects, start=row):
            aid = aspect.replace(' ', '_').lower()
            a_label = 'aspect_{0}_label'.format(aid)
            a_field = 'aspect_{0}_field'.format(aid)
            a_value = 'aspect_{0}'.format(aid)
            label_text = '{0} Aspect:'.format(aspect)

            label = ttk.Label(parent, text=label_text)
            label.grid(column=0, row=row, sticky=tkinter.E)
            value = tkinter.StringVar()
            field = ttk.Entry(parent, textvariable=value)
            field.grid(column=1, row=row, sticky=tkinter.EW)
            setattr(self, a_label, label)
            setattr(self, a_field, field)
            setattr(self, a_value, value)
        return row+1

    def make_level(self, parent=None, row=0):
        parent = self if parent is None else parent
        self.level_label = ttk.Label(parent, text="Level:")
        self.level_label.grid(column=0, row=row, sticky=tkinter.E)
        self.level = tkinter.IntVar(value=1)
        self.level_field = tkinter.Spinbox(
            parent, from_=1, to=20, increment=1, textvariable=self.level,
        )
        self.level_field.grid(column=1, row=row, sticky=tkinter.EW)
        row += 1
        self.edge_label = ttk.Label(parent, text="Edge:")
        self.edge_label.grid(column=0, row=row, sticky=tkinter.E)
        self.edge = self.level
        self.edge_field = ttk.Label(parent, textvariable=self.edge)
        self.edge_field.grid(column=1, row=row, sticky=tkinter.W)
        row += 1
        self.stamina_label = ttk.Label(parent, text="Stamina:")
        self.stamina_label.grid(column=0, row=row, sticky=tkinter.E)
        self.stamina = tkinter.IntVar(value=20)
        self.stamina_field = ttk.Label(parent, textvariable=self.stamina)
        self.stamina_field.grid(column=1, row=row, sticky=tkinter.W)

        def level_trace(*args):
            varname, _, mode = args
            if varname == str(self.level):
                self.stamina.set(self.level.get() * 20)

        self.level.trace('w', level_trace)
        self.level.trace('r', level_trace)
        return row+1

    def make_abilities(self, parent=None, row=0):
        parent = self if parent is None else parent
        abilities = [
            'Body',
            'Reflexes',
            'Wits',
            'Persona',
        ]
        for row, ability in enumerate(abilities, start=row):
            aid = ability.lower()
            a_label = 'ability_{0}_label'.format(aid)
            a_field = 'ability_{0}_field'.format(aid)
            a_value = 'ability_{0}'.format(aid)
            label_text = '{0}:'.format(ability)

            label = ttk.Label(parent, text=label_text)
            label.grid(column=0, row=row, sticky=tkinter.E)
            value = tkinter.IntVar()
            field = tkinter.Spinbox(
                parent, from_=0, to=5, increment=1, textvariable=value,
            )
            field.grid(column=1, row=row, sticky=tkinter.EW)
            setattr(self, a_label, label)
            setattr(self, a_field, field)
            setattr(self, a_value, value)
        return row+1

    def make_menu(self):
        self.root.option_add('*tearOff', tkinter.FALSE)
        self.menu = tkinter.Menu(self.root)
        self.root['menu'] = self.menu
        self.menu_file = tkinter.Menu(self.menu)
        self.menu.add_cascade(menu=self.menu_file, label='File')
        self.menu_file.add_command(label='New', command=lambda *p: None)
        self.menu_file.add_command(label='Open...', command=lambda *p: None)
        self.menu_file.add_command(label='Save', command=lambda *p: None)
        self.menu_file.add_command(label='Save As...', command=lambda *p: None)
        self.menu_file.add_separator()
        self.menu_file.add_command(label='Exit', command=lambda *p: None)


def main(argv):
    root = MainWindow()
    root.mainloop()
