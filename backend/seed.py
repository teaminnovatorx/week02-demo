"""Seed data — makes the dashboard come alive with rich, realistic AMR surveillance data."""

import json
import random
from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from .database import SessionLocal
from .models import Case, Alert, User, ResistanceData

# ── Geography: 15 districts across 4 regions ──
REGIONS = {
    "West Africa": ["Lagos", "Accra", "Kumasi", "Abuja", "Dakar"],
    "East Africa": ["Nairobi", "Dar es Salaam", "Kampala", "Addis Ababa", "Mombasa"],
    "Southern Africa": ["Lusaka", "Harare", "Lilongwe", "Johannesburg"],
    "Central Africa": ["Kinshasa"],
}
DISTRICTS = [d for region in REGIONS.values() for d in region]

# ── Drugs ──
DRUGS = [
    "Amoxicillin", "Ciprofloxacin", "Gentamicin", "Ceftriaxone",
    "Azithromycin", "Doxycycline", "Penicillin", "Erythromycin",
    "Clindamycin", "Vancomycin", "Meropenem", "Levofloxacin",
]

# ── Pathogens ──
PATHOGENS = [
    "E. coli", "K. pneumoniae", "S. aureus", "P. aeruginosa",
    "S. pneumoniae", "H. influenzae", "N. gonorrhoeae", "S. typhi",
    "Group A Streptococcus", "Proteus mirabilis",
]

# ── Realistic complaints ──
COMPLAINTS = [
    "Fever with chills for 5 days, no response to amoxicillin",
    "Productive cough with yellow sputum, chest pain on deep breathing",
    "Burning urination, frequency, suprapubic pain for 3 days",
    "Infected surgical wound with purulent discharge, erythema spreading",
    "Persistent watery diarrhea with dehydration signs, 4 days",
    "Severe headache, neck stiffness, photophobia, fever 39.5°C",
    "Lower abdominal pain, vaginal discharge, dyspareunia",
    "Joint pain with swelling, heat, limited range of motion — right knee",
    "Non-healing ulcer on foot, surrounding cellulitis, diabetic patient",
    "High fever with rash, myalgia, severe fatigue — 3 days",
    "Dysuria with cloudy urine, foul odor, previous UTI history",
    "Chest congestion, wheezing, green sputum, SOB on exertion",
    "Purulent conjunctivitis, eye discharge, crusting on eyelids",
    "Ear discharge with pain, hearing reduced, fever since 1 week",
    "Skin abscess with surrounding cellulitis, axillary lymphadenopathy",
    "Meningeal signs, altered consciousness, petechial rash on trunk",
    "Bloody diarrhea with mucus, tenesmus, abdominal cramps",
    "Fever with rigors, jaundice, dark urine — possible malaria",
    "Cough with hemoptysis, night sweats, weight loss over 2 weeks",
    "Septic arthritis right hip, fever, inability to bear weight",
]

# ── CHW names ──
CHWS = [
    "Grace Okafor", "James Mwangi", "Fatima Bello", "Samuel Ochieng",
    "Aisha Mohammed", "Daniel Akinyemi", "Beatrice Nyambura", "Paul Nkosi",
    "Esther Mensah", "Patrick Mugabe", "Rose Kamau", "Emmanuel Adebayo",
    "Dr. Chinwe Eze", "Sr. Margaret Wanjiku", "John Komba", "Halima Yusuf",
    "Michael Omondi", "Grace Akello", "Thomas Chirwa", "Amina Diallo",
]

# ── Facilities ──
FACILITIES = [
    "General Hospital", "University Teaching Hospital", "District Health Center",
    "Rural Health Post", "Maternal & Child Health Clinic", "Mission Hospital",
    "Military Hospital", "Private Clinic", "Community Health Center", "Regional Referral Hospital",
]

# ── Realistic AMR resistance patterns ──
# For each drug-district pair, generate a realistic baseline resistance
# Higher for older/more used antibiotics, varies by district
DRUG_BASELINE_RESISTANCE = {
    "Amoxicillin": (40, 75), "Penicillin": (35, 70), "Erythromycin": (25, 60),
    "Ciprofloxacin": (15, 55), "Gentamicin": (10, 40), "Doxycycline": (10, 35),
    "Azithromycin": (8, 30), "Ceftriaxone": (5, 25), "Clindamycin": (8, 28),
    "Levofloxacin": (5, 20), "Vancomycin": (0, 8), "Meropenem": (0, 15),
}

