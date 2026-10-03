"""
Veterinary Emergency First-Aid Protocols Database
Provides dynamic, species-specific, and injury-severity-tailored first-aid guidance.
"""

SPECIES_FIRST_AID = {
    'DOG': {
        'name': 'Canine (Dog)',
        'icon': 'fa-dog',
        'safe_handling': [
            "Approach slowly, speaking in a calm, soothing voice.",
            "Never put your face directly near the dog's mouth; an injured dog may bite out of intense fear or pain.",
            "Fashion an emergency muzzle using a soft cloth, gauze strip, or leash (UNLESS the dog is vomiting, gasping, or has a snout fracture).",
            "Gently wrap the dog in a warm towel or blanket before attempting to move them.",
        ],
        'critical_dos': [
            "Keep the dog lying on a flat, firm surface on their uninjured side.",
            "Apply direct, gentle pressure with a clean cloth or sterile gauze if there is active bleeding.",
            "Keep the animal warm to prevent physiological shock using a light blanket or jacket.",
            "Check breathing frequency by watching chest movement.",
        ],
        'critical_donts': [
            "DO NOT administer human pain medications (e.g. Paracetamol, Ibuprofen, Aspirin) - these are lethal to dogs!",
            "DO NOT offer water or food if the dog is unconscious or in severe shock.",
            "DO NOT try to reset a broken bone or push exposed bone back into flesh.",
            "DO NOT leave an injured dog unattended in the middle of a traffic lane.",
        ],
    },
    'CAT': {
        'name': 'Feline (Cat)',
        'icon': 'fa-cat',
        'safe_handling': [
            "Approach with extreme caution; frightened cats may scratch violently.",
            "Use a thick towel or blanket to gently wrap the cat ('Burrito wrap' method) leaving only the nose exposed.",
            "Place the cat in a secure, well-ventilated cardboard box or pet carrier for transport.",
            "Dim direct light to reduce stress and sensory overload.",
        ],
        'critical_dos': [
            "Keep the cat in a warm, dark, and quiet environment until help arrives.",
            "If bleeding, apply light, constant pressure with sterile gauze.",
            "Keep the airway clear and neck extended gently.",
            "Observe gum color: pink is healthy, pale/white indicates shock, blue/purple indicates asphyxiation.",
        ],
        'critical_donts': [
            "DO NOT scruff an adult cat suffering from respiratory distress or chest trauma.",
            "DO NOT give human medication or cow's milk.",
            "DO NOT attempt to pull strings or foreign objects lodged in the throat or rectum.",
        ],
    },
    'BIRD': {
        'name': 'Avian (Bird)',
        'icon': 'fa-dove',
        'safe_handling': [
            "Gently cover the bird with a lightweight, soft towel to prevent wing fluttering.",
            "Hold the bird securely around the body without pressing on its breastbone (birds lack a diaphragm and can suffocate).",
            "Place in a small, dark, ventilated cardboard box lined with paper towels.",
        ],
        'critical_dos': [
            "Keep the container in a warm (approx 28°C-30°C / 82°F-86°F), quiet room away from pets.",
            "For broken wings, support the wing gently against the body with a light cloth.",
            "For minor bleeding, apply light pressure using a clean cotton swab and cornstarch/flour.",
        ],
        'critical_donts': [
            "DO NOT force water or liquids into the bird's beak (high risk of drowning/aspiration).",
            "DO NOT expose to drafts, air conditioners, or direct harsh sunlight.",
            "DO NOT spray antiseptics or aerosols near the bird.",
        ],
    },
    'COW': {
        'name': 'Bovine / Cattle (Cow / Bull)',
        'icon': 'fa-cow',
        'safe_handling': [
            "Keep a safe distance from horns and hind legs (cows can kick sideways and backward).",
            "Alert local traffic immediately to prevent secondary vehicular collisions.",
            "Ensure the animal is not lying with its head downhill or in a drainage ditch.",
        ],
        'critical_dos': [
            "If standing in traffic, place emergency cones or warning markers 50 meters upstream.",
            "Provide shade or cover if exposed to harsh midday heat.",
            "Offer clean water in a shallow bucket only if the animal is alert and standing.",
            "Apply clean cotton cloths with moderate pressure on visible horn or leg lacerations.",
        ],
        'critical_donts': [
            "DO NOT try to forcefully drag a recumbent heavy cow by the limbs or tail.",
            "DO NOT crowd or shout, which agitates large livestock.",
        ],
    },
    'HORSE': {
        'name': 'Equine (Horse / Donkey)',
        'icon': 'fa-horse',
        'safe_handling': [
            "Always approach toward the shoulder, never from directly behind.",
            "Speak in low, soothing tones and avoid abrupt gestures.",
            "Keep bystanders at a minimum 10-meter perimeter.",
        ],
        'critical_dos': [
            "Check for severe limb fractures; if present, discourage the horse from standing.",
            "Cover with a light blanket if shivering or in shock.",
            "Apply firm pressure bandages to arterial bleeds.",
        ],
        'critical_donts': [
            "DO NOT tie the horse with a tight knot that cannot be quickly released.",
            "DO NOT feed grain or cold water to a horse in colic or shock.",
        ],
    },
    'WILDLIFE': {
        'name': 'Wildlife & Exotic Animals',
        'icon': 'fa-tree',
        'safe_handling': [
            "Maintain a strict safe perimeter. Do not touch venomous reptiles or wild carnivores.",
            "Contact wildlife sanctuary wardens immediately via the emergency hotline.",
            "Block off domestic dogs and humans from harassing the wild animal.",
        ],
        'critical_dos': [
            "Cover non-venomous smaller wildlife with a ventilated basket or crate.",
            "Keep silence and darkness to reduce fatal capture myopathy.",
        ],
        'critical_donts': [
            "DO NOT attempt to pet, handle, or take selfies with injured wild animals.",
            "DO NOT feed inappropriate wild foods.",
        ],
    }
}

