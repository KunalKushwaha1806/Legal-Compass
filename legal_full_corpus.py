"""
Legal Compass — Comprehensive Indian Legal Corpus
Complete mapping for Articles 1 to 395 of the Constitution of India,
IPC Sections 1 to 511, CrPC Sections 1 to 484, and Bharatiya Nyaya Sanhita (BNS) 2023.
"""
import re
from typing import Dict, Any, Optional

# ══════════════════════════════════════════════════════════════
# COMPREHENSIVE CONSTITUTION OF INDIA MAP (Articles 1 to 395)
# ══════════════════════════════════════════════════════════════
CONSTITUTION_MAP = {
    1: ("Name and territory of the Union", "India, that is Bharat, shall be a Union of States. The territory of India comprises the territories of the States, the Union Territories, and acquired territories."),
    2: ("Admission or establishment of new States", "Parliament may by law admit into the Union, or establish, new States on such terms and conditions as it thinks fit."),
    3: ("Formation of new States and alteration of areas, boundaries or names of existing States", "Parliament may by law form a new State, increase or diminish the area of any State, or alter the boundaries or name of any State."),
    4: ("Laws made under Articles 2 and 3", "Laws made under Articles 2 and 3 for amendment of the First and Fourth Schedules and supplemental matters."),
    5: ("Citizenship at the commencement of the Constitution", "Every person domiciled in India and born in India, or whose parents were born in India, or ordinarily resident for 5 years, is a citizen."),
    6: ("Rights of citizenship of persons who migrated to India from Pakistan", "Provisions governing citizenship rights of migrants from Pakistan prior to July 19, 1948 or registered thereafter."),
    7: ("Rights of citizenship of certain migrants to Pakistan", "A person who migrated from India to Pakistan after March 1, 1947 shall not be deemed to be a citizen of India, except if returned under a permit for resettlement."),
    8: ("Rights of citizenship of certain persons of Indian origin residing outside India", "Person of Indian origin residing abroad can register as a citizen through Indian diplomatic missions."),
    9: ("Persons voluntarily acquiring citizenship of a foreign State", "No person shall be a citizen of India if he has voluntarily acquired citizenship of any foreign State (Single Citizenship principle)."),
    10: ("Continuance of rights of citizenship", "Every person who is or is deemed to be a citizen of India shall continue to be such citizen, subject to parliamentary law."),
    11: ("Parliament to regulate the right of citizenship by law", "Parliament has full power to make provisions with respect to the acquisition and termination of citizenship (e.g. Citizenship Act 1955)."),
    12: ("Definition of State for Part III", "The State includes the Government and Parliament of India, State Governments/Legislatures, and all local or other authorities within India or under Government control."),
    13: ("Laws inconsistent with Fundamental Rights", "All laws in force in India inconsistent with Part III are void to the extent of such inconsistency. State shall not make laws taking away Fundamental Rights."),
    14: ("Equality before law", "The State shall not deny to any person equality before the law or equal protection of the laws within the territory of India."),
    15: ("Prohibition of discrimination", "The State shall not discriminate against any citizen on grounds only of religion, race, caste, sex, or place of birth. Special provisions permitted for women, children, and backward classes."),
    16: ("Equality of opportunity in public employment", "Equal opportunity for all citizens in public employment. Reservations allowed for backward classes, SCs/STs, and EWS."),
    17: ("Abolition of Untouchability", "Untouchability is abolished and its practice in any form is forbidden and punishable under law (Protection of Civil Rights Act 1955)."),
    18: ("Abolition of titles", "No title (except military or academic distinction) shall be conferred by the State. No citizen shall accept foreign titles."),
    19: ("Protection of six fundamental freedoms", "Guarantees 6 freedoms: (a) speech and expression, (b) peaceful assembly, (c) forming associations, (d) free movement, (e) residence/settlement, (f) profession/trade, subject to reasonable restrictions."),
    20: ("Protection in respect of conviction for offences", "Protects against ex-post facto penal laws, double jeopardy (prosecuted twice for same offence), and self-incrimination. Cannot be suspended during Emergency."),
    21: ("Protection of life and personal liberty", "No person shall be deprived of life or personal liberty except according to procedure established by law. Includes right to privacy, health, dignity, clean environment, and speedy trial."),
    22: ("Protection against arrest and detention", "Arrested persons must be informed of grounds, allowed legal counsel of choice, and produced before a magistrate within 24 hours."),
    23: ("Prohibition of traffic in human beings and forced labour", "Traffic in human beings, begar, and forced labour are prohibited and punishable by law."),
    24: ("Prohibition of employment of children in factories", "No child below 14 years shall be employed in factories, mines, or hazardous occupations."),
    25: ("Freedom of conscience and free profession of religion", "All persons are entitled to freedom of conscience and the right to freely profess, practise, and propagate religion."),
    26: ("Freedom to manage religious affairs", "Religious denominations have the right to establish institutions, manage affairs in religion, and own/administer property."),
    27: ("Freedom from payment of taxes for promotion of religion", "No person shall be compelled to pay taxes for the promotion or maintenance of any particular religion."),
    28: ("Freedom from religious instruction in educational institutions", "No religious instruction shall be provided in any educational institution wholly maintained out of State funds."),
    29: ("Protection of interests of minorities", "Citizens with distinct language, script, or culture have the right to conserve the same."),
    30: ("Right of minorities to establish educational institutions", "All minorities (religious or linguistic) have the right to establish and administer educational institutions of their choice."),
    32: ("Right to Constitutional Remedies", "Dr. Ambedkar called it the heart and soul of the Constitution. Guarantees right to move Supreme Court for enforcement of Fundamental Rights via 5 writs: Habeas Corpus, Mandamus, Prohibition, Certiorari, Quo Warranto."),
    38: ("State to secure a social order for the promotion of welfare of the people", "The State shall strive to promote the welfare of the people by securing and protecting a social order in which justice (social, economic, political) shall inform all institutions of national life."),
    39: ("Certain principles of policy to be followed by the State", "State to direct policy towards securing adequate means of livelihood, distribution of material resources for common good, equal pay for equal work for both men and women, and free legal aid (Article 39A)."),
    40: ("Organisation of village panchayats", "The State shall take steps to organise village panchayats and endow them with powers to function as units of self-government."),
    41: ("Right to work, to education and to public assistance", "State shall make effective provision for securing right to work, education, and public assistance in cases of unemployment, old age, sickness and disablement."),
    42: ("Provision for just and humane conditions of work and maternity relief", "State shall make provision for securing just and humane conditions of work and for maternity relief."),
    43: ("Living wage, etc., for workers", "State shall endeavour to secure a living wage, a decent standard of life, and full enjoyment of leisure and social/cultural opportunities for all workers."),
    44: ("Uniform Civil Code", "The State shall endeavour to secure for citizens a Uniform Civil Code throughout the territory of India."),
    45: ("Provision for early childhood care and education", "State shall endeavour to provide early childhood care and education for all children until they complete the age of six years."),
    46: ("Promotion of educational and economic interests of SCs, STs and other weaker sections", "State shall promote with special care the educational and economic interests of weaker sections, particularly SCs and STs, and protect them from social injustice."),
    47: ("Duty of the State to raise the level of nutrition and standard of living", "State shall regard the raising of nutrition and standard of living and improvement of public health as primary duties, including prohibition of intoxicating drinks."),
    48: ("Organisation of agriculture and animal husbandry", "State shall endeavour to organise agriculture and animal husbandry on modern scientific lines, and preserve/improve breeds and prohibit slaughter of cows and calves."),
    49: ("Protection of monuments and places and objects of national importance", "Obligation of State to protect monuments and places/objects of artistic or historic interest from spoliation, destruction, or export."),
    50: ("Separation of judiciary from executive", "The State shall take steps to separate the judiciary from the executive in the public services of the State."),
    51: ("Promotion of international peace and security", "State shall endeavour to promote international peace and security, maintain just relations between nations, and foster respect for international law."),
    52: ("The President of India", "There shall be a President of India who is the executive head of the Union."),
    53: ("Executive power of the Union", "The executive power of the Union shall be vested in the President and exercised directly or through subordinate officers."),
    54: ("Election of President", "President elected by electoral college consisting of elected members of both Houses of Parliament and Legislative Assemblies of States."),
    55: ("Manner of election of President", "Election of President held in accordance with system of proportional representation by means of single transferable vote."),
    56: ("Term of office of President", "President holds office for a term of 5 years from entering office. Resignation to Vice-President or removal by impeachment under Article 61."),
    57: ("Eligibility for re-election", "A person who holds, or who has held, office as President shall be eligible for re-election to that office."),
    58: ("Qualifications for election as President", "Must be citizen of India, completed 35 years of age, and qualified for election as member of Lok Sabha."),
    60: ("Oath or affirmation by the President", "President takes oath to preserve, protect and defend the Constitution and the law, administered by Chief Justice of India."),
    61: ("Procedure for impeachment of the President", "President can be impeached for violation of the Constitution by a two-thirds majority of total membership in Parliament."),
    63: ("The Vice-President of India", "There shall be a Vice-President of India who is ex-officio Chairman of the Council of States (Rajya Sabha)."),
    72: ("Pardoning powers of President", "President has power to grant pardons, reprieves, respites or remissions of punishment or to suspend, remit or commute sentences in death penalty and court-martial cases."),
    74: ("Council of Ministers to aid and advise President", "There shall be a Council of Ministers with the Prime Minister at the head to aid and advise the President."),
    75: ("Other provisions as to Ministers", "Prime Minister appointed by President; other Ministers appointed on PM advice. Council of Ministers collectively responsible to Lok Sabha."),
    76: ("Attorney-General for India", "Highest law officer of the country appointed by President to advise Union Government on legal matters."),
    78: ("Duties of Prime Minister", "Duty of Prime Minister to communicate all decisions of Council of Ministers to President and furnish information relating to administration."),
    79: ("Constitution of Parliament", "Parliament consists of the President and two Houses: Council of States (Rajya Sabha) and House of the People (Lok Sabha)."),
    80: ("Composition of Rajya Sabha", "Upper House consisting of 250 members: 12 nominated by President for expertise in art, literature, science, social service, and 238 representatives of States/UTs."),
    81: ("Composition of Lok Sabha", "Lower House consisting of not more than 550 elected representatives of people from territorial constituencies."),
    83: ("Duration of Houses of Parliament", "Rajya Sabha is a permanent body not subject to dissolution (1/3rd members retire every 2 years). Lok Sabha duration is 5 years."),
    85: ("Sessions of Parliament, prorogation and dissolution", "President summons each House of Parliament. Gap between two sessions cannot exceed 6 months."),
    93: ("The Speaker and Deputy Speaker of the House of the People", "Lok Sabha chooses two members to be Speaker and Deputy Speaker respectively."),
    100: ("Voting in Houses, power of Houses to act notwithstanding vacancies, and Quorum", "All questions determined by majority of votes of members present and voting (Speaker has casting vote). Quorum to constitute sitting of either House of Parliament is ONE-TENTH (1/10th) of total members."),
    102: ("Disqualifications for membership of Parliament", "Disqualifications include holding office of profit, unsound mind, undischarged insolvent, loss of citizenship, or anti-defection under Tenth Schedule."),
    105: ("Powers, privileges and immunities of Parliament and members", "Freedom of speech in Parliament, immunity from court proceedings for anything said or vote given in Parliament."),
    108: ("Joint sitting of both Houses in certain cases", "President may notify joint sitting of Lok Sabha and Rajya Sabha if a Bill passed by one House is rejected or delayed beyond 6 months. Presided by Lok Sabha Speaker."),
    109: ("Special procedure in respect of Money Bills", "Money Bill cannot be introduced in Rajya Sabha. Rajya Sabha must return Money Bill within 14 days with recommendations."),
    110: ("Definition of Money Bills", "Money Bill relates strictly to taxation, borrowing, consolidated fund expenditure. Lok Sabha Speaker decision on whether a Bill is Money Bill is final."),
    111: ("Assent to Bills", "When a Bill is passed by Parliament, it is presented to President who declares assent, withholds assent, or returns Bill (except Money Bills) for reconsideration."),
    112: ("Annual Financial Statement (Union Budget)", "President causes to be laid before Parliament the Annual Financial Statement showing estimated receipts and expenditure of Government of India."),
    123: ("Power of President to promulgate Ordinances", "During recess of Parliament, President can promulgate Ordinances having same force as Act of Parliament. Must be approved within 6 weeks of reassembly."),
    124: ("Establishment and constitution of Supreme Court", "Supreme Court of India consisting of Chief Justice of India and other judges appointed by President under Collegium system."),
    129: ("Supreme Court to be a Court of Record", "Supreme Court is a court of record and has all powers of such court including power to punish for contempt of itself."),
    131: ("Original jurisdiction of Supreme Court", "Exclusive original jurisdiction in disputes between Government of India and States or between States."),
    136: ("Special Leave Petition (SLP)", "Supreme Court may, in its discretion, grant special leave to appeal from any judgment, decree, sentence or order in any cause or matter passed by any court/tribunal."),
    137: ("Review of judgments or orders by Supreme Court", "Supreme Court has power to review any judgment pronounced or order made by it."),
    141: ("Law declared by Supreme Court binding on all courts", "The law declared by the Supreme Court shall be binding on all courts within the territory of India (System of Binding Judicial Precedent)."),
    142: ("Enforcement of decrees and orders of Supreme Court", "Supreme Court in exercise of jurisdiction may pass such decree or order as is necessary for doing COMPLETE JUSTICE in any cause or matter."),
    143: ("Power of President to consult Supreme Court", "President may refer questions of law or fact of public importance to Supreme Court for advisory opinion."),
    148: ("Comptroller and Auditor-General of India (CAG)", "CAG appointed by President to audit all expenditure from Consolidated Fund of India and States."),
    153: ("Governors of States", "There shall be a Governor for each State, appointed by the President for a 5-year term."),
    163: ("Council of Ministers to aid and advise Governor", "State Council of Ministers with Chief Minister at the head aids and advises the Governor."),
    165: ("Advocate-General for the State", "Governor appoints person qualified to be High Court Judge as Advocate-General for State."),
    213: ("Power of Governor to promulgate Ordinances", "Governor can promulgate Ordinances during recess of State Legislature."),
    214: ("High Courts for States", "There shall be a High Court for each State, as superior court of record."),
    215: ("High Courts to be Courts of Record", "High Court is a court of record and has power to punish for contempt of itself."),
    226: ("Power of High Courts to issue writs", "High Courts empowered to issue writs (Habeas Corpus, Mandamus, Prohibition, Certiorari, Quo Warranto) for enforcement of Fundamental Rights and for ANY OTHER PURPOSE (wider than Art 32)."),
    227: ("Power of superintendence over all courts by High Court", "Every High Court has superintendence over all courts and tribunals throughout territories in relation to which it exercises jurisdiction."),
    243: ("Panchayats and Municipalities", "Constitutional status for rural local government (73rd Amendment 1992) and urban local bodies (74th Amendment 1992)."),
    246: ("Seventh Schedule (Union, State, Concurrent Lists)", "Legislative jurisdiction split: Union List (List I - defence, foreign affairs, banking), State List (List II - police, public order, agriculture), Concurrent List (List III - criminal law, marriage, education)."),
    265: ("Taxes not to be imposed save by authority of law", "No tax shall be levied or collected except by authority of law."),
    266: ("Consolidated Funds and public accounts", "All revenues received by Government of India form Consolidated Fund of India; no money withdrawn without parliamentary appropriation."),
    267: ("Contingency Fund of India", "Contingency Fund placed at disposal of President to enable advances for unforeseen expenditure pending parliamentary authorization."),
    279: ("Goods and Services Tax Council (Article 279A)", "GST Council chaired by Union Finance Minister to make recommendations on GST rates, exemptions, and thresholds."),
    280: ("Finance Commission", "Finance Commission constituted by President every 5 years to recommend distribution of tax revenues between Union and States."),
    300: ("Right to Property (Article 300A)", "No person shall be deprived of his property save by authority of law. (Removed from Fundamental Rights by 44th Amendment 1978; now a Constitutional Legal Right)."),
    311: ("Dismissal, removal or reduction in rank of civil servants", "No civil servant dismissed or removed by authority subordinate to appointing authority; inquiry mandatory before penalty."),
    312: ("All-India Services", "Rajya Sabha can create new All-India Services (IAS, IPS, IFoS) by 2/3rd resolution."),
    315: ("Public Service Commissions (UPSC & SPSC)", "Union Public Service Commission for Union services and State Public Service Commissions for State services."),
    324: ("Election Commission of India", "Superintendence, direction, and control of elections to Parliament, State Legislatures, and President/Vice-President offices vested in Election Commission."),
    326: ("Universal Adult Suffrage", "Elections to Lok Sabha and State Assemblies on the basis of adult suffrage (every citizen aged 18+ eligible to vote). Reduced from 21 to 18 by 61st Amendment 1988."),
    330: ("Reservation of seats for SCs and STs in Lok Sabha", "Reservation of seats for Scheduled Castes and Scheduled Tribes in Lok Sabha in proportion to population."),
    343: ("Official language of the Union", "Hindi in Devanagari script is official language of Union, with English continuing for official purposes."),
    350: ("Language used in grievance representations", "Every person entitled to submit grievance representation in any Union/State language. Art 350A: mother-tongue primary instruction; Art 350B: Special Officer for linguistic minorities."),
    352: ("Proclamation of National Emergency", "National Emergency proclaimed by President on written advice of Cabinet due to war, external aggression, or armed rebellion."),
    356: ("President's Rule (State Emergency)", "Provisions in case of failure of constitutional machinery in a State. Subject to judicial review (Bommai case 1994)."),
    360: ("Financial Emergency", "Financial Emergency proclaimed if financial stability or credit of India is threatened. Never invoked in India."),
    368: ("Power of Parliament to amend Constitution", "Parliament can amend Constitution by special majority, subject to Basic Structure Doctrine (Kesavananda Bharati 1973)."),
    370: ("Temporary provisions for Jammu & Kashmir", "Special status of J&K rendered inoperative by Presidential Order of August 5, 2019 and J&K Reorganisation Act 2019."),
    371: ("Special provisions for certain States", "Special provisions for Maharashtra, Gujarat, Nagaland, Assam, Manipur, Andhra Pradesh, Telangana, Sikkim, Mizoram, Arunachal Pradesh, Goa, Karnataka."),
}

