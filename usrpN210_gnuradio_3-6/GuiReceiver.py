#!/usr/bin/env python
'''
Created on May 18, 2011
#
#@author: zitouni
#'''

from __future__ import division
import wx
import time
import math
import gnuradio.gr.gr_threading as _threading
import wx.lib.plot as plot

from receiver_path import receiver_path
#For plot
from numpy import *
import Gnuplot, Gnuplot.funcutils 

class Param():
    
    def __init__(self):
        
        self.set_param()
        
        self.dac_courant = 0.0 
        self.distance = 0.0
        self.frequence = 0.0 
        self.dac_pas = 0.0
          
    def set_param(self):
        self.nbr_values = 0.0
        self.som_ber = 0.0 
        self.moy_ber = 0.0
        self.som_snr = 0.0 
        self.moy_snr = 0.0 
        self.moy_snr = 0.0
        
        self.min_ber = float('+inf')
        self.min_snr = float('+inf')
        self.max_ber = float('-inf')
        self.max_snr = float('-inf') 

        
    def calculSum (self, ber, snr):
        self.som_ber = self.som_ber + ber
        self.som_snr = self.som_snr + snr 
        
    def calculMaxMin (self, ber, snr):
        if ber <= self.min_ber :
            self.min_ber = ber
        if ber >= self.max_ber :
            self.max_ber = ber
            
        if snr <= self.min_snr :
            self.min_snr = snr
        if snr >= self.max_snr :
            self.max_snr = snr 
    
    # Calculate the values of parameters means  
    def calculAverage (self):
        try :
            self.moy_ber = self.som_ber  /self.nbr_values
            self.moy_snr = self.som_snr / self.nbr_values            
        except ZeroDivisionError:
            print "Attention division by 0 !!"
    
    def get_moy_snr(self):
        return self.moy_snr
    
    def get_moy_ber(self):
        return self.moy_ber
    
    def get_min_ber(self):
        return self.min_ber
    
    def get_min_snr(self):
        return self.min_snr
    
    def get_max_ber(self):
        return self.max_ber
    
    def get_max_snr(self):
        return self.max_snr
    
    def inc_dac_pas (self, valeur_courant):
        return valeur_courant + self.dac_pas    

    def inc_nbr_values(self):
        self.nbr_values +=1 
    
    def set_dac_courant(self, dac_courant_valeur):
        self.dac_courant = dac_courant_valeur
      
    def set_distance(self, valeur_distance):
        self.distance = valeur_distance
        
    def set_dac_pas(self, valeur_dac_pas):
        self.dac_pas = valeur_dac_pas
        
    def set_frequence(self, valeur_frequence):
        self.frequence = valeur_frequence
        
    def get_nbr_value(self):
        return self.nbr_values
        
    def get_distance(self):
        return self.distance
    
    def get_dac_fin(self):
        return self.dac_fin   
        
    def get_dac_courant (self):
        return self.dac_courant   
    
    def get_frequence (self):
        return self.frequence  

class thread_flot_graph (_threading.Thread):
    def __init__(self, tb):
        _threading.Thread.__init__(self)
        self.setDaemon(1)
        
        self.tb = tb
        self.done = False
        self.start()
        
    def run(self):
        try:
            self.tb.run() 
        except KeyboardInterrupt:
            pass


    
class Option():
    frequence = 0.0
    def __init__(self, options =None):
        self.nbr_init = 0.0
        self.distance = 0.0
        self.dac_pas = 0.0
        self.dac_init = 0.0
        self.dac_fin = 0.0
        
        self.periode_temps = 0.0
        self.attente = 0.0 
        
        if not options  == None :
            self.frequence = options.freq 
    
    
    def set_nbr_init (self, valeur_nbr_init):
        self.nbr_init = valeur_nbr_init
        
    def set_dac_init (self, valeur_init):
        self.dac_init = valeur_init
        self.dac_courant = self.dac_init
    
    def set_dac_pas (self, valeur_dac_pas):
        self.dac_pas = valeur_dac_pas
        
    def set_distance (self, valeur_distance):
        self.distance = valeur_distance
        
    def set_dac_fin (self, valeur_dac_fin):
        self.dac_fin = valeur_dac_fin
        
    def set_frequence(self, valeur_frequence):
        self.frequence = valeur_frequence
        
    def get_dac_fin(self):
        return self.dac_fin
  
    def get_nbr_init (self):
        return self.nbr_init
    
    def get_dac_init (self):
        return self.dac_init
    
    def get_distance(self):
        return self.distance
    
    def get_dac_pas(self):
        return self.dac_pas
    
    def get_frequence (self):
        return self.frequence  

