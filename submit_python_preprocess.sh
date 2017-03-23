#!/bin/sh

# Submits n jobs to the torque queing system

for i in {0..11}
do
  echo 'Start Job rev' $i "$i"
  python preprocess.py $i    
  #echo "./job_kernel_CP_all_subjects.sh var1=$i" | qsub
  #sleep 1
done
echo "All send"
