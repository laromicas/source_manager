import os
from sys import platform

WORKDIR = os.getenv('WORKDIR', '/mnt/sources')
os.chdir(WORKDIR)
