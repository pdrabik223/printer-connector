#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pocketvna
import math
import numpy as np
import skrf  as rf
import similaritymeasures as sm
import sys
import os
import pylab as plt
import datetime

from sys import exit

import tkinter as tk
from tkinter import ttk
from tkinter import font as tkFont

import threading
import time

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import python_test_includee as helper

pwd = os.path.dirname(os.path.abspath(__file__))
standardsDir=os.path.join(pwd, 'python_test_curves_similarity_data/')
helper.hack_LoadNetworks(standardsDir)

def get_desc(descriptors, ifaceCode):
    for desc in descriptors:
        if desc['InterfaceCode'] == ifaceCode:
            return desc
    return dict({})

class WizardStep(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

    def on_close(self):
        pass

    def Run(self):
        pass

class Step1SN(WizardStep):
    def on_connect_selected(self):
        sn = str(self.snedit.get()).strip()
        if len(sn) > 0:
            print( 'START CONNECTION `{}`'.format(sn) )
            self.btn['state'] = tk.DISABLED
            self.on_start_callback(sn)

    def header_text(self):
        return "Serial Number"

    def __init__(self, parent, on_start_callback):
        super().__init__(parent)

        lb = tk.Label(self, text="  Please connect pocketVNA without")
        lb.pack()
        lb = tk.Label(self, text="connection (fitting) and enter serial number*")
        lb.pack()

        frame = tk.Frame(self)
        frame.pack(expand=True, fill=tk.BOTH)

        lb = tk.Label(frame, text="Serial Number on Sticker*")
        lb.pack(side=tk.LEFT, padx=5, pady=5)

        self.snedit = tk.Entry(frame)
        self.snedit.pack(side=tk.RIGHT, padx=5, pady=5)

        self.btn = tk.Button (self, text ="Start >>", command=self.on_connect_selected)
        self.btn.pack(padx=5, pady=5, expand=True)
        self.on_start_callback = on_start_callback

        # frame.lift()
        self.snedit.focus()

class Step2Connected(WizardStep):
    def header_text(self):
        return "Connected & Start Open-Open Check"

    def Run(self):
        self.scan_thread = threading.Thread(target=self.start_test1_open_open)
        self.scan_thread.start()
    
    def on_complete(self):
        self.on_scan_complete(self.ntwk)

    def on_failed(self):
        self.on_scan_failed()
        
    def start_test1_open_open(self):
        try:
            self.ntwk = self.driver.scan_skrf_network(helper.StandardFrequencyVector,5, self.on_progress)
            self.after(100, self.on_complete)
        except pocketvna.PocketVnaHandlerInvalid:
            self.after(100, self.on_failed)
            self.driver.close()

    def __init__(self, parent, device, on_scan_complete, on_scan_failed):
        super().__init__(parent)
        self.driver = device
        self.infoLabel = tk.Label(self, text='No Connection')
        self.infoLabel.pack(expand=True, fill=tk.X)
        self.progressbar=ttk.Progressbar(self, orient=tk.HORIZONTAL,length=100,mode='determinate')
        self.progressbar.pack(expand=True, fill=tk.X)
        devinfo = device.devinfo()
        self.infoLabel['text'] = 'Connected: {}&{}, {}'.format(devinfo['VendorId'], devinfo['ProductId'], devinfo['SN'])
        self.thread = None
        self.ntwk = None
        self.on_scan_complete = on_scan_complete
        self.on_scan_failed   = on_scan_failed

    def on_progress(self, u, i):
        self.set_progress(  i * 100 / len(helper.StandardFrequencyVector) )
        return pocketvna.Continue

    def set_progress(self, percent):
        self.progressbar['value'] = percent

class Step3OpenOpenCheck(WizardStep):
    def header_text(self):
        return "Check Whether Open-Open"

    def on_close(self):
        for w in self.result_plots:
            w.destroy()
        self.result_plots = []
    
    def Run(self):
        self.result = dict({})
        self.check_is_open_open(self.ntwk)

    def check_is_open_open(self, ntwk):
        if ntwk is not None:
            dists, names = helper.find_nearest_network(ntwk)
            passed = True
            for p1 in range(0,2):
                for p2 in range(0,2):
                    if not self.bg_set_4_port(dists, names, p1, p2):
                        passed = False

            self.result["passed"] = passed
            if passed:
                self.on_test_passed()
            else:
                self.on_test_failed()

    def is_requried_standard(self, p1, p2, dist, standard):
        standard = standard.lower()
        if p1 == p2:
            return dist < helper.adjust_threshold(helper.GoodDistanceThreshold) and (standard == 'open' or standard == 'open-open')
        else:
            return  dist < helper.adjust_threshold(helper.GoodDistanceThreshold) and ('open' in standard or 'short' in standard or 'shrt' in standard or 'load' in standard)


    def bg_set_4_port(self, dists, names, p1, p2):
        d    = dists[p1][p2]
        fn   = names[p1][p2]
        content = helper.parse_filename(fn)
        standard = content['s{}{}'.format(p1+1, p2+1)]

        self.result['s{}{}-distance'.format(p1+1, p2+1)] = d
        self.result['s{}{}-filename'.format(p1+1, p2+1)] = fn
        self.result['s{}{}-standard'.format(p1+1, p2+1)] = standard

        cb = self.scan_result_s[p1][p2]
        cb['text'] = 'S{}{} - {}, {}'.format(p1+1, p2+1, d, standard)
        cb.configure( background=helper.get_color_for_distance(d) )
        if self.is_requried_standard(p1, p2, d, standard):
            cb.select()
            self.result['s{}{}-passed'.format(p1+1, p2+1)] = True
            return True
        else:
            self.bg_show_plot(p1, p2, d, standard, helper.StandardNetworks[fn])
            cb.deselect()
            self.result['s{}{}-passed'.format(p1+1, p2+1)] = False
            return False

    def bg_show_plot(self, p1, p2, d, standard, standardNtwk):
        if p1 == p2:
            self.bg_show_network_parameter(standardNtwk, self.ntwk, p1, p2, standard, d, 'reflective')
        if p2 != p1:
            self.bg_show_network_parameter(standardNtwk, self.ntwk, p1, p2, standard, d, 'transmissive')

    def bg_show_network_parameter(self, standardNetwork, scannedNetwork, p1, p2, fittingStandard, dist, addition):
        goodFit=dist < helper.adjust_threshold(helper.GoodDistanceThreshold)

        top = tk.Toplevel()
        top.geometry("300x300")

        if goodFit:
            fig = plt.Figure(figsize=(5,5), dpi=100)
            top.title('{}, S{}{} as {} ({})'.format(addition, p1+1, p2+1, fittingStandard, dist))
        else:
            fc = '#f1948a' if dist > helper.adjust_threshold(helper.BadDistanceThreshold) else "#f9e79f"
            fig = plt.Figure(figsize=(5,5), dpi=100, facecolor=fc)
            top.title('S{}{} as {}. But dosnt fit well ({})'.format(p1+1, p2+1, fittingStandard, dist))

        a = fig.add_subplot(111)
        a.set_xlabel('Frequency (Hz)')
        a.set_ylabel('dB')

        a.plot(standardNetwork.f, helper.db(standardNetwork.s[:,p1,p2]), label='Predefined Standard', color='gray', lw=3, linestyle='dashdot')

        curveColor='#2471a3' if goodFit else 'red'
        curveWidth= 1 if goodFit else 2
        a.plot(scannedNetwork.f,  helper.db(scannedNetwork.s[:,p1,p2]), label='Measured', color=curveColor, lw=curveWidth, linestyle='solid')

        # a.plot(standardNetwork.f, moving_average(db(standardNetwork.s[:,p1,p2])), label='PS MA', color='black', lw=1, linestyle='solid')

        canvas = FigureCanvasTkAgg(fig, top)
        canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        self.result_plots.append(top)

    def on_next_test(self):
        self.on_next_SL_test(self.result)

    def on_test_passed(self):
        self.nextButton['state'] = tk.NORMAL
        self.verdictLabel['text'] = 'Passed'
        self.verdictLabel.configure(background=helper.ExcellentColor)

    def on_test_failed(self):
        self.verdictLabel['text'] = 'Failed'
        self.verdictLabel.configure(background=helper.BadColor)
        self.nextButton['state'] = tk.NORMAL

    def create_button(self):
        lbl = tk.Label(self, text='Please connect S to port 1')
        lbl.pack()
        lbl = tk.Label(self, text=' and L to port 2 and press enter')
        lbl.pack()
        self.nextButton = tk.Button(self, text='Start Next >>', command=self.on_next_test)
        self.nextButton.pack()
        self.nextButton['state'] = tk.DISABLED

 
    def __init__(self, parent, ntwk, on_next_SL_test, on_rescan_requested):
        super().__init__(parent)
        self.scan_result = tk.Frame(self)
        self.ntwk = ntwk
        self.on_next_SL_test = on_next_SL_test

        self.scan_result_s = [[None,None],[None,None]]
        self.original_background = self.scan_result.cget("background")
        self.vars = [[tk.BooleanVar(),tk.BooleanVar()],[tk.BooleanVar(),tk.BooleanVar()]]
        for p1 in range(0,2):
            for p2 in range(0,2):
                cvar1 = self.vars[p1][p2]
                cvar1.set(0)
                self.scan_result_s[p1][p2] = tk.Checkbutton(self.scan_result, text='s{}{}'.format(p1+1, p2+1), variable=cvar1)
                self.scan_result_s[p1][p2].deselect()
                self.scan_result_s[p1][p2].configure(background=self.original_background, state=tk.DISABLED)
                self.scan_result_s[p1][p2].grid(column=p2, row=p1, padx=15, pady=15)
        self.scan_result.pack()
        self.result_plots = []

        fontStyle = tkFont.Font(family="Courier New", size=20)
        self.verdictLabel = tk.Label(self, text='...', font=fontStyle)
        self.verdictLabel.pack()

        self.create_button()
        self.updatebtn = tk.Button(self, text='<< Re-SCAN', command=on_rescan_requested, relief=tk.FLAT)
        self.updatebtn.pack(side=tk.LEFT, padx=5, pady=5)

class Step4Connected(Step2Connected):
    def header_text(self):
        return "Start Short-Load Check"

    def __init__(self, parent, device, on_scan_complete, on_scan_failed):
        super().__init__(parent, device, on_scan_complete, on_scan_failed)

class Step5ShortLoadCheck(Step3OpenOpenCheck):
    def header_text(self):
        return "Check Whether Short-Load"

    def create_button(self):
        self.nextButton = tk.Button(self, text='Done', command=self.on_next_test)
        self.nextButton.pack()
        self.nextButton['state'] = tk.DISABLED

    def is_requried_standard(self, p1, p2, dist, standard):
        standard = standard.lower()
        if p1 != p2:
            return dist < helper.adjust_threshold(helper.GoodDistanceThreshold)
        else:
            if p1 == 0 and p2 == 0:
                return dist < helper.adjust_threshold(helper.GoodDistanceThreshold) and (standard == 'short' or standard == 'shrt')
            elif p1 == 1 and p2 == 1: 
                return dist < helper.adjust_threshold(helper.GoodDistanceThreshold) and (standard == 'load' or standard == 'match')
        return False

    def __init__(self, parent, ntwk, on_next_SL_test, on_rescan_requested):
        super().__init__(parent, ntwk, on_next_SL_test, on_rescan_requested)

class MyApp(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.page_index, self.page_code = -1, 'nopage'
        self.topmost = parent
        self.scan_mutex = threading.Lock()

        self.driver = None
        self.scan_thread = None
        self.mutex = threading.Lock()
        self.active_SerialNumber = None

        parent.geometry('500x300')

        self.set_title("Device Checker")
        self.header = tk.Label(self, text="~", bd=2, relief="groove")
        self.header.pack(side=tk.TOP, fill=tk.X)

        self.current_wizard_page = None

        self.statusbar = tk.Label(parent, text="No device", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.statusbar.pack(side=tk.BOTTOM, fill=tk.X)
        #

    def __del__(self):
        if self.driver is not None:
            self.driver.close()
            self.driver = None
        pocketvna.close_api()

    def set_title(self, s):
        self.topmost.title(s)

    def jump_step(self):
        self.next_select_step()
        self.current_wizard_page.pack(fill="both", expand=True)
        self.header['text'] = self.current_wizard_page.header_text()
        self.current_wizard_page.Run()

    def on_serial_number_entered(self, sn):
        self.active_SerialNumber = sn        
        self.set_title("Device Checker: " + sn)
        self.connect_2_device()

    def on_open_open_network_scanned(self, ntwk):
        self.open_open_network = ntwk
        self.jump_step()

    def jump_to_starter(self):
        self.set_title("Device Checker")
        self.active_SerialNumber = None
        self.page_index = -1
        self.driver.close()
        self.driver = None
        self.statusbar['text'] = "No device"
        self.jump_step()

    def on_next_SL_test(self, dictOpenOpenCheckResult):
        self.open_open_check_result = dictOpenOpenCheckResult
        self.jump_step()

    def on_short_load_network_scanned(self, ntwk):
        self.short_load_network = ntwk
        self.jump_step()

    def on_test_complete(self, dictShortLoadCheckResult):
        self.short_load_check_result = dictShortLoadCheckResult
        self.save_results()
        self.jump_to_starter()

    def save_results(self):
        if self.active_SerialNumber is not None:
            dirname = "./" + self.active_SerialNumber + '.' + datetime.datetime.now().strftime("%Y-%m-%dT%H_%M_%S")
            os.mkdir(dirname)
            self.open_open_network.write_touchstone(filename=dirname + '/Open_Open.s2p')
            self.short_load_network.write_touchstone(filename=dirname + '/Short_Load.s2p')
            try:
                with open(dirname + '/Open-Open-check.txt', 'a') as the_file:
                    the_file.write(str(self.open_open_check_result))
            except:
                print('Could not save Open-Open check results: ')
                print(self.open_open_check_result)

            try:
                with open(dirname + '/Short_Load-check.txt', 'a') as the_file:
                    the_file.write(str(self.short_load_check_result))
            except:
                print('Could not save Short_Load check results: ')
                print(self.short_load_check_result)

    def connect_2_device(self):
        driver = pocketvna.Driver()
        if self.set_appropriate_connection(driver):
            self.driver = driver
            devinfo = self.driver.devinfo()
            ifcs = "VCI" if devinfo["InterfaceCode"] == pocketvna.ConnectionInterfaceCode.CIface_VCI else "HID"
            self.statusbar['text'] = '+ {}&{}, {} / {}'.format(devinfo['VendorId'], devinfo['ProductId'], devinfo['SN'], ifcs)
            self.jump_step()
            # 
        else:
            driver.close()
            self.after(5000, self.connect_2_device)

    def on_connection_lost(self):
        tk.messagebox.showerror("Connection Lost", "Device/Connection has disappeared :(")
        self.jump_to_starter()

    def jump_2_previous(self):
        self.page_index -= 2
        self.jump_step()

    def next_select_step(self):
        self.page_index += 1
        if self.current_wizard_page  is not None:
            self.current_wizard_page.on_close()
            self.current_wizard_page.destroy()
            self.current_wizard_page = None

        if self.page_index == 0:
            self.current_wizard_page = Step1SN(self, self.on_serial_number_entered)
        elif self.page_index == 1:
            self.current_wizard_page = Step2Connected(self, self.driver, self.on_open_open_network_scanned, self.on_connection_lost)
        elif self.page_index == 2:
            self.current_wizard_page = Step3OpenOpenCheck(self, self.open_open_network, self.on_next_SL_test, self.jump_2_previous)
        elif self.page_index == 3:
            self.current_wizard_page = Step4Connected(self, self.driver, self.on_short_load_network_scanned, self.on_connection_lost)
        elif self.page_index == 4:
            self.current_wizard_page = Step5ShortLoadCheck(self, self.short_load_network, self.on_test_complete, self.jump_2_previous)
        else:
            self.page_index, self.page_code = -1, 'nopage'
            self.next_select_step()


    def Run(self):
        self.pack()
        self.after(50, self.jump_step)
        self.mainloop()

    def set_appropriate_connection(self, driver):
        if driver.count() < 1:
            return False

        descriptors = sorted(driver.ext_get_devices_list(), key=helper.get_comare_field)
        for iface in list([pocketvna.ConnectionInterfaceCode.CIface_VCI, pocketvna.ConnectionInterfaceCode.CIface_HID]):
            desc = get_desc(descriptors, iface)
            if bool(desc):
                if driver.safe_connect_to(desc):
                    if driver.valid():
                        return True

        return False


 

# lbl = tk.Label(top, text="Hello")
# lbl.grid(column=0, row=0)
# btn = tk.Button (top, text ="Connect", command=on_click)
# btn.grid(column=1, row=0)
#btn.pack()

app = MyApp(tk.Tk())
app.Run()

