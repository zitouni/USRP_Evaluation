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

from gnuradio import gr, eng_notation
from gnuradio.eng_option import eng_option
from optparse import OptionParser
from transmit_path import transmit_path

import sys, time 
import gnuradio.gr.gr_threading as _threading

import wx
import wx.grid as gridl
import InterfaceEmetteur


_dac_rate = 128e6

n2s = eng_notation.num_to_str
        

def get_options():
    parser = OptionParser(option_class=eng_option)
    parser.add_option("-w", "--which", type="int", default=0,
                      help="select which USRP (0, 1, ...) default is %default",
                      metavar="NUM")
    parser.add_option("-T", "--tx-subdev-spec", type="subdev", default=None,
                      help="select USRP Tx side A or B (default=first one with a daughterboard)")
    parser.add_option("-f", "--freq", type="eng_float", default=None,
                      help="set frequency to FREQ", metavar="FREQ")
    parser.add_option("-a", "--amplitude", type="eng_float", default=None,
                      help="set Tx amplitude (0-32767) (default=%default)")
    parser.add_option("-r", "--rate", type="eng_float", default=40e3,
                      help="Select modulation symbol rate (default=%default)")
    parser.add_option("", "--sps", type="int", default=8,
                      help="Select samples per symbol (default=%default)")
    parser.add_option("", "--excess-bw", type="eng_float", default=0.35,
                      help="Select RRC excess bandwidth (default=%default)")
		      
    (options, args) = parser.parse_args()
    if len(args) != 0:
        parser.print_help()
        sys.exit(1)
	
    if options.freq == None:
        print "Must supply frequency as -f or --freq"
        sys.exit(1)

    return (options, args)

if __name__ == "__main__":
    
    (options, args) = get_options()
    

    app = wx.App()
    sizer = wx.GridBagSizer()
    frame = InterfaceEmetteur.Fenetre(sizer, None, -1, '***Emetteur***Evaluation de performances des transmissions BERT', options)
    
    app.MainLoop()
    

