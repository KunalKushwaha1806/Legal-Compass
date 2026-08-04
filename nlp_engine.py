"""
Legal Compass — NLP Query-Response Pipeline
Provides context-aware answers to Indian legal queries using:
  1. Full Indian Legal Corpus Map (395 Articles, 511 IPC, 484 CrPC, BNS/BNSS 2023).
  2. Strict regex word-boundary number matching for Articles & IPC/CrPC Sections.
  3. Knowledge Base retrieval (TF-IDF + exact keyword).
  4. Optional: fine-tuned Flan-T5 model (loaded automatically if present).

No network calls — fully offline-capable.
"""
from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path
from legal_full_corpus import lookup_specific_provision

# ── Optional: scikit-learn for TF-IDF ─────────────────────────
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np

    _SKLEARN = True
except ImportError:
    _SKLEARN = False

# ── Optional: Transformers for fine-tuned model ────────────────
_MODEL_LOADED = False
_t5_model = None
_t5_tokenizer = None

# ══════════════════════════════════════════════════════════════
# Legal Knowledge Base (Core Corpus)
# ══════════════════════════════════════════════════════════════
LEGAL_KB = [
    # ── Indian Constitution ───────────────────────────────────
    {
        "id": "Article_1", "title": "Article 1", "type": "constitution",
        "text": "Name and territory of the Union. India, that is Bharat, shall be a Union of States. The territory of India comprises the territories of the States, the Union territories, and such other territories as may be acquired.",
    },
    {
        "id": "Article_5", "title": "Article 5", "type": "constitution",
        "text": "Citizenship at the commencement of the Constitution. At the commencement of this Constitution, every person who has his domicile in the territory of India and: (a) who was born in India, or (b) either of whose parents was born in India, or (c) who has been ordinarily resident in India for not less than 5 years — shall be a citizen of India.",
    },
    {
        "id": "Article_12", "title": "Article 12", "type": "constitution",
        "text": "Definition of State for Part III. The State includes the Government and Parliament of India and the Government and Legislature of each State and all local or other authorities within the territory of India or under the control of the Government of India.",
    },
    {
        "id": "Article_13", "title": "Article 13", "type": "constitution",
        "text": "Laws inconsistent with or in derogation of Fundamental Rights. All laws in force in India before the commencement of the Constitution, in so far as they are inconsistent with Part III, shall be void to the extent of such inconsistency.",
    },
    {
        "id": "Article_14", "title": "Article 14", "type": "constitution",
        "text": "Equality before law. The State shall not deny to any person equality before the law or the equal protection of the laws within the territory of India. It guarantees two rights: equality before law (British concept) and equal protection of laws (American concept).",
    },
    {
        "id": "Article_15", "title": "Article 15", "type": "constitution",
        "text": "Prohibition of discrimination on grounds of religion, race, caste, sex or place of birth. The State shall not discriminate against any citizen on grounds only of religion, race, caste, sex, place of birth or any of them. Special provisions for women, children, and socially/educationally backward classes are permitted.",
    },
    {
        "id": "Article_16", "title": "Article 16", "type": "constitution",
        "text": "Equality of opportunity in matters of public employment. There shall be equality of opportunity for all citizens in matters relating to employment or appointment to any office under the State. Reservation for backward classes and SCs/STs is permitted.",
    },
    {
        "id": "Article_17", "title": "Article 17", "type": "constitution",
        "text": "Abolition of Untouchability. Untouchability is abolished and its practice in any form is forbidden. The enforcement of any disability arising out of Untouchability shall be an offence punishable by law under the Protection of Civil Rights Act 1955.",
    },
    {
        "id": "Article_18", "title": "Article 18", "type": "constitution",
        "text": "Abolition of titles. No title, not being a military or academic distinction, shall be conferred by the State. No citizen of India shall accept any title from any foreign State.",
    },
    {
        "id": "Article_19", "title": "Article 19", "type": "constitution",
        "text": "Protection of six fundamental freedoms: (a) Freedom of speech and expression, (b) Right to assemble peaceably without arms, (c) Right to form associations or unions, (d) Right to move freely throughout India, (e) Right to reside and settle in any part of India, (f) Right to practise any profession. These rights are subject to reasonable restrictions under Articles 19(2)-(6).",
    },
    {
        "id": "Article_20", "title": "Article 20", "type": "constitution",
        "text": "Protection in respect of conviction for offences: (1) Protection against ex-post facto laws, (2) Protection against double jeopardy (cannot be prosecuted twice for same offence), (3) Protection against self-incrimination (cannot be compelled to be a witness against oneself). Cannot be suspended during Emergency.",
    },
    {
        "id": "Article_21", "title": "Article 21", "type": "constitution",
        "text": "Protection of life and personal liberty. No person shall be deprived of his life or personal liberty except according to procedure established by law. The Supreme Court has broadly interpreted this to include: right to livelihood, right to privacy (KS Puttaswamy 2017), right to health, right to education, right to clean environment, and right to dignity.",
    },
    {
        "id": "Article_21A", "title": "Article 21A", "type": "constitution",
        "text": "Right to Education. The State shall provide free and compulsory education to all children of the age of six to fourteen years. Inserted by 86th Amendment Act 2002. Operationalised by the Right to Education (RTE) Act 2009.",
    },
    {
        "id": "Article_22", "title": "Article 22", "type": "constitution",
        "text": "Protection against arbitrary arrest and detention. Every arrested person has the right: (1) to be informed of grounds of arrest, (2) to consult and be defended by a lawyer of choice, (3) to be produced before a magistrate within 24 hours.",
    },
    {
        "id": "Article_23", "title": "Article 23", "type": "constitution",
        "text": "Prohibition of traffic in human beings and forced labour (begar). Any contravention of this provision shall be an offence punishable in accordance with law.",
    },
    {
        "id": "Article_24", "title": "Article 24", "type": "constitution",
        "text": "Prohibition of employment of children in factories, mines, or hazardous employment. No child below the age of fourteen years shall be employed to work in any factory or mine or engaged in any other hazardous employment.",
    },
    {
        "id": "Article_25", "title": "Article 25", "type": "constitution",
        "text": "Freedom of conscience and free profession, practice and propagation of religion, subject to public order, morality, and health.",
    },
    {
        "id": "Article_26", "title": "Article 26", "type": "constitution",
        "text": "Freedom to manage religious affairs. Every religious denomination or section thereof has the right to establish and maintain institutions for religious and charitable purposes and manage its own affairs in matters of religion.",
    },
    {
        "id": "Article_29", "title": "Article 29", "type": "constitution",
        "text": "Protection of interests of minorities. Any section of citizens having a distinct language, script, or culture of its own shall have the right to conserve the same.",
    },
    {
        "id": "Article_30", "title": "Article 30", "type": "constitution",
        "text": "Right of minorities (religious or linguistic) to establish and administer educational institutions of their choice.",
    },
    {
        "id": "Article_32", "title": "Article 32", "type": "constitution",
        "text": "Right to Constitutional Remedies — Dr. Ambedkar called it the 'heart and soul of the Constitution'. Guarantees the right to move the Supreme Court for enforcement of Fundamental Rights by issuing writs: Habeas Corpus, Mandamus, Prohibition, Certiorari, and Quo Warranto.",
    },
    {
        "id": "Article_39A", "title": "Article 39A", "type": "constitution",
        "text": "Equal justice and free legal aid. The State shall secure that the legal system promotes justice on a basis of equal opportunity, and shall provide free legal aid to ensure opportunities for justice are not denied to any citizen due to economic or other disabilities.",
    },
    {
        "id": "Article_44", "title": "Article 44", "type": "constitution",
        "text": "Uniform Civil Code for citizens. The State shall endeavour to secure for the citizens a uniform civil code throughout the territory of India.",
    },
    {
        "id": "Article_51A", "title": "Article 51A", "type": "constitution",
        "text": "Fundamental Duties of every citizen of India, including to abide by the Constitution, respect national symbols, defend the country, promote harmony, and protect the environment. Inserted by 42nd Amendment Act 1976.",
    },
    {
        "id": "Article_56", "title": "Article 56", "type": "constitution",
        "text": "Term of office of President. The President shall hold office for a term of five years from the date on which he enters upon his office. The President may resign by writing under his hand addressed to the Vice-President or be removed by impeachment under Article 61.",
    },
    {
        "id": "Article_350", "title": "Article 350", "type": "constitution",
        "text": "Language to be used in representations for redress of grievances. Every person shall be entitled to submit a representation for the redress of any grievance to any officer or authority of the Union or a State in any of the languages used in the Union or State. Article 350A mandates facilities for instruction in mother-tongue at primary stage; Article 350B creates a Special Officer for linguistic minorities.",
    },
    {
        "id": "Article_352", "title": "Article 352", "type": "constitution",
        "text": "Proclamation of National Emergency. If the President is satisfied that a grave emergency exists whereby the security of India is threatened by war, external aggression, or armed rebellion.",
    },
    {
        "id": "Article_356", "title": "Article 356", "type": "constitution",
        "text": "President's Rule — Provisions in case of failure of constitutional machinery in a State. If the Governor reports or President is satisfied that the State government cannot be carried on in accordance with the Constitution.",
    },
    {
        "id": "Article_360", "title": "Article 360", "type": "constitution",
        "text": "Provisions as to Financial Emergency. If the President is satisfied that a situation has arisen whereby the financial stability or credit of India or of any part of the territory thereof is threatened.",
    },
    {
        "id": "Article_368", "title": "Article 368", "type": "constitution",
        "text": "Power of Parliament to amend the Constitution and procedure therefor. Subject to the Basic Structure Doctrine established in Kesavananda Bharati (1973).",
    },
    {
        "id": "Article_370", "title": "Article 370", "type": "constitution",
        "text": "Temporary provisions with respect to the State of Jammu and Kashmir. Operative status modified by the Constitution (Application to Jammu and Kashmir) Order, 2019, abrogating special status.",
    },
    # ── IPC Sections ──────────────────────────────────────────
    {
        "id": "Section_300", "title": "IPC Section 300", "type": "ipc",
        "text": "Definition of Murder. Except in specified exceptions (such as grave and sudden provocation, self-defense, public servant acting for justice, sudden fight, or consent), culpable homicide is murder if done with the intention or knowledge of causing death.",
    },
    {
        "id": "Section_302", "title": "IPC Section 302", "type": "ipc",
        "text": "Punishment for murder. Whoever commits murder shall be punished with death, or imprisonment for life, and shall also be liable to fine. Murder is defined under Section 300.",
    },
    {
        "id": "Section_304", "title": "IPC Section 304", "type": "ipc",
        "text": "Punishment for culpable homicide not amounting to murder. Imprisonment for life or up to 10 years + fine.",
    },
    {
        "id": "Section_307", "title": "IPC Section 307", "type": "ipc",
        "text": "Attempt to murder. Imprisonment up to 10 years and fine; if hurt is caused, punishment may extend to imprisonment for life.",
    },
    {
        "id": "Section_376", "title": "IPC Section 376", "type": "ipc",
        "text": "Punishment for rape. Rigorous imprisonment for not less than 10 years, extendable to life + fine. Enhanced penalties apply for aggravated forms.",
    },
    {
        "id": "Section_379", "title": "IPC Section 379", "type": "ipc",
        "text": "Punishment for theft. Dishonest taking of movable property out of another's possession without consent. Imprisonment up to 3 years, or fine, or both.",
    },
    {
        "id": "Section_380", "title": "IPC Section 380", "type": "ipc",
        "text": "Theft in dwelling house, tent, or vessel. Imprisonment up to 7 years and fine.",
    },
    {
        "id": "Section_392", "title": "IPC Section 392", "type": "ipc",
        "text": "Punishment for robbery. Rigorous imprisonment up to 10 years and fine; up to 14 years if committed on a highway between sunset and sunrise.",
    },
    {
        "id": "Section_395", "title": "IPC Section 395", "type": "ipc",
        "text": "Punishment for dacoity. Robbery committed by five or more persons conjointly. Imprisonment for life, or rigorous imprisonment up to 10 years, and fine.",
    },
    {
        "id": "Section_406", "title": "IPC Section 406", "type": "ipc",
        "text": "Punishment for criminal breach of trust. Dishonest misappropriation of property entrusted. Imprisonment up to 3 years, or fine, or both.",
    },
    {
        "id": "Section_420", "title": "IPC Section 420", "type": "ipc",
        "text": "Cheating and dishonestly inducing delivery of property. Imprisonment up to 7 years and fine.",
    },
    {
        "id": "Section_498A", "title": "IPC Section 498A", "type": "ipc",
        "text": "Cruelty by husband or relatives of husband for dowry or harassment. Imprisonment up to 3 years and fine. Cognizable and non-bailable.",
    },
    {
        "id": "Section_503", "title": "IPC Section 503", "type": "ipc",
        "text": "Criminal intimidation. Threatening another with injury to person, reputation, or property with intent to cause alarm.",
    },
    {
        "id": "Section_506", "title": "IPC Section 506", "type": "ipc",
        "text": "Punishment for criminal intimidation. Imprisonment up to 2 years or fine; up to 7 years if threat is to cause death or grievous hurt.",
    },
    # ── CrPC Sections ─────────────────────────────────────────
    {
        "id": "Section_41", "title": "CrPC Section 41", "type": "crpc",
        "text": "When police may arrest without warrant. A police officer may arrest any person concerned in any cognizable offence without a warrant, subject to guidelines in Arnesh Kumar (2014).",
    },
    {
        "id": "Section_154", "title": "CrPC Section 154 (FIR)", "type": "crpc",
        "text": "First Information Report (FIR). Information relating to cognizable offences given orally to police shall be reduced to writing, signed, and a free copy given to the informant.",
    },
    {
        "id": "Section_161", "title": "CrPC Section 161", "type": "crpc",
        "text": "Examination of witnesses by police. Police officer investigating a case may examine orally any person supposed to be acquainted with the facts.",
    },
    {
        "id": "Section_167", "title": "CrPC Section 167", "type": "crpc",
        "text": "Procedure when investigation cannot be completed in 24 hours. Accused must be produced before magistrate. Default bail (statutory bail) applies after 60 or 90 days.",
    },
    {
        "id": "Section_173", "title": "CrPC Section 173", "type": "crpc",
        "text": "Report of police officer on completion of investigation (Charge Sheet) submitted to the competent Magistrate.",
    },
    {
        "id": "Section_313", "title": "CrPC Section 313", "type": "crpc",
        "text": "Power to examine the accused. The Court shall question the accused personally on the evidence presented against him to enable explanation.",
    },
    {
        "id": "Section_374", "title": "CrPC Section 374", "type": "crpc",
        "text": "Appeals from convictions. Any person convicted by a Sessions Judge or High Court may appeal to the higher appellate forum.",
    },
    {
        "id": "Section_438", "title": "CrPC Section 438 (Anticipatory Bail)", "type": "crpc",
        "text": "Anticipatory bail. Direction for grant of bail to a person apprehending arrest for a non-bailable offence from the High Court or Court of Session BEFORE arrest.",
    },
    {
        "id": "Section_439", "title": "CrPC Section 439", "type": "crpc",
        "text": "Special powers of High Court or Sessions Court regarding bail. Special authority to grant, modify, or cancel bail in non-bailable cases.",
    },
]

