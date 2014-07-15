import Tkinter
import Tix

root = Tix.Tk()
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
hl = Tix.HList(root, columns=2, separator="/")
bodyvar = Tkinter.IntVar(hl, value=2)
body = Tix.Control(hl, variable=bodyvar)
hl.add('body', text='Body')
hl.item_create('body', col=1, itemtype='window', window=body)
bskill1var = Tkinter.IntVar(hl, value=2)
bskill1 = Tix.Control(hl, variable=bskill1var)
hl.add('body/bskill1', text='Lift/Carry/Haul')
hl.item_create('body/bskill1', col=1, itemtype='window', window=bskill1)
hl.grid(sticky='NEWS')
root.mainloop()
