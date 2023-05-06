from dataclasses import dataclass

@dataclass
class Event:
    """Class for keeping track of an interaction event."""
    name: str # event type i.e mouse_press
    time: float
    fname: int = 0


def is_pause(prev_event, period_len_s):
    # if the previous event is mouse_release
    if prev_event.name == 'mouse_release':
        # and the duration is over 20 seconds
        if period_len_s > 20:
            # then don't include the interaction - we consider this a pause in annotation
            return True
    return False



def get_annot_duration_s(events, fname):
    # we consider interaction as mouseup and mouse down events
    fname_events = [e for e in events if e.fname == fname and e.name in [
                    'mouse_press', 'mouse_release']]
    if len(fname_events) < 2: # must have both mouse_press and mouse_release
        return 0

    assert len(fname_events) >= 2, f'at least two fname_events are required, fname_events={fname_events}'
    # fname_events are already filtered by filename
    total_duration = 0
    most_recent_event = fname_events[0]
    for e in fname_events[1:]:
        assert e.name != most_recent_event.name
        period_between_events = e.time - most_recent_event.time
        if not is_pause(most_recent_event, period_between_events):
            total_duration += period_between_events
        most_recent_event = e
    return total_duration




def events_from_client_log(client_log_fpath):
    lines = open(client_log_fpath).readlines()
    events = []
    for l in lines:
        parts = l.strip().split(',')
        event_time = parts[1]
        event_name = parts[2]
        fname = [p for p in parts if 'fname:' in p][0].replace('fname:', '')
        events.append(Event(name=event_name, fname=fname, time=float(event_time)))
    return events


def interaction_time_per_fname_s(client_log_fpath):
    """ estimate interaction time for each file based
        on the timing of mouse_press and mouse_release events
        logged whilst the user was interacting with each file 

        Example usage:
        interaction_times = interaction_time_per_fname_s(client_log_fpath='logs/client.csv')
     """
    events = events_from_client_log(client_log_fpath)     
    unique_fnames = list(set(e.fname for e in events))
    fname_times = {}
    for fname in unique_fnames:
        fname_times[fname] = get_annot_duration_s(events, fname)
    return fname_times