# Generic stopwords to ignore during keyword matching
STOP_WORDS = {
    "article", "section", "sec", "art", "law", "act", "code", "india",
    "what", "is", "the", "of", "for", "in", "about", "explain", "tell",
    "me", "under", "details", "on", "a", "an", "to", "and", "or",
}

CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "constitution": [
        "article", "constitution", "fundamental right", "directive principle",
        "amendment", "rights", "citizen", "parliament", "president", "dpsp",
        "emergency", "writ", "habeas corpus", "mandamus", "certiorari",
        "equality", "freedom of speech", "right to life", "personal liberty",
        "right to education", "free legal aid", "untouchability", "preamble",
    ],
    "ipc": [
        "ipc", "section 302", "section 376", "section 420", "section 498",
        "murder", "theft", "robbery", "dacoity", "rape", "cheating", "fraud",
        "criminal", "offence", "punishment", "penal code", "attempt",
        "assault", "kidnapping", "dowry", "cruelty", "manslaughter",
        "culpable homicide", "extortion", "criminal breach", "intimidation",
    ],
    "crpc": [
        "crpc", "fir", "bail", "arrest", "police", "magistrate",
        "charge sheet", "investigation", "anticipatory bail", "cognizable",
        "non-cognizable", "first information report", "custody", "warrant",
        "summons", "default bail", "statutory bail", "zero fir",
    ],
    "general": [
        "contract", "agreement", "property", "rent", "tenant", "landlord",
        "consumer", "employment", "labour", "labor", "divorce", "marriage",
        "inheritance", "will", "cyber", "internet", "company", "insurance",
    ],
}

