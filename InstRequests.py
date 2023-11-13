import threading
import random
import pdb
from time import sleep


from ConsoleOutput import console
from ConfigGet import main_delay, delay_error
# from ProcessHandler import format_all_processes_to_ini


MAIN_DELAY = main_delay()
LAST_DELAY_ERROR = 0
LAST_REQUEST = {'integer': MAIN_DELAY + 1, 'decimal': 0}


def sleeping(process, time):

    repeats = int(time // 0.5)
    for _ in range(repeats):
        if process.status == 'alive':
            sleep(0.5)
        else:
            return


def process_delay_error():
    global LAST_DELAY_ERROR
    main_error = delay_error()
    while True:
        dice = random.randint(0, 100)
        add_delay = main_error*dice//100
        if 2*abs(add_delay-LAST_DELAY_ERROR) > main_error:
            break

    LAST_DELAY_ERROR = add_delay
    console(f'ADD_DELAY: {add_delay}', end='\n\n')
    return add_delay


def stopwatch():
    global LAST_REQUEST, MAIN_DELAY
    while True:
        sleep(0.2)
        LAST_REQUEST['decimal'] += 2
        if LAST_REQUEST['decimal'] == 10:
            LAST_REQUEST['decimal'] = 0
            LAST_REQUEST['integer'] += 1


def reload_stopwatch():
    global LAST_REQUEST
    console(f'[STOPWATCH RELOAD] LAST_REQUEST: {LAST_REQUEST["integer"]}.{LAST_REQUEST["decimal"]} --> 0', level='global')
    LAST_REQUEST['integer'] = 0
    LAST_REQUEST['decimal'] = 0


def get_last_request():
    return LAST_REQUEST


def get_last_request_error():
    return LAST_DELAY_ERROR


# threading.Thread(target=stopwatch).start()




