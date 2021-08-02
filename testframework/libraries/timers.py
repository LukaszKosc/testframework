

def get_time_delta(stop, start):
    days, hours, minutes, seconds = None, None, None, None
    difference = stop - start
    seconds_in_day = 24 * 60 * 60
    minutes, seconds = divmod(difference.days * seconds_in_day + difference.seconds, 60)
    days, minutes = divmod(minutes, 24 * 60)
    if minutes > 60:
        hours, minutes = divmod(minutes, 60)
        if minutes > 60:
            minutes, seconds = divmod(minutes, 60)
    days = days if days else 0
    hours = hours if hours else 0
    minutes = minutes if minutes else 0
    seconds = seconds if seconds else 0

    def get_time_string(value, ending):
        ret_string = '0{}'.format(value) if value < 10 else '{}'.format(value)
        ret = ret_string + ':' if ending != 's' else ret_string
        return ret

    out = get_time_string(days, 'd') + get_time_string(hours, 'h') + get_time_string(minutes, 'm') + get_time_string(seconds, 's')
    while out.startswith('00:'):
        out = out.replace('00:', '')
    return out