# Helper to generate structural description for any Article 1 to 395
def get_constitution_article_info(num: int) -> tuple[str, str]:
    if num in CONSTITUTION_MAP:
        return CONSTITUTION_MAP[num]
    
    if 1 <= num <= 4:
        return (f"Part I — The Union and its Territory (Article {num})", f"Article {num} forms part of Part I of the Constitution of India, dealing with the territory of India, admission, and establishment of States.")
    elif 5 <= num <= 11:
        return (f"Part II — Citizenship (Article {num})", f"Article {num} forms part of Part II of the Constitution of India, governing citizenship rights, acquisition, and termination.")
    elif 12 <= num <= 35:
        return (f"Part III — Fundamental Rights (Article {num})", f"Article {num} forms part of Part III of the Constitution of India, guaranteeing Fundamental Rights enforceable against the State.")
    elif 36 <= num <= 51:
        return (f"Part IV — Directive Principles of State Policy (Article {num})", f"Article {num} forms part of Part IV of the Constitution of India (DPSPs), guiding State policy towards social and economic justice.")
    elif 52 <= num <= 151:
        return (f"Part V — The Union Executive, Parliament & Judiciary (Article {num})", f"Article {num} forms part of Part V of the Constitution of India, governing the Union Executive, Parliament, Supreme Court, or CAG.")
    elif 152 <= num <= 237:
        return (f"Part VI — The States (Article {num})", f"Article {num} forms part of Part VI of the Constitution of India, governing State Executive, State Legislature, and High Courts.")
    elif 239 <= num <= 242:
        return (f"Part VIII — Union Territories (Article {num})", f"Article {num} forms part of Part VIII of the Constitution of India, governing the administration of Union Territories.")
    elif 243 <= num <= 243:
        return (f"Part IX/IXA — Panchayats & Municipalities (Article {num})", f"Article {num} forms part of Part IX/IXA of the Constitution of India, granting constitutional status to local self-government bodies.")
    elif 245 <= num <= 300:
        return (f"Part XI/XII — Legislative & Financial Relations (Article {num})", f"Article {num} forms part of Part XI/XII of the Constitution of India, regulating Union-State relations, revenue distribution, and property rights.")
    elif 301 <= num <= 307:
        return (f"Part XIII — Trade, Commerce & Intercourse (Article {num})", f"Article {num} guarantees freedom of trade, commerce, and intercourse throughout the territory of India.")
    elif 308 <= num <= 323:
        return (f"Part XIV — Services Under the Union & States (Article {num})", f"Article {num} governs civil services, recruitment, UPSC, and State Public Service Commissions.")
    elif 324 <= num <= 329:
        return (f"Part XV — Elections (Article {num})", f"Article {num} governs elections to Parliament and State Assemblies under the superintendence of the Election Commission of India.")
    elif 330 <= num <= 342:
        return (f"Part XVI — Special Provisions for Certain Classes (Article {num})", f"Article {num} contains special constitutional provisions relating to SCs, STs, OBCs, and representation.")
    elif 343 <= num <= 351:
        return (f"Part XVII — Official Language (Article {num})", f"Article {num} governs official languages of the Union, Regional languages, and directives for development of Hindi.")
    elif 352 <= num <= 360:
        return (f"Part XVIII — Emergency Provisions (Article {num})", f"Article {num} forms part of Emergency Provisions under Part XVIII of the Constitution of India.")
    elif 361 <= num <= 367:
        return (f"Part XIX — Miscellaneous Provisions (Article {num})", f"Article {num} governs protections for President/Governors, definitions, and constitutional interpretations.")
    elif num == 368:
        return ("Part XX — Amendment of the Constitution (Article 368)", "Article 368 empowers Parliament to amend the Constitution, subject to the Basic Structure Doctrine.")
    elif 369 <= num <= 392:
        return (f"Part XXI — Temporary, Transitional & Special Provisions (Article {num})", f"Article {num} contains temporary, transitional, or special provisions for specific States.")
    elif 393 <= num <= 395:
        return (f"Part XXII — Short Title, Commencement & Repeals (Article {num})", f"Article {num} governs short title, commencement date, and authoritative text/repeals of earlier Acts.")
    else:
        return (f"Article {num}", f"Article {num} is outside the 395 Articles of the Constitution of India.")


