#!/usr/bin/env python
from sys import exit
import os, config_loader 

def main():
    config = config_loader.load_config()
    if not os.path.exists(config['menu_fifo']):
        os.mkfifo(config['menu_fifo'])

    pipeout = os.open(config['menu_fifo'], os.O_WRONLY)
    instr = ""
    while instr != "n":
        instr = input("Select action:\n1 - block\n2 - run\n3 - kill\n4 - emulate\n")
        os.write(pipeout, bytearray(instr + '\n', 'utf-8'))
        if (instr == '2' or instr == '3'):
            name = input("Enter process name\n")
            os.write(pipeout, bytearray(name + '\n', 'utf-8'))
        instr = input("Add instruction(Y/n)\n")
    os.write(pipeout, b'stop\n')
    return 0

if (__name__ == "__main__"):
    exit(main())
