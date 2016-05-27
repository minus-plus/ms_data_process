#!/usr/bin/python
# coding: utf-8

import os
import sys
from os import listdir
from os.path import isfile, join

import operator
import math
import numpy as np
from scipy import stats

import read_params
class Data(dict):
    def __getitem__(self, index):
        self.setdefault(index, 0.0)
        return dict.__getitem__(self,index)

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
        return k, round(-r, 4)
    else:
        print '%s folder does not exist!' % folder

def get_slopes(path, peaks):
    folders = [d for d in listdir(path)]
    slopes = {}
    for folder in folders:
        folder_path = os.path.join(path, folder)
        p = peaks[folder].split(' ')
        slopes[folder] = get_slope_r(folder_path, p)
    return slopes

def get_params():
    cwd = os.getcwd()
    params_reaction = os.path.join(cwd, r'params_reaction.txt')
    params_kinetics = os.path.join(cwd, r'params_kinetics.txt')
    params = {}
    p_r = read_params.read_parameters(params_reaction)
    p_k = read_params.read_parameters(params_kinetics)
    return p_k, p_r
    
def calculate(path):
    kenetics_params, reaction_params = get_params()
    # read peaks:
    peaks = dict()
    peaks['pre'] = kenetics_params['compound_1'][1] + ' ' + kenetics_params['compound_2'][1]
    peaks['post'] = peaks['pre']
    peaks['reaction'] = reaction_params['compound_1'][1] + ' ' + reaction_params['compound_2'][1]
    
    slopes = get_slopes(path, peaks)
    P_pre = - slopes['pre'][0] * 1000 / (kenetics_params['kcoll'] * kenetics_params['constant'])
    P_post = - slopes['post'][0] * 1000 / (kenetics_params['kcoll'] * kenetics_params['constant'])
    P_reaction = (P_pre + P_post) / 2
    K_exp = -slopes['reaction'][0] * 1000 / (P_reaction * kenetics_params['constant'])
    efficiency = round(K_exp / reaction_params['kcoll'] * 100, 2)
    print ''
    print '========================================='
    print 'results: '
    print r'efficiency is %s %%' % efficiency
    return efficiency
    
if __name__ == '__main__':
    path = r'E:\lcqdata\data_3\mgf'
    calculate(path)


