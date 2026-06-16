"""
Legal Compass - Phase 2: Model Fine-Tuning
Fine-tunes a pretrained BERT/DistilBERT model on our legal Q&A dataset.
Model: google/muril-base-cased (Multilingual for Indian languages)
  OR   bert-base-uncased (English only, lighter)

Run this on your local machine or Google Colab (free GPU).
"""

import json
import torch
import numpy as np
from pathlib import Path
from torch.utils.data import Dataset, DataLoader
from transformers import (
    AutoTokenizer,
    AutoModelForQuestionAnswering,
    AutoModelForSeq2SeqLM,
    T5ForConditionalGeneration,
    T5Tokenizer,
    TrainingArguments,
    Trainer,
    default_data_collator,
)

PROCESSED_DIR = Path(__file__).parent.parent / "data" / "processed"
MODEL_DIR = Path(__file__).parent / "saved_model"
MODEL_DIR.mkdir(exist_ok=True)

# ─── Choose your model ───────────────────────────────────
# Option A: Lighter, English only (good start)
MODEL_NAME = "google/flan-t5-base"

# Option B: Multilingual for Hindi + English (better for India)
# MODEL_NAME = "google/muril-base-cased"

# Option C: If you have GPU and want best results
# MODEL_NAME = "google/flan-t5-large"
# ─────────────────────────────────────────────────────────

MAX_INPUT_LENGTH = 512
MAX_TARGET_LENGTH = 256
BATCH_SIZE = 8          # Reduce to 4 if you get OOM errors
EPOCHS = 3
LEARNING_RATE = 3e-4


# ─────────────────────────────────────────────
# Dataset Class
# ─────────────────────────────────────────────
class LegalQADataset(Dataset):
    def __init__(self, data: list, tokenizer, max_input_len: int, max_target_len: int):
        self.data = data
        self.tokenizer = tokenizer
        self.max_input_len = max_input_len
        self.max_target_len = max_target_len

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        item = self.data[idx]
        # Format: "question: <Q> context: <context>"
        input_text = f"question: {item['question']} context: {item.get('context', item['question'])}"
        target_text = item['answer']

        input_enc = self.tokenizer(
            input_text,
            max_length=self.max_input_len,
            padding="max_length",
            truncation=True,
            return_tensors="pt"
        )
        target_enc = self.tokenizer(
            target_text,
            max_length=self.max_target_len,
            padding="max_length",
            truncation=True,
            return_tensors="pt"
        )

        labels = target_enc["input_ids"].squeeze()
        # Replace padding token id with -100 so loss ignores padding
        labels[labels == self.tokenizer.pad_token_id] = -100

        return {
            "input_ids": input_enc["input_ids"].squeeze(),
            "attention_mask": input_enc["attention_mask"].squeeze(),
            "labels": labels,
        }


# ─────────────────────────────────────────────
# Training
# ─────────────────────────────────────────────
def load_data():
    with open(PROCESSED_DIR / "train.json", encoding="utf-8") as f:
        train = json.load(f)
    with open(PROCESSED_DIR / "val.json", encoding="utf-8") as f:
        val = json.load(f)
    return train, val


def train_model():
    print(f"\n{'='*55}")
    print(f"  Legal Compass - Phase 2: Fine-Tuning")
    print(f"  Model: {MODEL_NAME}")
    print(f"{'='*55}\n")

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"  Device: {device.upper()}")
    if device == "cpu":
        print("  [!]  No GPU detected. Training will be slow.")
        print("     Tip: Use Google Colab (free T4 GPU) for faster training.\n")

    # Load tokenizer and model
    print("  Loading tokenizer and model...")
    tokenizer = T5Tokenizer.from_pretrained(MODEL_NAME)
    model = T5ForConditionalGeneration.from_pretrained(MODEL_NAME)
    model.to(device)

    # Load and prepare datasets
    train_data, val_data = load_data()
    print(f"  Train size: {len(train_data)} | Val size: {len(val_data)}")

    train_dataset = LegalQADataset(train_data, tokenizer, MAX_INPUT_LENGTH, MAX_TARGET_LENGTH)
    val_dataset = LegalQADataset(val_data, tokenizer, MAX_INPUT_LENGTH, MAX_TARGET_LENGTH)

    # Training arguments
    training_args = TrainingArguments(
        output_dir=str(MODEL_DIR / "checkpoints"),
        num_train_epochs=EPOCHS,
        per_device_train_batch_size=BATCH_SIZE,
        per_device_eval_batch_size=BATCH_SIZE,
        warmup_steps=100,
        weight_decay=0.01,
        learning_rate=LEARNING_RATE,
        logging_dir=str(MODEL_DIR / "logs"),
        logging_steps=50,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        predict_with_generate=True,
        fp16=torch.cuda.is_available(),  # Use half precision on GPU
        report_to="none",
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        tokenizer=tokenizer,
        data_collator=default_data_collator,
    )

    # Train!
    print("\n  [>>] Starting training...\n")
    trainer.train()

    # Save final model
    model.save_pretrained(MODEL_DIR / "final")
    tokenizer.save_pretrained(MODEL_DIR / "final")
    print(f"\n  [OK] Model saved -> {MODEL_DIR / 'final'}")


# ─────────────────────────────────────────────
# Inference (test your trained model)
# ─────────────────────────────────────────────
def answer_question(question: str, context: str = "", model_path: str = None):
    """Run inference with your trained model."""
    path = model_path or str(MODEL_DIR / "final")
    tokenizer = T5Tokenizer.from_pretrained(path)
    model = T5ForConditionalGeneration.from_pretrained(path)
    model.eval()

    input_text = f"question: {question} context: {context}" if context else f"question: {question}"
    inputs = tokenizer(input_text, return_tensors="pt", max_length=512, truncation=True)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=256,
            num_beams=4,
            early_stopping=True
        )

    answer = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return answer


if __name__ == "__main__":
    import sys

    if "--infer" in sys.argv:
        # Test inference mode
        q = "What is Article 21 of the Indian Constitution?"
        print(f"Q: {q}")
        print(f"A: {answer_question(q)}")
    else:
        # Train mode
        train_model()

        # Quick test after training
        print("\n[>] Quick inference test:")
        q = "What is Article 21 of the Indian Constitution?"
        a = answer_question(q)
        print(f"  Q: {q}")
        print(f"  A: {a}")