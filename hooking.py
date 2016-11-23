#!/usr/bin/env python2
from pycopia.OS.Linux import event, Input
from pymouse import PyMouseEvent, PyMouse
from pykeyboard import PyKeyboardEvent, PyKeyboard
import daemon, sys, os, time, json, threading, config_loader

__config_path__ = '/home/valex/workspace/IiPU/lab4/config'
config = {}

def main():
    global config
    config = config_loader.load_config()
    daemon = InputDaemon(pidfile=config['pidfile'], stdout=config['stdout'], stderr=config['stderr'])
    daemon.start()
    return 0

class InputDaemon(daemon.Daemon):

    def run(self):
        key_listener = KeyboardListener()
        click_listener = ClickListener()
        click_thread = threading.Thread(target=click_listener.run)
        click_thread.start()
        key_listener.start()#Blocks until user not quit
        unblock_keys()
        click_listener.stop()
        print 'daemon downs'

class Listener(object):
    #log - log all key presses and mouse clicks
    #act_dict - actions dictionary like (keycode: actions list)
    log = []
    act_dict = {}#They both are static variables
    __keyboard_ev__ = PyKeyboardEvent()
    __keyboard__ = PyKeyboard()
    __mouse__ = PyMouse()

    def __init__(self):
        if self.act_dict == {}:
            for i in range(0, 255):
                self.act_dict[i] = []
    
    @classmethod
    def add_action(self):
        if (len(self.log) == 0):
            return
        pre_last = -1
        if (len(self.log) > 1):
            pre_last = self.log[-2]
        last = self.log[-1]
        new_actions = get_new_action(last, pre_last)
        self.act_dict[last].extend(new_actions)

    @classmethod
    def simulate(self, key_code):
        if (key_code > 8):#In X 11 keycodes start from 9 thats why
            #keycodes from 1 to 8 allocated to mouse buttons
            key_name = self.__keyboard_ev__.lookup_char_from_keycode(key_code)
            self.__keyboard__.tap_key(key_name)
        else:
            (x, y) = self.__mouse__.position()
            self.__mouse__.click(x, y, key_code)
            

class ClickListener(PyMouseEvent, Listener):
    
    mask = ['1','2','3','4','5','6','0','0','0']#It's static

    def __init__(self):
        PyMouseEvent.__init__(self)

    def click(self, x, y, button, press):
        if press:
            execute(self.act_dict[button])
            self.log.append(button)
            print 'clicked ' + str(button) 

class KeyboardListener(Listener):

    def start(self):
        event_file = Input.EventFile(config['keyboard_event'], 'r')
        out = 0
        while True:
            current = event_file.read()
            if (current.evtype == Input.EV_KEY and current.value == 0):
                if (current.code == event.KEY_F1):
                    self.add_action()
                if (current.code == event.KEY_F2):
                    break
                execute(self.act_dict[current.code + 8])
                self.log.append(current.code + 8)
                print str(current.code) 

def execute(act_list):
    print 'execute: ' + str(act_list)
    for action in act_list:
        (instr, arg) = action
        if instr == '4':#simulate
            Listener.simulate(arg)
        if instr == '3':#kill
            os.system('kill -9 $(pidof ' + arg + ')')
        if instr == '2':#run
            f = open(config['clonner_fifo'], 'w')
            f.write(arg + '\n')
            f.close()

def get_new_action(key_code, pre_key):
    run_menu()
    instr = get_instruction()
    instr_list = []
    while instr!= 'stop':
        if instr == '1': #block key
            block_key(key_code)
        elif instr == '4': #emulate key which was pushed before current
            instr_list.append( (instr, pre_key) )
        else: #kill / start programm
            arg = get_instruction()
            instr_list.append( (instr, arg) )
        instr = get_instruction()
    return instr_list

def run_menu():
    global cofig
    print config['clonner_fifo']
    pipeout = os.open(config['clonner_fifo'], os.O_WRONLY)
    os.write(pipeout, b"clone\n")
    os.close(pipeout)

def get_instruction():
    global config
    menu_fifo =config['menu_fifo']
    if not os.path.exists(menu_fifo):
        os.mkfifo(menu_fifo)
    pipein = open(menu_fifo, 'r')
    instr = pipein.readline()[:-1]
    return instr

def block_key(key_code):
    instr = ""
    if (key_code > 8):
        instr = 'xmodmap -e \"keycode ' + str(key_code) + '=' + '\"'
    else:
        ClickListener.mask[key_code-1] = '0'
        instr = 'xmodmap -e \"pointer = ' + ' '.join(ClickListener.mask) + '\"'
    print instr
    os.system(instr)

def unblock_keys():
    global config
    os.system('xmodmap ' + config['keymap'])

if __name__ == '__main__':
    sys.exit(main())
