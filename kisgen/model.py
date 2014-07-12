import collections


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
