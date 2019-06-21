#!/bin/sh

# Submits n jobs to the torque queing system

for i in {0..3}
do
  echo 'Start Job rev' $i "$i"
  python decoding_sigmas.py $i > jobs_output/decoding_sigmas$i.txt 2>&1     
  #echo "./job_kernel_CP_all_subjects.sh var1=$i" | qsub
  #sleep 1
done
echo "All send"
