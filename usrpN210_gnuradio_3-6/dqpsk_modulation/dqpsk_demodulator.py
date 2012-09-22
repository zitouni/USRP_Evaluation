'''
Created on Sep 13, 2012

@author: zitouni
'''

from gnuradio import gr, ucla, digital
from grc_gnuradio import blks2 as grc_blks2
from math import pi

import howto

class dqpsk_demodulator(gr.hier_block2):
    def __init__(self, options):
        """
        Hierarchical block for DQPSK demodulation.
        
        The input is the complex modulated signal at baseband
        and the output is a stream of bytes.
        
        @param sps: samples per symbol
        @type sps: integer
        """ 
        
        gr.hier_block2.__init__(self, "dqpsk_demodulator",
                gr.io_signature(1, 1, gr.sizeof_gr_complex), # Input
                gr.io_signature(0, 0, 0))  # Output
        
        self.sps = options.samples_per_symbol
        
        self.dqpsk_demod = digital.psk_demod(
          constellation_points=4,
          differential=True,
          samples_per_symbol=self.sps,
          excess_bw=0.35,
          phase_bw=(6.28)/100.0,
          timing_bw=(6.28)/100.0,
          gray_coded="gray",
          verbose=False,
          log=False,
          )
        
        self.gr_null_sink_f = gr.null_sink(gr.sizeof_float*1)
        
        self._vector_source_ref = gr.vector_source_b(([1,]), True, 1)
        #create a comparator 
        self.comparator = howto.compare_vector_cci((1, 1, 1, 1 ,0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1), (0,0, 1, 1, 0,0), 5, 0, True)
        
        self._ber = grc_blks2.error_rate(type='SER', 
                                         win_size=1000,
                                         bits_per_symbol=1)
        
        self.connect(self, self.dqpsk_demod, self.comparator, (self._ber,0))
        
        self.connect(self._vector_source_ref, (self._ber,1))
        self.connect(self._ber, self.gr_null_sink_f)
        
        
                                            
    
    def get_compare_vector_decision(self):
        return self.comparator.is_same_vector_decision
    
    def set_compare_vector_decision(self, decision):
        self.comparator.is_same_vector_decision = decision
        
    def get_comparator_vector_number(self):
        return self.comparator.is_same_vector_number

    def snr(self):
        #return self._snr_probe.snr()
        return 0

    def ber(self):
        ratio = float(7.0/8.0)
        return (ratio - self._ber.ber_)       
        
