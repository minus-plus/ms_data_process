#!usr/bin/python
import os
from os.path import join
from Tkinter import *
import Tkinter as tk

root = Tk()
logo = PhotoImage(file=os.path.join(os.getcwd(), 'logo.gif'))
w1 = Label(root, image=logo).pack(side='right')
explanation = """At present, only GIF and PPM/PGM
formats are supported, but an interface 
exists to allow additional image file
formats to be added easily."""
l2 = Label(root, text=explanation)
l2.config(justify=LEFT, padx=20, fg='red', bg='blue', font='Arial 14 bold')
l2.pack(side='left')
           
def counter_label(label):
  def count():
    global counter
    counter += 1
    label.config(text=str(counter))
    label.after(1000, count)
  count()

root1 = Tk()
counter = 0
root1.title('counting times')
label = Label(root1, fg='black')
label.pack()
counter_label(label)
button = Button(root1, text='Stop', width=25, command=root1.destroy)
button.pack()
m = Tk()
whatever_you_do = "Whatever you do will be insignificant, but it is very important that you do it.\n(Mahatma Gandhi)"
msg = Message(m, text=whatever_you_do)
msg.config(bg='lightgreen', font='Times 24 italic') 
msg.pack()
 
mainloop()