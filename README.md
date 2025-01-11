# gr-pdw: GNU Radio Pulse Descriptor Word (PDW) Blocks

This module contains blocks to generate pulse descriptor words (PDW) in GNU Radio. PDWs are measurements of pulse properties and can include:
* Pulse width
* Pulse power
* Pulse frequency
* Time of Arrival
* Polarization
* Pulse Angle of Arrival
* Many others

Pull requests are very welcome as well as feature requests and bug reports.

## Quick Start

Dependencies required:

* GNU Radio
* UHD: For PDW Generation from SDR
* h5py: Logging PDW measurements to file

To install from source:

    $ git clone https://github.com/gtri/gr-pdw
    $ cd gr-pdw
    $ mkdir build; cd build
    $ cmake ..
    $ make
    $ make install

Steps may vary slightly depending on how your particular GNU Radio environment is setup.

Generate Pulse Generator Heir Block:

* Open GNU Radio Companion (GRC)
* Load the Pulse Generator Flowgraph: gr-pdw/examples/pulse_gen_heir.grc
* Generate / Run the Flowgraph

## Contents

* Blocks
  * pulse_detect: Performs pulse detection and tags start/stop of pulse.
  * pulse_extract: Extracts pulse I/Q and makes pulse measurements
  * pdw_to_file: Writes PDW measurements to file.
  * pdw_plot: Real time plots of PDW measurements
  * usrp_power_cal_table: Gain calibration for USRP pulse power measurements.
  * virtual_power_cal_table: Virtual gain calibration of simulated PDW flowgraphs.

### SDR Support
gr-pdw is agnostic to the SDR being used in **UNCALIBRATED** modes. That is, pulse power measurements will be in units of dBfs instead of dBm.

For **CALIBRATED** pulse power measurements, gr-pdw has been tested with the USRP B2xx series SDR. A calibration table is provided for these SDRs.

## Examples

### Flowgraphs
    gr-pdw/apps

* virtual_pdw.grc 
  * Simulated pulse generation and measurements.

* usrp_pdw.grc
  * PDW measurements with a USRP B210 SDR

### Hier Blocks
    gr-pdw/examples
* pulse_gen_heir.grc
  * Generates pulses based on input pulse width, pulse amplitude, and pulse repetition interval (PRI)

### Scripts
    gr-pdw/examples
* read_pdw_file_example.py
  * Example script to read PDW file in hdf5 format.
* test_pdw.hdf5
  * Example PDW file

## Roadmap

* Port blocks to C++ to improve performance with regards to sample rate, long pulse, and high PRI scenarios
* Improved plotting / visualization tools
* Improved PDW file manipulation tools
* Modulation detection
* Pulse I/Q data export
* PDW Streaming over a network
* Firmware / RFNoC PDW Generation (High bandwidth or embedded modes)
* PDW Replay
