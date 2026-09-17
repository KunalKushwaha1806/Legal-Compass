/**
 * Legal Compass — Built-in Legal Knowledge Engine
 * Provides authentic statutory Indian law responses with legal citations
 * when running in frontend preview / demo mode or if backend is offline.
 */

const LEGAL_KNOWLEDGE_BASE = [
  {
    keywords: ['article 21', 'right to life', 'personal liberty', 'privacy'],
    category: 'constitution',
    answer: `**Article 21 — Protection of Life and Personal Liberty**

> *"No person shall be deprived of his life or personal liberty except according to procedure established by law."*

### Key Principles:
1. **Universal Applicability:** Applies to citizens and non-citizens alike.
2. **Substantive Due Process:** In *Maneka Gandhi v. Union of India (1978)*, the Supreme Court held that the procedure must be "just, fair, and reasonable", not merely formal.
3. **Expansive Scope:** Over decades, the Supreme Court has expanded Article 21 to encompass:
   - **Right to Privacy:** Recognized as a fundamental right (*K.S. Puttaswamy v. Union of India, 2017*).
   - **Right to Clean Environment:** *M.C. Mehta v. Union of India*.
   - **Right to Free Legal Aid:** *Hussainara Khatoon v. Home Secretary, State of Bihar*.
   - **Right to Livelihood & Dignity:** *Olga Tellis v. Bombay Municipal Corporation*.
   - **Right to Speedy Trial:** An integral component of fundamental justice.`,
    sources: [
      { act: 'Constitution of India', section: 'Article 21', title: 'Protection of Life and Personal Liberty' },
      { act: 'Supreme Court of India', section: 'AIR 1978 SC 597', title: 'Maneka Gandhi v. Union of India' },
      { act: 'Supreme Court of India', section: '(2017) 10 SCC 1', title: 'K.S. Puttaswamy v. Union of India' }
    ]
  },
  {
    keywords: ['fir', 'first information report', 'file an fir', 'police complaint', 'zero fir'],
    category: 'procedure',
    answer: `**Procedure for Filing a First Information Report (FIR)**

Under **Section 154 of the Code of Criminal Procedure (CrPC)** [now **Section 173 of the Bharatiya Nagarik Suraksha Sanhita (BNSS), 2023**]:

### Step-by-Step Procedure:
1. **Jurisdiction & Zero FIR:**
   - An FIR can be registered at the police station having geographical jurisdiction over the scene of the offense.
   - If there is urgency, a **Zero FIR** can be lodged at *any* police station regardless of jurisdiction, and it will subsequently be transferred to the competent station (*Lalita Kumari v. Govt of UP, 2014*).

2. **Filing the Complaint:**
   - The information can be given orally or in writing.
   - If oral, the officer-in-charge must reduce it to writing and read it over to you.

3. **Mandatory Free Copy:**
   - Under Section 154(2) CrPC / Section 173(2) BNSS, you are legally entitled to receive a **free copy of the registered FIR** immediately.

4. **Remedy if Police Refuse to Register FIR:**
   - **Step 1:** Send substance of complaint in writing to the **Superintendent of Police (SP / DCP)** by registered post under Section 154(3) CrPC / Section 173(4) BNSS.
   - **Step 2:** File an application before the Judicial Magistrate under **Section 156(3) CrPC / Section 175(3) BNSS** seeking directions to register an FIR.`,
    sources: [
      { act: 'Code of Criminal Procedure (CrPC)', section: 'Section 154', title: 'Information in cognizable cases' },
      { act: 'Bharatiya Nagarik Suraksha Sanhita (BNSS)', section: 'Section 173', title: 'Information in cognizable cases & Zero FIR' },
      { act: 'Supreme Court of India', section: '(2014) 2 SCC 1', title: 'Lalita Kumari v. Govt of UP' }
    ]
  },
  {
    keywords: ['anticipatory bail', 'section 438', 'arrest', 'bail before arrest', 'apprehension of arrest'],
    category: 'procedure',
    answer: `**Anticipatory Bail under Indian Law**

Governed by **Section 438 of the CrPC** [now **Section 482 of BNSS, 2023**]:

### What is Anticipatory Bail?
Anticipatory bail is a pre-arrest legal protection granted by a **Sessions Court** or the **High Court** directing that in the event of an arrest on accusation of having committed a non-bailable offense, the person shall be released on bail.

### Key Legal Guidelines:
1. **Conditions Imposed:**
   - Making oneself available for interrogation by police officers as required.
   - Not directly or indirectly making any inducement, threat, or promise to witnesses.
   - Not leaving India without prior permission of the court.
2. **Landmark Rulings:**
   - *Gurbaksh Singh Sibbia v. State of Punjab (1980):* Constitution Bench established that anticipatory bail should not be fettered with unnecessary restrictions.
   - *Sushila Aggarwal v. State (NCT of Delhi) (2020):* Held that anticipatory bail does not automatically expire upon filing of chargesheet; it can continue till the end of trial unless canceled.
   - *Arnesh Kumar v. State of Bihar (2014):* Police cannot automatically arrest for offenses punishable with imprisonment up to 7 years without complying with Section 41A CrPC notice requirements.`,
    sources: [
      { act: 'Code of Criminal Procedure (CrPC)', section: 'Section 438', title: 'Direction for grant of bail to person apprehending arrest' },
      { act: 'Bharatiya Nagarik Suraksha Sanhita (BNSS)', section: 'Section 482', title: 'Direction for grant of bail to person apprehending arrest' },
      { act: 'Supreme Court of India', section: '(2020) 5 SCC 1', title: 'Sushila Aggarwal v. State (NCT of Delhi)' }
    ]
  },
  {
    keywords: ['murder', 'ipc 302', 'section 302', 'bns 103', 'punishment for murder'],
    category: 'criminal',
    answer: `**Section 302 Indian Penal Code (IPC) — Punishment for Murder**
*(Corresponding Section: **Section 103 of Bharatiya Nyaya Sanhita, 2023 (BNS)**)*

### Definition & Ingredients:
Murder is defined under **Section 300 IPC** / **Section 101 BNS**:
- An act done with the intention of causing death, or
- Causing bodily injury known to be likely to cause death, or
- Bodily injury sufficient in the ordinary course of nature to cause death.

### Punishment:
Under Section 302 IPC / Section 103(1) BNS:
- **Capital Punishment (Death penalty)**, OR
- **Imprisonment for life**, AND
- **Liable to fine**.

### Sentencing Doctrine:
- **"Rarest of Rare Cases" Doctrine:** The Supreme Court in *Bachan Singh v. State of Punjab (1980)* held that the death penalty should only be awarded in the rarest of rare cases where the alternative option of life imprisonment is unquestionably foreclosed.
- *Machhi Singh v. State of Punjab (1983):* Laid down aggravating and mitigating circumstances including the manner of commission, motive, and vulnerability of the victim.`,
    sources: [
      { act: 'Indian Penal Code (IPC)', section: 'Section 302', title: 'Punishment for murder' },
      { act: 'Bharatiya Nyaya Sanhita (BNS)', section: 'Section 103', title: 'Punishment for murder' },
      { act: 'Supreme Court of India', section: '(1980) 2 SCC 684', title: 'Bachan Singh v. State of Punjab' }
    ]
  },
  {
    keywords: ['tenant', 'rent', 'landlord', 'eviction', 'tenancy'],
    category: 'civil',
    answer: `**Rights and Protections of Tenants in India**

Governed by State Rent Control Acts and the **Model Tenancy Act, 2021**:

### Essential Legal Protections:
1. **Protection Against Arbitrary Eviction:**
   - A landlord cannot forcibly evict a tenant, disconnect water/electricity supplies, or change locks without due process of law. Eviction requires a decree from a competent Rent Authority or civil court.
2. **Written Tenancy Agreement:**
   - Mandatory execution of a rent agreement specifying rent, tenure, and security deposit terms.
3. **Security Deposit Ceiling:**
   - Under the Model Tenancy Act, security deposits are capped at a maximum of **2 months' rent** for residential premises and **6 months' rent** for commercial premises.
4. **Notice Period for Entry & Rent Revision:**
   - Landlords must give at least **24 hours' written notice** before entering rented premises for inspection or repairs.
   - At least **3 months' prior notice** is required before revising rent.
5. **Right to Basic Amenities:**
   - Essential services (water, electricity, sanitation) cannot be withheld under any circumstances even in case of rent dispute.`,
    sources: [
      { act: 'Ministry of Housing & Urban Affairs', section: 'Model Tenancy Act 2021', title: 'Tenancy agreement and eviction regulations' },
      { act: 'Transfer of Property Act, 1882', section: 'Section 106 - 111', title: 'Duration and determination of leases' }
    ]
  },
  {
    keywords: ['498a', 'dowry', 'cruelty', 'domestic violence', 'section 498a'],
    category: 'criminal',
    answer: `**Section 498A IPC — Cruelty by Husband or Relatives of Husband**
*(Corresponding Section: **Section 85 of Bharatiya Nyaya Sanhita, 2023 (BNS)**)*

### Definition:
Whoever, being the husband or the relative of the husband of a woman, subjects such woman to cruelty shall be punished:
- **Imprisonment:** Up to **3 years**, AND
- **Fine**.

### What constitutes "Cruelty":
1. **Mental or physical harm:** Willful conduct of such a nature as is likely to drive the woman to commit suicide or cause grave injury or danger to life, limb, or health.
2. **Unlawful demands (Dowry):** Harassment of the woman with a view to coercing her or any person related to her to meet any unlawful demand for property or valuable security.

### Procedural Safeguards:
- **Cognizable and Non-bailable:** Traditionally non-bailable, requiring bail from court.
- In *Social Action Forum for Manav Adhikar v. Union of India (2018)* and *Arnesh Kumar v. State of Bihar (2014)*, the Supreme Court mandated that arrest is not automatic and police must record specific reasons satisfying Section 41/41A CrPC.`,
    sources: [
      { act: 'Indian Penal Code (IPC)', section: 'Section 498A', title: 'Husband or relative of husband of a woman subjecting her to cruelty' },
      { act: 'Bharatiya Nyaya Sanhita (BNS)', section: 'Section 85', title: 'Cruelty to woman' },
      { act: 'Protection of Women from Domestic Violence Act', section: '2005', title: 'Civil remedies, protection orders and residence orders' }
    ]
  },
  {
    keywords: ['article 14', 'equality', 'equal protection', 'discrimination'],
    category: 'constitution',
    answer: `**Article 14 of the Constitution of India — Equality Before Law**

> *"The State shall not deny to any person equality before the law or the equal protection of the laws within the territory of India."*

### Two Core Concepts:
1. **Equality Before Law (Negative concept, British origin):** Absence of any special privilege in favor of any individual; all individuals are subject to ordinary law administered by ordinary courts.
2. **Equal Protection of the Laws (Positive concept, US origin):** Equality of treatment under equal circumstances; equals must be treated equally (*like should be treated alike*).

### Doctrine of Reasonable Classification:
Article 14 permits classification if two conditions are met:
- The classification must be founded on an **intelligible differentia** distinguishing persons/things grouped together from others left out.
- The differentia must have a **rational nexus** to the object sought to be achieved by the statute (*State of West Bengal v. Anwar Ali Sarkar*).

In *E.P. Royappa v. State of Tamil Nadu (1974)*, the Supreme Court established that Article 14 strikes at **arbitrariness** — equality and arbitrariness are sworn enemies.`,
    sources: [
      { act: 'Constitution of India', section: 'Article 14', title: 'Equality before law' },
      { act: 'Supreme Court of India', section: 'AIR 1974 SC 555', title: 'E.P. Royappa v. State of Tamil Nadu' }
    ]
  }
];

