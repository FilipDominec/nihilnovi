#!/usr/bin/python3
#-*- coding: utf-8 -*-

import liborigin
opj = liborigin.parseOriginFile('../test.opj')

coloured = True
if coloured:
    normal = "\033[1;0m"
    bold   = "\033[1;1m"
    grey   = "\033[1;2m"
else:
    normal, bold  , grey   = '', '', ''
maxlistlen = 5
def explore(obj, parentstr, indent):
    print(indent + parentstr)
    if coloured: indent = indent + grey + parentstr + normal ## prints ancestry objects with grey color for better clarity (terminal only)
    else:        indent = indent + ' '*len(parentstr) ## replaces ancestry objects with whitespace for clarity
    if len(indent)>200: 
        print('                          --------------- nesting too deep - halted here ----------------')
        return

    if type(obj) == list:
        print(indent+bold+'[', normal)
        for n, item in enumerate(obj[:maxlistlen]):
            explore(item, '[%d]' % n,  indent)
        if len(obj) > maxlistlen:
            print(indent+bold+'--- listing truncated here, %d values would follow ---' % (len(obj)-maxlistlen))
        print(indent+bold+']', normal)
    elif type(obj) == dict:
        print(indent+bold+'{', normal)
        for key, value in obj.items():
            explore(value, '["'+key+'"]', indent)
        print(indent+bold+'}', normal)
    elif type(obj) == str:
        print(indent+bold+'"'+obj+'"', normal)
    elif type(obj) == bytes:
        print(indent+bold+' b"'+obj.decode('utf-8').strip()+'"')
    elif type(obj) in (float, int, bool):
        print(indent+bold,obj, normal)
    else:
        print(indent, bold, obj, grey, type(obj), normal)
        usefulattrs = [attrname for attrname in dir(obj) if not attrname.startswith('__')]
        print(' '*(len(indent)-len(parentstr)), grey, usefulattrs, normal)
        for attrname in usefulattrs:
            explore(getattr(obj, attrname), '.'+attrname, indent)
    

explore(opj, '', '')
