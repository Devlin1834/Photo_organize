# -*- coding: utf-8 -*-
"""
Created on Sun Feb  2 01:35:05 2020

@author: Devlin
"""

import os
import csv
import json
import random as rn
import tkinter as tk
from PIL import ImageTk, Image
from tkinter import messagebox
###############################################################################
# Ok, so it's not actually a Face-Finder. You do the face finding. 
# I made the mistake (had the generosity of spirit...) of telling the kids 
# I'd print pictures for them if they paid for it. But this meant looking
# through (at the time) 2000 pictures with 300 students and that wasn't gonna
# fly. So I wrote this to help me sort the pictures. It lets me group the 
# pictures by the people in them and then only view the pictures with certain
# subjects. So I can see only the 15 pictures with Angela in them instead of
# trying to pick them out of all 2000.
# It has the added benefit of telling me how many pics I have of each kid so I
# can make sure to get at least a few shots of everyone. Especially the ones 
# who like to look at themselves. 
#.............................................................................#
###############################################################################
## GLOBAL VARIABLE DEFINITION #################################################
## Replace data_dir with the directory of your class registries (stored as CSVs
## listing the names of all students). Replace the data list in names_populate
## with a list of the CSVs used to do this. names_populate will then create the
## necessary JSONs and populate them accordingly
## Replace photo_dir with the directory of the pics you want to attach faces to
data_dir = 'C:/Users/Devlin/Documents/CSV/project_facefinder'
photo_dir = 'C:/Users/Devlin/Pictures/Master Faves GH'

###############################################################################
## FUNTIONS ###################################################################
###############################################################################
def resizer(pic):
    '''These pics are big. I need them to fit on my screen. I decided that a
    height of 720 was the biggest I wanted so I rescale all the images to match
    that'''
    
    h, w = pic.size
    mod = 540 / w
    return [int(i * mod) for i in (h, w)]

###############################################################################
def names_populate():
    '''These CSVs were created for my gradebook, I removed the gender column
    and repurposed it for this'''
    
    data = ['1a', '1b', '2a', '2b', '3a', '3b', 'staff'] # List of CSV names
    base = '{}/{}.{}'.format(data_dir)
    for i in data:
        faces = {}
    
        file = open(base.format(i, 'csv'))
        lol = list(csv.reader(file))
        flat = [n for l in lol for n in l]
        for n in flat:
            faces[n.lower()] = []
    
        file.close()
        
        with open(base.format('names', 'json'), 'w') as file_obj:
            json.dump(faces, file_obj)
    
    ## Create the other JSONs if they don't exist
    if not os.path.exists(base.format('checked', 'json')):
        with open(base.format('checked', 'json'), 'w') as file_obj:
            json.dump([], file_obj)
        
    if not os.path.exists(base.format('receipt', 'json')):
        with open(base.format('receipt', 'json'), 'w') as file_obj:
            json.dump({}, file_obj)
 
###############################################################################           
###############################################################################
class PhotoFrame():
    '''The base class for the slideshow windows. Contains the relevant file
    paths and the img_display function'''
    def __init__(self):
        self.base_photos = os.listdir(photo_dir)
        
        self.checked_path = '{}/checked.json'.format(data_dir)
        self.name_path = '{}/names.json'.format(data_dir)
        self.receipt_path = '{}/receipt.json'.format(data_dir)
        
        self.viewing = ''
        
    ###########################################################################
    def img_display(self):
        '''loads and resizes the image, creates the canvas and populates it'''
        
        im = Image.open('{}/{}'.format(photo_dir, self.viewing))               # Imported from PIL
        height, width = resizer(im)
        im = im.resize((height, width), Image.ANTIALIAS)
        photo = ImageTk.PhotoImage(im)                                         # Imported from PIL 
        self.photo = photo
        self.cv = tk.Canvas(self.master)
        self.cv.pack(side = tk.TOP, fill = tk.BOTH, expand = True)
        self.cv.create_image(10, 10, image = self.photo, anchor = 'nw')
        self.master.geometry('{}x{}'.format(height + 50, width + 50))
            
