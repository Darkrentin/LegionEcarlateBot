import time

SEED_TIME = 1757856287#1757790000-311
CLOSE_PHASE_TIME = 7200  #2h
OPEN_PHASE_TIME = 3600   #1h
RESET_PHASE_TIME = 300   #5min

CYCLE_TIME = CLOSE_PHASE_TIME + OPEN_PHASE_TIME + RESET_PHASE_TIME


CLOSE_PHASE_START = 0
CLOSE_PHASE_END = CLOSE_PHASE_TIME

OPEN_PHASE_START = CLOSE_PHASE_END
OPEN_PHASE_END = CLOSE_PHASE_TIME + OPEN_PHASE_TIME

RESET_PHASE_START = OPEN_PHASE_END
RESET_PHASE_END = CYCLE_TIME

GREEN_LIGHT = "🟢"
OFF_LIGHT = "⚫"
RED_LIGHT = "🔴"
NUMBER_OF_LIGHT = 5


def get_time_in_cycle():
    actual_time = int(time.time())

    time_since_seed_time = actual_time - SEED_TIME

    time_in_cycle = time_since_seed_time % CYCLE_TIME

    return time_in_cycle

def get_hangar_phase(time_in_cycle=-1):
    if time_in_cycle==-1 : time_in_cycle = get_time_in_cycle()

    if(time_in_cycle<CLOSE_PHASE_END):
        return 'CLOSE'
    elif(time_in_cycle<OPEN_PHASE_END):
        return 'OPEN'
    elif(time_in_cycle<RESET_PHASE_END):
        return 'RESET'


def get_time_until_next_phase(time_in_cycle=-1,hangar_phase=""):
    if time_in_cycle==-1 : time_in_cycle = get_time_in_cycle()
    if hangar_phase=="" : hangar_phase = get_hangar_phase(time_in_cycle)

    if hangar_phase=='CLOSE':
        return CLOSE_PHASE_END - time_in_cycle
    elif hangar_phase=='OPEN':
        return OPEN_PHASE_END - time_in_cycle
    elif hangar_phase=='RESET':
        return RESET_PHASE_END - time_in_cycle

def get_time_in_phase(time_in_cycle=-1,hangar_phase=""):
    if time_in_cycle==-1 : time_in_cycle = get_time_in_cycle()
    if hangar_phase=="" : hangar_phase = get_hangar_phase(time_in_cycle)

    if hangar_phase=='CLOSE':
        return time_in_cycle - CLOSE_PHASE_START
    elif hangar_phase=='OPEN':
        return time_in_cycle - OPEN_PHASE_START
    elif hangar_phase=='RESET':
        return time_in_cycle - RESET_PHASE_START
    
def get_time_of_phase(hangar_phase):
    if hangar_phase=='CLOSE':
        return CLOSE_PHASE_TIME
    elif hangar_phase=='OPEN':
        return OPEN_PHASE_TIME
    elif hangar_phase=='RESET':
        return RESET_PHASE_TIME

def get_time_until_end(time_in_cycle=-1):
    if time_in_cycle==-1 : time_in_cycle = get_time_in_cycle()

    return CYCLE_TIME-time_in_cycle

def get_light_status(time_in_cycle=-1,hangar_phase=""):
    if time_in_cycle==-1 : time_in_cycle = get_time_in_cycle()
    if hangar_phase=="" : hangar_phase = get_hangar_phase(time_in_cycle)

    time_in_phase = get_time_in_phase(time_in_cycle,hangar_phase)
    time_of_phase = get_time_of_phase(hangar_phase)

    time_per_light = time_of_phase / NUMBER_OF_LIGHT
    lights_count = int(time_in_phase / time_per_light)
    lights_count = min(lights_count, NUMBER_OF_LIGHT)

    lights = [OFF_LIGHT] * NUMBER_OF_LIGHT

    if hangar_phase == 'CLOSE':        
        for i in range(lights_count):
            lights[i] = GREEN_LIGHT
        for i in range(lights_count, NUMBER_OF_LIGHT):
            lights[i] = RED_LIGHT
    
    elif hangar_phase == 'OPEN':
        for i in range(lights_count):
            lights[i] = OFF_LIGHT
        for i in range(lights_count, 5):
            lights[i] = GREEN_LIGHT
    
    elif hangar_phase == 'RESET':
        pass

    return "  ".join(lights)


def load_time_seed(data):
    global SEED_TIME
    if data and 'time_seed' in data:
        SEED_TIME = data['time_seed']
        print(f"New time seed : {SEED_TIME}")
    else:
        print("Warning: time_seed not found or invalid in data. Using default.")