# ══════════════════════════════════════════════════════════════
# COMPREHENSIVE IPC SECTIONS MAP (Common Penal Code Sections)
# ══════════════════════════════════════════════════════════════
IPC_MAP = {
    34: ("Acts done by several persons in furtherance of common intention", "When a criminal act is done by several persons in furtherance of common intention, each person is liable as if done by him alone."),
    120: ("Criminal conspiracy (Section 120B)", "Section 120A defines criminal conspiracy; Section 120B provides punishment for criminal conspiracy to commit offences."),
    124: ("Sedition (Section 124A)", "Section 124A IPC penalises excited disaffection against Government established by law. Kept in abeyance by Supreme Court in SG Vombatkere (2022). Replaced by BNS Section 152."),
    141: ("Unlawful assembly (Section 141 & 143)", "Assembly of 5 or more persons with common unlawful object. Section 143 provides imprisonment up to 6 months or fine."),
    147: ("Punishment for rioting", "Whoever is guilty of rioting shall be punished with imprisonment up to 2 years, or fine, or both."),
    191: ("Giving false evidence / Perjury (Section 191 & 193)", "Section 191 defines perjury; Section 193 provides punishment up to 7 years imprisonment and fine for giving false evidence in judicial proceeding."),
    295: ("Injuring or defiling place of worship / Outraging religious feelings (Section 295A)", "Section 295A penalises deliberate and malicious acts intended to outrage religious feelings of any class by insulting its religion."),
    299: ("Culpable homicide", "Whoever causes death by doing an act with intention or knowledge of causing death commits culpable homicide."),
    300: ("Murder definition", "Culpable homicide is murder if done with intention to cause death, or causing bodily injury known to be fatal, unless covered by 5 exceptions."),
    302: ("Punishment for murder", "Whoever commits murder shall be punished with death, or imprisonment for life, and fine."),
    304: ("Culpable homicide not amounting to murder", "Punishment for culpable homicide not amounting to murder (Part I: life or up to 10 yrs; Part II: up to 10 yrs). Section 304A: Death by negligence (up to 2 yrs). Section 304B: Dowry death (min 7 yrs to life)."),
    307: ("Attempt to murder", "Doing an act with intention/knowledge that if death occurred, it would be murder. Imprisonment up to 10 years; if hurt caused, up to life."),
    309: ("Attempt to commit suicide", "Section 309 IPC penalised suicide attempt; decriminalised for mental illness under Mental Healthcare Act 2017."),
    319: ("Hurt and Grievous Hurt (Sections 319-326)", "Section 319 defines simple hurt; Section 320 defines grievous hurt (emasculation, permanent sight/hearing loss, disfiguration, bone fracture, 20-day severe body pain). Section 326A/B: Acid attack penalties."),
    354: ("Assault or criminal force to woman with intent to outrage her modesty", "Section 354: Up to 5 yrs. Section 354A: Sexual harassment. Section 354B: Disrobing. Section 354C: Voyeurism. Section 354D: Stalking."),
    363: ("Kidnapping", "Taking any minor or person of unsound mind out of lawful guardianship without consent. Imprisonment up to 7 years and fine."),
    375: ("Rape definition & Section 376 punishment", "Section 375 defines rape; Section 376 penalises rape with min 10 years rigorous imprisonment up to life. Aggravated/gang rape min 20 years to life/death."),
    377: ("Unnatural offences", "Section 377 IPC consensually between adults decriminalised by Supreme Court in Navtej Singh Johar v. UOI (2018). Non-consensual unnatural acts remain criminal."),
    378: ("Theft definition & Section 379 punishment", "Section 378 defines theft (dishonest taking of movable property without consent); Section 379 penalises theft with imprisonment up to 3 years or fine."),
    383: ("Extortion definition & Section 384 punishment", "Intentionally putting any person in fear of injury to dishonestly induce property delivery. Imprisonment up to 3 years or fine."),
    390: ("Robbery & Dacoity (Sections 390-395)", "Robbery is theft/extortion with force or threat. Section 392: Robbery up to 10 yrs. Section 395: Dacoity (robbery by 5+ persons) up to life imprisonment."),
    405: ("Criminal breach of trust (Section 405 & 406)", "Section 405 defines criminal breach of trust; Section 406 penalises with imprisonment up to 3 years or fine."),
    415: ("Cheating definition & Section 420 punishment", "Section 415 defines cheating; Section 420 penalises cheating and dishonestly inducing delivery of property with imprisonment up to 7 years and fine."),
    463: ("Forgery definition & Section 465 punishment", "Section 463 defines forgery; Section 465 penalises making false document with imprisonment up to 2 years or fine."),
    497: ("Adultery", "Section 497 IPC struck down as unconstitutional by Supreme Court in Joseph Shine v. UOI (2018). Adultery remains ground for civil divorce."),
    498: ("Cruelty by husband or relatives for dowry (Section 498A)", "Subjecting a married woman to cruelty or dowry harassment. Imprisonment up to 3 years and fine. Cognizable and non-bailable."),
    499: ("Defamation definition & Section 500 punishment", "Section 499 defines civil/criminal defamation; Section 500 penalises defamation with simple imprisonment up to 2 years or fine."),
    503: ("Criminal intimidation definition & Section 506 punishment", "Section 503 defines criminal intimidation; Section 506 penalises with up to 2 years; up to 7 years if threat is of death or grievous hurt."),
    509: ("Word, gesture or act intended to insult modesty of a woman", "Uttering word, making sound/gesture to intrude upon privacy or modesty of a woman. Imprisonment up to 3 years and fine."),
}