# ── Outbreak clusters ──
OUTBREAK_CLUSTERS = [
    {"district": "Lagos", "pathogen": "E. coli", "drug": "Ciprofloxacin",
     "case_count": 12, "pct": 67, "title": "Ciprofloxacin-Resistant E. coli Outbreak",
     "desc": "Lagos Island: 67% of E. coli isolates resistant to ciprofloxacin. Cluster linked to contaminated water source."},
    {"district": "Nairobi", "pathogen": "K. pneumoniae", "drug": "Ceftriaxone",
     "case_count": 8, "pct": 52, "title": "ESBL-Producing K. pneumoniae Cluster",
     "desc": "Kenyatta National Hospital: 5 MDR K. pneumoniae cases in ICU. Resistance to 3rd-gen cephalosporins confirmed."},
    {"district": "Kampala", "pathogen": "N. gonorrhoeae", "drug": "Azithromycin",
     "case_count": 15, "pct": 44, "title": "Azithromycin-Resistant Gonorrhea Surge",
     "desc": "Mulago region: 44% of N. gonorrhoeae isolates resistant. STI surveillance clinic reporting treatment failures."},
    {"district": "Kinshasa", "pathogen": "K. pneumoniae", "drug": "Meropenem",
     "case_count": 6, "pct": 72, "title": "Carbapenem Resistance Emerging",
     "desc": "Cliniques Universitaires: K. pneumoniae resistant to meropenem. Last-resort antibiotics compromised."},
    {"district": "Accra", "pathogen": "S. aureus", "drug": "Penicillin",
     "case_count": 20, "pct": 78, "title": "MRSA-like Penicillin Resistance in Accra",
     "desc": "Korle Bu: 78% S. aureus resistant to penicillin. Wound infection cluster in surgical ward."},
    {"district": "Johannesburg", "pathogen": "P. aeruginosa", "drug": "Gentamicin",
     "case_count": 9, "pct": 48, "title": "MDR Pseudomonas in ICU",
     "desc": "Chris Hani Baragwanath ICU: Multi-drug resistant P. aeruginosa. Limited treatment options remain."},
    {"district": "Mombasa", "pathogen": "E. coli", "drug": "Ceftriaxone",
     "case_count": 11, "pct": 41, "title": "ESBL E. coli in Coastal Kenya",
     "desc": "Coastal General: ESBL-producing E. coli in pediatric UTI cases. Linked to poultry antibiotic use."},
    {"district": "Addis Ababa", "pathogen": "S. typhi", "drug": "Ciprofloxacin",
     "case_count": 14, "pct": 38, "title": "Ciprofloxacin-Resistant Typhoid",
     "desc": "Black Lion Hospital: Ciprofloxacin resistance in S. typhi rising. Azithromycin alternative showing efficacy."},
    {"district": "Lilongwe", "pathogen": "S. pneumoniae", "drug": "Penicillin",
     "case_count": 18, "pct": 35, "title": "Penicillin-Resistant Pneumococcal Meningitis",
     "desc": "Kamuzu Central: Penicillin MICs rising in S. pneumoniae meningitis. Switch to ceftriaxone protocol."},
    {"district": "Abuja", "pathogen": "S. aureus", "drug": "Clindamycin",
     "case_count": 7, "pct": 33, "title": "Clindamycin Resistance in SSTIs",
     "desc": "National Hospital: 33% S. aureus from skin infections resistant to clindamycin. Inducible resistance mechanism."},
]


def _random_age(rng: random.Random) -> int:
    """Generate a realistic age for infectious disease cases."""
    # Bimodal: young children and adults 20-40 most common
    p = rng.random()
    if p < 0.18:
        return rng.randint(0, 5)      # Infants & young children
    elif p < 0.30:
        return rng.randint(6, 17)     # Children & adolescents
    elif p < 0.55:
        return rng.randint(18, 35)    # Young adults
    elif p < 0.75:
        return rng.randint(36, 55)    # Middle-aged
    elif p < 0.90:
        return rng.randint(56, 70)    # Older adults
    else:
        return rng.randint(71, 90)    # Elderly


