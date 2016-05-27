#!/usr/bin/python
# coding: utf-8

import os
import sys
from os import listdir
from os.path import isfile, join
import json

import operator
import math
import numpy as np
from scipy import stats

import read_params
class Data(dict):
    def __getitem__(self, index):
        self.setdefault(index, 0.0)
        return dict.__getitem__(self,index)

class MSDataApp(object):
    def __init__(self, path):
        self.path = path   
        self.data = self.read_data_path()
        self.params = self.read_params()
        self.kinetics_params = self.params['kinetics']
        self.reaction_params = self.params['reaction']
        self.peaks = self.read_peaks()
        self.results = []
       
    def read_peaks(self):
        peaks={}
        peaks['pre'] = self.kinetics_params['peaks']
        peaks['post'] = peaks['pre']
        peaks['reaction'] = self.reaction_params['peaks']
        return peaks
        
    def read_params(self):
        cwd = os.getcwd()
        params_file = open('params.json')
        params = json.load(params_file)
        params_file.close()
        return params
    
    def normalize(self, data):
        max_key = max(data.iteritems(), key=operator.itemgetter(1))[0]
        max_value = data[max_key]
        for key in data:
            val = data[key]
            data[key] = val / max_value * 100
    
    def read_data_file(self, filename):
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
        self.normalize(data)
        return data 
    
    def read_data_folder(self, path):
        if os.path.exists(path):
            print 'loading folder %s..' % path
            data_folder=Data()
            files = [f for f in listdir(path) if isfile(join(path, f))]
            for f in files:
                data = self.read_data_file(join(path, f))
                time = float(f.split('_')[-2].split('ms')[0])
                data_folder[time] = data
            return data_folder
        else:
            print '%s does not exist!' % path
    def read_data_path(self):
        folders = [d for d in listdir(self.path)]
        path_data = {}
        for folder in folders:
            folder_path = os.path.join(self.path, folder)
            path_data[folder] = self.read_data_folder(folder_path)
        return path_data
        
    def filt(self, data, peaks):
        new_data = dict()
        keys = sorted(data.keys())
        for key in keys:
            d = {}
            val = data[key][peaks[0]] + data[key][peaks[1]]
            #print val
            d[peaks[0]] = math.log(data[key][peaks[0]] / val )
            d[peaks[1]] = math.log(data[key][peaks[1]] / val)
            f = '{0:6} {1:6} {2:6}'
            #print f.format(key, round(data[key][peaks[0]], 2), round(data[key][peaks[1]], 2))
            self.results.append(f.format(key, round(data[key][peaks[0]], 2), round(data[key][peaks[1]], 2)))
            new_data[key] = d
        return new_data    
        
            
    def regression_calc(self, data, peaks):
        keys = sorted(data.keys()) 
        x, y = [], []
        for k in keys :
            x.append(float(k))
            y.append(data[k][peaks[0]])
        return stats.linregress(x, y)
    
    def get_slopes_folder(self, folder):
        data_folder = self.data[folder]
        peaks = self.peaks[folder].split(' ')
        self.results.append('===============================')
        f = '{0:>6} {1:>6} {2:>6}'
        self.results.append('%s'% folder)
        self.results.append(f.format('time', peaks[0], peaks[1]))
        data = self.filt(data_folder, peaks)
        k, b, r, p, std = self.regression_calc(data, peaks)
        return k, round(-r, 4)
        
    def get_slopes(self):
        folders = [d for d in listdir(self.path)]
        slopes = {}
        for folder in folders:
            slopes[folder] = self.get_slopes_folder(folder)
        self.slopes = slopes
        return slopes
    def calculate(self):
        slopes = self.get_slopes()
        P_pre = - slopes['pre'][0] * 1000 / (float(self.kinetics_params['kcoll']) * float(self.kinetics_params['constant']))
        P_post = - slopes['post'][0] * 1000 / (float(self.kinetics_params['kcoll']) * float(self.kinetics_params['constant']))
        P_reaction = (P_pre + P_post) / 2
        K_exp = -slopes['reaction'][0] * 1000 / (P_reaction * float(self.reaction_params['constant']))
        efficiency = round(K_exp / float(self.reaction_params['kcoll']) * 100, 2)
        self.results.append('')
        self.results.append('===============================')
        f_p = '{0:>6} {1:<10}'
        f_s = '{0:>6} {1:<10} {2:>6} {3:<10}'
        f_k = '{0:>6} {1:<16}' 
        f_e = '{0:>6} {1:<6}'
        self.results.append('Results:')
        self.results.append(f_p.format('p_pre:', P_pre))
        self.results.append(f_s.format('slope_pre:', round(self.slopes['pre'][0]*1000, 4), 'R_pre:', self.slopes['pre'][1]))
        self.results.append(f_p.format('P_post', P_post))
        self.results.append(f_s.format('slope_post:', round(self.slopes['post'][0]*1000, 4), 'R-post:', self.slopes['post'][1]))
        self.results.append(f_p.format('P_reaction:', P_reaction))
        self.results.append(f_s.format('slope_reaction:', round(self.slopes['reaction'][0]*1000, 4), 'R_reaction:', self.slopes['reaction'][1]))
        self.results.append(f_k.format('K_exp:', K_exp))
        self.results.append(f_e.format('Efficiency:', efficiency))
        return self.show_results()
    def show_results(self):
        results_string = '\n'.join(self.results)
        return results_string
if __name__ == '__main__':
    path = r'E:\lcqdata\data_3\mgf'
    ms = MSDataApp(path)
    ms.calculate()
    print ms.show_results()