CATEGORY_LABELS = {
    "constitution": "⚖️ Constitutional Law",
    "ipc": "🔴 Indian Penal Code",
    "crpc": "🔵 Criminal Procedure",
    "general": "📋 General Law",
}

GREETINGS = {
    "hello", "hi", "hey", "namaste", "good morning", "good afternoon",
    "good evening", "greetings", "hola", "salaam",
}
FAREWELLS = {
    "bye", "goodbye", "thank you", "thanks", "ok thank you",
    "that's all", "that is all", "ok thanks", "great thanks",
}


class LegalNLPEngine:
    """Main NLP engine: Full Indian Legal Map + Strict regex word-boundary number matching + TF-IDF fallback."""

    def __init__(self):
        self.kb = LEGAL_KB
        self.vectorizer = None
        self.kb_vectors = None
        self._build_tfidf_index()
        self._try_load_model()
        print(
            f"[NLP Engine] Ready | KB: {len(self.kb)} entries"
            f" | sklearn: {_SKLEARN} | fine-tuned model: {_MODEL_LOADED}"
        )

    def _build_tfidf_index(self):
        if not _SKLEARN:
            return
        try:
            texts = [f"{e['title']} {e['text']}" for e in self.kb]
            self.vectorizer = TfidfVectorizer(
                ngram_range=(1, 2), max_features=8000, stop_words="english"
            )
            self.kb_vectors = self.vectorizer.fit_transform(texts)
            print(f"[NLP Engine] TF-IDF index built: {self.kb_vectors.shape}")
        except Exception as exc:
            print(f"[NLP Engine] TF-IDF build failed: {exc}")

    def _try_load_model(self):
        global _MODEL_LOADED, _t5_model, _t5_tokenizer
        model_path = Path(__file__).parent / "model" / "saved_model" / "final"
        if not model_path.exists():
            return
        try:
            from transformers import T5ForConditionalGeneration, T5Tokenizer

            print("[NLP Engine] Loading fine-tuned Flan-T5 model …")
            _t5_tokenizer = T5Tokenizer.from_pretrained(str(model_path))
            _t5_model = T5ForConditionalGeneration.from_pretrained(str(model_path))
            _t5_model.eval()
            _MODEL_LOADED = True
            print("[NLP Engine] Fine-tuned model loaded ✓")
        except Exception as exc:
            print(f"[NLP Engine] Model load failed: {exc}")

    def _detect_category(self, query: str) -> str:
        q = query.lower()
        scores: dict[str, int] = defaultdict(int)
        for cat, keywords in CATEGORY_KEYWORDS.items():
            for kw in keywords:
                if kw in q:
                    scores[cat] += 1
        if not scores:
            return "general"
        return max(scores, key=lambda k: scores[k])

    def _exact_number_search(self, query: str) -> dict | None:
        """Find exact Article or Section number requested using STRICT regex word boundaries."""
        q_clean = query.upper().strip()

        # Extract number tokens like "350", "302", "498A", "21A", "5", "56", "154"
        numbers = re.findall(r"\b\d+[A-Z]?\b", q_clean)

        for num in numbers:
            for entry in self.kb:
                title_upper = entry["title"].upper()
                id_upper    = entry["id"].upper()

                # STRICT Regex matching with word boundaries (\b)
                art_pattern = rf"\bARTICLE\s+{re.escape(num)}\b"
                sec_pattern = rf"\bSECTION\s+{re.escape(num)}\b"
                id_pattern  = rf"^(ARTICLE|SECTION)_{re.escape(num)}$"

                if (
                    re.search(art_pattern, title_upper)
                    or re.search(sec_pattern, title_upper)
                    or re.match(id_pattern, id_upper)
                    or (num == title_upper)
                ):
                    return entry

        return None

    def _retrieve(self, query: str, top_k: int = 3) -> list[dict]:
        """Return top-k matches from the knowledge base."""
        # 1. First priority: Strict exact article/section number match
        exact = self._exact_number_search(query)
        if exact:
            return [{"entry": exact, "score": 1.0}]

        # 2. Second priority: TF-IDF vector similarity
        if self.vectorizer is not None and self.kb_vectors is not None:
            results = self._tfidf_retrieve(query, top_k)
            if results and results[0]["score"] > 0.12:
                return results

        # 3. Third priority: Smart keyword overlap (excluding generic stop words)
        return self._smart_keyword_retrieve(query, top_k)

    def _tfidf_retrieve(self, query: str, top_k: int) -> list[dict]:
        q_vec = self.vectorizer.transform([query])
        sims = cosine_similarity(q_vec, self.kb_vectors).flatten()
        top_idx = sims.argsort()[::-1][:top_k]
        return [
            {"entry": self.kb[i], "score": float(sims[i])}
            for i in top_idx
            if sims[i] > 0.05
        ]

    def _smart_keyword_retrieve(self, query: str, top_k: int) -> list[dict]:
        """Word-overlap retrieval filtering out generic stopwords like 'article'."""
        words = re.findall(r"\w+", query.lower())
        meaningful_words = {w for w in words if w not in STOP_WORDS and len(w) > 1}

        if not meaningful_words:
            return []

        scored = []
        for entry in self.kb:
            e_text = (entry["title"] + " " + entry["text"]).lower()
            e_words = set(re.findall(r"\w+", e_text))
            overlap = len(meaningful_words & e_words)
            if overlap > 0:
                scored.append((overlap, entry))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [{"entry": e, "score": float(s)} for s, e in scored[:top_k]]

    def _format_answer(self, primary: dict, results: list[dict]) -> str:
        title = primary["title"]
        text = primary["text"]
        entry_type = primary["type"]
        label = CATEGORY_LABELS.get(entry_type, entry_type)

        parts = [f"**{title}** *({label})*\n", text]

        related = [
            r["entry"]["title"]
            for r in results[1:]
            if r.get("score", 0) > 0.07 and r["entry"]["title"] != title
        ]
        if related:
            parts.append(f"\n\n**Related:** {', '.join(related)}")

        parts.append(
            "\n\n*⚠️ For informational purposes only."
            " Consult a qualified advocate for specific legal advice.*"
        )
        return "\n".join(parts)

    def answer(self, question: str) -> dict:
        question = question.strip()
        q_lower = question.lower()

        # Greetings
        if any(g in q_lower for g in GREETINGS):
            return {
                "answer": (
                    "Hello! 👋 I'm **Legal Compass AI**, your intelligent legal assistant"
                    " trained on Indian law.\n\n"
                    "I can help you understand:\n"
                    "- ⚖️ **Constitutional Rights** — Articles 1 to 395 (Articles 14, 19, 21, 32, 56, 350, 352, 356, 368, 370…)\n"
                    "- 🔴 **IPC Sections** — Sections 1 to 511 (300, 302, 307, 376, 379, 420, 498A, 503, 506…)\n"
                    "- 🔵 **CrPC & BNS 2023** — FIR (154), bail (438, 439), arrest (41), charge sheet (173), BNS/BNSS 2023…\n"
                    "- 📋 **General Law** — Contracts, property, consumer rights, employment…\n\n"
                    "Just ask me anything in plain language! ⬇️"
                ),
                "category": "general",
                "confidence": 1.0,
                "sources": [],
            }

        # Farewells
        if any(f in q_lower for f in FAREWELLS):
            return {
                "answer": (
                    "Thank you for using **Legal Compass AI**! ⚖️\n\n"
                    "Remember, this assistant provides *informational content only*."
                    " Free legal aid is available at your nearest **DLSA** (District"
                    " Legal Services Authority) — Article 39A.\n\n"
                    "Stay informed, stay protected! 🙏"
                ),
                "category": "general",
                "confidence": 1.0,
                "sources": [],
            }

        # 1. Check Full Indian Legal Corpus Map (Articles 1-395, IPC 1-511, CrPC 1-484, BNS 2023)
        full_match = lookup_specific_provision(question)
        if full_match:
            return full_match

        # 2. Check Core Knowledge Base & Vector Search
        category = self._detect_category(question)
        results = self._retrieve(question, top_k=3)

        if not results:
            return {
                "answer": (
                    f"**Legal Information for: \"{question}\"** *(📋 General Law)*\n\n"
                    f"Your query relates to Indian legal provisions. Under Indian law, legal matters are governed by specific statutes:\n\n"
                    "• **Constitutional Law:** Governed by Articles 1 to 395 of the Constitution of India.\n"
                    "• **Criminal Law:** Governed by Bharatiya Nyaya Sanhita (BNS) 2023 / IPC 1860.\n"
                    "• **Criminal Procedure:** Governed by Bharatiya Nagarik Suraksha Sanhita (BNSS) 2023 / CrPC 1973.\n"
                    "• **Civil & Property Rights:** Governed by Transfer of Property Act 1882, Indian Contract Act 1872, and RERA 2016.\n\n"
                    "For specific case advice or legal filings, free legal aid is available nationwide at **NALSA** (`nalsa.gov.in`) under Article 39A.\n\n"
                    "*⚠️ For informational purposes only. Consult a qualified advocate for specific legal advice.*"
                ),
                "category": category,
                "confidence": 0.5,
                "sources": ["Constitution of India", "Indian Penal Code", "CrPC / BNSS 2023"],
            }

        best = results[0]
        entry = best["entry"]
        confidence = float(best.get("score", 1.0))

        if _MODEL_LOADED and confidence > 0.1:
            answer_text = self._model_answer(question, entry["text"])
        else:
            answer_text = self._format_answer(entry, results)

        return {
            "answer": answer_text,
            "category": entry["type"],
            "confidence": round(confidence, 3),
            "sources": [
                r["entry"]["title"] for r in results if r.get("score", 0) > 0.05
            ],
        }

    def get_suggestions(self, category: str | None = None) -> list[str]:
        if category and category in SUGGESTIONS:
            return SUGGESTIONS[category]
        mixed: list[str] = []
        for s in SUGGESTIONS.values():
            mixed.extend(s[:2])
        return mixed

    def get_categories(self) -> dict[str, int]:
        cats: dict[str, int] = defaultdict(int)
        for entry in self.kb:
            cats[entry["type"]] += 1
        return dict(cats)
