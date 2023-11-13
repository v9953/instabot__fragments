import threading
import random
from copy import copy
from time import sleep

from ConsoleOutput import console
from Signals import send_signal


Processes = []
Dead_Processes = []


class Process:
    def __init__(self, process_type):
        self.client_id = int
        self.target = str
        self.id = int

        self.type = process_type
        self.type_abr = ''.join([word[0] for word in self.type.split(' ')])
        self.info = self.type_abr
        if self.type == 'Save Stories':
            self.priority = 1
        elif self.type == 'Monitor Stories':
            self.priority = 2
            self.launch_number = 1
            self.database = None
        else:
            self.priority = 3

        self.state = 'waiting'
        self.queue = None

        self.driver = None
        self.waiting_time = int
        self.status = 'alive'

    def rqueue(self, place, signal=True):
        if place == 'top':
            place = 1

        elif place == 'bottom':
            place = len(Processes)

        new = None
        if self.queue is None:
            new = self
            for process in Processes:
                if process.queue in range(place, len(Processes) + 1):
                    process.queue += 1
        else:
            old_place = self.queue

            if place < old_place:
                for process in Processes:
                    if process.queue in range(place, old_place):
                        process.queue += 1

            elif place > old_place:
                for process in Processes:
                    if process.queue in range(old_place + 1, place + 1):
                        process.queue -= 1

        self.queue = place
        if signal is True:
            send_signal('process update', Processes)
        show_queue(new=new)

    def rstate(self, state):

        self.state = state

        msg_level = 'basic'
        if state == 'running':
            msg_level = 'good'
            self.rqueue('top')
            send_signal('reload last request')
        elif state == 'sleeping':
            self.rqueue('bottom')
        elif state == 'waiting':
            send_signal('process update', Processes)

        console(f'Process {self.id} ({self.info}) is {state}', level=msg_level)


def create_process(client_id, process_type, target):

    for process in Processes:
        if process.client_id == client_id and process.type == process_type and process.target == target:
            p_info = ''.join([word[0] for word in process_type.split(' ')]) + f' {target} for {client_id}'
            console(f'Process {p_info} already exists', level='exception', end='\n\n')
            return None

    p = Process(process_type)

    while True:
        process_id = random.randint(0, 999)
        if process_id not in [process.id for process in Processes]:
            break

    p.target = target
    p.client_id = client_id
    p.info = '{} {} for {}'.format(p.type_abr, p.target, p.client_id)

    p.id = process_id
    p.state = 'waiting'

    if process_type == 'Monitor Stories':
        queue = len(Processes) + 1
    elif process_type == 'Save Stories':
        queue = len([process for process in Processes if process.type == 'Save Stories']) + 1
    else:
        return

    p.rqueue(queue, signal=False)
    Processes.append(p)
    send_signal('process update', Processes)

    # queue = [process.id for process in sorted(Processes, key=lambda x: x.n)]
    console('Create Process {}:  {}'.format(p.id, p.info), level='handler')

    return p


def close_process(process):
    if process in Processes:
        process.status = 'dead'
        process.driver.dismiss()
        process.rstate('sleeping')
        Processes.remove(process)
        Dead_Processes.append(process)
        send_signal('process update', Processes)
        console('Close Process {}:  {}'.format(process.id, process.info), level='handler', end='\n\n')
    else:
        if process in Dead_Processes:
            error_message = f'[Delete Process] Error: process {process.id} ({process.info}) is already dead'
        else:
            if hasattr(process, 'id') and hasattr(process, 'info'):
                error_message = f'[Delete Process] Error: process {process.id} ({process.info}) does not exist'
            elif hasattr(process, 'info'):
                error_message = f'[Delete Process] Error: process {process.id} does not exist and it has no process.info'
            elif hasattr(process, 'id'):
                error_message = f'[Delete Process] Error: process "{process.info}" does not exist and it has no process.id'
            else:
                error_message = f'[Delete Process] Critical Error: process does not exist and it has no process.id or process.info'

        console(error_message, level='error')


def add_process(client_id, process_type, target, attrs):

    p = Process(process_type)

    p.target = target
    p.client_id = client_id
    p.info = '{} {} for {}'.format(p.type_abr, p.target, p.client_id)

    if 'process_id' in attrs:
        p.id = attrs['process_id']
    else:
        while True:
            process_id = random.randint(0, 999)
            if process_id not in [process.id for process in Processes]:
                break
        p.id = process_id

    if 'queue' in attrs:
        p.rqueue(attrs['queue'], signal=False)
    else:
        if process_type == 'Monitor Stories':
            queue = len(Processes) + 1
        elif process_type == 'Save Stories':
            queue = len([process for process in Processes if process.type == 'Save Stories']) + 1
        else:
            return
        p.rqueue(queue, signal=False)

    if process_type == 'Monitor Stories':
        if 'launch_number' in attrs:
            p.launch_number = attrs['launch_number']
        elif process_type == 'Monitor Stories' and 'database' not in attrs:
            p.launch_number = 1

        if 'database' in attrs:
            p.database = attrs['database']
        if p.database is not None and p.launch_number == 1:
            p.launch_number = 2

    Processes.append(p)
    send_signal('process update', Processes)

    console('Add Process: {}  --  {}'.format(p.id, p.info), level='handler')

    return p


def show_processes():
    pass


def show_queue(new=None):
    if new is None:
        queue = [process for process in sorted(Processes, key=lambda x: x.queue)]
    else:
        queue = [process for process in sorted(Processes + [new], key=lambda x: x.queue)]
    queue_line = 'Queue: '
    for process in queue:
        if process != queue[0]:
            queue_line += f'       {process.queue}. {process.info}, id: {process.id}\n'
        else:
            queue_line += f'{process.queue}. {process.info}, id: {process.id}\n'
    console(queue_line)


def get_processes():
    return Processes







# def check_process_updates():
#     global processes_ini_need_update
#     while True:
#         if processes_ini_need_update:
#             update_processes(Processes)
#             processes_ini_need_update = False
#         sleep(0.1)


# threading.Thread(target=check_process_updates).start()

