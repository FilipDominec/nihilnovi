#!/usr/bin/python3
#-*- coding: utf-8 -*-
"""
A simplistic attempt to parse simple procedural languages that control e.g. MOVPE apparatuses gas flow (not finished)
"""

import sys,re

time = 0
labels  = {}

tableheader = [] ## TODO TODO efficient accumulation of data w/ possibility of new variables in the middle of EPI recipe
tablevalues = []
tabletiming = []

with open(sys.argv[1], encoding='latin1') as epifile:
    lines = epifile.readlines()
    for n, line in enumerate(lines):
        #line = '1:020 " Setup: lateral growth", NH3_2.run close, TMGa_1.run close,  N2.line close, N2.run open,'

        ## Detect and remember labels
        if len(line.strip())>=1 and line.strip()[-1] == '{': 
            labels[line.strip()] = n
            continue
            
        timematch       = re.match('^\\s*\\d?\\d?:?\\d+', line)
        timedelim       = timematch.end() if timematch else 0

        namematch       = re.search('"[^"]*"', line)
        namedelim       = namematch.end() if namematch else timedelim
        cmntmatch       = re.search('#', line)
        cmntdelim       = cmntmatch.end()-1 if cmntmatch else 1000000
        timestr, namestr, cmdsstr = line[:timedelim].strip(), line[timedelim:namedelim].strip(), line[namedelim:cmntdelim].strip() 
        print("DEBUG: timestr, = ", timestr,)
        print("DEBUG: namestr, = ", namestr,)
        print("DEBUG: cmdsstr = ", cmdsstr)
        for cmd in [c.strip().strip(';') for c in cmdsstr.split(',') if c.strip()!='']:
            print(time, "     DEBUG: cmd = ", cmd)
            if ' to ' in cmd: 
                variable, value = [c.strip() for c in cmd.split(' to ', 1)]
                variables[variable]

            ## TODO if cmd == "GOTO OR WHATEVER": n = labels[JUMPTO]; continue


        ## Advance the time 
        if timematch:
            if ':' in timestr:  time += 60*int(timestr.split(':')[0]) +   int(timestr.split(':')[1])
            else:               time +=                                 int(timestr);

        
