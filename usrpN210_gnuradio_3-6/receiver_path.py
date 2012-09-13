#!/usr/bin/env python
'''
Created on july, 2012
#
#@author: zitouni
#'''

from gnuradio import gr, eng_notation, uhd
from gnuradio.eng_option import eng_option

#from bpsk_demodulator import bpsk_demodulator

from bpsk_demodulator import bpsk_demodulator

class receiver_path(gr.top_block):
    def __init__(self, options):    

        gr.top_block.__init__(self, "rx_mpsk")

        # Create a USRP source at desired board, sample rate, frequency, and gain
        self._setup_usrp(options)
 
        self._receiver = bpsk_demodulator(options)
        
        self.connect(self._usrp, self._receiver)


    def _setup_usrp(self, options):
        print "******************************************************Reception parameters***************************"
        print "USRP Adress: ", options.address
        print "Transmission Freqeuncy: ", eng_notation.num_to_str(options.freq)
        print "Sample rate or (Freqeuncy Sampling): ", eng_notation.num_to_str(options.samp_rate)
        print "Samples per symbol: ", options.samples_per_symbol
        print "Data rate : ", eng_notation.num_to_str(options.data_rate)
        print "Gain  : ", options.gain
        print "*******************************************************Reception parameters************************"
                        
        self.data_rate = options.data_rate
        self.samples_per_symbol = options.samples_per_symbol
        
        samp_rate= options.samp_rate
        
        u = uhd.usrp_source(
            device_addr=options.address, 
            stream_args=uhd.stream_args(
            cpu_format="fc32",
            channels=range(1),
            ),
        )
        u.set_subdev_spec("A:0", 0)
        u.set_samp_rate(samp_rate)
        u.set_center_freq(options.freq, 0)
        u.set_gain(options.gain, 0)
        
        self._usrp = u
    
    def get_compare_vector_decision(self):
        return self._receiver.get_compare_vector_decision()
    
    def set_compare_vector_decision(self, decision):
        self._receiver.set_compare_vector_decision(decision)
    
    def get_comparator_vector_number(self):
        return self._receiver.get_comparator_vector_number()
       
    def snr(self):
        return self._receiver.snr()

    def ber(self):
        return self._receiver.ber()
    
    def kill(self):
        del self