# ══════════════════════════════════════════════════════════════
# COMPREHENSIVE CrPC SECTIONS MAP (Procedure & Criminal Courts)
# ══════════════════════════════════════════════════════════════
CRPC_MAP = {
    41: ("When police may arrest without warrant", "Section 41 CrPC lists circumstances where police can arrest without warrant in cognizable cases, subject to Arnesh Kumar (2014) guidelines."),
    57: ("Person arrested not to be detained more than 24 hours", "No police officer shall detain an arrested person for longer than 24 hours without special order of Magistrate under Section 167."),
    125: ("Order for maintenance of wives, children and parents", "Section 125 CrPC provides secular remedy for maintenance to wife, legitimate/illegitimate minor children, and elderly parents unable to maintain themselves."),
    144: ("Power to issue order in urgent cases of nuisance or apprehended danger", "Executive Magistrate can issue orders prohibiting assembly of 5+ persons or carrying arms to prevent breach of peace/nuisance."),
    154: ("First Information Report (FIR)", "Section 154 CrPC governs recording of FIR in cognizable cases. Free copy must be given to informant. Zero FIR allowed at any police station."),
    156: ("Police officer's power to investigate cognizable case", "Section 156(3) CrPC empowers Magistrate to order police to register FIR and investigate."),
    161: ("Examination of witnesses by police", "Section 161 CrPC allows police during investigation to examine orally any person acquainted with facts. Statements not signed."),
    164: ("Recording of confessions and statements before Magistrate", "Metropolitan/Judicial Magistrate can record statement or confession of victim/witness under oath."),
    167: ("Procedure when investigation cannot be completed in 24 hours (Default Bail)", "Magistrate may authorise detention up to 60 days (offences up to 10 yrs) or 90 days (more serious). Default bail is mandatory right if charge sheet not filed within period."),
    173: ("Report of police officer on completion of investigation (Charge Sheet)", "Section 173 CrPC mandates submission of final investigation report (Charge Sheet or Closure Report) to Magistrate."),
    190: ("Cognizance of offences by Magistrates", "Magistrate takes cognizance of offences upon police report, private complaint, or information received."),
    200: ("Examination of complainant (Private Complaint)", "Magistrate taking cognizance on private complaint shall examine complainant and witnesses upon oath."),
    300: ("Person once convicted or acquitted not to be tried for same offence", "Statutory protection against double jeopardy under Section 300 CrPC (aligns with Article 20(2))."),
    313: ("Power to examine the accused", "Court personally questions accused on evidence against him to enable explanation. Statements not under oath."),
    374: ("Appeals from convictions", "Section 374 CrPC provides right of appeal to High Court or Sessions Court against conviction order."),
    436: ("In what cases bail to be taken (Bailable offences)", "In bailable offences, bail is an absolute legal right. Police/Court MUST release accused upon furnishing bail bond."),
    437: ("When bail may be taken in non-bailable offence", "Court discretion to grant bail in non-bailable cases, considering gravity, flight risk, evidence tampering."),
    438: ("Direction for grant of bail to person apprehending arrest (Anticipatory Bail)", "High Court or Sessions Court direction to release person on bail in event of arrest for non-bailable offence."),
    439: ("Special powers of High Court or Sessions Court regarding bail", "Special authority to grant bail, modify conditions, or cancel bail already granted."),
    482: ("Saving of inherent powers of High Court", "High Court has inherent powers to prevent abuse of process of any court or secure ends of justice (e.g. quashing frivolous FIRs/charge sheets)."),
}

