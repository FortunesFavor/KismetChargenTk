from __future__ import print_function, absolute_import
import Tkinter
import ttk
import sys
import collections
import textwrap
import tkFileDialog
import tkMessageBox

import yaml
from ptemplate.formatter import Formatter

TEMPLATE = """{name}

High Concept              - {concept}
Ambition Aspect           - {aspect_ambition}
Background Aspect         - {aspect_background}
Conviction Aspect         - {aspect_conviction}
Disadvantage Aspect       - {aspect_disadvantage}
Exceptional Skill Aspect  - {aspect_exceptional_skill}
Foe Aspect                - {aspect_foe}
Gear Aspect               - {aspect_gear}
Help Aspect               - {aspect_help}
Inferior Skill Aspect     - {aspect_inferior_skill}


Level      [{level}]
Stamina    [{stamina}]
Edge       [{level}]

Health
{#armor}    [Armor tier {tier}]
{/armor}    [Healthy]
    [Injured]
    [Wounded]
    [Incapacitated]

{#abilities}
{name:<28}[{level}]{#skills}
    {name:<24}[{level}]{/skills}
{/abilities}

Stunts/Powers{#stunts}
    {name}\n{description}
{/stunts}"""


def aspect_wrap(text):
    _indent = dict(
        initial_indent=(' ' * 28),
        subsequent_indent=(' ' * 28),
    )
    lines = textwrap.wrap(text, 80, **_indent)
    return '\n'.join(lines).lstrip()


def stunt_wrap(text):
    _indent = dict(
        initial_indent=(' ' * 8),
        subsequent_indent=(' ' * 8),
    )
    in_lines = filter(None, text.splitlines())
    out_text = []
    for line in in_lines:
        lines = textwrap.wrap(line, 80, **_indent)
        out_text.append('\n'.join(lines))
    return '\n\n'.join(out_text)


class VarStump(object):
    '''
    All this does is store a value, and provide get and set methods.  This is
    possibly the most unpythonic code ever written, but it is here to match the
    Tkinter *Var API.
    '''
    def __init__(self, value):
        self.value = value

    def get(self):
        """
        Stumps happily give you their value.
        """
        return self.value

    def set(self, value):
        """
        Quietly ignore .set - Stumps are as immutable as they are hard to pull
        from the ground.
        """

    def trace_variable(self, *p, **k):
        raise NotImplementedError(
            'I am a stump, not a Tkinter *Var.  '
            'There are some things I just cant do, tracing is one of them.'
        )

    trace = trace_vinfo = trace_vdelete = trace_variable


class DataTracker(object):
    def __init__(self, reset=None, skill_load=None, stunt_load=None):
        self.reset_method = reset
        self.skill_load_method = skill_load
        self.stunt_load_method = stunt_load
        self._data = collections.OrderedDict()

    def register(self, key, varobj):
        self._data[key] = varobj

    def unregister(self, key):
        if key in self._data:
            del self._data[key]

    def collect(self):
        out = collections.OrderedDict()
        for key, var in self._data.items():
            out[key] = var.get()
        return out

    def reset(self):
        for key, val in self._data.items():
            if isinstance(val, Tkinter.IntVar):
                self._data[key].set(0)
            else:
                self._data[key].set('')

    def to_template(self):
        data = self.collect()
        body = dict(name='Body', level=data['ability_body'], skills=[])
        reflexes = dict(
            name='Reflexes', level=data['ability_reflexes'], skills=[]
        )
        wits = dict(name='Wits', level=data['ability_wits'], skills=[])
        persona = dict(
            name='Persona', level=data['ability_persona'], skills=[]
        )
        abilities = [body, reflexes, wits, persona]
        amap = dict(Body=body, Reflexes=reflexes, Wits=wits, Persona=persona)
        template_data = dict(abilities=abilities)
        stunts = template_data['stunts'] = []
        for key, val in data.items():
            if key.startswith('ability_'):
                continue
            elif key.startswith('skill|'):
                _, aname, sname = key.split('|')
                skill = {'name': sname, 'level': val}
                amap[aname]['skills'].append(skill)
            elif key.startswith('stunt|'):
                _, stunt = key.split('|')
                val = stunt_wrap(val)
                stunt = {'name': stunt, 'description': val}
                stunts.append(stunt)
            elif key == 'armor':
                val = [{'tier': x} for x in range(int(val), 0, -1)]
                template_data['armor'] = val
            elif key.startswith('aspect_') or key == 'concept':
                val = aspect_wrap(val)
                template_data[key] = val
            elif key == 'level':
                template_data['stamina'] = int(val) * 20
                template_data[key] = val
            else:
                template_data[key] = val
        return template_data

    def load(self, data):
        if self.reset_method:
            self.reset_method()
        skills = []
        stunts = []
        for key, val in data.items():
            if key.startswith('stunt|'):
                _, name = key.split('|')
                stunts.append((name, val))
            elif key.startswith('skill|'):
                _, ability, name = key.split('|')
                skills.append((ability, name, val))
            elif key in self._data:
                self._data[key].set(val)
        if self.skill_load_method:
            self.skill_load_method(skills)
        if self.stunt_load_method:
            self.stunt_load_method(stunts)


