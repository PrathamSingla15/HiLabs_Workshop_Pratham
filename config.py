"""Central configuration for the Clinical NLP Evaluation Pipeline."""

import os
from dotenv import load_dotenv

load_dotenv()

# ── API Configuration ──────────────────────────────────────────────────────────
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_MODEL = "openai/gpt-4o-mini"
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")

# ── Scoring Weights ────────────────────────────────────────────────────────────
OBJECTIVE_WEIGHT = 0.4
SUBJECTIVE_WEIGHT = 0.6

# ── LLM Settings ──────────────────────────────────────────────────────────────
LLM_TEMPERATURE = 0
LLM_SEED = 42
LLM_MAX_TOKENS = 1
LLM_TOP_LOGPROBS = 5
PASS_K = 3
EARLY_STOP_LOGPROB_THRESHOLD = -0.1  # >90% confidence

# ── Concurrency ───────────────────────────────────────────────────────────────
MAX_CONCURRENT_LLM_CALLS = 10
LLM_RETRY_ATTEMPTS = 3
LLM_RETRY_BACKOFF = 2.0

# ── Ambiguity thresholds for LLM routing ──────────────────────────────────────
AMBIGUOUS_LOW = 2.0
AMBIGUOUS_HIGH = 4.5

# ── Output Schema Keys ────────────────────────────────────────────────────────
ENTITY_TYPES = [
    "MEDICINE", "PROBLEM", "PROCEDURE", "TEST", "VITAL_NAME",
    "IMMUNIZATION", "MEDICAL_DEVICE", "MENTAL_STATUS", "SDOH", "SOCIAL_HISTORY",
]
ASSERTION_TYPES = ["POSITIVE", "NEGATIVE", "UNCERTAIN"]
TEMPORALITY_TYPES = ["CURRENT", "CLINICAL_HISTORY", "UPCOMING", "UNCERTAIN"]
SUBJECT_TYPES = ["PATIENT", "FAMILY_MEMBER"]

# ── Expected QA Attributes per Entity Type ────────────────────────────────────
EXPECTED_ATTRIBUTES = {
    "MEDICINE": {
        "critical": ["STRENGTH", "FREQUENCY"],
        "important": ["UNIT", "DOSE", "ROUTE"],
        "optional": ["FORM", "DURATION", "STATUS"],
    },
    "TEST": {
        "critical": ["TEST_VALUE"],
        "important": ["TEST_UNIT"],
        "optional": ["exact_date"],
    },
    "VITAL_NAME": {
        "critical": ["VITAL_NAME_VALUE"],
        "important": ["VITAL_NAME_UNIT"],
        "optional": [],
    },
    "IMMUNIZATION": {
        "critical": [],
        "important": ["exact_date"],
        "optional": ["ROUTE", "DOSE", "STATUS"],
    },
    "PROCEDURE": {
        "critical": [],
        "important": [],
        "optional": ["exact_date", "derived_date", "STATUS"],
    },
    "PROBLEM": {
        "critical": [],
        "important": [],
        "optional": ["exact_date", "derived_date", "STATUS"],
    },
    "MEDICAL_DEVICE": {
        "critical": [],
        "important": [],
        "optional": ["STATUS"],
    },
    "MENTAL_STATUS": {
        "critical": [],
        "important": [],
        "optional": ["VALUE", "STATUS"],
    },
    "SDOH": {
        "critical": [],
        "important": [],
        "optional": ["VALUE", "STATUS"],
    },
    "SOCIAL_HISTORY": {
        "critical": [],
        "important": [],
        "optional": ["VALUE", "STATUS", "FREQUENCY"],
    },
}

# ── Drug INN Suffixes ─────────────────────────────────────────────────────────
DRUG_SUFFIXES = [
    "olol", "pril", "statin", "sartan", "dipine", "prazole",
    "cillin", "floxacin", "cycline", "mycin", "thromycin",
    "azole", "mab", "nib", "tinib", "zumab", "ximab",
    "tide", "glutide", "gliptin", "gliflozin", "formin",
    "parin", "tidine", "setron", "lukast", "afil",
    "semide", "thiazide", "barbital", "triptyline", "oxetine",
    "azepam", "zolam", "codone", "morphone", "profen",
    "caine", "navir", "vudine", "dronate", "lamide",
    "pine", "done", "amine", "vir", "lam",
]

