#This is a script to add newly genotyped individuals and downloaded GeneSeek zip file (Final Reports)
#to the existing database of the latest genotypes

#Pipeline:
#1)define chip, dictionary, dictionary to hold chip: genotype package: animal ids, dictionary to hold genotype package : download date
#2)create temp directory within breed_TEMP/DownloadDate
#3)create directory if not existin, unzip file
#4)for each genotype package: unzip Final report and SNP_Map, change spurious strings within the files and adjust peddar.param file
#run peddar_row to transform FinalReports to PLINK and MAP formats
#write names to dictionaries


import os
import sys
import zipfile
import shutil
from collections import defaultdict
import csv
import GenFiles
import commands
import pandas as pd
from colorama import init, Fore, Back, Style
init()




########################################################
#set directories and file names
########################################################
#date=13012017
#pasma="Rjava"
#AlleleFormat="ab"
#zip_file="Matija_Rigler.zip"
#merge_ask='N'
#Ask the user for the current date (date of download) and breed
date = raw_input("Enter the date (today): ")
pasma = raw_input("Enter the breed: ") 
AlleleFormat=raw_input("Enter the desired allele coding [top / forward / ab]: ")
merge_ask=raw_input("Do you want to merge newly downloaded genotypes to the Latest Genotypes files (by chip)? [Y/N] ")
#ask what action does the user want to perform
action = raw_input("Do you want to extract SNPs for parental verification  [Y/N] ")
if action == 'Y':
    PVSNPs = input("How many SNPs would you like to use for parental verification? ")


#create directory path to hold current temp genotype files within Genotipi_DATA and breed directory
tempDir = "/home/janao/Genotipi/Genotipi_DATA/"+pasma+"_TEMP/Genotipi_"+date+"/"
#PEDDAROW directory
peddarow="/home/janao/Genotipi/Genotipi_CODES/SNPchimpRepo/source_codes/PEDDA_ROW"
#Zip latest
#Zip_lat="/run/user/1000/gvfs/smb-share:server=kis-h2.si,share=kisdfs/ZIV/vol1/ZIV/VSI/JanaO/"+pasma+"/ZipGenoFiles/"
Zip_lat="/home/janao/Genotipi/TEST/"

#Genotipi_latest directory
Gen_lat = "/home/janao/Genotipi/Genotipi_DATA/Genotipi_latest/"+pasma+"/"
#File with a list of 800 SNPs for parentage verification
SNP800="/home/janao/Genotipi/ParentalVerification_SNPSNP/Names_800SNPs.txt"
#path to Zanardi
ZanDir="/home/janao/Genotipi/Genotipi_CODES/Zanardi"
#file with IDs and seq for the animals
RJ_IDSeq="/home/janao/Genotipi/Genotipi_CODES/Rjave_seq_ID.csv"
#SNP coding
SNPSifrant="/home/janao/Genotipi/ParentalVerification_SNPSNP/Sifrant_SNP.csv"



##########################################################################################################
##########################################################################################################
#create dictionaries
##########################################################################################################
##########################################################################################################

#create a dictionary of the number of SNPs and corresponding chip names
chips = GenFiles.chips
SNP800Sifrant_Dict = GenFiles.SNP800Sifrant_Dict

GenoFile = defaultdict(set)
SampleIDs = defaultdict(list)
PedFiles = defaultdict(list)
MapFiles = defaultdict(list)
AllInfo = []
#dictionary to hold downlaod date of the genotype package   
DateDownloaded = defaultdict(list)
DateGenotyped = defaultdict(list)

#list to hold the SNP800 files produced in the run
SNP800_Peds=[]
SNP800_Maps=[]


#read in animal ID / Seq / DateOfBirth / SexCode table
#create a dictionary
Rj_IDSeq_Dict = defaultdict()
with open(RJ_IDSeq, 'rb') as IDSeq:
    reader = csv.reader(IDSeq, delimiter=',')
    for line in reader:
        Rj_IDSeq_Dict[line[0]] = line[1:]
        

############################################################################################################
#############################################################################################################
#create a directory with the current date for temp genotype manipulation
if not os.path.exists(tempDir):
    os.makedirs(tempDir)


#change current working directory to the created directory
os.chdir(tempDir)

#create a list of all latest zip packages with FinalReports
#extract the FinalReport from each of them and SNPMap
zipPackages = (filter(lambda x: x.endswith('.zip'), os.listdir(Zip_lat)))
    
