#!/bin/bash

#defined required Rscripts
RSCRIPT=~/Genotipi/Genotipi_CODES/Add_MS_to_bgl.R
RSCRIPT1=~/Genotipi/Genotipi_CODES/MergePhasedSampleAndRef.R

#directories to sample and reference files
DIRS=/home/janao/Genotipi/MS_Imputation/MS_03062016 # set directory to the sample unphased beagle files - transformed from ped with fcgene, all SNPs and no MS
DIRP=/home/janao/Genotipi/MS_Imputation/MS_03062016/BeagleImputed1000it # set directory to phased file
DIRR=/home/janao/Genotipi/MS_Imputation/beagle #directory to the reference files
DIRA=/home/janao/Genotipi/MS_Imputation/MS_03062016/AddingToRef #directory to store the new ref files

#write a loop to read sample unphased bgl file, add lab MS and add to the reference file for all the chromosome carrying 12 MS
#for i in 1 2 3 5 9 15 16 18 19 20 21 23
#do
#	#first copy the R script to modify the names  to process the current chromosome file
#	cp $RSCRIPT .
#	sed -i "s%ChromosomePhasedFile%$DIRP/Chr${i}_1000it.Chr${i}ImpBase.bgl.phased%g" $PWD/Add_MS_to_bgl.R #phased Beagle file to provide the list of SNps required
#	sed -i "s%ChromosomeSampleBeagleFile%$DIRS/Chr${i}.bgl%g" $PWD/Add_MS_to_bgl.R #unphased BEagle sample file - contains all the SNP and no MS
#	sed -i "s%ChrOfTheMS%${i}%g" $PWD/Add_MS_to_bgl.R #MS sequence according to chromosome
#	sed -i "s%FinalFilePathAndName%$DIRS/Chr${i}Sample.bgl%g" $PWD/Add_MS_to_bgl.R
#	sed -i "s%MarkerFile%$DIRR/MinSNP+MS_06112013_chr${i}.txt%g" $PWD/Add_MS_to_bgl.R
#	#!/usr/bin/enc Rscript
#	Rscript $PWD/Add_MS_to_bgl.R
#	#phased newly created Sample MinSNPset + MS chromosome bgl file with reference chromosome file
#	java -Xmx1000m -jar ~/bin/beagle3.jar unphased=$DIRS/Chr${i}Sample.bgl missing=? niterations=100 out=SamplePhasedChr${i} 
#	#rm *Sample.bgl
#	less $DIRS/Chr${i}Sample.bgl | wc -l
#	less $DIRR/p_IDB+MS_BT_ref_20150715_chr${i}.bgl.phased | wc -l
#	rm SamplePhased*.log
#	#rm SamplePhased*.r2
#done

#additional parameters for Beagle
#phased=$DIRR/p_IDB+MS_BT_ref_20150715_chr${i}.bgl.phased markers=$DIRR/MinSNP+MS_06112013_chr${i}.txt

#mv *gz $DIRA
cd $DIRA
#gunzip *


#add newly phased sample to the reference
for i in 1 2 3 5 9 15 16 18 19 20 21 23
do
	#first copy the R script from the original directory 
	cp $RSCRIPT1 .
	#edit input files for each of the 12 chromosomes
	sed -i "s%ReferenceFile%$DIRR/p_IDB+MS_BT_ref_20150715_chr${i}.bgl.phased%g" $PWD/MergePhasedSampleAndRef.R #phased Beagle file to provide the list of SNps required
	sed -i "s%NewPhasedFile%$DIRA/SamplePhasedChr${i}.Chr${i}Sample.bgl.phased%g" $PWD/MergePhasedSampleAndRef.R
	sed -i "s%MarkerFile%$DIRR/MinSNP+MS_06112013_chr${i}.txt%g" $PWD/MergePhasedSampleAndRef.R
	sed -i "s%AddedReference%$DIRA/NewRefChr${i}.bgl%g" $PWD/MergePhasedSampleAndRef.R
	#!/usr/bin/enc Rscript
	Rscript $PWD/MergePhasedSampleAndRef.R
	#remove the script before new loop turn
	rm MergePhasedSampleAndRef.R
done

rm *SamplePhased.bgl
rm *Ref.bgl
rm *Ref_.bgl
rm *phased.phased



#this did not work because some reference files had less marker than marker file (Chromosome 9)
#	#extract Min CHR SNPs (which is in the Phased / now Sample) file from second file Ref (contains more SNPs) based on line in the first file - print the COMMON elements in both files
#	awk 'FNR==NR{a[$1];next}($2 in a){print}' $DIRR/MinSNP+MS_06112013_chr${i}.txt Chr${i}Ref.bgl  > Chr${i}RefRef.bgl
#	awk 'FNR==NR{a[$2];next}($2 in a){print}' Chr${i}SamplePhased.bgl Chr${i}Ref.bgl  > Chr${i}RefRef.bgl
#	#remove M and markername columns from Reference File
#	cut -f3- -d " " Chr${i}RefRef.bgl > Chr${i}Ref_.bgl
#	#paste together Sample bgl and Ref bgl files with MinSNP set for the chromosome
#	paste Chr${i}SamplePhased.bgl Chr${i}Ref_.bgl > Chr${i}RefAdded.bgl

#don't need to capitalise since both files are outputs of Beagle
#	#capitalise both files - old reference and the sample to add
#	sed 's/.*/\U&/' SamplePhasedChr${i}.Chr${i}Sample.bgl.phased > Chr${i}SamplePhased.bgl
#	sed 's/.*/\U&/' $DIRR/p_IDB+MS_BT_ref_20150715_chr${i}.bgl.phased > Chr${i}Ref.bgl

