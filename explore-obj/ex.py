#!/usr/bin/python3
#-*- coding: utf-8 -*-

import liborigin
import sys
try:
    opj = liborigin.parseOriginFile(sys.argv[1])
except IndexError:
    print('Please specify the origin file'); quit()

style = 'x' #$False
if style == 'color':
    normal = r"\033[1;0m"
    bold   = r"\033[1;1m"
    grey   = r"\033[2;2m"
else:
    normal, bold  , grey   = '', '', ''
maxlistlen = 5
allstrings = []

branchdict = {'│':'├', '║':'╟', '┃':'┣'}

def explore(obj, parentstr, indent):

    print(indent[:-1]+ branchdict.get(indent[-1:],'') + parentstr, end='')

    if style == 'color': indent = indent + grey + parentstr + normal ## prints ancestry objects with grey color for better clarity (terminal only)
    else:        indent = indent + ' '*(len(parentstr)+1) ## replaces ancestry objects with whitespace for clarity
    if len(indent)>200: 
        print('                          --------------- nesting too deep - halted here ----------------')
        return

    if type(obj) == list:
        print(bold+'[', normal)
        for n, item in enumerate(obj[:maxlistlen]):
            explore(item, 'item #%d' % n,  indent[:-1]+'║')
        if len(obj) > maxlistlen:
            print(indent+bold+'--- listing truncated here, %d values would follow ---' % (len(obj)-maxlistlen))
        print(indent, bold+']', normal)
    elif type(obj) == dict:
        print(bold+'{', normal)
        for key, value in obj.items():
            explore(value, '["'+key+'"]', indent[:-1]+'┃')
        print(bold+'}', normal)
    elif type(obj) == str:
        print(bold+'"'+obj+'"', normal)
        allstrings.append(obj)
    elif type(obj) == bytes:
        print(bold+' b"'+obj.decode('utf-8').strip()+'"')
    elif type(obj) in (float, int, bool):
        print(bold,obj, normal)
    else:
        print(bold, obj, grey, type(obj), normal)
        usefulattrs = [attrname for attrname in dir(obj) if not attrname.startswith('__')]
        #print(' '*(len(indent)-len(parentstr)), grey, usefulattrs, normal)
        for attrname in usefulattrs:
            explore(getattr(obj, attrname), '.'+attrname, indent[:-1]+'│')
    
explore(opj, '', '')
print(allstrings)
