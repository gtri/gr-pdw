import zmq
import pmt
import time
import datetime
import signal

from matplotlib import pyplot as plt
from matplotlib.widgets import TextBox

TIME_SPAN = 10

class ExitHelper():
    def __init__(self):
        self.state = False
        signal.signal(signal.SIGINT, self.change_state)

    def change_state(self, signum, frame):
        # print("Receieved SIGINT from CTRL+C...signaling SDR manager to stop...")
        # logging.info("Receieved SIGINT from CTRL+C...signaling SDR manager to stop...")
        # rootLogger.info("Receieved SIGINT from CTRL+C...signaling SDR manager to stop...")
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        self.state = True

    def exit(self):
        return self.state
    
def submit(text):
    global TIME_SPAN
    TIME_SPAN = int(text)
    
exit_flag = ExitHelper()

fig, axs = plt.subplots(nrows=2, ncols=2)

# axbox = plt.axes([0.1, 0.05, 0.8, 0.075])
# text_box = TextBox(axbox, 'Evaluate', initial=str(TIME_SPAN))
# text_box.on_submit(submit)

print(axs)
pw_ax = axs[0][0]
pp_ax = axs[0][1]
np_ax = axs[1][0]
freq_ax = axs[1][1]
pw = []
pp = []
np = []
f_start = []
f_stop = []
pdw_time = []
# fig.show(block=False)
# fig.show()


t_start = time.time()
pdw_time_start = datetime.datetime.now()
pdw_time_stop = pdw_time_start + datetime.timedelta(seconds=TIME_SPAN)

while(True):

    if exit_flag.exit():
        break

    if not plt.fignum_exists(fig.number):
        break

    if time.time() - t_start >= TIME_SPAN:
        pw = []
        pp = []
        np = []
        f_start = []
        f_stop = []
        pdw_time = []
        pdw_time_start = datetime.datetime.now()
        pdw_time_stop = pdw_time_start + datetime.timedelta(seconds=TIME_SPAN)
        t_start = time.time()

    try:
        context = zmq.Context()

        socket = context.socket(zmq.SUB)
        socket.setsockopt( zmq.RCVTIMEO, 1000 )
        socket.setsockopt(zmq.SUBSCRIBE, b"") 
        socket.setsockopt(zmq.RCVHWM, 100)
        socket.setsockopt(zmq.LINGER, 0)

        socket.connect("tcp://localhost:5555")

        data = socket.recv()
    except zmq.error.Again:
        time.sleep(0.01)
    else:
        data = pmt.deserialize_str(data)
        data = pmt.to_python(data)
        # print(data)
        # plt.clf()
        pw_ax.clear()
        pp_ax.clear()
        np_ax.clear()
        freq_ax.clear()
        keys = list(data.keys())
        keys.sort()
        for pdw_num in keys:
        # for pdw_key in data:
            # print(data[pdw])
            # pdw = data[pdw_key]['pdw']
            pdw = data[pdw_num]['pdw']
            pw.append(pdw['pw_time']/1e-6)
            pp.append(pdw['pulse_power'])
            np.append(pdw['noise_power'])
            f_start.append(pdw['start_freq']/1e6)
            f_stop.append(pdw['stop_freq']/1e6)
            pdw_time.append(datetime.datetime.now())

            # course_time = pdw['course_toa']
            # fine_time = pdw['fine_toa']/pdw['freq_fabric']
            # ts = datetime.datetime.utcfromtimestamp(course_time + fine_time)
            # print(ts)
            # print(f"Course Time: {course_time}")
            # print(f"Fine Time: {fine_time}")
            # pdw_time.append(ts)

        pw_ax.scatter(pdw_time, pw)
        pw_ax.set_ylim([0, 10])
        pw_ax.set_xlim([pdw_time_start, pdw_time_stop])
        # pw_ax.set_xlim([pdw_time[0], pdw_time[0]+datetime.timedelta(seconds=TIME_SPAN)])
        pw_ax.set_ylabel("Pulse Width (us)")
        pw_ax.grid()

        # pp_ax.scatter(range(len(pp)), pp)
        pp_ax.scatter(pdw_time, pp)
        pp_ax.set_ylim([-40, 0])
        pp_ax.set_xlim([pdw_time_start, pdw_time_stop])
        # pp_ax.set_xlim([pdw_time[0], pdw_time[0]+datetime.timedelta(seconds=TIME_SPAN)])
        pp_ax.set_ylabel("Pulse Power (dBm)")
        pp_ax.grid()

        np_ax.scatter(pdw_time, np)
        np_ax.set_ylim([-80, 0])
        np_ax.set_xlim([pdw_time_start, pdw_time_stop])
        # np_ax.set_xlim([pdw_time[0], pdw_time[0]+datetime.timedelta(seconds=TIME_SPAN)])
        np_ax.set_ylabel("Noise Power (dBm)")
        np_ax.grid()

        freq_ax.scatter(pdw_time, f_start)
        freq_ax.scatter(pdw_time, f_stop)
        freq_ax.set_ylim([-5, 5])
        freq_ax.set_xlim([pdw_time_start, pdw_time_stop])
        # freq_ax.set_xlim([pdw_time[0], pdw_time[0]+datetime.timedelta(seconds=TIME_SPAN)])
        freq_ax.set_ylabel("Freq. (MHz)")
        freq_ax.grid()

        # plt.tight_layout()
        fig.suptitle("SK PDW Viewer", fontsize=16)
        fig.tight_layout(rect=[0, 0.03, 1, 0.95])
        plt.pause(0.01)
        socket.close()