def seed():
    """Populate DB with rich demo data if empty."""
    db = SessionLocal()
    try:
        existing = db.execute(select(Case).limit(1)).scalar_one_or_none()
        if existing:
            return

        rng = random.Random(42)
        now = datetime.now(timezone.utc)

        # ── Step 1: Generate 250 Cases ──
        severity_pool = ["mild", "mild", "mild", "moderate", "moderate",
                         "moderate", "moderate", "severe", "severe", "critical"]
        status_pool = ["verified", "verified", "verified", "verified",
                       "pending_review", "pending_review", "flagged"]
        source_pool = ["telegram", "telegram", "telegram", "whatsapp",
                       "whatsapp", "ussd", "ussd", "manual", "sms", "sms"]
        sex_pool = ["male", "female", "female", "male", "male", "unknown"]

        for i in range(250):
            district = DISTRICTS[i % len(DISTRICTS)]
            source = source_pool[i % len(source_pool)]
            age = _random_age(rng)
            sex = sex_pool[i % len(sex_pool)]
            severity = severity_pool[i % len(severity_pool)]
            status = status_pool[i % len(status_pool)]
            pathogen = PATHOGENS[i % len(PATHOGENS)]
            complaint = COMPLAINTS[i % len(COMPLAINTS)]
            created = now - timedelta(
                days=rng.randint(0, 28),
                hours=rng.randint(0, 23),
                minutes=rng.randint(0, 59),
            )
            is_resistant = rng.random() < 0.35

            # Pick 1-3 drugs for this case
            num_drugs = rng.randint(1, 3)
            drugs = rng.sample(DRUGS, min(num_drugs, len(DRUGS)))

            specimen_options = ["Blood", "Urine", "Sputum", "Stool",
                                "Wound Swab", "CSF", "Vaginal Swab", "Urethral Swab",
                                "Pus", "Sputum", "Blood", "Urine"]
            specimen = specimen_options[i % len(specimen_options)]

            symptom_sets = [
                ["fever", "chills", "malaise"],
                ["fever", "cough", "dyspnea"],
                ["fever", "cough", "sputum"],
                ["dysuria", "frequency", "urgency"],
                ["pain", "swelling", "redness"],
                ["diarrhea", "vomiting", "dehydration"],
                ["headache", "photophobia", "neck_stiffness"],
                ["myalgia", "fatigue", "arthralgia"],
                ["wound_discharge", "erythema", "warmth"],
                ["pain", "fever", "limited_motion"],
                ["dysuria", "abdominal_pain", "fever"],
                ["rash", "fever", "malaise"],
                ["ear_pain", "discharge", "hearing_loss"],
                ["ocular_discharge", "redness", "itching"],
            ]
            symptoms = symptom_sets[i % len(symptom_sets)]

            duration_days = rng.randint(1, 21)
            duration = f"{duration_days} day{'s' if duration_days != 1 else ''}"

            db.add(Case(
                source=source,
                language=rng.choice(["en", "en", "en", "sw", "fr", "ha", "yo"]),
                patient_age_years=age,
                patient_sex=sex,
                complaint=complaint,
                symptoms=",".join(symptoms),
                duration=duration,
                medications=",".join(drugs),
                specimen=specimen,
                pathogen=pathogen,
                resistance_pattern="MDR" if is_resistant and rng.random() < 0.3 else ("resistant" if is_resistant else "susceptible"),
                drugs_prescribed=json.dumps(drugs),
                severity=severity,
                status=status,
                district=district,
                facility=f"{district} {FACILITIES[i % len(FACILITIES)]}",
                reported_by=CHWS[i % len(CHWS)],
                resistance_flag=is_resistant,
                created_at=created,
                updated_at=created + timedelta(hours=rng.randint(1, 48)),
            ))

        # ── Step 2: Generate 15+ Alerts ──
        # Outbreak alerts (from clusters)
        for cluster in OUTBREAK_CLUSTERS:
            alert_severity = (
                "critical" if cluster["pct"] > 60 else
                "high" if cluster["pct"] > 35 else
                "medium"
            )
            db.add(Alert(
                severity=alert_severity,
                title=cluster["title"],
                message=cluster["desc"],
                district=cluster["district"],
                drug=cluster["drug"],
                resistance_pct=cluster["pct"],
                status="active",
                created_at=now - timedelta(
                    hours=rng.randint(2, 168),
                    minutes=rng.randint(0, 59),
                ),
            ))

        # Trend alerts
        trend_alerts = [
            ("medium", "Gentamicin Trending Up", "Dar es Salaam ICU: gentamicin resistance trending from 18% to 28% over 3 months. Review empiric protocols.",
             "Dar es Salaam", "Gentamicin", 28.0),
            ("high", "Azithromycin STI Failure", "Kampala STI clinic: 44% azithromycin resistance in N. gonorrhoeae. WHO recommends switching to ceftriaxone + doxycycline.",
             "Kampala", "Azithromycin", 44.0),
            ("medium", "Penicillin Above Threshold", "Accra: penicillin resistance at 35% — exceeds WHO 30% action threshold. Review prescribing guidelines.",
             "Accra", "Penicillin", 35.0),
            ("medium", "Ampicillin Resistance Widespread", "Lusaka: 62% E. coli resistant to ampicillin. Nearly all UTIs now require alternative therapy.",
             "Lusaka", "Amoxicillin", 62.0),
            ("low", "Surveillance Coverage Gap", "Addis Ababa: less than 10 cases this month. Active CHW re-engagement campaign needed.",
             "Addis Ababa", None, 0.0),
            ("high", "Vancomycin MIC Creep", "Johannesburg: vancomycin MICs in S. aureus trending upward. Daptomycin reserve being deployed.",
             "Johannesburg", "Vancomycin", 4.0),
            ("medium", "Post-AMR Campaign Dip", "Kumasi: case reporting dropped 40% after CHW incentive campaign ended. Restart engagement.",
             "Kumasi", None, 0.0),
            ("low", "Doxycycline Resistance Detected", "Mombasa: first doxycycline-resistant S. aureus isolate. Monitor closely.",
             "Mombasa", "Doxycycline", 8.0),
            ("critical", "Neonatal Sepsis Outbreak", "Harare: 6 neonatal sepsis cases in NICU. K. pneumoniae resistant to ampicillin + gentamicin.",
             "Harare", "Gentamicin", 58.0),
            ("medium", "MDR-TB Suspected Cluster", "Lilongwe: 3 patients with TB not responding to first-line therapy. GeneXpert testing underway.",
             "Lilongwe", "Rifampicin", 25.0),
            ("high", "Surgical Site Infections Spike", "Dakar: SSI rate tripled in past week. MRSA suspected. Wound surveillance intensified.",
             "Dakar", "Clindamycin", 38.0),
            ("low", "Lab Supply Chain Alert", "Lusaka: AST media stock running low. Impact on resistance surveillance for next 2 weeks.",
             "Lusaka", None, 0.0),
        ]
        for sev, title, msg, dist, drug, pct in trend_alerts:
            db.add(Alert(
                severity=sev, title=title, message=msg,
                district=dist, drug=drug, resistance_pct=pct,
                status="active",
                created_at=now - timedelta(hours=rng.randint(1, 72)),
            ))

        # ── Step 3: Admin Users ──
        admin_users = [
            ("admin@udara.health", "Dr. Amina Diallo", "admin", "Lagos"),
            ("ops@udara.health", "Samuel Ochieng", "operator", "Nairobi"),
            ("viewer@udara.health", "Dr. Grace Mensah", "viewer", "Accra"),
        ]
        for email, name, role, district in admin_users:
            db.add(User(
                email=email, name=name,
                password_hash="demo",
                role=role, district=district,
            ))

        # ── Step 4: Comprehensive Resistance Data ──
        for drug in DRUGS:
            baseline_min, baseline_max = DRUG_BASELINE_RESISTANCE.get(drug, (10, 50))
            for district in DISTRICTS:
                # Add realistic variation by district
                district_factor = DISTRICTS.index(district) / len(DISTRICTS)  # 0-1
                rng_variation = rng.uniform(-10, 12)
                pct = max(0, min(100, round(
                    baseline_min + (baseline_max - baseline_min) * district_factor + rng_variation, 1
                )))

                # Check if this drug-district is part of an outbreak cluster
                for cluster in OUTBREAK_CLUSTERS:
                    if cluster["district"] == district and cluster["drug"] == drug:
                        pct = max(pct, cluster["pct"] + rng.uniform(-3, 3))
                        break

                pct = round(max(0, min(100, pct)), 1)
                category = "resistant" if pct > 50 else "intermediate" if pct > 25 else "susceptible"
                alts = [d for d in DRUGS if d != drug]
                rng.shuffle(alts)
                sample_size = rng.randint(20, 800)

                db.add(ResistanceData(
                    drug=drug, district=district,
                    resistance_pct=pct, category=category,
                    confidence=round(rng.uniform(0.65, 0.99), 2),
                    sample_size=sample_size,
                    alternatives=json.dumps(alts[:4]),
                    year=2026,
                    month=rng.randint(1, 6),
                ))

        db.commit()
        print(f"✅ Week 02 demo database seeded!")
        print(f"   • {len(DISTRICTS)} districts across {len(REGIONS)} regions")
        print(f"   • {len(OUTBREAK_CLUSTERS)} outbreak clusters tracked")
        print(f"   • {len(DRUGS)} antibiotics under surveillance")
        print(f"   • {len(PATHOGENS)} pathogens monitored")
    finally:
        db.close()
