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
import math
from gnuradio import gr
import pmt
from datetime import datetime
import time

class pulse_extract(gr.sync_block):
    """
    docstring for block pulse_extract
    """
    def __init__(self, fs: float=None):
        gr.sync_block.__init__(self,
            name="pulse_extract",
            in_sig=[np.complex64, ],
            out_sig=None)
        
        self.fs = fs
        self.ref_level = 0
        
        self.message_port_register_out(pmt.intern("pulse_data"))

        self.message_port_register_in(pmt.intern("set_ref_level"))
        self.set_msg_handler(pmt.intern("set_ref_level"), self.set_ref_level)

        self.start_time = int(time.time())

    def work(self, input_items, output_items):
        in0 = input_items[0]

        all_tags = self.get_tags_in_window(0,0, len(in0))

        if (len(all_tags)) == 0:
            return len(input_items[0])

        burst_msg = pmt.make_dict()
        p_idx = 0
        for idx, pdw_tag in enumerate(all_tags):
            if (idx==0) and (pmt.to_python(pdw_tag.key) == "pdw_eob"):
                pass

            else:
                if (pmt.to_python(pdw_tag.key) == "pdw_eob"):
                    eob_offset = pdw_tag.offset - self.nitems_read(0)
                    sob_offset = all_tags[idx-1].offset - self.nitems_read(0)

                    data = in0[sob_offset:eob_offset]

                    noise_guard = 3
                    noise_window = 7
                    noise_iq = in0[eob_offset+noise_guard:eob_offset+noise_guard+noise_window]

                    sob_v = float(pmt.to_python(all_tags[idx-1].value))
                    eob_v = float(pmt.to_python(pdw_tag.value))

                    pdw = self.measure_pulse(sob_v, eob_v, data, noise_iq)

                    pdw_dict = pmt.make_dict()
                    pdw_dict = pmt.dict_add(pdw_dict, pmt.intern('pdw'), pmt.to_pmt(pdw))
                    burst_msg = pmt.dict_add(burst_msg, pmt.to_pmt(p_idx), pdw_dict)

                    p_idx += 1

        self.message_port_pub(pmt.intern('pulse_data'), burst_msg)

        return len(input_items[0])
 
        
    def measure_pulse(self, time_sob, time_eob, iq, iq_noise):
        # Generate pulse measurements
        pw_time = time_eob - time_sob
        pw_cycles = int(round(pw_time * self.fs))

        # Course Time of Arrival
        # Whole second of the time of burst (second without factional part)
        course_toa = math.floor(time_sob) + int(time.time()) #self.start_time

        # Fine Time of Arrival
        # Number of clock cycles (in this case samples) since the 
        # last whole second. (Fractional part of time of burst)
        fine_toa = time_sob % 1 # Fractional part of sob time
        fine_toa = round(self.fs * fine_toa) # Number of samples since last second

        # Calculate dbfs (This will need to be calibrated to power
        # based on SDR gain, frequency, and reference level)
        i_mid = int(len(iq)/2)
        sample = iq[i_mid]

        pulse_power_adc = int(((np.abs(sample)+1e-15)**2)*(2**32)-1)
        dbfs = 20 * np.log10(np.abs(sample)+1e-15)
        pulse_power = dbfs + self.ref_level

        num_bits = 32
        scale = 10*np.log10(1/(2**num_bits))
        
        # Find noise power in dBfs    
        noise_power = np.abs(iq_noise)		

        if len(iq_noise) > 0:

            dbfs_noise = 10*np.log10(noise_power[-1])
            dBm_noise = dbfs_noise + self.ref_level

        else:
            # Quick fix for the case of pulse extending
            # beyond buffer.
            dbfs_noise = -100
            dBm_noise = -100
     
        # Calculate frequency content of signal
        num_zeros = 128
        padded_iq = np.pad(iq, (num_zeros, num_zeros), mode='constant')
        
        X = np.fft.fft(padded_iq)
        X = np.fft.fftshift(X)
        X_abs = np.abs(X)
      
        N = len(padded_iq)
        f = np.arange(-self.fs/2, self.fs/2, self.fs/N)
        
        peak_freq_index = np.argmax(X_abs)
        peak_freq = f[peak_freq_index]	

        
        pdw = {
            'pw_time': pw_time,
            'pw_clock': pw_cycles,
            'dbfs': dbfs,
            'dbfs_noise': dbfs_noise,
            'pulse_power_adc': pulse_power_adc,
            'pulse_power': pulse_power,
            'noise_power_ave': dBm_noise,
            'power_scale': (self.ref_level+scale),
            'ref_lvl': self.ref_level,
            'toa': time_sob,
            'course_toa': course_toa,
            'fine_toa': fine_toa,
            'start_freq': peak_freq,
            'stop_freq': 0e6,
            'freq_fabric': self.fs,
          	'iq_noise_length': len(iq_noise),
        }
          
        return pdw
    
    def set_ref_level(self, pmt_msg):
        ref_key = pmt.intern("ref_level")
        ref_level = pmt.to_python(pmt.dict_ref(pmt_msg, ref_key, pmt.PMT_NIL))
        self.ref_level = ref_level