class status_thread(_threading.Thread):
    def __init__(self, tb):
        _threading.Thread.__init__(self)
        self.setDaemon(1) 
        self.tb = tb  
        #self.condition = condition
        self.done = False 
        self.start() 

    def run(self):
        while not self.done:
            #print "Estimated SNR: %4.1f dB  BER: %g" % ( tb.snr(), tb.ber())       
            print "Estimated SNR: %f dB  BER: %f" % ( self.tb.snr(), self.tb.ber()) 
       
            try:
                time.sleep(1.0)
            except KeyboardInterrupt:
                self.done = True
                
#            if (self.tb.get_compare_vector_decision()):
#                print "I received signalization trame"
#                self.tb.set_compare_vector_decision(False)
     

class Form(wx.Frame):   
    nbr_fichiers_sauvegarde = 0
    nomFichier = "Experience_0.dat" 
    arreter_calcul = False
    
    def __init__(self, sizer,  parent, id, title, options = None):
        wx.Frame.__init__(self, parent, id, title)
        
        self.options = Option(options) 
              
        self.initialiser(sizer)
        self.init_options_gui()
        self.nbr_lignes_text = 0.0
        
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        
        self.tb = receiver_path(options)
        #thread_check = Thread_check(self.tb)
        
        self.flot_graph = thread_flot_graph(self.tb)
        self.status = status_thread(self.tb)
        
    def OnClose(self, event):
        self.tb.stop()
        self.flot_graph.stop()
        self.status.stop()
# Create the form of the window      
    def initialiser (self, sizer):       
        vbox = wx.BoxSizer(wx.VERTICAL) # The vertical box of different part of interface
        sizer.Add(vbox,(0,0),(1,1),wx.EXPAND)
        
        #First panel of buttons 
        self.panneau_1(sizer)
        
        # Second panel to calculate parameters with time condition
        self.panneau_2(sizer)
        
        #Third panel of text containing the values of parameters 
        self.panneau_3(sizer)    
        
        vbox.Add(self.pnl1, 0, wx.EXPAND | wx.ALL, 2)
        vbox.Add(self.pnl_button, 0, wx.EXPAND | wx.ALL, 3)
        vbox.Add(self.pnl3, 1, wx.EXPAND | wx.ALL, 3)

        self.SetSizerAndFit(sizer)
        self.SetSizeHints(-1,self.GetSize().y,-1,self.GetSize().y );

        self.Show(True)
    
    def init_options_gui (self):
        self.options.set_nbr_init(float(self.nbr_values_gui.GetValue()))
        self.options.set_distance(float(self.distance_gui.GetValue()))
        self.options.set_dac_init(float(self.dac_init_gui.GetValue()))
        self.options.set_dac_pas(float(self.dac_pas_gui.GetValue()))
        self.options.set_dac_fin(float(self.dac_fin_gui.GetValue()))
        #self.options.set_periode_temps(float(self.temps_gui.GetValue()))
        #self.options.set_attente(float(self.attente_gui.GetValue()))
        #self.options.set_frequence(float(self.freq_gui.GetValue()))
        
    def panneau_1 (self, sizer):
        self.pnl1= wx.Panel(self, -1, style = wx.SIMPLE_BORDER)
        
        self.radio_b1 = wx.RadioButton(self.pnl1, -1, 'Fix a number of measured parameters values', (10,10), style=wx.RB_GROUP)
        self.radio_b1.SetValue(False)
        self.etat1 = False
        self.etat2 = True
        self.nbr_values_gui = wx.TextCtrl(self.pnl1, -1, pos=wx.Point(480, 5), size=wx.Size(80, 25), 
                                             value='100') 
        self.text_distance = wx.StaticText(self.pnl1, -1, pos = wx.Point(570, 10), label= "Distance between transmitter and receiver (cm)")
        self.distance_gui = wx.TextCtrl(self.pnl1, -1, pos=wx.Point(890, 5), size=wx.Size(80, 25), 
                                             value='100')
        
        
        self.radio_b2 = wx.RadioButton(self.pnl1, -1, 'Fix a period of time to calculate the average of parametres (Sec)', (10,70))
        self.radio_b2.SetValue(True)
