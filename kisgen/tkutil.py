"""
kisgen.tkutil.tkmenu
A builder for tkinter menus.

>>> import Tkinter as tkinter
>>> def test(arg):
...    def inner():
...        print('{0} has fired'.format(arg))
...    return inner
...
>>> root = tkinter.Tk()
>>> menu_def = Menu(
...     None,
...     Menu(
...         'File',
...         Item('New', test('New')),
...         Menu(
...             'Export',
...             Item('Ascii', test('Export Ascii')),
...             Item('PDF', test('Export PDF')),
...         ),
...         Item('Exit', test('Exit')),
...     ),
...     Menu(
...         'Edit',
...         Item('Undo', test('Undo')),
...         Item('Redo', test('Redo')),
...     )
... )
>>> menu = menu_def.build(root)
>>> root.mainloop()
"""
try:
    import Tkinter as tkinter
except ImportError:
    import tkinter


class Menu(object):
    """
    This builder represents cascading menus.
    """
    def __init__(self, name=None, *children):
        """
        :param name: The label for the menu (None for the root menu)
        :param *children: Other Menu or Item instances (or anything with a
                          build method.)
        """
        self.name = name
        self.children = children

    def build(self, master):
        """
        :param master: The tkinter.Tk, tkinter.TopLevel, or tkinter.Menu
                       instance to bind to.
        :returns: The menu object.
        """
        menu = tkinter.Menu(master)
        if self.name is None:
            master.option_add('*tearOff', tkinter.FALSE)
            master['menu'] = menu
        else:
            master.add_cascade(menu=menu, label=self.name)
        for child in self.children:
            child.build(menu)
        return menu


class Item(object):
    """
    Represents a clickable menu item.
    """
    def __init__(self, name, command=None):
        """
        :param name: The label for the menu item
        :param command: the function to call when the menu item is clicked.
        """
        self.name = name
        self.command = command

    def build(self, master):
        """
        :param master: The tkinter.Menu instance to bind to.
        """
        args = {
            'label': self.name,
        }
        if self.command is not None:
            args['command'] = self.command
        master.add_command(**args)


if __name__ == '__main__':
    def test(arg):
        def inner():
            print('{0} has fired'.format(arg))
        return inner

    root = tkinter.Tk()
    menu_def = Menu(
        None,
        Menu(
            'File',
            Item('New', test('New')),
            Menu(
                'Export',
                Item('Ascii', test('Export Ascii')),
                Item('PDF', test('Export PDF')),
            ),
            Item('Exit', test('Exit')),
        ),
        Menu(
            'Edit',
            Item('Undo', test('Undo')),
            Item('Redo', test('Redo')),
        )
    )
    menu = menu_def.build(root)
    root.mainloop()
