import collections

import yaml


class KeyMap(collections.MutableMapping):
    def __init__(self, fields, iterable=None, **kwargs):
        self.fields = fields
        self.data = collections.OrderedDict.fromkeys(fields)
        if iterable is not None:
            self.update(iterable)
        self.update(kwargs)

    def __setitem__(self, name, value):
        self._validate(name)
        self.data[name] = value

    def __getitem__(self, name):
        self._validate(name)
        return self.data[name]

    def __delitem__(self, name):
        self._validate(name)
        del self.data[name]

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        return iter(self.data)

    def _validate(self, name):
        if name not in self.fields:
            raise KeyError('%s not in fields' % (name,))

    def __repr__(self):
        cn = self.__class__.__name__
        it = ', '.join("(%r, %r)" % i for i in self.data.items())
        return '%s(%r, [%s])' % (cn, self.fields, it)


class DefaultKeyMap(KeyMap):
    def __init__(self, factory, fields, iterable=None, **kwargs):
        super(DefaultKeyMap, self).__init__(fields, iterable, **kwargs)
        self.data.update({k: factory() for k in fields})


class Character(object):
    fields = {
        'info': ('Name', 'Age', 'Description', 'Notes', 'Concept'),
        'aspects': (
            'Ambition',
            'Background',
            'Conviction',
            'Disadvantage',
            'Exceptional Skill',
            'Foe',
            'Gear',
            'Help',
            'Inferior Skill',
        ),
        'stats': ('Level', 'Armor'),
        'abilities': ('Body', 'Reflexes', 'Wits', 'Persona'),
    }

    def __init__(self):
        self.info = KeyMap(self.fields['info'])
        self.aspects = KeyMap(self.fields['aspects'])
        self.stats = KeyMap(self.fields['stats'])
        self.abilities = KeyMap(self.fields['abilities'])
        self.skills = DefaultKeyMap(dict, self.fields['abilities'])
        self.stunts = collections.OrderedDict()

    def asdict(self):
        data = dict()
        data['info'] = dict(self.info.items())
        data['aspects'] = dict(self.aspects.items())
        data['stats'] = dict(self.stats.items())
        data['abilities'] = dict(self.abilities.items())
        data['skills'] = dict(self.skills.items())
        data['stunts'] = dict(self.stunts.items())
        return data

    @classmethod
    def fromdict(cls, data):
        self = cls()
        self.info.update(data['info'])
        self.aspects.update(data['aspects'])
        self.stats.update(data['stats'])
        self.abilities.update(data['abilities'])
        self.skills.update(data['skills'])
        self.stunts.update(data['stunts'])
        return self

    def dump(self):
        return yaml.dump(self.asdict(), default_flow_style=False)

    @classmethod
    def load(cls, stream):
        return cls.fromdict(yaml.load(stream))
