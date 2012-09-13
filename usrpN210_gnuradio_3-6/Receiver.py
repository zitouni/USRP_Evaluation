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
from bpsk_demodulator import bpsk_demodulator

import gnuradio.gr.gr_threading as _threading
import sys, time

import wx
import wx.grid as gridl
import GuiReceiver

n2s = eng_notation.num_to_str  

            
def get_options():
    parser = OptionParser(option_class=eng_option)
    
    parser.add_option("-a", "--address", type="string", default="addr=192.168.10.2", 
                       help="Address of UHD device, [default=%default]") 
        
    parser.add_option("-S", "--samples-per-symbol", type = "float", default=2,
                          help="set samples/symbol [default=%default]")
    
    parser.add_option("-s", "--samp-rate", type="eng_float", default=0.25e6,
                      help="Select modulation sample rate (default=%default)")
    
    parser.add_option("-r", "--data-rate", type="eng_float", default=250e3,
                      help="Select modulation symbol rate (default=%default)")

    parser.add_option("-f", "--freq", type="eng_float", default=2485000000,
                      help="set frequency to FREQ", metavar="FREQ")
    
    parser.add_option ("-g", "--gain", type="eng_float", default=70,
                       help="set Rx PGA gain in dB [0,20]")
        
    parser.add_option("-v", "--verbose", action ="store_true", default=False)
    
    #####################################
    
    
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
    
    app = wx.App()
    sizer = wx.GridBagSizer()
    frame = GuiReceiver.Form(sizer, None, -1, '***Receiver*** Performance Evaluation of Modulations BERT', options)
    
    app.MainLoop()