# ── Known Drug Names ──────────────────────────────────────────────────────────
KNOWN_DRUG_NAMES = {
    "aspirin", "insulin", "heparin", "warfarin", "tylenol", "advil", "motrin",
    "albuterol", "calcium", "iron", "zinc", "vitamin", "potassium", "sodium",
    "magnesium", "morphine", "codeine", "fentanyl", "oxycodone", "hydrocodone",
    "prednisone", "dexamethasone", "methylprednisolone", "hydrocortisone",
    "levothyroxine", "synthroid", "eliquis", "xarelto", "plavix", "coumadin",
    "lasix", "norvasc", "zocor", "crestor", "lipitor", "nexium", "prilosec",
    "protonix", "metformin", "januvia", "jardiance", "farxiga", "ozempic",
    "trulicity", "lantus", "humalog", "novolog", "toradol", "dilaudid",
    "percocet", "vicodin", "ativan", "valium", "xanax", "ambien", "seroquel",
    "zyprexa", "risperdal", "abilify", "prozac", "zoloft", "lexapro", "cymbalta",
    "wellbutrin", "remeron", "trazodone", "gabapentin", "lyrica", "neurontin",
    "dilantin", "keppra", "depakote", "tegretol", "topamax", "baclofen",
    "flexeril", "robaxin", "celebrex", "colchicine", "allopurinol",
    "buspirone", "hydroxyzine", "promethazine", "ondansetron", "zofran",
    "reglan", "docusate", "miralax", "senna", "dulcolax", "pepcid",
    "benadryl", "claritin", "zyrtec", "flonase", "symbicort", "spiriva",
    "anoro", "breo", "advair", "proair", "ventolin", "combivent",
    "acetaminophen", "naproxen", "ibuprofen", "tramadol", "methadone",
    "naloxone", "suboxone", "zolpidem", "melatonin", "fish oil",
    "multivitamin", "vitamin d", "vitamin b12", "folic acid", "areds2",
    "prenatal vitamins", "coq10", "biotin", "thiamine", "riboflavin",
    "lisinopril", "amlodipine", "metoprolol", "atenolol", "carvedilol",
    "losartan", "valsartan", "hydrochlorothiazide", "furosemide",
    "spironolactone", "atorvastatin", "simvastatin", "rosuvastatin",
    "omeprazole", "esomeprazole", "pantoprazole", "lansoprazole",
    "amoxicillin", "azithromycin", "ciprofloxacin", "levofloxacin",
    "doxycycline", "clindamycin", "vancomycin", "cephalexin", "ceftriaxone",
    "fluconazole", "acyclovir", "oseltamivir", "tamiflu",
    "lorazepam", "diazepam", "clonazepam", "alprazolam", "midazolam",
    "sertraline", "fluoxetine", "paroxetine", "citalopram", "escitalopram",
    "duloxetine", "venlafaxine", "bupropion", "mirtazapine",
    "quetiapine", "olanzapine", "risperidone", "aripiprazole", "haloperidol",
    "lithium", "valproic acid", "carbamazepine", "phenytoin", "levetiracetam",
    "topiramate", "lamotrigine", "oxcarbazepine", "lacosamide",
    "tamsulosin", "finasteride", "sildenafil", "tadalafil",
    "cyclobenzaprine", "methocarbamol", "tizanidine",
    "diphenhydramine", "cetirizine", "loratadine", "fexofenadine",
    "famotidine", "ranitidine", "sucralfate", "polyethylene glycol",
    "enoxaparin", "apixaban", "rivaroxaban", "dabigatran", "clopidogrel",
    "digoxin", "amiodarone", "diltiazem", "verapamil", "nifedipine",
    "nitroglycerin", "isosorbide", "hydralazine", "clonidine",
    "propranolol", "nadolol", "sotalol", "bisoprolol", "nebivolol",
    "fluticasone", "budesonide", "montelukast", "ipratropium", "tiotropium",
    "pioglitazone", "glimepiride", "glipizide", "glyburide",
    "semaglutide", "liraglutide", "dulaglutide", "empagliflozin",
    "dapagliflozin", "canagliflozin", "sitagliptin", "linagliptin",
    "tacrolimus", "cyclosporine", "mycophenolate", "azathioprine",
    "methotrexate", "hydroxychloroquine", "sulfasalazine",
    "oxygen", "normal saline", "lactated ringers", "d5w", "saline",
    "potassium chloride", "sodium chloride", "sodium bicarbonate",
    "dextrose", "albumin", "fluids", "ivf", "tpn",
}

