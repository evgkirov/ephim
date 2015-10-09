from datetime import datetime
import string


def to_base(num, b, numerals=string.digits + string.ascii_lowercase):
    return ((num == 0) and numerals[0]) or (to_base(num // b, b, numerals).lstrip(numerals[0]) + numerals[num % b])


def datetime_to_string(dt: datetime):
    delta = dt - datetime.fromtimestamp(0)

    ### 0
    # return dt.strftime('%Y-%m-%d %H.%M.%S.')

    ### 1
    # ts = int(dt.timestamp())
    # return '{sign}{ts}'.format(
    #     sign='N' if ts < 0 else 'P',
    #     ts=abs(ts),
    # )

    ### 2
    return '{sign}{days}_{seconds}'.format(
        sign='0' if delta.days < 0 else '',
        days=to_base(abs(delta.days), 36, string.digits + string.ascii_uppercase),
        seconds=str(delta.seconds).zfill(5),
    )

    # return '{sign}{days}_{seconds}'.format(
    #     sign='n' if delta.days < 0 else 'p',
    #     days=to_base(abs(delta.days), 36),
    #     seconds=str(delta.seconds).zfill(5),
    # )
    # return str(dt.strftime('%Y%m%d')) + '_' + str(delta.seconds).zfill(5)
    # return str(int(dt.timestamp()))
    # return to_base(int(dt.timestamp()), 36)
    # return '{days}_{seconds}'.format(
    #     days=to_base(abs(delta.days), 26, string.ascii_uppercase),
    #     seconds=str(delta.seconds).zfill(5),
    # )
    # print(delta.seconds)
    # return '{days}{seconds}'.format(
    #     days=to_base(abs(delta.days), 26, string.ascii_uppercase),
    #     # hours=to_base(delta.seconds // 3600, 26, string.ascii_uppercase),
    #     seconds=str(delta.seconds).zfill(5),
    #     # seconds=dt.strftime('%H%M'),
    # )
    # return to_base(int(dt.timestamp()), 26, string.ascii_lowercase)
