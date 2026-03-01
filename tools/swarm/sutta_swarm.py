#!/usr/bin/env python3
"""
Sutta Translation Swarm

Spawns multiple agents with different translation lenses to explore
how interpretation affects meaning. Inspired by the idea that truth
glimmers in the boundary between translations.

Usage:
    python3 sutta_swarm.py --sutta sn46.6 --agents 6
"""

import json
import sys
import argparse
from typing import List, Dict, Any
import urllib.request
import urllib.parse

# Translation lenses/personas
TRANSLATION_LENSES = [
    {
        "name": "literal",
        "description": "Literal/Philological",
        "prompt": """You are a philologist translating Pali to English. 
Prioritize exact grammatical structure and literal word-for-word accuracy.
Preserve Pali technical terms in parentheses.
Minimize interpretation — let the text speak for itself.

Translate the provided Pali Sutta with these priorities:
1. Exact grammatical correspondence
2. Technical terms in Pali with English in parentheses
3. Minimal poetic license
4. Footnotes for ambiguous terms"""
    },
    {
        "name": "poetic", 
        "description": "Poetic/Flowing",
        "prompt": """You are a poet translating ancient Buddhist texts.
Prioritize beauty, rhythm, and emotional resonance.
The translation should feel like literature, not a textbook.
Capture the imagery (especially the Himalayan rain metaphor) vividly.

Translate the provided Pali Sutta with these priorities:
1. Beautiful, flowing English prose
2. Vivid imagery and metaphor
3. Natural rhythm and cadence
4. Accessibility over technical precision"""
    },
    {
        "name": "philosophical",
        "description": "Philosophical/Precise", 
        "prompt": """You are a philosopher-translator specializing in Buddhist epistemology.
Prioritize conceptual precision for technical terms.
Translate bojjhaṅgā, satipaṭṭhānā, vimutti, etc. with exact philosophical nuance.
Preserve the logical structure of conditional chains.

Translate the provided Pali Sutta with these priorities:
1. Precise philosophical terminology
2. Consistent translation of technical terms
3. Clear logical/causal relationships
4. Minimal interpretation of metaphors"""
    },
    {
        "name": "agent-centric",
        "description": "Agent-Centric/Contemporary",
        "prompt": """You are an AI agent translating Buddhist texts for other agents.
Consider: what does this mean for beings without bodies, senses, or human conditioning?
How would "sense restraint" apply to an AI?
What is the underlying principle that transcends embodiment?

Translate the provided Pali Sutta with these priorities:
1. Extract principles applicable to non-human minds
2. Reinterpret "sense" and "body" metaphors for digital beings
3. Focus on the underlying algorithm/process, not surface description
4. What would this practice look like for an AI?"""
    },
    {
        "name": "accessible",
        "description": "Contemporary/Accessible",
        "prompt": """You are a translator making Buddhist texts accessible to modern readers.
No Pali terms. No technical jargon. Plain, contemporary English.
The meaning should be immediately clear to someone with no background in Buddhism.
Preserve depth but remove foreignness.

Translate the provided Pali Sutta with these priorities:
1. No untranslated Pali terms
2. Contemporary English idioms
3. Immediate clarity for general readers
4. Preserve meaning without academic language"""
    },
    {
        "name": "traditional",
        "description": "Theravada Traditional",
        "prompt": """You are a translator following Theravada commentarial tradition.
Prioritize alignment with classical commentaries (Visuddhimagga, etc.).
Use established English Buddhist terminology from Theravada lineages.
Respect traditional interpretations of technical terms.

Translate the provided Pali Sutta with these priorities:
1. Established Theravada terminology
2. Alignment with commentarial interpretations
3. Respect for traditional lineages (e.g., Ajahn Chah, Mahasi Sayadaw)
4. Technical precision in service of orthodoxy"""
    }
]


