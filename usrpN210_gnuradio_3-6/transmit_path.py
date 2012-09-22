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
# MODIFIER PAR RAFIK ZITOUNI     

from gnuradio import gr, eng_notation, uhd
from gnuradio.eng_option import eng_option

import howto
#from bpsk_modulator import bpsk_modulator
from bpsk_modulation import bpsk_modulator
from oqpsk_modulation import oqpsk_modulator  
from dqpsk_modulation import dqpsk_modulator

class transmit_path(gr.top_block):
    def __init__(self, options, state_mod):    
        gr.top_block.__init__(self, "tx_mpsk")
        
        self.options = options
        self.state_mod = state_mod
    
        self.vector_source = gr.vector_source_b([1], True)
        
        self._modulator = self.construct_transmitter(self.options, self.state_mod, self.vector_source)
        
        self._setup_usrp(options)
    
        self.connect(self._modulator, self._usrp)

    def construct_transmitter(self, options, state_mod, vector_source, amplitude =None):
       
        if amplitude is not None :
            self.amplitude = amplitude
        else :
            self.amplitude = options.amplitude
              
        if (state_mod == 1) :
            #Modulation technique is BPSK
            modulator = bpsk_modulator.bpsk_modulator(options.sps,
                                          options.excess_bw,
                                          self.amplitude, self.vector_source)
        if (state_mod == 2):
            #Modulation technique is OQPSK
            modulator = oqpsk_modulator.oqpsk_modulator(options.sps,
                                          options.excess_bw,
                                          self.amplitude, self.vector_source)
        
        if (state_mod == 3):
            #Modulation technique is DQPSK
            modulator = dqpsk_modulator.dqpsk_modulator(options.sps,
                                        options.excess_bw, self.amplitude, self.vector_source)
        
        return modulator 

        
    def _setup_usrp(self, options):
        """
        Creates a USRP sink, determines the settings for best bitrate,
        and attaches to the transmitter's subdevice.
        """
        #self.u = usrp_options.create_usrp_sink(options)
        
        #self.u.set_interp_rate(self._interp)
        #print "interpolation : ",  self._interp     
        self._samples_per_symbol = options.sps
        samp_rate= options.samp_rate
        
        self.rs_rate = options.rate    # Store requested bit rat
        print "*******************************************************Transmission Parameters************************"
        print "USRP Adress: ", options.address
        print "Transmission Freqeuncy: ", eng_notation.num_to_str(options.freq)
        print "Sample rate or (Freqeuncy Sampling): ", eng_notation.num_to_str(options.samp_rate)
        print "Samples per symbol: ", options.sps
        print "data rate : ",  eng_notation.num_to_str(options.rate)
        print "Gain  : ", options.gain
        print "Amplitude : ", options.amplitude
        print "*******************************************************Transmission Parameters************************"

        
        #Configuration of USRP by UHD Driver

        self.u = uhd.usrp_sink(
            device_addr=options.address,
            stream_args=uhd.stream_args(
                cpu_format="fc32",
                channels=range(1),
            ),
        )
        
        self.u.set_subdev_spec("A:0", 0)
        self.u.set_samp_rate(samp_rate)
        self.u.set_center_freq(options.freq, 0)
        self.u.set_gain(options.gain, 0)
        
        self._usrp = self.u
        
    def changeOptionsTransmitter(self, options, state_mod):
        
        #self.state_mod to choose which modulation
        self.state_mod = state_mod
        #disconnect the current tranmitter from the usrp
        self.disconnect(self._modulator, self._usrp)
        
        self.vector_source = gr.vector_source_b([1], True)
        
        self._modulator = self.construct_transmitter(self.options, self.state_mod, self.vector_source)
        
        self.connect(self._modulator, self._usrp)
    
    def changeOptionsTransmitterWithVectorCode(self, options, state_mod):
        #disconnect the current tranmitter from the usrp
        self.state_mod = state_mod
        
        self.disconnect(self._modulator, self._usrp)
        
        self.vector_source = howto.vector_source2(( 1, 1, 1, 1 ,0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1), (0,0,1,1,0,0), True, True, 1)
        #self.vector_source = gr.vector_source_b([1, 0, 0, 0 ,0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], True) 
        
        #send vector with high amplitude
        self.amplitude = 1
        
        self._modulator = self.construct_transmitter(self.options, self.state_mod, self.vector_source, self.amplitude)
       
        self.connect(self._modulator, self._usrp)
        
    def kill(self):
        self.stop()
        self.disconnect_all()
        self._transmitter = None
        self._usrp = None
        del self

                