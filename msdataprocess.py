#coding=utf-8 
import os
import path

from Tkinter import *
import tkFileDialog
import json

import msdataapp


fields_kinetics = ['compound 1', 'compound 2', 'ploarizability', 'dipole moment', 'constant', 'kcoll', 'peaks']
fields_reaction = ['compound 1', 'compound 2', 'ploarizability', 'dipole moment', 'constant', 'kcoll', 'peaks']

class MainPage():
    def __init__(self, master, info='Home'):
        self.master = master
        self.main_label = Label(self.master, text=info,  justify=CENTER, bg='white')
        self.main_label.grid(row=0, columnspan=5) 
        self.main_label.config(width=80)
        
        self.path_label = Label(self.master, text='Folder Path :', borderwidth=2, bg='white') 
        self.path_label.grid(row=1, sticky='e', padx=5, pady=5)
        
        self.path_var = StringVar(self.master, value=os.getcwd())
        self.path_entry = Entry(self.master, textvariable=self.path_var, bg='white')
        self.path_entry.grid(row=1, column=1, columnspan=3)
        self.path_entry.config(width=70)

        self.select_path_button = Button(self.master, text='Edit..', command=(lambda path=self.path_var: self.read_path(path)))
        self.select_path_button.grid(row=1, column=4, sticky='w')

        #reault path
        self.result_path_label = Label(self.master, text='Result Path :', borderwidth=2, bg='white') 
        self.result_path_label.grid(row=2, sticky='e', padx=5, pady=5)
        
        self.result_path_var = StringVar(self.master, value=os.getcwd())
        self.result_path_entry = Entry(self.master, textvariable=self.result_path_var, bg='white')
        self.result_path_entry.grid(row=2, column=1, columnspan=3)
        self.result_path_entry.config(width=70)
        self.result_path_entry.focus_set()

        self.select_result_path_button = Button(self.master, text='Edit..', command=(lambda path=self.result_path_var: self.read_path(path)))
        self.select_result_path_button.grid(row=2, column=4, sticky='w')
        
        # result name
        self.result_name_label = Label(self.master, text='Result name :', borderwidth=2, bg='white') 
        self.result_name_label.grid(row=3, sticky='e', padx=5, pady=5)
        
        self.result_name_var = StringVar(self.master)
        self.result_name_entry = Entry(self.master, textvariable=self.result_name_var, bg='white')
        self.result_name_entry.grid(row=3, column=1, columnspan=2)
        self.result_name_entry.config(width=70)
                
        # kinetics and reaction parameter frame
        self.params_frame = Frame(self.master)
        self.params_frame.grid(row=4, columnspan = 5)
        
        self.params_page = ParamsPage(self.params_frame, self.master)
        
        # run button
        self.run_button = Button(self.master, text='Run', justify='center', command=self.run)
        self.run_button.grid(row=5, columnspan=5, padx=5, pady=5, ipady=5)
        self.run_button.config(width=70, bg='sea green', font = 'Arial 10 bold')
        self.run_button.focus_set()
   
    def run(self):
        print self.path_entry.get()
        ms = msdataapp.MSDataApp(self.path_entry.get())
        self.results = ms.calculate()
        re_path = os.path.join(self.result_path_var.get(),self.result_name_var.get())
        print re_path
        re = open(re_path + '.txt', 'w')
        re.write(self.results)
        re.close()
        self.show_results()
        print self.results
        
    def read_path(self, path):
        dirpage = Toplevel(self.master)
        dirpage.withdraw()
        # show an "Open" dialog box and return the path to the selected file
        dir_opt = {'parent':dirpage, 'initialdir':os.getcwd(), 'title':'Select the folder', 'mustexist':True}
        dirname = tkFileDialog.askdirectory(**dir_opt)
        path.set(dirname)
        dirpage.destroy()
        
    def show_results(self):
        msg = Message(Tk(), text=self.results)
        msg.pack()


    
class ParamsPage():
    def __init__(self, master=None, root = None, info='Edit Parameters'):
        self.fields_kinetics = ['compound 1', 'compound 2', 'ploarizability', 'dipole moment', 'constant', 'kcoll', 'peaks']
        self.fields_reaction = ['compound 1', 'compound 2', 'ploarizability', 'dipole moment', 'constant', 'kcoll', 'peaks']
        self.entries = []
        self.root = root
        #print master
        if not master:
            self.new_page = True
            self.master = Tk()
        else:
            self.new_page = False
            self.master = master

        #self.master = Toplevel(master)
        self.params = self.load_params()
        self.label_k = Label(self.master, text='Kinetics Parameters')
        self.label_r = Label(self.master, text='Reaction Parameters')
        self.label_k.grid(row=0, column=0, sticky='w')
        self.label_k.config(width=40)
        self.label_r.grid(row=0, column=1, sticky='w')
        self.label_r.config(width=40)
        
        self.params_str = StringVar()
        self.form_k = Frame(self.master)
        self.form_r = Frame(self.master)
        self.form_k.grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.form_r.grid(row=1, column=1, sticky='e', padx=5, pady=5)

        self.entries_k = self.make_form(self.form_k, fields_kinetics, self.params['kinetics'])
        self.entries_r = self.make_form(self.form_r, fields_kinetics, self.params['reaction'])

        self.form_save = Frame(self.master)
        
        #save button
        self.form_save.grid(row=2, column=0, columnspan=2, sticky='w', padx=5, pady=5)
        self.save_button = Button(self.master, text='Save', command=self.save_form)
        self.save_button.grid(row=2, column=0, ipadx=5, padx=5, pady=5)
        
        # quit button
        self.quit_button = Button(self.master, text='Quit', command=self.root.destroy)
        self.quit_button.grid(row=2, column=1, ipadx=5, padx=5, pady=5)
        self.quit_button.config(bg='goldenrod')
        

        
    def load_params(self):
        file = open('params.json')
        params_saved = json.load(file)
        file.close()
        return params_saved
    
    def make_form(self, master, fields, params_saved):
        entries = []
        for field in fields:
            row = Frame(master)
            lab = Label(row, width=15, text=field, anchor='w')
            ent = Entry(row)
            row.pack(side='top', fill='x', padx=5, pady=5)
            lab.pack(side='left')
            ent.pack(side='right', expand='yes', fill='x')
            ent.insert(0, params_saved[field])
            entries.append((field, ent))
        return entries
        
    def get_entries(self, entries):
        params = {}
        for entry in entries:
            params[entry[0]] = entry[1].get()
        return params
        
    def save_form(self):
        params_dict = {}
        params_dict['kinetics'] = self.get_entries(self.entries_k)
        params_dict['reaction'] = self.get_entries(self.entries_r)
        #print params_dict
        #print json.dumps(params_dict)
        #print 'dumping jason'
        outfile = open('params.json', 'w')
        json.dump(params_dict, outfile)
        outfile.close()

        
if __name__ == '__main__':
    
    root = Tk()
    root.title('MS Data Processing Application ..')
    main_page = MainPage(root)
    #ms = msdataapp.MSDataApp()
    mainloop()