#        self.temps_gui = wx.TextCtrl(self.pnl1, -1, pos=wx.Point(480, 65), size=wx.Size(80, 25), 
#                                             value='10') 
#        wx.StaticText(self.pnl1, -1, pos = wx.Point(35, 95), label= " Waiting time betwenn the periods of calculating the average (Sec)")
#        self.attente_gui = wx.TextCtrl(self.pnl1, -1, pos=wx.Point(480, 90), size=wx.Size(80, 25), 
#                                             value='2')
        
        self.text_dac_init = wx.StaticText(self.pnl1, -1, pos = wx.Point(570, 40), label= "Initial value of signal amplitude")
        self.dac_init_gui = wx.TextCtrl(self.pnl1, -1, pos=wx.Point(890, 35), size=wx.Size(80, 25), 
                                             value='0')
        
        
        self.text_dac_pas = wx.StaticText(self.pnl1, -1, pos = wx.Point(570, 70), label= "Amplitude variation step ")
        self.dac_pas_gui = wx.TextCtrl(self.pnl1, -1, pos=wx.Point(890, 65), size=wx.Size(80, 25), 
                                             value='0.001')
    
    
        self.text_dac_fin = wx.StaticText(self.pnl1, -1, pos = wx.Point(570, 100), label= "Maximum amplitude value")
        self.dac_fin_gui = wx.TextCtrl(self.pnl1, -1, pos=wx.Point(890, 95), size=wx.Size(80, 25), 
                                             value='0.9')
        
        
        self.Bind(wx.EVT_RADIOBUTTON, self.InitValeurRadio, id = self.radio_b1.GetId())
        self.Bind(wx.EVT_RADIOBUTTON, self.InitValeurRadio, id = self.radio_b2.GetId())
        
        self.statusbar = self.CreateStatusBar(2)
        self.statusbar.SetStatusText("Number of taken parameter values",0) 
    
    def panneau_2 (self, sizer):
         
        self.pnl_button = wx.Panel(self, -1, style = wx.SIMPLE_BORDER)
        self.hbox = wx.BoxSizer(wx.HORIZONTAL)
        
        self.button_calculer = wx.Button(self.pnl_button, -1, label = "Calculate", pos = (0,0))
        self.hbox.Add(self.button_calculer, 1 )
        self.Bind(wx.EVT_BUTTON, self.cliq_Calculer, self.button_calculer)
        
        self.button_arreter = wx.Button(self.pnl_button, -1, label = "Stop", pos = (0,0))
        self.hbox.Add(self.button_arreter, 1 )
        self.Bind(wx.EVT_BUTTON, self.cliq_Arreter, self.button_arreter)
        
        self.button_sauvegarder = wx.Button(self.pnl_button, -1, label = "Save", pos = (100, 0))
        self.hbox.Add(self.button_sauvegarder, 1 )
        self.Bind(wx.EVT_BUTTON, self.cliq_Sauvegarder, self.button_sauvegarder) 
        
        self.button_courbe = wx.Button(self.pnl_button, -1, label = "Curve", pos = (100, 0))
        self.hbox.Add(self.button_courbe, 1 )
        self.Bind(wx.EVT_BUTTON, self.cliq_courbe, self.button_courbe) 
        
        self.pnl_button.SetSizer(self.hbox)  # allow the panel to have the size of box         
    
    def panneau_3 (self, sizer):
        self.pnl3 = wx.Panel(self, -1, style = wx.SIMPLE_BORDER)
        self.text_performances = wx.TextCtrl(self.pnl3, -1, pos=wx.Point(0, 0), size=wx.Size(1600,400), style=wx.TE_MULTILINE, 
                                             value='The averages of parameters SNR et BER')
        
    def InitValeurRadio (self, event):
        self.etat1 = self.radio_b1.GetValue()
        self.etat2 = self.radio_b2.GetValue()
        if self.etat1 == True :
            self.statusbar.SetStatusText("Number between taking the average of parameters",0)
        else :
            self.statusbar.SetStatusText(" ",0)
            
        if self.etat2 == True :
            self.statusbar.SetStatusText("Time between taking the average of parameters",1)
        else :
            self.statusbar.SetStatusText(" ",1)
            
        
