#!/usr/bin/env python3

import os
import re
import subprocess
import argparse
from fuzzyfinder import main as ff

IMPORTANT_GROUP='!'
LONG_GROUP='_'

def deletion_index(arg :str, lines :list[str]):
    if arg.isdecimal():
        index = int(arg)
        if index < 1 or index > len(lines): return None

        important_quick_list = []
        important_long_list = []
        osef_quick_list = []
        osef_long_list = []
        for i in range(0, len(lines)):
            if re.match(f'^{IMPORTANT_GROUP}: .*', lines[i]) != None:
                important_quick_list.append(i)
            elif re.match(f'^{IMPORTANT_GROUP}{LONG_GROUP}: .*', lines[i]) != None:
                important_long_list.append(i)
            elif re.match(f'^: .*', lines[i]) != None:
                osef_quick_list.append(i)
            elif re.match(f'^{LONG_GROUP}: .*', lines[i]) != None:
                osef_long_list.append(i)

        offset = 0
        if len(important_quick_list) > 0 and index-offset <= len(important_quick_list):
            return int(important_quick_list[index-offset-1])
        else:
            offset += len(important_quick_list)
            if len(important_long_list) > 0 and index-offset <= len(important_long_list):
                return int(important_long_list[index-offset-1])
            else:
                offset += len(important_long_list)
                if len(osef_quick_list) > 0 and index-offset <= len(osef_quick_list):
                    return int(osef_quick_list[index-offset-1])
                else:
                    offset += len(osef_quick_list)
                    return int(osef_long_list[index-offset-1])

    else:
        matches = list(ff.fuzzyfinder(arg, lines))
        if len(matches) == 1:
            for number, line in enumerate(lines):
                if line == matches[0]:
                    return number+1
        print('Could not find a matching entry for this text')
        return None

def print_list(title: str, lines: list[str], offset: int, filter: str|None = None):
    def hasMatch(str):
        if(filter == None): return True

        match = re.match(filter, str)
        if(match == None): return False
        return True

    lines = [line[line.find(':')+1:].strip(' \t') for line in lines if hasMatch(line)]

    if len(lines) > 0:
        print(title)
        ps = subprocess.Popen(['echo', ('offset\n' * int(offset))+''.join(lines).strip()], stdout=subprocess.PIPE)
        subprocess.run(['bat', '--style=numbers,snip,grid', f'--line-range={offset+1}:'], stdin=ps.stdout)
        ps.wait()
        return len(lines)
    return 0

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

arg_parser = argparse.ArgumentParser(prog='todo', description='Simple todo utility')
arg_parser.add_argument('-x', '--delete', nargs=1, metavar='<line number>')
arg_parser.add_argument('-a', '--add', nargs=1, metavar='<stuff to do>')
arg_parser.add_argument('-i', '--important', action='store_true', help='is the task important')
arg_parser.add_argument('-l', '--long', action='store_true', help='is the task long to do')

args = arg_parser.parse_args()

if args.add == None and (args.important != False or args.long != False):
    arg_parser.error('Use --important and --long with --add only')

filepath = os.path.expanduser('~/.cache/todo.todo')

# Add
if args.add != None:
    with open(filepath, 'a') as f:
        entry = ': '+args.add[0]+'\n'
        if(args.long == True):
            entry = LONG_GROUP+entry
        if(args.important == True):
            entry = IMPORTANT_GROUP+entry
        f.write(entry)
# Delete
elif args.delete != None:
    if os.path.exists(filepath):
        with open(filepath, 'r+') as f:
            lines = f.readlines()
            line_num = len(lines)
            del_line = deletion_index(args.delete[0], lines)
            if del_line != None:
                f.seek(0)
                if del_line <= 1:
                    #Just delete everything
                    f.truncate()
                    pass
                if del_line < line_num and del_line >= 0:
                    print('[x] '+lines[del_line][lines[del_line].find(':')+1:].strip())
                    f.truncate()
                    f.writelines(lines[:del_line])
                    f.writelines(lines[del_line+1:])
                else:
                    print('Nothing to cross here')
            else:
                print('Nothing to cross here')
    else:
        print('Nothing to cross here')
# Show
else:
    try:
        with open(filepath, 'r') as f:
            lines = f.readlines()
            if len(lines) > 0:
                printed = 0
                print('')
                # Print important short stuff
                printed += print_list(f'{bcolors.FAIL}Important quick{bcolors.ENDC}', lines, printed, f'^{IMPORTANT_GROUP}: (.*)')
                # Print important long stuff
                printed += print_list(f'{bcolors.WARNING}Important long{bcolors.ENDC}', lines, printed, f'^{IMPORTANT_GROUP}{LONG_GROUP}: (.*)')
                # Print non important short stuff
                printed += print_list(f'{bcolors.OKBLUE}Osef quick{bcolors.ENDC}', lines, printed, f'^: (.*)')
                # Print non important long stuff
                printed += print_list(f'{bcolors.OKGREEN}Osef long{bcolors.ENDC}', lines, printed, f'^{LONG_GROUP}: (.*)')
            else:
                print('Nothing todo!')
    except FileNotFoundError:
        print('Nothing todo!')
