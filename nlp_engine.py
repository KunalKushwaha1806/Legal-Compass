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
    # ── Expert Q&A (ported from training data) ─────────────────
    {
        "id": "Expert_FundamentalRights_Overview", "title": "Fundamental Rights — Overview", "type": "constitution",
        "text": "The Fundamental Rights are guaranteed under Part III (Articles 12-35) of the Indian Constitution. They include: Right to Equality (Articles 14-18), Right to Freedom (Articles 19-22), Right against Exploitation (Articles 23-24), Right to Freedom of Religion (Articles 25-28), Cultural and Educational Rights (Articles 29-30), and Right to Constitutional Remedies (Article 32). There are 6 Fundamental Rights in total.",
    },
    {
        "id": "Expert_FundamentalRights_Suspension", "title": "Can Fundamental Rights be Suspended?", "type": "constitution",
        "text": "Yes, Fundamental Rights can be suspended during a National Emergency (Article 352) EXCEPT Articles 20 and 21 which can NEVER be suspended. The President can suspend the right to move courts for enforcement of Fundamental Rights during an emergency under Article 359.",
    },
    {
        "id": "Expert_BailableVsNonBailable", "title": "Bailable vs Non-Bailable Offences — Difference", "type": "crpc",
        "text": "In a bailable offence, bail is an absolute legal right and police must grant it. In a non-bailable offence, bail is NOT a right — it is at the discretion of the court. Examples of non-bailable: murder (Section 302 IPC), rape (Section 376 IPC), dacoity (Section 395 IPC). Cognizable offences allow police to arrest without warrant; non-cognizable require Magistrate's order.",
    },
    {
        "id": "Expert_DPSP", "title": "Directive Principles of State Policy (DPSP) — Part IV", "type": "constitution",
        "text": "Directive Principles of State Policy (DPSP) are in Part IV (Articles 36-51) of the Constitution. They are non-justiciable guidelines for government. Key DPSPs: equal pay for equal work (Article 39d), free legal aid (Article 39A), Uniform Civil Code (Article 44), living wage (Article 43). They are fundamental in governance though not enforceable in court.",
    },
    {
        "id": "Expert_MurderPunishment", "title": "Punishment for Murder — IPC 300 and 302", "type": "ipc",
        "text": "Murder is defined under Section 300 IPC and punished under Section 302 IPC: death penalty OR imprisonment for life + fine. Death penalty is awarded only in the 'rarest of rare' cases (Bachan Singh vs State of Punjab, 1980). Culpable homicide not amounting to murder (Section 304) carries up to life imprisonment or 10 years. From July 1, 2024 IPC is replaced by BNS 2023.",
    },
    {
        "id": "Expert_FIR_Procedure", "title": "FIR — What it is and How to File It", "type": "crpc",
        "text": "FIR (First Information Report) is registered under Section 154 CrPC at the police station where the offence occurred. Police must record the information in writing, read it back, and give a free copy to the informant. If police refuse to register, approach the Superintendent of Police or file before Magistrate under Section 156(3) CrPC. Zero FIR can be filed at any station. Police CANNOT refuse FIR for cognizable offences.",
    },
    {
        "id": "Expert_AnticipatorBail", "title": "Anticipatory Bail — Section 438 CrPC", "type": "crpc",
        "text": "Anticipatory bail under Section 438 CrPC allows a person apprehending arrest for a non-bailable offence to apply before the Sessions Court or High Court for bail BEFORE arrest. If granted, the person is released on bail immediately upon arrest. Courts consider: nature of accusation, criminal antecedents, possibility of fleeing. Default bail (statutory bail) under Section 167 is available if charge sheet is not filed within 60 or 90 days.",
    },
    {
        "id": "Expert_498A_Details", "title": "IPC Section 498A — Dowry Cruelty (Detailed)", "type": "ipc",
        "text": "Section 498A IPC deals with cruelty by husband or relatives towards a married woman, including physical/mental cruelty and dowry harassment. It is cognizable, non-bailable, and non-compoundable. Punishment: up to 3 years + fine. The Supreme Court in Arnesh Kumar v. State of Bihar (2014) mandated that arrest should not be automatic — proper investigation must precede arrest.",
    },
    {
        "id": "Expert_FreeLegalAid", "title": "Free Legal Aid in India — Article 39A and NALSA", "type": "constitution",
        "text": "Article 39A mandates free legal aid. The Legal Services Authorities Act 1987 operationalizes this through NALSA (National Legal Services Authority) and District/State Legal Services Authorities (DLSA/SLSA). Eligible persons: those with income below prescribed limit, women and children, SC/ST members, victims of disaster, persons with disabilities, industrial workmen, and persons in custody.",
    },
    {
        "id": "Expert_ConstitutionAmendments", "title": "Indian Constitution — Number of Amendments", "type": "constitution",
        "text": "The Indian Constitution has been amended 106 times as of 2024 under Article 368. Key amendments: 42nd (1976) — Mini Constitution, added Socialist/Secular/Integrity; 44th (1978) — removed Right to Property from Fundamental Rights; 73rd/74th (1992) — Panchayats/Municipalities; 86th (2002) — Article 21A Right to Education; 101st (2016) — GST; 106th (2023) — 33% women reservation in Parliament.",
    },
    # ── IPC Sections for Physical Offences & Crimes Against Women ──
    {
        "id": "IPC_Section_323", "title": "IPC Section 323 — Punishment for Voluntarily Causing Hurt", "type": "ipc",
        "text": "Whoever voluntarily causes hurt shall be punished with imprisonment of either description for a term which may extend to one year, or with fine which may extend to one thousand rupees, or with both. Hurt includes bodily pain, disease or infirmity. Slapping, hitting, punching are forms of hurt. BNS 2023 equivalent: Section 115.",
    },
    {
        "id": "IPC_Section_325", "title": "IPC Section 325 — Punishment for Voluntarily Causing Grievous Hurt", "type": "ipc",
        "text": "Whoever voluntarily causes grievous hurt (broken bones, loss of eye/ear/limb, permanent disfigurement) shall be punished with imprisonment of either description for a term which may extend to seven years, and shall also be liable to fine. BNS 2023 equivalent: Section 117.",
    },
    {
        "id": "IPC_Section_351", "title": "IPC Section 351 — Assault (Definition)", "type": "ipc",
        "text": "Whoever makes any gesture, or any preparation, intending or knowing it to be likely that such gesture or preparation will cause any person present to apprehend that he who makes that gesture or preparation is about to use criminal force to that person, is said to commit an assault. Assault includes any threatening act that causes apprehension of criminal force.",
    },
    {
        "id": "IPC_Section_352", "title": "IPC Section 352 — Punishment for Assault or Criminal Force", "type": "ipc",
        "text": "Whoever assaults or uses criminal force to any person otherwise than on grave and sudden provocation given by that person, shall be punished with imprisonment of either description for a term which may extend to three months, or with fine which may extend to five hundred rupees, or with both. Slapping, pushing, punching someone is criminal force under IPC 352. BNS 2023 equivalent: Section 131.",
    },
    {
        "id": "IPC_Section_354", "title": "IPC Section 354 — Assault or Criminal Force to Woman with Intent to Outrage Her Modesty", "type": "ipc",
        "text": "Whoever assaults or uses criminal force to any woman, intending to outrage or knowing it to be likely that he will thereby outrage her modesty, shall be punished with imprisonment of either description for a term which shall not be less than one year but which may extend to five years, and shall also be liable to fine. Slapping, touching, or using force against a woman's modesty falls under this section. BNS 2023: Section 74. This is a cognizable and non-bailable offence.",
    },
    {
        "id": "IPC_Section_354A", "title": "IPC Section 354A — Sexual Harassment of Women", "type": "ipc",
        "text": "Section 354A punishes sexual harassment of women including: physical contact and advances involving unwelcome and explicit sexual overtures, demand or request for sexual favours, showing pornography against a woman's will, and making sexually coloured remarks. Punishment: imprisonment up to 3 years or fine or both for the more serious acts. BNS 2023: Section 75.",
    },
    {
        "id": "IPC_Section_354B", "title": "IPC Section 354B — Assault with Intent to Disrobe a Woman", "type": "ipc",
        "text": "Whoever assaults or uses criminal force to any woman or abets such act with the intention of disrobing or compelling her to be naked shall be punished with imprisonment of not less than three years but may extend to seven years plus fine. BNS 2023: Section 76.",
    },
    {
        "id": "IPC_Section_354D", "title": "IPC Section 354D — Stalking", "type": "ipc",
        "text": "Whoever follows a woman and contacts, or attempts to contact such woman to foster personal interaction repeatedly despite a clear indication of disinterest, or monitors the use by a woman of the internet or electronic communication, commits stalking. Punishment: first conviction up to 3 years; repeat offence up to 5 years. BNS 2023: Section 78.",
    },
    {
        "id": "IPC_Section_509", "title": "IPC Section 509 — Word, Gesture or Act Intended to Insult Modesty of a Woman", "type": "ipc",
        "text": "Whoever, intending to insult the modesty of any woman, utters any word, makes any sound or gesture, or exhibits any object, intending that such word or sound shall be heard, or that such gesture or object shall be seen, by such woman, or intrudes upon the privacy of such woman, shall be punished with simple imprisonment for a term which may extend to three years, and also with fine. Eve-teasing falls under this section. BNS 2023: Section 79.",
    },
    {
        "id": "IPC_Section_294", "title": "IPC Section 294 — Obscene Acts and Songs", "type": "ipc",
        "text": "Whoever, to the annoyance of others: (a) does any obscene act in any public place, or (b) sings, recites or utters any obscene song, ballad or words, in or near any public place, shall be punished with imprisonment of either description for a term which may extend to three months, or with fine, or with both. BNS 2023: Section 294.",
    },
    {
        "id": "IPC_Section_375_376", "title": "IPC Section 375 & 376 — Rape (Definition and Punishment)", "type": "ipc",
        "text": "Section 375 defines rape as sexual intercourse by a man with a woman against her will, without her consent, or with consent obtained by fear, fraud or intoxication. Section 376 prescribes punishment: rigorous imprisonment not less than 7 years, extending to life imprisonment, plus fine. Rape of minor below 12 years: minimum 20 years, may extend to life or death. BNS 2023: Sections 63 and 64. This is a cognizable, non-bailable offence.",
    },
    {
        "id": "Domestic_Violence_Act", "title": "Protection of Women from Domestic Violence Act 2005", "type": "general",
        "text": "The Protection of Women from Domestic Violence Act 2005 (PWDVA) protects women from physical, sexual, emotional, verbal and economic abuse by a partner or family member. A woman can approach a Protection Officer (PO), magistrate, or police directly. The magistrate can issue Protection Orders, Residence Orders, Monetary Relief, Custody Orders, and Compensation Orders. The offence is cognizable and the complaint can be filed at any police station.",
    },
    {
        "id": "POSH_Act_2013", "title": "Sexual Harassment of Women at Workplace (POSH Act) 2013 & Educational Institutions", "type": "general",
        "text": "The Sexual Harassment of Women at Workplace (Prevention, Prohibition and Redressal) Act 2013 (POSH Act) applies to all workplaces, schools, colleges, and educational institutions in India. Unwelcome physical contact, requests for sexual favours, sexually coloured remarks, unwanted phone calls/messages at night or outside working hours by teachers, professors, employers or colleagues constitute sexual harassment. Every institution must have an Internal Complaints Committee (ICC) / Local Complaints Committee (LCC). Criminal remedies are also available under IPC Section 354A, IPC Section 509, and POCSO Act (if victim is under 18).",
    },
]

