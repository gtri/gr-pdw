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

class virtual_power_cal_table(gr.sync_block):
    """
    docstring for block virtual_power_cal_table
    """
    def __init__(self, freq, ref_level):
        gr.sync_block.__init__(self,
            name="virtual_power_cal_table",
            in_sig=None,
            out_sig=None)
        
        self.freq = freq
        self.ref_level = ref_level

        self.message_port_register_out(pmt.intern("ref_level_msg"))

    def start(self):
        # GNU Radio calls start on each block at start of flowgraph
        # Need this to emit a single gain calculation message for the
        # default parameters
        self.send_ref_msg()
        return True
    
    def stop(self):
        return True
    
    def ref_changed(self, value):
        self.ref_level = value
        self.send_ref_msg()
        
    def send_ref_msg(self):
        set_ref_level_cmd = pmt.make_dict()
        set_ref_level_cmd = pmt.dict_add(set_ref_level_cmd, pmt.to_pmt('ref_level'), pmt.to_pmt(self.ref_level))
        self.message_port_pub(pmt.intern("ref_level_msg"), set_ref_level_cmd)

    def freq_changed(self, value):
        self.freq = value