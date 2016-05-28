from distutils.core import setup
import py2exe


opts = {"py2exe": {
    "includes": ['scipy', 'scipy.integrate', 'scipy.special.*','scipy.linalg.*', 'scipy.sparse.csgraph._validation']}}
setup(console=['msdataprocess.py'],options=opts)