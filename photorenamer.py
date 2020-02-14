# -*- coding: utf-8 -*-
"""
Created on Wed Jan 30 06:00:31 2019

@author: Devlin
"""

import os
from PIL import Image
from PIL.ExifTags import TAGS
import collections as c
import csv

def get_exif(pic):
    data = {}
    i = Image.open(pic)
    raw = i._getexif()
    for tag, value in raw.items():
        decoded = TAGS.get(tag, tag)
        data[decoded] = value
    return data

def renamer(directory, aspect = "DateTimeOriginal", img_type = ".jpg"):
    os.chdir(directory)
    n = aspect
    var = 0

    for i in os.listdir():
        if i[:4] == '_DSC': 
            pic = "{}/{}".format(directory, i)
            data = get_exif(pic)
            try:
                name = ((data[n]).replace(":", "")).replace(" ", "_")
                name += img_type
                os.rename(pic, name)
            except FileExistsError:
                name = ((data[n]).replace(":", "")).replace(" ", "_")
                name += '_{}{}'.format(var, img_type)
                os.rename(pic, name)
                var += 1

def data_collector(start_dir, save_dir, tag = ''):
    
    if tag == '':
        end = '.csv'
    else:
        end = '_' + str(tag) + '.csv'
    
    print('You can record data on any of these points')
    for key in get_exif(start_dir + "/" + os.listdir(start_dir)[0]):
        print(key)
    
    special = ['stop', 'default']
    choices = []
    while True:
        choice = input('Type a point, or stop to collect the data: ')
        if choice.lower() not in special:
            if choice not in get_exif(start_dir + "/" + os.listdir(start_dir)[0]).keys():
                print('Type it exactly as it appears above, or type stop to move on')
            else:
                choices.append(choice)
        elif choice.lower() == 'stop':
            break
        elif choice.lower() == 'default' and len(choices) == 0:
            choices.append('GHANA')
            print('default options are good')
            break
        else:
            pass
    
    if choices[0] != 'GHANA':
        data = [[] for point in choices]
    
        for point in choices:
            for pic in os.listdir(start_dir):
                data[choices.index(point)].append(get_exif(start_dir + "/" + pic)[point])

        os.chdir(save_dir)
        
        for point in choices:
            counted = sorted(list(c.Counter(data[choices.index(point)]).items()), key = lambda x: x[0])
            file = open(point + end, 'w', newline  = '')
            writer = csv.writer(file)
            for line in counted:
                writer.writerow(line)
            file.close()
     
    else:         
        data = {"FocalLength": [], #(x, 10) x/10
                "fNumber": [], #(x, 10) x/10
                "ExposureTime": [], #(x, y) x/y
                "ISOSpeedRatings": [],
                "LensModel": []
                }

        for i in os.listdir(start_dir):
            data["FocalLength"].append((get_exif(start_dir + "/" + i)['FocalLength'][0])/10)
            data["fNumber"].append((get_exif(start_dir + "/" + i)['FNumber'][0])/10)
            data["ExposureTime"].append((get_exif(start_dir + "/" + i)['ExposureTime'][1]))
            data["ISOSpeedRatings"].append((get_exif(start_dir + "/" + i)['ISOSpeedRatings']))
            data["LensModel"].append((get_exif(start_dir + "/" + i)['LensModel']))
        
        for i in data['fNumber']:
            if i < 1:
                data['fNumber'][data['fNumber'].index(i)] = i * 10
    
        counted_data = {'lens': sorted(list(c.Counter(data['LensModel']).items()), key = lambda x: x[0]),
                        'apperture': sorted(list(c.Counter(data['fNumber']).items()), key = lambda x: x[0]),
                        'shutter': sorted(list(c.Counter(data['ExposureTime']).items()), key = lambda x: x[0]),
                        'iso': sorted(list(c.Counter(data['ISOSpeedRatings']).items()), key = lambda x: x[0]),
                        'zoom': sorted(list(c.Counter(data['FocalLength']).items()), key = lambda x: x[0])
                        }
    
        os.chdir(save_dir)

        for key in counted_data:
            name = 'C:/Users/Devlin/Documents/CSV/project_camera/{}_data{}'.format(key, end)
            file = open(name, 'w', newline = '')
            writer = csv.writer(file)
            for line in counted_data[key]:
                writer.writerow(line)
            file.close()

if __name__ == "__main__": 
    directory = "C:/Users/Devlin/Pictures/Master Faves GH"
    renamer(directory)
    data_collector(directory, "C:/Users/Devlin/Documents")
 