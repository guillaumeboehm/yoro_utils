#!/usr/bin/env python3

import os
import re
import subprocess
import argparse
from fuzzyfinder import main as ff

def deletion_index(arg :str, lines :list[str]):
    if arg.isdecimal():
        return int(arg)
    else:
        matches = list(ff.fuzzyfinder(arg, lines))
        if len(matches) != 1:
            print('Could not find a matching entry for this text')
            return None
        else:
            for number, line in enumerate(lines):
                if line == matches[0]:
                    return number+1

def print_list(title: str, lines: list[str], filter: str|None = None):
    def hasMatch(str):
        if(filter == None): return True

        match = re.match(filter, str)
        if(match == None): return False
        return True

    lines = [line[line.find(':')+1:] for line in lines if hasMatch(line)]

    if len(lines) > 0:
        print(title)
        ps = subprocess.Popen(['echo', ''.join(lines).strip()], stdout=subprocess.PIPE)
        subprocess.run(['bat', '--style=numbers,snip,grid'], stdin=ps.stdout)
        ps.wait()

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
            entry = '_'+entry
        if(args.important == True):
            entry = '!'+entry
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
                if del_line <= line_num and del_line > 0:
                    f.truncate()
                    f.writelines(lines[:del_line-1])
                    f.writelines(lines[del_line:])
                    print('[x] '+lines[del_line-1].strip())
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
                print('')
                # Print important short stuff
                print_list(f'{bcolors.FAIL}Important quick{bcolors.ENDC}', lines, '^!: (.*)')
                # Print important long stuff
                print_list(f'{bcolors.WARNING}Important long{bcolors.ENDC}', lines, '^!_: (.*)')
                # Print non important short stuff
                print_list(f'{bcolors.OKBLUE}Osef quick{bcolors.ENDC}', lines, '^: (.*)')
                # Print non important long stuff
                print_list(f'{bcolors.OKGREEN}Osef long{bcolors.ENDC}', lines, '^_: (.*)')
            else:
                print('Nothing todo!')
    except FileNotFoundError:
        print('Nothing todo!')
