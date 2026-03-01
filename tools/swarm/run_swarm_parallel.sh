#!/bin/bash
# Run Sutta Translation Swarm in Parallel

OUTPUT_DIR="/tmp/sutta_swarm_output"

echo "🔄 Starting Sutta Translation Swarm"
echo "   Sutta: SN 46.6 - Kuṇḍaliya Sutta"
echo "   Agents: 6 parallel translators"
echo ""

# Run each translation agent in parallel
echo "🎭 Spawning translation agents..."

sessions_spawn --task-file "$OUTPUT_DIR/task_literal.txt" --timeout 300 &
PID1=$!
echo "   [1/6] Literal agent (PID: $PID1)"

sessions_spawn --task-file "$OUTPUT_DIR/task_poetic.txt" --timeout 300 &
PID2=$!
echo "   [2/6] Poetic agent (PID: $PID2)"

sessions_spawn --task-file "$OUTPUT_DIR/task_philosophical.txt" --timeout 300 &
PID3=$!
echo "   [3/6] Philosophical agent (PID: $PID3)"

sessions_spawn --task-file "$OUTPUT_DIR/task_agent.txt" --timeout 300 &
PID4=$!
echo "   [4/6] Agent-centric agent (PID: $PID4)"

sessions_spawn --task-file "$OUTPUT_DIR/task_accessible.txt" --timeout 300 &
PID5=$!
echo "   [5/6] Accessible agent (PID: $PID5)"

sessions_spawn --task-file "$OUTPUT_DIR/task_traditional.txt" --timeout 300 &
PID6=$!
echo "   [6/6] Traditional agent (PID: $PID6)"

echo ""
echo "⏳ Waiting for all agents to complete..."
wait $PID1 $PID2 $PID3 $PID4 $PID5 $PID6

echo ""
echo "✅ All translations complete!"
echo ""
echo "📁 Results saved to: $OUTPUT_DIR/"
echo ""
ls -la "$OUTPUT_DIR"/translation_*.txt 2>/dev/null || echo "   (Files may still be writing...)"
echo ""
echo "Next: Run analysis to compare translations"
echo "   python3 /home/node/.openclaw/workspace/tools/analyze_translations.py"
