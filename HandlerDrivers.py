import random
import threading
from instagrapi import Client
import pdb
from time import sleep
from pprint import pprint

from ConsoleOutput import console
from InnerFuncs import form_line
from ConfigGet import relogin_delay
from ProfilesInstagram import get_account, get_accounts
from ConfigGet import authorization_delay, last_performers, driver_strength
from Kunteynir import DriversKunteynir

Drivers = DriversKunteynir()
Broken_Drivers = DriversKunteynir()
Dead_Drivers = DriversKunteynir()


class Driver:
    def __init__(self, name, driver):
        self.name = name
        self.driver = driver
        self.status = 'enable'
        self.occupation = 'unemployed'

    def employ(self, process_id):
        self.occupation = process_id

    def dismiss(self):
        global Drivers
        queue_len = last_performers() - Dead_Drivers.len
        enable_len = len(Drivers.enable())
        if queue_len >= enable_len:
            queue_len = enable_len - 1

        if queue_len <= 0:
            for driver in Drivers.content:
                driver.occupation = 'unemployed'

        drivers = sorted([driver for driver in Drivers.content if type(driver.occupation) == int],
                         key=lambda x: -x)

        if len(drivers) > queue_len:
            emp = drivers[:queue_len]
            unemp = [x for x in drivers if x not in emp]
        else:
            emp = []
            unemp = drivers

        for driver in unemp:
            driver.occupation = 'unemployed'

        k = -1
        for l in range(len(emp)):
            emp[l].occupation = k
            k -= 1


def wait_for_available_drivers(process_id):
    global Drivers
    i = 0
    minutes = 0
    while not Drivers.available():

        if minutes == 0 and i == 0:
            console(f'[GET DRIVER] Exception: No available drivers for process {process_id}',
                    level='exception')

        if i == 600:
            if minutes == 1:
                console(f'[GET DRIVER] Exception: No available drivers for process {process_id}. '
                        f'{minutes} minute has passed', level='exception')
            else:
                console(f'[GET DRIVER] Exception: No available drivers for process {process_id}. '
                        f'{minutes} minutes have passed', level='exception')
            Drivers.show()
            minutes += 1
            i = 0
        sleep(0.1)
        i += 1


def assign_driver(available_drivers, process):
    driver = random.choice(available_drivers)

    driver.employ(process.id)
    console(f'Drivers was updated by process {process.id}', level='global', end='\n\n')
    Drivers.show()
    console('Process {} ({}) is assigned driver "{}"'.format(process.id, process.info, driver.name),
            level='good', end='\n\n')

    return driver


def get_driver(process):
    console(f'Start assigning a driver to a process {process.id} ({process.info})', level='handler')

    if Drivers.enable():
        if Drivers.available():
            return assign_driver(Drivers.available(), process)
        else:
            wait_for_available_drivers(process.id)
            return assign_driver(Drivers.available(), process)
    else:
        i = 0
        seconds = 0
        while not Drivers.enable():
            if i == 100:
                if seconds == 0:
                    console(f'[GET DRIVER] Error: No enable drivers', level='error')
                else:
                    console(f'[GET DRIVER] Error: No enable drivers. {seconds} seconds have passed', level='error')
                seconds += 10
                i = 0
            sleep(0.1)
            i += 1

        if Drivers.available():
            return assign_driver(Drivers.available(), process)
        else:
            wait_for_available_drivers(process.id)
            return assign_driver(Drivers.available(), process)


def relogin_target(driver, mode):
    profile = get_account(driver.name)
    if profile is None:
        console(f'[RELOGIN DRIVER] Error: Failed to get driver "{driver.name}" information', level='error')
        exit()

    delay = relogin_delay()
    console(f'Relogin delay for "{profile.name}" is {delay} seconds', level='norm', end='\n\n')
    sleep(delay)
    console(f'Relogin delay is over, relogin "{profile.name}" starts', level='handler', end='\n\n')
    new_driver = login_to_instagram(profile, mode=mode)
    if new_driver is not None:
        Drivers.append(new_driver)
        Broken_Drivers.remove(driver)
        drivers_line = ', '.join([driver.name for driver in Drivers.content])
        console('[RELOGIN DRIVER] drivers was updated. Drivers ({}): {}'.format(Drivers.len, drivers_line),
                level='global', end='\n\n')
    else:
        driver.status = 'dead'
        Broken_Drivers.remove(driver)
        Dead_Drivers.append(driver)
        console(f'[RELOGIN DRIVER] Failed : "{profile.name}"', level='error')
        console('Dead Drivers: ' + ', '.join([driver.name for driver in Dead_Drivers.content]), end='\n\n')


