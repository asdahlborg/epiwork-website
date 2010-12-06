from datetime import datetime, timedelta

def epoch():
    """Use the Unix epoch for a date so far in the past at which no
    participation could have taken place. A participition with this date stamp
    indicates that there was no such participation.
    """
    return datetime(1970, 1, 1)

seconds_in_a_day = 24 * 60 * 60

def epochal_to_timedate(j):
  return timedelta(j/seconds_in_a_day/1000) + epoch()

def timedate_to_epochal(td):
  delta = td - epoch()
  return 1000 * (delta.days * seconds_in_a_day + delta.seconds)

