
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
    return peaks.split(' ')
def normalize(data):
    max_key = max(data.iteritems(), key=operator.itemgetter(1))[0]
    max_value = data[max_key]
    for key in data:
        val = data[key]
        data[key] = val / max_value * 100

def get_data_per_file(filename):
    #print 'reading file %s..' % filename
    data = Data()
    if os.path.exists(filename):
        lines = open(filename).readlines()
        for l in lines:
            l = l.split('\n')[0]
            if l[0].isdigit():
                l = l.split(' ')
                peak, value = str(int(round(float(l[0]),0))), float(l[1])
                data[peak] = max(value, data[peak])
    else:
        print '%s does not exist!' % filename
        sys.exit(0)
    normalize(data)
    return data 

# working on read file from folder


def get_data_from_folder(path):
    if os.path.exists(path):
        print 'loading folder %s..' % path
        data_folder=Data()
        files = [f for f in listdir(path) if isfile(join(path, f))]
        for f in files:
            data = get_data_per_file(join(path, f))
            t = float(f.split('_')[-2].split('ms')[0])
            data_folder[t] = data
        return data_folder
    else:
        print '%s does not exist!' % path

def filt(data, peaks):
    new_data = dict()
    keys = sorted(data.keys())
    for key in keys:
        d = {}
        val = data[key][peaks[0]] + data[key][peaks[1]]
        #print val
        d[peaks[0]] = math.log(data[key][peaks[0]] / val )
        d[peaks[1]] = math.log(data[key][peaks[1]] / val)
        f = '{0:6} {1:6} {2:6}'
        print f.format(key, round(data[key][peaks[0]], 2), round(data[key][peaks[1]], 2))
        new_data[key] = d
    return new_data

# correlation
def regression_calc(data, peaks):
    keys = sorted(data.keys()) 
    x, y = [], []
    for k in keys :
        x.append(float(k))
        y.append(data[k][peaks[0]])
    return stats.linregress(x, y)
def get_slope_r(folder_path, peaks):
    if os.path.exists(folder_path):
        data_folder = get_data_from_folder(folder_path)
        data = filt(data_folder, peaks)
        k, b, r, p, std = regression_calc(data, peaks)
        return k * 1000, round(-r, 4)
    else:
        print '%s folder does not exist!' % folder
def test():
    folder_path = None
    folder_path = str(raw_input('input the path of folder: '))
    folder_path = r'E:\lcqdata\data_3\mgf\post'
    print folder_path
    if not os.path.exists(folder_path):
        print 'wrong path, run again'
        sys.exit(0)
    peaks = set_peaks()
    data_folder = get_data_from_folder(folder_path)
    data = filt(data_folder, peaks)

    k, b, r, p, std = regression_calc(data, peaks)
    print get_slope_r(folder_path, peaks)
    print k, b, r


def test_path(path):
    folders = [d for d in listdir(path)]
    print folders
    peaks = dict()
    peaks['pre'] = '102 153'
    peaks['post'] = '102 153'
    peaks['reaction'] = '322 153'
    slopes = {}
    for folder in folders:
        folder_path = os.path.join(path, folder)
        p = peaks[folder].split(' ')
        slopes[folder] = get_slope_r(folder_path, p)
    print slopes

def get_slopes(path):
    folders = [d for d in listdir(path)]
    print folders
    peaks = dict()
    peaks['pre'] = '102 153'
    peaks['post'] = '102 153'
    peaks['reaction'] = '322 153'
    slopes = {}
    for folder in folders:
        folder_path = os.path.join(path, folder)
        p = peaks[folder].split(' ')
        slopes[folder] = get_slope_r(folder_path, p)
    return slopes
    
if __name__ == '__main__':
    path = r'E:\lcqdata\data_3\mgf'
    #test()
    slopes = get_slopes(path)
    print slopes



