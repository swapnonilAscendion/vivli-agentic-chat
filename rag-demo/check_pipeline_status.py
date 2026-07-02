#!/usr/bin/env python3
"""
Real-time status checker for the ingestion pipeline.
Run this repeatedly to monitor progress.
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict

def get_file_size_kb(filepath):
    """Get file size in KB."""
    try:
        return os.path.getsize(filepath) / 1024
    except:
        return 0

def count_pattern(filepath, pattern):
    """Count occurrences of a pattern in file."""
    count = 0
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                if pattern in line:
                    count += 1
    except:
        pass
    return count

def get_latest_batch_info(filepath):
    """Extract latest batch information."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            # Search backwards for batch info
            for line in reversed(lines):
                if 'Batch' in line and 'Processing chunks' in line:
                    return line.strip()
    except:
        pass
    return None

def get_final_stats(filepath):
    """Extract final statistics if available."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            if 'Total documents indexed:' in content:
                # Extract from the total indexed line
                for line in content.split('\n'):
                    if 'Total documents indexed:' in line:
                        return line.strip()
    except:
        pass
    return None

def check_for_errors(filepath):
    """Check for error lines and return the last few."""
    errors = []
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                if 'ERROR' in line or 'Error' in line or 'error' in line:
                    if any(x in line for x in ['Error', 'error', 'ERROR', 'Exception', 'exception', 'Traceback']):
                        errors.append(line.strip())
    except:
        pass
    return errors[-5:] if errors else []  # Return last 5 errors

def check_completion(filepath):
    """Check if pipeline has completed."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            if 'INGESTION COMPLETE' in content:
                return 'COMPLETED', 'success'
            if 'Total documents indexed:' in content:
                return 'INDEXING_DONE', 'success'
            if 'Ingestion pipeline error' in content or 'Failed to' in content:
                return 'FAILED', 'error'
            if 'Processing chunks' in content:
                return 'RUNNING', 'running'
    except:
        pass
    return 'UNKNOWN', 'unknown'

def print_status(log_file):
    """Print current pipeline status."""
    print("\n" + "=" * 80)
    print(f"VIVLI RAG INGESTION PIPELINE STATUS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    if not os.path.exists(log_file):
        print("ERROR: Log file not found!")
        return

    # Get metrics
    file_size = get_file_size_kb(log_file)
    embeddings = count_pattern(log_file, 'Generated embedding')
    batches_indexed = count_pattern(log_file, 'Indexed batch')
    errors = count_pattern(log_file, 'ERROR')
    status, status_type = check_completion(log_file)

    print(f"\n[METRICS]")
    print(f"  • Log file size: {file_size:.1f} KB")
    print(f"  • Embeddings generated: {embeddings}")
    print(f"  • Batches indexed: {batches_indexed}")
    print(f"  • Error count: {errors}")

    # Get current batch
    batch_info = get_latest_batch_info(log_file)
    if batch_info:
        print(f"\n[CURRENT PROGRESS]")
        print(f"  {batch_info}")

    # Get final stats if available
    final_stats = get_final_stats(log_file)
    if final_stats:
        print(f"\n[FINAL STATS]")
        print(f"  {final_stats}")

    # Status
    print(f"\n[STATUS]: {status}")
    if status_type == 'success':
        print("     SUCCESS - Pipeline completed successfully!")
    elif status_type == 'error':
        print("     ERROR - Pipeline encountered an error!")
    elif status_type == 'running':
        print("     RUNNING - Pipeline is still running...")

    # Show errors if any
    error_lines = check_for_errors(log_file)
    if error_lines:
        print(f"\n[RECENT ERRORS] ({len(error_lines)}):")
        for i, err in enumerate(error_lines, 1):
            print(f"  {i}. {err[:100]}...")

    # Show tail of log
    print(f"\n[LATEST LOG ENTRIES]:")
    print("-" * 80)
    try:
        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            for line in lines[-10:]:
                print(line.rstrip())
    except:
        pass

    print("-" * 80)
    print("=" * 80 + "\n")

if __name__ == "__main__":
    log_file = "ingestion_full.log"
    if len(sys.argv) > 1:
        log_file = sys.argv[1]

    check_dir = os.path.dirname(log_file) or "."
    if not os.path.exists(check_dir):
        print(f"Error: Directory not found: {check_dir}")
        sys.exit(1)

    # Change to the directory containing the log file
    os.chdir(check_dir)
    print_status(os.path.basename(log_file))