# Generic stopwords to ignore during keyword matching
STOP_WORDS = {
    "article", "section", "sec", "art", "law", "act", "code", "india",
    "what", "is", "the", "of", "for", "in", "about", "explain", "tell",
    "me", "under", "details", "on", "a", "an", "to", "and", "or",
    # Extra factual/quantity words that pollute keyword matching
    "how", "many", "total", "number", "count", "much", "are", "there",
    "does", "do", "has", "have", "was", "were", "be", "been", "being",
    "which", "who", "when", "where", "why", "its", "this", "that",
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

# ── Factual Q&A patterns ───────────────────────────────────────────────
# Each tuple: (regex_pattern, answer_text, category)
# Matched BEFORE any retrieval — for direct factual questions.
FACTUAL_QA: list[tuple[str, str, str]] = [
    # ── Constitution structural facts ─────────────────────────
    (
        r"how\s+many\s+articles",
        "**How Many Articles in the Indian Constitution?** *(\u2696\ufe0f Constitutional Law)*\n\n"
        "The Constitution of India originally had **395 Articles** when adopted in 1949. "
        "After various amendments, it now has **448 Articles** (as of 2024).\n\n"
        "\u2022 **Parts:** 22 Parts (Part I to Part XXII)\n"
        "\u2022 **Schedules:** 12 Schedules\n"
        "\u2022 **Amendments:** 106 (as of 2024)\n\n"
        "Adopted: **November 26, 1949** \u2014 Came into force: **January 26, 1950**\n\n"
        "*\u26a0\ufe0f For informational purposes only. Consult a qualified advocate for specific legal advice.*",
        "constitution"
    ),
    (
        r"how\s+many\s+parts.*constitution|constitution.*how\s+many\s+parts",
        "**Parts of the Indian Constitution** *(\u2696\ufe0f Constitutional Law)*\n\n"
        "The Constitution of India is divided into **22 Parts** (Part I to Part XXII).\n\n"
        "Key Parts:\n"
        "\u2022 **Part I** \u2014 The Union and its Territory (Articles 1-4)\n"
        "\u2022 **Part III** \u2014 Fundamental Rights (Articles 12-35)\n"
        "\u2022 **Part IV** \u2014 Directive Principles (Articles 36-51)\n"
        "\u2022 **Part IVA** \u2014 Fundamental Duties (Article 51A)\n"
        "\u2022 **Part V** \u2014 The Union (Executive, Parliament, Supreme Court)\n"
        "\u2022 **Part XVIII** \u2014 Emergency Provisions (Articles 352-360)\n"
        "\u2022 **Part XX** \u2014 Amendment of Constitution (Article 368)\n\n"
        "*\u26a0\ufe0f For informational purposes only. Consult a qualified advocate for specific legal advice.*",
        "constitution"
    ),
    (
        r"how\s+many\s+schedules",
        "**Schedules of the Indian Constitution** *(\u2696\ufe0f Constitutional Law)*\n\n"
        "The Constitution has **12 Schedules** (originally 8, now 12 after amendments).\n\n"
        "\u2022 **1st** \u2014 States and Union Territories\n"
        "\u2022 **2nd** \u2014 Salaries of constitutional offices\n"
        "\u2022 **3rd** \u2014 Forms of oaths and affirmations\n"
        "\u2022 **7th** \u2014 Union List, State List, Concurrent List\n"
        "\u2022 **8th** \u2014 22 Official Languages of India\n"
        "\u2022 **9th** \u2014 Laws protected from judicial review\n"
        "\u2022 **10th** \u2014 Anti-Defection Law (1985)\n"
        "\u2022 **11th** \u2014 Panchayati Raj subjects (73rd Amendment)\n"
        "\u2022 **12th** \u2014 Municipal subjects (74th Amendment)\n\n"
        "*\u26a0\ufe0f For informational purposes only. Consult a qualified advocate for specific legal advice.*",
        "constitution"
    ),
    (
        r"how\s+many\s+fundamental\s+rights",
        "**Fundamental Rights in the Indian Constitution** *(\u2696\ufe0f Constitutional Law)*\n\n"
        "There are **6 Fundamental Rights** under **Part III (Articles 12-35)**:\n\n"
        "1. **Right to Equality** (Articles 14-18) \u2014 No discrimination, equality before law, abolition of untouchability\n"
        "2. **Right to Freedom** (Articles 19-22) \u2014 6 freedoms: speech, assembly, association, movement, residence, profession\n"
        "3. **Right against Exploitation** (Articles 23-24) \u2014 No forced labour, no child labour below 14 years\n"
        "4. **Right to Freedom of Religion** (Articles 25-28) \u2014 Freedom of conscience and religion\n"
        "5. **Cultural and Educational Rights** (Articles 29-30) \u2014 Minority rights\n"
        "6. **Right to Constitutional Remedies** (Article 32) \u2014 Right to approach Supreme Court\n\n"
        "> Note: Right to Property was originally a Fundamental Right but removed by the 44th Amendment (1978). Now Article 300A.\n\n"
        "*\u26a0\ufe0f For informational purposes only. Consult a qualified advocate for specific legal advice.*",
        "constitution"
    ),
    (
        r"how\s+many\s+(?:times\s+(?:has\s+(?:the\s+)?constitution\s+been\s+)?amended|amendments)",
        "**Constitutional Amendments in India** *(\u2696\ufe0f Constitutional Law)*\n\n"
        "The Constitution has been amended **106 times** as of 2024 (procedure under **Article 368**).\n\n"
        "Notable Amendments:\n"
        "\u2022 **1st (1951)** \u2014 Added 9th Schedule to protect land reform laws\n"
        "\u2022 **42nd (1976)** \u2014 Mini Constitution; added Socialist, Secular, Integrity to Preamble; Fundamental Duties\n"
        "\u2022 **44th (1978)** \u2014 Removed Right to Property from Fundamental Rights\n"
        "\u2022 **73rd/74th (1992)** \u2014 Constitutional status to Panchayats and Municipalities\n"
        "\u2022 **86th (2002)** \u2014 Right to Education (Article 21A)\n"
        "\u2022 **101st (2016)** \u2014 Introduced GST\n"
        "\u2022 **106th (2023)** \u2014 33% reservation for women in Parliament\n\n"
        "*\u26a0\ufe0f For informational purposes only. Consult a qualified advocate for specific legal advice.*",
        "constitution"
    ),
    # ── Who/When factual ──────────────────────────────────────
    (
        r"who\s+(?:wrote|drafted|framed|made|designed|authored|is\s+(?:the\s+)?(?:father|architect|chairman))\b.*constitution|father\s+of\s+(?:the\s+)?(?:indian\s+)?constitution",
        "**Father / Architect of the Indian Constitution** *(\u2696\ufe0f Constitutional Law)*\n\n"
        "**Dr. B.R. Ambedkar** is called the Father of the Indian Constitution. "
        "He was **Chairman of the Drafting Committee** of the Constituent Assembly.\n\n"
        "Key Facts:\n"
        "\u2022 Constituent Assembly formed: **December 1946**\n"
        "\u2022 Drafting Committee: 7 members, chaired by Dr. Ambedkar\n"
        "\u2022 Constitution adopted: **November 26, 1949** (Constitution Day)\n"
        "\u2022 Constitution in force: **January 26, 1950** (Republic Day)\n"
        "\u2022 Drafting time: **2 years, 11 months, and 18 days**\n"
        "\u2022 Constituent Assembly had **299 members**\n"
        "\u2022 **Dr. Rajendra Prasad** was President of the Constituent Assembly\n\n"
        "*\u26a0\ufe0f For informational purposes only. Consult a qualified advocate for specific legal advice.*",
        "constitution"
    ),
    (
        r"when\s+was\s+(?:the\s+)?constitution\s+(?:adopted|made|passed|enacted|created|drafted|written)",
        "**Adoption of the Indian Constitution** *(\u2696\ufe0f Constitutional Law)*\n\n"
        "\u2022 **November 26, 1949** \u2014 Constitution **adopted** by Constituent Assembly (Constitution Day)\n"
        "\u2022 **January 26, 1950** \u2014 Constitution **came into force** (Republic Day)\n"
        "\u2022 Drafting took **2 years, 11 months, and 18 days**\n"
        "\u2022 **284 members** signed the Constitution\n"
        "\u2022 Replaced the **Government of India Act 1935**\n\n"
        "*\u26a0\ufe0f For informational purposes only. Consult a qualified advocate for specific legal advice.*",
        "constitution"
    ),
    (
        r"who\s+appoints\s+(?:the\s+)?chief\s+justice|chief\s+justice.*appointed\s+by",
        "**Appointment of Chief Justice of India** *(\u2696\ufe0f Constitutional Law)*\n\n"
        "The **Chief Justice of India (CJI)** is appointed by the **President of India** under **Article 124**.\n\n"
        "\u2022 By convention, the **senior-most judge** of the Supreme Court becomes CJI\n"
        "\u2022 Appointment is on recommendation of the **outgoing CJI**\n"
        "\u2022 Retirement age: **65 years**\n"
        "\u2022 CJI administers the **oath of office to the President**\n"
        "\u2022 Under the **Collegium System**, CJI + 4 senior SC judges recommend appointments\n\n"
        "*\u26a0\ufe0f For informational purposes only. Consult a qualified advocate for specific legal advice.*",
        "constitution"
    ),
    # ── IPC/CrPC counts ───────────────────────────────────────
    (
        r"how\s+many\s+(?:sections\s+)?(?:are\s+(?:there\s+)?in\s+)?(?:the\s+)?ipc|ipc.*how\s+many\s+sections",
        "**Indian Penal Code (IPC) \u2014 Section Count** *(\U0001f534 Indian Penal Code)*\n\n"
        "The **IPC 1860** has **511 Sections**.\n\n"
        "\u2022 Enacted: **October 6, 1860** (effective January 1, 1862)\n"
        "\u2022 Drafted by: **Lord Macaulay's First Law Commission**\n\n"
        "> **Important:** IPC has been **replaced** by **Bharatiya Nyaya Sanhita (BNS) 2023** "
        "from **July 1, 2024**. BNS has 358 sections.\n\n"
        "*\u26a0\ufe0f For informational purposes only. Consult a qualified advocate for specific legal advice.*",
        "ipc"
    ),
    (
        r"how\s+many\s+(?:sections\s+)?(?:are\s+(?:there\s+)?in\s+)?(?:the\s+)?crpc|crpc.*how\s+many\s+sections",
        "**Code of Criminal Procedure (CrPC) \u2014 Section Count** *(\U0001f535 Criminal Procedure)*\n\n"
        "The **CrPC 1973** has **484 Sections**.\n\n"
        "> **Important:** CrPC has been **replaced** by **Bharatiya Nagarik Suraksha Sanhita (BNSS) 2023** "
        "from **July 1, 2024**. BNSS has 531 sections.\n\n"
        "*\u26a0\ufe0f For informational purposes only. Consult a qualified advocate for specific legal advice.*",
        "crpc"
    ),
    # ── Legal term definitions ────────────────────────────────
    (
        r"what\s+is\s+habeas\s+corpus",
        "**Habeas Corpus** *(\u2696\ufe0f Constitutional Law)*\n\n"
        "**Habeas Corpus** (Latin: 'Produce the Body') is a writ directing the detaining authority "
        "to produce the detained person before the court to justify the detention.\n\n"
        "\u2022 Issued by: Supreme Court (Article 32) or High Court (Article 226)\n"
        "\u2022 Protects individual liberty against illegal detention\n"
        "\u2022 Available against both State and private individuals\n"
        "\u2022 **Cannot be suspended** during Emergency (Articles 20 & 21 are non-suspendable)\n\n"
        "**Example:** If someone is held in custody without charges, a family member or lawyer "
        "can file a Habeas Corpus petition to secure their release.\n\n"
        "*\u26a0\ufe0f For informational purposes only. Consult a qualified advocate for specific legal advice.*",
        "constitution"
    ),
    (
        r"what\s+is\s+mandamus",
        "**Mandamus** *(\u2696\ufe0f Constitutional Law)*\n\n"
        "**Mandamus** (Latin: 'We Command') is a writ commanding a public authority to perform "
        "a public duty it has failed or refused to perform.\n\n"
        "\u2022 Issued against: Public officials, government bodies, lower courts, corporations\n"
        "\u2022 Cannot be issued against: President/Governor (personal acts), private individuals\n\n"
        "**Example:** If a government authority refuses to issue a licence despite you meeting all "
        "requirements, a Mandamus writ can compel them to issue it.\n\n"
        "*\u26a0\ufe0f For informational purposes only. Consult a qualified advocate for specific legal advice.*",
        "constitution"
    ),
    (
        r"what\s+(?:are\s+(?:the\s+)?(?:5|five)\s+writs|is\s+(?:a\s+)?writ)|(?:5|five)\s+writs|types\s+of\s+writs",
        "**5 Types of Writs in Indian Law** *(\u2696\ufe0f Constitutional Law)*\n\n"
        "Writs issued by **Supreme Court (Article 32)** or **High Courts (Article 226)**:\n\n"
        "1. **Habeas Corpus** \u2014 'Produce the Body' \u2014 Free an illegally detained person\n"
        "2. **Mandamus** \u2014 'We Command' \u2014 Compel public authority to perform its legal duty\n"
        "3. **Prohibition** \u2014 Prevent a lower court from *exceeding jurisdiction* (before judgment)\n"
        "4. **Certiorari** \u2014 Quash an order of a lower court/tribunal that *exceeded jurisdiction* (after judgment)\n"
        "5. **Quo Warranto** \u2014 'By what authority' \u2014 Challenge a person's claim to a public office\n\n"
        "**Key:** Article 32 (SC) is itself a Fundamental Right. Article 226 (HC) is wider \u2014 "
        "writs can be issued for *any purpose*, not just Fundamental Rights violations.\n\n"
        "*\u26a0\ufe0f For informational purposes only. Consult a qualified advocate for specific legal advice.*",
        "constitution"
    ),
    (
        r"what\s+is\s+(?:the\s+)?preamble",
        "**Preamble of the Indian Constitution** *(\u2696\ufe0f Constitutional Law)*\n\n"
        "*\"WE, THE PEOPLE OF INDIA, having solemnly resolved to constitute India into a "
        "**SOVEREIGN SOCIALIST SECULAR DEMOCRATIC REPUBLIC** and to secure to all its citizens:\n\n"
        "**JUSTICE**, social, economic and political;\n"
        "**LIBERTY** of thought, expression, belief, faith and worship;\n"
        "**EQUALITY** of status and of opportunity;\n"
        "and to promote among them all **FRATERNITY** assuring the dignity of the individual "
        "and the **unity and integrity of the Nation** \u2014\n"
        "IN OUR CONSTITUENT ASSEMBLY this twenty-sixth day of November, 1949\"*\n\n"
        "> Note: 'Socialist', 'Secular', and 'Integrity' were added by the **42nd Amendment (1976)**.\n\n"
        "*\u26a0\ufe0f For informational purposes only. Consult a qualified advocate for specific legal advice.*",
        "constitution"
    ),
    (
        r"what\s+is\s+basic\s+structure|kesavananda\s+bharati",
        "**Basic Structure Doctrine** *(\u2696\ufe0f Constitutional Law)*\n\n"
        "Established by the Supreme Court in **Kesavananda Bharati v. State of Kerala (1973)** \u2014 "
        "13-judge bench, decided 7:6.\n\n"
        "**Principle:** Parliament CANNOT amend the *basic/essential features* of the Constitution "
        "even through Article 368.\n\n"
        "Basic features (non-exhaustive):\n"
        "\u2022 Supremacy of the Constitution\n"
        "\u2022 Democratic and Republican form of Government\n"
        "\u2022 Secular character\n"
        "\u2022 Separation of Powers\n"
        "\u2022 Federal structure\n"
        "\u2022 Judicial Review and Fundamental Rights\n"
        "\u2022 Unity and Integrity of India\n\n"
        "*\u26a0\ufe0f For informational purposes only. Consult a qualified advocate for specific legal advice.*",
        "constitution"
    ),
    (
        r"what\s+is\s+(?:a\s+)?pil|public\s+interest\s+litigation|how\s+to\s+file\s+(?:a\s+)?pil",
        "**Public Interest Litigation (PIL)** *(\u2696\ufe0f Constitutional Law)*\n\n"
        "PIL is a petition filed in Supreme Court (Article 32) or High Court (Article 226) "
        "by any citizen on behalf of the public, even if not personally affected.\n\n"
        "**How to file a PIL:**\n"
        "1. Draft petition stating the public issue and relief sought\n"
        "2. File in Supreme Court (nationwide) or High Court (state-level)\n"
        "3. Pay nominal court fees (very low to encourage public interest cases)\n"
        "4. No need to be personally affected\n\n"
        "**Key facts:**\n"
        "\u2022 First recognised in **Hussainara Khatoon v. State of Bihar (1979)**\n"
        "\u2022 Even a **postcard/letter** to the Chief Justice can become a PIL\n"
        "\u2022 Court can take **suo motu** cognizance from newspaper reports\n\n"
        "*\u26a0\ufe0f For informational purposes only. Consult a qualified advocate for specific legal advice.*",
        "constitution"
    ),
    # ── Procedural questions ──────────────────────────────────
    (
        r"(?:how\s+(?:to|(?:do|can)\s+(?:i|we|one|a\s+person))\s+(?:file|register|lodge)|steps\s+to\s+(?:file|register|lodge)|process\s+(?:of|to)\s+(?:file|register))\s+(?:a\s+|an\s+)?fir|fir\s+(?:filing|registration)\s+(?:process|steps|procedure)|how\s+(?:is\s+(?:an?\s+)?fir\s+(?:filed|registered)|to\s+register\s+(?:an?\s+)?fir)",
        "**How to File an FIR** *(\U0001f535 Criminal Procedure \u2014 Section 154 CrPC)*\n\n"
        "**Step-by-Step:**\n"
        "1. Go to the **police station** of the area where the offence occurred\n"
        "2. Give information **orally or in writing** about the offence\n"
        "3. Police officer must **record it in writing** and read it back to you\n"
        "4. **Sign the FIR** (or put thumb impression)\n"
        "5. Demand and receive the **free copy** of FIR immediately\n\n"
        "**If police refuse to register FIR:**\n"
        "\u2022 Approach the **Superintendent of Police (SP)** with a written complaint\n"
        "\u2022 File complaint before **Magistrate under Section 156(3) CrPC**\n"
        "\u2022 File a **Zero FIR** at any police station (offence need not be in that jurisdiction)\n"
        "\u2022 For cognizable offences, police **cannot legally refuse** to register an FIR\n\n"
        "*\u26a0\ufe0f For informational purposes only. Consult a qualified advocate for specific legal advice.*",
        "crpc"
    ),
    (
        r"how\s+to\s+(?:get|apply\s+for|obtain)\s+(?:anticipatory\s+)?bail|bail\s+(?:process|procedure|application)",
        "**How to Get Bail in India** *(\U0001f535 Criminal Procedure)*\n\n"
        "**1. Anticipatory Bail (Section 438 CrPC) \u2014 Before Arrest:**\n"
        "\u2022 File application before **Sessions Court or High Court**\n"
        "\u2022 State: apprehension of arrest, grounds, nature of accusation\n"
        "\u2022 If granted: released on bail immediately upon arrest\n\n"
        "**2. Regular Bail \u2014 Non-Bailable Offence (Sections 437/439 CrPC):**\n"
        "\u2022 Apply before **Magistrate (S.437)** or **Sessions Court/HC (S.439)**\n"
        "\u2022 Court considers: gravity, criminal history, flight risk, evidence tampering\n"
        "\u2022 Bail may have conditions (surety, surrender passport, periodic reporting)\n\n"
        "**3. Default/Statutory Bail (Section 167(2) CrPC):**\n"
        "\u2022 If charge sheet NOT filed within **60 days** (up to 10-yr offences) or **90 days** (serious offences)\n"
        "\u2022 Apply immediately \u2014 right lapses if charge sheet is filed before your application\n\n"
        "*\u26a0\ufe0f For informational purposes only. Consult a qualified advocate for specific legal advice.*",
        "crpc"
    ),
    (
        r"(?:what\s+are\s+my\s+)?rights\s+(?:if\s+|after\s+|when\s+|of\s+(?:an?\s+)?)arrested|arrested\s+person.*rights|rights\s+(?:of\s+)?accused",
        "**Rights of an Arrested Person in India** *(\u2696\ufe0f Constitutional Law + \U0001f535 CrPC)*\n\n"
        "**Constitutional Rights (Articles 20-22):**\n"
        "\u2022 **Article 20(1)** \u2014 No punishment for acts not criminal at time of commission\n"
        "\u2022 **Article 20(2)** \u2014 No double jeopardy (cannot be tried twice for same offence)\n"
        "\u2022 **Article 20(3)** \u2014 Cannot be compelled to be a witness against yourself\n"
        "\u2022 **Article 22** \u2014 Must be informed of grounds of arrest; right to a lawyer; produced before magistrate within 24 hours\n\n"
        "**CrPC Rights:**\n"
        "\u2022 Right to know **why** you are being arrested\n"
        "\u2022 Right to **call and meet a lawyer** of your choice immediately\n"
        "\u2022 Right to be **produced before magistrate within 24 hours**\n"
        "\u2022 Right to **free legal aid** (NALSA \u2014 Article 39A)\n"
        "\u2022 Right to **bail** in all bailable offences (absolute right)\n"
        "\u2022 Right to **medical examination** if alleging police brutality\n\n"
        "*\u26a0\ufe0f For informational purposes only. Consult a qualified advocate for specific legal advice.*",
        "constitution"
    ),
    (
        r"(?:what\s+is\s+(?:the\s+)?difference\s+between\s+)?bailable\s+(?:and|vs\.?)\s+non.bailable|bailable\s+offence",
        "**Bailable vs Non-Bailable Offences** *(\U0001f535 Criminal Procedure)*\n\n"
        "| | **Bailable** | **Non-Bailable** |\n"
        "|---|---|---|\n"
        "| Bail right | Absolute legal right | Court's discretion |\n"
        "| Granted by | Police or court | Only by court |\n"
        "| Examples | Simple hurt, minor theft | Murder (S.302), Rape (S.376) |\n"
        "| Punishment | Generally minor | 7 years to life/death |\n\n"
        "**Cognizable vs Non-Cognizable:**\n"
        "\u2022 **Cognizable** \u2014 Police can arrest WITHOUT a warrant (murder, robbery, rape)\n"
        "\u2022 **Non-Cognizable** \u2014 Police CANNOT arrest without warrant; need Magistrate's permission\n\n"
        "*\u26a0\ufe0f For informational purposes only. Consult a qualified advocate for specific legal advice.*",
        "crpc"
    ),
    # \u2500\u2500 Crimes against women \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500
    (
        r"(?:slap|hit|punch|beat|assault|attack|hurt|push|grab|touch|molest|harass)\s+(?:a\s+)?(?:girl|woman|lady|female|wife|sister|mother)|(?:what\s+(?:happens?|is\s+the\s+(?:law|punishment|offence|section))\s+if\s+(?:i|someone|a\s+person)?\s+)?(?:slap|hit|punch|beat|assault|attack|hurt|molest|eve.teas)\s+(?:a\s+)?(?:girl|woman|lady|female)",
        "**Assault / Criminal Force Against a Woman** *(\U0001f534 Indian Penal Code)*\n\n"
        "Under Indian law, any physical assault or force against a woman attracts serious criminal liability:\n\n"
        "\u2022 **IPC Section 323** \u2014 Voluntarily causing hurt \u2014 up to **1 year** imprisonment / fine\n"
        "\u2022 **IPC Section 352** \u2014 Assault or criminal force \u2014 up to **3 months** imprisonment / fine\n"
        "\u2022 **IPC Section 354** \u2014 Assault on a woman with intent to outrage her modesty \u2014 **1 to 5 years** (cognizable, non-bailable)\n"
        "\u2022 **IPC Section 354A** \u2014 Sexual harassment \u2014 up to **3 years** / fine\n"
        "\u2022 **IPC Section 509** \u2014 Words or gestures to insult a woman's modesty \u2014 up to **3 years** / fine\n\n"
        "> Under **BNS 2023** (effective July 1, 2024), the equivalent sections are:\n"
        "> IPC 323 \u2192 BNS 115 | IPC 354 \u2192 BNS 74 | IPC 354A \u2192 BNS 75 | IPC 509 \u2192 BNS 79\n\n"
        "**What the victim can do:**\n"
        "1. File an FIR at the nearest police station under Section 154 CrPC\n"
        "2. Approach a Magistrate directly under Section 156(3) CrPC if police refuse\n"
        "3. Seek protection under the **Protection of Women from Domestic Violence Act 2005** if the offender is a family member\n"
        "4. Contact **NALSA (1800-110-002)** or the nearest DLSA for free legal aid\n\n"
        "*\u26a0\ufe0f For informational purposes only. Consult a qualified advocate for specific legal advice.*",
        "ipc"
    ),
    (
        r"(?:teacher|professor|boss|manager|employer|colleague|principal|staff)\s+.*(?:call|text|message|harass|bother|touch|approach).*(?:night|inappropriate|unwanted|home)|(?:call|text|message|harass)\s+.*(?:night|unwanted|inappropriate).*(?:teacher|professor|boss|manager|girl|woman)|what\s+if\s+my\s+(?:teacher|boss|professor)\s+calls\s+me",
        "**Harassment by Teacher / Authority Figure / Workplace & College Harassment** *(\U0001f534 IPC / POSH Act 2013)*\n\n"
        "If a teacher, professor, employer, or authority figure makes unwanted calls at night, sends inappropriate messages, or harasses you, this is illegal under Indian law:\n\n"
        "**Legal Protections & Applicable Laws:**\n"
        "\u2022 **POSH Act 2013 (Workplace & Educational Institutions):** Unwelcome calls, messages, or demands outside hours by teachers or superiors constitute sexual harassment.\n"
        "\u2022 **IPC Section 354A:** Sexual harassment (unwelcome physical contact, advances, sexually coloured remarks) \u2014 punishable by up to **3 years imprisonment**.\n"
        "\u2022 **IPC Section 509:** Word, gesture or act intended to insult the modesty of a woman (including inappropriate calls/texts) \u2014 punishable by up to **3 years imprisonment**.\n"
        "\u2022 **IPC Section 354D:** Stalking / persistent unwanted contact despite disinterest \u2014 punishable by up to **3 years**.\n"
        "\u2022 **POCSO Act 2012 (If under 18 years old):** Sexual harassment of a minor student by a person in authority (teacher) is a severe non-bailable offence.\n\n"
        "**Recommended Action Steps:**\n"
        "1. **Save Evidence:** Keep call logs, text messages, audio recordings, or WhatsApp chats as proof.\n"
        "2. **Report Internally:** File a written complaint to the institution's **Internal Complaints Committee (ICC)**, Principal, or Dean.\n"
        "3. **File a Police Complaint (FIR):** Approach the local police station or Women's Police Station under IPC 354A / 509 / POCSO Act.\n"
        "4. **Helplines & Free Legal Support:**\n"
        "   \u2022 **Women Helpline:** `1091` or Emergency `112`\n"
        "   \u2022 **National Commission for Women (NCW):** `ncwapps.nic.in`\n"
        "   \u2022 **NALSA Free Legal Aid:** `1800-110-002`\n\n"
        "*\u26a0\ufe0f For informational purposes only. Consult a qualified advocate for specific legal advice.*",
        "ipc"
    ),
    (
        r"what\s+is\s+(?:the\s+)?posh\s+act|what\s+is\s+sexual\s+harassment\s+at\s+workplace",
        "**POSH Act 2013 (Sexual Harassment of Women at Workplace)** *(\U0001f534 Constitutional Law)*\n\n"
        "The **Sexual Harassment of Women at Workplace (Prevention, Prohibition and Redressal) Act, 2013** protects women against sexual harassment at all workplaces.\n\n"
        "\u2022 **Applicability:** Both organized and unorganized sectors, private and public institutions, educational facilities, and hospitals.\n"
        "\u2022 **Workplace Definition:** Any place visited by the employee during the course of employment, including transportation provided by the employer.\n"
        "\u2022 **Redressal:** Employers must constitute an **Internal Complaints Committee (ICC)** if having 10 or more employees.\n\n"
        "*\u26a0\ufe0f For informational purposes only. Consult a qualified advocate for specific legal advice.*",
        "constitution"
    ),
    (
        r"(?:eve.teas|stalk|follow|harass)\s+(?:a\s+)?(?:girl|woman|lady|female)|what\s+is\s+eve.teas|eve.teas.*law|eve.teas.*india",
        "**Eve-Teasing / Stalking / Harassment of Women** *(\U0001f534 Indian Penal Code)*\n\n"
        "\u2022 **IPC Section 354D** \u2014 Stalking \u2014 following or repeatedly contacting a woman despite her disinterest \u2014 up to **3 years** (first conviction), **5 years** (repeat)\n"
        "\u2022 **IPC Section 509** \u2014 Words, gestures, acts insulting a woman's modesty (eve-teasing) \u2014 up to **3 years** / fine\n"
        "\u2022 **IT Act Section 67** \u2014 Cyber stalking / online harassment \u2014 up to **3 years** + fine\n\n"
        "**What to do:**\n"
        "1. File FIR at the police station under IPC 354D / 509\n"
        "2. File a complaint with the **National Commission for Women (NCW)** at ncwapps.nic.in\n"
        "3. Contact **Women Helpline: 1091** or **Emergency: 112**\n"
        "4. Seek free legal aid from **NALSA (1800-110-002)**\n\n"
        "*\u26a0\ufe0f For informational purposes only. Consult a qualified advocate for specific legal advice.*",
        "ipc"
    ),
    (
        r"what\s+(?:happens?|is\s+(?:the\s+)?(?:law|punishment|section|offence|case))\s+(?:if\s+(?:i|someone|a\s+person)?\s+)?(?:hit|punch|beat|slap|assault|attack|hurt|kick|fight)\s+(?:someone|a\s+person|another\s+person|him|her)|(?:i\s+)?(?:hit|punch|slap|beat|assault|kick)\s+someone|physical\s+(?:fight|assault|violence)\s+(?:law|india|punishment|ipc)",
        "**Physical Fight / Assault Under Indian Law** *(\U0001f534 Indian Penal Code)*\n\n"
        "If you hit, punch or assault someone, these IPC sections apply:\n\n"
        "\u2022 **IPC 323** \u2014 Causing hurt (slap, punch, minor injury) \u2014 up to **1 year** + fine (bailable)\n"
        "\u2022 **IPC 325** \u2014 Causing grievous hurt (broken bones, serious injury) \u2014 up to **7 years** + fine (non-bailable)\n"
        "\u2022 **IPC 352** \u2014 Assault or criminal force \u2014 up to **3 months** + fine (bailable)\n"
        "\u2022 **IPC 324** \u2014 Causing hurt with a dangerous weapon \u2014 up to **3 years** (non-bailable)\n"
        "\u2022 **IPC 307** \u2014 Attempt to murder \u2014 up to **10 years** (non-bailable)\n\n"
        "If the victim is a **woman**, additionally:\n"
        "\u2022 **IPC 354** \u2014 Assault on woman to outrage modesty \u2014 **1 to 5 years** (non-bailable)\n\n"
        "> Under **BNS 2023** (from July 1, 2024): IPC 323 \u2192 BNS 115 | IPC 325 \u2192 BNS 117 | IPC 352 \u2192 BNS 131\n\n"
        "**Self-defence** is a valid legal defence under **IPC Section 96-106** \u2014 if force used was reasonable and proportionate to the threat.\n\n"
        "*\u26a0\ufe0f For informational purposes only. Consult a qualified advocate for specific legal advice.*",
        "ipc"
    ),
]


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
        # First try the correct path (model weights directly in model/)
        model_path = Path(__file__).parent / "model"
        # Fallback: older save location
        if not (model_path / "config.json").exists():
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
            if results and results[0]["score"] > 0.18:
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

    def _factual_answer(self, query: str) -> dict | None:
        """Return a direct answer if the query matches a known factual pattern."""
        q = query.lower().strip()
        for pattern, answer_text, category in FACTUAL_QA:
            if re.search(pattern, q, re.IGNORECASE):
                return {
                    "answer": answer_text,
                    "category": category,
                    "confidence": 1.0,
                    "sources": ["Legal Compass Factual Knowledge Base"],
                }
        return None

    def _model_answer(self, question: str, context: str) -> str | None:
        """Generate an answer using the loaded Flan-T5 model. Returns None on failure."""
        global _t5_model, _t5_tokenizer
        try:
            import torch
            input_text = f"question: {question} context: {context}"
            inputs = _t5_tokenizer(
                input_text,
                return_tensors="pt",
                max_length=512,
                truncation=True,
            )
            with torch.no_grad():
                outputs = _t5_model.generate(
                    **inputs,
                    max_new_tokens=256,
                    num_beams=4,
                    early_stopping=True,
                )
            answer_text = _t5_tokenizer.decode(outputs[0], skip_special_tokens=True).strip()
            if not answer_text or answer_text.lower().startswith("context:") or "commencement of this constitution" in answer_text.lower():
                return None
            return (
                answer_text
                + "\n\n*\u26a0\ufe0f For informational purposes only."
                " Consult a qualified advocate for specific legal advice.*"
            )
        except Exception as exc:
            print(f"[NLP Engine] Model inference failed: {exc}")
            return None

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

        # 0. Factual Q&A — direct answers to common factual questions (highest priority)
        factual = self._factual_answer(question)
        if factual:
            return factual

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

        if _MODEL_LOADED and confidence > 0.35:
            model_ans = self._model_answer(question, entry["text"])
            answer_text = model_ans if model_ans else self._format_answer(entry, results)
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
