#!/usr/bin/env python
# -*- coding: utf-8 -*-
##
#    
#    Copyright (C) 2009  Mahdieh Saeed
#
#    This program is free software; Used Mola Pahnadayan source code; 
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; 
#
#    This program is defines events and functions that GTK Calendar used;
#    So It's easy to use for users that familiar with GTK Calendar;
#    But some functions will be complete in future.
##

import pygtk
pygtk.require('2.0')

import gtk,gobject
from gtk import gdk
import pango
import cairo
import os
import utility
from string import strip, lower
import datetime
import time

import warnings

#os.environ['LANG']="fa_IR.UTF-8"

BORDER_WIDTH = 0
days_in_months=( [0,31, 62, 93, 124, 155, 186, 216, 246, 276, 306, 336, 365],
                 [0,31, 62, 93, 124, 155, 186, 216, 246, 276, 306, 336, 366])

month_length = ( [0,31, 31, 31, 31, 31, 31, 30, 30, 30, 30, 30, 29],
                 [0,31, 31, 31, 31, 31, 31, 30, 30, 30, 30, 30, 30])

#gtk.widget_set_default_direction(gtk.TEXT_DIR_RTL)


mon_name = ["فروردین","اردیبهشت","خرداد","تیر","مرداد","شهریور"
            ,"مهر","آبان","آذر","دی","بهمن","اسفند"]
milady_monname = ["January","February","March","April","May","June","July",
                  "August","September","October","November","December"]

class GtkWarning(Warning):
    def __init__(self,param):
        Warning.__init__(self,param)

class wmonth:
    def __init__(self):
        self.hbox=gtk.HBox()
        self.arrow_left2=gtk.Button()
        self.arrow_left2.set_relief(2)
        arrow_left1 = gtk.Arrow(gtk.ARROW_LEFT, gtk.SHADOW_NONE)
        self.arrow_left2.add(arrow_left1)
        self.hbox.pack_start(self.arrow_left2,0,0,0)
        self.monthname=gtk.Label(" <b></b> ")
        self.monthname.set_width_chars(8)
        self.monthname.set_alignment(0.5,0.5)
        self.monthname.set_use_markup(True)
        self.hbox.pack_start(self.monthname,0,0,0)
        self.arrow_right2=gtk.Button()
        self.arrow_right2.set_relief(2)
        arrow_right1 = gtk.Arrow(gtk.ARROW_RIGHT, gtk.SHADOW_NONE)
        self.arrow_right2.add(arrow_right1)

        self.hbox.pack_start(self.arrow_right2,0,0,0)
        self.hbox.show_all()
        
        self.label=gtk.Label('')
        self.hbox.pack_start(self.label,1,1,0)
        
        self.arrow_left=gtk.Button()
        self.arrow_left.set_relief(2)
        arrow_left2 = gtk.Arrow(gtk.ARROW_LEFT, gtk.SHADOW_NONE)        
        self.arrow_left.add(arrow_left2)
        self.hbox.pack_start(self.arrow_left,0,0,0)
        self.yearnum=gtk.Label(" <b></b> ")
        self.yearnum.set_use_markup(True)
        self.hbox.pack_start(self.yearnum,0,0,0)
        self.arrow_right=gtk.Button()
        self.arrow_right.set_relief(2)
        arrow_right2 = gtk.Arrow(gtk.ARROW_RIGHT, gtk.SHADOW_NONE)
        self.arrow_right.add(arrow_right2)
        self.hbox.pack_start(self.arrow_right,0,0,0)

