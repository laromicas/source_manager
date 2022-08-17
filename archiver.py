#!/usr/bin/python3
import sys
import os
from datetime import datetime
import sourceManager as sm

toarchive = sys.argv[1] if len(sys.argv) > 1 else None
if not toarchive:
    print('No file specified')
    exit(1)


data = sm.loaddata('list.json')
# print(data.keys())
# print(data['indexes']['urls'].keys())

resource = data['indexes']['urls'].get(toarchive, None)
if not resource:
    print('No resource found')
    exit(1)

# print(resource)
date = datetime.today().strftime('%Y-%m-%d')


path_array = resource['path'].split('/')

execute_path = os.getcwd() + '/' + '/'.join(path_array[:-1])

source_path = path_array[-1:][0]
# print(execute_path)
# print(source_path)
# print(resource)

command = 'cd ' + execute_path + \
    ' && 7z a -t7z -m0=lzma2 -mx=9 -aoa -mfb=64 -md=32m ' + source_path + '_' + date + '.7z ' + source_path + \
    ' && mv ' + source_path + '_' + date + '.7z ' + os.getcwd() + '/../dead/' + resource['app_type'] + \
    ' && rm -rf ' + source_path

os.system(command)

command = './sourceManager.py delete ' + \
    resource['app_type'] + ' ' + resource['developer'] + ' ' + resource['name']
os.system(command)
