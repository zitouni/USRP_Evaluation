#!/usr/bin/env python
'''
Created on Jun 9, 2011

@author: rafik
'''
from __future__ import division

from gnuradio import gr, eng_notation, usrp
from gnuradio.eng_option import eng_option
from optparse import OptionParser
from transmit_path import transmit_path

import wx
import time
import gnuradio.gr.gr_threading as _threading
import wx.lib.plot as plot

_dac_rate = 128e6

n2s = eng_notation.num_to_str

class Option ():
    def __init__(self):
        self.dac = 0.0
        self.frequence = 0.0
        self.periode_temps = 0.0
        self.dac_pas = 0.0
        
        self.distance = 0.0
        self.dac_init = 0.0
        self.dac_courant = 0.0 
        self.dac_fin = 0.0
                
    def set_dac (self, valeur_amplitude):
        self.dac = valeur_amplitude
        self.dac_courant = valeur_amplitude
        
    def set_frequence (self, valeur_frequence):
        self.frequence = valeur_frequence * 1e6 
    
    def set_periode_temps (self, valeur_temps):
        self.periode_temps = valeur_temps
    
    def set_dac_pas (self, valeur_dac_pas):
        self.dac_pas = valeur_dac_pas
    
    def set_dac_fin (self, valeur_dac_fin):
        self.dac_fin = valeur_dac_fin
        
    def get_dac_pas(self):
        return self.dac_pas
    
    def get_periode_temps(self):
        return self.periode_temps
    
    def get_dac (self):
        return self.dac
    
    def get_dac_courant (self):
        return self.dac_courant
    
    def get_dac_fin (self):
        return self.dac_fin
    
    def get_frequence (self):
        return self.frequence
    
        
    
class tx_bpsk_block(gr.top_block):
    def __init__(self, options, plusieurs = None):    
        gr.top_block.__init__(self, "tx_mpsk")
        
        self.plusieurs = plusieurs

        self._transmitter = transmit_path(options.sps,
                                          options.excess_bw,
                                          options.amplitude)

        if_rate = options.rate*options.sps
        interp = int(_dac_rate/if_rate)

        print "Modulation:", n2s(options.rate), "bits/sec"
        print "TX IF rate:", n2s(if_rate), "samples/sec"
        print "USRP interpolation:", interp
        print "DAC amplitude:", options.amplitude
        

        self._setup_usrp(options.which,
                         interp,
                         options.tx_subdev_spec,
                         options.freq)
    
        self.connect(self._transmitter, self._usrp)

        
    def _setup_usrp(self, which, interp, subdev_spec, freq):
    
        self._usrp = usrp.sink_c(which=which, interp_rate=interp)
        
        if subdev_spec is None:
            subdev_spec = usrp.pick_tx_subdevice(self._usrp)
        self._usrp.set_mux(usrp.determine_tx_mux_value(self._usrp, subdev_spec))
        self._subdev = usrp.selected_subdev(self._usrp, subdev_spec)
        tr = usrp.tune(self._usrp, self._subdev.which(), self._subdev, freq)
        
        if not (tr):
            print "Failed to tune to center frequency!"
        else:
            print "Center frequency:", n2s(freq)
        gain = float(self._subdev.gain_range()[1]) # Max TX gain
        self._subdev.set_gain(gain)
        self._subdev.set_enable(True)
        print "TX d'board:", self._subdev.side_and_name()
        
    def change_options_transmitter(self, options):
        
        #disconnect the current tranmitter from the usrp
        self.disconnect(self._transmitter, self._usrp)
        #delet the old (current) parameters of transmission
        del self._transmitter
#        del self._usrp
        #create the new transmitter parameters
        
        self._transmitter = transmit_path(options.sps,
                                          options.excess_bw,
                                          options.amplitude)
        print "DAC amplitude:", options.amplitude

#        if_rate = options.rate*options.sps
#        interp = int(_dac_rate/if_rate)
#        self._setup_usrp(options.which,
#                         interp,
#                         options.tx_subdev_spec,
#                         options.freq)
        
#        connect the transmitter to the old usrp
        self.connect(self._transmitter, self._usrp)
        
    def kill(self):
        del self._transmitter
        del self._usrp
        del self

                

