#!/bin/bash
# Batch evaluation of all API models across all prompt strategies

mkdir -p results

PROVIDERS=("openai" "anthropic" "google" "qwen" "llama")
STRATEGIES=("unified" "optimized" "fewshot")

echo "=========================================="
echo "Batch API model evaluation"
echo "=========================================="

for provider in "${PROVIDERS[@]}"; do
    for strategy in "${STRATEGIES[@]}"; do
        echo ""
        echo "===================="
        echo "Evaluating: $provider - $strategy"
        echo "===================="

        python eval_api_models.py \
            --provider "$provider" \
            --prompt_strategy "$strategy" \
            --dataset_path data/test.json \
            --config_file api_config.json \
            --num_print 3 \
            --output_dir results

        if [ $? -eq 0 ]; then
            echo "✓ $provider - $strategy done"
        else
            echo "✗ $provider - $strategy failed"
        fi

        # Avoid rate limits
        sleep 5
    done
done

echo ""
echo "=========================================="
echo "All evaluations complete. Results in results/"
echo "=========================================="
