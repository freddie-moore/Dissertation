#!/bin/bash

#SBATCH -c3 --mem=32g
#SBATCH --gpus 1
#SBATCH -p csug -q csug

source /usr2/share/gpu.sbatch

# Generate a random port in the range 1024-65535
PORT=$((1024 + RANDOM % 64511))

torchrun --nproc_per_node=1 --master_port=$PORT rl_main.py 