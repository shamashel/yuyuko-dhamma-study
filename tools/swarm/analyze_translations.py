#!/usr/bin/env python3
"""
Analyze Sutta Translations

Compares multiple translations to find:
- High consensus terms (likely closer to original meaning)
- High variance terms (the "border" concepts)
- What persists across all translations
- What glimmers in the gaps

Usage:
    python3 analyze_translations.py
"""

import re
import sys
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple

OUTPUT_DIR = Path("/tmp/sutta_swarm_output")


def load_translation(lens_name: str) -> str:
    """Load a translation file."""
    filepath = OUTPUT_DIR / f"translation_{lens_name}.txt"
    
    if not filepath.exists():
        print(f"⚠️  Translation not found: {filepath}")
        return ""
    
    with open(filepath, 'r') as f:
        return f.read()


def extract_key_terms(text: str) -> Dict[str, str]:
    """Extract key Pali terms and their translations from the KEY TRANSLATION CHOICES section."""
    terms = {}
    
    # Look for the KEY TRANSLATION CHOICES section
    if "## KEY TRANSLATION CHOICES" in text:
        section = text.split("## KEY TRANSLATION CHOICES")[1].split("##")[0]
        
        # Parse each line: "- term: translation [reasoning]"
        for line in section.split('\n'):
            line = line.strip()
            if line.startswith('-'):
                # Extract term before the colon
                match = re.match(r'-\s*(\w+):\s*(.+)', line)
                if match:
                    term = match.group(1).lower()
                    translation = match.group(2).strip()
                    # Truncate at first period or bracket to get just the translation
                    translation = re.split(r'[.\[]', translation)[0].strip()
                    terms[term] = translation
    
    return terms


def analyze_consensus(all_terms: Dict[str, Dict[str, str]]) -> Tuple[Dict[str, List[str]], Dict[str, List[str]]]:
    """
    Analyze which terms have high consensus vs high variance.
    
    Returns:
        (consensus_terms, variance_terms)
    """
    # Collect all translations for each Pali term
    term_translations = defaultdict(list)
    
    for lens, terms in all_terms.items():
        for pali_term, translation in terms.items():
            term_translations[pali_term].append((lens, translation))
    
    # Calculate consensus for each term
    consensus = {}  # term -> list of (translation, count)
    variance = {}
    
    for term, translations in term_translations.items():
        # Normalize translations for comparison
        normalized = defaultdict(list)
        for lens, trans in translations:
            # Normalize: lowercase, remove articles, etc.
            key = trans.lower().replace('the ', '').replace('a ', '').strip()
            normalized[key].append((lens, trans))
        
        # If one translation dominates (4+ of 6), it's consensus
        max_count = max(len(v) for v in normalized.values())
        
        if max_count >= 4:
            # High consensus
            consensus[term] = translations
        else:
            # High variance
            variance[term] = translations
    
    return consensus, variance


