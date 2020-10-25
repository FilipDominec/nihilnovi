#!/usr/bin/python3
#-*- coding: utf-8 -*-

import liborigin
import sys
try:
    opj = liborigin.parseOriginFile(sys.argv[1])
except IndexError:
    print('Please specify the origin file'); quit()

coloured = 0 #$False
if coloured:
    normal = "\033[1;0m"
    bold   = "\033[1;1m"
    grey   = "\033[2;2m"
else:
    normal, bold  , grey   = '', '', ''
maxlistlen = 5
allstrings = []
def explore(obj, parentstr, indent):
    print(indent + parentstr, end='')
    if coloured: indent = indent + grey + parentstr + normal ## prints ancestry objects with grey color for better clarity (terminal only)
    else:        indent = indent + '_'*len(parentstr) ## replaces ancestry objects with whitespace for clarity
    if len(indent)>200: 
        print('                          --------------- nesting too deep - halted here ----------------')
        return

    if type(obj) == list:
        print(bold+'[', normal)
        for n, item in enumerate(obj[:maxlistlen]):
            explore(item, 'item #%d' % n,  indent)
        if len(obj) > maxlistlen:
            print(indent+bold+'--- listing truncated here, %d values would follow ---' % (len(obj)-maxlistlen))
        print(bold+']', normal)
    elif type(obj) == dict:
        print(bold+'{', normal)
        for key, value in obj.items():
            explore(value, '["'+key+'"]', indent)
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
            explore(getattr(obj, attrname), '.'+attrname, indent)
    
explore(opj, '', '')
print(allstrings)