class Fenetre(wx.Frame):    
    
    def __init__(self, sizer,  parent, id, title, options =None):
        wx.Frame.__init__(self, parent, id, title)
               
        self.options = options
        self.options_gui = Option()     
        
        #self.condition = condition
        self.initialiser(sizer)
        
        #initiate the gui options 
        self.set_options_gui()
        #initialiser les options de transmission par ceux de l'interface graphique
        self.set_options_real()
         
        self.tb = tx_bpsk_block(self.options)
        #self.th_premiers_op = Thread_Premiers_Options(self.options)
        
    def set_options_real(self):
        self.options.amplitude = self.options_gui.get_dac() 
        
    
    def set_options_gui(self):   
        self.options_gui.set_periode_temps(float(self.temps_gui.GetValue()))
        self.options_gui.set_dac(float(self.dac_init_gui.GetValue()))
        #self.options_gui.set_frequence(float(self.freq_gui.GetValue()))
        self.options_gui.set_dac_pas(float(self.dac_pas_gui.GetValue()))
        self.options_gui.set_dac_fin(float(self.dac_fin.GetValue()))
        
# Create the form of the window      
    def initialiser (self, sizer):       
        vbox = wx.BoxSizer(wx.VERTICAL) # The vertical box of different part of interface
        sizer.Add(vbox,(0,0),(1,1),wx.EXPAND)
        
        #First panel of buttons 
        self.panneau_1(sizer)
        
        # Second panel to calculate parameters with time condition
        self.panneau_2(sizer)  
        
        vbox.Add(self.pnl1, 0, wx.EXPAND | wx.ALL, 2)
        vbox.Add(self.pnl_button, 0, wx.EXPAND | wx.ALL, 3)
        #vbox.Add(self.pnl3, 1, wx.EXPAND | wx.ALL, 3)

        self.SetSizerAndFit(sizer)
        self.SetSizeHints(-1,self.GetSize().y,-1,self.GetSize().y );

        self.Show(True)

    def panneau_1 (self, sizer):
        self.pnl1= wx.Panel(self, -1, style = wx.SIMPLE_BORDER)
        
#        self.radio_b1 = wx.RadioButton(self.pnl1, -1, 'Fixer le nombre de prise de valeurs de parametres', (10,10), style=wx.RB_GROUP)
#        self.nbr_values_gui = wx.TextCtrl(self.pnl1, -1, pos=wx.Point(410, 5), size=wx.Size(80, 25), 
#                                             value='100')
        self.radio_b2 = wx.RadioButton(self.pnl1, -1, 'Fixer le temps entre changement de parametres (Sec)', (10,40))
        self.temps_gui = wx.TextCtrl(self.pnl1, -1, pos=wx.Point(430, 40), size=wx.Size(80, 25), 
                                             value='600')
        
        self.text_indication = wx.StaticText(self.pnl1, -1, pos = wx.Point(20, 70), label= "Ce temps = au moins deux fois le temps attente du recepteur")
        #self.options_gui.set_periode_temps(float(self.temps_gui.GetValue()))
        
        self.radio_b2.SetValue(True)
        self.etat1 = True
        self.etat2 = False
                 
        self.text_distance = wx.StaticText(self.pnl1, -1, pos = wx.Point(530, 10), label= "Distance entre emetteur et recepteur (cm)")
        self.distance_gui = wx.TextCtrl(self.pnl1, -1, pos=wx.Point(830, 5), size=wx.Size(80, 25), 
                                             value='100')
        
        
        self.text_dac_init = wx.StaticText(self.pnl1, -1, pos = wx.Point(530, 40), label= "Valeur d'amplitude initiale DAC")
        self.dac_init_gui = wx.TextCtrl(self.pnl1, -1, pos=wx.Point(830, 35), size=wx.Size(80, 25), 
                                             value='0')
        self.options_gui.set_dac(float(self.dac_init_gui.GetValue()))
        
        
        self.text_dac_pas = wx.StaticText(self.pnl1, -1, pos = wx.Point(530, 70), label= "Le pas de variation du DAC")
        self.dac_pas_gui = wx.TextCtrl(self.pnl1, -1, pos=wx.Point(830, 65), size=wx.Size(80, 25), 
                                             value='50')
        #self.options_gui.set_dac_pas(float(self.dac_pas_gui.GetValue()))
        
        self.text_dac_fin = wx.StaticText(self.pnl1, -1, pos = wx.Point(530, 100), label= "Valeur finale d'amplitude")
        self.dac_fin = wx.TextCtrl(self.pnl1, -1, pos=wx.Point(830, 95), size=wx.Size(80, 25), 
                                             value='33000')

