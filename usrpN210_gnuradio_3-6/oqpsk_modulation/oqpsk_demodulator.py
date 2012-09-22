'''
Created on Sep 13, 2012

@author: zitouni
'''

from gnuradio import gr, ucla, digital
from grc_gnuradio import blks2 as grc_blks2
from math import pi

import howto

class oqpsk_demodulator(gr.hier_block2):
    def __init__(self, options):
        """
        Hierarchical block for O-QPSK demodulation.
        
        The input is the complex modulated signal at baseband
        and the output is a stream of bytes.
        
        @param sps: samples per symbol
        @type sps: integer
        """ 
        try:
            #self.sps = kwargs.pop('sps')
            self.sps = 2
        except KeyError:
            pass
        
        gr.hier_block2.__init__(self, "oqpsk_demodulator",
                gr.io_signature(1, 1, gr.sizeof_gr_complex), # Input
                gr.io_signature(0, 0, 0))  # Output
        
        # Demodulate FM
        sensitivity = (pi / 2) / self.sps
        #self.fmdemod = gr.quadrature_demod_cf(1.0 / sensitivity)
        self.fmdemod = gr.quadrature_demod_cf(1)
        
        # Low pass the output of fmdemod to allow us to remove
        # the DC offset resulting from frequency offset
        
        alpha = 0.0008/self.sps
        self.freq_offset = gr.single_pole_iir_filter_ff(alpha)
        self.sub = gr.sub_ff()
        
        # recover the clock
        omega = self.sps
        gain_mu=0.03
        mu=0.5
        omega_relative_limit=0.0002
        freq_error=0.0
        
        gain_omega = .25*gain_mu*gain_mu        # critically damped
        
        # Descramble BERT sequence.  A channel error will create 3 incorrect bits
        #self._descrambler = gr.descrambler_bb(0x8A, 0x7F, 31) # CCSDS 7-bit descrambler
        
        self.clock_recovery_f = digital.clock_recovery_mm_ff(omega, gain_omega, mu, gain_mu,
                                                      omega_relative_limit)
    
        self.gr_float_to_complex = gr.float_to_complex(1)
        
        #Create a vector source reference to calculate BER
        self._vector_source_ref = gr.vector_source_b(([1,]), True, 1)
        #create a comparator 
        self.comparator = howto.compare_vector_cci((1, 1, 1, 1 ,0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1), (0,0, 1, 1, 0,0), 5, 0, True)
        
        self._ber = grc_blks2.error_rate(type='BER', 
                                         win_size=1000,
                                         bits_per_symbol=1)
        
        self._slicer = digital.binary_slicer_fb()
        
        
        self.gr_null_sink_f = gr.null_sink(gr.sizeof_float*1)
        
        # Add an SNR probe on the demodulated constellation
        #self._snr_probe = gr.probe_mpsk_snr_c(10.0/symbol_rate)
        self._snr_probe = digital.mpsk_snr_est_cc(0, 10000, 0.001) # 0 at the first mean Simple
        self.gr_null_sink_cc = gr.null_sink(gr.sizeof_gr_complex*1)
        
        self.gr_null_source = gr.null_source(gr.sizeof_float*1)
        
        ###############################
        ###------->                                            -->gr_float_to_complex--->_snr_probe --> gr_null_sink_cc
        ###---->fmdemod -->freq_offset--->sub-->clock_recovery --> _slicer -->_descrambler --> comparator -->_ber--> self.gr_null_sink_f 
        ###'''''''''''''|-->----------------|-->'                      _vector_source_ref-->
        #############################
        # Connect
        
        self.connect(self, self.fmdemod)
        self.connect(self.fmdemod, (self.sub, 0))
        self.connect(self.fmdemod, self.freq_offset, (self.sub, 1))
        
        #self.connect(self.sub, self.clock_recovery_f, self._slicer, self._descrambler, self.comparator, (self._ber, 0))
        self.connect(self.sub, self.clock_recovery_f, self._slicer, self.comparator, (self._ber, 0))
        
#        self.connect(self.clock_recovery_f, (self.gr_float_to_complex, 1))
#        self.connect(self.gr_null_source, (self.gr_float_to_complex, 0))
#    
#        self.connect(self.gr_float_to_complex, self._snr_probe, self.gr_null_sink_cc)
        
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
        return self._ber.ber_       
        
