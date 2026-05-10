"""
Google Gemma 2 2B/9B Fine-tuning Template for Colab (using Unsloth)
Target: Export GGUF for Ollama
"""

# !pip install unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git
# !pip install --no-deps xformers trl peft accelerate bitsandbytes

from unsloth import FastLanguageModel
import torch
from trl import SFTTrainer
from transformers import TrainingArguments
from datasets import load_dataset
import os

# 1. Configuration
model_name = "unsloth/gemma-2-2b-it-bnb-4bit" # or "unsloth/gemma-2-9b-it-bnb-4bit"
max_seq_length = 2048
dtype = None # Auto detection
load_in_4bit = True

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = model_name,
    max_seq_length = max_seq_length,
    dtype = dtype,
    load_in_4bit = load_in_4bit,
)

# 2. Add LoRA adapters
model = FastLanguageModel.get_peft_model(
    model,
    r = 16,
    target_modules = ["q_proj", "k_proj", "v_proj", "o_proj",
                      "gate_proj", "up_proj", "down_proj",],
    lora_alpha = 16,
    lora_dropout = 0,
    bias = "none",
    use_gradient_checkpointing = "unsloth",
    random_state = 3407,
)

# 3. Data Formatting
# Assume alpaca format for simplicity
alpaca_prompt = """Below is an instruction that describes a task. Write a response that appropriately completes the request.

### Instruction:
{}

### Response:
{}"""

def formatting_prompts_func(examples):
    instructions = examples["instruction"]
    outputs      = examples["output"]
    texts = []
    for instruction, output in zip(instructions, outputs):
        text = alpaca_prompt.format(instruction, output)
        texts.append(text)
    return { "text" : texts, }

# Load your uploaded data (e.g., from Step 1 Export in app)
# dataset = load_dataset("json", data_files="exported_data.jsonl", split="train")
# dataset = dataset.map(formatting_prompts_func, batched = True,)

# 4. Training
# trainer = SFTTrainer(...)
# trainer.train()

# 5. Export to GGUF for Ollama
# This will create 'model-q4_k_m.gguf' which you can download and upload to MedAutoRAG UI
model.save_pretrained_gguf("model", tokenizer, quantization_method = "q4_k_m")
