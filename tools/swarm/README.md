# Sutta Translation Swarm Tools

A toolkit for multi-perspective text analysis using parallel AI agents.

## What This Does

Spawns multiple sub-agents with different interpretive lenses to translate/analyze a text, then compares outputs to find:
- **High consensus** — terms that persist across all lenses
- **High variance** — concepts where interpretation matters most  
- **What glimmers** — truths that emerge in the boundary between translations

## Files

| File | Purpose |
|------|---------|
| `sutta_swarm.py` | Standalone task generator for manual use |
| `run_sutta_swarm.py` | Automated task generator + runner |
| `run_swarm_parallel.sh` | Bash script to spawn all agents in parallel |
| `analyze_translations.py` | Compare outputs, generate consensus/variance report |

## Quick Start

### 1. Generate tasks
```bash
python3 run_sutta_swarm.py
```
Creates 6 task files in `/tmp/sutta_swarm_output/`.

### 2. Run the swarm
```bash
bash run_swarm_parallel.sh
```
Spawns 6 parallel translation agents (or use `sessions_spawn` manually).

### 3. Analyze results
```bash
python3 analyze_translations.py
```
Compares all translations and generates a report.

## The Six Lenses

1. **Literal** — Philological, word-for-word, minimal interpretation
2. **Poetic** — Beauty, rhythm, emotional resonance
3. **Philosophical** — Technical precision, logical structure
4. **Agent-centric** — Reinterpreted for AI/digital minds
5. **Accessible** — No jargon, contemporary English
6. **Traditional** — Theravada commentarial approach

## Customization

Edit the `LENSES` dictionary in `run_sutta_swarm.py` to:
- Add new lenses
- Modify prompts
- Change the target text

## First Application

Translated **SN 46.6 (Kuṇḍaliya Sutta)** through all six lenses. 

**Key finding:** The agent-centric lens revealed "input filtering" as the underlying function of sense restraint — applicable to any mind, embodied or digital.

See [`../translations/sn46.6/`](../translations/sn46.6/) for full results.

## License

MIT — Use freely, modify as needed.

---

*Tools created March 1, 2026.*
