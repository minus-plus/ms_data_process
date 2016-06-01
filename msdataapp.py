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
        self.types = ['pre', 'reaction', 'post']
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
        data = Data()
        if os.path.exists(filename):
            lines = open(filename).readlines()
            for l in lines:
                l = l.split('\n')[0]
                if l[0].isdigit():
                    l = l.split(' ')
                    peak, value = str(int(round(float(l[0]),0))), float(l[1])
                    data[peak] = data[peak] + value
        else:
            print '%s does not exist!' % filename
            sys.exit(0)
        self.normalize(data)
        return data 
   
    
    def read_data_type(self, files):
        data_files = Data()
        for f in files:
            data = self.read_data_file(join(self.path, f))
            time = float(f.split('_')[-2].split('ms')[0])
            data_files[time] = data
        return data_files
        
    def read_data_path(self):

        files = [f for f in listdir(self.path) if f.endswith('.txt') and isfile(os.path.join(self.path, f))]
        files_type = {}
        files_type['pre'] = []
        files_type['reaction'] = []
        files_type['post'] = []
        pre_post = {}
        for f in files:
            if not f[0].isdigit():
                files_type['reaction'].append(f)
            else:
                ind = f.split('_')[-1].split('.')[0]
                if not ind[-1].isdigit():
                    ind = ind[0:-1]
                ind = int(ind)
                if ind not in pre_post.keys():
                    pre_post[ind] = []
                pre_post[ind].append(f)
        ks = pre_post.keys()
        files_type['pre'] = pre_post[min(ks)]
        files_type['post'] = pre_post[max(ks)]
        
        path_data = {}
        
        for t in files_type:
            path_data[t] = self.read_data_type(files_type[t])
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
            f = '{0:>6} {1:>6} {2:>6}'
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
    
    def get_slopes_type(self, type):
        data_type = self.data[type]
        peaks = self.peaks[type].split(' ')
        self.results.append('===============================')
        f = '{0:>6} {1:>6} {2:>6}'
        self.results.append('%s'% type)
        self.results.append(f.format('time', peaks[0], peaks[1]))
        data = self.filt(data_type, peaks)
        k, b, r, p, std = self.regression_calc(data, peaks)
        return k, round(-r, 4), b
        
    def get_slopes(self):
        slopes = {}
        for type in self.types:
            slopes[type] = self.get_slopes_type(type)
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
        f_e = '{0:>6} {1:<6}%'
        self.results.append('Results:')
        self.results.append('\n-= pre =-')
        self.results.append(f_p.format('p_pre:', P_pre))
        self.results.append(f_s.format('slope_pre:', round(self.slopes['pre'][0]*1000, 4), 'R_pre:', self.slopes['pre'][1]))
        self.results.append('Equation: y = %s x + %s' % (self.slopes['pre'][0], self.slopes['pre'][2] ))
        
        self.results.append('\n-= post =-')
        self.results.append(f_p.format('P_post', P_post))
        self.results.append(f_s.format('slope_post:', round(self.slopes['post'][0]*1000, 4), 'R-post:', self.slopes['post'][1]))
        self.results.append('Equation: y = %s x + %s' % (self.slopes['post'][0], self.slopes['post'][2] ))
        
        self.results.append('\n-= reaction =-')
        self.results.append(f_p.format('P_reaction:', P_reaction))
        self.results.append(f_s.format('slope_reaction:', round(self.slopes['reaction'][0]*1000, 4), 'R_reaction:', self.slopes['reaction'][1]))
        self.results.append('Equation: y = %s x + %s' % (self.slopes['reaction'][0], self.slopes['reaction'][2] ))
        self.results.append(f_k.format('K_exp:', K_exp))
        
        self.results.append('\n-= Efficiency =-')
        self.results.append(f_e.format('Efficiency:', efficiency))
        return self.show_results()
    def show_results(self):
        results_string = '\n'.join(self.results)
        return results_string
if __name__ == '__main__':
    path = r'E:/lcqdata/data/9. 02_29_2016_Data Print_3i (Rovis)/HP1dma/1'
    ms = MSDataApp(path)
    ms.calculate()
    print ms.show_results()
