import OpenOPC


def start():
    return OpenOPC.client()


def servers(opc):
    return opc.servers()


# def is_connected():
#     return True

def connect(opc, server):
    try:
        opc.connect(server)
        info = dict(opc.info())
        if info['OPC Server'] == server:
            connected = True
        else:
            connected = False
    except Exception:
        connected = False
    return connected


def tags(opc):
    return opc.list(recursive=True)


def read(opc, tags):
    results = opc.read(tags)
    return csv_line(results)


def demux_results(results):
    tags = [tag for tag, value, status, time in results]
    values = [value for tag, value, status, time in results]
    statuses = [status for tag, value, status, time in results]
    times = [time for tag, value, status, time in results]
    return tags, values, statuses, times


def csv_line(results,
             sep=';',
             halt_if_bad=False,
             bad_value='',
             halt_if_not_sync=True,
             include_timestamp=True,
             timestamp_col_name='Timestamp'):
    tags, values, statuses, times = demux_results(results)
    sync = all(times[0] == time for time in times)
    if not sync:
        pass
    all_good = all(status == 'Good' for status in statuses)
    if not all_good:
        pass
    tags_line = sep.join(['Timestamp'] + tags)
    values_line = sep.join([times[0]] + [str(value) for value in values])
    return tags_line, values_line
