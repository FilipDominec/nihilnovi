#!/usr/bin/python3
#-*- coding: utf-8 -*-

from pathlib import Path
import liborigin
import sys
style = 'abbrev' #$False
if style == 'color':
    normal = r"\033[1;0m"
    bold   = r"\033[1;1m"
    grey   = r"\033[2;2m"
else:
    normal, bold  , grey   = '', '', ''
maxlistlen = 200
allstrings = []

branchdict = {'│':'├', '║':'╟', '┃':'┣'}


def save_sheetdata(data, head, out_dir_name):
    outdir = Path(out_dir_name)
    outdir.mkdir(exist_ok = True)
    #print(lineindent,f"SAVING INTO {filename}/{sheetname.decode('utf8')}.dat: {len(sheetdata)} columns") #TODO
    with open(outdir / (sheetname + '.dat'), 'w') as outfile:
        outfile.write('#' + '\t'.join(sheethead) + '\n')
        for vals in zip(*sheetdata):
            if isinstance(vals[0], float) and vals[0] != 0 and abs(vals[0])<1e-100: continue  # origin encodes NaNs as *very* small numbers
            outfile.write('\t'.join(str(val) for val in vals)+'\n')

def explore(obj, parentstr, indent):
    global sheetdata
    global sheethead
    global sheetname 
    enc = 'cp1250' ## not specified by liborigin, set manually!

    lineindent = indent[:-1]+ branchdict.get(indent[-1:],'') + parentstr

    if style == 'color': indent = indent + grey + parentstr + normal ## prints ancestry objects with grey color for better clarity (terminal only)
    elif style == 'abbrev':        indent = indent + ' '*(len(parentstr)+1) ## replaces ancestry objects with whitespace for clarity
    else: indent = indent +  parentstr  ## prints ancestry objects with grey color for better clarity (terminal only)
    if len(indent)>200: 
        print(lineindent,'                          --------------- nesting too deep - halted here ----------------')
        return

    if isinstance(obj, list):
        print(lineindent,bold+'[', normal)
        for n, item in enumerate(obj[:maxlistlen]):
            #print(lineindent,f'n {n} item {item}')
            explore(item, 'item #%d' % n,  indent[:-1]+'║')
        if len(obj) > maxlistlen:
            print(lineindent+bold+'--- listing truncated here, %d values would follow ---' % (len(obj)-maxlistlen))
        print(lineindent, bold+']', normal)
    elif isinstance(obj, dict):
        print(lineindent,bold+'{', normal)
        for key, value in obj.items():
            #print(lineindent,f'K {key} V {value}')
            explore(value, '["'+key+'"]', indent[:-1]+'┃')
        print(lineindent,bold+'}', normal)
    elif isinstance(obj, str):
        print(lineindent,bold+'"'+obj+'"', normal)
        allstrings.append(obj)
    elif isinstance(obj, bytes):
        print(lineindent,bold+' b"'+obj.decode(enc).strip()+'"')
    elif type(obj) in (float, int, bool):
        print(lineindent,bold,obj, normal)
    else:
        print(lineindent,bold, obj, grey, type(obj), normal)
        
        #print(lineindent,' '*(len(indent)-len(parentstr)), grey, usefulattrs, normal)
        if isinstance(obj, liborigin.SpreadSheet):
            if sheetdata: save_sheetdata(sheetdata, sheethead, out_dir_name)
            sheetdata = []
            sheethead = []
            try:
                sheetname = obj.label.decode(enc).split('@${[')[0]
            except AttributeError:
                sheetname = obj.name.decode(enc)

            #if getattr(obj, 'label', None):
                #print(f"---- sheet named {sheetname} has label {getattr(obj, 'label', b'').decode('cp1252').split('@${[')[0]}")
        if isinstance(obj, liborigin.SpreadColumn):
            if getattr(obj, 'type', None) != 6:
                sheetdata.append(obj.data)
                sheethead.append(obj.name.decode(enc))
        usefulattrs = [attrname for attrname in dir(obj) if not attrname.startswith('__')]
        for attrname in usefulattrs:
            explore(getattr(obj, attrname), '.'+attrname, indent[:-1]+'│')


for opj_name in sys.argv[1:]:
    print('PROCESSING', opj_name)
    try:
        opj = liborigin.parseOriginFile(opj_name)
    except IndexError:
        print(lineindent,'Please specify the origin file'); quit()

    sheetdata, sheethead, sheetname = [], [], None

    out_dir_name=opj_name.replace(' ','_').replace('.opj','_exported')
    explore(opj, '', '')
    if sheetdata: save_sheetdata(sheetdata, sheethead, out_dir_name)
    
