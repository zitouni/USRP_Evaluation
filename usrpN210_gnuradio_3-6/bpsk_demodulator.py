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
from gnuradio import gr, digital
from gnuradio.eng_option import eng_option
from gnuradio.gr import firdes
from gnuradio.wxgui import numbersink2
from gnuradio.wxgui import scopesink2
from grc_gnuradio import blks2 as grc_blks2

from grc_gnuradio import wxgui as grc_wxgui
from optparse import OptionParser
import wx
import math

import howto 

n2s = eng_notation.num_to_str

class bpsk_demodulator(gr.hier_block2, grc_wxgui.top_block_gui):
    def __init__(self, options):
        
        gr.hier_block2.__init__(self, "receive_path",
                                gr.io_signature(1, 1, gr.sizeof_gr_complex), # Input signature
                                gr.io_signature(0, 0, 0))                    # Output signature
        
        grc_wxgui.top_block_gui.__init__(self, title="Top Block")
        
        self._samples_per_symbol = options.samples_per_symbol
        # Create AGC to scale input to unity
        self._agc = gr.agc_cc(1e-5, 1.0, 1.0, 1.0)
        # Create RRC with specified excess bandwidth
        taps = gr.firdes.root_raised_cosine(1.0,       # Gain
					    self._samples_per_symbol,      # Sampling rate
					    1.0,                           # Symbol rate
					    0.35,                          # Roll-off factor
					    11*self._samples_per_symbol)                  # Number of taps
        
        self._rrc = gr.fir_filter_ccf(1, taps)
        
        # Create a Costas loop frequency/phase recovery block
        self._costas = digital.costas_loop_cc(6.28/100.0, 2)
        self.gr_null_sink = gr.null_sink(gr.sizeof_float*1)
        self.connect((self._costas, 1), (self.gr_null_sink, 0))
        
        
        # Create a M&M bit synchronization retiming block        
        self._mm = digital.clock_recovery_mm_cc(self._samples_per_symbol,       # Initial samples/symbol
                                           1e-06,  # Second order gain
                                           0.5,          # Initial symbol phase
                                           0.001,     # First order gain
                                           0.0001) # Maximum timing offset
        
        # Add an SNR probe on the demodulated constellation
        #self._snr_probe = gr.probe_mpsk_snr_c(10.0/symbol_rate)
        self._snr_probe = digital.mpsk_snr_est_cc(0, 10000, 0.001) # 0 at the first mean Simple
        
#        #Null for recuperate the out of snr


        self.gr_null_sink = gr.null_sink(gr.sizeof_gr_complex*1)
    
        # Slice the resulting constellation into bits.
        # Get inphase channel and make decision about 0
        self._c2r = gr.complex_to_real()
        self._slicer = digital.binary_slicer_fb() 
        
        # Descramble BERT sequence.  A channel error will create 3 incorrect bits
        self._descrambler = gr.descrambler_bb(0x8A, 0x7F, 31) # CCSDS 7-bit descrambler

        # Measure BER by the density of 0s in the stream
        # self._ber = gr.probe_density_b(1.0/symbol_rate)
        self._ber = grc_blks2.error_rate(type='BER', 
                                         win_size=1000,
                                         bits_per_symbol=1)
        
        self.create_number_sink(self._samples_per_symbol)
        
        #Create a vector source reference to calculate BER
        self._vector_source_ref = gr.vector_source_b(([1,]), True, 1)
        
        #create a comparator 
        self.comparator = howto.compare_vector_cci((1, 1, 1, 1 ,0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1), (0,0, 1, 1, 0,0), 5, 0, True)
        
        
        #Connection of blocks
        #"""""""""""""""""""""""""""""""""""""""""""""""""""""
        # agc --> _rrc --> costas --> _mm --> _c2r --> _slicer --> _descrambler --> _ber --> wxgui_numbersink
        #"""""""""""""""""""""""""""""""""--> gr_null_sink "" _vector_source_ref-->
        
        self.connect(self._vector_source_ref, (self._ber,0)) 

        self.connect(self, self._agc, self._rrc, self._costas, self._mm, 
                     self._c2r, self._slicer, self._descrambler, self.comparator, (self._ber, 1))
        
        self.connect(self._ber, self.wxgui_numbersink)
        
        self.connect(self._mm, self._snr_probe, self.gr_null_sink)
    
    
    
    def get_compare_vector_decision(self):
        return self.comparator.is_same_vector_decision
    
    def set_compare_vector_decision(self, decision):
        self.comparator.is_same_vector_decision = decision
        
    def get_comparator_vector_number(self):
        return self.comparator.is_same_vector_number

    def snr(self):
        return self._snr_probe.snr()

    def ber(self):
        return self._ber.ber_
    
    def create_number_sink (self, samp_rate):   
        self.wxgui_numbersink = numbersink2.number_sink_f(
            self.GetWin(),
            unit="Units",
            minval=-100,
            maxval=100,
            factor=1.0,
            decimal_places=10,
            ref_level=0,
            sample_rate=samp_rate,
            number_rate=15,
            average=False,
            avg_alpha=None,
            label="SNR",
            peak_hold=False,
            show_gauge=True,
        )
        self.Add(self.wxgui_numbersink.win)