SEVERITY_PROTOCOLS = {
    'CRITICAL': {
        'title': 'CRITICAL EMERGENCY (Immediate Life Threat)',
        'badge_class': 'bg-danger text-white',
        'alert_class': 'alert-danger',
        'urgency': 'Ambulance is requested on TOP PRIORITY with emergency sirens.',
        'steps': [
            "1. AIRWAY: Ensure mouth and nose are unobstructed. Clear vomit or debris gently with a cloth.",
            "2. BLEEDING CONTROL: If arterial (spurting or bright red), apply immediate direct pressure with sterile pad. Do not release pressure until medics arrive.",
            "3. SHOCK PREVENTION: Keep the animal lying flat. Wrap body in a dry blanket. Keep head level with spine.",
            "4. DO NOT MOVE: Unless the animal is in immediate danger of fire or oncoming traffic, do not move spinal injuries.",
            "5. MONITOR VITALS: Observe if chest is rising and falling. Keep bystanders away to maximize oxygen circulation."
        ]
    },
    'SEVERE': {
        'title': 'SEVERE (Urgent Medical Intervention Required)',
        'badge_class': 'bg-warning text-dark',
        'alert_class': 'alert-warning',
        'urgency': 'Hospital triage alert active. Rescue crew dispatched with ETA ~10-20 mins.',
        'steps': [
            "1. IMMOBILIZATION: Prevent the animal from walking if a limb fracture or joint dislocation is suspected.",
            "2. DRESSING: Cover open wounds with a clean damp cloth to keep tissues hydrated and reduce bacterial contamination.",
            "3. CALM THE ANIMAL: Sit near the head, talk softly, shield eyes from bright glare.",
            "4. HYDRATION: Do not force drinking if breathing is labored or animal is disoriented.",
            "5. PREPARE ACCESS: Clear a smooth path for the arriving rescue ambulance team."
        ]
    },
    'MODERATE': {
        'title': 'MODERATE (Stable but Needs Clinical Treatment)',
        'badge_class': 'bg-info text-dark',
        'alert_class': 'alert-info',
        'urgency': 'Rescue team queued. First-aid will stabilize the animal.',
        'steps': [
            "1. INSPECT WOUNDS: Clean superficial cuts gently with saline water or clean drinking water.",
            "2. BANDAGE: Apply light gauze wrap around minor bleeding or abrasions.",
            "3. COMFORT: Provide a cushioned mat or cardboard bed in a shaded spot.",
            "4. WATER: Small sips of clean water may be offered if the animal is fully conscious.",
            "5. OBSERVE: Watch for sudden lethargy or worsening symptoms."
        ]
    },
    'MINOR': {
        'title': 'MINOR (Superficial Injury / Welfare Check)',
        'badge_class': 'bg-success text-white',
        'alert_class': 'alert-success',
        'urgency': 'Paramedic or volunteer scheduled for on-site dressing & vaccination check.',
        'steps': [
            "1. CLEANSE: Wash minor scrapes with saline solution or mild soap water.",
            "2. ANTISEPTIC: Apply pet-safe antiseptic ointment (e.g. Betadine / Povidone-iodine dilution).",
            "3. NUTRITION: Provide clean water and wholesome food.",
            "4. MONITOR: Check if the animal is eating, drinking, and walking normally."
        ]
    }
}

def get_first_aid_guide(species='DOG', severity='MODERATE'):
    """Returns tailored first-aid dictionary combining species and severity protocols."""
    species_key = species.upper() if species else 'DOG'
    if species_key not in SPECIES_FIRST_AID:
        species_key = 'DOG'
        
    sev_key = severity.upper() if severity else 'MODERATE'
    if sev_key not in SEVERITY_PROTOCOLS:
        sev_key = 'MODERATE'
        
    return {
        'species_info': SPECIES_FIRST_AID[species_key],
        'severity_info': SEVERITY_PROTOCOLS[sev_key],
    }