class Calendar(gtk.VBox):

    def __init__(self):
        gtk.VBox.__init__(self)
        
        #register pcalender as widget
        try:
            gobject.signal_new("month-changed",pcalendar, gobject.SIGNAL_RUN_LAST ,
                       gobject.TYPE_NONE, [gobject.TYPE_INT,gobject.TYPE_INT,gobject.TYPE_INT])
            gobject.signal_new("day_selected",pcalendar, gobject.SIGNAL_RUN_LAST ,
                       gobject.TYPE_NONE, [gobject.TYPE_INT,gobject.TYPE_INT,gobject.TYPE_INT])
            gobject.signal_new("day-selected-double-click",pcalendar, gobject.SIGNAL_RUN_LAST ,
                       gobject.TYPE_NONE, [gobject.TYPE_INT,gobject.TYPE_INT,gobject.TYPE_INT])
            gobject.type_register(pcalendar) 
        except:
            pass
        
        #get current date              
        jdate=utility.convert_to_jalali(time.time())       
        self.year=jdate[0]
        self.month=jdate[1]
        self.day=jdate[2]
        self.lastday = self.day
        self.lastmin = -1       
        
        self.box2=gtk.Viewport()
        self.vbox2=gtk.VBox()
        self.vbox2.set_spacing(1)
        self.box2.add(self.vbox2)
        
        self.box1=gtk.Viewport()
        self.box1.set_border_width(5)
        self.vbox2.pack_start(self.box1,0,0,0)
        
        self.add(self.box2)
        
        self.connect("destroy",self.quit)
        self.vbox=gtk.VBox()
        self.vbox.set_spacing(3)
        self.box1.add(self.vbox)

        self.header=wmonth()
        self.vbox.pack_start(self.header.hbox,0,0,0)
        self.header.arrow_left2.connect("clicked",self.month_prev)
        self.header.arrow_right2.connect("clicked",self.month_next)
        self.header.arrow_left.connect("clicked",self.year_prev)
        self.header.arrow_right.connect("clicked",self.year_next)
        
        #add calendar widget
        self.cal=pcalendar(self.year,self.month,self.day)
        
        self.cal.connect("month-changed",self.monthchange)
        self.cal.connect("day_selected",self.daychange,'day_selected')
        self.cal.connect("day-selected-double-click",self.daychange,'day-selected-double-click')
        self.vbox.pack_start(self.cal ,1 ,1, 0)
        
        self.header.yearnum.set_label("<b>"+self.convert_to_str(self.year)+"</b>")
        self.header.monthname.set_label(' <b>'+mon_name[self.month-1]+'</b> ')

        self.box2.show_all()
        self.change_lable(self.day)
        
            
    #added by Mahdieh         
    def get_date(self,type='j'):
        if type == 'j': 
            return self.year,self.month-1,self.day 
        elif type == 'g':
            return self.gyear,self.gmonth-1,self.gday
        
    def get_jdate(self):
        return self.year,self.month-1,self.day 

    def get_gdate(self):
        return self.gyear,self.gmonth-1,self.gday 
    
    def select_month(self,month,year):
        if month in xrange(12):
            self.monthchange(year=year,month=month+1,day = self.day)
            self.daychange(month=month+1,year=year,day=self.day)
        else:
            warnings.warn("gtk_calendar_select_month: assertion `month <= 11' failed",GtkWarning,stacklevel=2)

    def select_day(self,day):
        if day in xrange(32):
            self.daychange(month=self.month,year=self.year,day=day)
        else:
            warnings.warn("gtk_calendar_select_day: assertion `day <= 31' failed",GtkWarning,stacklevel=2) 
            
    def mark_day(self,day):
        warnings.warn("gtk_calendar_mark_day: will be assert in future",GtkWarning,stacklevel=2)
        
    def unmark_day(self,day):
        warnings.warn("gtk_calendar_unmark_day: will be assert in future",GtkWarning,stacklevel=2)
    
    def clear_marks(self):
        warnings.warn("gtk_calendar_clear_marks: will be assert in future",GtkWarning,stacklevel=2)

    def get_display_options(self):
        warnings.warn("gtk_calendar_get_display_options: will be assert in future",GtkWarning,stacklevel=2)
        
    def set_display_options(self,flags):
        warnings.warn("gtk_calendar_set_display_options: will be assert in future",GtkWarning,stacklevel=2)

    def get_detail_height_rows(self):
        warnings.warn("gtk_calendar_get_detail_height_rows: will be assert in future",GtkWarning,stacklevel=2)

    def set_detail_height_rows(self,rows):
        warnings.warn("gtk_calendar_set_detail_height_rows: will be assert in future",GtkWarning,stacklevel=2)

    def get_detail_width_chars(self):
        warnings.warn("gtk_calendar_get_detail_width_chars: will be assert in future",GtkWarning,stacklevel=2)

    def set_detail_width_chars(self,chars):
        warnings.warn("gtk_calendar_set_detail_width_chars: will be assert in future",GtkWarning,stacklevel=2)

    def display_options(self,flags):
        warnings.warn("gtk_calendar_display_options: will be assert in future",GtkWarning,stacklevel=2)

    def freeze(self):
        warnings.warn("gtk_calendar_freeze: will be assert in future",GtkWarning,stacklevel=2)

    def thaw(self):
        warnings.warn("gtk_calendar_thaw: will be assert in future",GtkWarning,stacklevel=2)
        
