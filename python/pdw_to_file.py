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

import time
import datetime

import h5py

class pdw_to_file(gr.sync_block):
    """
    docstring for block pdw_to_file
    """
    def __init__(self, file_name, fs: float=None, buffer_size: int=10000, enabled: bool=False):
        gr.sync_block.__init__(self,
            name="pdw_to_file",
            in_sig=None,
            out_sig=None)
        
        self.file_name = file_name
        self.fs = fs

        self.np_buffer_size = buffer_size
        self.pdw_idx = 0

        # Enable / disable PDW logging
        # This should only be specified at runtime. Reference level can't change
        # while logging is in progress.
        self.enabled = enabled
        if self.enabled:
            # If enabled in GRC, enable run
            self.run = True
        else:
            # Disable run until run command is received (So this won't
            # keep logging after when not enabled)
            self.run = False

        # Once we get the first PDW:
        # Write Header to File
        self.got_first_pdw = False
        self.header_written = False

        self.np_first_buffer = True
        
        self.message_port_register_in(pmt.intern("pdw_in"))
        self.set_msg_handler(pmt.intern("pdw_in"), self.handle_pdw_msg)

        self.pdw_header = {
            'format_type': 0,
            'format_src': 0,
            'pdw_cv': 0,
            'time_unix': 0,
            'time_py': 0,
            'samp_rate': 0,
            'power_scale': 0,
            'ref_lvl': 0
        }

        time_unix = int(round(time.time()))
        self.pdw_header['time_unix'] = time_unix

        py_timestamp = datetime.datetime.utcfromtimestamp(time_unix).strftime('%Y-%m-%dT%H:%M:%SZ')
        self.pdw_header['time_py'] = py_timestamp

        self.pdw_header['samp_rate'] = self.fs

        self.np_buffer0 = np.zeros((self.np_buffer_size, 8))
        self.np_buffer1 = np.zeros((self.np_buffer_size, 8))

        self.first_write_done = False

    def stop(self):
        # When the flowgraph is stopped, write the active buffer to log file
        if self.enabled:
            self.buffer_to_file(buffer_select=self.np_first_buffer, final=True)
        return True
    
    def reset(self):
        # This will reset the file name, pdw header info as the logger is 
        # enabled / disabled. For now the logs get written to the same file
        # each time the flowgraph is run. (New log file created each time
        # flow graph run)
        pass


    def handle_pdw_msg(self, pmt_msg):
        if self.enabled and self.run:
            pdw_dict = pmt.to_python(pmt_msg)

            if isinstance(pdw_dict, dict):
            
                keys = list(pdw_dict.keys())
                keys.sort()
                for pdw_num in keys:
                    if pdw_dict[pdw_num]['pdw'] is None:
                        pass
                    else:
                        self.got_first_pdw = True
                        pdw_data = pdw_dict[pdw_num]['pdw']

                        self.pdw_header['power_scale'] = pdw_data['power_scale']
                        self.pdw_header['ref_level'] = pdw_data['ref_lvl']

                        fine_toa = pdw_data['fine_toa']
                        course_toa = pdw_data['course_toa']
                        pulse_pwr = pdw_data['pulse_power']
                        noise_pwr = pdw_data['noise_power_ave']
                        start_freq = pdw_data['start_freq']
                        stop_freq = pdw_data['stop_freq']
                        pulse_width = pdw_data['pw_clock']
                        pdw_channel = 0 # We don't specify channel yet

                        if self.np_first_buffer:
                            self.np_buffer0[self.pdw_idx, :] = np.array([pdw_channel, pulse_width, pulse_pwr, noise_pwr, start_freq, stop_freq, course_toa, fine_toa])
                        else:
                            self.np_buffer1[self.pdw_idx, :] = np.array([pdw_channel, pulse_width, pulse_pwr, noise_pwr, start_freq, stop_freq, course_toa, fine_toa])

                        self.pdw_idx += 1

                        if self.pdw_idx >= self.np_buffer_size:
                            self.buffer_to_file(buffer_select=self.np_first_buffer, final=False)
                            self.pdw_idx = 0
                            self.np_first_buffer = not(self.np_first_buffer)


    def buffer_to_file(self, buffer_select, final):

        if not self.first_write_done:
            self.first_write_done = True
            with h5py.File(self.file_name, 'w') as f:
                # Write attributes / header information
                f.attrs['time_unix'] = self.pdw_header['time_unix']
                f.attrs['time_py'] = self.pdw_header['time_py']
                f.attrs['samp_rate'] = self.pdw_header['samp_rate']
                f.attrs['ref_level'] = self.pdw_header['ref_level']

                # Write the first chunk of data
                f.create_dataset('pulse_width', data=self.np_buffer0[:,1], chunks=True, maxshape=(None,))
                f.create_dataset('pulse_power', data=self.np_buffer0[:,2], chunks=True, maxshape=(None,))
                f.create_dataset('noise_power', data=self.np_buffer0[:,3], chunks=True, maxshape=(None,))
                f.create_dataset('freq_start', data=self.np_buffer0[:,4], chunks=True, maxshape=(None,))
                f.create_dataset('toa_course', data=self.np_buffer0[:,6], chunks=True, maxshape=(None,))
                f.create_dataset('toa_fine', data=self.np_buffer0[:,7], chunks=True, maxshape=(None,))

        else:
            # Appending data in chunks
            with h5py.File(self.file_name, 'a') as f:
                if buffer_select:
                    f['pulse_width'].resize((f['pulse_width'].shape[0]+self.np_buffer0.shape[0]), axis=0)
                    f['pulse_width'][-self.np_buffer0.shape[0]:] = self.np_buffer0[:,1]

                    f['pulse_power'].resize((f['pulse_power'].shape[0]+self.np_buffer0.shape[0]), axis=0)
                    f['pulse_power'][-self.np_buffer0.shape[0]:] = self.np_buffer0[:,2]

                    f['noise_power'].resize((f['noise_power'].shape[0]+self.np_buffer0.shape[0]), axis=0)
                    f['noise_power'][-self.np_buffer0.shape[0]:] = self.np_buffer0[:,3]

                    f['freq_start'].resize((f['freq_start'].shape[0]+self.np_buffer0.shape[0]), axis=0)
                    f['freq_start'][-self.np_buffer0.shape[0]:] = self.np_buffer0[:,4]

                    f['toa_course'].resize((f['toa_course'].shape[0]+self.np_buffer0.shape[0]), axis=0)
                    f['toa_course'][-self.np_buffer0.shape[0]:] = self.np_buffer0[:,6]

                    f['toa_fine'].resize((f['toa_fine'].shape[0]+self.np_buffer0.shape[0]), axis=0)
                    f['toa_fine'][-self.np_buffer0.shape[0]:] = self.np_buffer0[:,7]

                else:
                    f['pulse_width'].resize((f['pulse_width'].shape[0]+self.np_buffer1.shape[0]), axis=0)
                    f['pulse_width'][-self.np_buffer1.shape[0]:] = self.np_buffer1[:,1]
       
                    f['pulse_power'].resize((f['pulse_power'].shape[0]+self.np_buffer1.shape[0]), axis=0)
                    f['pulse_power'][-self.np_buffer1.shape[0]:] = self.np_buffer1[:,2]

                    f['noise_power'].resize((f['noise_power'].shape[0]+self.np_buffer1.shape[0]), axis=0)
                    f['noise_power'][-self.np_buffer1.shape[0]:] = self.np_buffer1[:,3]

                    f['freq_start'].resize((f['freq_start'].shape[0]+self.np_buffer1.shape[0]), axis=0)
                    f['freq_start'][-self.np_buffer1.shape[0]:] = self.np_buffer1[:,4]

                    f['toa_course'].resize((f['toa_course'].shape[0]+self.np_buffer1.shape[0]), axis=0)
                    f['toa_course'][-self.np_buffer1.shape[0]:] = self.np_buffer1[:,6]

                    f['toa_fine'].resize((f['toa_fine'].shape[0]+self.np_buffer1.shape[0]), axis=0)
                    f['toa_fine'][-self.np_buffer1.shape[0]:] = self.np_buffer1[:,7]




    

