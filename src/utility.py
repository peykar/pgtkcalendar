#!/usr/bin/env python


import math

monthDays=[31, 31, 31, 31, 31, 31, 30, 30, 30, 30, 30, 29]
monthdays=[31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

days_in_year = [365,366]

#dervied from http://farsitools.sf.net
g_days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
j_days_in_month = [31, 31, 31, 31, 31, 31, 30, 30, 30, 30, 30, 29]


class GregorianToJalali:

    def __init__(self,gyear,gmonth,gday):
        """
            Convert gregorian date to jalali date
            gmonth: number of month in range 1-12
        """
        self.gyear=gyear
        self.gmonth=gmonth
        self.gday=gday
        self.__gregorianToJalali()

    def getJalaliList(self):
        return (self.jyear,self.jmonth,self.jday)

    def __gregorianToJalali(self):
        """
            g_y: gregorian year
            g_m: gregorian month
            g_d: gregorian day
        """
        global g_days_in_month,j_days_in_month

        gy = self.gyear-1600
        gm = self.gmonth-1
        gd = self.gday-1

        g_day_no = 365*gy+(gy+3)/4-(gy+99)/100+(gy+399)/400

        for i in range(gm):
            g_day_no += g_days_in_month[i]
        if gm>1 and ((gy%4==0 and gy%100!=0) or (gy%400==0)):
            # leap and after Feb
            g_day_no+=1
        g_day_no += gd

        j_day_no = g_day_no-79

        j_np = j_day_no / 12053
        j_day_no %= 12053
        jy = 979+33*j_np+4*int(j_day_no/1461)

        j_day_no %= 1461

        if j_day_no >= 366:
            jy += (j_day_no-1)/ 365
            j_day_no = (j_day_no-1)%365

        for i in range(11):
            if not j_day_no >= j_days_in_month[i]:
                i-=1
                break
            j_day_no -= j_days_in_month[i]

        jm = i+2
        jd = j_day_no+1


        self.jyear=jy
        self.jmonth=jm
        self.jday=jd



class JalaliToGregorian:
    def __init__(self,jyear,jmonth,jday):
        """
            Convert db time stamp (in gregorian date) to jalali date
        """
        self.jyear=jyear
        self.jmonth=jmonth
        self.jday=jday
        self.__jalaliToGregorian()

    def getGregorianList(self):
        return (self.gyear,self.gmonth,self.gday)


    def __jalaliToGregorian(self):
        global g_days_in_month,j_days_in_month
        jy = self.jyear-979
        jm = self.jmonth-1
        jd = self.jday-1


        j_day_no = 365*jy +int(jy/33)*8 + (jy%33+3)/4
        for i in range(jm):
            j_day_no += j_days_in_month[i]

        j_day_no += jd

        g_day_no = j_day_no+79

        gy = 1600 + 400*int(g_day_no/ 146097) # 146097 = 365*400 + 400/4 - 400/100 + 400/400
        g_day_no = g_day_no % 146097

        leap = 1
        if g_day_no >= 36525: # 36525 = 365*100 + 100/4
            g_day_no-=1
            gy += 100*int(g_day_no/ 36524) # 36524 = 365*100 + 100/4 - 100/100
            g_day_no = g_day_no % 36524

            if g_day_no >= 365:
                g_day_no+=1
            else:
                leap = 0


        gy += 4*int(g_day_no/1461) # 1461 = 365*4 + 4/4
        g_day_no %= 1461

        if g_day_no >= 366:
            leap = 0
            g_day_no-=1
            gy += g_day_no/365
            g_day_no = g_day_no % 365

        i=0
        while g_day_no >= g_days_in_month[i] + (i == 1 and leap):
            g_day_no -= g_days_in_month[i] + (i == 1 and leap)
            i+=1
        self.gmonth = i+1
        self.gday = g_day_no+1
        self.gyear = gy




class cal:
    def __init__(self):
        self.year =0
        self.month=0
        self.day =0
        self.weekOfYear =0
        self.weekOfMonth =0
        self.dayOfYear =0
        self.dayOfWeek =0 # shanbe 0,yekshanbe 1, ... , jome 6
        self.era =0


def leap(year):
    pr = year
    pr-=475 ;
    if (pr < 0):
        pr -=1
 
    pr%=2820
    if (pr >= 2783):
        pr-=2783
        if (pr == 0):
            return 0
        elif ((pr % 4) == 0):
            return 1
        else: 
            return 0
    else:
        pr%=128
        if (pr<29):
            if (pr == 0):
                return 0
            elif (pr % 4 == 0):
                return 1
            else:
                return 0
        elif (pr < 62):
            pr-=29
            if (pr == 0):
                return 0
            elif (pr % 4 == 0):
                return 1
            else:
                return 0
        elif (pr < 95):
            pr-=62
            if (pr == 0):
                return 0
            elif (pr % 4 == 0):
                return 1
            else:
                return 0
        else:
            pr-=95
            if (pr == 0):
                return 0
            elif (pr % 4 == 0):
                return 1
            else:
                return 0
            
def scalar_Days (year,month,day): 
    daysNo=long(0)

    year = year -475+2820
    month -= 1

    daysNo=(year/2820)*1029983
    year=year % 2820

    daysNo+=(year/128)* 46751
    if((year/128)>21):
        daysNo-=46751
        year=(year%128)+128
    else:
        year=year%128

    if(year>=29):
        year-=29
        daysNo+=10592

    if(year>=66):
        year-=66
        daysNo+=24106
    elif( year>=33):
        daysNo+=(year/33)* 12053
        year=year%33

    if (year >= 5):
        daysNo += 1826
        year -=5
    elif (year == 4):
        daysNo += 1460
        year -=4

    daysNo += 1461 * (year/4)
    year %= 4
    daysNo += 365 * year
    i=0
    while(i < month):
        daysNo += monthDays[i]
        i+=1

    daysNo += day

    return daysNo-856493

def jalalyDate (daysNo):
    h=cal()
    month=0
    day=0
    scalarDays=0
    yearOffset=0
    monthOffset=0
    
    daysNo+=856493;
    scalarDays=daysNo
    year=(daysNo/1029983)*2820
    daysNo=daysNo%1029983

    if((daysNo/46751)<=21):
        year+=(daysNo/46751)* 128
        daysNo=daysNo%46751
    else:
        year+=(daysNo/46751)* 128
        daysNo=daysNo%46751
        year-=128
        daysNo+=46751

	if (daysNo >= 10592):
		year+= 29
		daysNo -= 10592

	if(daysNo>=24106):
		daysNo-=24106
		year+=66

	if(daysNo>=12053):
		daysNo-=12053
		year+=33


	if (daysNo >= 1826):
		year+= 5
		daysNo -= 1826
	elif (daysNo > 1095):
		year+= 3
		daysNo -= 1095

	year +=(4 * (daysNo/1461))
	daysNo %= 1461

	if (daysNo == 0):
		year -= 1
		daysNo = 366
	else:
		year += daysNo/365
		daysNo = daysNo % 365
		if (daysNo == 0):
			year -= 1
			daysNo = 365

	h.dayOfYear=daysNo
	yearOffset=(scalarDays-h.dayOfYear+4)%7
	h.weekOfYear=(h.dayOfYear+yearOffset-1)/7+1
    
    i=0
    while((i < 11)and(daysNo > monthDays[i])):
        daysNo -= monthDays[i]
        i+=1

	month = i + 1
	day = daysNo
	h.day = day

	monthOffset=(scalarDays-h.day+4)%7

	h.weekOfMonth=(h.day+monthOffset-1)/7+1
	h.month = month
	h.year = year-2345

	if (h.year<0):
		h.era=0
	else:
		h.era=1
    h.dayOfWeek=(scalarDays+3)%7
    return h.dayOfWeek

BASE_CAL_DAY=11
BASE_CAL_MONTH=10
BASE_CAL_YEAR=1348
DAY_LEN=86400
YEAR_LEN=31557600
SEGMENT_REDIRECTION=0.70
YEAR_LEND=365.24220

def convert_to_jalali(fu_days):
    fu_days += (210 * 60)
    fu_days = (int(fu_days) / DAY_LEN)
    n_days=fu_days
    n_days%= 7
    n_days+= 5
    if (n_days == -1):
        n_days = 6
    wday = abs(n_days % 7)
    
    fn_days = fu_days + 287

    n_years = long(fu_days / YEAR_LEND)
    year = n_years + BASE_CAL_YEAR

    redirect = ((n_years * YEAR_LEND) - math.floor(n_years * YEAR_LEND))
    
    if (redirect <= SEGMENT_REDIRECTION):
        today = math.ceil(fn_days - (n_years * YEAR_LEND))
    elif ((redirect > SEGMENT_REDIRECTION) and (redirect < 0.88)):
        today = (fn_days - (n_years * YEAR_LEND)) + 1
    else:
        today = math.floor(fn_days - (n_years * YEAR_LEND))

    if ((fu_days<0) and (today<=0)):
        if (today == 0):
            today = days_in_year[leap(year-1)] #(!leap((year)-1)) ? 365:366
        else:
            today+= days_in_year[leap(year-1)] #(!is_jleap((*year)-1)) ? 365:366
            year-=1
    
    if (today == 366):
        if not(leap(year)):
            today -= 365
            year +=1
    elif (today > 366):
        if (leap(year)):
            today -= 366
        else:
            today -= 365
        year +=1

    r_days = int(today)

    mon=0
    i = 1
    while(i<=11):
        if (r_days < monthDays[i-1]+1):
            month = i
            day = r_days
            return year,month,day
        r_days-=monthDays[i-1]
        i+=1
    
    month = 12
    day = r_days
    return year,month,day

def jalali_to_milady (year,month,day):
    gy= gm= gd = 0
    g_day_no = j_day_no =long()
    leap=0

    jy = year-979;
    jm = month-1;
    jd = day-1;

    j_day_no = 365*jy + (jy/33)*8 + (jy%33+3)/4
    i = 0
    while (i<jm):
        j_day_no += monthDays[i]
        i +=1

    j_day_no += jd
    g_day_no = j_day_no+79

    gy = 1600 + 400*(g_day_no/146097) 
    g_day_no = g_day_no % 146097

    leap = 1
    if (g_day_no >= 36525):
        g_day_no -=1
        gy += 100*(g_day_no/36524)
        g_day_no = g_day_no % 36524
      
        if (g_day_no >= 365):
            g_day_no +=1
        else:
            leap = 0

    gy += 4*(g_day_no/1461)
    g_day_no %= 1461

    if (g_day_no >= 366):
        leap = 0

        g_day_no -=1
        gy += g_day_no/365
        g_day_no = g_day_no % 365

    i=0
    while (g_day_no >= monthdays[i] + (i == 1 and leap)):
        g_day_no -= monthdays[i] + (i == 1 and leap)
        i+=1
    gm = i+1
    gd = g_day_no+1

    return gy,gm,gd