#Method lunched with user click
    def cliq_Calculer (self, event):
        self.button_calculer.Disable()   
        self.arreter_calcul = False    
        self.init_options_gui()
        Thread_Trait_Cliq_Calculer(self, self.tb)
            
    def cliq_Arreter (self, event):
        print "End of Calcul"  
        self.arreter_calcul = True
    
    def get_arreter_calcul (self):
        return self.arreter_calcul
                 
    def cliq_Sauvegarder (self, event):
        print "Save"
        self.nomFichier = "Experience_%d.dat" % (self.nbr_fichiers_sauvegarde)
        self.nbr_fichiers_sauvegarde +=1
        fichier = open(self.nomFichier,"w")
        fichier.writelines(self.text_performances.GetValue())
        fichier.close()
    
    def cliq_courbe (self, event):
        print "Curve"
        Thread_Trait_Cliq_Courbe(self)       

    def Status_bar_values (self, nbr_values = None) :
#        if nbr_values is None :
             self.statusbar.SetStatusText("Number between taking the average of parameters : "+ str(nbr_values) ,0)
#        else :
#            self.statusbar.SetStatusText(str(nbr_values),0)
    def sauvegarder_fichier(self):
        fichier = open(self.nomFichier,"w")
        fichier.writelines(self.text_performances.GetValue())
        fichier.close()
        

    def afficher_param (self, param):
        #Test if the value of tb is passed by constructure
        try :
            if not param== None :
                self.text_performances.WriteText("nbr: " + str(param.get_nbr_value())+
                                                 " Dist: "+ str(param.get_distance())+
                                                 " BerMoy: " + str(param.get_moy_ber())+
                                                 " BerMin: " + str(param.get_min_ber())+ 
                                                 " BerMax: " + str(param.get_max_ber())+
                                                 " SnrMoy: " + str(param.get_moy_snr())+
                                                 " SnrMin: " + str(param.get_min_snr())+ 
                                                 " SnrMax: " + str(param.get_max_snr())+ 
                                                 " Amp: " + str(param.get_dac_courant()) + 
                                                 " Freq: " + str(param.get_frequence()) +"\n") 
                #Save Backup of data mesured
                nomFichier = "BackUp.dat"
                fichierBackUp = open(nomFichier,"w")  
                fichierBackUp.writelines(self.text_performances.GetValue())
                fichierBackUp.close()
                                                    
                #                                             " Frequency_Offset: " + str(self.pm.Calcul_Moyennes()[3]) +
                #                                             " Timing_offset: " + str(self.pm.Calcul_Moyennes()[4])+"\n" )
            else :
                self.text_performances.WriteText("Calculate\n")
        except Exception:
            print 'Application interrupted 1'  
    
    def OnClose(self, event):
        self.tb.kill()
        self.Destroy()
         

class Thread_Trait_Cliq_Courbe (_threading.Thread):
    def __init__(self, Form):
        _threading.Thread.__init__(self)
        self.setDaemon(1)
        self.fenetre = Form
        self.start()
        
    def run(self):
         g= Gnuplot.Gnuplot(debug = 1 )
         g.title("SNR function of amplitude 900Mhz")
         
         #print self.fenetre.nomFichier
         nomFichier = "BackUp.dat"
         g.xlabel('DAC')
         g.ylabel('SNR')
         

         g.plot('"%s" using 10:8 title "BPSK" with linespoints 3 3'%(nomFichier) )
         #with_='points 3 3'

         #g('set xrange [5:6]')
         #g('set yrange [0.1:0.2]')
              
         #Save the plot on the files
         g.hardcopy('%s.ps'%(nomFichier), enhanced=1, color=1)
         g.hardcopy('%s.png'%(nomFichier), terminal = 'png')
         g.replot()

         raw_input('Press any key to close curve..\n')
 
         
class Thread_Trait_Cliq_Calculer (_threading.Thread):
    def __init__(self, Form, tb):
        _threading.Thread.__init__(self)
        self.setDaemon(1)
        self.fenetre = Form
        self.tb = tb
        self.start()
        
    def run(self):
        condition = _threading.Condition()
        condition.acquire()
        
        #just to clean for first insertion of text performances 
        if self.fenetre.nbr_lignes_text == 0 :
            self.fenetre.text_performances.Clear()
        self.fenetre.nbr_lignes_text+=1
        ###End Just
         
        #Calcul with initiating the numbre of values
        if self.fenetre.etat1 :
            #initiate the nbr_value nbr of the parameters to sample
            #pm is object containing a results of calcul
            #self.pm_nbr = Thread_Param_Calcul_Nbr(self.fenetre.arreter_calcul,float(self.fenetre.nbr_values_gui.GetValue()), condition, self.tb)
            self.pm_nbr = Thread_Param_Calcul_Nbr(self.fenetre, condition, self.tb)
            
            condition.wait()
            
