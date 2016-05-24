# this file used to read parameters from files
import os
import sys
from os.path import isfile, join
def read_parameters(file):
    if os.path.exists(file):
        lines = open(file).readlines()
        params = {}
        for l in lines:
            l = l.split('\n')[0]
            if l:
                p = l.split(': ')
                if p[0][0:3] == 'com':
                    p[1] = p[1].split(', ')
                elif p[0][0:3] != 'typ':
                    p[1] = float(p[1])
                params[p[0]] = p[1]
        return params
    else:
        print 'file %s does not exist!'
if __name__ == '__main__':
    cwd = os.getcwd()
    file = os.path.join(cwd, r'params_reaction.txt')
    print read_parameters(file)