#        self.text_freq = wx.StaticText(self.pnl1, -1, pos = wx.Point(500, 130), label= "Valeur de Frequence (Mhz)")
#        self.freq_gui = wx.TextCtrl(self.pnl1, -1, pos=wx.Point(800, 125), size=wx.Size(80, 25), 
#                                             value='900')
        #self.options_gui.set_frequence(float(self.freq_gui.GetValue()))
        
 #       self.Bind(wx.EVT_RADIOBUTTON, self.InitValeurRadio, id = self.radio_b1.GetId())
        self.Bind(wx.EVT_RADIOBUTTON, self.InitValeurRadio, id = self.radio_b2.GetId())
        
        self.statusbar = self.CreateStatusBar(2)
        self.statusbar.SetStatusText("Temps entre prise de valeurs de parametres",0) 
    
    def panneau_2 (self, sizer):
         
        self.pnl_button = wx.Panel(self, -1, style = wx.SIMPLE_BORDER)
        self.hbox = wx.BoxSizer(wx.HORIZONTAL)
        
        self.button_commencer = wx.Button(self.pnl_button, -1, label = "Commencer la transmission", pos = (0,0))
        self.hbox.Add(self.button_commencer, 1 )
        self.Bind(wx.EVT_BUTTON, self.cliq_commencer, self.button_commencer)
        
        self.button_arreter = wx.Button(self.pnl_button, -1, label = "Arreter", pos = (0,0))
        self.hbox.Add(self.button_arreter, 1 )
        self.Bind(wx.EVT_BUTTON, self.cliq_Arreter, self.button_arreter)
        
        
        self.pnl_button.SetSizer(self.hbox)  # allow the panel to have the size of box         

        
    def InitValeurRadio (self, event):
        self.etat2 = self.radio_b2.GetValue()
        
        if self.etat2 == True :
            self.statusbar.SetStatusText("Temps entre changement de parametres",0)
        else :
            self.statusbar.SetStatusText(" ",1)
            
        
#Method lunched with user click
    def cliq_commencer (self, event):
        print "Commencer la transmission"
        #self.condition.acquire()
        self.button_commencer.Disable()
        
        self.set_options_gui()      
        #initialiser les options de transmission par ceux de l'interface graphique
        self.set_options_real()
        
        self.tb.change_options_transmitter(self.options)
        
        self.th_cliq_commencer = Thread_Trait_Cliq_Commencer(self, self.tb)
        
#    def modifier_options(self) :
#        self.options.amplitude = 2000.0
#        self.options.freq = 2500.0 * 1e6 
#        
#        #change options of transmission 
#        self.tb.change_options_transmitter(self.options)

                               
    def cliq_Arreter (self, event):
        print "Fin de transmission"
        
        self.th_cliq_commencer.stop()
        self.tb.stop()
        self.button_commencer.Enable()
        #self.tb.kill()
        
        
        #self.modifier_options()
                 
    def Status_bar_values (self, nbr_values = None) :
        self.statusbar.SetStatusText("Nombre de prise de valeurs de parametres : "+ str(nbr_values) ,0)

class Thread_Timer (_threading.Thread):
    def __init__(self, Fenetre, done, tb):
        _threading.Thread.__init__(self)
        self.setDaemon(1)
        self.done = done
        self.tb = tb
        self.fenetre = Fenetre
        self.options_gui = self.fenetre.options_gui
        self.start()
        
    def run(self):
        temps_courant = time.time()
        temps_periode = temps_courant + self.options_gui.get_periode_temps()
        
        print temps_periode
        
        while  time.time() < temps_periode :
            time.sleep(1)
        
        #stop process of tb to continue the run of cliq commencer
        self.tb.stop()
        print "fin de transmission"
            

class Thread_Trait_Cliq_Commencer (_threading.Thread):
    def __init__(self, Fenetre, tb):
        _threading.Thread.__init__(self)
        self.setDaemon(1)
        self.fenetre = Fenetre
        self.options = self.fenetre.options
        self.options_gui = self.fenetre.options_gui
        self.tb = tb
        
        #Boolean variable shared to indicate the end of transmission
        self.done = False
        
        super(Thread_Trait_Cliq_Commencer, self).__init__()
        self._stop = _threading.Event()

        
        self.start()
        
    def run(self): 
        
        while self.options.amplitude <= self.options_gui.get_dac_fin():
            
            #run the Timer to count the time of each transmission with a parameters
            print self.options.amplitude
            
            Thread_Timer(self.fenetre, self.done, self.tb)
            try:
                self.tb.run()
            except KeyboardInterrupt:
                pass   
            
            #when the run is stoped by the Timer, we change the options of transmission 
            self.modifier_amplitude() 
        
        #enable the button of commencer to allow a new use of commencer button
        self.fenetre.button_commencer.Enable()
    
            
    def modifier_amplitude(self) :
        self.options.amplitude = self.options.amplitude + self.options_gui.get_dac_pas()
        #initialiser les options de transmission
    
        self.tb.change_options_transmitter(self.options)
        
        
    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()


if __name__ == "__main__":
    app = wx.App()
    sizer = wx.GridBagSizer()
    frame = Fenetre(sizer, None, -1, '***Emetteur***Evaluation de performances des transmissions BERT')

    app.MainLoop()
