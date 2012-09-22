#!/usr/bin/env python
'''
Created on Jun 9, 2011

@author: rafik
'''
from __future__ import division

from gnuradio import gr, eng_notation, uhd
from gnuradio.eng_option import eng_option
from optparse import OptionParser

from transmit_path import transmit_path

import wx
import time
import gnuradio.gr.gr_threading as _threading
import wx.lib.plot as plot

_dac_rate = 128e6

n2s = eng_notation.num_to_str

class Options ():
    def __init__(self):
        self.dac = 0.0
        self.frequence = 0.0
        self.periode_temps = 0.0
        self.dac_pas = 0.0
        
        self.distance = 0.0
        self.dac_init = 0.0
        self.dac_courant = 0.0 
        self.dac_fin = 0.0
                
    def setAmplitude (self, valeur_amplitude):
        self.dac = valeur_amplitude
        self.dac_courant = valeur_amplitude
        
    def setFrequency (self, valeur_frequence):
        self.frequence = valeur_frequence * 1e6 
    
    def setPeriodTime (self, valeur_temps):
        self.periode_temps = valeur_temps
    
    def setAmplitudeStep (self, valeur_dac_pas):
        self.dac_pas = valeur_dac_pas
    
    def setAmplitudeEnd(self, valeur_dac_fin):
        self.dac_fin = valeur_dac_fin
        
    def getAmplitudeStep(self):
        return self.dac_pas
    
    def getPeriodTime(self):
        return self.periode_temps
    
    def getAmplitude (self):
        return self.dac
    
    def getAmplitudeCurrent (self):
        return self.dac_courant
    
    def getAmplitudeEnd (self):
        return self.dac_fin
    
    def getFrequency(self):
        return self.frequence
    
        

class Form(wx.Frame):    
    
    def __init__(self, sizer,  parent, id, title, options =None):
        wx.Frame.__init__(self, parent, id, title)
               
        self.options = options
        self.options_gui = Options()   
        
        self.buttonStopPushed = False  
        
        #self.condition = condition
        self.setInterface(sizer)
    
        
    def setOptionsReal(self):
        self.options.amplitude = self.options_gui.getAmplitude() 
        
    
    def setOptionsGui(self):   
        self.options_gui.setPeriodTime(float(self.temps_gui.GetValue()))
        self.options_gui.setAmplitude(float(self.dac_init_gui.GetValue()))
        #self.options_gui.set_frequence(float(self.freq_gui.GetValue()))
        self.options_gui.setAmplitudeStep(float(self.dac_pas_gui.GetValue()))
        self.options_gui.setAmplitudeEnd(float(self.dac_fin.GetValue()))
        
# Create the form of the window      
    def setInterface (self, sizer):       
        vbox = wx.BoxSizer(wx.VERTICAL) # The vertical box of different part of interface
        sizer.Add(vbox,(0,0),(1,1),wx.EXPAND)
        
        #First panel of buttons 
        self.panel_1(sizer)
        
        # Second panel to calculate parameters with time condition
        self.panel_2(sizer) 
                #Third Pannel to choose the modulation Technique
        self.panel_3(sizer) 
        
        vbox.Add(self.pnl1, 0, wx.EXPAND | wx.ALL, 2)
        vbox.Add(self.pnl_modulation, 0, wx.EXPAND | wx.ALL, 3)
        vbox.Add(self.pnl_button, 1, wx.EXPAND | wx.ALL, 3)

        self.SetSizerAndFit(sizer)
        self.SetSizeHints(-1,self.GetSize().y,-1,self.GetSize().y );
        
        self.button_arreter.Disable()

        
        self.Show(True)

    def panel_1 (self, sizer):
        self.pnl1= wx.Panel(self, -1, style = wx.SIMPLE_BORDER)
        
