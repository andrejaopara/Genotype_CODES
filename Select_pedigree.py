# -*- coding: utf-8 -*-
from __future__ import division
from collections import defaultdict
import pandas as pd
import numpy as np
from collections import defaultdict
import random
#reload(selection)
#from selection import *
# -*- coding: utf-8 -*-

#############################################33
#tukaj naštimaj parametre
#1) odstotki živali v kateogorijah
#nT = 20000 # velikost populacije
#perF = 0.9
#perM = 0.1 # odstotki ženskih in moških živali v aktivni populaciji
#odstotki kategorij znotraj spola
stNB = 6700

nrF = stNB * 0.5
tel = 0.966
pt = 0.85 #koliko jih pride do telic
kraveRemont = 0.25
bm = 0.0127 #TO JE OD KRAV!!!
#sum([nrF, ptel, tel, pt24, t24, k])


nrM = 0.55
mladi = 0.17777778 #TO JE ZNOTRAJ POTOMCEV NAČRTNIH PARJENJ
bik12 = 0.40
pripust = 0.0135 #TO JE ZNOTRAJ BIKOV 12!!!!
#cakajoci = 0.018 #to je znotraj bikov12!!!!!
bik24 = 0.05
potomciNP = 0.0134 #%OD NOVOROJENIH
vhlevljeni = 0.6 #TO JE ODSTOTEK OD POTOMCEV NAČRNIH PARJENJ


pb = 0.5 #KOLIKO OD MLADIH POSTANE TESTIRANIH
nrM + bik12 +  bik24 

#2)števila let v uporabi
kraveUp = 4 #povprečno koliko let so krave v populaciji (koliko laktacij)
bmUp = 3 # koliko let so v uporabi BM - REMONT!
cak = 4 #koliko časa so mladi biki v testu oz. koliko časa so čakajoči
pbUp = 5 #koliko let so povrpečno v uporabi biki v AI
pripustUp = 1.4 # koliko let so v uporabi biki v pripustu
genomUp = 1.3 #koliko let so povprečno v uporabi genomsko testirani biki

##################################################################################################################3
##################################################################################################################3
#od tu naprej samo delo s parametri = spremenvljivkami
##################################################################################################################3

#številke
#ženske
nrFn = int(stNB * 0.5)

teln = int(tel * nrFn)
ptn = int(pt* teln)
bmn = int(round(ptn * kraveUp *bm)) #to je od vseh krav
#kn = int(k * nF)
#bmn = int(bm * k * nF)
#sum([nrFn, pteln, teln, pt24n, t24n, kn])

nM = 0.5
nrMn = int(round(stNB * nM))
bik12n = int(round(bik12 * nrMn))
bik24n = int(round(bik24 * nrMn))
potomciNPn = int(round(potomciNP * nrMn))
mladin = int(round(mladi * potomciNPn)) ###Mladi: mladin = int(nrM * nM * mladi)
vhlevljenin  = int(round(potomciNPn * vhlevljeni))
#cakajocin = int(cakajoci* nM)
pripustTn = int(round((vhlevljenin - mladin)*pripustUp))
pripust1n = vhlevljenin - mladin
pripust2n = pripustTn - pripust1n
pbn = int(pb * mladin)
#sum([nrMn, bik12n, bik24n, cakajocin, pripustn, pbn, mladin])
sum([nrMn, bik12n, bik24n])
##########################################################
#ženske
#odberi novorojene
#tu se ne rabiš obremenjevat s tem, katere so matere in kateri očetje - to narediš na koncu, ko konstruiraš novorojene za naslednjo gene
#ti novorojeni so že prva generacija
#na koncu potegni skupaj ID in kategorije ter to uporabi za določitev staršev#
#tudi šele tam se ukvarjaj z [pb]
reload(selection)
import selection
from selection import *
ped = pedigree("~/Documents/PhD/Simulaton/Pedigrees/PedPython.txt")    

###################################
#loop za vajo
#################################

 #tretja odbira
 #TUKAJ NE MOREŠ ODBIRATI PO EBV DOKLER DA NIMAŠ ZGENERIRANIH! - zato random za vajo
stevilo_krogov = 8

