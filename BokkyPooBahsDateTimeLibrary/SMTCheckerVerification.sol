// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract SMTCheckerVerification
{
    function musl_libc_daysToDate(int t) public pure returns (uint,uint,uint)  {

        require (t >= 0);
        require (t < 100000000000000);

        int _days;
        int _secs;
        int remsecs;

        /* Reject time_t values whose year would overflow int */
        require (!(t < -2147483648 * 31622400 || t > 2147483647 * 31622400));

        int LEAPOCH = (946684800 + 86400*(31+29));
        _secs = t - LEAPOCH;
        _days = _secs / 86400;
        remsecs = _secs % 86400;
        if (remsecs < 0) {
            remsecs += 86400;
            _days--;
        }

        int remdays;
        int _years;
        {
            int qc_cycles;
            int DAYS_PER_400Y = (365*400 + 97);
            qc_cycles = _days / DAYS_PER_400Y;
            remdays = _days % DAYS_PER_400Y;
            if (remdays < 0) {
                remdays += DAYS_PER_400Y;
                qc_cycles--;
            }

            int c_cycles;
            int DAYS_PER_100Y = (365*100 + 24);
            c_cycles = remdays / DAYS_PER_100Y;
            if (c_cycles == 4) c_cycles--;
            remdays -= c_cycles * DAYS_PER_100Y;

            int q_cycles;
            int DAYS_PER_4Y   = (365*4   + 1);
            q_cycles = remdays / DAYS_PER_4Y;
            if (q_cycles == 25) q_cycles--;
            remdays -= q_cycles * DAYS_PER_4Y;

            int remyears;
            remyears = remdays / 365;
            if (remyears == 4) remyears--;
            remdays -= remyears * 365;
            _years = remyears + 4*q_cycles + 100*c_cycles + 400*qc_cycles;
        }


        uint months;
        // int[12] memory days_in_month = [int(31),30,31,30,31,31,30,31,30,31,31,29];
        // for (months=0; days_in_month[months] <= remdays; months++)
        //     remdays -= days_in_month[months];
        int[12] memory cum_days_in_month = [int(31), 61, 92, 122, 153, 184, 214, 245, 275, 306, 337, 366];
        if (remdays >= cum_days_in_month[11]) {
            remdays = remdays-cum_days_in_month[11];
            months = 12;
        } else if (remdays >= cum_days_in_month[10]) {
            remdays = remdays-cum_days_in_month[10];
            months = 11;
        } else if (remdays >= cum_days_in_month[9]) {
            remdays = remdays-cum_days_in_month[9];
            months = 10;
        } else if (remdays >= cum_days_in_month[8]) {
            remdays = remdays-cum_days_in_month[8];
            months = 9;
        } else if (remdays >= cum_days_in_month[7]) {
            remdays = remdays-cum_days_in_month[7];
            months = 8;
        } else if (remdays >= cum_days_in_month[6]) {
            remdays = remdays-cum_days_in_month[6];
            months = 7;
        } else if (remdays >= cum_days_in_month[5]) {
            remdays = remdays-cum_days_in_month[5];
            months = 6;
        } else if (remdays >= cum_days_in_month[4]) {
            remdays = remdays-cum_days_in_month[4];
            months = 5;
        } else if (remdays >= cum_days_in_month[3]) {
            remdays = remdays-cum_days_in_month[3];
            months = 4;
        } else if (remdays >= cum_days_in_month[2]) {
            remdays = remdays-cum_days_in_month[2];
            months = 3;
        } else if (remdays >= cum_days_in_month[1]) {
            remdays = remdays-cum_days_in_month[1];
            months = 2;
        } else if (remdays >= cum_days_in_month[0]) {
            remdays = remdays-cum_days_in_month[0];
            months = 1;
        }
        
        require (!(_years+100 > 2147483647 || _years+100 < -2147483648));

        int tm_year = _years + 100;
        int tm_mon = int(months) + 2;
        if (tm_mon >= 12) {
            tm_mon -=12;
            tm_year++;
        }
        int tm_mday = remdays + 1;

        tm_year += 1900;
        tm_mon += 1;

        return (uint(tm_year),uint(tm_mon),uint(tm_mday));
    }

    function bokkyPooBah_daysToDate(int t) public pure returns (uint,uint,uint) {
        require (t >= 0);
        require (t < 100000000000000);

        int SECONDS_PER_DAY = 24 * 60 * 60;

        int _days = t / SECONDS_PER_DAY;

        int OFFSET19700101 = 2440588;

        int __days = int(_days);

        int L = __days + 68569 + OFFSET19700101;
        int N = 4 * L / 146097;
        L = L - (146097 * N + 3) / 4;
        int _year = 4000 * (L + 1) / 1461001;
        L = L - 1461 * _year / 4 + 31;
        int _month = 80 * L / 2447;
        int _day = L - 2447 * _month / 80;
        L = _month / 11;
        _month = _month + 2 - 12 * L;
        _year = 100 * (N - 49) + _year + L;

        uint year = uint(_year);
        uint month = uint(_month);
        uint day = uint(_day);
        return (year, month, day);
    }

    function test(int t) public pure {
        require (t >= 0);
        require (t < 100000000000000);
        uint y1;
        uint m1;
        uint d1;
        (y1,m1,d1) = bokkyPooBah_daysToDate(t);
        uint y2;
        uint m2;
        uint d2;
        (y2,m2,d2) = shit(t);
        assert(y1 == y2);
        assert(m1 == m2);
        assert(d1 == d2);
    }
}