def relogin_driver(driver, mode='test'):
    global Drivers, Broken_Drivers
    try:
        driver.status = 'broken'
        Drivers.remove(driver)
        Broken_Drivers.append(driver)
        console('Broken Drivers:' + ', '.join([driver.name for driver in Broken_Drivers.content]), end='\n\n')
        driver.dismiss()
        drivers_line = ', '.join([driver.name for driver in Drivers.content])
        console('Drivers was updated. Drivers ({}): {}'.format(Drivers.len, drivers_line), level='global')
    except Exception as ex:
        console(ex)
        console('[RELOGIN DRIVER] Error: Removing driver "{}" from drivers failed'.format(driver.name), level='error')
        Drivers.show()
        relogin_driver(driver, mode=mode)
        exit()

    console(f'[RELOGIN DRIVER] Driver "{driver.name}" needs to relogin', level='norm')

    threading.Thread(target=relogin_target, args=(driver, mode)).start()


# Authorization Part

LAST_AUTH_DELAY_ERROR = 0


def authorize(mode='test'):
    global Drivers
    Drivers.append(initial_auth(mode=mode.lower()), unpack=True)
    Drivers.show()


def initial_auth(mode='test'):
    allowed_profiles = get_accounts(mode='allowed')

    console('Allowed Accounts ({}): {}'.format(len(allowed_profiles),
                                               form_line([profile.name for profile in allowed_profiles])))

    drivers = []
    delay = authorization_delay()
    num = len(allowed_profiles)
    i = 1
    for profile in allowed_profiles:
        driver = login_to_instagram(profile, done=f'{i}/{num}', mode=mode)
        if driver is not None:
            drivers.append(driver)
        if profile != allowed_profiles[-1]:
            sleep(delay)
            sleep(process_auth_delay_error(delay // 2))
        i += 1
    console('')

    return drivers


def login_to_instagram(profile, done='', mode='test'):
    driver = Client()

    if mode == 'real':
        console(f'[LOGIN TO INSTAGRAM] REAL LOGIN: "{profile.name}"')
        try:
            driver.login(profile.email, profile.password)
        except Exception as ex:
            console(ex)
            console(f'[LOGIN TO INSTAGRAM] Failed to login: "{profile.name}"', level='error')
            Broken_Drivers.append(profile.name)
            console('Broken Drivers: {}'.format(' ,'.join(Broken_Drivers.content)))
            return None

    # if mode == 'test':
    #     try:
    #         if done == '':
    #             driver_strength_test(strength=20)
    #     except Exception as ex:
    #         console(f'[LOGIN TO INSTAGRAM] Failed to login: "{profile.name}"', level='error')
    #         return None

    console('[Authorize] {} Account "{}" logged in'.format(done, profile.name), level='good')

    return Driver(profile.name, driver)


def process_auth_delay_error(main_error):
    global LAST_AUTH_DELAY_ERROR
    while True:
        dice = random.randint(0, 100)
        add_delay = main_error * dice // 100
        if 2 * abs(add_delay - LAST_AUTH_DELAY_ERROR) > main_error:
            break
    LAST_AUTH_DELAY_ERROR = add_delay
    console(f'ADD_AUTH_DELAY: {add_delay}', )
    return add_delay


def driver_strength_test(strength=None):
    if strength is None:
        strength = driver_strength()
    dice = random.randint(0, 99)
    if dice > strength:
        console('[Driver Strength Test] Driver is BROKEN', level='error')
        raise Exception('[Driver Strength Test] Error')
        # return True
    else:
        console('[Driver Strength Test] Driver is OK', level='good')
