#!/bin/sh

#PBS -q batch
#PBS -l walltime=1500:00:00
#PBS -l nodes=node041:ppn=3
#PBS -l pmem=10gbs

# -- run in the current working (submission) directory --
cd $PBS_O_WORKDIR


chmod g=wx $PBS_JOBNAME
#echo $s
# FILE TO EXECUTE
python preprocess_s14.py 1> /mnt/homes/home024/gortega/jobs/$PBS_JOBID.out 2> /mnt/homes/home024/gortega/jobs/$PBS_JOBID.err
#python prova_qsub.py  ${foo} 1> /mnt/homes/home024/gortega/jobs/$PBS_JOBID.out 2> /mnt/homes/home024/gortega/jobs/$PBS_JOBID.err
