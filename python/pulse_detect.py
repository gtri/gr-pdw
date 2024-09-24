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

class pulse_detect(gr.sync_block):
    """
    docstring for block pulse_detect
    """
    def __init__(self, threshold: float=0, fs: float=None):
        gr.sync_block.__init__(self,
            name="pulse_detect",
            in_sig=[np.complex64, ],
            out_sig=[np.complex64, np.float32])

        self.threshold = threshold
        self.fs = fs

        thold_min = 0.0
        thold_max = 1.0
        if (threshold<thold_min) or (threshold>thold_max):
            raise RuntimeError("Threshold out of bounds (0,1)")

        self.found_start = False
        self.found_end = False
        self.pulse_len = 0

        self.found_last = False

    def set_ref_lvl(self, ref_level_dbm):
        self.ref_level = ref_level_dbm

    def work(self, input_items, output_items):
        
        in0 = input_items[0]
        thold_samps = in0

        thresh_idx = self.apply_threshold(np.abs(in0))

        thold_samps = np.abs(in0)

        found_pulse = False
        for idx in thresh_idx:
            
            if (thold_samps[idx] > 0) and (not found_pulse):
                value = (self.nitems_written(0) + idx) / self.fs
                self.add_item_tag(0, self.nitems_written(0) + idx, pmt.intern("pdw_sob"), pmt.intern(str(value)))
                found_pulse = True
            elif found_pulse:
                sub_idx = idx+1
                if sub_idx >= len(in0):
                    pass
                elif (thold_samps[sub_idx] < self.threshold):
                    value = (self.nitems_written(0) + idx) / self.fs
                    self.add_item_tag(0, self.nitems_written(0) + idx, pmt.intern("pdw_eob"), pmt.intern(str(value)))
                    found_pulse = False


        out = output_items[0]
        dt = output_items[1]
        out[:] = in0
        dt[:] = self.ediff(np.abs(in0))
        return len(output_items[0])
    
    def apply_threshold(self, samples):
        thold_idx = np.argwhere(samples > self.threshold)
        return thold_idx[:,0]     
    
    def threshold_changed(self, value):
        # Callback
        # Event: Threshold variable is changed
        self.threshold = value

    def ediff(self, samples):
        # Calculates 1st derivative of
        # magnitude of samples
        samples = np.abs(samples)
        dt_samples = np.ediff1d(samples)
        dt_samples = np.insert(dt_samples, 0, 0)
        return dt_samples


