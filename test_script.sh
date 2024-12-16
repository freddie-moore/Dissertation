#!/bin/bash

#SBATCH -c3 --mem=32g
#SBATCH --gpus 1
#SBATCH -p csug -q csug

source /usr2/share/gpu.sbatch

torchrun rl_main.py 