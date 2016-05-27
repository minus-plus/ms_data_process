import os
import path

from Tkinter import *
import tkFileDialog
import json

import msdata


fields_kinetics = ['compound 1', 'compound 2', 'ploarizability', 'dipole moment', 'constant', 'kcoll', 'peaks']
fields_reaction = ['compound 1', 'compound 2', 'ploarizability', 'dipole moment', 'constant', 'kcoll', 'peaks']

def get_entries(entries):
    params = {}
    for entry in entries:
        params[entry[0]] = entry[1].get()
    return params
def get_entries_form(entries_tuple):
    global params_dict_str
    params_dict = {}
    entries_k = entries_tuple[0]
    entries_r = entries_tuple[1]
    params_dict['kenetics'] = get_entries(entries_k)
    params_dict['reaction'] = get_entries(entries_r)
    #print json.dumps(params_dict)
    with open('params.json', 'w') as outfile:
        json.dump(params_dict, outfile)
    outfile.close()
    return params_dict
        
def make_form(root, fields, params_saved=None):
    entries = []
    for field in fields:
        row = Frame(root)
        lab = Label(row, width=15, text=field, anchor='w')
        ent = Entry(row)
        row.pack(side='top', fill='x', padx=5, pady=5)
        lab.pack(side='left')
        ent.pack(side='right', expand='yes', fill='x')
        ent.insert(0, params_saved[field])
        entries.append((field, ent))
    return entries
    
def input_params(frame=None):
    if not frame:
        frame = Tk()
    file = open('params.json')
    params_saved = json.load(file)
    file.close()
       
    global params_dict_str
    params_dict_str = StringVar()
    params_dict_str.set('')
    label_k = Label(frame, text='Kinetics Parameters:', font='Times 12 bold')
    label_r = Label(frame, text='Reaction Parameters:', font='Times 12 bold')
    label_k.grid(row=0, column=0, sticky='w', padx=5, pady=5)
    label_r.grid(row=0, column=1, sticky='w', padx=5, pady=5)
    form_k = Frame(frame)
    form_r = Frame(frame)
    form_k.grid(row=1, column=0, sticky='w', padx=5, pady=5)
    form_r.grid(row=1, column=1, sticky='e', padx=5, pady=5)
    ents_k = make_form(form_k, fields_kinetics, params_saved['kenetics'])
    ents_r = make_form(form_r, fields_reaction, params_saved['reaction'])
    #root.bind('<Return>', (lambda event, e=ents: get_entries(e)))
    form_save = Frame(frame)
    form_save.grid(row=2, column=0, columnspan=2, sticky='w', padx=5, pady=5)
    b1 = Button(frame, text='Save',
          command=(lambda e1=ents_k, e2 = ents_r:  get_entries_form((e1, e2))))
    b1.grid(row=2, column=0, ipadx=5, padx=5, pady=5)
    b2 = Button(frame, text='Quit', command=frame.destroy)
    b2.grid(row=2, column=1, ipadx=5, padx=5, pady=5)

def read_path(path):
    root = Tk()
    root.withdraw()
    # show an "Open" dialog box and return the path to the selected file
    dir_opt = {'parent':root, 'initialdir':os.getcwd(), 'title':'Select the folder'}
    dirname = tkFileDialog.askdirectory(**dir_opt)
    path.set(dirname)
    root.destroy()
    

def main_ui():
    root = Tk()
    root.geometry('400x300+30+30')
    #path_frame.grid(row=2, sticky='w', padx=10, pady=5)
    label_path = Label(root, text='Folder :') 
    label_path.grid(row=0, sticky='e', padx=5, pady=5)
    var_path = StringVar(root, value=os.getcwd())
    ent_path = Entry(root, textvariable=var_path)
    ent_path.config(width=30)
    ent_path.grid(row=0, column=1, sticky='w', padx=5, pady=5)
    select_path = Button(root, text='Edit..', command=(lambda path=var_path: read_path(path)))
    select_path.grid(row=0, column=2, sticky='e', padx=5, pady=5)
    print '=================='
    #param_frame = Frame(root)
    #input_params(param_frame)

    
    
    
if __name__ == '__main__':

    input_params()
    mainloop()

    print 'end of executation...'
    