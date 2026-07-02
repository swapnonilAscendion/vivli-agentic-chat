#!/bin/bash

# Continuous monitoring script for ingestion pipeline
LOG_FILE="ingestion_full.log"
LAST_SIZE=0

echo "=================================="
echo "VIVLI RAG PIPELINE MONITOR"
echo "Started: $(date)"
echo "=================================="
echo ""

check_status() {
    local current_size=$(stat -f%z "$LOG_FILE" 2>/dev/null || stat -L --format=%s "$LOG_FILE" 2>/dev/null || echo 0)
    local embeddings=$(grep -c "Generated embedding" "$LOG_FILE" 2>/dev/null || echo 0)
    local indexed=$(grep -c "Indexed batch" "$LOG_FILE" 2>/dev/null || echo 0)
    local errors=$(grep -c "ERROR" "$LOG_FILE" 2>/dev/null || echo 0)
    local batches=$(grep "Batch.*Processing chunks" "$LOG_FILE" 2>/dev/null | tail -1)
    local completion=$(grep "INGESTION COMPLETE\|Total documents indexed" "$LOG_FILE" 2>/dev/null | tail -1)

    echo "[$(date '+%Y-%m-%d %H:%M:%S')] PIPELINE STATUS"
    echo "  Log size: $(($current_size / 1024))KB (was $(($LAST_SIZE / 1024))KB)"
    echo "  Embeddings generated: $embeddings"
    echo "  Batches indexed: $indexed"
    echo "  Errors: $errors"

    if [ ! -z "$batches" ]; then
        echo "  Current: $batches"
    fi

    if [ ! -z "$completion" ]; then
        echo "  ✅ COMPLETE: $completion"
        return 0
    elif grep -q "ERROR.*Ingestion pipeline error\|Failed to\|Exception" "$LOG_FILE"; then
        echo "  ❌ ERROR DETECTED - Check logs"
        return 1
    else
        echo "  ⏳ Still running..."
        return 2
    fi

    LAST_SIZE=$current_size
    echo ""
}

# First check
check_status
check_result=$?

# Keep checking every 30 seconds
while [ $check_result -eq 2 ]; do
    sleep 30
    check_status
    check_result=$?
done

if [ $check_result -eq 0 ]; then
    echo "=================================="
    echo "✅ INGESTION PIPELINE COMPLETED SUCCESSFULLY"
    echo "=================================="
    tail -20 "$LOG_FILE"
else
    echo "=================================="
    echo "❌ INGESTION PIPELINE FAILED"
    echo "=================================="
    tail -30 "$LOG_FILE"
fi
