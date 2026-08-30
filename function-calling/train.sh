#!/bin/bash
# Training script for xLAM-2-8b-fc-r LoRA SFT
# Run from inside the LLaMA-Factory root directory

# Single GPU
# CUDA_VISIBLE_DEVICES=0 USE_MODELSCOPE_HUB=1 llamafactory-cli train xlam_lora_sft_8b.yaml

# Multi-GPU (2×)
# CUDA_VISIBLE_DEVICES=0,1 USE_MODELSCOPE_HUB=1 llamafactory-cli train xlam_lora_sft_8b.yaml

# Background with logging
mkdir -p logs
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="logs/train_${TIMESTAMP}.log"

CUDA_VISIBLE_DEVICES=0 USE_MODELSCOPE_HUB=1 \
    nohup llamafactory-cli train xlam_lora_sft_8b.yaml \
    > "$LOG_FILE" 2>&1 &

echo "Training started (PID: $!)"
echo "Log: $LOG_FILE"
echo "Monitor: tail -f $LOG_FILE"
