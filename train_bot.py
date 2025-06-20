from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer, DataCollatorForLanguageModeling
from datasets import load_dataset
from peft import get_peft_model, LoraConfig, TaskType

# Load base model and tokenizer
model_id = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
model = AutoModelForCausalLM.from_pretrained(model_id)
tokenizer = AutoTokenizer.from_pretrained(model_id)
tokenizer.pad_token = tokenizer.eos_token

# Load dataset from JSONL file (must contain 'scenario' and 'evaluation' keys)
dataset = load_dataset("json", data_files="qa_data.jsonl", split="train")

# Tokenization function
def tokenize(example):
    prompt = f"Scenario: {example['scenario']}\nUser Response: <user_input>"
    label = f"Score and Feedback: {example['evaluation']}"
    full_input = prompt + "\n" + label
    return tokenizer(full_input, truncation=True, padding="max_length", max_length=512)

# Apply tokenizer
dataset = dataset.map(tokenize)

# Configure LoRA adapter
peft_config = LoraConfig(
    task_type=TaskType.CAUSAL_LM,
    inference_mode=False,
    r=8,
    lora_alpha=16,
    lora_dropout=0.1
)
model = get_peft_model(model, peft_config)

# Training arguments
training_args = TrainingArguments(
    output_dir="trained_bot",
    per_device_train_batch_size=4,
    num_train_epochs=3,
    logging_dir="./logs",
    logging_steps=10,
    save_strategy="epoch",
    save_total_limit=2,
    report_to="none"
)

# Trainer setup
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset,
    tokenizer=tokenizer,
    data_collator=DataCollatorForLanguageModeling(tokenizer, mlm=False),
)

# Train the model
trainer.train()

# Save adapter after training
model.save_pretrained("trained_bot/checkpoint-9")