###############################################################################
###############################################################################
class Home(tk.Tk):
    '''The home page. Lets you pick one student to view or open the adding 
    window to add faces to new pictures'''
    def __init__(self):
        super().__init__()
        self.frame = tk.Frame(self.master)
        self.title('Face Finder')
        self.ttl = tk.Label(self.frame, 
                            text = "Face Finder",
                            font = ("Times", 30))
        
        self.name_ent = tk.Entry(self.frame, width = 25)
        
        self.look_btn = tk.Button(self.frame, 
                                  text = "Look at a Person",
                                  command = self.open_selector,
                                  font = ("Times", 12))
        
        self.add_btn = tk.Button(self.frame, 
                                 text = "Find new Faces", 
                                 command = self.open_finder,
                                 font = ("Times", 12))
        
        self.ttl.pack()
        self.name_ent.pack(side = tk.TOP, padx  = 10, pady = 5)
        self.look_btn.pack(side = tk.LEFT, padx = 10, pady = 10)
        self.add_btn.pack(side = tk.RIGHT, padx = 10, pady = 10)
        self.frame.pack()
        
    ###########################################################################
    def open_finder(self):
        '''Opens the Finder window'''
        
        self.session = tk.Toplevel(self.master)
        Finder(self.session)
        
    ###########################################################################
    def open_selector(self):
        '''Opens the Selector Window. Throws error messages if a student either
        doesn't exist in the JSON or has no pictures listed in the JSON'''
        
        with open('{}/names.json'.format(data_dir)) as file_obj:
            self.faces = json.load(file_obj)
            
        name = self.name_ent.get()
        if name.lower() not in self.faces.keys():
            messagebox.showinfo('Not Found', 'We couldn\'t find this student')
        elif len(self.faces.get(name.lower())) == 0:
            messagebox.showinfo('No Pictures Yet', 'You need to take some pics of {} ASAP'.format(name))
        else:
            self.session = tk.Toplevel(self.master)
            Selector(self.session, name.lower())
        
###############################################################################
###############################################################################
class Selector(PhotoFrame):
    '''The selector lets you view all the pictures for any one student. It lets
    you pick which pictures they want and appends it to a new json and then
    displays the total cost of their selections'''
    
    def __init__(self, master, name):
        super().__init__()
        self.master = master
        self.subject = name
        
        with open(self.receipt_path) as file_obj:
            self.sales = json.load(file_obj)
        
        ## SUBJECT CREATION ###################################################
        with open(self.name_path) as file_obj:
            self.faces = json.load(file_obj)
        
        self.pics = [i for i in self.faces.get(self.subject) if i in self.base_photos]
        self.index = 0
        self.viewing = self.pics[self.index]
        
        ## GUI CREATION #######################################################
        self.img_display()
        
        self.data_frame = tk.Frame(self.master)
        
        self.prv_btn = tk.Button(self.data_frame, 
                                 text = 'Prev. Picture',
                                 command = lambda x = -1: self.move(x))
        
        self.bought = tk.BooleanVar()
        self.boolset()
        self.takeit = tk.Checkbutton(self.data_frame, 
                                     variable = self.bought,
                                     text = "I'll Take It!")
        
        self.cost = tk.Label(self.data_frame,
                             text = '{} Ghana Cedi'.format(self.costset()))
        
        self.nxt_button = tk.Button(self.data_frame, 
                                    text = 'Next Picture', 
                                    command = lambda x = 1: self.move(x))

        self.prv_btn.pack(side = tk.LEFT)
        self.nxt_button.pack(side = tk.RIGHT)    
        self.takeit.pack()
        self.cost.pack()
        self.data_frame.pack(side = tk.BOTTOM, fill = tk.BOTH)
    
    ###########################################################################
    def costset(self):
        '''Returns the properly formatted price of the pictures'''
        l = self.sales.get(self.subject)
        if l is not None:
            c = str(len(l) * 3.5)
        else:
            c = "0.00"
            
        dot = c.find('.')
        while len(c[dot:]) < 3:
            c += '0'
            
        return c
    
    ###########################################################################
    def boolset(self):
        '''helps to set the BooleanVar to the correct state'''
        l = self.sales.get(self.subject)
        if l is not None and self.viewing in l:
            self.bought.set(True)
        else:
            self.bought.set(False)
    
    ###########################################################################
    def move(self, d):
        '''Progresses to the next picture. Allows for directional movement
        through the __d__ parameter. Modifies the Receipt JSON to allow for a 
        selected or deselected picture'''
      
        if self.bought.get():
            if self.subject not in self.sales:
                self.sales[self.subject] = [self.viewing]
                self.cost.configure(text = '{} Ghana Cedi'.format(self.costset()))
            else:
                receipt = self.sales.get(self.subject)
                if self.viewing not in receipt:
                    receipt.append(self.viewing)
                    
                    self.cost.configure(text = '{} Ghana Cedi'.format(self.costset()))
                    
                    with open(self.receipt_path, 'w') as file_obj:
                        json.dump(self.sales, file_obj)
                    
        else:
            if self.subject in self.sales:
                l = self.sales.get(self.subject)
                if self.viewing in l:
                    l.remove(self.viewing)
                    
                    self.cost.configure(text = '{} Ghana Cedi'.format(self.costset()))
                    
                    with open(self.receipt_path, 'w') as file_obj:
                        json.dump(self.sales, file_obj)
                        
        self.cv.destroy()
        self.index += d
        
        try:
            self.viewing = self.pics[self.index]
        except IndexError:
            print('Finished! {} has seen every picture!'.format(self.subject))
            self.index = 0
            self.viewing = self.pics[0]
        
        self.master.title(self.viewing)
        self.img_display()
        self.boolset()

