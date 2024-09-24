#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Not titled yet
# Author: jhumphries33
# GNU Radio version: v3.8.5.0-6-g57bd109d

from distutils.version import StrictVersion

if __name__ == '__main__':
    import ctypes
    import sys
    if sys.platform.startswith('linux'):
        try:
            x11 = ctypes.cdll.LoadLibrary('libX11.so')
            x11.XInitThreads()
        except:
            print("Warning: failed to XInitThreads()")

import os
import sys
sys.path.append(os.environ.get('GRC_HIER_PATH', os.path.expanduser('~/.grc_gnuradio')))

from PyQt5 import Qt
from gnuradio import eng_notation
from gnuradio import qtgui
from gnuradio.filter import firdes
import sip
from gnuradio import analog
from gnuradio import blocks
import pmt
from gnuradio import gr
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import zeromq
from gnuradio.qtgui import Range, RangeWidget
from pulses import pulses  # grc-generated hier_block
import pdw

from gnuradio import qtgui

class thold_test(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Not titled yet")
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Not titled yet")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except:
            pass
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("GNU Radio", "thold_test")

        try:
            if StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
                self.restoreGeometry(self.settings.value("geometry").toByteArray())
            else:
                self.restoreGeometry(self.settings.value("geometry"))
        except:
            pass

        ##################################################
        # Variables
        ##################################################
        self.pw = pw = 1e-6
        self.variable_qtgui_label_0 = variable_qtgui_label_0 = pw
        self.threshold = threshold = 0.2
        self.sq_amp = sq_amp = 0.5
        self.samp_rate = samp_rate = 10e6
        self.ref_level = ref_level = -10
        self.pulse_freq = pulse_freq = 0
        self.pri = pri = 100e-6
        self.freq = freq = 1e9

        ##################################################
        # Blocks
        ##################################################
        self._threshold_range = Range(0, 1, 0.01, 0.2, 200)
        self._threshold_win = RangeWidget(self._threshold_range, self.set_threshold, 'Pulse Threshold', "counter_slider", float)
        self.top_layout.addWidget(self._threshold_win)
        self._sq_amp_range = Range(0, 1, 0.01, 0.5, 200)
        self._sq_amp_win = RangeWidget(self._sq_amp_range, self.set_sq_amp, 'sq_amp', "counter_slider", float)
        self.top_layout.addWidget(self._sq_amp_win)
        self._pw_range = Range(0.1e-6, 10e-6, 0.1e-6, 1e-6, 200)
        self._pw_win = RangeWidget(self._pw_range, self.set_pw, 'Pulse Width', "slider", float)
        self.top_layout.addWidget(self._pw_win)
        self._pulse_freq_range = Range(-samp_rate/2, samp_rate/2, 100e3, 0, 200)
        self._pulse_freq_win = RangeWidget(self._pulse_freq_range, self.set_pulse_freq, 'Pulse Freq', "counter_slider", float)
        self.top_layout.addWidget(self._pulse_freq_win)
        self._pri_range = Range(10e-6, 500e-6, 1e-6, 100e-6, 200)
        self._pri_win = RangeWidget(self._pri_range, self.set_pri, 'PRI', "counter_slider", float)
        self.top_layout.addWidget(self._pri_win)
        self.zeromq_pull_msg_source_0 = zeromq.pull_msg_source("tcp://127.0.0.1:5556", 100, False)
        self.zeromq_pub_msg_sink_0 = zeromq.pub_msg_sink("tcp://*:5555", 100, True)
        self._variable_qtgui_label_0_tool_bar = Qt.QToolBar(self)

        if None:
            self._variable_qtgui_label_0_formatter = None
        else:
            self._variable_qtgui_label_0_formatter = lambda x: eng_notation.num_to_str(x)

        self._variable_qtgui_label_0_tool_bar.addWidget(Qt.QLabel('variable_qtgui_label_0' + ": "))
        self._variable_qtgui_label_0_label = Qt.QLabel(str(self._variable_qtgui_label_0_formatter(self.variable_qtgui_label_0)))
        self._variable_qtgui_label_0_tool_bar.addWidget(self._variable_qtgui_label_0_label)
        self.top_layout.addWidget(self._variable_qtgui_label_0_tool_bar)
        self.qtgui_time_sink_x_0_1_1 = qtgui.time_sink_f(
            4096, #size
            samp_rate, #samp_rate
            "", #name
            1 #number of inputs
        )
        self.qtgui_time_sink_x_0_1_1.set_update_time(0.10)
        self.qtgui_time_sink_x_0_1_1.set_y_axis(-1, 1)

        self.qtgui_time_sink_x_0_1_1.set_y_label('Amplitude', "")

        self.qtgui_time_sink_x_0_1_1.enable_tags(True)
        self.qtgui_time_sink_x_0_1_1.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.qtgui_time_sink_x_0_1_1.enable_autoscale(False)
        self.qtgui_time_sink_x_0_1_1.enable_grid(False)
        self.qtgui_time_sink_x_0_1_1.enable_axis_labels(True)
        self.qtgui_time_sink_x_0_1_1.enable_control_panel(True)
        self.qtgui_time_sink_x_0_1_1.enable_stem_plot(False)


        labels = ['Signal 1', 'Signal 2', 'Signal 3', 'Signal 4', 'Signal 5',
            'Signal 6', 'Signal 7', 'Signal 8', 'Signal 9', 'Signal 10']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ['blue', 'red', 'green', 'black', 'cyan',
            'magenta', 'yellow', 'dark red', 'dark green', 'dark blue']
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]
        styles = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        markers = [-1, -1, -1, -1, -1,
            -1, -1, -1, -1, -1]


        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_time_sink_x_0_1_1.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_time_sink_x_0_1_1.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_0_1_1.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_0_1_1.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_0_1_1.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_0_1_1.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_0_1_1.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_0_1_1_win = sip.wrapinstance(self.qtgui_time_sink_x_0_1_1.pyqwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_time_sink_x_0_1_1_win)
        self.qtgui_time_sink_x_0_1 = qtgui.time_sink_c(
            4096, #size
            samp_rate, #samp_rate
            "", #name
            1 #number of inputs
        )
        self.qtgui_time_sink_x_0_1.set_update_time(0.10)
        self.qtgui_time_sink_x_0_1.set_y_axis(-1, 1)

        self.qtgui_time_sink_x_0_1.set_y_label('Amplitude', "")

        self.qtgui_time_sink_x_0_1.enable_tags(True)
        self.qtgui_time_sink_x_0_1.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.qtgui_time_sink_x_0_1.enable_autoscale(False)
        self.qtgui_time_sink_x_0_1.enable_grid(False)
        self.qtgui_time_sink_x_0_1.enable_axis_labels(True)
        self.qtgui_time_sink_x_0_1.enable_control_panel(True)
        self.qtgui_time_sink_x_0_1.enable_stem_plot(False)


        labels = ['Signal 1', 'Signal 2', 'Signal 3', 'Signal 4', 'Signal 5',
            'Signal 6', 'Signal 7', 'Signal 8', 'Signal 9', 'Signal 10']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ['blue', 'red', 'green', 'black', 'cyan',
            'magenta', 'yellow', 'dark red', 'dark green', 'dark blue']
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]
        styles = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        markers = [-1, -1, -1, -1, -1,
            -1, -1, -1, -1, -1]


        for i in range(2):
            if len(labels[i]) == 0:
                if (i % 2 == 0):
                    self.qtgui_time_sink_x_0_1.set_line_label(i, "Re{{Data {0}}}".format(i/2))
                else:
                    self.qtgui_time_sink_x_0_1.set_line_label(i, "Im{{Data {0}}}".format(i/2))
            else:
                self.qtgui_time_sink_x_0_1.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_0_1.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_0_1.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_0_1.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_0_1.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_0_1.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_0_1_win = sip.wrapinstance(self.qtgui_time_sink_x_0_1.pyqwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_time_sink_x_0_1_win)
        self.pulses_0 = pulses(
            a=sq_amp,
            pri=pri,
            pulse_width=pw,
            samp_rate=samp_rate,
        )
        self.pdw_virtual_power_cal_table_0 = pdw.virtual_power_cal_table(freq, ref_level)
        self.pdw_remote_controller_0 = pdw.remote_controller('sk')
        self.pdw_pulse_extract_0 = pdw.pulse_extract(samp_rate)
        self.pdw_pulse_detect_0 = pdw.pulse_detect(threshold, samp_rate, 3)
        self.pdw_pdw_to_file_0 = pdw.pdw_to_file('pdw_log.bin', samp_rate, 10000, False)
        self.blocks_throttle_0 = blocks.throttle(gr.sizeof_gr_complex*1, samp_rate,True)
        self.blocks_multiply_xx_0 = blocks.multiply_vcc(1)
        self.blocks_message_strobe_0 = blocks.message_strobe(pmt.intern("TEST"), 1000)
        self.blocks_message_debug_0_0 = blocks.message_debug()
        self.blocks_message_debug_0 = blocks.message_debug()
        self.blocks_add_xx_0 = blocks.add_vcc(1)
        self.analog_sig_source_x_0 = analog.sig_source_c(samp_rate, analog.GR_COS_WAVE, pulse_freq, 1, 0, 0)
        self.analog_fastnoise_source_x_0 = analog.fastnoise_source_c(analog.GR_GAUSSIAN, 0.05, 0, 8192)


        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.blocks_message_strobe_0, 'strobe'), (self.blocks_message_debug_0, 'print'))
        self.msg_connect((self.pdw_pulse_extract_0, 'pulse_data'), (self.blocks_message_strobe_0, 'set_msg'))
        self.msg_connect((self.pdw_pulse_extract_0, 'pulse_data'), (self.pdw_pdw_to_file_0, 'pdw_in'))
        self.msg_connect((self.pdw_pulse_extract_0, 'pulse_data'), (self.zeromq_pub_msg_sink_0, 'in'))
        self.msg_connect((self.pdw_remote_controller_0, 'settings'), (self.blocks_message_debug_0, 'print'))
        self.msg_connect((self.pdw_remote_controller_0, 'settings'), (self.blocks_message_debug_0_0, 'print'))
        self.msg_connect((self.pdw_remote_controller_0, 'settings'), (self.pdw_pdw_to_file_0, 'settings'))
        self.msg_connect((self.pdw_remote_controller_0, 'settings'), (self.pdw_pulse_detect_0, 'settings'))
        self.msg_connect((self.pdw_remote_controller_0, 'settings'), (self.pdw_pulse_extract_0, 'settings'))
        self.msg_connect((self.pdw_remote_controller_0, 'settings'), (self.pdw_virtual_power_cal_table_0, 'settings'))
        self.msg_connect((self.pdw_virtual_power_cal_table_0, 'ref_level_msg'), (self.pdw_pulse_extract_0, 'set_ref_level'))
        self.msg_connect((self.zeromq_pull_msg_source_0, 'out'), (self.pdw_remote_controller_0, 'remote_msg'))
        self.connect((self.analog_fastnoise_source_x_0, 0), (self.blocks_add_xx_0, 1))
        self.connect((self.analog_sig_source_x_0, 0), (self.blocks_multiply_xx_0, 0))
        self.connect((self.blocks_add_xx_0, 0), (self.pdw_pulse_detect_0, 0))
        self.connect((self.blocks_multiply_xx_0, 0), (self.blocks_throttle_0, 0))
        self.connect((self.blocks_throttle_0, 0), (self.blocks_add_xx_0, 0))
        self.connect((self.pdw_pulse_detect_0, 0), (self.pdw_pulse_extract_0, 0))
        self.connect((self.pdw_pulse_detect_0, 0), (self.qtgui_time_sink_x_0_1, 0))
        self.connect((self.pdw_pulse_detect_0, 1), (self.qtgui_time_sink_x_0_1_1, 0))
        self.connect((self.pulses_0, 0), (self.blocks_multiply_xx_0, 1))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "thold_test")
        self.settings.setValue("geometry", self.saveGeometry())
        event.accept()

    def get_pw(self):
        return self.pw

    def set_pw(self, pw):
        self.pw = pw
        self.set_variable_qtgui_label_0(self._variable_qtgui_label_0_formatter(self.pw))
        self.pulses_0.set_pulse_width(self.pw)

    def get_variable_qtgui_label_0(self):
        return self.variable_qtgui_label_0

    def set_variable_qtgui_label_0(self, variable_qtgui_label_0):
        self.variable_qtgui_label_0 = variable_qtgui_label_0
        Qt.QMetaObject.invokeMethod(self._variable_qtgui_label_0_label, "setText", Qt.Q_ARG("QString", self.variable_qtgui_label_0))

    def get_threshold(self):
        return self.threshold

    def set_threshold(self, threshold):
        self.threshold = threshold
        self.pdw_pulse_detect_0.threshold_changed(self.threshold)

    def get_sq_amp(self):
        return self.sq_amp

    def set_sq_amp(self, sq_amp):
        self.sq_amp = sq_amp
        self.pulses_0.set_a(self.sq_amp)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.analog_sig_source_x_0.set_sampling_freq(self.samp_rate)
        self.blocks_throttle_0.set_sample_rate(self.samp_rate)
        self.pulses_0.set_samp_rate(self.samp_rate)
        self.qtgui_time_sink_x_0_1.set_samp_rate(self.samp_rate)
        self.qtgui_time_sink_x_0_1_1.set_samp_rate(self.samp_rate)

    def get_ref_level(self):
        return self.ref_level

    def set_ref_level(self, ref_level):
        self.ref_level = ref_level
        self.pdw_virtual_power_cal_table_0.ref_changed(self.ref_level)

    def get_pulse_freq(self):
        return self.pulse_freq

    def set_pulse_freq(self, pulse_freq):
        self.pulse_freq = pulse_freq
        self.analog_sig_source_x_0.set_frequency(self.pulse_freq)

    def get_pri(self):
        return self.pri

    def set_pri(self, pri):
        self.pri = pri
        self.pulses_0.set_pri(self.pri)

    def get_freq(self):
        return self.freq

    def set_freq(self, freq):
        self.freq = freq
        self.pdw_virtual_power_cal_table_0.freq_changed(self.freq)





def main(top_block_cls=thold_test, options=None):

    if StrictVersion("4.5.0") <= StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
        style = gr.prefs().get_string('qtgui', 'style', 'raster')
        Qt.QApplication.setGraphicsSystem(style)
    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()

    tb.start()

    tb.show()

    def sig_handler(sig=None, frame=None):
        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    def quitting():
        tb.stop()
        tb.wait()

    qapp.aboutToQuit.connect(quitting)
    qapp.exec_()

if __name__ == '__main__':
    main()