for krog in (range(0,stevilo_krogov)):
    if krog == 0:
        ped.set_cat_gen(max(ped.gen), "nr") #to je samo na prvem loopu
        categories = ped.save_cat()
        ped = pedigree("~/Documents/PhD/Simulaton/Pedigrees/PedPython.txt")
        ped.set_sex(0, nrFn, "F") #choose female new borns from generation before
        #prva odbira
        ped.compute_age()        
        select_age_0_1(ped)
        ped.add_new_gen_naive(stNB)
            
        categories.clear()
        categories = ped.save_cat()
        sex = ped.save_sex()
    
    if krog == 1:
        #druga odbira
        ped.set_cat_gen(1, "")
        ped.set_cat_gen(2, "")
        ped.set_cat_old('izl', 'izl', categories)
        
        ped.compute_age()        
        select_age_0_1(ped) 
        select_age_1_2(ped)
        
        ped.add_new_gen_naive(stNB)  
        
        categories.clear()
        categories = ped.save_cat()
        sex = ped.save_sex()
        active = ped.save_active()
        age = ped.save_age() 
    
    if krog >= 2:
        for i in ped.gens():
            ped.set_cat_gen(i, "")
            
        ped.set_cat_old('izl', 'izl', categories) 

        ped.compute_age()        
        select_age_0_1(ped)
        select_age_1_2(ped)

        select_age_2_3(ped)
        
        ped.add_new_gen_naive(stNB)  
        
        categories.clear()
        categories = ped.save_cat()
        sex = ped.save_sex()
        active = ped.save_active()
        age = ped.save_age() 

#dodaj starše novorojenim
#MATERE
bmMother = ped.select_mother_random('bm', 100)

ped.set_mother(bmMother) #

mother = ped.select_mother_EBV_top('k', int(round(11000*0.7))) #tukaj odberi brez tistih, ki so za gospodarsko križanje
motherOther = random.sample(mother, (stNB - len(bmMother)))

ped.set_mother(motherOther) #TUKAJ SO DOLOČENE SEDAJ VSE MATERE!!!

#OČETJE
testirani = ped.catCurrent_indiv('pripust1') | ped.catCurrent_indiv('pripust2') | ped.catCurrent_indiv_age('pripust1')


        """TOLE NI NAJBOLJŠE!        
def selekcija_ena_gen(pedFile):
    ped = pedigree(pedFile) 
       
    if max(ped.gens()) == 1:
        print "PRVA SELEKCIJA"
        ped.set_cat_gen(max(ped.gen), "nr") #to je samo na prvem loopu
        categories = ped.save_cat()
        ped = pedigree(pedFile)
        ped.set_sex(0, nrFn, "F") #choose female new borns from generation before
        #prva odbira
        select_age_0_1(ped)
        ped.add_new_gen_naive(stNB)
            
        categories.clear()
        categories = ped.save_cat()
        sex = ped.save_sex()

        
    elif max(ped.gens()) == 2:
        print "DRUGA SELEKCIJA"
        #druga odbira
        ped.set_cat_gen(1, "")
        ped.set_cat_gen(2, "")
        ped.set_cat_old('izl', 'izl', categories)
        
        select_age_0_1(ped) 
        select_age_1_2(ped)
        
        ped.add_new_gen_naive(stNB)  
        
        categories.clear()
        categories = ped.save_cat()
        sex = ped.save_sex()
        active = ped.save_active()
        age = ped.save_age() 
    
    elif max(ped.gens()) >= 3:
        print "TRETJA SELEKCIJA"
        for i in ped.gens():
            ped.set_cat_gen(i, "")
            
        ped.set_cat_old('izl', 'izl', categories) 
        
        select_age_0_1(ped)
        select_age_1_2(ped)
        ped.compute_age()
        select_age_2_3(ped)
        
        ped.add_new_gen_naive(stNB)  
        
        categories.clear()
        categories = ped.save_cat()
        sex = ped.save_sex()
        active = ped.save_active()
        age = ped.save_age() """
##############################################################################################3
##############################################################################################3
##############################################################################################3    
    
#VEDNO NAJPREJ IZLOČI /ODBERI PO PV!!! - funckije za odbiro na random imajo pogoj, da je kateogrija prosta
def select_age_0_1(ped): #tukaj odbereš iz novorojenih živali tel, ptel in mlade bike, pripust1
    #FEMALES
    izlF = nrFn - teln#koliko jih izločiš
    ped.izloci_poEBV("F", izlF, "nr", categories) #tukaj jih izloči, funkcija v modulu
    ped.izberi_poEBV_top("F", (nrFn - izlF), "nr", "tel", categories) #izberi telice, ki jih osemeniš --> krave
    
    
    #MALES
    ped.set_sex(nrFn, (nrFn + nrMn), "M") #nastavi sex = M od zadnje novorojene teličke do
    izlM = nrMn - bik12n #choose female new borns from generation before
    ped.izberi_poEBV_top( "M", vhlevljenin, "nr", "vhlevljeni", categories) #odberi mlade TO SAMO NA ZAČETKU; POTEM POTOMCI BM IN ELITE!
    ped.izberi_random( "M", bik12n, "nr", "bik12", categories)
    ped.izloci_random( "M", (nrMn - bik12n - vhlevljenin),"nr", categories)
    

