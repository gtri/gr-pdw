
import h5py
import numpy as np

file_name = './test_pdw.hdf5'

with h5py.File(file_name, 'r') as f:

    print(f"Sample Rate: {f.attrs['samp_rate']}")
    print(f"Reference Level: {f.attrs['ref_level']}")
    print(f"Timestamp: {f.attrs['time_py']}")
    print(f"Unix Timestamp: {f.attrs['time_unix']}")

    pdw_pw = np.array(f['pulse_width'][:])
    pdw_pp = f['pulse_power'][:]
    pdw_np = f['noise_power'][:]
    pdw_pf = f['freq_start'][:]
    pdw_toa_course = f['toa_course'][:]
    pdw_toa_fine = f['toa_fine'][:]

print(pdw_pw)