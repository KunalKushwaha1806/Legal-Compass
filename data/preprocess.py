"""
Legal Compass - Phase 1: Data Cleaning & Preprocessing
Cleans raw corpus and converts it into training-ready Q&A pairs.
"""

import json
import re
import pandas as pd
from pathlib import Path
from tqdm import tqdm

RAW_DIR = Path(__file__).parent / "raw"
PROCESSED_DIR = Path(__file__).parent / "processed"
PROCESSED_DIR.mkdir(exist_ok=True)


# ─────────────────────────────────────────────
# 1. Text Cleaning
# ─────────────────────────────────────────────
def clean_text(text: str) -> str:
    text = re.sub(r'\s+', ' ', text)                   # collapse whitespace
    text = re.sub(r'[^\x00-\x7F\u0900-\u097F]+', ' ', text)  # keep ASCII + Devanagari
    text = re.sub(r'\b(ibid|supra|infra)\b', '', text, flags=re.I)  # remove legal latin
    text = text.strip()
    return text


def clean_corpus(corpus: list) -> list:
    cleaned = []
    for entry in corpus:
        text = clean_text(entry.get("text", ""))
        if len(text) < 20:          # skip too-short entries
            continue
        entry["text"] = text
        entry["char_count"] = len(text)
        cleaned.append(entry)
    return cleaned


# ─────────────────────────────────────────────
# 2. Q&A Pair Generation
#    Each legal passage -> multiple Q&A pairs
#    This becomes your fine-tuning dataset
# ─────────────────────────────────────────────

QA_TEMPLATES = {
    "constitution": [
        ("What does {title} of the Indian Constitution state?", "{text}"),
        ("Explain {title} in simple terms.", "{text}"),
        ("What are the provisions under {title}?", "{text}"),
        ("Is {title} a Fundamental Right?", "{text}"),
    ],
    "ipc": [
        ("What is the punishment under {title} of IPC?", "{text}"),
        ("What does {title} of the Indian Penal Code say?", "{text}"),
        ("Under which IPC section is {title} covered?", "{text}"),
        ("Explain the offence described in {title} of IPC.", "{text}"),
    ],
    "crpc": [
        ("What does {title} of CrPC deal with?", "{text}"),
        ("Explain {title} of the Code of Criminal Procedure.", "{text}"),
        ("What are the police powers under {title}?", "{text}"),
    ],
    "default": [
        ("What is {title}?", "{text}"),
        ("Explain {title} in the context of Indian law.", "{text}"),
    ]
}