def select_age_1_2(ped): # tukaj odbereš nič pri kravah - razen, če so že bikovske matere, pripust 2, bike24

    currentGen = max(ped.gens())-1
    #FEMALES
    ped.izberi_poEBV_top("F", ptn, 'tel', 'pt', categories)
    ped.izloci_poEBV("F", (teln - ptn),'tel', categories) #terlice postanejo
   
    
    #MALES
    ped.izberi_poEBV_top( "M", mladin, "vhlevljeni", "mladi", categories) #odberi mlade
    ped.izberi_poEBV_OdDo( "M", mladin, (mladin + (vhlevljenin - mladin)), "vhlevljeni", "pripust1", categories) #odberi v pripustu
    ped.izberi_random( "M", bik24n, 'bik12', 'bik24', categories)
    ped.izloci_random( "M", (bik12n - bik24n), 'bik12', categories)



#tukaj lahk daš vse v eno funkcijo - variabilno - koliko let krave, koliko let v testu
def select_age_2_3(ped):
    #FEMALES
    #najprej dodaj nove krave
    ped.set_cat_old('pt', 'k', categories) #osemenjene telice postanejo krave - predpostavimo, da vse
    #potem izloči najstarejše krave - po 4. laktaciji
    if ('k' in categories.keys()) and ((kraveUp+2) in ped.age()): #izloči koliko laktacij + 2 leti
        ped.izloci_age_cat((kraveUp+2), 'k', categories)
    #ostale krave prestavi naprej v krave - OZIROMA PODALJŠAJ STATUS!
    ped.set_cat_age_old(3, 'k', 'k', categories)
    ped.set_cat_age_old(4, 'k', 'k', categories) 
    ped.set_cat_age_old(5, 'k', 'k', categories)    
              
    #če imaš že dovolj stare krave, potem odberi BM
    #BM se odbira po drugi laktaciji - to je starost 3 - 4 (starost v pedigreju = 3, ker imaš tudi 0)
    if ('k' in categories.keys()) and (3 in ped.age()):
        ped.izberi_poEBV_top_age("F",3, int(bmn /bmUp), 'k', 'bm', categories) #izberi bikovske matere
    #in izloči najastarejše BM, če jih imaš
    if ('bm' in categories.keys()) and ((bmUp+3) in ped.age()):
        ped.izloci_age_cat((bmUp+3), 'bm', categories)
    #ostale BM prestavi naprej
    ped.set_cat_age_old(4, 'bm', 'bm', categories)
    ped.set_cat_age_old(5, 'bm', 'bm', categories)
    
    #MALES
    #mladi biki postanejo čakajoči (~1 leto, da se osemeni krave s semenom oz. malo po 2. letu)
    ped.set_cat_old('mladi', 'cak', categories) 
    ped.set_active_cat('mladi', 2, categories)
    
    #čakajočim bikov podaljšaj status (do starosti 5 let)
    #hkrati jim tudi nastavi status izl
    #ped.set_cat_age_old(2, 'cak', 'cak', categories)
    ped.set_cat_age_old(3, 'cak', 'cak', categories)
    ped.set_cat_age_old(4, 'cak', 'cak', categories)
    
    #povprečna doba v pripustu - glede na to odberi bike, ki preživijo še eno leto
    if 'pripust1' in categories.keys():
        ped.izberi_random( "M", pripust2n, 'pripust1', 'pripust2', categories)
        ped.izloci_random( "M", (pripust1n - pripust2n), 'pripust1', categories)

    #plemenske bike prestavljaj naprej
    ped.set_cat_old('pb', 'pb', categories)
    ped.izloci_cat('bik24', categories)
    ped.izloci_cat('pripust2', categories)
    if ('cak' in categories.keys()) and ((cak+1) in ped.age()):
        ped.izberi_poEBV_top_age("M", (cak +1), int(mladin * 0.5), 'cak', 'pb', categories)
        ped.set_active_cat('cak', 2, categories) #tukaj moraš to nastaviti, zato ker fja izberi avtomatsko nastavi na active=1
        ped.izloci_poEBV_age("M",(cak+1), int(mladin * 0.5), 'cak', categories) #TUKAJ MORA BITI ŠE STAROST!!!!!!!!!!!
    #plemenskim bikov po pbUp spremeni active
 
 
 """   
def select_age_3_4(ped):
    #FEMALES
    ped.set_cat_old('k2', 'k3', categories)
    
    
    #MALES
    ped.set_cat_old('mladi3', 'mladi4', categories)
 
def select_age_4_5(ped):
    #FEMALES
    #ped.set_cat_old('bm1', 'bm2', categories)
    ped.set_cat_old('k3', 'k4', categories)
    
    #MALES
    ped.set_cat_old('mladi4', 'mladi5', categories)
 
def select_age_5_6(ped):
    ped.set_cat_old('k4', 'k5', categories)
    #ped.set_cat_old('bm2', 'bm3', categories)
  """    


      