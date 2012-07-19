#!/usr/bin/env python
#
# Copyright 2008 Free Software Foundation, Inc.
#
# This file is part of GNU Radio
#
# GNU Radio is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
#
# GNU Radio is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with GNU Radio; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
# MODIFIER PAR ZITOUNI RAFIK

from __future__ import division
from gnuradio import gr, eng_notation, uhd
from optparse import OptionParser
from gnuradio.eng_option import eng_option
from receive_path import receive_path

import gnuradio.gr.gr_threading as _threading
import sys, time

import wx
import wx.grid as gridl
import InterfaceRecepteur

n2s = eng_notation.num_to_str  


class interface_thread (_threading.Thread):
    def __init__(self, sizer, tb = None, options = None):
        _threading.Thread.__init__(self)
        self.setDaemon(1)
        self.sizer = sizer
        self.done = False 
        self.options = options
        self.tb = tb
        self.start()
        
    def run(self):
        app = wx.App() 
        self.fenetre = InterfaceRecepteur.Fenetre(sizer, None, -1, 'Evaluation de performances des transmissions BERT', self.tb, self.options)      
        app.MainLoop()  

    
  
class status_thread(_threading.Thread):
    def __init__(self, tb):
        _threading.Thread.__init__(self)
        self.setDaemon(1) 
        self.tb = tb  
        #self.condition = condition
        self.done = False 
        self.start() 

    def run(self):
        while not self.done:
            #print "Estimated SNR: %4.1f dB  BER: %g" % ( tb.snr(), tb.ber())       
            print "Estimated SNR: %f dB  BER: %f" % ( tb.snr(), tb.ber())           
            try:
                time.sleep(1.0)
            except KeyboardInterrupt:
                self.done = True

class rx_bpsk_block(gr.top_block):
    def __init__(self, options):    

        gr.top_block.__init__(self, "rx_mpsk")

        # Create a USRP source at desired board, sample rate, frequency, and gain
        self._setup_usrp(options)
 
        self._receiver = receive_path(options)
        
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
        
    def snr(self):
        return self._receiver.snr()

    def ber(self):
        return self._receiver.ber()
    
    def kill(self):
        del self
            
def get_options():
    parser = OptionParser(option_class=eng_option)
    
    parser.add_option("-a", "--address", type="string", default="addr=192.168.10.2", 
                       help="Address of UHD device, [default=%default]") 
        
    parser.add_option("-S", "--samples-per-symbol", type = "float", default=2,
                          help="set samples/symbol [default=%default]")
    
    parser.add_option("-s", "--samp-rate", type="eng_float", default=0.5e6,
                      help="Select modulation sample rate (default=%default)")
    
    parser.add_option("-r", "--data-rate", type="eng_float", default=250e3,
                      help="Select modulation symbol rate (default=%default)")

    parser.add_option("-f", "--freq", type="eng_float", default=2480000000,
                      help="set frequency to FREQ", metavar="FREQ")
    
    parser.add_option ("-g", "--gain", type="eng_float", default=40,
                       help="set Rx PGA gain in dB [0,20]")
        
    parser.add_option("-v", "--verbose", action ="store_true", default=False)
    
    #####################################
    
    parser.add_option("-w", "--which", type="int", default=0,
                      help="select which USRP (0, 1, ...) (default is %default)",
                      metavar="NUM")
    parser.add_option("-R", "--rx-subdev-spec", type="subdev", default=None,
                      help="select USRP Rx side A or B (default=first one with a daughterboard)")
    
    
    parser.add_option("", "--excess-bw", type="eng_float", default=0.35,
                      help="Select RRC excess bandwidth (default=%default)")
    parser.add_option("", "--costas-alpha", type="eng_float", default=0.05,
                      help="set Costas loop 1st order gain, (default=%default)")
    parser.add_option("", "--costas-beta", type="eng_float", default=0.00025,
                      help="set Costas loop 2nd order gain, (default=%default)")
    parser.add_option("", "--costas-max", type="eng_float", default=0.05,
                      help="set Costas loop max freq (rad/sample) (default=%default)")
    parser.add_option("", "--mm-gain-mu", type="eng_float", default=0.001,
                      help="set M&M loop 1st order gain, (default=%default)")
    parser.add_option("", "--mm-gain-omega", type="eng_float", default=0.000001,
                      help="set M&M loop 2nd order gain, (default=%default)")
    parser.add_option("", "--mm-omega-limit", type="eng_float", default=0.0001,
                      help="set M&M max timing error, (default=%default)")

		      
    (options, args) = parser.parse_args()
    if len(args) != 0:
        parser.print_help()
        sys.exit(1)
	
    if options.freq == None:
        print "You must supply a frequency with -f or --freq"
        sys.exit(1)

    return (options, args)


if __name__ == "__main__":
    
    (options, args) = get_options()

    tb = rx_bpsk_block(options)
    
    print "\n*** SNR estimator is inaccurate below about 7dB"
    print "*** BER estimator is inaccurate above about 10%\n"
     
    #status = status_thread(tb)
    sizer = wx.GridBagSizer()
    
    status = status_thread(tb)
    
    interface = interface_thread(sizer, tb, options) 
    try:
        tb.run() 
    except KeyboardInterrupt:
        status.done = True
        status = None

