from time import sleep

from ConsoleOutput import console
from InstRequests import get_last_request_error
from Stopwatch import Stopwatches
from HandlerProcess import get_processes
from ConfigGet import main_delay


def get_permission(p):

    processes = get_processes()

    if p not in processes or p.status == 'dead':
        console(f'Process {p.id} ({p.info}) is already dead', level='exception')
        exit()

    # Checks if there are running processes in ALL_PROCESSES
    for process in processes:
        if process.state == 'running':
            console(f'Process {p.id} ({p.info})  should wait  (# other process is running)', level='norm')
            return {'permission': False, 'tag': 'other process is running', 'process_id': p.id,
                    'running_process': process}

    # Checks if process is the first in queue
    if p in processes:
        if p.queue != 1:
            console(f'Process {p.id} ({p.info}) not the first in queue', level='norm')
            return {'permission': False, 'tag': 'not the first in queue', 'process': p}
    else:
        console(f'Process {p.id} ({p.info}) not found in Processes', level='error')
        console('Processes:', [f'{p.id} : {p.info}' for p in processes])
        return {'permission': False, 'tag': 'error', 'process': p}

    # Checks if there are "1st priority" processes in ALL_PROCESSES
    if p.priority != 1:
        for process in processes:
            if process.priority == 1:
                console(f'Process {p.id} ({p.info}) should wait  (# low priority)', level='norm')
                return {'permission': False, 'tag': 'low priority', 'process_id': p.id}

    # Checks that the requested delay (MAIN_DELAY) has elapsed since the last request
    if Stopwatches.Last_request.check(main_delay()+get_last_request_error()):
        console(f'Process {p.id}  ({p.info}) should wait  (# too frequent requests)', level='norm')
        return {'permission': False, 'tag': 'too frequent requests', 'process_id': p.id}

    return {'permission': True}


def process_permission(response):

    if response['permission'] is True:
        console(f'[PROCESS PERMISSION]: Access is allowed', level='good')
        return None
    else:
        if response['tag'] == 'low priority':
            first_priorities = len([process for process in get_processes() if process.priority == 1])
            waiting_time = first_priorities*main_delay()
            if first_priorities == 1:
                number_line = '1 process'
            else:
                number_line = f'{first_priorities} processes'
            console(f'There are {number_line} of the 1st priority in queue.'
                  f'Estimated waiting time is {waiting_time}-{2*waiting_time} seconds')
            return waiting_time

        if response['tag'] == 'other process is running':
            running_process = response['running_process']
            waiting_time = main_delay() + 10
            console(f'Process {running_process.info} is running now. Wait for {waiting_time}-{2*waiting_time-10} seconds')
            return waiting_time

        if response['tag'] == 'too frequent requests':
            MAIN_DELAY, last_request, LAST_DELAY_ERROR = main_delay(), Stopwatches.Last_request, get_last_request_error()
            waiting_time = LAST_DELAY_ERROR+MAIN_DELAY-last_request.int
            if waiting_time <= 0:
                waiting_time = 1
            console(f'The last request was made {last_request.time} seconds ago '
                    f'(MAIN_DELAY+ADD_DELAY is {MAIN_DELAY}+{LAST_DELAY_ERROR} seconds). '
                    f'Estimated waiting time is {waiting_time}-{waiting_time*2} seconds', end='\n\n')
            return waiting_time

        if response['tag'] == 'not the first in queue':

            main_inst_delay = main_delay()

            process = response['process']
            queue = process.queue
            waiting_time = (queue-1) * main_inst_delay

            if queue == 2:
                queue_line = '2nd'
            elif queue == 3:
                queue_line = '3rd'
            else:
                queue_line = f'{queue}th'

            console(f'Process {process.info} {queue_line} in the execution queue. '
                    f'Estimated waiting time is {waiting_time}-{waiting_time+main_inst_delay} seconds')
            return waiting_time

        if response['tag'] == 'error':
            exit()

    console(response)


def active_sleep(process, sleep_time):
    sleep_time = sleep_time // 1 + 1
    for _ in range(sleep_time):
        if process.queue == 1 and process.status != 'dead':
            sleep(1)
        else:
            return 'get out of line'
    return 'done'


def queue_up(process):
    while True:
        waiting_time = process_permission(get_permission(process))
        if waiting_time is not None:
            if process.queue != 1:
                sleep(waiting_time)
            else:
                response = active_sleep(process, waiting_time)
                if response == 'get out of line':
                    print('GET OUT OF LINE')
                    process.driver.occupation = 'unemployed'
        else:
            break
