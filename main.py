#!/usr/bin/env python3
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf
import imutils
from imutils.video import VideoStream
from threading import Thread
import time
import cv2
import numpy as np

class Worker(Thread):
    def __init__(self,input):
        Thread.__init__(self)
        self.data = input
        self.run_command = False
    def run(self):
        while self.run_command:
            #Command executed by Worker
            self.data.pic = self.data.vs.read()
            pic = imutils.resize(self.data.pic, width=600)
            blurred = cv2.GaussianBlur(pic,(11,11),0)
            hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
            msk = cv2.inRange(hsv,self.data.lower,self.data.upper)
            msk = cv2.erode(msk, None, iterations=2)
            msk = cv2.dilate(msk, None, iterations=2)
            msk = cv2.cvtColor(msk, cv2.COLOR_GRAY2BGR)
            pic = np.array(msk).flatten()
            pixbuf = GdkPixbuf.Pixbuf.new_from_data(pic,GdkPixbuf.Colorspace.RGB,False,8,600,400,3*600)
            self.data.image.set_from_pixbuf(pixbuf)
            time.sleep(1.0/self.data.worker_freq)

class PyApp(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self,title="PyTracking")
        self.set_default_size(600,450)
        self.connect("destroy", self.quit_and_kill_worker)
        #Initialize widget grid
        self.grid = Gtk.Grid()
        self.grid.set_row_spacing(5)
        self.grid.set_column_spacing(2)
        self.add(self.grid)
        #Start/Stop button
        self.start_stop_button = Gtk.Button(label=("Start"))
        self.start_stop_button.connect("clicked",self.start_stop_worker)
        self.grid.attach(self.start_stop_button, 1,0, 1, 1)        
        #Slider
        self.slider1 = Gtk.Scale.new_with_range(Gtk.Orientation.VERTICAL,0,255,1)
        self.slider2 = Gtk.Scale.new_with_range(Gtk.Orientation.VERTICAL,0,255,1)
        self.slider3 = Gtk.Scale.new_with_range(Gtk.Orientation.VERTICAL,0,255,1)
        self.slider4 = Gtk.Scale.new_with_range(Gtk.Orientation.VERTICAL,0,255,1)
        self.slider5 = Gtk.Scale.new_with_range(Gtk.Orientation.VERTICAL,0,255,1)
        self.slider6 = Gtk.Scale.new_with_range(Gtk.Orientation.VERTICAL,0,255,1)
        self.slider7 = Gtk.Scale.new_with_range(Gtk.Orientation.VERTICAL,1,60,1)
        self.slider8 = Gtk.Scale.new_with_range(Gtk.Orientation.VERTICAL,1,200,1)
        self.slider1.set_value(0)
        self.slider2.set_value(0)
        self.slider3.set_value(0)
        self.slider4.set_value(255)
        self.slider5.set_value(255)
        self.slider6.set_value(255)
        self.slider7.set_value(5)
        self.slider8.set_value(75)
        self.lower = np.array([0,0,0])
        self.upper = np.array([255,255,255])
        self.worker_freq = 5
        self.rad = 75
        self.slider1.connect("value-changed", self.slider1_moved)
        self.slider2.connect("value-changed", self.slider2_moved)
        self.slider3.connect("value-changed", self.slider3_moved)
        self.slider4.connect("value-changed", self.slider4_moved)
        self.slider5.connect("value-changed", self.slider5_moved)
        self.slider6.connect("value-changed", self.slider6_moved)
        self.slider7.connect("value-changed", self.slider7_moved)
        self.slider8.connect("value-changed", self.slider8_moved)
        self.slider1_label = Gtk.Label()
        self.slider1_label.set_label("R")
        self.slider2_label = Gtk.Label()
        self.slider2_label.set_label("G")
        self.slider3_label = Gtk.Label()
        self.slider3_label.set_label("B")
        self.slider4_label = Gtk.Label()
        self.slider4_label.set_label("R")
        self.slider5_label = Gtk.Label()
        self.slider5_label.set_label("G")
        self.slider6_label = Gtk.Label()
        self.slider6_label.set_label("B")
        self.slider7_label = Gtk.Label()
        self.slider7_label.set_label("Hz")
        self.slider8_label = Gtk.Label()
        self.slider8_label.set_label("Rad")
        self.grid.attach(self.slider1, 4,0, 1, 30)        
        self.grid.attach(self.slider2, 5,0, 1, 30)        
        self.grid.attach(self.slider3, 6,0, 1, 30)        
        self.grid.attach(self.slider4, 7,0, 1, 30)        
        self.grid.attach(self.slider5, 8,0, 1, 30)        
        self.grid.attach(self.slider6, 9,0, 1, 30)
        self.grid.attach(self.slider7, 10,0, 1, 30)
        self.grid.attach(self.slider8, 11,0, 1, 30)
        self.grid.attach(self.slider1_label, 4,35, 1, 1)        
        self.grid.attach(self.slider2_label, 5,35, 1, 1)        
        self.grid.attach(self.slider3_label, 6,35, 1, 1)        
        self.grid.attach(self.slider4_label, 7,35, 1, 1)        
        self.grid.attach(self.slider5_label, 8,35, 1, 1)        
        self.grid.attach(self.slider6_label, 9,35, 1, 1)        
        self.grid.attach(self.slider7_label, 10,35, 1, 1)        
        self.grid.attach(self.slider8_label, 11,35, 1, 1)        
        #Initialize frame
        self.frame = Gtk.Frame()
        self.image = Gtk.Image.new()
        self.vs = VideoStream(src=0).start()
        time.sleep(2.0)
        self.pic = self.vs.read()
        pic = imutils.resize(self.pic, width=600)
        pic = np.array(pic).flatten()
        pixbuf = GdkPixbuf.Pixbuf.new_from_data(pic,GdkPixbuf.Colorspace.RGB, False, 8, 600, 400, 3*600)
        self.image.set_from_pixbuf(pixbuf)
        self.frame.add(self.image)
        self.grid.attach(self.frame, 1,50,10,1)
        #Initialize worker
        self.worker = Worker(self)
        self.worker.start()
        #Show Window
        self.show_all()

    #Function to start and stop worker
    def start_stop_worker(self, widget):
        self.worker.run_command = not self.worker.run_command
        if not self.worker.run_command:
            widget.set_label("Start")
            self.worker.join()
            self.set_title("PyTracking - Stopped")
        else:
            widget.set_label("Stop")
            self.worker = Worker(self)
            self.worker.run_command = True
            self.worker.start()
            self.set_title("PyTracking - Running")
    #Functions to handle slider
    def slider1_moved(self, widget):
        slidervalue = int(self.slider1.get_value())
        if slidervalue > self.upper[0]:
            self.upper[0] = slidervalue
            self.slider4.set_value(slidervalue)
        self.lower[0] = slidervalue
    def slider2_moved(self, widget):
        slidervalue = int(self.slider2.get_value())
        if slidervalue > self.upper[1]:
            self.upper[1] = slidervalue
            self.slider5.set_value(slidervalue)
        self.lower[1] = slidervalue
    def slider3_moved(self, widget):
        slidervalue = int(self.slider3.get_value())
        if slidervalue > self.upper[2]:
            self.upper[2] = slidervalue
            self.slider6.set_value(slidervalue)
        self.lower[2] = slidervalue
    def slider4_moved(self, widget):
        slidervalue = int(self.slider4.get_value())
        if slidervalue < self.lower[0]:
            self.lower[0] = slidervalue
            self.slider1.set_value(slidervalue)
        self.upper[0] = slidervalue
    def slider5_moved(self, widget):
        slidervalue = int(self.slider5.get_value())
        if slidervalue < self.lower[1]:
            self.lower[1] = slidervalue
            self.slider2.set_value(slidervalue)
        self.upper[1] = slidervalue
    def slider6_moved(self, widget):
        slidervalue = int(self.slider6.get_value())
        if slidervalue < self.lower[2]:
            self.lower[2] = slidervalue
            self.slider3.set_value(slidervalue)
        self.upper[2] = slidervalue
    def slider7_moved(self, widget):
        self.worker_freq = int(self.slider7.get_value())
    def slider8_moved(self, widget):
        self.rad = int(self.slider8.get_value())
    #Function evaluated at window kill
    def quit_and_kill_worker(self,widget):
        self.worker.quit = True
        self.worker.join()
        print("Quiting PyTracking")
        Gtk.main_quit()

PyApp()
Gtk.main()