# ── Disease/Problem Suffixes ──────────────────────────────────────────────────
DISEASE_SUFFIXES = [
    "itis", "osis", "emia", "oma", "pathy", "algia", "dynia",
    "ectasis", "megaly", "penia", "philia", "plegia", "paresis",
    "rrhea", "rrhage", "rrhagia", "sclerosis", "stenosis",
    "trophy", "uria", "cele", "malacia", "ptosis", "iasis",
]

# ── Known Problem/Disease Terms ──────────────────────────────────────────────
KNOWN_PROBLEM_TERMS = {
    "diabetes", "hypertension", "asthma", "copd", "chf", "cad", "dvt", "pe",
    "stroke", "seizure", "cancer", "tumor", "fracture", "infection", "sepsis",
    "pneumonia", "bronchitis", "flu", "covid", "obesity", "depression", "anxiety",
    "dementia", "alzheimer", "parkinson", "epilepsy", "migraine", "gerd", "ulcer",
    "cirrhosis", "hepatitis", "pancreatitis", "colitis", "diverticulitis",
    "appendicitis", "hernia", "gallstones", "kidney stones", "ckd", "esrd", "aki",
    "uti", "cellulitis", "abscess", "wound", "laceration", "contusion", "concussion",
    "pain", "edema", "swelling", "fever", "nausea", "vomiting", "diarrhea",
    "constipation", "bleeding", "clot", "embolism", "thrombosis", "anemia",
    "leukemia", "lymphoma", "melanoma", "carcinoma", "sarcoma",
    "fibrillation", "arrhythmia", "tachycardia", "bradycardia",
    "hypotension", "hypoglycemia", "hyperglycemia", "hyperkalemia", "hyponatremia",
    "hypothyroidism", "hyperthyroidism", "osteoporosis", "osteoarthritis",
    "rheumatoid arthritis", "lupus", "psoriasis", "eczema", "dermatitis",
    "glaucoma", "cataract", "retinopathy", "neuropathy", "nephropathy",
    "cardiomyopathy", "encephalopathy", "myopathy", "myelopathy",
    "dysphagia", "dyspnea", "dysuria", "hematuria", "proteinuria",
    "acute kidney injury", "chronic kidney disease", "heart failure",
    "coronary artery disease", "peripheral vascular disease",
    "deep vein thrombosis", "pulmonary embolism", "atrial fibrillation",
    "congestive heart failure", "chronic obstructive pulmonary disease",
    "obstructive sleep apnea", "sleep apnea", "insomnia",
    "bipolar", "schizophrenia", "ptsd", "adhd", "ocd",
    "malignancy", "neoplasm", "metastasis", "mass", "nodule", "polyp", "cyst",
    "stenosis", "insufficiency", "regurgitation", "prolapse",
    "delirium", "encephalitis", "meningitis", "osteomyelitis",
    "endocarditis", "pericarditis", "myocarditis", "vasculitis",
    "aneurysm", "dissection", "tamponade", "pneumothorax", "pleural effusion",
    "ascites", "ileus", "obstruction", "perforation", "ischemia", "infarction",
    "shock", "respiratory failure", "renal failure", "liver failure",
    "coagulopathy", "thrombocytopenia", "neutropenia", "pancytopenia",
    "rash", "pruritus", "urticaria", "angioedema",
    "syncope", "vertigo", "dizziness", "weakness", "fatigue", "malaise",
    "cachexia", "dehydration", "malnutrition", "hypothermia", "hyperthermia",
    "hammertoe", "bunion", "plantar fasciitis", "gout",
    "spinal stenosis", "disc herniation", "spondylosis", "scoliosis",
}