class Skill(object):
    def __init__(self, parent, ability, name, level):
        self.parent = parent
        self.ability = ttk.Label(parent.skill_frame, text=ability)
        self.name = ttk.Label(parent.skill_frame, text=name)
        self.level = Tkinter.IntVar(value=int(level))
        self.field = self._level_field()
        self.button = self._del_button()
        self.skill_name = 'skill|{0}|{1}'.format(ability, name)
        parent._total_register(self.skill_name, self.level)
        parent.data.register(self.skill_name, self.level)

    def _level_field(self):
        field = Tkinter.Spinbox(
            self.parent.skill_frame,
            from_=0,
            to=10,
            increment=1,
            textvariable=self.level,
            width=4,
            state='readonly',
        )
        return field

    def _del(self):
        self.parent.remove_skill(self)
        self.parent._total_unregister(self.skill_name)
        self.destroy()
        self.parent.data.unregister(self.skill_name)

    def _del_button(self):
        button = ttk.Button(
            self.parent.skill_frame, text="Delete", command=self._del
        )
        return button

    def insert(self, row):
        self.ability.grid(column=0, row=row, sticky='w')
        self.name.grid(column=1, row=row, sticky='w')
        self.field.grid(column=2, row=row, sticky='ew')
        self.button.grid(column=3, row=row, sticky='ew')

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


class Stunt(object):
    def __init__(self, parent, name, description):
        description = str(description).strip()
        self.parent = parent
        self.name = ttk.Label(parent.stunt_frame, text=name)
        self.description = ttk.Label(parent.stunt_frame, text=description)
        self.button = self._del_button()
        self.stunt_name = 'stunt|{0}'.format(name)
        self._stump = VarStump(description)
        parent.data.register(self.stunt_name, self._stump)

    def _del(self):
        self.parent.remove_stunt(self)
        self.destroy()
        self.parent.data.unregister(self.stunt_name)

    def _del_button(self):
        button = ttk.Button(
            self.parent.stunt_frame, text="Delete", command=self._del
        )
        return button

    def insert(self, row):
        self.name.grid(column=0, row=row, sticky='nw')
        self.description.grid(column=1, row=row, sticky='new')
        self.button.grid(column=2, row=row, sticky='new')

    def remove(self):
        self.name.grid_forget()
        self.description.grid_forget()
        self.button.grid_forget()

    def destroy(self):
        self.name.destroy()
        self.description.destroy()
        self.button.destroy()