for zipPackage in zipPackages:
    shutil.copy(Zip_lat+zipPackage, tempDir)
    onePackage=GenFiles.genZipPackage(zipPackage)
    if not onePackage.finalreportname:
        print (Back.RED + "No FinalReport in {}".format(zipPackage))
        pass
    elif onePackage.finalreportname:
        onePackage.extractFinalReport()
        onePackage.extractSNPMap()
        os.remove(zipPackage)
        
        #copy pedda.param and python script to the current directory
        shutil.copy((peddarow+"/peddar.param"), "peddar.param")
        shutil.copy((peddarow+"/pedda_row.py"), "pedda_row.py")
        #replace strings with shell command
        os.system('sed -i "s/test_FinalReport.txt/"'+onePackage.name+'_FinalReport.txt'+'"/g" peddar.param') #insert FinalReport name into peddar.param
        os.system('sed -i "s|Dominant |Dominant_|g" ' + onePackage.name+'_FinalReport.txt') #problem Dominant Red with a space
        os.system('sed -i "s|Dominant |Dominant_|g" ' + onePackage.name+'_SNP_Map.txt') ##problem Dominant Red with a space
        os.system('sed -i "s/test_outputfile/"'+onePackage.name+'"/g" peddar.param') #insert OutPut name into peddar.param
        os.system('sed -i "s/test_SNPMap.txt/"'+onePackage.name+'_SNP_Map.txt'+'"/g" peddar.param') #insert SNPMap name into peddar.param
        os.system('sed -i "s/AlleleFormat/"'+AlleleFormat+'"/g" peddar.param') #insert desired AlleleFormat name into peddar.param
        os.system('sed -i "s/TEST/"'+pasma+'"/g" peddar.param')
        os.system("python pedda_row.py") #transform into ped and map file
        
        
        #remove FinalReport and SNPMap
        os.remove(onePackage.name+'_FinalReport.txt')
        os.remove(onePackage.name+'_SNP_Map.txt')
    
        #make pedfile a GenFiles pedFile object
        pedfile=GenFiles.pedFile(onePackage.name +  '.ped')     
        mapfile=GenFiles.mapFile(onePackage.name +  '.map')
        
        ##########################################################
        #add file to the dictionary of chip files
        ###########################################################
        PedFiles[pedfile.chip].append(tempDir+pedfile.pedname)
        MapFiles[pedfile.chip].append(tempDir+mapfile.mapname)
        GenoFile[pedfile.chip].add(pedfile.name)
        DateDownloaded[date] += (pedfile.name)
        DateGenotyped[onePackage.genodate] += [(x, pedfile.chip) for x in (pedfile.samples)]
        AllInfo += [(x, pedfile.chip, pedfile.name, pedfile.genodate) for x in (pedfile.samples)]
        for i in pedfile.samples:
            if i in Rj_IDSeq_Dict:
                SampleIDs[i] = [Rj_IDSeq_Dict.get(i)[0], pedfile.genodate, pedfile.chip, date]
            else: 
                print "Sample ID " + i + " not found!!!"
     
     
        ##############################################################    
        #extract the 800 SNPs
        ##############################################################
        if action == 'Y':
            pedfile.extractParentalSNPs(PVSNPs)
    
        SNP800_Peds.append(os.getcwd()+"/ParentalSNP"+str(PVSNPs)+"_"+pedfile.sernum+".ped")
        SNP800_Maps.append(os.getcwd()+"/ParentalSNP"+str(PVSNPs)+"_"+pedfile.sernum+".map")

    

################################################################################################
###############################################################################################
#END OF THE LOOP
#merge produced SNP800 files
#merge ped files if merge_ask = Y
#create table for govedo
#############################################################################################
###############################################################################################
print "The number of genotyped animals is {}.".format(len(SampleIDs))
print "The number of genotype packages (different date of genotyping) is {}.".format(len(DateGenotyped))
print "The number of different genotyping chips is {0}: {1}.".format(len(PedFiles), PedFiles.keys())

#merge SNP800 files
#first check whether there are more than one SNP800 files
if len(SNP800_Peds) == len(SNP800_Maps) & len(SNP800_Peds) != 1:
    # write a --merge-list file for plink with all the SNP800 file on the download date
    with open('SNP800_List.txt', 'w') as csvfile:
        writer = csv.writer(csvfile, delimiter=" ")
        [writer.writerow(r) for r in zip(SNP800_Peds[1:], SNP800_Maps[1:])] #leave the first one out - that goes in the plink command line
    #merge with plink
    mergecommand = "plink --file {0} --cow --merge-list {1} --recode --out {2}".format((SNP800_Peds[0].strip(".ped")),"SNP800_List.txt", str(date)+"_SNP800") 
    status, output = commands.getstatusoutput(mergecommand)
    if status == 0:
        for i in filter(lambda x: x.startswith("Parental"), os.listdir(tempDir)):
            os.remove(i)
