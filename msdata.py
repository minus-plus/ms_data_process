
# coding: utf-8

import os
import sys
from os import listdir
from os.path import isfile, join

import operator
import math
import numpy as np
from scipy import stats
class Data(dict):
    def __getitem__(self, index):
        self.setdefault(index, 0.0)
        return dict.__getitem__(self,index)
def set_peaks():
    print 'input two peaks: '
    print 'example: 322 153'
    peaks = raw_input('two peaks: ')
    peaks = '322 153'
    return peaks.split(' ')
def normalize(data):
    max_key = max(data.iteritems(), key=operator.itemgetter(1))[0]
    max_value = data[max_key]
    for key in data:
        val = data[key]
        data[key] = round(val / max_value * 100, 2)

filename = r'C:\Users\Yun Wang\Desktop\data_txt\ms.txt'
def get_data_per_file(filename):
    data = Data()
    if os.path.exists(filename):
        lines = open(filename).readlines()
        for l in lines:
            l = l.split('\n')[0]
            if l[0].isdigit():
                l = l.split(' ')
                peak, value = str(int(round(float(l[0]),0))), float(l[1])
                data[peak] = max(value, data[peak])
    normalize(data)
    return data 

# working on read file from folder
mypath = r'E:\lcqdata\data_2\mgf'

files = [f for f in listdir(mypath) if isfile(join(mypath, f))]

def get_data_from_folder(path):
    data_folder=Data()
    files = [f for f in listdir(mypath) if isfile(join(mypath, f))]
    for f in files:
        data = get_data_per_file(join(path, f))
        data_folder[f.split('_')[-2].split('ms')[0]] = data
    return data_folder

def filt(data, peaks):
    new_data = dict()
    for key in data:
        d = {}
        val = data[key][peaks[0]] + data[key][peaks[1]]
        print val
        d[peaks[0]] = math.log(data[key][peaks[0]] / val )
        d[peaks[1]] = math.log(data[key][peaks[1]] / val)
        print key, data[key][peaks[0]], data[key][peaks[1]] 
        new_data[key] = d
    return new_data

# correlation
def regression_calc(data, peaks):
    keys = sorted(data.keys()) 
    print keys
    x = []
    y = []
    for k in keys :
        x.append(float(k))
        y.append(data[k][peaks[0]])
    print x
    print y
    return stats.linregress(x, y)
def run():
    folder_path = None
    folder_path = str(raw_input('input the path of folder: '))
    folder_path = r'E:\lcqdata\data_2\mgf'
    print folder_path
    if not os.path.exists(folder_path):
        print 'wrong path, run again'
        sys.exit(0)
    peaks = set_peaks()
    data_folder = get_data_from_folder(folder_path)
    data = filt(data_folder, peaks)
    print data

    # print regression_calc(data, peaks)
    k, b, r, p, std= regression_calc(data, peaks)
    print k * 1000 , r, b


# In[48]:

run()




