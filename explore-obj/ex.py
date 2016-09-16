#!/usr/bin/python3
#-*- coding: utf-8 -*-

import liborigin
opj = liborigin.parseOriginFile('../test.opj')


indentation = '    '
maxlistlen = 5
def explore(obj, parentstr, indent):
    print(indent + parentstr)
    if len(indent)>70: 
        print('                          --------------- nesting too deep - halted here ----------------')
        return

    if type(obj) == list:
        print(indent+indentation+'[')
        for n, item in enumerate(obj[:maxlistlen]):
            explore(item, parentstr+'[%d]' % n,  indent+indentation)
        if len(obj) > maxlistlen:
            print(indent+indentation+'--- listing truncated here, %d values would follow ---' % (len(obj)-maxlistlen))
        print(indent+indentation+']')
    elif type(obj) == dict:
        print(indent+indentation+'{')
        for key, value in obj.items():
            explore(value, parentstr+'["'+key+'"]', indent+indentation)
        print(indent+indentation+'}')
    elif type(obj) == str:
        print(indent+indentation+'"'+obj+'"')
    elif type(obj) == bytes:
        print(indent+indentation+'b"'+obj.decode('utf-8').strip()+'"')
    elif type(obj) in (float, int, bool):
        print(indent+indentation,obj)
    else:
        print(indent, obj, type(obj))
        for attrname in dir(obj):
            if not attrname.startswith('__'):
                explore(getattr(obj, attrname), parentstr+'.'+attrname, indent+indentation)
    

explore(opj, '', '')