# ── Procedure Suffixes ────────────────────────────────────────────────────────
PROCEDURE_SUFFIXES = [
    "ectomy", "plasty", "scopy", "otomy", "ostomy", "centesis",
    "tripsy", "pexy", "rrhaphy", "desis", "gram",
]

# ── Known Procedure Terms ────────────────────────────────────────────────────
KNOWN_PROCEDURE_TERMS = {
    "surgery", "operation", "biopsy", "transplant", "catheterization",
    "intubation", "extubation", "dialysis", "transfusion", "infusion",
    "injection", "aspiration", "drainage", "debridement", "reduction",
    "fixation", "fusion", "graft", "implant", "replacement", "repair",
    "removal", "excision", "resection", "ablation", "embolization",
    "stenting", "bypass", "shunt", "physical exam", "examination",
    "assessment", "evaluation", "consultation", "counseling",
    "screening", "vaccination", "immunization",
}

# ── Known Test Terms ──────────────────────────────────────────────────────────
KNOWN_TEST_TERMS = {
    "glucose", "hemoglobin", "hgb", "a1c", "hba1c", "hgba1c",
    "creatinine", "bun", "egfr", "sodium", "potassium", "chloride",
    "calcium", "magnesium", "phosphorus", "albumin", "bilirubin",
    "ast", "alt", "alp", "ggt", "ldh", "ck", "troponin", "bnp",
    "inr", "ptt", "pt", "aptt", "fibrinogen", "d-dimer",
    "wbc", "rbc", "platelets", "hematocrit", "mcv", "mch", "mchc",
    "rdw", "mpv", "esr", "crp", "procalcitonin", "lactate", "ammonia",
    "lipase", "amylase", "tsh", "t3", "t4", "free t4", "psa",
    "ferritin", "iron studies", "tibc", "transferrin", "folate", "b12",
    "urinalysis", "ua", "culture", "sensitivity", "abg", "vbg",
    "cholesterol", "ldl", "hdl", "triglycerides", "lipid panel",
    "cbc", "cmp", "bmp", "hepatic function panel", "coagulation studies",
    "sed rate", "uric acid", "cea", "afp", "ca-125",
    "blood gas", "arterial blood gas", "prealbumin", "haptoglobin",
    "reticulocyte", "coombs", "complement", "ana", "anti-ccp",
    "rheumatoid factor", "anca", "immunoglobulin",
}

# ── Known Vital Terms ─────────────────────────────────────────────────────────
KNOWN_VITAL_TERMS = {
    "blood pressure", "bp", "systolic", "diastolic",
    "heart rate", "hr", "pulse", "pulse rate",
    "temperature", "temp",
    "respiratory rate", "rr", "resp rate",
    "oxygen saturation", "spo2", "o2 sat", "o2 saturation",
    "weight", "height", "bmi", "body mass index",
    "pain", "pain scale", "pain score", "pain level",
    "map", "mean arterial pressure",
}

# ── Known Immunization Terms ──────────────────────────────────────────────────
KNOWN_IMMUNIZATION_TERMS = {
    "vaccine", "vaccination", "immunization",
    "flu vaccine", "influenza vaccine", "flu shot",
    "covid vaccine", "covid-19 vaccine", "coronavirus vaccine",
    "pneumococcal vaccine", "pneumovax", "prevnar",
    "tetanus", "tdap", "td vaccine",
    "hepatitis a vaccine", "hepatitis b vaccine", "hep b",
    "mmr", "measles", "mumps", "rubella",
    "varicella", "chickenpox vaccine",
    "shingles vaccine", "shingrix", "zostavax",
    "hpv vaccine", "gardasil",
    "meningococcal vaccine",
    "polio vaccine", "ipv",
}