elif len(SNP800_Peds)==1 & len(SNP800_Maps) == 1: #if there is only one genoPackage, then just copy the SNP800 file and rename it to date_SNP800
    print "Only one SNP800 file"
    shutil.move(SNP800_Peds[0], tempDir+"/"+str(date)+"_SNP800.ped")
    shutil.move(SNP800_Maps[0], tempDir+"/"+str(date)+"_SNP800.map")
elif len(SNP800_Peds) != len(SNP800_Maps): #if the number of SNP800 ped and map files is not the same, report an error
    print "The length of Ped and Map SNP800 List are not equal, check for inconsistences and errors"


######################################################################################
#create a table of individuals for govedo   
#columns are seq, chip, date genotyped  
GenotypedInd = pd.DataFrame.from_dict(SampleIDs, orient='index', dtype=None)
GenotypedInd.columns = ['ZIV_ID_SEQ','GenoDate','Chip','DownloadDate']
GenotypedInd.to_csv(path_or_buf = tempDir+date+'_GovedoInd.csv', sep=",", index=False  )
######################################################################################


#create a table of SNPs for parental verification
parentalTable = pd.read_table(str(date)+'_SNP800.ped', sep=" ", header=None)
parentalTable = parentalTable.drop(parentalTable.columns[[0,2,3,4,5]], axis=1)

#ind800SNP = pd.DataFrame({'ID' = Rj_IDSeq_Dict['SI04640608']*1600, 
ped800 = GenFiles.pedFile(str(date)+"_SNP800.ped")
map800 = GenFiles.mapFile(str(date)+"_SNP800.map")

AlleleCodes = []
for i in map800.snps:
    AlleleCodes.append((i, min(SNP800Sifrant_Dict[i])))
    AlleleCodes.append((i, max(SNP800Sifrant_Dict[i])))
    
    
IndSNPs = []
for sampleID in ped800.samples:
    for (value, (snpname, code)) in zip(ped800.individualSNPsList(sampleID), AlleleCodes):
        try:
            IndSNPs.append((Rj_IDSeq_Dict.get(sampleID)[0], value, code))
        except:
            print sampleID


IndSNPsDF = pd.DataFrame(IndSNPs)
IndSNPsDF.to_csv(('{0}_Govedo{1}SNPs.csv'.format(date,str(PVSNPs))), index=None, header=False)
######################################################################################

 
#check whether the number of individuals in all genoPackages corresponds to the number of individuals with extracted 800SNPs for parentage testing
if len(SampleIDs) == len(ped800.samples):
    print "The number of individuals corresponds to the number of individuals in SNP800 ped file"
else: 
    print "The number of individuals DOES NOT correspond to the number of individuals in SNP800 ped file, check for ERRORS!"

######################################################################################


if merge_ask == 'Y':
#merge is outside the loop
#merge all the chips needed updating
    for i in PedFiles:
        if not os.path.exists(Gen_lat+str(i)): #if the chip directory does not exist create it
            os.makedirs(Gen_lat+str(i))
        os.chdir(Gen_lat+str(i))
        shutil.copy("/home/janao/Genotipi/Genotipi_CODES/PARAMFILE.txt", Gen_lat+i)
        pedToMerge = ",".join(PedFiles[i]).strip("'")
        mapToMerge = ",".join(MapFiles[i]).strip("'")
        if not os.path.isfile(Gen_lat+i+'/PLINK_MERGED.ped'): #if there is no prior PLINK_MERGED file, merge all the ped files in this step, onto othe first one
            with open('MergeChip.txt', 'w') as csvfile:
                writer = csv.writer(csvfile, delimiter=" ")
                [writer.writerow(r) for r in zip(PedFiles[i][1:], MapFiles[i][1:])] #leave the first one out - that goes in the plink command line
        #merge with plink
            mergeChipCommand = "plink --file {0} --cow --merge-list {1} --recode --out PLINK_MERGED".format((PedFiles[i][0].strip(".ped")), 'MergeChip.txt')
        if os.path.isfile(Gen_lat+i+'/PLINK_MERGED.ped'): #if there is PLINK_MERGED, merge onto that one
            with open('MergeChip.txt', 'w') as csvfile:
                writer = csv.writer(csvfile, delimiter=" ")
                [writer.writerow(r) for r in zip(PedFiles[i], MapFiles[i])] 
        #merge with plink
            mergeChipCommand = "plink --file PLINK_MERGED --cow --merge-list {0} --recode --out PLINK_MERGED".format('MergeChip.txt')
        status, output = commands.getstatusoutput(mergeChipCommand)
        if status == 0:
           print "Successfully merged" + str(i)
        else:
            print "Merging went wrong, error: " + str(status)
        
