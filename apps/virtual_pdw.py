#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: SDR PDW Generator
# Author: GTRI
# GNU Radio version: 3.10.10.0

from PyQt5 import Qt
from gnuradio import qtgui
import os
import sys
sys.path.append(os.environ.get('GRC_HIER_PATH', os.path.expanduser('~/.grc_gnuradio')))

from PyQt5 import QtCore
from gnuradio import analog
from gnuradio import blocks
from gnuradio import gr
from gnuradio.filter import firdes
from gnuradio.fft import window
import signal
from PyQt5 import Qt
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from pulses import pulses  # grc-generated hier_block
import pdw
import sip
import threading



class virtual_pdw(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "SDR PDW Generator", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("SDR PDW Generator")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except BaseException as exc:
            print(f"Qt GUI: Could not set Icon: {str(exc)}", file=sys.stderr)
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

        self.settings = Qt.QSettings("gnuradio/flowgraphs", "virtual_pdw")

        try:
            geometry = self.settings.value("geometry")
            if geometry:
                self.restoreGeometry(geometry)
        except BaseException as exc:
            print(f"Qt GUI: Could not restore geometry: {str(exc)}", file=sys.stderr)
        self.flowgraph_started = threading.Event()

        ##################################################
        # Variables
        ##################################################
        self.threshold = threshold = 0.1
        self.sq_amp = sq_amp = 1
        self.samp_rate = samp_rate = 1e6
        self.ref_level = ref_level = -10
        self.pw = pw = 5
        self.pulse_freq = pulse_freq = 0
        self.pri = pri = 1e-3
        self.plotUpdateRate = plotUpdateRate = 0.1
        self.numPlotItems = numPlotItems = 250
        self.maxItemsUpdate = maxItemsUpdate = 10
        self.freq = freq = 1e9

        ##################################################
        # Blocks
        ##################################################

        self._threshold_range = qtgui.Range(0, 1, 0.01, 0.1, 200)
        self._threshold_win = qtgui.RangeWidget(self._threshold_range, self.set_threshold, "Pulse Threshold", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._threshold_win, 3, 2, 1, 1)
        for r in range(3, 4):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(2, 3):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._sq_amp_range = qtgui.Range(0, 1, 0.01, 1, 200)
        self._sq_amp_win = qtgui.RangeWidget(self._sq_amp_range, self.set_sq_amp, "Pulse Amplitude", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._sq_amp_win, 0, 2, 1, 1)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(2, 3):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._pw_range = qtgui.Range(1, 200, 0.1, 5, 200)
        self._pw_win = qtgui.RangeWidget(self._pw_range, self.set_pw, "Pulse Width (us)", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._pw_win, 1, 2, 1, 1)
        for r in range(1, 2):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(2, 3):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._pulse_freq_range = qtgui.Range(-samp_rate/2, samp_rate/2, 10e3, 0, 200)
        self._pulse_freq_win = qtgui.RangeWidget(self._pulse_freq_range, self.set_pulse_freq, "Pulse Freq (Hz)", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._pulse_freq_win, 2, 2, 1, 1)
        for r in range(2, 3):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(2, 3):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._pri_range = qtgui.Range(1e-3, 50e-3, 1e-3, 1e-3, 200)
        self._pri_win = qtgui.RangeWidget(self._pri_range, self.set_pri, "PRI", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._pri_win, 4, 2, 1, 1)
        for r in range(4, 5):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(2, 3):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.qtgui_time_sink_x_0 = qtgui.time_sink_f(
            1024, #size
            samp_rate, #samp_rate
            "", #name
            2, #number of inputs
            None # parent
        )
        self.qtgui_time_sink_x_0.set_update_time(0.10)
        self.qtgui_time_sink_x_0.set_y_axis(-1, 1)

        self.qtgui_time_sink_x_0.set_y_label('Amplitude', "")

        self.qtgui_time_sink_x_0.enable_tags(True)
        self.qtgui_time_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_NORM, qtgui.TRIG_SLOPE_POS, 0.2, 0, 0, "")
        self.qtgui_time_sink_x_0.enable_autoscale(False)
        self.qtgui_time_sink_x_0.enable_grid(False)
        self.qtgui_time_sink_x_0.enable_axis_labels(True)
        self.qtgui_time_sink_x_0.enable_control_panel(True)
        self.qtgui_time_sink_x_0.enable_stem_plot(False)


        labels = ['Signal 1', 'Signal 2', 'Signal 3', 'Signal 4', 'Signal 5',
            'Signal 6', 'Signal 7', 'Signal 8', 'Signal 9', 'Signal 10']
        widths = [2, 2, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ['blue', 'red', 'green', 'black', 'cyan',
            'magenta', 'yellow', 'dark red', 'dark green', 'dark blue']
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]
        styles = [1, 2, 1, 1, 1,
            1, 1, 1, 1, 1]
        markers = [-1, -1, -1, -1, -1,
            -1, -1, -1, -1, -1]


        for i in range(2):
            if len(labels[i]) == 0:
                self.qtgui_time_sink_x_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_time_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_0.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_0.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_0.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_0.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_0.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_0_win = sip.wrapinstance(self.qtgui_time_sink_x_0.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_time_sink_x_0_win)
        self.pulses_0 = pulses(
            a=sq_amp,
            pri=pri,
            pulse_width=(pw*(1e-6)),
            samp_rate=samp_rate,
        )
        self.pdw_virtual_power_cal_table_0 = pdw.virtual_power_cal_table(freq, ref_level)
        self.pdw_pulse_extract_0 = pdw.pulse_extract(samp_rate)
        self.pdw_pulse_detect_0 = pdw.pulse_detect(threshold, samp_rate)
        self.pdw_pdw_to_file_0 = pdw.pdw_to_file('/home/jhumphries33/sdr/git/gr-pdw/examples/test_pdw.hdf5', samp_rate, 1000, True)
        self.pdw_pdw_plot_0_0_0 = _pdw_plot_pdw_pdw_plot_0_0_0 = pdw.pdw_plot('', 'FREQ', [(-samp_rate/2)/1e6, ( samp_rate/2)/1e6], maxItemsUpdate, numPlotItems, plotUpdateRate, "white", "white", "red", self)
        self.pdw_pdw_plot_0_0_0 = _pdw_plot_pdw_pdw_plot_0_0_0

        self.top_grid_layout.addWidget(_pdw_plot_pdw_pdw_plot_0_0_0, 4, 1, 4, 1)
        for r in range(4, 8):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(1, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.pdw_pdw_plot_0_0 = _pdw_plot_pdw_pdw_plot_0_0 = pdw.pdw_plot('', 'WIDTH', [], maxItemsUpdate, numPlotItems, plotUpdateRate, "white", "white", "red", self)
        self.pdw_pdw_plot_0_0 = _pdw_plot_pdw_pdw_plot_0_0

        self.top_grid_layout.addWidget(_pdw_plot_pdw_pdw_plot_0_0, 4, 0, 4, 1)
        for r in range(4, 8):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.pdw_pdw_plot_0 = _pdw_plot_pdw_pdw_plot_0 = pdw.pdw_plot('', 'POWER', [-60,0], maxItemsUpdate, numPlotItems, plotUpdateRate, "white", "white", "red", self)
        self.pdw_pdw_plot_0 = _pdw_plot_pdw_pdw_plot_0

        self.top_grid_layout.addWidget(_pdw_plot_pdw_pdw_plot_0, 0, 0, 4, 2)
        for r in range(0, 4):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.blocks_throttle2_0 = blocks.throttle( gr.sizeof_gr_complex*1, samp_rate, True, 0 if "auto" == "auto" else max( int(float(0.1) * samp_rate) if "auto" == "time" else int(0.1), 1) )
        self.blocks_multiply_xx_0 = blocks.multiply_vcc(1)
        self.blocks_complex_to_mag_0 = blocks.complex_to_mag(1)
        self.blocks_add_xx_0 = blocks.add_vcc(1)
        self.analog_sig_source_x_0 = analog.sig_source_c(samp_rate, analog.GR_COS_WAVE, pulse_freq, 1, 0, 0)
        self.analog_fastnoise_source_x_0 = analog.fastnoise_source_c(analog.GR_GAUSSIAN, 0.01, 0, 8192)


        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.pdw_pulse_extract_0, 'pulse_data'), (self.pdw_pdw_plot_0, 'pdw'))
        self.msg_connect((self.pdw_pulse_extract_0, 'pulse_data'), (self.pdw_pdw_plot_0_0, 'pdw'))
        self.msg_connect((self.pdw_pulse_extract_0, 'pulse_data'), (self.pdw_pdw_plot_0_0_0, 'pdw'))
        self.msg_connect((self.pdw_pulse_extract_0, 'pulse_data'), (self.pdw_pdw_to_file_0, 'pdw_in'))
        self.msg_connect((self.pdw_virtual_power_cal_table_0, 'ref_level_msg'), (self.pdw_pulse_extract_0, 'set_ref_level'))
        self.connect((self.analog_fastnoise_source_x_0, 0), (self.blocks_add_xx_0, 1))
        self.connect((self.analog_sig_source_x_0, 0), (self.blocks_multiply_xx_0, 0))
        self.connect((self.blocks_add_xx_0, 0), (self.pdw_pulse_detect_0, 0))
        self.connect((self.blocks_complex_to_mag_0, 0), (self.qtgui_time_sink_x_0, 0))
        self.connect((self.blocks_multiply_xx_0, 0), (self.blocks_throttle2_0, 0))
        self.connect((self.blocks_throttle2_0, 0), (self.blocks_add_xx_0, 0))
        self.connect((self.pdw_pulse_detect_0, 0), (self.blocks_complex_to_mag_0, 0))
        self.connect((self.pdw_pulse_detect_0, 0), (self.pdw_pulse_extract_0, 0))
        self.connect((self.pdw_pulse_detect_0, 1), (self.qtgui_time_sink_x_0, 1))
        self.connect((self.pulses_0, 0), (self.blocks_multiply_xx_0, 1))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("gnuradio/flowgraphs", "virtual_pdw")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

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
        self.blocks_throttle2_0.set_sample_rate(self.samp_rate)
        self.pulses_0.set_samp_rate(self.samp_rate)
        self.qtgui_time_sink_x_0.set_samp_rate(self.samp_rate)

    def get_ref_level(self):
        return self.ref_level

    def set_ref_level(self, ref_level):
        self.ref_level = ref_level
        self.pdw_virtual_power_cal_table_0.ref_changed(self.ref_level)

    def get_pw(self):
        return self.pw

    def set_pw(self, pw):
        self.pw = pw
        self.pulses_0.set_pulse_width((self.pw*(1e-6)))

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

    def get_plotUpdateRate(self):
        return self.plotUpdateRate

    def set_plotUpdateRate(self, plotUpdateRate):
        self.plotUpdateRate = plotUpdateRate

    def get_numPlotItems(self):
        return self.numPlotItems

    def set_numPlotItems(self, numPlotItems):
        self.numPlotItems = numPlotItems

    def get_maxItemsUpdate(self):
        return self.maxItemsUpdate

    def set_maxItemsUpdate(self, maxItemsUpdate):
        self.maxItemsUpdate = maxItemsUpdate

    def get_freq(self):
        return self.freq

    def set_freq(self, freq):
        self.freq = freq
        self.pdw_virtual_power_cal_table_0.freq_changed(self.freq)




def main(top_block_cls=virtual_pdw, options=None):

    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()

    tb.start()
    tb.flowgraph_started.set()

    tb.show()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    qapp.exec_()

if __name__ == '__main__':
    main()