#        self.radio_b1 = wx.RadioButton(self.pnl1, -1, 'Fixer le nombre de prise de valeurs de parametres', (10,10), style=wx.RB_GROUP)
#        self.nbr_values_gui = wx.TextCtrl(self.pnl1, -1, pos=wx.Point(410, 5), size=wx.Size(80, 25), 
#                                             value='100')
        #self.radio_b2 = wx.RadioButton(self.pnl1, -1, 'Fix time between the change of parameters (Sec)', (10,40))
      
        
        self.text_indication = wx.StaticText(self.pnl1, -1, pos = wx.Point(10, 40), label= 'Fix time between the change of parameters (Sec)')
        self.temps_gui = wx.TextCtrl(self.pnl1, -1, pos=wx.Point(430, 40), size=wx.Size(80, 25), 
                                             value='10')
        #self.options_gui.set_periode_temps(float(self.temps_gui.GetValue()))
        
        #self.radio_b2.SetValue(True)
        self.etat1 = True
        self.etat2 = False
                 
        self.text_distance = wx.StaticText(self.pnl1, -1, pos = wx.Point(530, 10), label= "Distance between receiver and transmitter (cm)")
        self.distance_gui = wx.TextCtrl(self.pnl1, -1, pos=wx.Point(850, 5), size=wx.Size(80, 25), 
                                             value='100')
        
        
        self.text_dac_init = wx.StaticText(self.pnl1, -1, pos = wx.Point(530, 40), label= "Initial amplitude value")
        self.dac_init_gui = wx.TextCtrl(self.pnl1, -1, pos=wx.Point(850, 35), size=wx.Size(80, 25), 
                                             value='0')
        self.options_gui.setAmplitude(float(self.dac_init_gui.GetValue()))
        
        
        self.text_dac_pas = wx.StaticText(self.pnl1, -1, pos = wx.Point(530, 70), label= "Step of amplitude variation")
        self.dac_pas_gui = wx.TextCtrl(self.pnl1, -1, pos=wx.Point(850, 65), size=wx.Size(80, 25), 
                                             value='0.001')
        
        
        self.text_dac_fin = wx.StaticText(self.pnl1, -1, pos = wx.Point(530, 100), label= "Final amplitude value")
        self.dac_fin = wx.TextCtrl(self.pnl1, -1, pos=wx.Point(850, 95), size=wx.Size(80, 25), 
                                             value='33000')
        
        self.statusbar = self.CreateStatusBar(2)
        self.statusbar.SetStatusText("Time between taking parameters value",0) 

    def panel_2 (self, sizer):
        self.pnl_modulation = wx.Panel(self, -1, style = wx.SIMPLE_BORDER)
        #self.hbox = wx.BoxSizer(wx.HORIZONTAL)   
        
        self.radio_mod1 = wx.RadioButton(self.pnl_modulation, -1, 'BPSK modulation for IEEE 802.15.4', (10,10), style=wx.RB_GROUP)
        self.radio_mod1.SetValue(True)
        self.statusbar.SetStatusText("BPSK modulation",1)
        #Indicate type of modulation technique 
        self.state_mod = 1
        
        self.radio_mod2 = wx.RadioButton(self.pnl_modulation, -1, 'O-QPSK modulation for IEEE 802.15.4', (10,40))
        self.radio_mod2.SetValue(False)    
        
        self.radio_mod3 = wx.RadioButton(self.pnl_modulation, -1, 'DQPSK modulation for IEEE 802.15.4', (10,70))
        self.radio_mod3.SetValue(False)   
        
        self.Bind(wx.EVT_RADIOBUTTON, self.InitValeurRadio, id = self.radio_mod1.GetId())
        self.Bind(wx.EVT_RADIOBUTTON, self.InitValeurRadio, id = self.radio_mod2.GetId())
        self.Bind(wx.EVT_RADIOBUTTON, self.InitValeurRadio, id = self.radio_mod3.GetId())
        
    def InitValeurRadio (self, event):
        self.state_mod_bpsk = self.radio_mod1.GetValue()
        self.state_mod_oqpsk = self.radio_mod2.GetValue()
        self.state_mod_dqpsk = self.radio_mod3.GetValue()
        
        if self.state_mod_bpsk == True :
            self.statusbar.SetStatusText("BPSK modulation",1)
            self.state_mod = 1
            
        if self.state_mod_oqpsk == True :
            self.statusbar.SetStatusText("O-QPSK modulation",1)
            self.state_mod = 2
            
        if self.state_mod_dqpsk == True :
            self.statusbar.SetStatusText("DQPSK modulation", 1)
            self.state_mod = 3

    
    def panel_3 (self, sizer):  
        self.pnl_button = wx.Panel(self, -1, style = wx.SIMPLE_BORDER)
        self.hbox = wx.BoxSizer(wx.HORIZONTAL)
        
        self.button_commencer = wx.Button(self.pnl_button, -1, label = "Start Transmission", pos = (0,0))
        self.hbox.Add(self.button_commencer, 1 )
        self.Bind(wx.EVT_BUTTON, self.clickStart, self.button_commencer)
        
        self.button_arreter = wx.Button(self.pnl_button, -1, label = "Stop", pos = (0,0))
        self.hbox.Add(self.button_arreter, 1 )
        self.Bind(wx.EVT_BUTTON, self.clickStop, self.button_arreter)
             
        self.pnl_button.SetSizer(self.hbox)  # allow the panel to have the size of box  
        
            
        
