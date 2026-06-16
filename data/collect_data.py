"""
Legal Compass - Phase 1: Data Collection
Collects Indian Constitution, IPC, and legal Q&A data from public sources.
"""

import requests
import json
import time
import os
import re
from pathlib import Path

RAW_DIR = Path(__file__).parent / "raw"
RAW_DIR.mkdir(exist_ok=True)

HEADERS = {"User-Agent": "Mozilla/5.0 (LegalCompass Research Bot)"}


# ─────────────────────────────────────────────
# 1. IndianKanoon API  (free, no key needed)
# ─────────────────────────────────────────────
def fetch_indiankanoon(query: str, doc_type: str = "constitution", max_docs: int = 20):
    """
    Fetches documents from IndianKanoon public search.
    query     : search term e.g. "fundamental rights Article 19"
    doc_type  : label for saving (constitution / ipc / crpc)
    max_docs  : how many results to pull
    """
    print(f"\n[IndianKanoon] Fetching: '{query}'")
    base_url = "https://api.indiankanoon.org/search/"
    results = []

    try:
        params = {"formInput": query, "pagenum": 0}
        resp = requests.post(base_url, data=params, headers=HEADERS, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            docs = data.get("docs", [])[:max_docs]
            for doc in docs:
                results.append({
                    "title": doc.get("title", ""),
                    "text": doc.get("headline", "") + " " + doc.get("doc", ""),
                    "source": "indiankanoon",
                    "type": doc_type,
                    "tid": doc.get("tid", "")
                })
            print(f"  -> Got {len(results)} docs")
        else:
            print(f"  -> Failed: HTTP {resp.status_code}")
    except Exception as e:
        print(f"  -> Error: {e}")

    return results


# ─────────────────────────────────────────────
# 2. Constitution of India - Article Scraper
# ─────────────────────────────────────────────
CONSTITUTION_ARTICLES = {
    "Part I - The Union and its Territory": list(range(1, 5)),
    "Part II - Citizenship": list(range(5, 12)),
    "Part III - Fundamental Rights": list(range(12, 36)),
    "Part IV - Directive Principles": list(range(36, 52)),
    "Part IVA - Fundamental Duties": [51],
    "Part V - The Union": list(range(52, 152)),
    "Part VI - The States": list(range(152, 238)),
    "Part XVIII - Emergency Provisions": list(range(352, 361)),
}

CONSTITUTION_TEXT = {
    # Fundamental Rights - Most queried
    "Article 12": "Definition of State for Part III (Fundamental Rights). The State includes the Government and Parliament of India and the Government and the Legislature of each of the States.",
    "Article 13": "Laws inconsistent with or in derogation of the fundamental rights shall be void. The State shall not make any law which takes away or abridges the rights conferred by this Part.",
    "Article 14": "Equality before law - The State shall not deny to any person equality before the law or the equal protection of the laws within the territory of India.",
    "Article 15": "Prohibition of discrimination on grounds of religion, race, caste, sex or place of birth. The State shall not discriminate against any citizen on grounds only of religion, race, caste, sex, place of birth or any of them.",
    "Article 16": "Equality of opportunity in matters of public employment. There shall be equality of opportunity for all citizens in matters relating to employment or appointment to any office under the State.",
    "Article 17": "Abolition of Untouchability. Untouchability is abolished and its practice in any form is forbidden. The enforcement of any disability arising out of Untouchability shall be an offence punishable in accordance with law.",
    "Article 18": "Abolition of titles. No title, not being a military or academic distinction, shall be conferred by the State.",
    "Article 19": "Protection of certain rights regarding freedom of speech, etc. All citizens shall have the right to freedom of speech and expression, to assemble peaceably and without arms, to form associations or unions, to move freely throughout the territory of India, to reside and settle in any part of India, and to practise any profession.",
    "Article 20": "Protection in respect of conviction for offences. No person shall be convicted of any offence except for violation of a law in force at the time of commission of the act charged as an offence.",
    "Article 21": "Protection of life and personal liberty. No person shall be deprived of his life or personal liberty except according to procedure established by law.",
    "Article 21A": "Right to Education. The State shall provide free and compulsory education to all children of the age of six to fourteen years in such manner as the State may, by law, determine.",
    "Article 22": "Protection against arbitrary arrest and detention. No person who is arrested shall be detained in custody without being informed, as soon as may be, of the grounds for such arrest nor shall he be denied the right to consult, and to be defended by, a legal practitioner of his choice.",
    "Article 23": "Prohibition of traffic in human beings and forced labour.",
    "Article 24": "Prohibition of employment of children in factories, etc. No child below the age of fourteen years shall be employed to work in any factory or mine or engaged in any other hazardous employment.",
    "Article 25": "Freedom of conscience and free profession, practice and propagation of religion.",
    "Article 26": "Freedom to manage religious affairs.",
    "Article 29": "Protection of interests of minorities.",
    "Article 30": "Right of minorities to establish and administer educational institutions.",
    "Article 32": "Remedies for enforcement of rights conferred by this Part (Right to Constitutional Remedies). The right to move the Supreme Court by appropriate proceedings for the enforcement of the rights conferred by this Part is guaranteed.",
    # Directive Principles
    "Article 39A": "Equal justice and free legal aid. The State shall secure that the operation of the legal system promotes justice, on a basis of equal opportunity, and shall, in particular, provide free legal aid.",
    "Article 44": "Uniform civil code for the citizens. The State shall endeavour to secure for the citizens a uniform civil code throughout the territory of India.",
    # Emergency
    "Article 352": "Proclamation of Emergency. If the President is satisfied that a grave emergency exists whereby the security of India or of any part of the territory thereof is threatened.",
    "Article 356": "Provisions in case of failure of constitutional machinery in State (President's Rule).",
    "Article 360": "Provisions as to Financial Emergency.",
    # Amendment
    "Article 368": "Power of Parliament to amend the Constitution and procedure therefor.",
}

IPC_SECTIONS = {
    "Section 302": "Punishment for murder. Whoever commits murder shall be punished with death, or imprisonment for life, and shall also be liable to fine.",
    "Section 304": "Punishment for culpable homicide not amounting to murder.",
    "Section 307": "Attempt to murder. Whoever does any act with such intention or knowledge, and under such circumstances that, if he by that act caused death, he would be guilty of murder, shall be punished with imprisonment of either description for a term which may extend to ten years.",
    "Section 376": "Punishment for rape. Whoever commits rape shall be punished with rigorous imprisonment of either description for a term which shall not be less than seven years.",
    "Section 379": "Punishment for theft. Whoever commits theft shall be punished with imprisonment of either description for a term which may extend to three years, or with fine, or with both.",
    "Section 380": "Theft in dwelling house, etc. Whoever commits theft in any building, tent or vessel, which building, tent or vessel is used as a human dwelling, shall be punished with imprisonment of either description for a term which may extend to seven years.",
    "Section 392": "Punishment for robbery. Whoever commits robbery shall be punished with rigorous imprisonment for a term which may extend to ten years, and shall also be liable to fine.",
    "Section 395": "Punishment for dacoity. Whoever commits dacoity shall be punished with imprisonment for life, or with rigorous imprisonment for a term which may extend to ten years, and shall also be liable to fine.",
    "Section 406": "Punishment for criminal breach of trust. Whoever commits criminal breach of trust shall be punished with imprisonment of either description for a term which may extend to three years, or with fine, or with both.",
    "Section 420": "Cheating and dishonestly inducing delivery of property. Whoever cheats and thereby dishonestly induces the person deceived to deliver any property to any person, shall be punished with imprisonment of either description for a term which may extend to seven years.",
    "Section 498A": "Husband or relative of husband of a woman subjecting her to cruelty. Whoever, being the husband or the relative of the husband of a woman, subjects such woman to cruelty shall be punished with imprisonment for a term which may extend to three years and shall also be liable to fine.",
    "Section 503": "Criminal intimidation. Whoever threatens another with any injury to his person, reputation or property, with intent to cause alarm to that person.",
    "Section 506": "Punishment for criminal intimidation. If threat be to cause death or grievous hurt, etc., shall be punished with imprisonment of either description for a term which may extend to seven years.",
}

CRPC_SECTIONS = {
    "Section 41": "When police may arrest without warrant. A police officer may without an order from a Magistrate and without a warrant, arrest any person who has been concerned in any cognizable offence.",
    "Section 154": "Information in cognizable cases (FIR). Every information relating to the commission of a cognizable offence, if given orally to an officer in charge of a police station, shall be reduced to writing by him or under his direction.",
    "Section 161": "Examination of witnesses by police.",
    "Section 167": "Procedure when investigation cannot be completed in twenty-four hours. Bail provisions when police cannot complete investigation within 24 hours.",
    "Section 173": "Report of police officer on completion of investigation (Charge Sheet / Final Report).",
    "Section 197": "Prosecution of Judges and public servants.",
    "Section 313": "Power to examine the accused.",
    "Section 374": "Appeals from convictions.",
    "Section 438": "Direction for grant of bail to person apprehending arrest (Anticipatory Bail).",
    "Section 439": "Special powers of High Court or Court of Session regarding bail.",
}


def build_legal_corpus() -> list:
    """Combine all hardcoded legal knowledge into a structured corpus."""
    corpus = []

    for article, text in CONSTITUTION_TEXT.items():
        corpus.append({
            "id": article.replace(" ", "_"),
            "source": "Constitution of India",
            "type": "constitution",
            "title": article,
            "text": text
        })

    for section, text in IPC_SECTIONS.items():
        corpus.append({
            "id": section.replace(" ", "_"),
            "source": "Indian Penal Code (IPC)",
            "type": "ipc",
            "title": section,
            "text": text
        })

    for section, text in CRPC_SECTIONS.items():
        corpus.append({
            "id": section.replace(" ", "_"),
            "source": "Code of Criminal Procedure (CrPC)",
            "type": "crpc",
            "title": section,
            "text": text
        })

    return corpus


# ─────────────────────────────────────────────
# 3. Save to disk
# ─────────────────────────────────────────────
def save_corpus(corpus: list, filename: str = "legal_corpus.json"):
    out_path = RAW_DIR / filename
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(corpus, f, ensure_ascii=False, indent=2)
    print(f"\n[OK] Saved {len(corpus)} entries -> {out_path}")


if __name__ == "__main__":
    print("=" * 55)
    print("  Legal Compass - Phase 1: Data Collection")
    print("=" * 55)

    corpus = build_legal_corpus()
    print(f"\n[*] Built local corpus: {len(corpus)} entries")

    # Optionally try IndianKanoon (network dependent)
    try:
        ik_docs = fetch_indiankanoon("fundamental rights Article 21", "constitution", max_docs=10)
        corpus.extend(ik_docs)
    except Exception as e:
        print(f"  [Skipping IndianKanoon - offline or blocked]: {e}")

    save_corpus(corpus)
    print("\nBreakdown:")
    from collections import Counter
    counts = Counter(d["type"] for d in corpus)
    for t, c in counts.items():
        print(f"  {t:15s} -> {c} entries")