##################################################################### 

    def _get_text(nodelist):
        rc = u""
        name = nodelist.nodeName
        for node in nodelist.childNodes:
            if node.nodeType == node.TEXT_NODE:
                rc = rc+ node.data
        return name,rc.strip()
    
    
    def convert_to_str(self,num):
        s = str(num)
        uni_c = [u'\u06f0',u'\u06f1',u'\u06f2',u'\u06f3',u'\u06f4',u'\u06f5',u'\u06f6',u'\u06f7',u'\u06f8',u'\u06f9']
        res = u""
        if len(s)>0:
            for i in s:
                res += uni_c[int(i)]
        return res
        
    def monthchange(self,obj=None,year=None,month=None,day=None):
        self.header.yearnum.set_label("<b>"+self.convert_to_str(year)+"</b>")
        self.header.monthname.set_label(' <b>'+mon_name[month-1]+'</b> ')
        self.change_lable(day)
        self.emit('month-changed')
        
    def daychange(self,obj=None,month=None,year=None,day=None,event=None):
        self.change_lable(day)
        self.day=day
        self.cal.jday = day
        self.month=month
        self.year=year
        if event:
            self.emit(event)

    def month_next(self,obj,data=None):
        self.cal.next_month()
        month=self.cal.get_month()
        self.header.monthname.set_label(' <b>'+mon_name[month-1]+'</b> ')
        year=self.cal.get_year()
        self.header.yearnum.set_label(' <b>'+self.convert_to_str(year)+'</b> ')
        self.month=month
        self.year=year
        self.change_lable(self.day)
        self.emit('next-month')
        
    def month_prev(self,obj,data=None):
        self.cal.prev_month()
        month=self.cal.get_month()
        self.header.monthname.set_label(' <b>'+mon_name[month-1]+'</b> ')
        year=self.cal.get_year()
        self.header.yearnum.set_label(' <b>'+self.convert_to_str(year)+'</b> ')
        self.month=month
        self.year=year
        self.change_lable(self.day)
        self.emit('prev-month')

    def year_next(self,obj,data=None):
        self.cal.next_year()
        year=self.cal.get_year()
        self.header.yearnum.set_label(' <b>'+self.convert_to_str(year)+'</b> ')
        self.year=year
        self.change_lable(self.day)
        self.emit('next-year')
    
    def year_prev(self, obj, data=None):
        self.cal.prev_year()
        year=self.cal.get_year()
        self.header.yearnum.set_label(' <b>'+self.convert_to_str(year)+'</b> ')
        self.year=year
        self.change_lable(self.day)
        self.emit('prev-year')

    def change_lable(self, day):
        self.year = self.cal.get_year()
        self.month=self.cal.get_month()
        self.day = day
        self.gyear,self.gmonth,self.gday = utility.jalali_to_milady(self.year,self.month,self.day)
        
    def quit(self,obj):
        self.destroy()