# ── UI Noise Detection ────────────────────────────────────────────────────────
UI_NOISE_ENTITY_PATTERNS = [
    "quick search", "fax inbox", "info hub", "ask eva",
    "external viewer", "web mode", "patient documents",
    "cover page", "click here", "add description",
    "electronically signed", "admit notice",
    "encounter_date", "patient_name", "provider_name",
    "facility_name", "hospital_name",
    "mrn", "acct", "account_number", "chart_number",
    "guarantor", "payor", "insurance",
    "readmission risk", "risk score", "risk model",
    "internally validated", "patient level characteristics",
    "if content is not visible",
]

UI_NOISE_HEADING_PATTERNS = [
    "cover page", "patient documents", "web mode", "info hub",
    "electronically signed", "active insurance",
    "basic information", "fax", "rcvd:",
]

ADMIN_ENTITY_PATTERNS = [
    "encounter 1", "encounter 2", "encounter 3", "encounter 4",
    "hospital account", "guarantor account", "length of stay",
    "admission date", "admission status", "attending physician",
    "patient class", "discharge disposition",
    "f/o payor", "cal optima", "medicaid",
]

# ── NegEx Pre-Negation Triggers ───────────────────────────────────────────────
NEGEX_PRE_TRIGGERS = [
    "no evidence of", "no signs of", "no symptoms of",
    "no sign of", "no findings of", "no finding of",
    "no complaints of", "no history of", "no h/o",
    "no hx of", "no known", "no acute",
    "no significant", "no new", "no further",
    "no prior", "no previous", "no recent", "no current",
    "not demonstrate", "did not demonstrate",
    "does not have", "did not have", "do not have",
    "has no", "had no", "have no", "with no",
    "shows no", "showed no", "show no",
    "reveal no", "revealed no", "reveals no",
    "negative for", "neg for",
    "fails to reveal", "failed to reveal",
    "free of", "free from", "clear of",
    "rules out", "ruled out", "rule out", "r/o",
    "without", "without any", "without evidence",
    "absence of", "absent",
    "denies", "denied", "deny", "denying",
    "declined", "declines",
    "never", "never had", "never developed",
    "non-contributory", "noncontributory",
    "unremarkable",
    "no ", "not ", "none",
]

# ── NegEx Post-Negation Triggers ──────────────────────────────────────────────
NEGEX_POST_TRIGGERS = [
    "unlikely", "was ruled out", "have been ruled out",
    "were ruled out", "is ruled out", "has been ruled out",
    "was negative", "are negative", "is negative",
    "was not found", "not found", "not seen",
    "not identified", "not demonstrated", "not present",
    "not appreciated", "not detected", "not noted",
    "was absent", "is absent", "was denied", "is denied",
    "have resolved", "has resolved", "resolved",
    "has cleared", "is unremarkable",
]

# ── NegEx Termination Terms ───────────────────────────────────────────────────
NEGEX_TERMINATION = [
    "but", "however", "although", "though", "except",
    "apart from", "aside from", "still", "yet",
    "nevertheless", "secondary to", "due to",
    "because of", "cause of", "reason for",
]

# ── Pseudo-Negation (should NOT trigger negation) ─────────────────────────────
NEGEX_PSEUDO = [
    "no change", "no increase", "no decrease",
    "not only", "not necessarily", "not certain",
    "gram negative", "no need", "no longer",
    "without difficulty", "without complication",
    "without incident", "without delay",
]

# ── Uncertainty Triggers ──────────────────────────────────────────────────────
UNCERTAINTY_TRIGGERS = [
    "possible", "possibly", "probable", "probably",
    "suspect", "suspected", "suspicion of", "suspicious",
    "may have", "may be", "might be", "might have",
    "could be", "could have",
    "consider", "considering", "considered",
    "likely", "most likely", "appears to be",
    "question of", "questionable",
    "rule out", "r/o", "to rule out",
    "cannot exclude", "cannot rule out",
    "differential includes", "differential diagnosis",
    "concern for", "concerning for",
    "suggestive of", "consistent with",
    "equivocal", "indeterminate", "uncertain", "unclear",
    "presumably", "presumed", "presumptive",
    "borderline", "pending",
]

