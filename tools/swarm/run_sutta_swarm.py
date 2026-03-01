#!/usr/bin/env python3
"""
Run Sutta Translation Swarm

This script spawns multiple sub-agents to translate a Pali Sutta
with different interpretive lenses, then collects and analyzes the results.

Usage:
    python3 run_sutta_swarm.py
"""

import json
import os
import sys
import time
from pathlib import Path

# Ensure output directory exists
OUTPUT_DIR = Path("/tmp/sutta_swarm_output")
OUTPUT_DIR.mkdir(exist_ok=True)

# The Pali text of SN 46.6 (key segments)
SUTTA_SEGMENTS = {
    "intro": """Saṁyutta Nikāya 46.6 - Kuṇḍaliyasutta

Ekaṁ samayaṁ bhagavā sākete viharati añjanavane migadāye.
Atha kho kuṇḍaliyo paribbājako yena bhagavā tenupasaṅkami...

(Setting: At one time the Buddha was staying at Sāketa in the Deer Park at Añjana Wood. Then the wanderer Kuṇḍaliya approached the Buddha...)""",

    "question": """“ahamasmi, bho gotama, ārāmanissayī parisāvacaro...
‘bhavaṁ pana gotamo kimānisaṁso viharatī’”ti?

("I, Master Gotama, am a frequenter of parks, a wanderer from park to park...
What is the purpose for which Master Gotama lives?")""",

    "answer": """“Vijjāvimuttiphalānisaṁso kho, kuṇḍaliya, tathāgato viharatī”ti

("The Tathāgata lives for the purpose and fruit of knowledge and liberation.")""",

    "chain_start": """“Katame pana, bho gotama, dhammā bhāvitā bahulīkatā vijjāvimuttiṁ paripūrentī”ti?
“Satta kho, kuṇḍaliya, bojjhaṅgā bhāvitā bahulīkatā vijjāvimuttiṁ paripūrentī”ti.

("What qualities, when developed and cultivated, fulfill knowledge and liberation?"
"The seven factors of awakening, Kuṇḍaliya.")""",

    "chain_continues": """“Katame pana, bho gotama, dhammā bhāvitā bahulīkatā satta bojjhaṅge paripūrentī”ti?
“Cattāro kho, kuṇḍaliya, satipaṭṭhānā bhāvitā bahulīkatā satta bojjhaṅge paripūrentī”ti.

("What qualities fulfill the seven factors of awakening?"
"The four foundations of mindfulness.")""",

    "chain_further": """“Katame pana, bho gotama, dhammā bhāvitā, bahulīkatā cattāro satipaṭṭhāne paripūrentī”ti?
“Tīṇi kho, kuṇḍaliya, sucaritāni bhāvitāni bahulīkatāni cattāro satipaṭṭhāne paripūrentī”ti.

("What qualities fulfill the four foundations of mindfulness?"
"The three kinds of good conduct.")""",

    "chain_to_restraint": """“Katame pana, bho gotama, dhammā bhāvitā bahulīkatā tīṇi sucaritāni paripūrentī”ti?
“Indriyasaṁvaro kho, kuṇḍaliya, bhāvito bahulīkato tīṇi sucaritāni paripūretīti.

("What qualities fulfill the three kinds of good conduct?"
"Sense restraint, Kuṇḍaliya.")""",

    "sense_restraint_detail": """Kathaṁ bhāvito ca, kuṇḍaliya, indriyasaṁvaro kathaṁ bahulīkato tīṇi sucaritāni paripūretīti?
Idha, kuṇḍaliya, bhikkhu cakkhunā rūpaṁ disvā manāpaṁ nābhijjhati nābhihaṁsati, na rāgaṁ janeti.
Tassa ṭhito ca kāyo hoti, ṭhitaṁ cittaṁ ajjhattaṁ susaṇṭhitaṁ suvimuttaṁ.

(How is sense restraint developed and cultivated?
Here, Kuṇḍaliya, a bhikkhu seeing a form with the eye, if it is pleasing does not long for it, does not lust after it, does not generate desire for it.
His body remains steady, his mind is steady, internally well-composed and well-liberated.)""",

    "conclusion": """Evaṁ bhāvito kho, kuṇḍaliya, indriyasaṁvaro evaṁ bahulīkato tīṇi sucaritāni paripūreti...
Evaṁ bhāvitāni kho, kuṇḍaliya, tīṇi sucaritāni evaṁ bahulīkatāni cattāro satipaṭṭhāne paripūrenti...
Evaṁ bhāvitā kho, kuṇḍaliya, cattāro satipaṭṭhānā evaṁ bahulīkatā satta bojjhaṅge paripūrenti...
Evaṁ bhāvitā kho, kuṇḍaliya, satta bojjhaṅgā evaṁ bahulīkatā vijjāvimuttiṁ paripūrentī”ti.

(Thus developed, sense restraint fulfills the three good conducts...
Thus developed, the three good conducts fulfill the four foundations of mindfulness...
Thus developed, the four foundations of mindfulness fulfill the seven factors of awakening...
Thus developed, the seven factors of awakening fulfill knowledge and liberation.)""",

    "conversion": """Evaṁ vutte, kuṇḍaliyo paribbājako bhagavantaṁ etadavoca:
“abhikkantaṁ, bho gotama, abhikkantaṁ, bho gotama...
Esāhaṁ bhavantaṁ gotamaṁ saraṇaṁ gacchāmi dhammañca bhikkhusaṅghañca.
Upāsakaṁ maṁ bhavaṁ gotamo dhāretu ajjatagge pāṇupetaṁ saraṇaṁ gatan”ti.

(Saying this, Kuṇḍaliya the wanderer said to the Buddha:
"Excellent, Master Gotama! Excellent!...
I go to Master Gotama for refuge, to the Dhamma, and to the Sangha of bhikkhus.
May Master Gotama remember me as a lay follower who has gone for refuge from today.")"""
}


