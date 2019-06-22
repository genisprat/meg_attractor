#!/bin/sh
source activate mne
which python
#echo $1 $2
for i in $@
do
	for j in {5..7} 
	do
		
		for k in {1..10}
		do	
			echo 'Start Job rev' $i $j $k		
			python /storage/genis/meg_attractor/attractor/extract.py $i $j $k &>> /storage/genis/meg_analysis_2018/jobs/sub$i-sesion$j-extract_output.txt 
		done
	done
done
