#!/bin/bash

####################################################
#SCRIPT TO RUN IMPUTATION FROM SMALLER TO LARGER CHIP
#RUN FROM STEPX DIRECTORY
####################################################
STEP=1 #<-- CHANGE!
SCHIP=GGP #<-- CHANGE!
LCHIP=GP4 #<-- CHANGE!
#EXCLUDE=/home/janao/Genotipi/Genotipi1_12042016/StepImputation/Step$STEP/Exclude_from_Small.txt #SmallChip exclusive SNPs
SMALLPLINK=/home/janao/Genotipi/Genotipi1_12042016/StepImputation/Step1/GGP_exc #input imputed file from the PREVIOUS  step
LARGEPLINK=~/Genotipi/Genotipi03062016/PLINK_genotypeFiles/$LCHIP/OUTPUT/PLINK_MERGED
LARGEPLINK2=/home/janao/Genotipi/Genotipi1_12042016/StepImputation/Step2/GP3_exc 
LARGEPLINK3=/home/janao/Genotipi/Genotipi1_12042016/StepImputation/Step3/HD_exc
LARGEPLINK4=/home/janao/Genotipi/Genotipi1_12042016/StepImputation/StepAllInOne/HD138K_exc
LARGEPLINK5=/home/janao/Genotipi/Genotipi1_12042016/StepImputation/Step4/50K_exc
SNPSETS=/home/janao/Genotipi/Genotipi1_12042016/StepImputation/Step$STEP/CVSNPset
CLUSTERFILE=/home/janao/Genotipi/Genotipi1_12042016/StepImputation/Step$STEP/SNP_Cluster.txt
INDCLUSTER=/home/janao/Genotipi/Genotipi1_12042016/StepImputation/Step$STEP

rm Conc*

#Rscript 
echo "Did you run the R script to obtain exclude and cluster files?"
echo "Did you change the input file variables?"
echo "Did you comment out metge two large plink files?"

#first exclude the exclusive GGP SNPs from GGP file
~/bin/plink --file $SMALLPLINK --cow --chr 1-29 --recode --out ${SCHIP}_exc

#merge GP3 and GGP3 maps together
~/bin/plink --file  $LARGEPLINK --cow --chr 1-29 --recode --out LARGEPLINK1 #${LCHIP}
~/bin/plink --file  LARGEPLINK1 --cow --merge $LARGEPLINK2.ped $LARGEPLINK2.map --chr 1-29 --recode --out LARGEPLINK2
~/bin/plink --file  LARGEPLINK2 --cow --merge $LARGEPLINK3.ped $LARGEPLINK3.map --chr 1-29 --recode --out LARGEPLINK3
~/bin/plink --file  LARGEPLINK3 --cow --merge $LARGEPLINK4.ped $LARGEPLINK4.map --chr 1-29 --recode --out LARGEPLINK4
~/bin/plink --file  LARGEPLINK4 --cow --merge $LARGEPLINK5.ped $LARGEPLINK5.map --chr 1-29 --recode --out ${LCHIP}

#create a file with variants with the same physical position
cut -d ";" ./OUTPUT/Error_SNP_position.txt -f1 | tail -n +2 > SamePosSNP.txt

#Exclude these SNPs from PLINK files
~/bin/plink --file ${SCHIP}_exc --cow --exclude SamePosSNP.txt --recode --out ${SCHIP}_exc
~/bin/plink --file ${LCHIP} --cow --exclude SamePosSNP.txt --recode --out ${LCHIP}

#Extract individuals FID and ID from the genotype files - in order to create a cluster individuals file
cut -d " " -f1,2 ${SCHIP}_exc.ped > ${SCHIP}_ind.txt
cut -d " " -f1,2 ${LCHIP}.ped > ${LCHIP}_ind.txt


#mask every tenth SNP 
#first mask 1/10 SNPs each time and produce 10 bed/bim/fam files
for i in 1 2 3 4 5 6 7 8 9 10
do

#create individual cluster file with all the inviduals on the lower chip masked (assigned to a cluster 1-10)
#awk script to add Cluster CX number to the third column
	awk -v column=3 -v value="C$i" '
	    BEGIN {
	        FS = OFS = " ";
	    }
	    {
		for ( i = NF + 1; i > column; i-- ) {
		    $i = $(i-1);
		}
		$i = value;
		print $0;
	    }
	' ${SCHIP}_ind.txt > ${SCHIP}_ClustInd$i.txt


	~/bin/plink --file ${SCHIP}_exc --cow --zero-cluster $CLUSTERFILE --within ${SCHIP}_ClustInd$i.txt --make-bed --out ${SCHIP}_Masked$i
	~/bin/plink --bfile ${SCHIP}_Masked$i --recode --cow --out ${SCHIP}_Masked$i



####################################################3
#Impute all 10 Masked files
#######################################################

	cp /home/janao/Genotipi/Genotipi1_12042016/PARAMFILE.txt .
	sed -i "s%PathToPed%$PWD/${SCHIP}_Masked$i.ped,$PWD/${LCHIP}.ped%g" PARAMFILE.txt #change ped file input 
	sed -i "s%PathToMap%$PWD/${SCHIP}_Masked$i.map,$PWD/${LCHIP}.map%g" PARAMFILE.txt #change map file input
	sed -i "s%OutputName%ImpMasked${i}%g" PARAMFILE.txt #change output name
	python ~/Genotipi/Zanardi/Zanardi.py --fimpute --save
	rm PARAMFILE.txt
#########################################################################
#a script to extract SNPs from 10 imputed MergeMasked files and one original genotype file
#extract a different subset of SNPs each time
#also check concordance simultaneously
#############################################################################

	~/bin/plink --file ${SCHIP}_exc --extract ${SNPSETS}${i}.txt --cow --recode --out Genotyped$i #extract masked SNPs from merged genotype file
	~/bin/plink --file OUTPUT/FIMPUTE_ImpMasked$i --extract ${SNPSETS}${i}.txt --cow --recode --out Imputed$i #extract masked and imputed SNPs from a file
	~/bin/plink --file Genotyped$i --merge Imputed$i.ped Imputed$i.map --merge-mode 7 --cow --recode --out Concordance$i 
	grep "for a concordance rate" Concordance$i.log > Conc_num$i.txt
done;

cat Conc_num* > Concordance_num.txt
grep -o ' 0.*' Concordance_num.txt > Conc_num.txt
sed -i 's/\.$//' Conc_num.txt
awk '{ sum += $1 } END { if (NR > 0) print sum / NR }' Conc_num.txt > Concordance_avg.txt

##############################################
#impute non-masked files to obtain imputated genotypes for all the SNPs
###############################################
cp /home/janao/Genotipi/Genotipi1_12042016/PARAMFILE.txt .
sed -i "s%PathToPed%$PWD/${SCHIP}_exc.ped,$PWD/${LCHIP}.ped%g" PARAMFILE.txt #change ped file input 
sed -i "s%PathToMap%$PWD/${SCHIP}_exc.map,$PWD/${LCHIP}.map%g" PARAMFILE.txt #change map file input
sed -i "s%OutputName%Imputed%g" PARAMFILE.txt #change output name
#python ~/Genotipi/Zanardi/Zanardi.py --fimpute --save