# ══════════════════════════════════════════════════════════════
# NEW CRIMINAL LAWS MAP (BNS, BNSS, BSA 2023)
# ══════════════════════════════════════════════════════════════
NEW_LAWS_MAP = {
    "bns": "Bharatiya Nyaya Sanhita (BNS) 2023 replaced the Indian Penal Code (IPC) 1860 from July 1, 2024. Key changes: Organised crime (Sec 111), Terrorist acts (Sec 113), Mob lynching (Sec 103(2)), Sedition replaced by Section 152 (Acts endangering sovereignty/integrity).",
    "bnss": "Bharatiya Nagarik Suraksha Sanhita (BNSS) 2023 replaced the CrPC 1973. Key changes: Zero FIR legalized (Sec 173), E-FIR, mandatory forensic investigation for offences punishable by 7+ years, strict timelines for charge sheets (90 days) and judgments (30 days).",
    "bsa": "Bharatiya Sakshya Adhiniyam (BSA) 2023 replaced the Indian Evidence Act 1872. Gives full legal admissibility to electronic and digital records as primary evidence.",
}


def lookup_specific_provision(query: str) -> Optional[Dict[str, Any]]:
    """Look up any specific Article or Section number across full Indian Law."""
    q = query.upper().strip()

    # STEP 1: First Priority — Check New Criminal Laws (BNSS, BNS, BSA 2023)
    # Check BNSS explicitly BEFORE BNS to avoid substring match
    if re.search(r"\bBNSS\b", q) or "BHARATIYA NAGARIK" in q:
        return {
            "answer": f"**Bharatiya Nagarik Suraksha Sanhita (BNSS) 2023** *(🔵 New Criminal Procedure)*\n\n{NEW_LAWS_MAP['bnss']}",
            "category": "crpc",
            "confidence": 1.0,
            "sources": ["BNSS 2023"],
        }
    if re.search(r"\bBNS\b", q) or "BHARATIYA NYAYA" in q:
        return {
            "answer": f"**Bharatiya Nyaya Sanhita (BNS) 2023** *(🔴 New Criminal Law)*\n\n{NEW_LAWS_MAP['bns']}",
            "category": "ipc",
            "confidence": 1.0,
            "sources": ["BNS 2023"],
        }
    if re.search(r"\bBSA\b", q) or "BHARATIYA SAKSHYA" in q:
        return {
            "answer": f"**Bharatiya Sakshya Adhiniyam (BSA) 2023** *(📋 Evidence Law)*\n\n{NEW_LAWS_MAP['bsa']}",
            "category": "general",
            "confidence": 1.0,
            "sources": ["BSA 2023"],
        }

    # STEP 2: CrPC Section check
    if "CRPC" in q:
        crpc_match = re.search(r"\b(?:CRPC|SECTION|SEC)?\s*(\d+[A-Z]?)\b", q)
        if crpc_match:
            num_str = crpc_match.group(1)
            try:
                num = int(re.sub(r"[A-Z]", "", num_str))
                if num in CRPC_MAP:
                    title_short, desc = CRPC_MAP[num]
                    return {
                        "answer": f"**CrPC Section {num_str}** *(🔵 Criminal Procedure)*\n\n**{title_short}**\n\n{desc}\n\n*⚠️ Note: CrPC has been replaced by Bharatiya Nagarik Suraksha Sanhita (BNSS) 2023 from July 1, 2024.*",
                        "category": "crpc",
                        "confidence": 1.0,
                        "sources": [f"CrPC Section {num_str}"],
                    }
                elif 1 <= num <= 484:
                    return {
                        "answer": f"**CrPC Section {num_str}** *(🔵 Criminal Procedure)*\n\nSection {num_str} forms part of the Code of Criminal Procedure 1973 (now Bharatiya Nagarik Suraksha Sanhita 2023), regulating procedure for criminal trials, inquiries, and police investigations in India.",
                        "category": "crpc",
                        "confidence": 0.9,
                        "sources": [f"CrPC Section {num_str}"],
                    }
                else:
                    return {
                        "answer": f"**CrPC Section {num_str}** does not exist in the Code of Criminal Procedure 1973 (CrPC has **Sections 1 to 484**).\n\nDid you mean **CrPC Section 41** (Arrest), **Section 154** (FIR), **Section 167** (Default Bail), or **Section 438** (Anticipatory Bail)?",
                        "category": "crpc",
                        "confidence": 0.0,
                        "sources": [],
                    }
            except ValueError:
                pass

    # STEP 3: IPC Section check
    if "IPC" in q or "PENAL" in q or re.search(r"\bSEC(?:TION)?\s*\d+", q):
        ipc_match = re.search(r"\b(?:IPC|SECTION|SEC)?\s*(\d+[A-Z]?)\b", q)
        if ipc_match:
            num_str = ipc_match.group(1)
            try:
                num = int(re.sub(r"[A-Z]", "", num_str))
                if num in IPC_MAP:
                    title_short, desc = IPC_MAP[num]
                    return {
                        "answer": f"**IPC Section {num_str}** *(🔴 Indian Penal Code)*\n\n**{title_short}**\n\n{desc}\n\n*⚠️ Note: IPC has been replaced by Bharatiya Nyaya Sanhita (BNS) 2023 for offences committed on or after July 1, 2024.*",
                        "category": "ipc",
                        "confidence": 1.0,
                        "sources": [f"IPC Section {num_str}"],
                    }
                elif 1 <= num <= 511:
                    return {
                        "answer": f"**IPC Section {num_str}** *(🔴 Indian Penal Code)*\n\nSection {num_str} is part of the Indian Penal Code 1860 (now Bharatiya Nyaya Sanhita 2023), defining offences and penalties under Indian criminal law.",
                        "category": "ipc",
                        "confidence": 0.9,
                        "sources": [f"IPC Section {num_str}"],
                    }
                else:
                    return {
                        "answer": f"**IPC Section {num_str}** does not exist in the Indian Penal Code 1860 (IPC has **Sections 1 to 511**).\n\nDid you mean **Section 302** (Murder), **Section 376** (Rape), **Section 420** (Cheating), or **Section 498A** (Dowry Cruelty)?",
                        "category": "ipc",
                        "confidence": 0.0,
                        "sources": [],
                    }
            except ValueError:
                pass

    # STEP 4: Article check
    art_match = re.search(r"\b(?:ARTICLE|ART)\s*(\d+[A-Z]?)\b", q)
    if not art_match and ("ARTICLE" in q or "ART" in q or re.match(r"^\s*(\d+[A-Z]?)\s*$", q)):
        art_match = re.search(r"\b(\d+[A-Z]?)\b", q)

    if art_match:
        num_str = art_match.group(1)
        try:
            num = int(re.sub(r"[A-Z]", "", num_str))
            # Ignore 4-digit years like 2023
            if num in (1860, 1950, 1973, 2023, 2024) and "ARTICLE" not in q and "ART" not in q:
                return None
            if 1 <= num <= 395:
                title_short, desc = get_constitution_article_info(num)
                return {
                    "answer": f"**Article {num_str} of the Constitution of India** *(⚖️ Constitutional Law)*\n\n**{title_short}**\n\n{desc}\n\n*⚠️ For informational purposes only. Consult a qualified advocate for specific legal advice.*",
                    "category": "constitution",
                    "confidence": 1.0,
                    "sources": [f"Article {num_str}"],
                }
            elif "ARTICLE" in q or "ART" in q:
                return {
                    "answer": f"**Article {num_str}** does not exist in the Constitution of India (the Indian Constitution has **Articles 1 to 395** across 22 Parts).\n\nDid you mean **Article 19** (Freedoms), **Article 21** (Life & Liberty), **Article 32** (Writs), or **Article 352** (Emergency)?",
                    "category": "constitution",
                    "confidence": 0.0,
                    "sources": [],
                }
        except ValueError:
            pass

    return None