# ── Temporality Heading Mappings ──────────────────────────────────────────────
HISTORY_HEADINGS = [
    "past medical history", "pmh", "pmhx", "medical history",
    "surgical history", "past surgical history",
    "clinical history", "history", "prior",
    "previous", "resolved problems", "past problem",
    "historical", "inactive problems",
]

CURRENT_HEADINGS = [
    "active problems", "current medications", "medications",
    "active hospital problems", "hospital problem list",
    "assessment", "assessment/plan", "assessment and plan", "a/p",
    "impression", "diagnosis", "discharge diagnosis", "discharge diagnoses",
    "admission diagnosis", "hospital course",
    "current outpatient medications", "medication list",
    "discharge medication", "physical exam", "physical examination",
    "vital signs", "vitals", "examination", "exam",
    "hpi", "history of present illness", "present illness",
    "chief complaint", "reason for visit", "reason for appointment",
    "review of systems", "ros",
    "allergies", "allergy",
    "lab", "labs", "laboratory", "results",
]

UPCOMING_HEADINGS = [
    "follow up", "follow-up", "followup",
    "future appointments", "upcoming", "scheduled",
    "discharge plan", "discharge instructions",
    "discharge documentation", "discharge",
    "orders", "pending orders",
    "plan", "plan of care", "recommendations",
    "care timeline",
]

# ── Temporality Text Triggers ─────────────────────────────────────────────────
HISTORY_TEXT_TRIGGERS = [
    "history of", "h/o", "hx of",
    "previously", "prior", "former", "formerly",
    "past", "in the past",
    "years ago", "months ago", "weeks ago", "days ago",
    "childhood", "since childhood",
    "diagnosed in", "was diagnosed",
    "remote history", "distant history",
    "long-standing", "longstanding",
    "status post", "s/p", "post-",
    "resolved", "has resolved",
    "completed", "had been", "had a",
    "at age", "in 19", "in 20",
]

CURRENT_TEXT_TRIGGERS = [
    "currently", "current", "presently", "present",
    "active", "actively", "ongoing", "continues", "continuing",
    "is on", "is taking", "takes", "taking",
    "now", "at this time", "at present",
    "today", "this visit", "on admission",
    "recent", "recently", "new onset", "new",
    "acute", "acutely",
    "worsening", "improving", "stable",
    "maintained", "maintaining",
]

UPCOMING_TEXT_TRIGGERS = [
    "scheduled", "scheduled for", "to be scheduled",
    "planned", "planning", "plan for", "plan to",
    "upcoming", "will", "will be",
    "to undergo", "to have", "to receive",
    "follow up", "follow-up", "f/u",
    "pending", "await", "awaiting",
    "referral to", "referred to", "refer to",
    "recommend", "recommended", "recommending",
    "consider", "should", "needs to",
    "next visit", "next appointment",
    "return to clinic", "rtc",
]

# ── Family Member Triggers ────────────────────────────────────────────────────
FAMILY_HEADINGS_LIST = [
    "family history", "fhx", "family hx",
    "family medical history", "fh:",
]

FAMILY_TRIGGERS = [
    "mother", "father", "brother", "sister",
    "daughter", "son", "grandmother", "grandfather",
    "aunt", "uncle", "cousin", "mom", "dad",
    "maternal", "paternal", "sibling", "parent", "parents",
    "grandparent", "spouse", "husband", "wife",
    "family member", "family members",
    "family history of", "fh of", "fhx of",
    "runs in the family", "familial",
    "half-brother", "half-sister",
    "stepmother", "stepfather",
    "twin", "step-mother", "step-father",
    "mother's side", "father's side",
    "deceased",
]

# Social history exclusions (these mention family but are about the patient)
SOCIAL_CONTEXT_EXCLUSIONS = [
    "lives with", "married to", "cared for by",
    "accompanied by", "brought in by",
    "emergency contact", "next of kin",
    "supported by", "caregiver",
]
