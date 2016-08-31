#!/usr/bin/env python
##################################################
# Gnuradio Python Flow Graph
# Title: Usrp Fft
# Generated: Tue Feb  3 14:10:52 2015
#
#nodeX:
#   entry usrp_fft.py
#   params -T 'TX/RX' -G '25' -W '4M' -F '2.49G' -P '6663' -I 'srvwww.cortexlab.fr' -A '-110' -B '-60' -R '4M' -S '1024' -H '10'
#   passive true
#
#
##################################################

from fft_web import fft_web
from gnuradio import eng_notation
from gnuradio import gr
from gnuradio import uhd
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes
from optparse import OptionParser
import time

class usrp_fft(gr.top_block):

    def __init__(self, freq=2.49e9, samp_rate=1e6, gain=0, fft_size=1024, frame_rate=10, power_min=-100, power_max=0, port=7000, ip_address="srvwww.cortexlab.fr", antenna="TX/RX", bandwidth=0):
        gr.top_block.__init__(self, "Usrp Fft")

        ##################################################
        # Parameters
        ##################################################
        self.freq = freq
        self.samp_rate = samp_rate
        self.gain = gain
        self.fft_size = fft_size
        self.frame_rate = frame_rate
        self.power_min = power_min
        self.power_max = power_max
        self.port = port
        self.ip_address = ip_address
        self.antenna = antenna
        self.bandwidth = bandwidth

        ##################################################
        # Blocks
        ##################################################
        self.uhd_usrp_source_0 = uhd.usrp_source(
        	",".join(("addr=192.168.10.2", "")),
        	uhd.stream_args(
        		cpu_format="fc32",
        		channels=range(1),
        	),
        )
        self.uhd_usrp_source_0.set_clock_source("internal", 0)
        self.uhd_usrp_source_0.set_samp_rate(samp_rate)
        self.uhd_usrp_source_0.set_center_freq(freq, 0)
        self.uhd_usrp_source_0.set_gain(gain, 0)
        self.uhd_usrp_source_0.set_antenna(antenna, 0)
        self.fft_web_1 = fft_web(
            fft_size=fft_size,
            power_max=power_max,
            power_min=power_min,
            port=port,
            frame_rate=frame_rate,
            sample_rate=samp_rate,
            ip_address=ip_address,
        )

        ##################################################
        # Connections
        ##################################################
        self.connect((self.uhd_usrp_source_0, 0), (self.fft_web_1, 0))    


    def get_freq(self):
        return self.freq

    def set_freq(self, freq):
        self.freq = freq
        self.uhd_usrp_source_0.set_center_freq(self.freq, 0)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.uhd_usrp_source_0.set_samp_rate(self.samp_rate)
        self.fft_web_1.set_sample_rate(self.samp_rate)

    def get_gain(self):
        return self.gain

    def set_gain(self, gain):
        self.gain = gain
        self.uhd_usrp_source_0.set_gain(self.gain, 0)

    def get_fft_size(self):
        return self.fft_size

    def set_fft_size(self, fft_size):
        self.fft_size = fft_size
        self.fft_web_1.set_fft_size(self.fft_size)

    def get_frame_rate(self):
        return self.frame_rate

    def set_frame_rate(self, frame_rate):
        self.frame_rate = frame_rate
        self.fft_web_1.set_frame_rate(self.frame_rate)

    def get_power_min(self):
        return self.power_min

    def set_power_min(self, power_min):
        self.power_min = power_min
        self.fft_web_1.set_power_min(self.power_min)

    def get_power_max(self):
        return self.power_max

    def set_power_max(self, power_max):
        self.power_max = power_max
        self.fft_web_1.set_power_max(self.power_max)

    def get_port(self):
        return self.port

    def set_port(self, port):
        self.port = port
        self.fft_web_1.set_port(self.port)

    def get_ip_address(self):
        return self.ip_address

    def set_ip_address(self, ip_address):
        self.ip_address = ip_address
        self.fft_web_1.set_ip_address(self.ip_address)

    def get_antenna(self):
        return self.antenna

    def set_antenna(self, antenna):
        self.antenna = antenna
        self.uhd_usrp_source_0.set_antenna(self.antenna, 0)

    def get_bandwidth(self):
        return self.bandwidth

    def set_bandwidth(self, bandwidth):
        self.bandwidth = bandwidth
        self.uhd_usrp_source_0.set_bandwidth(self.bandwidth, 0)

if __name__ == '__main__':
    parser = OptionParser(option_class=eng_option, usage="%prog: [options]")
    parser.add_option("-F", "--freq", dest="freq", type="eng_float", default=eng_notation.num_to_str(2.49e9),
        help="Set freq [default=%default]")
    parser.add_option("-R", "--samp-rate", dest="samp_rate", type="eng_float", default=eng_notation.num_to_str(1e6),
        help="Set samp_rate [default=%default]")
    parser.add_option("-G", "--gain", dest="gain", type="eng_float", default=eng_notation.num_to_str(0),
        help="Set gain [default=%default]")
    parser.add_option("-S", "--fft-size", dest="fft_size", type="intx", default=1024,
        help="Set fft_size [default=%default]")
    parser.add_option("-H", "--frame-rate", dest="frame_rate", type="intx", default=10,
        help="Set frame_rate [default=%default]")
    parser.add_option("-A", "--power-min", dest="power_min", type="eng_float", default=eng_notation.num_to_str(-100),
        help="Set power_min [default=%default]")
    parser.add_option("-B", "--power-max", dest="power_max", type="eng_float", default=eng_notation.num_to_str(0),
        help="Set power_max [default=%default]")
    parser.add_option("-P", "--port", dest="port", type="intx", default=7000,
        help="Set port [default=%default]")
    parser.add_option("-I", "--ip-address", dest="ip_address", type="string", default="srvwww.cortexlab.fr",
        help="Set ip address [default=%default]")
    parser.add_option("-T", "--antenna", dest="antenna", type="string", default="TX/RX",
        help="Set TX/RX [default=%default]")
    parser.add_option("-W", "--bandwidth", dest="bandwidth", type="eng_float", default=eng_notation.num_to_str(0),
        help="Set bandwidth [default=%default]")
    (options, args) = parser.parse_args()
    tb = usrp_fft(freq=options.freq, samp_rate=options.samp_rate, gain=options.gain, fft_size=options.fft_size, frame_rate=options.frame_rate, power_min=options.power_min, power_max=options.power_max, port=options.port, ip_address=options.ip_address, antenna=options.antenna, bandwidth=options.bandwidth)
    tb.start()
    tb.wait()
