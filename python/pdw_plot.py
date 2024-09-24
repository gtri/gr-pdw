#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2024 GTRI.
#
# This is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this software; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
#



import sys
from PyQt5 import QtWidgets
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

import threading
import time

from gnuradio import gr
import pmt

from enum import Enum

class PLOT_TYPE(Enum):
    WIDTH = 0
    POWER = 1
    FREQ = 2
    TOA = 3

    @staticmethod
    def from_string(s):
        try:
            return PLOT_TYPE[s.upper()]
        except KeyError:
            raise ValueError()

class update_timer(threading.Thread):
    def __init__(self, event, plot_event, updateRate):
        threading.Thread.__init__(self)
        self.wait_done = event
        self.plot_event = plot_event
        self.updateRate = updateRate

    def run(self):
        while not self.wait_done.wait(self.updateRate):
            self.plot_event.set()


class pdw_plot(gr.sync_block, FigureCanvas):
    """
    docstring for block pdw_plot
    """
    def __init__(self, lbl, plotData, plotLimits, maxPDW, plotItemNum, updateRate, backgroundColor, fontColor, ringColor, Parent=None,
                 width=4, height=4, dpi=100):
        gr.sync_block.__init__(self,
            name="pdw_plot",
            in_sig=None,
            out_sig=None)

        self.lbl = lbl

        self.plotData = PLOT_TYPE[plotData]
        self.maxPDW = maxPDW
        self.plotItemNum = plotItemNum
        self.updateRate = updateRate
        self.plotLimits = plotLimits

        self.times_up = threading.Event()
        self.update_plot_now = threading.Event()
        self.update_timer = update_timer(self.times_up, self.update_plot_now, self.updateRate)
        self.update_timer.start()

        self.message_port_register_in(pmt.intern("pdw"))
        self.set_msg_handler(pmt.intern("pdw"), self.msgHandler)

        self.fontColor = fontColor
        self.backgroundColor = backgroundColor
        self.ringColor = ringColor

        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.fig.patch.set_facecolor(self.backgroundColor)
        self.fig.set_tight_layout(True)
        self.axes_pw = self.fig.add_subplot(
            111, polar=False, facecolor=self.backgroundColor)

        self.line, = self.axes_pw.plot([],[], '.', markersize=8, linestyle=None, markeredgecolor="blue")
        self.axes_pw.grid(True)

        self.axes_pw.set_xlim([0, self.plotItemNum])

        if self.plotData == PLOT_TYPE.WIDTH:
            if self.plotLimits:
                self.axes_pw.set_ylim([self.plotLimits[0], self.plotLimits[1]])
            else:
                self.axes_pw.set_ylim([0, 200])
            self.axes_pw.set_ylabel("Pulse Width (us)")
            self.axes_pw.set_title("PDW: Pulse Width")

        elif self.plotData == PLOT_TYPE.POWER:
            if self.plotLimits:
                self.axes_pw.set_ylim([self.plotLimits[0], self.plotLimits[1]])
            else:
                self.axes_pw.set_ylim([-100, 0])
            self.axes_pw.set_ylabel("Pulse Power (dBm)")
            self.axes_pw.set_title("PDW: Pulse Power")

        elif self.plotData == PLOT_TYPE.FREQ:
            if self.plotLimits:
                self.axes_pw.set_ylim([self.plotLimits[0], self.plotLimits[1]])
            else:
                self.axes_pw.set_ylim([-1, 1])
            self.axes_pw.set_ylabel("Frequency (MHz)")
            self.axes_pw.set_title("PDW: Pulse Frequency")

        FigureCanvas.__init__(self, self.fig)
        self.setParent(Parent)

        self.title = self.fig.suptitle(self.lbl, fontsize=8, fontweight='bold',
                                        color=self.fontColor)

        FigureCanvas.setSizePolicy(self,
                                    QtWidgets.QSizePolicy.Expanding,
                                    QtWidgets.QSizePolicy.Expanding)
        self.setMinimumSize(250, 250)
        FigureCanvas.updateGeometry(self)

        # Plotting Data
        self.pw = [] # Pulse Width
        self.pp = [] # Pulse Power
        self.f_start = [] # Pulse Frequency
        self.pdw_time = [] # Not Used



    def start(self):
        return True
    
    def stop(self):
        self.times_up.set()
        self.update_timer.join()

        return True
    
    def msgHandler(self, msg):

        if self.update_plot_now.is_set():
            self.updatePlots(msg)
        else:
            data = msg

    def updatePlots(self, msg):

        data = pmt.to_python(msg)
        
        if isinstance(data, dict):
            keys = list(data.keys())
            keys.sort()

            for pdw_num in keys:
                if pdw_num > self.maxPDW:
                    break
                else:
                    pdw = data[pdw_num]['pdw']
                    if self.plotData == PLOT_TYPE.POWER:
                        self.pp.append(pdw['pulse_power'])
                    elif self.plotData == PLOT_TYPE.WIDTH:
                        self.pw.append(pdw['pw_time']/1e-6)
                    elif self.plotData == PLOT_TYPE.FREQ:
                        self.f_start.append(pdw['start_freq']/1e6)

            if len(self.pw) > self.plotItemNum:
                items_remove = int(len(self.pw) - self.plotItemNum)
                self.pw = self.pw[items_remove:]

            if len(self.pp) > self.plotItemNum:
                items_remove = int(len(self.pp) - self.plotItemNum)
                self.pp = self.pp[items_remove:]

            if len(self.f_start) > self.plotItemNum:
                items_remove = int(len(self.f_start) - self.plotItemNum)
                self.f_start = self.f_start[items_remove:]


            if self.plotData == PLOT_TYPE.WIDTH:
                self.line.set_data(np.arange(0, len(self.pw), step=1), self.pw)

            elif self.plotData == PLOT_TYPE.POWER:
                self.line.set_data(np.arange(0, len(self.pp), step=1), self.pp)

            elif self.plotData == PLOT_TYPE.FREQ:
                
                self.line.set_data(np.arange(0, len(self.f_start), step=1), self.f_start)

            self.draw()

            self.update_plot_now.clear()