class MainWindow(ttk.Frame, object):
    def __init__(self, **kwargs):
        self.data = DataTracker(
            reset=self.reset,
            skill_load=self.add_skills,
            stunt_load=self.add_stunts,
        )
        self.filename = None
        self.root = Tkinter.Tk()
        self.root.title("Character Manager")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.mainloop = self.root.mainloop

        ttk.Frame.__init__(self, master=self.root, **kwargs)
        self.grid(column=0, row=0, sticky=Tkinter.NSEW)
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self['padding'] = 5
        self._skills = []
        self._stunts = []
        self.make_menu()

        # status bar
        self._totals = {}
        self._total = Tkinter.IntVar(value=0)
        self.status_frame = ttk.Frame()
        self.status_frame.grid(column=0, row=999, sticky='sew')
        self.status_frame.columnconfigure(2, weight=1)
        self.total_label = ttk.Label(self.status_frame, text="Total:")
        self.total_label.grid(column=0, row=0, sticky='e')
        self.total_display = ttk.Label(
            self.status_frame,
            textvariable=self._total,
        )
        self.total_display.grid(column=1, row=0, sticky='w')
        ttk.Sizegrip(self.status_frame).grid(column=4, row=0, sticky='se')

        # Top left frame
        self.aspect_frame = ttk.LabelFrame(self, text="Concept and Aspects")
        self.aspect_frame.grid(column=0, row=0, columnspan=2, sticky='NEWS')
        self.aspect_frame.columnconfigure(0, weight=0)
        self.aspect_frame.columnconfigure(1, weight=1)
        row = self.make_charname(parent=self.aspect_frame, row=0)
        row = self.make_concept(parent=self.aspect_frame, row=row)
        row = self.make_aspects(parent=self.aspect_frame, row=row)

        # Top right frame
        self.ability_frame = ttk.LabelFrame(self, text="Level and Abilities")
        self.ability_frame.grid(column=0, row=1, sticky=Tkinter.NSEW)
        self.ability_frame.columnconfigure(0, weight=0)
        self.ability_frame.columnconfigure(1, weight=1)
        row = self.make_level(parent=self.ability_frame, row=0)
        row = self.make_abilities(parent=self.ability_frame, row=row)

        # middle frame
        self.skill_frame = ttk.LabelFrame(self, text="Skills")
        self.skill_frame.grid(
            column=1, row=1, sticky=Tkinter.NSEW,
        )
        self.skill_frame.columnconfigure(1, weight=1)
        self.make_skill_adder(self.skill_frame)

        # bottom frame
        self.stunt_frame = ttk.LabelFrame(self, text="Powers/Stunts")
        self.stunt_frame.grid(
            column=0, row=2, columnspan=2, sticky=Tkinter.NSEW,
        )
        self.stunt_frame.columnconfigure(1, weight=1)
        self.make_stunt_adder(self.stunt_frame)

    def _total_register(self, name, valobj):
        self._totals[name] = valobj
        valobj.trace('w', self._total_collect)
        self._total_collect()

    def _total_unregister(self, name):
        if name in self._totals:
            del self._totals[name]
        self._total_collect()

    def _total_collect(self, *args):
        total = sum(int(x.get()) for x in self._totals.values())
        self._total.set(total)

    def reset(self):
        for stunt in self._stunts:
            stunt._del()
        for skill in self._skills:
            skill._del()
        self._skills = []
        self._stunts = []
        self.data.reset()
        self.filename = None

    def add_stunts(self, iterable):
        for name, description in iterable:
            self._add_stunt(name, description)

    def add_stunt(self):
        name = self._st_name.get()
        description = self._st_des.get('1.0', 'end')
        self._add_stunt(name, description)
        self._st_name.set('')
        self._st_des.delete('1.0', 'end')

    def _add_stunt(self, name, description):
        if not name and not description:
            return
        name = name.replace('|', ' ').replace(':', ' ')
        newstunt = Stunt(self, name, description)
        self._clear_stunts()
        self._stunts.append(newstunt)
        self._render_stunts()

    def remove_stunt(self, stunt):
        if stunt in self._stunts:
            self._clear_stunts()
            self._stunts.remove(stunt)
            self._render_stunts()

    def _clear_stunts(self):
        for stunt in self._stunts:
            stunt.remove()

    def _render_stunts(self):
        for row, stunt in enumerate(
            sorted(self._stunts, key=lambda x: x.name),
            start=1,
        ):
            stunt.insert(row)

    def make_stunt_adder(self, parent=None, row=999):
        parent = self if parent is None else parent
        self._st_name = stuntname = Tkinter.StringVar()
        stuntname_field = ttk.Entry(parent, textvariable=stuntname)
        stuntname_field.grid(column=0, row=row, sticky='new')
        stuntname_label = ttk.Label(parent, text='Stunt Name')
        stuntname_label.grid(column=0, row=0, sticky=Tkinter.EW)
        self._st_des = stuntdes_field = Tkinter.Text(parent, height=2)
        stuntdes_field.config(wrap='word')
        stuntdes_field.grid(column=1, row=row, sticky=Tkinter.EW)
        stuntlev_label = ttk.Label(parent, text="Skill Description")
        stuntlev_label.grid(column=1, row=0, sticky='news')
        add_button = ttk.Button(parent, text='Add', command=self.add_stunt)
        add_button.grid(column=2, row=row, sticky='new')

    def add_skills(self, iterable):
        for ability, name, level in iterable:
            self._add_skill(ability, name, level)

    def add_skill(self):
        ability = self._as_ability.get()
        name = self._as_name.get()
        level = int(self._as_level.get())
        self._add_skill(ability, name, level)
        self._as_ability.set('')
        self._as_name.set('')
        self._as_level.set(0)

    def _add_skill(self, ability, name, level):
        if not name and not ability:
            return
        name = name.replace('|', ' ').replace(':', ' ')
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

    def make_skill_adder(self, parent=None, row=999):
        parent = self if parent is None else parent
        self._as_ability = ability = Tkinter.StringVar()
        ability_select = ttk.Combobox(
            parent, textvariable=ability, state='readonly',
        )
        ability_select['values'] = ['Body', 'Reflexes', 'Wits', 'Persona']
        ability_select.grid(column=0, row=row, sticky=Tkinter.E)
        ability_label = ttk.Label(parent, text="Root Ability")
        ability_label.grid(column=0, row=0, sticky=Tkinter.EW)
        self._as_name = skillname = Tkinter.StringVar()
        skillname_field = ttk.Entry(parent, textvariable=skillname)
        skillname_field.grid(column=1, row=row, sticky=Tkinter.EW)
        skillname_label = ttk.Label(parent, text='Skill Name')
        skillname_label.grid(column=1, row=0, sticky=Tkinter.EW)
        self._as_level = skilllev = Tkinter.IntVar(value=0)
        skilllev_field = Tkinter.Spinbox(
            parent, from_=0, to=10, increment=1, textvariable=skilllev,
            width=4, state='readonly',
        )
        skilllev_field.grid(column=2, row=row, sticky=Tkinter.EW)
        skilllev_label = ttk.Label(parent, text="Skill Level")
        skilllev_label.grid(column=2, row=0, sticky=Tkinter.EW)
        add_button = ttk.Button(parent, text='Add', command=self.add_skill)
        add_button.grid(column=3, row=row)

    def make_charname(self, parent=None, row=0):
        parent = self if parent is None else parent
        self.name_label = ttk.Label(parent, text="Character Name:")
        self.name_label.grid(column=0, row=row, sticky=Tkinter.E)
        self.name = Tkinter.StringVar()
        self.data.register('name', self.name)
        self.name_field = ttk.Entry(parent, textvariable=self.name)
        self.name_field.grid(column=1, row=row, sticky=Tkinter.EW)
        return row+1

    def make_concept(self, parent=None, row=0):
        parent = self if parent is None else parent
        self.concept_label = ttk.Label(parent, text="High Concept:")
        self.concept_label.grid(column=0, row=row, sticky=Tkinter.E)
        self.concept = Tkinter.StringVar()
        self.data.register('concept', self.concept)
        self.concept_field = ttk.Entry(parent, textvariable=self.concept)
        self.concept_field.grid(column=1, row=row, sticky=Tkinter.EW)
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
            label.grid(column=0, row=row, sticky=Tkinter.E)
            value = Tkinter.StringVar()
            field = ttk.Entry(parent, textvariable=value)
            field.grid(column=1, row=row, sticky=Tkinter.EW)
            self.data.register(a_value, value)
            setattr(self, a_label, label)
            setattr(self, a_field, field)
            setattr(self, a_value, value)
        return row+1

    def make_level(self, parent=None, row=0):
        parent = self if parent is None else parent
        self.level_label = ttk.Label(parent, text="Level:")
        self.level_label.grid(column=0, row=row, sticky=Tkinter.E)
        self.level = Tkinter.IntVar(value=1)
        self.level_field = Tkinter.Spinbox(
            parent, from_=1, to=20, increment=1, textvariable=self.level,
            width=4, state='readonly',
        )
        self.level_field.grid(column=1, row=row, sticky=Tkinter.EW)
        row += 1
        self.armor_label = ttk.Label(parent, text="Armor:")
        self.armor_label.grid(column=0, row=row, sticky=Tkinter.E)
        self.armor = Tkinter.IntVar(value=0)
        self.armor_field = Tkinter.Spinbox(
            parent, from_=0, to=3, increment=1, textvariable=self.armor,
            width=4, state='readonly',
        )
        self.armor_field.grid(column=1, row=row, sticky=Tkinter.EW)
        row += 1
        self.edge_label = ttk.Label(parent, text="Edge:")
        self.edge_label.grid(column=0, row=row, sticky=Tkinter.E)
        self.edge = self.level
        self.edge_field = ttk.Label(parent, textvariable=self.edge)
        self.edge_field.grid(column=1, row=row, sticky=Tkinter.W)
        row += 1
        self.stamina_label = ttk.Label(parent, text="Stamina:")
        self.stamina_label.grid(column=0, row=row, sticky=Tkinter.E)
        self.stamina = Tkinter.IntVar(value=20)
        self.stamina_field = ttk.Label(parent, textvariable=self.stamina)
        self.stamina_field.grid(column=1, row=row, sticky=Tkinter.W)
        self.data.register('level', self.level)
        self.data.register('armor', self.armor)

        def level_trace(*args):
            if self.level.get():
                self.stamina.set(self.level.get() * 20)

        self.level.trace('w', level_trace)
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
            label.grid(column=0, row=row, sticky=Tkinter.E)
            value = Tkinter.IntVar(value=0)
            field = Tkinter.Spinbox(
                parent, from_=0, to=5, increment=1, textvariable=value,
                width=4, state='readonly',
            )
            field.grid(column=1, row=row, sticky=Tkinter.EW)
            self.data.register(a_value, value)
            self._total_register(a_value, value)
            setattr(self, a_label, label)
            setattr(self, a_field, field)
            setattr(self, a_value, value)
        return row+1

    def make_menu(self):
        self.root.option_add('*tearOff', Tkinter.FALSE)
        self.menu = Tkinter.Menu(self.root)
        self.root['menu'] = self.menu
        self.menu_file = Tkinter.Menu(self.menu)
        self.menu.add_cascade(menu=self.menu_file, label='File')
        self.menu_file.add_command(label='New', command=self.new)
        self.menu_file.add_command(label='Open...', command=self.open)
        self.menu_file.add_command(label='Save', command=self.save)
        self.menu_file.add_command(label='Save As...', command=self.saveas)
        self.menu_file.add_separator()
        self.menu_file.add_command(label='Export...', command=self.export)
        self.menu_file.add_separator()
        self.menu_file.add_command(label='Exit', command=lambda *p: None)

    def new(self):
        title = 'Save?'
        msg = 'Would you like to save your work before creating a new file?'
        answer = tkMessageBox.askyesnocancel(title=title, message=msg)
        if answer is None:
            return
        elif answer is True:
            self.save()
        self.reset()

    def open(self, skip_save=False):
        if not skip_save:
            title = 'Save?'
            msg = 'Would you like to save your work before opening a file?'
            answer = tkMessageBox.askyesnocancel(title=title, message=msg)
            if answer is None:
                return
            elif answer is True:
                self.save()
        filename = tkFileDialog.askopenfilename(
            parent=self,
        )
        if filename == '':
            return
        with open(filename) as f:
            data = yaml.load(f)
        self.data.load(data)
        self.filename = filename

    def save(self):
        if not self.filename:
            return self.saveas()
        else:
            return self.saveas(self.filename)

    def saveas(self, filename=None):
        if not filename:
            self.filename = filename = tkFileDialog.asksaveasfilename(
                defaultextension='.yaml',
                parent=self,
            )
        if filename == '':
            return
        data = dict(self.data.collect())
        serial = yaml.dump(data, default_flow_style=False)
        with open(filename, 'w') as f:
            f.write(serial)
        return True

    def export(self):
        formatter = Formatter()
        filename = tkFileDialog.asksaveasfilename(
            defaultextension='.txt',
            parent=self,
        )
        data = self.data.to_template()
        sheet = formatter.format(TEMPLATE, **data)
        with open(filename, 'w') as f:
            f.write(sheet.strip() + '\n')


def main(argv):
    root = MainWindow()
    root.mainloop()

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
