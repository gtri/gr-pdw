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


import numpy as np
from gnuradio import gr
import pmt
import os, time
import pickle

class usrp_power_cal_table(gr.sync_block):
    """
    docstring for block usrp_power_cal_table
    """
    def __init__(self, use_cal, freq, ref_level):
        gr.sync_block.__init__(self,
            name="usrp_power_cal_table",
            in_sig=None,
            out_sig=None)
        
        cal_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "./"))
        cal_file = os.path.join(cal_dir, 'b210_pdw.pickle')

        self.cal_table_file = cal_file
        self.freq = freq
        self.ref_level = ref_level
        self.use_cal = use_cal

        with open(self.cal_table_file, 'rb') as cal_file:
            self.cal_table = pickle.load(cal_file)
        
        self.message_port_register_out(pmt.intern("gain_msg"))
        self.message_port_register_out(pmt.intern("ref_level_msg"))

        self.get_gain()
    
    def start(self):
        # GNU Radio calls start on each block at start of flowgraph
        # Need this to emit a single gain calculation message for the
        # default parameters
        self.send_ref_msg()
        self.get_gain()
        return True
    
    def stop(self):
        return True
    
    def ref_changed(self, value):
        self.ref_level = value
        self.send_ref_msg() 
        self.get_gain()

    def send_ref_msg(self):
        set_ref_level_cmd = pmt.make_dict()
        set_ref_level_cmd = pmt.dict_add(set_ref_level_cmd, pmt.to_pmt('ref_level'), pmt.to_pmt(self.ref_level))
        self.message_port_pub(pmt.intern("ref_level_msg"), set_ref_level_cmd)

    def freq_changed(self, value):
        self.freq = value
        self.get_gain()
    
    def get_gain(self):

        if self.use_cal:
            channel = 0
            port = "RX2"
            freq = self.freq
            ref_level = self.ref_level

            cal = self.cal_table[channel][port]
            cal_freqs = list(cal.keys())

            freq_index = np.searchsorted(cal_freqs, freq)
            
            lower_freq = cal_freqs[freq_index-1]
            upper_freq = cal_freqs[freq_index]

            # Find the calibrated gain for the actual calibrated freqs
            cal_gains_lower = list(cal[lower_freq].keys())
            cal_refs_lower = list(cal[lower_freq].values())

            cal_gains_upper = list(cal[upper_freq].keys())
            cal_refs_upper = list(cal[upper_freq].values())

            gain_lower = np.interp(ref_level, cal_refs_lower, cal_gains_lower)
            gain_upper = np.interp(ref_level, cal_refs_upper, cal_gains_upper)

            gain_bounds = [gain_lower, gain_upper]
            freq_bounds = [lower_freq, upper_freq]

            gain = np.interp(freq, freq_bounds, gain_bounds)

            freq = self.freq
            set_freq_cmd = pmt.make_dict()
            set_freq_cmd = pmt.dict_add(set_freq_cmd, pmt.to_pmt('freq'), pmt.to_pmt(freq))
            self.message_port_pub(pmt.intern("gain_msg"), set_freq_cmd)

            time.sleep(0.1)

            set_gain_cmd = pmt.make_dict()
            set_gain_cmd = pmt.dict_add(set_gain_cmd, pmt.to_pmt('gain'), pmt.to_pmt(gain))
            self.message_port_pub(pmt.intern("gain_msg"), set_gain_cmd)

            

        else:
            # May need to do something else when gain calibration table
            # is not selected. Keeping this here for now.
            pass