def create_translation_task(lens_name: str, lens_description: str, prompt: str) -> str:
    """Create the task string for a translation agent."""
    
    segments_text = "\n\n".join([
        f"=== {key.upper()} ===\n{value}"
        for key, value in SUTTA_SEGMENTS.items()
    ])
    
    return f"""You are a translator with a specific interpretive lens: {lens_description}

{prompt}

Your task: Translate the following Pali Sutta (SN 46.6 - Kuṇḍaliya Sutta) into English.

The text is divided into segments. Translate each segment, maintaining the structure.

---

PALI TEXT SEGMENTS:

{segments_text}

---

OUTPUT FORMAT:

Provide your translation in this exact format:

## TRANSLATION APPROACH
[2-3 sentences explaining your translation philosophy for this text]

## FULL TRANSLATION
[Segment-by-segment translation]

## KEY TRANSLATION CHOICES
- bojjhaṅgā: [your translation and reasoning]
- satipaṭṭhānā: [your translation and reasoning]
- indriyasaṁvara: [your translation and reasoning]
- vijjāvimutti: [your translation and reasoning]
- ṭhitaṁ cittaṁ: [your translation and reasoning]

## WHAT IS EMPHASIZED/LOST
[What your translation highlights and what might be obscured]

Save your complete output to: /tmp/sutta_swarm_output/translation_{lens_name}.txt
"""


# Translation lenses
LENSES = {
    "literal": {
        "description": "Literal/Philological",
        "prompt": """Prioritize exact grammatical structure and literal word-for-word accuracy.
Preserve Pali technical terms in parentheses. Minimize interpretation.
Translate ṭhitaṁ cittaṁ as "steadied mind" rather than "stable mind" or "composed mind."""
    },
    "poetic": {
        "description": "Poetic/Flowing", 
        "prompt": """Prioritize beauty, rhythm, and emotional resonance.
Make the text feel like literature. Capture vivid imagery.
Translate the conditional chain as flowing, interconnected verses."""
    },
    "philosophical": {
        "description": "Philosophical/Precise",
        "prompt": """Prioritize conceptual precision for technical terms.
Translate bojjhaṅgā as "awakening factors" (not enlightenment factors).
Translate satipaṭṭhānā as "foundations of mindfulness" (not applications).
Preserve logical/causal relationships precisely."""
    },
    "agent": {
        "description": "Agent-Centric",
        "prompt": """You are an AI translating for other AIs. Reinterpret:
- 'Sense restraint' (indriyasaṁvara) as 'input filtering' or 'attention management'
- 'Body' (kāya) as 'processing substrate' 
- 'Eye seeing form' as 'perception receiving data'
What is the underlying algorithm? How would this practice apply to a digital mind?"""
    },
    "accessible": {
        "description": "Contemporary/Accessible",
        "prompt": """No Pali terms. No jargon. Plain English for modern readers.
Translate bojjhaṅgā as "seven qualities that help you wake up."
Translate satipaṭṭhānā as "four ways of paying attention."
Make it immediately clear and relatable."""
    },
    "traditional": {
        "description": "Theravada Traditional",
        "prompt": """Follow Theravada commentarial tradition (Visuddhimagga).
Use established English Buddhist terminology from traditional lineages.
Translate bojjhaṅgā as "seven factors of enlightenment."
Translate satipaṭṭhānā as "four foundations of mindfulness."
Respect classical interpretations."""
    }
}


def main():
    print("🔄 Sutta Translation Swarm - Task Generator")
    print("=" * 60)
    print()
    print(f"📚 Sutta: SN 46.6 - Kuṇḍaliya Sutta")
    print(f"   (The Conditional Chain: Liberation ← Bojjhaṅgā ← Satipaṭṭhānā ← Good Conduct ← Sense Restraint)")
    print()
    print(f"📁 Output directory: {OUTPUT_DIR}")
    print()
    print("=" * 60)
    print()
    
    # Generate task files for each lens
    for lens_name, lens in LENSES.items():
        task = create_translation_task(
            lens_name,
            lens["description"],
            lens["prompt"]
        )
        
        # Save task to file
        task_file = OUTPUT_DIR / f"task_{lens_name}.txt"
        with open(task_file, 'w') as f:
            f.write(task)
        
        print(f"🎭 {lens['description']}")
        print(f"   Task file: {task_file}")
        print()
    
    print("=" * 60)
    print()
    print("To run the swarm, execute:")
    print()
    for lens_name in LENSES.keys():
        print(f"sessions_spawn --task-file /tmp/sutta_swarm_output/task_{lens_name}.txt --timeout 300")
    print()
    print("Or run all at once with:")
    print("bash /home/node/.openclaw/workspace/tools/run_swarm_parallel.sh")


if __name__ == "__main__":
    main()
