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

class oqpsk_modulator(gr.hier_block2):
    def __init__(self, sps, excess_bw, amplitude, vector_source): 
        try:
            self.sps = 2
        except KeyError:
            pass
        
        gr.hier_block2.__init__(self, "OQPSK Modulator",
                                gr.io_signature(0, 0, 0),                     # Input 
                                gr.io_signature(1, 1, gr.sizeof_gr_complex))  # Output 
        
        if not isinstance(self.sps, int) or self.sps < 2: 
            raise TypeError, "sample per symbol  sps ou spb must be an integer >= 2"
        
        self.vector_source = vector_source
        
        self.symbolsToChips = ucla.symbols_to_chips_bi()
        
        self.chipsToSymbols = gr.packed_to_unpacked_ii(2, gr.GR_MSB_FIRST)
        
        #self.symbolsToConstellation = gr.chunks_to_symbols_ic((-1-1j, -1+1j, 1-1j, 1+1j))
        self.symbolsToConstellation = gr.chunks_to_symbols_bc((-1-1j, -1+1j, 1-1j, 1+1j))
        
        #self._scrambler = gr.scrambler_bb(0x8A, 0x7F, 31) # CCSDS 7-bit scrambler
        
        self.pskmod = ucla.qpsk_modulator_cc()
        
        self.delay = ucla.delay_cc(self.sps)
        
        self.amp = gr.multiply_const_cc(amplitude) 
        
        #self.connect(self.vector_source , self.symbolsToChips, self.chipsToSymbols, self.symbolsToConstellation, self.pskmod, self.delay, self.amp, self)
        
        #self.connect(self.vector_source , self._scrambler, self.symbolsToConstellation, self.pskmod, self.delay, self.amp, self)
        self.connect(self.vector_source, self.symbolsToConstellation, self.pskmod, self.delay, self.amp, self)
    
        #self.connect(self, self.symbolsToChips, self.chipsToSymbols, self.symbolsToConstellation, self.pskmod, self)