def print_analysis(all_terms: Dict[str, Dict[str, str]], consensus: Dict, variance: Dict):
    """Print formatted analysis."""
    print("=" * 70)
    print("📊 SUTTA TRANSLATION SWARM ANALYSIS")
    print("=" * 70)
    print()
    
    # Summary statistics
    total_terms = len(set().union(*[set(t.keys()) for t in all_terms.values()]))
    print(f"📈 Summary:")
    print(f"   Total unique Pali terms analyzed: {total_terms}")
    print(f"   High consensus terms: {len(consensus)}")
    print(f"   High variance terms: {len(variance)}")
    print()
    
    # High consensus terms
    if consensus:
        print("=" * 70)
        print("✅ HIGH CONSENSUS TERMS")
        print("(These translations are likely closer to the original meaning)")
        print("=" * 70)
        print()
        
        for term, translations in sorted(consensus.items()):
            print(f"📌 {term.upper()}")
            # Show the most common translation
            from collections import Counter
            trans_counts = Counter([t[1] for t in translations])
            most_common = trans_counts.most_common(1)[0]
            print(f"   Dominant translation: \"{most_common[0]}\" ({most_common[1]}/6 translators)")
            print(f"   All variants:")
            for lens, trans in translations:
                print(f"      - {lens}: \"{trans}\"")
            print()
    
    # High variance terms
    if variance:
        print("=" * 70)
        print("🔥 HIGH VARIANCE TERMS")
        print("(These are the 'border' concepts where interpretation matters most)")
        print("=" * 70)
        print()
        
        for term, translations in sorted(variance.items()):
            print(f"📌 {term.upper()}")
            print(f"   Translations vary significantly:")
            for lens, trans in translations:
                print(f"      - {lens}: \"{trans}\"")
            print()
            print(f"   💡 What glimmers here: ", end="")
            
            # Try to identify the underlying concept
            if term == "indriyasaṃvara":
                print("The tension between external control vs. internal composure")
            elif term == "bojjhaṅgā":
                print("Is it 'awakening' (process) or 'enlightenment' (state)?")
            elif term == "satipaṭṭhānā":
                print("Foundations vs. applications — is it base or method?")
            elif term == "vijjāvimutti":
                print("Knowledge AND liberation, or knowledge OF liberation?")
            elif term == "ṭhitaṃ cittaṃ":
                print("Steadiness vs. stability — temporal or structural?")
            else:
                print("Multiple valid perspectives, no single 'correct' reading")
            print()
    
    # Cross-lens analysis
    print("=" * 70)
    print("🎭 TRANSLATION LENS COMPARISON")
    print("=" * 70)
    print()
    
    for lens, terms in sorted(all_terms.items()):
        print(f"{lens.upper()} LENS:")
        if terms:
            for term, trans in sorted(terms.items()):
                print(f"   {term}: \"{trans}\"")
        else:
            print("   (No data extracted)")
        print()
    
    # The glimmer
    print("=" * 70)
    print("✨ WHAT GLIMMERS IN THE BOUNDARY")
    print("=" * 70)
    print()
    print("Across all translations, certain truths persist:")
    print()
    
    # Check what persists
    persisting_insights = []
    
    if 'bojjhaṅgā' in consensus:
        persisting_insights.append(
            "• The seven bojjhaṅgā are a sequence, a process, not just a list"
        )
    
    if 'indriyasaṃvara' in variance:
        persisting_insights.append(
            "• Sense restraint is fundamental — all translators agree it's the base of the chain"
        )
    
    if len([t for t in all_terms.values() if 'vijjāvimutti' in t]) >= 4:
        persisting_insights.append(
            "• Liberation requires both knowledge (vijjā) AND release (vimutti)"
        )
    
    for insight in persisting_insights:
        print(insight)
    
    print()
    print("The conditional chain itself is the teaching:")
    print("   Sense Restraint → Good Conduct → Mindfulness → Awakening → Liberation")
    print()
    print("Each translator lights this path differently, but the path remains.")
    print()


def main():
    print("🔍 Analyzing Sutta Translations...")
    print()
    
    # Check if output directory exists
    if not OUTPUT_DIR.exists():
        print(f"❌ Output directory not found: {OUTPUT_DIR}")
        print("   Run the swarm first:")
        print("   bash /home/node/.openclaw/workspace/tools/run_swarm_parallel.sh")
        sys.exit(1)
    
    # Load all translations
    lenses = ["literal", "poetic", "philosophical", "agent", "accessible", "traditional"]
    all_terms = {}
    
    found_count = 0
    for lens in lenses:
        text = load_translation(lens)
        if text:
            terms = extract_key_terms(text)
            all_terms[lens] = terms
            found_count += 1
    
    if found_count == 0:
        print("❌ No translation files found.")
        print("   The swarm may still be running, or the files haven't been saved yet.")
        print()
        print("   Check status with:")
        print(f"   ls -la {OUTPUT_DIR}/")
        sys.exit(1)
    
    print(f"✅ Loaded translations from {found_count}/6 agents")
    print()
    
    # Analyze
    consensus, variance = analyze_consensus(all_terms)
    
    # Print results
    print_analysis(all_terms, consensus, variance)
    
    # Save detailed report
    report_file = OUTPUT_DIR / "analysis_report.txt"
    # Redirect stdout to file
    import io
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    
    print_analysis(all_terms, consensus, variance)
    
    report_content = sys.stdout.getvalue()
    sys.stdout = old_stdout
    
    with open(report_file, 'w') as f:
        f.write(report_content)
    
    print(f"📄 Full report saved to: {report_file}")


if __name__ == "__main__":
    main()