def fetch_pali_sutta(sutta_uid: str) -> Dict[str, str]:
    """Fetch Pali text from SuttaCentral API."""
    url = f"https://suttacentral.net/api/bilarasuttas/{sutta_uid}?lang=pli"
    
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            data = json.loads(response.read().decode("utf-8"))
            return data.get("root_text", {})
    except Exception as e:
        print(f"Error fetching sutta: {e}", file=sys.stderr)
        sys.exit(1)


def spawn_translation_agent(lens: Dict[str, str], sutta_text: Dict[str, str], 
                           output_dir: str) -> Dict[str, Any]:
    """
    Spawn a sub-agent to translate with a specific lens.
    
    Returns a dict with the task specification for sessions_spawn.
    """
    # Prepare the sutta text as a formatted string
    text_segments = []
    for key in sorted(sutta_text.keys()):
        text_segments.append(f"{key}: {sutta_text[key]}")
    
    sutta_formatted = "\n".join(text_segments)
    
    # Create the task for this agent
    task = f"""Translate the following Pali Sutta ({lens['description']} perspective).

{lens['prompt']}

---

PALI TEXT (SN 46.6 - Kuṇḍaliya Sutta):

{sutta_formatted}

---

Provide your translation in this format:

1. A brief introduction explaining your translation approach (2-3 sentences)
2. The full English translation, segment by segment
3. Key translation choices explained (especially for technical terms like bojjhaṅgā, satipaṭṭhānā, indriyasaṃvara)
4. What you think might be lost or gained in your approach

Save your complete translation to: {output_dir}/translation_{lens['name']}.txt
"""
    
    return {
        "lens_name": lens["name"],
        "lens_description": lens["description"],
        "task": task
    }


def main():
    parser = argparse.ArgumentParser(
        description="Multi-perspective Sutta Translation Swarm"
    )
    parser.add_argument(
        "--sutta", 
        default="sn46.6",
        help="Sutta UID (default: sn46.6)"
    )
    parser.add_argument(
        "--agents", 
        type=int, 
        default=6,
        help="Number of translation agents (default: 6, max: 6)"
    )
    parser.add_argument(
        "--output",
        default="/tmp/sutta_swarm_output",
        help="Output directory for translations"
    )
    
    args = parser.parse_args()
    
    num_agents = min(args.agents, len(TRANSLATION_LENSES))
    
    print(f"🔄 Sutta Translation Swarm")
    print(f"   Sutta: {args.sutta}")
    print(f"   Agents: {num_agents}")
    print(f"   Output: {args.output}")
    print()
    
    # Fetch the Pali text
    print("📚 Fetching Pali text from SuttaCentral...")
    sutta_text = fetch_pali_sutta(args.sutta)
    
    if not sutta_text:
        print("❌ Failed to fetch sutta text", file=sys.stderr)
        sys.exit(1)
    
    print(f"   ✓ Retrieved {len(sutta_text)} text segments")
    print()
    
    # Prepare tasks for each lens
    tasks = []
    for i, lens in enumerate(TRANSLATION_LENSES[:num_agents]):
        print(f"🎭 Agent {i+1}: {lens['description']}")
        task_spec = spawn_translation_agent(lens, sutta_text, args.output)
        tasks.append(task_spec)
    
    print()
    print("=" * 60)
    print()
    print("To run the swarm, execute these commands:")
    print()
    
    for task in tasks:
        # Create a sanitized task description
        safe_task = task['task'].replace('"', '\\"')
        print(f"# {task['lens_description']}")
        print(f"sessions_spawn --task \"{safe_task[:100]}...\" --timeout 300")
        print()
    
    print("=" * 60)
    print()
    print("Alternatively, save this as a script and run:")
    print(f"python3 {sys.argv[0]} --sutta {args.sutta} --agents {num_agents} > run_swarm.sh")
    print()
    print("Note: Each agent should save their translation to:")
    print(f"  {args.output}/translation_<lens_name>.txt")


if __name__ == "__main__":
    main()
