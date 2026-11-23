import os
import sqlite3

DB_PATH = os.path.join("data", "herbal_monographs.db")

MONOGRAPHS = [
    {
        "class_key": "01_Vitex_negundo",
        "common_name": "Lagundi (Five-Leaved Chaste Tree)",
        "local_names": "Lagundi (Tagalog/Bisaya), Dangla (Ilokano), Dabtan (Ifugao)",
        "scientific_name": "Vitex negundo L.",
        "family": "Lamiaceae",
        "safety_tier": "SAFE_DOH_APPROVED",
        "safety_banner": "DOH / PITAHC Endorsed Herbal Medicine (RA 8423)",
        "botanical_markers": (
            "Palmately compound leaves with 5 (occasionally 3) lance-shaped leaflets radiating from a single petiole; "
            "upper surface dull green, underside distinctly pale grayish-white and finely velvety; aromatic camphor-like scent when crushed."
        ),
        "traditional_uses": (
            "Clinically validated by the Philippine Department of Health (DOH) for mild-to-moderate cough, "
            "colds, fever, and mild bronchospasm/asthma relief."
        ),
        "preparation": (
            "Decoction: Boil 4 tablespoons (approx. 40 g) of chopped fresh leaves (or 2 tbsp dried) in 2 glasses of water "
            "for 15 minutes in an uncovered pot. Cool, strain, and divide into 3 doses taken after meals."
        ),
        "contraindications": (
            "Avoid in pregnant or lactating women unless supervised by a physician. Seek immediate medical care if cough "
            "persists beyond 7 days, is accompanied by high fever, or causes shortness of breath."
        ),
        "reference": "DOH / PITAHC Philippine National Formulary & TAMA (RA 8423) Monograph",
    },
    {
        "class_key": "02_Momordica_charantia",
        "common_name": "Ampalaya (Bitter Melon / Bitter Gourd)",
        "local_names": "Ampalaya (Tagalog), Paliya (Bisaya/Cebuano), Paria (Ilokano)",
        "scientific_name": "Momordica charantia L.",
        "family": "Cucurbitaceae",
        "safety_tier": "SAFE_DOH_APPROVED",
        "safety_banner": "DOH / PITAHC Endorsed Herbal Medicine (RA 8423)",
        "botanical_markers": (
            "Alternate, thin, deeply 5-to-7-lobed palmate vine leaves with sinuate-toothed margins and slender unbranched tendrils; "
            "leaves are soft, bright-to-medium green, and emit a characteristic bitter herbaceous odor when bruised."
        ),
        "traditional_uses": (
            "Endorsed by DOH / PITAHC as a supportive adjunct for mild non-insulin-dependent (Type 2) diabetes mellitus "
            "management and postprandial blood glucose control."
        ),
        "preparation": (
            "Decoction or Steamed Greens: Wash young leaves thoroughly; steam as a culinary vegetable (approx. 1/2 cup twice daily) "
            "or boil 6 tablespoons of chopped fresh leaves in 2 glasses of water for 15 minutes uncovered, taking 1/3 glass 3 times daily after meals."
        ),
        "contraindications": (
            "Monitor blood glucose closely if taking prescription hypoglycemic medications (e.g., metformin, sulfonylureas, insulin) "
            "to prevent additive hypoglycemia. Contraindicated in pregnancy and individuals with G6PD deficiency."
        ),
        "reference": "DOH / PITAHC Essential Drug List & Philippine Herbal Pharmacopoeia",
    },
    {
        "class_key": "03_Carmona_retusa",
        "common_name": "Tsaang Gubat (Philippine Tea Tree / Scorpionbush)",
        "local_names": "Tsaang Gubat (Tagalog), Alangitngit (Bisaya), Mara-mara (Bikol)",
        "scientific_name": "Carmona retusa (Vahl) Masam. (syn. Ehretia microphylla)",
        "family": "Boraginaceae",
        "safety_tier": "SAFE_DOH_APPROVED",
        "safety_banner": "DOH / PITAHC Endorsed Herbal Medicine (RA 8423)",
        "botanical_markers": (
            "Small, clustered, obovate-to-spatulate leathery leaves (1.5–4 cm long) with a glossy dark-green upper surface, "
            "rough short-bristled texture, and 3–5 coarse teeth near the blunt leaf apex."
        ),
        "traditional_uses": (
            "DOH-approved antispasmodic for acute mild abdominal colic, stomach discomfort, and mild non-infectious diarrhea; "
            "also used as a fluoride-rich herbal mouth rinse."
        ),
        "preparation": (
            "Infusion / Decoction: Boil 2 tablespoons of chopped fresh leaves (or 1 tbsp dried) in 2 glasses of water for 15 minutes "
            "uncovered. Cool, strain, and drink 1/2 glass every 4 hours as needed for mild gastrointestinal spasms."
        ),
        "contraindications": (
            "Not a substitute for Oral Rehydration Salts (ORS) in acute diarrhea. Seek urgent medical care if bloody stools, "
            "severe abdominal pain, or signs of dehydration occur."
        ),
        "reference": "DOH / PITAHC Philippine Herbal Medicine Guidelines",
    },
    {
        "class_key": "04_Senna_alata",
        "common_name": "Akapulko (Ringworm Bush / Candle Bush)",
        "local_names": "Akapulko (Tagalog), Sunting / Palo-china (Bisaya), Andadasi (Ilokano)",
        "scientific_name": "Senna alata (L.) Roxb. (syn. Cassia alata)",
        "family": "Fabaceae",
        "safety_tier": "SAFE_DOH_APPROVED",
        "safety_banner": "DOH / PITAHC Endorsed Topical Antifungal (RA 8423)",
        "botanical_markers": (
            "Large pinnately compound leaves bearing 8–20 pairs of broad, oblong-elliptical leaflets with rounded tips, "
            "asymmetric bases, and a prominent yellowish-orange midrib; leaflets fold together at dusk."
        ),
        "traditional_uses": (
            "Clinically validated by DOH / PITAHC as a topical antifungal treatment for tinea infections including ringworm (buni), "
            "athlete's foot (alipunga), and tinea versicolor (an-an)."
        ),
        "preparation": (
            "Topical Poultice / Sap: Wash fresh mature leaflets thoroughly, pound into a smooth paste to express the green juice, "
            "and apply directly to clean, dry affected skin 1–2 times daily for 2–3 weeks."
        ),
        "contraindications": (
            "For EXTERNAL TOPICAL USE ONLY in this preparation—internal ingestion of leaves causes strong anthraquinone laxative cramping. "
            "Discontinue if localized contact dermatitis or irritation develops."
        ),
        "reference": "DOH / PITAHC Topical Herbal Monograph (RA 8423)",
    },
    {
        "class_key": "05_Psidium_guajava",
        "common_name": "Bayabas (Guava)",
        "local_names": "Bayabas (Tagalog/Bisaya/Ilokano), Guyabas",
        "scientific_name": "Psidium guajava L.",
        "family": "Myrtaceae",
        "safety_tier": "SAFE_DOH_APPROVED",
        "safety_banner": "DOH / PITAHC Endorsed Antiseptic Wash (RA 8423)",
        "botanical_markers": (
            "Opposite, oblong-elliptical leaves (7–15 cm long) with entire margins, slightly leathery matte-green surface, "
            "finely hairy underside, and 12–20 pairs of strongly impressed parallel lateral veins curving near the margin."
        ),
        "traditional_uses": (
            "DOH-approved astringent and antiseptic wash for superficial cuts, minor skin wounds, post-partum hygiene, "
            "and as an oral gargle for swollen gums and toothache."
        ),
        "preparation": (
            "Antiseptic Wash: Wash a handful of young leaves thoroughly and boil in 4 glasses of water for 15 minutes in an uncovered pot. "
            "Cool to lukewarm, strain, and use to irrigate minor wounds or gargle 2–3 times daily."
        ),
        "contraindications": (
            "Do not apply concentrated decoctions to deep puncture wounds, severe burns, or infected abscesses requiring antibiotics/tetanus care."
        ),
        "reference": "DOH / PITAHC Essential Herbal Wash Monograph",
    },
    {
        "class_key": "06_Coleus_amboinicus",
        "common_name": "Philippine Oregano (Suganda / Cuban Oregano)",
        "local_names": "Oregano / Suganda (Tagalog), Kalabo (Bisaya), Lata (Subanen)",
        "scientific_name": "Coleus amboinicus Lour. (syn. Plectranthus amboinicus)",
        "family": "Lamiaceae",
        "safety_tier": "SAFE_TRADITIONAL",
        "safety_banner": "Common Backyard Culinary & Traditional Respiratory Herb",
        "botanical_markers": (
            "Thick, fleshy, succulent ovate-to-deltoid leaves densely covered in fine velvety hairs, featuring coarsely scalloped (crenate) "
            "margins and a strong, pungent thymol/carvacrol aroma when bruised. Distinct from thin-leaved Mediterranean Origanum vulgare."
        ),
        "traditional_uses": (
            "Widely used in Philippine households as a culinary spice and soothing steam inhalation or warm infusion for mild cough, "
            "nasal congestion, and sore throat."
        ),
        "preparation": (
            "Warm Infusion: Wash 5–7 fresh mature leaves, bruise lightly, and steep in 1 cup of freshly boiled water for 5–10 minutes. "
            "Strain and drink warm with calamansi or honey; may also be crushed and inhaled for nasal congestion."
        ),
        "contraindications": (
            "Avoid concentrated essential oil or excessive high-dose extracts during pregnancy. Perform a skin patch test before topical application."
        ),
        "reference": "Philippine Traditional Botanical & Ethnomedicinal Compendium",
    },
    {
        "class_key": "07_Moringa_oleifera",
        "common_name": "Malunggay (Moringa / Drumstick Tree)",
        "local_names": "Malunggay (Tagalog/Bisaya), Marunggay (Ilokano), Balunggay",
        "scientific_name": "Moringa oleifera Lam.",
        "family": "Moringaceae",
        "safety_tier": "SAFE_NUTRITIONAL",
        "safety_banner": "Nutritional & Galactagogue Culinary Leaf",
        "botanical_markers": (
            "Tripinnately compound feathery leaves divided into numerous small (1–2 cm), oval-to-obovate, thin, entire-margined leaflets "
            "arranged in opposite pairs with a slightly larger terminal leaflet; pale green underside."
        ),
        "traditional_uses": (
            "Nutrient-dense vegetable rich in iron, calcium, vitamins A and C; traditionally consumed in broths to support maternal lactation "
            "(galactagogue) and general nutrition."
        ),
        "preparation": (
            "Culinary Broth / Infusion: Strip fresh leaflets from stems, wash thoroughly, and simmer in soups/broths for 3–5 minutes "
            "to preserve heat-sensitive vitamins, or steep 1 tablespoon of washed fresh leaflets in hot water for 5 minutes."
        ),
        "contraindications": (
            "Leaves are safe as food; strictly avoid consuming root or stem bark extracts, which contain toxic alkaloids (spirochin) "
            "and uterine-stimulating compounds."
        ),
        "reference": "DOST-FNRI Philippine Food Composition & Ethnobotanical Guide",
    },
    {
        "class_key": "08_Hibiscus_rosa_sinensis",
        "common_name": "Gumamela (China Rose / Shoe-Flower)",
        "local_names": "Gumamela (Tagalog/Bisaya), Kayanga (Ilokano)",
        "scientific_name": "Hibiscus rosa-sinensis L.",
        "family": "Malvaceae",
        "safety_tier": "SAFE_TOPICAL_TRADITIONAL",
        "safety_banner": "Traditional External Emollient Poultice Only",
        "botanical_markers": (
            "Alternate, glossy dark-green, ovate-to-lanceolate leaves with a pointed apex, rounded-to-wedge base, and coarsely toothed (serrate) "
            "margins along the upper two-thirds of the blade; mucilaginous sap when crushed."
        ),
        "traditional_uses": (
            "Traditionally used externally in the Philippines as a soothing mucilaginous poultice to help soften and draw out minor superficial "
            "boils (pigsa) and localized skin swelling."
        ),
        "preparation": (
            "External Poultice: Wash fresh young leaves and flower buds thoroughly with clean water, pound into a mucilaginous paste, "
            "and apply externally over intact skin or closed minor boils covered with clean gauze."
        ),
        "contraindications": (
            "For EXTERNAL APPLICATION ONLY. Do not apply to open, draining, or deeply infected abscesses—seek medical evaluation if accompanied "
            "by fever, red streaks, or spreading warmth."
        ),
        "reference": "Philippine Medicinal Plants Ethnobotanical Reference",
    },
    {
        "class_key": "09_Jatropha_curcas",
        "common_name": "Tuba-tuba (Physic Nut / Purging Nut)",
        "local_names": "Tuba-tuba (Bisaya/Tagalog), Tawatawa (Ilokano), Kasla",
        "scientific_name": "Jatropha curcas L.",
        "family": "Euphorbiaceae",
        "safety_tier": "TOXIC_ALERT",
        "safety_banner": "TOXIC INGESTION ALERT — DO NOT EAT OR DRINK",
        "botanical_markers": (
            "Large, broadly cordate (heart-shaped) leaves (10–18 cm wide) that are shallowly 3-to-5-lobed with palmate venation, "
            "smooth entire margins, long petioles, and watery/milky sap that exudes when the stem or petiole is broken."
        ),
        "traditional_uses": (
            "Historically applied externally in folk practice as warmed leaves for minor sprains or bruises, "
            "but frequently mistaken for edible or internal medicinal herbs."
        ),
        "preparation": (
            "DO NOT PREPARE FOR INTERNAL CONSUMPTION. Never boil as tea, juice, or broth. External contact with raw latex sap "
            "can also irritate skin and eyes."
        ),
        "contraindications": (
            "SEVERE TOXICITY HAZARD: Seeds, sap, and raw plant tissues contain curcin (a toxalbumin) and phorbol esters. "
            "Ingestion causes violent vomiting, hemorrhagic diarrhea, severe dehydration, and cardiovascular collapse. Keep away from children."
        ),
        "reference": "UP-PGH National Poison Management and Control Center (NPMCC) Safety Advisory",
    },
    {
        "class_key": "10_Nerium_oleander",
        "common_name": "Adelfa (Oleander)",
        "local_names": "Adelfa (Tagalog/Bisaya/Spanish), Baladre",
        "scientific_name": "Nerium oleander L.",
        "family": "Apocynaceae",
        "safety_tier": "CRITICAL_POISON",
        "safety_banner": "CRITICAL LETHAL POISON WARNING — ALL PARTS TOXIC",
        "botanical_markers": (
            "Thick, leathery, narrow lance-shaped (linear-lanceolate) leaves arranged in opposite pairs or whorls of 3, "
            "with a prominent pale central midrib, fine parallel secondary veins, and thick milky-white latex sap."
        ),
        "traditional_uses": (
            "Ornamental roadside and garden shrub. HAS NO SAFE HOME MEDICINAL USE. Occasionally confused with narrow-leaved "
            "herbal shrubs by untrained foragers."
        ),
        "preparation": (
            "STRICTLY DO NOT HARVEST, BOIL, INGEST, OR APPLY. Even smoke from burning branches or water left in contact with leaves is toxic."
        ),
        "contraindications": (
            "LETHAL CARDIAC GLYCOSIDE POISONING: Contains oleandrin and neriine, which cause fatal cardiac arrhythmias, hyperkalemia, "
            "seizures, and sudden cardiac arrest even in small quantities. Contact Poison Control / Emergency Services immediately if ingested."
        ),
        "reference": "UP-PGH National Poison Management and Control Center (NPMCC) & WHO Toxicology Monograph",
    },
]


def build_database():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE monographs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            class_key TEXT UNIQUE NOT NULL,
            common_name TEXT NOT NULL,
            local_names TEXT NOT NULL,
            scientific_name TEXT NOT NULL,
            family TEXT NOT NULL,
            safety_tier TEXT NOT NULL,
            safety_banner TEXT NOT NULL,
            botanical_markers TEXT NOT NULL,
            traditional_uses TEXT NOT NULL,
            preparation TEXT NOT NULL,
            contraindications TEXT NOT NULL,
            reference TEXT NOT NULL
        )
    """)

    for m in MONOGRAPHS:
        cur.execute("""
            INSERT INTO monographs (
                class_key, common_name, local_names, scientific_name, family,
                safety_tier, safety_banner, botanical_markers, traditional_uses,
                preparation, contraindications, reference
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            m["class_key"], m["common_name"], m["local_names"], m["scientific_name"],
            m["family"], m["safety_tier"], m["safety_banner"], m["botanical_markers"],
            m["traditional_uses"], m["preparation"], m["contraindications"], m["reference"]
        ))

    conn.commit()
    conn.close()
    print(f"Successfully built {DB_PATH} with {len(MONOGRAPHS)} botanical & safety monographs.")


if __name__ == "__main__":
    build_database()