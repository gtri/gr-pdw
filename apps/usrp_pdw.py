#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: USRP PDW
# Author: GTRI
# GNU Radio version: v3.8.5.0-6-g57bd109d

from gnuradio import blocks
from gnuradio import gr
from gnuradio.filter import firdes
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import uhd
import time
from gnuradio import zeromq
import pdw


class usrp_pdw(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self, "USRP PDW")

        ##################################################
        # Variables
        ##################################################
        self.threshold = threshold = 0.2
        self.sq_amp = sq_amp = 0.5
        self.samp_rate = samp_rate = 1e6
        self.rx_gain = rx_gain = 30
        self.pw = pw = 1e-6
        self.pulse_freq = pulse_freq = 0
        self.pri = pri = 100e-6
        self.freq = freq = 2.8e9

        ##################################################
        # Blocks
        ##################################################
        self.zeromq_pull_msg_source_0 = zeromq.pull_msg_source("tcp://127.0.0.1:5556", 100, False)
        self.zeromq_pub_msg_sink_0 = zeromq.pub_msg_sink("tcp://*:5555", 100, True)
        self.uhd_usrp_source_0 = uhd.usrp_source(
            ",".join(("type=b200", "")),
            uhd.stream_args(
                cpu_format="fc32",
                args='',
                channels=list(range(0,1)),
            ),
        )
        self.uhd_usrp_source_0.set_center_freq(freq, 0)
        self.uhd_usrp_source_0.set_gain(rx_gain, 0)
        self.uhd_usrp_source_0.set_antenna('RX2', 0)
        self.uhd_usrp_source_0.set_samp_rate(samp_rate)
        self.uhd_usrp_source_0.set_time_unknown_pps(uhd.time_spec())
        self.pdw_usrp_power_cal_table_0 = pdw.usrp_power_cal_table(True, freq, -20)
        self.pdw_remote_controller_0 = pdw.remote_controller('sk')
        self.pdw_pulse_extract_0 = pdw.pulse_extract(samp_rate)
        self.pdw_pulse_detect_0 = pdw.pulse_detect(threshold, samp_rate, 3)
        self.pdw_pdw_to_file_0 = pdw.pdw_to_file('pdw_log.bin', samp_rate, 10000, False)
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_float*1)


        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.pdw_pulse_extract_0, 'pulse_data'), (self.pdw_pdw_to_file_0, 'pdw_in'))
        self.msg_connect((self.pdw_pulse_extract_0, 'pulse_data'), (self.zeromq_pub_msg_sink_0, 'in'))
        self.msg_connect((self.pdw_remote_controller_0, 'settings'), (self.pdw_pdw_to_file_0, 'settings'))
        self.msg_connect((self.pdw_remote_controller_0, 'settings'), (self.pdw_pulse_detect_0, 'settings'))
        self.msg_connect((self.pdw_remote_controller_0, 'settings'), (self.pdw_pulse_extract_0, 'settings'))
        self.msg_connect((self.pdw_remote_controller_0, 'settings'), (self.pdw_usrp_power_cal_table_0, 'settings'))
        self.msg_connect((self.pdw_usrp_power_cal_table_0, 'ref_level_msg'), (self.pdw_pulse_extract_0, 'set_ref_level'))
        self.msg_connect((self.pdw_usrp_power_cal_table_0, 'gain_msg'), (self.uhd_usrp_source_0, 'command'))
        self.msg_connect((self.zeromq_pull_msg_source_0, 'out'), (self.pdw_remote_controller_0, 'remote_msg'))
        self.connect((self.pdw_pulse_detect_0, 1), (self.blocks_null_sink_0, 0))
        self.connect((self.pdw_pulse_detect_0, 0), (self.pdw_pulse_extract_0, 0))
        self.connect((self.uhd_usrp_source_0, 0), (self.pdw_pulse_detect_0, 0))


    def get_threshold(self):
        return self.threshold

    def set_threshold(self, threshold):
        self.threshold = threshold
        self.pdw_pulse_detect_0.threshold_changed(self.threshold)

    def get_sq_amp(self):
        return self.sq_amp

    def set_sq_amp(self, sq_amp):
        self.sq_amp = sq_amp

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.uhd_usrp_source_0.set_samp_rate(self.samp_rate)

    def get_rx_gain(self):
        return self.rx_gain

    def set_rx_gain(self, rx_gain):
        self.rx_gain = rx_gain
        self.uhd_usrp_source_0.set_gain(self.rx_gain, 0)

    def get_pw(self):
        return self.pw

    def set_pw(self, pw):
        self.pw = pw

    def get_pulse_freq(self):
        return self.pulse_freq

    def set_pulse_freq(self, pulse_freq):
        self.pulse_freq = pulse_freq

    def get_pri(self):
        return self.pri

    def set_pri(self, pri):
        self.pri = pri

    def get_freq(self):
        return self.freq

    def set_freq(self, freq):
        self.freq = freq
        self.pdw_usrp_power_cal_table_0.freq_changed(self.freq)
        self.uhd_usrp_source_0.set_center_freq(self.freq, 0)





def main(top_block_cls=usrp_pdw, options=None):
    tb = top_block_cls()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        sys.exit(0)

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    tb.start()

    try:
        input('Press Enter to quit: ')
    except EOFError:
        pass
    tb.stop()
    tb.wait()


if __name__ == '__main__':
    main()
