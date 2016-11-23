#!/usr/bin/env python
import os, sys, json, config_loader

def main():
    config = config_loader.load_config()
    fifoname = config['clonner_fifo']
    if not os.path.exists(fifoname):
        os.mkfifo(fifoname)
    while True:
        pipein = open(fifoname, 'r')
        instr = pipein.readline()[:-1]
        pipein.close()
        print("Instruction readed: ", instr)
        if (instr == 'clone'):
            clone(config_loader.load_config())
        else:
            pid = os.fork()
            if (pid == 0):
                os.system(instr)
                return

def clone(config):
    pid = os.fork()
    if pid == 0:
        os.execv('/usr/bin/konsole', ['--noclose', '-e', config['menu_path']])

if (__name__ == "__main__"):
    sys.exit(main())
