import Tkinter

from kisgen.model import Character


class Binder(object):
    # proxy a character, returning a *Var
    def __init__(self, character=None):
        self.character = character if character is not None else Character()