#            #Calcul la moyenne des parametres

            self.fenetre.afficher_param(self.pm_nbr)
            self.fenetre.sauvegarder_fichier()          
        
        #Calcul with Time Period 
        if self.fenetre.etat2 :
                        
            self.pm_temps = Thread_Param_Calcul_Temps(self.fenetre, condition, self.tb)
            
            condition.wait()
            
            #Calcul la moyenne des parametres
            #self.pm_temps.calculAverage()
            #self.fenetre.afficher_param(self.pm_temps)
            self.fenetre.sauvegarder_fichier()  
        
        self.fenetre.button_calculer.Enable()    
        condition.release()
            

class Thread_Param_Calcul_Temps (_threading.Thread, Param):  
    def __init__(self, fenetre, condition, tb = None):
        _threading.Thread.__init__(self)
        Param.__init__(self)
            
        self.setDaemon(1)
        self.fenetre = fenetre

        self.arreter_calcul = self.fenetre.get_arreter_calcul()
        self.done = False
        self.tb = tb
        self.condition = condition
        
        self.init_param()
        self.start()
        
    def init_param (self):
        self.set_dac_courant(self.fenetre.options.get_dac_init())
        self.set_dac_pas(self.fenetre.options.get_dac_pas())
        self.set_distance(self.fenetre.options.get_distance())
        self.set_frequence(self.fenetre.options.get_frequence())
        
    def run(self):
        self.condition.acquire()
        print "State Time"     
        
        while self.get_dac_courant() <= self.fenetre.options.get_dac_fin() and not self.arreter_calcul :       
    
                
            while (( self.tb.ber()<=0.56) and (not self.arreter_calcul)):              
                try :
                    if (math.isinf(self.tb.ber()) or math.isnan(self.tb.ber()) or math.isinf(self.tb.snr()) or math.isnan(self.tb.snr())):
                        continue
                    else:
                        self.calculMaxMin(self.tb.ber(), self.tb.snr())
                        self.calculSum(self.tb.ber(), self.tb.snr())
                        self.inc_nbr_values()
                        self.arreter_calcul = self.fenetre.get_arreter_calcul()
                except Exception:
                    print 'Application interrupted 1'  
                
                try:
                    time.sleep(1.0)
                except KeyboardInterrupt:
                    self.done = True
                
#            if (self.tb.get_compare_vector_decision()):
            
            print "Estimated SNR: %f dB  BER: %f " % ( self.tb.snr(), self.tb.ber())
            
            try:
                time.sleep(1.0)
            except KeyboardInterrupt:
                print 'Application interrupted 3'

            #Calcul la moyenne des parametres
            try :
                if ((self.get_nbr_value() != 0) and ( self.tb.ber()>0.60)):
                    self.calculAverage()
                    self.fenetre.afficher_param(self)
                    self.dac_courant = self.inc_dac_pas(self.dac_courant)
                    self.tb.set_compare_vector_decision(False)  
                    self.set_param()  
            except Exception:
                print 'Application interrupted 2'  
                
                      
        self.condition.notify()
        self.condition.release()

class Thread_Param_Calcul_Nbr (_threading.Thread, Param):
    
    def __init__(self, fenetre, condition, tb = None):
        _threading.Thread.__init__(self)
        Param.__init__(self)
        
        self.setDaemon(1)
        self.fenetre = fenetre
        self.arreter_calcul = self.fenetre.get_arreter_calcul()
        self.done = False
        self.tb = tb
        self.condition = condition
        
        self.init_param()
        self.start()

    def run(self):
        self.condition.acquire()
        nbr_values_local = self.fenetre.options.get_nbr_init()
        while nbr_values_local > 0 and not self.arreter_calcul :
            self.calculSum(self.tb.ber(), self.tb.snr())
            self.inc_nbr_values()
            
            print self.get_nbr_value()
            self.arreter_calcul = self.fenetre.get_arreter_calcul()
            try:
                time.sleep(1.0)
            except KeyboardInterrupt:
                self.done = True
            
            nbr_values_local -=1
                       
        self.condition.notify()
        self.condition.release()
      
    def init_param (self):
        self.set_dac_courant(self.fenetre.options.get_dac_init())
        self.set_distance(self.fenetre.options.get_distance())
        self.set_frequence(self.fenetre.options.get_frequence())
             
if __name__ == "__main__":
    
    app = wx.App()
    sizer = wx.GridBagSizer()
    frame = Form(sizer, None, -1, '***Receiver*** Performance Evaluation of Modulations BERT')
    
    app.MainLoop()

