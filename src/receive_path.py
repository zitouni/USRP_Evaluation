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
#

from gnuradio import eng_notation
from gnuradio import gr
from gnuradio.eng_option import eng_option
from gnuradio.gr import firdes
from gnuradio.wxgui import numbersink2
from gnuradio.wxgui import scopesink2
from grc_gnuradio import blks2 as grc_blks2
from grc_gnuradio import usrp as grc_usrp
from grc_gnuradio import wxgui as grc_wxgui
from optparse import OptionParser
import wx
import math

n2s = eng_notation.num_to_str

class receive_path(gr.hier_block2, grc_wxgui.top_block_gui):
    def __init__(self,
                 if_rate,        # Incoming sample rate
                 symbol_rate,    # Original symbol rate
                 excess_bw,      # RRC excess bandwidth, typically 0.35-0.5
                 costas_alpha,   # Costas loop 1st order gain, typically 0.01-0.2
                 costas_beta,    # Costas loop 2nd order gain, typically alpha^2/4.0
                 costas_max,     # Costas loop max frequency offset in radians/sample
                 mm_gain_mu,     # M&M loop 1st order gain, typically 0.001-0.2
                 mm_gain_omega,  # M&M loop 2nd order gain, typically alpha^2/4.0
                 mm_omega_limit, # M&M loop max timing error
                 ):
        
        gr.hier_block2.__init__(self, "receive_path",
                                gr.io_signature(1, 1, gr.sizeof_gr_complex), # Input signature
                                gr.io_signature(0, 0, 0))                    # Output signature
        
        grc_wxgui.top_block_gui.__init__(self, title="Top Block")
        
        self._if_rate = if_rate
        self._sps = int(self._if_rate/symbol_rate)
        print "IF sample rate:", n2s(self._if_rate)
        print "Symbol rate:", n2s(symbol_rate)
        print "Samples/symbol:", self._sps
        print "RRC bandwidth:", excess_bw
        
        # Create AGC to scale input to unity
        self._agc = gr.agc_cc(1e-5, 1.0, 1.0, 1.0)

	# Create RRC with specified excess bandwidth
	taps = gr.firdes.root_raised_cosine(1.0,          # Gain
					    self._sps,    # Sampling rate
					    1.0,          # Symbol rate
					    excess_bw,    # Roll-off factor
					    11*self._sps) # Number of taps

	self._rrc = gr.fir_filter_ccf(1, taps)
        
        # Create a Costas loop frequency/phase recovery block

        print "Costas alpha:", costas_alpha
        print "Costas beta:", costas_beta
        print "Costas max:", costas_max
        
        self._costas = gr.costas_loop_cc(costas_alpha,  # PLL first order gain
                                         costas_beta,   # PLL second order gain
                                         costas_max,    # Max frequency offset rad/sample
                                         -costas_max,   # Min frequency offset rad/sample
                                         2)             # BPSK

        # Create a M&M bit synchronization retiming block
        mm_mu = 0.5
        mm_omega = self._sps

        print "MM gain mu:", mm_gain_mu
        print "MM gain omega:", mm_gain_omega
        print "MM omega limit:", mm_omega_limit
        
        self._mm = gr.clock_recovery_mm_cc(mm_omega,       # Initial samples/symbol
                                           mm_gain_omega,  # Second order gain
                                           mm_mu,          # Initial symbol phase
                                           mm_gain_mu,     # First order gain
                                           mm_omega_limit) # Maximum timing offset

        # Add an SNR probe on the demodulated constellation
        self._snr_probe = gr.probe_mpsk_snr_c(10.0/symbol_rate)
        
#        #Null for recuperate the out of snr
#        self.gr_null_sink_0 = gr.null_sink(gr.sizeof_double)
#        
#        self.connect(self._snr_probe, (self.gr_null_sink_0,0))
        
        self.connect(self._mm, self._snr_probe)
        
        # Slice the resulting constellation into bits.
        # Get inphase channel and make decision about 0
        self._c2r = gr.complex_to_real()
        self._slicer = gr.binary_slicer_fb() 
        
        # Descramble BERT sequence.  A channel error will create 3 incorrect bits
        self._descrambler = gr.descrambler_bb(0x8A, 0x7F, 7) # CCSDS 7-bit descrambler

        # Measure BER by the density of 0s in the stream
        self._ber = gr.probe_density_b(1.0/symbol_rate)
        
#        #Null for recuperate the out of ber
#        self.gr_null_sink_1 = gr.null_sink(gr.sizeof_double)
#        
#        self.connect(self._ber, self.gr_null_sink_1)
        
        self.create_number_sink(self._sps)
        self.connect((self._snr_probe, 0), (self.wxgui_numbersink2_0, 0))
        self.connect((self._ber, 0), (self.wxgui_numbersink2_1, 0))

        self.connect(self, self._agc, self._rrc, self._costas, self._mm, 
                     self._c2r, self._slicer, self._descrambler, self._ber)

    def frequency_offset(self):
        return self._costas.freq()*self._if_rate/(2*math.pi)

    def timing_offset(self):
        return self._mm.omega()/self._sps-1.0

    def snr(self):
        return self._snr_probe.snr()

    def ber(self):
        #print "ber : ", (1.0-self._ber.density())/3.0
        print "ber: %g"%(self._ber.ber_stream_1()/1.0)
        #print "ber : ", (self._ber.ber())
        
        return (1-self._ber.density())
        #return self._ber.ber_stream_1()/1.0
        #return (1.0-self._ber.density())/3.0
    
    def create_number_sink (self, sps):   
        self.wxgui_numbersink2_1 = numbersink2.number_sink_f(
            self.GetWin(),
            unit="Units",
            minval=-100,
            maxval=100,
            factor=1.0,
            decimal_places=10,
            ref_level=0,
            sample_rate=sps,
            number_rate=15,
            average=False,
            avg_alpha=None,
            label="BER",
            peak_hold=False,
            show_gauge=True,
        )
        self.Add(self.wxgui_numbersink2_1.win)
        self.wxgui_numbersink2_0 = numbersink2.number_sink_f(
            self.GetWin(),
            unit="Units",
            minval=-100,
            maxval=100,
            factor=1.0,
            decimal_places=10,
            ref_level=0,
            sample_rate=sps,
            number_rate=15,
            average=False,
            avg_alpha=None,
            label="SNR",
            peak_hold=False,
            show_gauge=True,
        )
        self.Add(self.wxgui_numbersink2_0.win)
