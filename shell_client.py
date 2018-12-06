from datetime import datetime, timedelta
from mysql import connector
from time import sleep

# 1 & 2 are continous data inputs, must monitor hearbeat
monitors = ['1', '2']
controller = '3'
arduino_sources = {'1': ['distance', 'movement'],
                   '2': ['distance', 'piezo'],
                   '3': ['keypad']}
source_tresholds = {'distance': 20,
                    'movement': 180,
                    'piezo': 0.02}
db_user = 'arduino'
db_pass = 'password'
db_name = 'iotsec'

# string to lookup last data row of device
query_latest_metric = "select * from metrics " + \
                      "where (name=%s and source=%s) " + \
                      "order by id desc limit 1;"
query_latest_metrics = "select * from metrics " + \
                      "where name=%s " + \
                      "order by id desc limit 10;"
query_latest_alarm = "select * from metrics " + \
                     "where (name=%s and source='keypad') " + \
                     "order by id desc limit 1;"

# Keypad logs failed attempts and alarm state
ALARM_INCORRECT = 2
ALARM_ON = 1
ALARM_OFF = 0

try:
    cnx = connector.connect(user=db_user, password=db_pass,
                            host='127.0.0.1', database=db_name)
    cnx.autocommit = True  # Otherwise queries won't update
except connector.Error as err:
    if err.errno == connector.errorcode.ER_ACCESS_DENIED_ERROR:
        print('Wrong DB username or password!')
    elif err.errno == connector.errorcode.ER_BAD_DB_ERROR:
        print('Database does not exist!')
    else:
        print(err)
    exit(1)


def set_alarm(state):
    add_metric = "INSERT INTO metrics " + \
                 "(name, source, value, datetime) " + \
                 "VALUES (%s, %s, %s, %s)"
    if state:
        value = ALARM_ON
    else:
        value = ALARM_OFF
    data = ('3', "keypad", value, datetime.now())
    cursor = cnx.cursor()
    cursor.execute(add_metric, data)
    cnx.commit()
    cursor.close()


def heartbeat_source(name, source):
    # Returns false if metric has not been updated recently
    cursor = cnx.cursor()

    data = (name, source)
    cursor.execute(query_latest_metric, data)

    # query ensures at most one entry in cursor
    for (row, name, source, value, time) in cursor:
        # TODO if data collection is more than 30 then change
        if time + timedelta(seconds=30) >= datetime.now():
            return True
    return False

    cursor.close()


def evaluate_source(name, source):
    # Returns false if metric is over specified threshold
    cursor = cnx.cursor()

    data = (name, source)
    cursor.execute(query_latest_metric, data)

    # query ensures at most one entry in cursor
    for (row, name, source, value, time) in cursor:
        # TODO if data collection is more than 30 then change
        if value < source_tresholds[source]:
            return True
    return False

    cursor.close()


def monitor_states():
    # Returns a list of (device, metric) that have not been updated recently
    failures = []
    for monitor in monitors:
        for source in arduino_sources[monitor]:
            if not (heartbeat_source(monitor, source) and evaluate_source(monitor, source)):
                failures.append((monitor, source))
    return failures


def alarm_state():
    # Returns false if last entry disabled the alarm
    cursor = cnx.cursor()

    data = (controller, )
    cursor.execute(query_latest_alarm, data)

    # query ensures at most one entry in cursor
    for (row, name, source, value, time) in cursor:
        if value == ALARM_OFF:
            return False
    return True

    cursor.close()


def latests(name):
    cursor = cnx.cursor()

    data = (name,)
    cursor.execute(query_latest_metrics, data)

    result = []
    # query ensures at most one entry in cursor
    for (row, name, source, value, time) in cursor:
        # TODO if data collection is more than 30 then change
        result.append((name, source, value, time))

    cursor.close()
    return result


def main():
    try:
        while True:
            failures = monitor_states()
            # print(failures)
            alarm = alarm_state()
            # print(alarm)
            if alarm:
                print(failures)
            else:
                print([])
            sleep(0.5)
    except KeyboardInterrupt:
        print('Exiting!')


if __name__ == '__main__':
    main()
    cnx.close()