###############################################################################
###############################################################################
class Finder(PhotoFrame):
    '''Its not pretty but it works. It displays a picture and lets you add
    names one at a time. The names are pre-entered into the json to help 
    prevent mispellings. It prints a short readout every time you add a name 
    to tell you how biased you are in choice of subjects. Best part is it uses
    a second json to save your place meansing you don't have to start over, 
    you can stop and take breaks and come back. or add new pictures and update
    the json whenever you feel like it.'''
    
    def __init__(self, master):
        super().__init__()
        self.master = master
        
        with open(self.checked_path) as file_obj:
            self.seen = json.load(file_obj)
        
        ## PICTURE SELECTION ##################################################
        self.checking = [p for p in self.base_photos if p not in self.seen]
        
        self.c = 0
        self.viewing = self.photo_select()
        self.master.title(self.viewing)
        self.photo = None
        
        ## GUI CREATION #######################################################
        self.img_display()
        
        self.data_frame = tk.Frame(self.master)
        self.name_ent = tk.Entry(self.data_frame, width = 35)
        self.add_btn = tk.Button(self.data_frame, 
                                 text = 'Add Face',
                                 command = self.add_name)
        self.nxt_button = tk.Button(self.data_frame, 
                                    text = 'Next Picture', 
                                    command = self.next_img)
        
        self.nxt_button.focus_force()

        self.name_ent.pack(side = tk.LEFT)
        self.add_btn.pack(side = tk.LEFT)
        self.nxt_button.pack(side = tk.RIGHT)        
        self.data_frame.pack(side = tk.BOTTOM, fill = tk.BOTH)
    
    ###########################################################################       
    def photo_select(self):
        '''used to prevent errors when I am up to date on faces'''
        
        if self.c < len(self.checking):
            p = self.checking[self.c]
        else:
            print('No unchecked Photos, randomly selecting one')
            p = rn.choice(self.base_photos)
            
        return p
    
    ###########################################################################
    def next_img(self):
        '''progresses to the next picture, saves viewing data'''
        
        self.seen.append(self.viewing)
        self.cv.destroy()
        self.c += 1
        self.viewing = self.photo_select()
        self.master.title(self.viewing)
        self.img_display()
        
        with open(self.checked_path, 'w') as file_obj:
            json.dump(self.seen, file_obj)
    
    ###########################################################################
    def add_name(self):
        '''appends a name to the name json file. contains all the if-catches
        in the event of special cases. prints data to the console'''
        
        name = self.name_ent.get()
        with open(self.name_path) as file_obj:
            faces = json.load(file_obj)
        
        face = name.lower()
        
        if face not in faces:
           messagebox.showinfo('Name Error', 
                               'Name not in JSON. add it or fix the spelling') 
        else:
            if self.viewing not in faces[face]:
                faces[face].append(self.viewing)
                self.name_ent.delete(0, tk.END)
                with open(self.name_path, 'w') as file_obj:
                    json.dump(faces, file_obj)
                
                ################################################################
                print('='*50)                                                  # The printout.
                print('{} has {} pictures now'.format(face, len(faces[face]))) # This is what tells
                print('-'*20)                                                  # me how I'm doing 
                x = [key for key in faces if len(faces[key]) > 0]              # as a fair and 
                print('{} people have pictures'.format(len(x)))                # unbiased dispensor
                print('{} people don\'t yet'.format(len(faces) - len(x)))      # or photo-love. 
                ################################################################
                
            else:
                self.name_ent.delete(0, tk.END)
                messagebox.showinfo('Done', 'Alrady logged this face')
                
############################################################################### 
###############################################################################
if __name__== '__main__':
    if not os.path.exists('{}/names.json'.format(data_dir)):
        names_populate()
    
    root = Home()   
    root.mainloop()   
