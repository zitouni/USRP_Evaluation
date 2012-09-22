'''
Created on Sep 18, 2012

@author: zitouni
'''
'''
Created on Sep 12, 2012

@author: zitouni
'''

from gnuradio import gr, ucla, digital
from math import pi

class dqpsk_modulator(gr.hier_block2):
    def __init__(self, sps, excess_bw, amplitude, vector_source): 

        gr.hier_block2.__init__(self, "DQPSK Modulator",
                                gr.io_signature(0, 0, 0),                     # Input 
                                gr.io_signature(1, 1, gr.sizeof_gr_complex))  # Output 
        
        
        self.vector_source = vector_source
        
        self.dqpsk_mod = digital.psk_mod(constellation_points=4,
          mod_code="gray",
          differential=True,
          samples_per_symbol=sps,
          excess_bw=0.35,
          verbose=False,
          log=False,
          )
        
        self.amp = gr.multiply_const_cc(amplitude) 
            
        self.connect (self.vector_source, self.dqpsk_mod, self.amp, self)
    