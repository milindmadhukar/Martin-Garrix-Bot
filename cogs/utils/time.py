import datetime

def parse_time(duration):
    timings = duration.split(' ')
    delta = datetime.timedelta(seconds=0)
    time_dict = {'y' : 365*24*60*60, 'm' : 30*24*60*60 ,'w':  7*24*60*60,'d' : 24*60*60 ,'h' : 60*60, 'm': 60, 's' : 1}
    for timing in timings:
        param = timing[-1]
        value = None
        try:
            value = int(timing[:-1])
        except:
            return None

        delta += datetime.timedelta(seconds=value*time_dict.get(param))

    return delta