class pcalendar(gtk.Widget):
    Dayname = ["شنبه","یک","دو","سه","چهار","پنج","جمعه"]
    left_margin = 30
    top_margin = 25
    row_height = [0,0,0,0,0,0]
    col_width = [0,0,0,0,0,0,0]
    day=[]
    day_mil=[]
    current_day=[0,0]
    cheight = 146
    def __init__(self,year,month,day):
        gtk.Widget.__init__(self)

        self.colormap = self.get_colormap()
        self.RED_COLOR   = self.colormap.alloc_color(60000, 10535, 10000)
        self.DEACTIVE_COLOR = self.style.fg[gtk.STATE_INSENSITIVE]
        self.NORMAL_DAY_COLOR = self.style.text[gtk.STATE_NORMAL]
        self.SELECTED_DAY_COLOR = self.style.text[gtk.STATE_SELECTED]
        self.MARKED_COLOR = self.style.base[gtk.STATE_SELECTED]
        self.BACKGROUND_COLOR = self.style.base[gtk.STATE_NORMAL]
        
        self.jyear=year
        self.jmonth=month
        self.jday=day
        i=1
        j=1
        tmp=[]
        while(i<7):
            while(j<8):
                tmp.append(0)
                j+=1
            self.day.append(tmp)
            self.day_mil.append(tmp)
            tmp=[]
            i+=1
            j=1

    def day_of_week(self,year,month,day):
        days=utility.scalar_Days(year,month,day)
        days=utility.jalalyDate(days)
        return days
    
    def week_number(self,year,month,day):
        first = self.day_of_week(year,1,1) - 1
        return( ( (self.dates_difference(year,1,1, year,month,day) + first) / 7 )+(first < 4) )
    
    def year_to_days(self,year):
        return( year * 365 + (year / 4) - (year / 100) + (year / 400) )
    
    def calc_days(self,year, month, day):
        if (year < 1):
            return 0
        if ((month < 1) or (month > 12)):
            return 0
        lp=utility.leap(year)
        if ((day < 1) or (day > month_length[lp][month])):
            return 0
        return( self.year_to_days( (year-1) ) + days_in_months[lp][month] + day )
    
    def dates_difference(self,year1,month1,day1,
                         year2,month2,day2):
      return( self.calc_days(year2, month2, day2) - self.calc_days(year1, month1, day1) )

    def do_realize(self):
        
        self.set_flags(self.flags() | gtk.REALIZED)
        
        self.window = gdk.Window(
                                 self.get_parent_window(),
                                 width=self.allocation.width,
                                 height=self.allocation.height,
                                 window_type=gdk.WINDOW_CHILD,
                                 wclass=gdk.INPUT_OUTPUT,
                                 event_mask=self.get_events() | gdk.EXPOSURE_MASK
                                 | gdk.BUTTON1_MOTION_MASK | gdk.BUTTON_PRESS_MASK
                                 | gtk.gdk.POINTER_MOTION_MASK
                                 | gtk.gdk.POINTER_MOTION_HINT_MASK
                                 )
        
        self.window.set_user_data(self)
        self.style.attach(self.window)
        self.style.set_background(self.window, gtk.STATE_NORMAL )
        self.window.move_resize(*self.allocation)
    
        self.connect("button_press_event", self.press_notify_event)
        self.connect("motion_notify_event", self.motion_notify_event)
        
    def do_expose_event(self, event):
        x, y, w, h = self.allocation
        cr = self.window.cairo_create()
        cr.set_source_color(self.MARKED_COLOR)
        cr.rectangle(BORDER_WIDTH, BORDER_WIDTH,w, 20)
        cr.fill()


        cr.set_source_color(self.BACKGROUND_COLOR)
        cr.rectangle(32,20,w-25, h )
        cr.fill()
        cr.set_source_color(self.MARKED_COLOR)
        cr.rectangle(w-25,0,w, h )
        cr.fill()
        
        self.compute_day()
        self.draw_day_name()
        self.draw_week_number()
        self.draw_day_month()
    def do_size_request(self, requisition):
        requisition.height = self.cheight
        requisition.width = 135 #155
        
    def draw_day_name(self):
        x, y, w, h = self.allocation
        cr = self.window.cairo_create()
        cr.set_source_color(self.SELECTED_DAY_COLOR)
        dy = 0 #self.left_margin
        i=6
        while (i>=0):
            _dayname = self.create_pango_layout(self.Dayname[i])
            _dayname.set_font_description(pango.FontDescription("Sans 10"))
            try:
                fontw, fonth = _dayname.get_pixel_size()
            except:
                fontw, fonth = _dayname.get_pixel_size()
            plus = ( (w-self.left_margin)/7 ) -(fontw+5)
            cr.move_to( (dy+(plus/2)) , 1)
            cr.update_layout(_dayname)
            cr.show_layout(_dayname)
            dy += _dayname.get_pixel_size()[0]+5+(plus)
            i-=1

    def draw_week_number(self):
        x, y, w, h = self.allocation
        cr = self.window.cairo_create()
        cr.set_source_color(self.SELECTED_DAY_COLOR)
        dx = self.top_margin
        i=0
        year=self.jyear
        month =self.jmonth
        change =False
        hh =0
        while(i<6):
            if (i>3)and(self.day[i][6]<15)and(change==False):
                month += 1
                if month > 12 :
                    month =1
                    year +=1
                change= True
            week = self.week_number(year,month, self.day[i][6])
            if week==0:
                week = 53
            tmp=self.convert_to_str(week)
            _weeknum = self.create_pango_layout(tmp)
            _weeknum.set_font_description(pango.FontDescription("Sans 10"))
            fontw, fonth = _weeknum.get_pixel_size()
            cr.move_to( 266 , dx)
            cr.update_layout(_weeknum)
            cr.show_layout(_weeknum)
            hh = ( ( (h-self.top_margin)/6 ) -(fonth+5) )
            dx += fonth+5+hh
            i+=1
            
        self.cheight = hh+self.top_margin
            
    def draw_day_month(self):
        x, y, w, h = self.allocation
        cr = self.window.cairo_create()
        dx = 2 #self.left_margin
        dy = self.top_margin
        sx,sy=self.current_day
        i=0
        j=6
        cred=False

        while(i<6):
            while (j>=0):
                tmp=self.convert_to_str(self.day[i][j])
                _daynum = self.create_pango_layout(tmp)
                _daynum.set_font_description(pango.FontDescription("Sans 10"))

                gray=False

                if (i<2)and(self.day[i][j]>15):
                    cr.set_source_color(self.DEACTIVE_COLOR)
                    gray=True
                if (i>=4)and(self.day[i][j]<20):
                    cr.set_source_color(self.DEACTIVE_COLOR)
                    gray=True               
                
                plus = ( (w-self.left_margin)/7 ) -(_daynum.get_pixel_size()[0]+5)
                            
                if ((i==sx)and(j==sy))and(gray==False):
                    cr.set_source_color(self.MARKED_COLOR)
                    
                    x2,y2=_daynum.get_pixel_size()
                    x2=16
                    cr.rectangle((dx),dy-3,(x2+16),y2+6)
                    cr.fill()
                    cr.set_source_color(self.SELECTED_DAY_COLOR)
                    gray=True
                    cred=True
                if gray == False:
                    cr.set_source_color(self.NORMAL_DAY_COLOR)
                cr.move_to( dx+2,dy)
                cr.update_layout(_daynum)
                cr.show_layout(_daynum)
                if (gray==False)or(cred==True):
                    zy,zm,zd=utility.jalali_to_milady(self.jyear,self.jmonth,self.day[i][j])
                    _daynumm = self.create_pango_layout(str(zd))
                    _daynumm.set_font_description(pango.FontDescription("Sans 6"))
                    cr.set_source_color(self.DEACTIVE_COLOR)
                    if ((i==sx)and(j==sy)):
                        cr.set_source_color(self.SELECTED_DAY_COLOR)
                    cr.move_to( (dx+18) , dy+5)
                    cr.update_layout(_daynumm)
                    cr.show_layout(_daynumm)
                cred=False
                dx += _daynum.get_pixel_size()[0]+5+(plus)
                self.col_width[j]=dx
                j-=1

            i+=1
            j=6
            fonth = _daynum.get_pixel_size()[1]
            hh = ( ( (h-self.top_margin)/6 ) -(fonth+5) )
            dy += fonth+5+hh
            self.row_height[i-1]=dy
            dx = 0 

    def convert_to_str(self,num):
        s = str(num)
        uni_c = [u'\u06f0',u'\u06f1',u'\u06f2',u'\u06f3',u'\u06f4',u'\u06f5',u'\u06f6',u'\u06f7',u'\u06f8',u'\u06f9']
        res = u""
        if len(s)>0:
            for i in s:
                res += uni_c[int(i)]
        return res
    
    def compute_day(self):
        pyear = year = self.jyear
        month= self.jmonth
        pmonth = month -1
        if pmonth <= 0 :
            pmonth =12
            pyear -=1
        prev_month_length = month_length[utility.leap(pyear)][pmonth]
        prev_day_week = self.day_of_week(pyear, pmonth, prev_month_length)
        
        current_month_length=month_length[utility.leap(year)][month]
        sc = utility.scalar_Days(self.jyear, self.jmonth, 1)
        current_day_week = utility.jalalyDate(sc)
        
        day = (prev_month_length-(current_day_week-1))

        if ( current_day_week==0):
            day=1

        i=0
        j=0
        sday = 0
        while(i<6):
            while(j<7):
                self.day[i][j]=day
                if (self.jday==day)and(sday==0):
                    self.current_day=[i,j]
                day+=1
                if (i>3)and(day>current_month_length):
                    day =1
                    sday=1

                if (i<2)and(day>prev_month_length):
                    day =1
                j+=1
            i+=1
            j=0
            
    def press_notify_event(self,obj,data):
        x,y,data_=data.window.get_pointer()
        col=self.find_col(x)
        row=self.find_row(y)
        if (row>=0)and(col>=0):
            self.jday = self.day[row][col]
            self.current_day=[0,0]
            if (row==0)and(self.day[row][col]>15):
                self.jmonth -= 1
                if self.jmonth <= 0 :
                    self.jmonth =12
                    self.jyear -=1
                self.emit("month-changed",self.jyear,self.jmonth,self.jday)

            if (row>3)and(self.day[row][col]<15):
                self.jmonth += 1
                if self.jmonth > 12 :
                    self.jmonth =1
                    self.jyear +=1
                self.emit("month-changed",self.jyear,self.jmonth,self.jday)
            
            alloc = self.get_allocation()
            rect = gdk.Rectangle(0, 0, alloc.width, alloc.height)
            self.window.invalidate_rect(rect,True)
            if data.type == gdk._2BUTTON_PRESS:
                self.emit("day-selected-double-click",self.jmonth,self.jyear,self.day[row][col])
            else:
                self.emit("day_selected",self.jmonth,self.jyear,self.day[row][col])
        return True
    
    def find_col(self,x):
        col=6
        i=6
        while (i>=0):
            if (x<self.col_width[i]):
                return col
            col-=1
            i-=1
        return -1

    def find_row(self,y):
        if (y<self.top_margin):
            return -1
        row=0
        for i in self.row_height :
            if (y<i):
                return row
            row+=1
        return -1
    
    def motion_notify_event(self,obj,event):
        pass
    
    def next_month(self):
        self.jmonth += 1
        if self.jmonth > 12 :
            self.jmonth =1
            self.jyear +=1
        alloc = self.get_allocation()
        rect = gdk.Rectangle(0, 0, alloc.width, alloc.height)
        self.window.invalidate_rect(rect,True)
            
    def prev_month(self):
        self.jmonth -= 1
        if self.jmonth <= 0 :
            self.jmonth =12
            self.jyear -=1
        alloc = self.get_allocation()
        rect = gdk.Rectangle(0, 0, alloc.width, alloc.height)
        self.window.invalidate_rect(rect,True)

    def next_year(self):
        self.jyear+=1
        alloc = self.get_allocation()
        rect = gdk.Rectangle(0, 0, alloc.width, alloc.height)
        self.window.invalidate_rect(rect,True)
        
    def prev_year(self):
        self.jyear-=1
        alloc = self.get_allocation()
        rect = gdk.Rectangle(0, 0, alloc.width, alloc.height)
        self.window.invalidate_rect(rect,True)
    
    def get_month(self):
        return self.jmonth

    def get_year(self):
        return self.jyear
    
    def get_day(self):
        return self.jday