#Method lunched with user click
    def clickStart (self, event):
        
        #self.condition.acquire()
        self.button_commencer.Disable()
        self.button_arreter.Enable()
        
        self.setOptionsGui()      
        #initialiser les options de transmission par ceux de l'interface graphique
        self.setOptionsReal()
        
        #self.tb.changeOptionsTransmitter(self.options)
    
        self.tb = transmit_path(self.options, self.state_mod)
        print "amplitude initial ", self.options.amplitude

        #self.th_premiers_op = Thread_Premiers_Options(self.options)
        self.th_cliq_commencer = Thread_click_start(self, self.tb)
    

                               
    def clickStop (self, event):
        
        #Change the state condition of the button to True to allow the break of transmission
        #when the user click on the  Stop button
        self.buttonStopPushed = True
        self.tb.stop()
        
        self.button_commencer.Enable()
        self.th_cliq_commencer.kill()
        self.tb.kill()
  
        #self.modifier_options()
                 
    def Status_bar_values (self, nbr_values = None) :
        self.statusbar.SetStatusText("Nombre de prise de valeurs de parametres : "+ str(nbr_values) ,0)

class Thread_timer (_threading.Thread):
    def __init__(self, time_to_send, tb):
        _threading.Thread.__init__(self)
        
        self.setDaemon(1)
        
        self.time_to_send = time_to_send
        self.tb = tb
        
        self.start()
        
    def run(self):
        
        print "Run thread Timer" 
        print "Time period of transmission is : ", self.time_to_send
        
        temps_courant = time.time() 
        temps_periode = temps_courant + self.time_to_send
    
        
        while  time.time() < temps_periode :
            time.sleep(1)
        
        #stop process of tb to continue the run of click start
        self.tb.stop()
         

class Thread_click_start (_threading.Thread):
    def __init__(self, Form, tb):
        _threading.Thread.__init__(self)
        
        self.form = Form
        self.options = self.form.options
        self.options_gui = self.form.options_gui
        
        self.time_to_send = self.options_gui.getPeriodTime()
        self.tb = tb
        
        self.start()
        
    def run(self): 
        
        while self.options.amplitude <= self.options_gui.getAmplitudeEnd():
            
            self.changeAmplitude()
            
            Thread_timer(self.time_to_send, self.tb)
            
            #Running a flow graph
            try:
                self.tb.run()
            except KeyboardInterrupt:
                pass   
            #Condition is used to bloc the process after the notify of Thread_Timer
            
            #If button stop is pushed 
            if (self.form.buttonStopPushed):
                break 
        
        #enable the button of commencer to allow a new use of commencer button
        self.form.button_commencer.Enable()
        
        self.form.buttonStopPushed = False
        print "Stop transmission at the amplitude of : ", self.options.amplitude
    
            
    def changeAmplitude(self) :
        
        #run the Timer to count the time of each transmission with a parameters
        print "Current amplitude : ", self.options.amplitude
        
        #Prepare change amplitude with indication by vector code
        self.tb.changeOptionsTransmitterWithVectorCode(self.options, self.form.state_mod)
        
        #Time to send vector code
        time_to_send_code = 10
        
        print "time to send code is : ", time_to_send_code
        
        #Thread to count time period to send the vector code
        Thread_timer(time_to_send_code, self.tb) 
        
        print "*************Begin send vector code*************"
        #Running a flow graph
        try:
            self.tb.run()
        except KeyboardInterrupt:
            pass   
        #Condition is used to bloc the process after the notify of Thread_Timer
        
        print "*************End send vector code*************"
           
        #Use the new amplitude to send a vector of values 1
        self.options.amplitude = self.options.amplitude + self.options_gui.getAmplitudeStep()
     
        self.tb.changeOptionsTransmitter(self.options, self.form.state_mod)
        #self.tb.changeOptionsTransmitterWithVectorCode(self.options)

        print "New amplitude : ", self.options.amplitude
        
    def kill(self):
        del self

if __name__ == "__main__":
    app = wx.App()
    sizer = wx.GridBagSizer()
    frame = Form(sizer, None, -1, '***Emetteur***Evaluation de performances des transmissions BERT')

    app.MainLoop()