EXTRA_QA_PAIRS = [
    # Fundamental Rights
    {
        "question": "What are the Fundamental Rights guaranteed by the Indian Constitution?",
        "answer": "The Fundamental Rights are guaranteed under Part III (Articles 12-35) of the Indian Constitution. They include: Right to Equality (Articles 14-18), Right to Freedom (Article 19-22), Right against Exploitation (Articles 23-24), Right to Freedom of Religion (Articles 25-28), Cultural and Educational Rights (Articles 29-30), and Right to Constitutional Remedies (Article 32).",
        "type": "constitution", "source": "Constitution of India"
    },
    {
        "question": "What is the Right to Life under Article 21?",
        "answer": "Article 21 states that no person shall be deprived of his life or personal liberty except according to procedure established by law. The Supreme Court has expanded this to include right to livelihood, right to privacy, right to health, right to education, right to a clean environment, and right to speedy trial.",
        "type": "constitution", "source": "Constitution of India"
    },
    {
        "question": "Can Fundamental Rights be suspended?",
        "answer": "Yes, Fundamental Rights can be suspended during a National Emergency (Article 352) except Articles 20 and 21 which can NEVER be suspended. The President can suspend the right to move courts for enforcement of Fundamental Rights during an emergency.",
        "type": "constitution", "source": "Constitution of India"
    },
    {
        "question": "What is anticipatory bail?",
        "answer": "Anticipatory bail is a provision under Section 438 of CrPC that allows a person to seek bail in anticipation of an arrest. If granted by the Sessions Court or High Court, the person can be released on bail immediately upon arrest. It is granted when there is apprehension of arrest for a non-bailable offence.",
        "type": "crpc", "source": "CrPC"
    },
    {
        "question": "What is an FIR and how is it filed?",
        "answer": "FIR (First Information Report) is registered under Section 154 of CrPC. It is the first document prepared by police when a cognizable offence is reported. To file an FIR: visit the police station of the area where the offence occurred, give information orally or in writing, the officer must record it, read it to you, and you sign it. A free copy must be given to you. If police refuse, you can approach the Superintendent of Police or file a complaint in court under Section 156(3) CrPC.",
        "type": "crpc", "source": "CrPC"
    },
    {
        "question": "What is the difference between bailable and non-bailable offences?",
        "answer": "In a bailable offence, bail is a right and police must grant it. Examples: theft under Rs 50, assault without grievous hurt. In a non-bailable offence, bail is not a right - it is at the discretion of the court. Examples: murder (Section 302 IPC), rape (Section 376 IPC), dacoity (Section 395 IPC). Non-bailable offences are generally more serious crimes with higher punishments.",
        "type": "ipc", "source": "IPC/CrPC"
    },
    {
        "question": "What is Section 498A of IPC?",
        "answer": "Section 498A of IPC deals with cruelty by husband or relatives of husband towards a married woman. It includes physical and mental cruelty and harassment for dowry demands. It is a cognizable, non-bailable, and non-compoundable offence. Punishment is up to 3 years imprisonment and fine. The Supreme Court in Arnesh Kumar vs State of Bihar (2014) gave guidelines to prevent misuse and said arrest should not be made automatically.",
        "type": "ipc", "source": "IPC"
    },
    {
        "question": "What is Article 32 of the Indian Constitution?",
        "answer": "Article 32 is the Right to Constitutional Remedies - Dr. B.R. Ambedkar called it the 'heart and soul of the Constitution'. It gives every citizen the right to directly approach the Supreme Court if their Fundamental Rights are violated. The Supreme Court can issue writs: Habeas Corpus (produce the body), Mandamus (command to do duty), Prohibition, Certiorari, and Quo Warranto. This right itself is a Fundamental Right and cannot be suspended except during Emergency.",
        "type": "constitution", "source": "Constitution of India"
    },
    {
        "question": "What is the punishment for murder in India?",
        "answer": "Murder is defined under Section 300 of IPC and punished under Section 302 IPC. The punishment is death penalty OR imprisonment for life, along with a fine. The death penalty is awarded only in the 'rarest of rare' cases as established by the Supreme Court in Bachan Singh vs State of Punjab (1980). Culpable homicide not amounting to murder (Section 304) carries lesser punishment.",
        "type": "ipc", "source": "IPC"
    },
    {
        "question": "What are Directive Principles of State Policy?",
        "answer": "Directive Principles of State Policy (DPSP) are contained in Part IV (Articles 36-51) of the Constitution. They are guidelines for the government to establish a just society. Unlike Fundamental Rights, they are non-justiciable (cannot be enforced in court). Key DPSPs include: equal pay for equal work (Article 39d), free legal aid (Article 39A), uniform civil code (Article 44), and living wage for workers (Article 43). Though not enforceable, they are fundamental in governance.",
        "type": "constitution", "source": "Constitution of India"
    },
    {
        "question": "What is the right to free legal aid in India?",
        "answer": "Article 39A of the Constitution mandates free legal aid. The Legal Services Authorities Act 1987 operationalizes this. Any person who cannot afford a lawyer can approach NALSA (National Legal Services Authority) or State/District Legal Services Authority for free legal representation. This right applies to: persons with annual income below the prescribed limit, women and children, SC/ST members, victims of disaster, disabled persons, and industrial workmen.",
        "type": "constitution", "source": "Constitution of India"
    },
    {
        "question": "How many times has the Indian Constitution been amended?",
        "answer": "The Indian Constitution has been amended 106 times as of 2024. The procedure for amendment is in Article 368. Some amendments require simple majority, some require special majority (2/3rd of members present and voting + majority of total membership of each House), and some also require ratification by at least half of State legislatures. The 42nd Amendment (1976) is called the 'Mini Constitution' as it made sweeping changes.",
        "type": "constitution", "source": "Constitution of India"
    },
]


