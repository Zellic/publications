import time
from tqdm import tqdm
from datetime import datetime
from multiprocessing import Pool

SECONDS_PER_DAY = 24 * 60 * 60
def bokkyPooBah_timestampToDate(secs):
    _days = secs // SECONDS_PER_DAY
    OFFSET19700101 = 2440588;
    __days = _days;

    L = __days + 68569 + OFFSET19700101;
    N = (4 * L) // 146097;
    L = L - (146097 * N + 3) // 4;
    _year = (4000 * (L + 1)) // 1461001;
    L = L - (1461 * _year) // 4 + 31;
    _month = (80 * L) // 2447;
    _day = L - (2447 * _month) // 80;
    L = _month // 11;
    _month = _month + 2 - 12 * L;
    _year = 100 * (N - 49) + _year + L;

    year = _year;
    month = _month;
    day = _day;
    return (year,month,day)

JOB_SIZE = 10000

def verify(start_t):
    for t in range(start_t, start_t+JOB_SIZE):
        dt = datetime.utcfromtimestamp(t)
        y,m,d = bokkyPooBah_timestampToDate(t)
        # print(t,y,m,d,dt)
        assert(y == dt.year)
        assert(m == dt.month)
        assert(d == dt.day)

now = int(time.time())
test_range = SECONDS_PER_DAY*365*30

with Pool() as p:
    work = range(now-test_range,now+test_range,JOB_SIZE)
    for _ in tqdm(p.imap_unordered(verify, work), total=len(work)):
        pass

print("Everything OK")