gobject.signal_new("prev-month",Calendar, gobject.SIGNAL_RUN_LAST ,gobject.TYPE_NONE, [])
gobject.signal_new("next-month",Calendar, gobject.SIGNAL_RUN_LAST ,gobject.TYPE_NONE, [])
gobject.signal_new("next-year",Calendar, gobject.SIGNAL_RUN_LAST ,gobject.TYPE_NONE, [])
gobject.signal_new("prev-year",Calendar, gobject.SIGNAL_RUN_LAST ,gobject.TYPE_NONE, [])
gobject.signal_new("day-selected",Calendar, gobject.SIGNAL_RUN_LAST ,gobject.TYPE_NONE, [])
gobject.signal_new("day-selected-double-click",Calendar, gobject.SIGNAL_RUN_LAST ,gobject.TYPE_NONE, [])
gobject.signal_new("month-changed",Calendar, gobject.SIGNAL_RUN_LAST ,gobject.TYPE_NONE, [])

def sayHello(widget):
    print widget.get_date()    

if __name__ == '__main__':
    window = gtk.Window(gtk.WINDOW_TOPLEVEL)
    window.set_default_size(300,75)
    window.set_title("Calendar Example")
    window.connect("destroy", lambda x: gtk.main_quit())
    calendar = Calendar()
    #calendar.connect("month-changed", sayHello)
    calendar.select_month(10,1388)
    window.add(calendar)
    window.show_all()
    gtk.main()
    