def generate_qa_pairs(corpus: list) -> list:
    qa_pairs = []

    for entry in tqdm(corpus, desc="Generating Q&A pairs"):
        doc_type = entry.get("type", "default")
        title = entry.get("title", "this provision")
        text = entry.get("text", "")
        source = entry.get("source", "Indian Law")

        templates = QA_TEMPLATES.get(doc_type, QA_TEMPLATES["default"])

        for q_template, a_template in templates:
            question = q_template.format(title=title, text=text)
            answer = a_template.format(title=title, text=text)

            qa_pairs.append({
                "question": question,
                "answer": answer,
                "context": text,
                "source": source,
                "type": doc_type,
                "origin": entry.get("id", "")
            })

    # Add handcrafted expert Q&A pairs
    for pair in EXTRA_QA_PAIRS:
        qa_pairs.append({
            "question": pair["question"],
            "answer": pair["answer"],
            "context": pair["answer"],
            "source": pair["source"],
            "type": pair["type"],
            "origin": "handcrafted"
        })

    return qa_pairs


# ─────────────────────────────────────────────
# 3. Train/Val/Test Split
# ─────────────────────────────────────────────
def split_dataset(qa_pairs: list, train=0.8, val=0.1):
    import random
    random.seed(42)
    random.shuffle(qa_pairs)

    n = len(qa_pairs)
    train_end = int(n * train)
    val_end = int(n * (train + val))

    return {
        "train": qa_pairs[:train_end],
        "val": qa_pairs[train_end:val_end],
        "test": qa_pairs[val_end:]
    }


def save_splits(splits: dict):
    for split_name, data in splits.items():
        out_path = PROCESSED_DIR / f"{split_name}.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"  [OK] {split_name:6s} -> {len(data):4d} pairs -> {out_path}")

    # Also save as CSV for easy inspection
    all_df = pd.DataFrame(splits["train"] + splits["val"] + splits["test"])
    all_df.to_csv(PROCESSED_DIR / "all_qa_pairs.csv", index=False)
    print(f"\n  [=] CSV saved -> {PROCESSED_DIR / 'all_qa_pairs.csv'}")


if __name__ == "__main__":
    print("=" * 55)
    print("  Legal Compass - Phase 1: Data Preprocessing")
    print("=" * 55)

    # Load raw corpus
    corpus_path = RAW_DIR / "legal_corpus.json"
    if not corpus_path.exists():
        print("❌ Run collect_data.py first!")
        exit(1)

    with open(corpus_path, encoding="utf-8") as f:
        corpus = json.load(f)

    print(f"\n[D] Loaded {len(corpus)} raw entries")

    # Clean
    corpus = clean_corpus(corpus)
    print(f"[~] After cleaning: {len(corpus)} entries")

    # Generate Q&A pairs
    qa_pairs = generate_qa_pairs(corpus)
    print(f"\n[?] Generated {len(qa_pairs)} Q&A pairs total")

    # Split & save
    print("\nSplitting dataset (80/10/10):")
    splits = split_dataset(qa_pairs)
    save_splits(splits)

    # Preview
    print("\n[>] Sample Q&A pair:")
    sample = splits["train"][0]
    print(f"  Q: {sample['question']}")
    print(f"  A: {sample['answer'][:120]}...")