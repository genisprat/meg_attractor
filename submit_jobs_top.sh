#!/bin/sh

# Submits n jobs to the torque queing system

for i in {0..12}
do
  echo 'Start Job rev' $i "$i"
  qsub -v foo="$i" job_decoding_all_subjects.sh  
  #echo "./job_kernel_CP_all_subjects.sh var1=$i" | qsub
  sleep 1
done

