from z3 import *

LEAPOCH = (946684800 + 86400*(31+29))

DAYS_PER_400Y = (365*400 + 97)
DAYS_PER_100Y = (365*100 + 24)
DAYS_PER_4Y   = (365*4   + 1)

# set_param(proof=True)
s = Solver(logFile="verify.smt2")

def __secs_to_tm(t):
    days_in_month = [31,30,31,30,31,31,30,31,30,31,31,29]
    cum_days_in_month = [31, 61, 92, 122, 153, 184, 214, 245, 275, 306, 337, 366]

    secs = t - LEAPOCH;
    days = secs / 86400;
    remsecs = secs % 86400;

    _remsecs = remsecs
    remsecs = Int(30004)
    s.add(remsecs == _remsecs)

    remsecs = If(remsecs < 0, remsecs + 86400, remsecs)
    days = If(remsecs < 0, days - 1, days)

    _remsecs = remsecs
    remsecs = Int(30005)
    s.add(remsecs == _remsecs)
    _days = days
    days = Int(30006)
    s.add(days == _days)

    qc_cycles = days / DAYS_PER_400Y;
    remdays = days % DAYS_PER_400Y;

    _remdays = remdays
    remdays = If(_remdays < 0, remdays + DAYS_PER_400Y, remdays)
    qc_cycles = If(_remdays < 0, qc_cycles - 1, qc_cycles)

    _remdays = remdays
    remdays = Int(10001)
    s.add(remdays == _remdays)
    _qc_cycles = qc_cycles
    qc_cycles = Int(30001)
    s.add(qc_cycles == _qc_cycles)

    c_cycles = remdays / DAYS_PER_100Y;
    c_cycles = If(c_cycles == 4, c_cycles - 1, c_cycles)
    remdays -= c_cycles * DAYS_PER_100Y;

    _remdays = remdays
    remdays = Int(10002)
    s.add(remdays == _remdays)
    _c_cycles = c_cycles
    c_cycles = Int(30002)
    s.add(c_cycles == _c_cycles)

    q_cycles = remdays / DAYS_PER_4Y;
    q_cycles = If(q_cycles == 25, q_cycles-1, q_cycles);
    remdays -= q_cycles * DAYS_PER_4Y;

    _remdays = remdays
    remdays = Int(10003)
    s.add(remdays == _remdays)
    _q_cycles = q_cycles
    q_cycles = Int(30003)
    s.add(q_cycles == _q_cycles)

    remyears = remdays / 365;
    remyears = If (remyears == 4, remyears-1,remyears);
    remdays -= remyears * 365;

    _remdays = remdays
    remdays = Int(10004)
    s.add(remdays == _remdays)

    years = remyears + 4*q_cycles + 100*c_cycles + 400*qc_cycles;

    # months = 0
    # for i in range(len(days_in_month)):
    #     _remdays = remdays
    #     remdays = If(days_in_month[i] <= _remdays, remdays - days_in_month[i], remdays)
    #     months = If(days_in_month[i] <= _remdays, months+1, months)

    _remdays = remdays
    months = 0
    for i in range(12):
        remdays = If(_remdays >= cum_days_in_month[i], _remdays-cum_days_in_month[i], remdays)
        months = If(_remdays >= cum_days_in_month[i], i+1, months)

        __remdays = remdays
        remdays = Int(20000+i)
        s.add(remdays == __remdays)

    year = years + 100
    mon = months + 2
    _mon = mon
    mon = If(_mon >= 12, mon-12, mon)
    year = If(_mon >= 12, year+1, year)
    mday = remdays + 1

    year += 1900
    mon += 1

    _year = year
    year = Int(40000)
    s.add(year == _year)
    _mon = mon
    mon = Int(40001)
    s.add(mon == _mon)
    _mday = mday
    mday = Int(40002)
    s.add(mday == _mday)

    return (year,mon,mday)

def other_algorithm(secs):
    SECONDS_PER_DAY = 24 * 60 * 60
    _days = secs / SECONDS_PER_DAY
    OFFSET19700101 = 2440588;
    __days = _days;

    L = __days + 68569 + OFFSET19700101;
    N = (4 * L) / 146097;
    L = L - (146097 * N + 3) / 4;
    _year = (4000 * (L + 1)) / 1461001;
    L = L - (1461 * _year) / 4 + 31;
    _month = (80 * L) / 2447;
    _day = L - (2447 * _month) / 80;
    L = _month / 11;
    _month = _month + 2 - 12 * L;
    _year = 100 * (N - 49) + _year + L;

    year = _year;
    month = _month;
    day = _day;

    _year = year
    year = Int(50000)
    s.add(year == _year)
    _month = month
    month = Int(50001)
    s.add(month == _month)
    _day = day
    day = Int(50002)
    s.add(day == _day)

    return (year,month,day)

# t = BitVec('t',32)
# t = BitVecVal(951520128, 32)
t = Int('t')
s.add(t >= 0)
s.add(t <= 200000000000)
# t = IntVal(951868799)

year,mon,mday = __secs_to_tm(t)
year1 = simplify(year)
mon1 = simplify(mon)
mday1 = simplify(mday)

# print(year1,mon1,mday1)
# exit()

year,mon,mday = other_algorithm(t)
year2 = simplify(year)
mon2 = simplify(mon)
mday2 = simplify(mday)

# print(year2,mon2,mday2)
# exit()

# s.add(And(year1 == 2000, mday1 == 5, mon == 1))
s.add(Or(mday1 != mday2, mon1 != mon2, year1 != year2))
print(s.check())
# unsat
# print(s.proof())
# m = s.model()
# print(m.eval(t))
