#!/bin/bash

#SBATCH -c6 --mem=32g
#SBATCH --gpus 2
#SBATCH -p csug -q csug

source /usr2/share/gpu.sbatch

# Generate a random port in the range 1024-65535
PORT=$((1024 + RANDOM % 64511))

torchrun --nproc_per_node=1 --master_port=$PORT trainingLoop.py