/**
 * Match a question against the built-in legal knowledge base
 */
export function getDemoLegalAnswer(question) {
  const qLower = question.toLowerCase();

  for (const item of LEGAL_KNOWLEDGE_BASE) {
    if (item.keywords.some((kw) => qLower.includes(kw))) {
      return {
        answer: item.answer + '\n\n---\n*💡 Note: Running in Demo / Preview Mode. For live fine-tuned GPU inference, configure your backend URL.*',
        category: item.category,
        sources: item.sources,
        response_time: 0.12,
      };
    }
  }

  // Generic fallback if question doesn't match predefined topics
  return {
    answer: `**Legal Overview for: "${question}"**\n\nUnder Indian jurisprudence, legal remedies and rights are governed by three primary pillars:\n\n1. **Constitutional Safeguards:** Fundamental rights guaranteed under Part III of the Constitution of India (Articles 12–35).\n2. **Substantive Penal Provisions:** Indian Penal Code, 1860 / Bharatiya Nyaya Sanhita, 2023 (BNS).\n3. **Procedural Framework:** Code of Criminal Procedure, 1973 / Bharatiya Nagarik Suraksha Sanhita, 2023 (BNSS) and Civil Procedure Code, 1908 (CPC).\n\n### Next Legal Steps:\n- Consult the relevant statutory provisions and district legal service authorities (DLSA).\n- For indigent citizens, free legal aid is constitutionally guaranteed under **Article 39A** and administered via **NALSA** (National Legal Services Authority).\n\n---\n*💡 Note: This is an automated summary from the built-in Legal Compass knowledge base (Demo Mode). Connect your live backend via VITE_API_URL for deep-learning Colab model responses.*`,
    category: 'general',
    sources: [
      { act: 'Constitution of India', section: 'Article 39A', title: 'Equal justice and free legal aid' },
      { act: 'Legal Services Authorities Act', section: '1987', title: 'Statutory framework for legal aid in India' }
    ],
    response_time: 0.18,
  };
}
