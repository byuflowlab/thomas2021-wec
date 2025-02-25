#!/bin/bash

#SBATCH --time=48:00:00   # walltime
#SBATCH --ntasks=1   # number of processor cores per sub-job(i.e. tasks)
#SBATCH --mem-per-cpu=3G  # memory per CPU core
#SBATCH -J '38 t 12 d alg: ps. wec method: none. # job name'
#SBATCH --mail-user=jaredthomas68@gmail.com   # email address
#SBATCH --mail-type=BEGIN
#SBATCH --mail-type=END
#SBATCH --array=116,191,188,198,197,195,115,93,46,49     # job array of size 200

echo ${SLURM_ARRAY_TASK_ID}

model_number=2
op_alg_number=2
wec_method_number=0
maxwec=1
nsteps=1

python3 opt_mstart_38turbs_12dirs.py ${SLURM_ARRAY_TASK_ID} $wec_method_number $model_number $op_alg_number $maxwec $nsteps
