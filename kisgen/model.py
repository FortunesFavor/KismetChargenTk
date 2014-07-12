import collections

import yaml


DEFAULT = None

info_keys = collections.OrderedDict((
    ('Name', 'name'),
    ('Concept', 'concept'),
    ('Description', 'description'),
    ('Ambition Aspect', 'ambition_aspect'),
    ('Background Aspect', 'background_aspect'),
    ('Conviction Aspect', 'conviction_aspect'),
    ('Disadvantage Aspect', 'disadvantage_aspect'),
    ('Exceptional Skill Aspect', 'exceptional_skill_aspect'),
    ('Foe Aspect', 'foe_aspect'),
    ('Gear Aspect', 'gear_aspect'),
    ('Help Aspect', 'help_aspect'),
    ('Inferior Skill Aspect', 'inferior_skill_aspect'),
))

keys = collections.OrderedDict()
keys.update(info_keys)

_internal_keys = list(keys.values())


def _is_key(name):
    return name in _internal_keys


class Character(collections.MutableMapping):
    def __init__(self, data):
        self.data = {}
        self.data.update(data)
        self.changed = False
        self.filename = None

    @classmethod
    def loadfile(cls, filename):
        if filename != DEFAULT:
            with open(filename, 'r') as flo:
                inst = cls.load(flo)
                inst.filename = filename
                return inst
        else:
            return cls(dict.fromkeys(_internal_keys))

    def savefile(self, filename):
        with open(filename, 'w') as flo:
            self.save(flo)
            self.filename = filename

    @classmethod
    def load(cls, flo):
        data = yaml.load(flo.read())
        inst = cls(data)
        inst.changed = False
        return inst

    def save(self, flo):
        flo.write(yaml.dump(self.data))
        self.changed = False

    def __getitem__(self, name):
        if _is_key(name):
            return self.data[name]

    def __setitem__(self, name, value):
        if _is_key(name):
            self.changed = True
            self.data[name] = value

    def __delitem__(self, name):
        if _is_key(name):
            self.changed = True
            del self.data[name]

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        return iter(self.data)
