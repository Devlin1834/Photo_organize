# -*- coding: utf-8 -*-
"""
Created on Thu Feb  6 02:38:34 2020

@author: Devlin
"""
import os
import csv
import json
import numpy as np
import matplotlib.pyplot as plt
import table_gen3 as tg
from collections import Counter

data_dir = 'C:/Users/Devlin/Documents/CSV/project_facefinder'
photo_raw_loc = '{}/names.json'.format(data_dir)
staff = 'staff.csv'

form_dir = 'C:/Users/Devlin/Documents/CSV/project_gradebook'
all_classes_raw = []
for i in os.listdir(form_dir):
    with open('{}/{}'.format(form_dir, i)) as file_obj:
        students = list(csv.reader(file_obj))
        
    all_classes_raw.append(students)
    
onea = {}
oneb = {}
twoa = {}
twob = {}
threea = {}
threeb = {}

registers = {'One A': onea, 
             'One B': oneb,
             'Two A': twoa, 
             'Two B': twob, 
             'Three A': threea, 
             'Three B': threeb}

for c in range(6):
    room = all_classes_raw[c]
    register = list(registers.values())[c]
    for s in room:
        register[s[0].lower()] = s[1]
        
###############################################################################
## Based on the below printed results, we add the names manually             ##
###############################################################################
'''none to add'''

###############################################################################
## Checking that we have all the students represented                        ##
###############################################################################  
staff_list = list(csv.reader(open('{}/{}'.format(data_dir, staff))))
staff_flat = [s.lower() for l in staff_list for s in l]
with open(photo_raw_loc) as file_obj:
    photo_data = json.load(file_obj)
    
all_students = [[key for key in i] for i in registers.values()]
stdnts_flat =[n for l in all_students for n in l]
for key in photo_data:
    if key not in stdnts_flat and key not in staff_flat:
        print("Did not find {}".format(key))
        
###############################################################################
## Printing the kids who have no pictures                                    ##
###############################################################################
nopics = [key for key in photo_data if len(photo_data.get(key)) == 0]
print(*nopics, sep = '\n')

print('-'*20)

npc = {k: [] for k in registers}
classes = []
gender = []
for name in nopics:
    for c in registers:
        room = registers[c]
        if name in room.keys():
            classes.append(c)
            gender.append(room[name].lower())
            npc[c].append(name)
            
class_sizes = [len(c) for c in registers.values()]
npc_len = [len(npc[k]) for k in npc]
capd_class_sizes = [class_sizes[i] - npc_len[i] for i in range(6)]
            
counted = Counter(classes)
for k in counted:
    print(k, counted[k])

print('-'*20)    
cgender = Counter(gender)
for k in cgender:
    print(k, cgender[k])
    
pcts = [list(counted.values())[i] / class_sizes[i] for i in range(6)]

plt.bar(counted.keys(), pcts)
plt.title('No Picture Percentage by Class')
plt.show()

print('-'*20)    

###############################################################################
##  Printing the counts for each class                                       ##
###############################################################################
class_pref = {c: 0 for c in registers}
for name in photo_data:
    for c in registers:
        room = registers[c]
        if name in room.keys():
            class_pref[c] += len(photo_data[name])
            
for k in class_pref:
    print(k, class_pref.get(k))

plt.bar(class_pref.keys(), class_pref.values())
plt.title('Pictures by Class')
plt.show()

mean_pics = [round(list(class_pref.values())[i] / capd_class_sizes[i], 2) for i in range(6)]   

###############################################################################
## Building tables                                                           ##
###############################################################################
np_data = list(npc.values())
detlen = max([len(l) for l in np_data])
for l in np_data:
    while len(l) < detlen:
        l.append('')
        
np_rnames = ['' for i in range(detlen)]
np_cnames = list(npc.keys())
np_table = tg.Table(np_rnames, np_cnames, np_data)
#print(np_table)  # Print only in terminal, not console

rnames = list(registers.keys())
cnames = ['No Pics', '# Pics', 'Mean Pics']
info = [list(counted.values()), list(class_pref.values()), mean_pics]

table = tg.Table(rnames, cnames, info)
print(table)

###############################################################################
## Checking Gender Split                                                     ##
###############################################################################
girls = []
boys = []
for r in registers.values():
    for key in r:
        if r[key].lower() == 'girl':
            girls.append(key.lower())
        elif r[key].lower() == 'boy':
            boys.append(key.lower())
        else:
            print('I don\'t know what to do about {}'.format(key))
            
girl_pics = [len(photo_data[n]) for n in photo_data if n in girls]
boys_pics = [len(photo_data[n]) for n in photo_data if n in boys]
girls_mean = round(np.mean(girl_pics), 2)
boys_mean = round(np.mean(boys_pics), 2)

###############################################################################
## Histogram Pic Count                                                       ##
###############################################################################
x = [len(i) for i in photo_data.values()]
plt.hist(x)
plt.title('Photo Subject Histogram')
plt.show()

plt.hist(girl_pics)
plt.title('Girls')
plt.show()

plt.hist(boys_pics)
plt.title('Boys')
plt.show()

###############################################################################
## Boy v Girl detail                                                         ##
###############################################################################
gsplit = {k: {} for k in registers}
for d in gsplit.values():
    a = {'boy': 0,
         'girl': 0}
    
    d.update(a)
    
for name in photo_data:
    for c in registers:
        room = registers[c]
        if name in room.keys():
            g = room[name].lower()
            gsplit[c][g] += len(photo_data[name])

gs = ['boy', 'girl']
gcounts = [[gsplit[k][g] for k in gsplit] for g in gs]
gtable = tg.Table(list(gsplit.keys()), gs, gcounts, [boys_mean, girls_mean])
print(gtable)
