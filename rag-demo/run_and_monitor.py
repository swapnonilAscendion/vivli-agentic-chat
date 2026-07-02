#!/usr/bin/env python3
"""
Comprehensive ingestion pipeline runner with real-time monitoring and status reporting.
"""

import asyncio
import subprocess
import sys
import time
import threading
import json
from datetime import datetime
from pathlib import Path
from collections import defaultdict

class PipelineMonitor:
    def __init__(self, log_file="ingestion_full.log"):
        self.log_file = log_file
        self.last_position = 0
        self.stats = {
            "chunks_processed": 0,
            "documents_indexed": 0,
            "errors": 0,
            "embeddings_generated": 0,
            "batches_completed": 0,
            "start_time": None,
            "current_batch": None,
            "total_batches": None,
        }
        self.error_log = []
        self.last_update = time.time()
        self.process = None

    def start_pipeline(self):
        """Start the ingestion pipeline as a subprocess."""
        print("\n" + "=" * 70)
        print("STARTING VIVLI RAG INGESTION PIPELINE")
        print("=" * 70)
        print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Log file: {self.log_file}")
        print("=" * 70 + "\n")

        # Run the pipeline with Python
        cmd = [
            sys.executable,
            "ingestion_pipeline.py",
        ]

        # Redirect output to log file and keep it running
        self.process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1,  # Line buffered
        )

        self.stats["start_time"] = datetime.now()
        return self.process.pid

    def monitor_logs(self):
        """Monitor the log file for updates and extract statistics."""
        try:
            if not Path(self.log_file).exists():
                return False

            with open(self.log_file, "r", encoding="utf-8", errors="ignore") as f:
                f.seek(self.last_position)
                new_lines = f.readlines()
                self.last_position = f.tell()

            for line in new_lines:
                self._parse_log_line(line)

            return True
        except Exception as e:
            print(f"Error monitoring logs: {e}")
            return False

    def _parse_log_line(self, line):
        """Parse a log line and extract relevant statistics."""
        line = line.strip()

        # Check for errors
        if "ERROR" in line:
            self.error_log.append(line)
            self.stats["errors"] += 1

        # Track embeddings generated
        if "Generated embedding" in line:
            self.stats["embeddings_generated"] += 1

        # Track batch processing
        if "Batch" in line and "Processing chunks" in line:
            try:
                parts = line.split("Batch ")
                if len(parts) > 1:
                    batch_info = parts[1].split(":")[0]
                    if "/" in batch_info:
                        current, total = batch_info.split("/")
                        self.stats["current_batch"] = int(current.strip())
                        self.stats["total_batches"] = int(total.strip())
            except:
                pass

        # Track documents indexed
        if "Indexed batch" in line:
            try:
                parts = line.split(":")
                if len(parts) > 1:
                    doc_count = int(parts[-1].split()[0])
                    self.stats["documents_indexed"] += doc_count
                    self.stats["batches_completed"] += 1
            except:
                pass

        # Check for completion
        if "INGESTION COMPLETE" in line or "Total documents indexed" in line:
            self.stats["completed"] = True

    def get_progress_string(self):
        """Generate a progress status string."""
        if self.stats["start_time"]:
            elapsed = (datetime.now() - self.stats["start_time"]).total_seconds()
            elapsed_str = f"{int(elapsed // 60)}m {int(elapsed % 60)}s"
        else:
            elapsed_str = "0m 0s"

        progress = []
        progress.append(f"\n{'=' * 70}")
        progress.append(f"PIPELINE STATUS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        progress.append(f"{'=' * 70}")
        progress.append(f"Elapsed time: {elapsed_str}")
        progress.append(f"Embeddings generated: {self.stats['embeddings_generated']}")
        progress.append(f"Documents indexed: {self.stats['documents_indexed']}")
        progress.append(f"Batches completed: {self.stats['batches_completed']}")

        if self.stats["current_batch"] and self.stats["total_batches"]:
            progress_pct = (
                self.stats["current_batch"] / self.stats["total_batches"] * 100
            )
            progress.append(
                f"Progress: Batch {self.stats['current_batch']}/{self.stats['total_batches']} ({progress_pct:.1f}%)"
            )

        if self.stats["errors"] > 0:
            progress.append(f"⚠️  Errors encountered: {self.stats['errors']}")
            # Show last few errors
            if self.error_log:
                progress.append("\nRecent errors:")
                for error in self.error_log[-3:]:
                    progress.append(f"  - {error[:100]}...")

        progress.append(f"{'=' * 70}\n")
        return "\n".join(progress)

    def monitor_process(self, check_interval=5):
        """Monitor the process and print status updates."""
        print(f"Process started (PID: {self.process.pid})")
        print(f"Monitoring with {check_interval}s check interval...\n")

        last_stats_print = time.time()

        while self.process.poll() is None:  # While process is running
            # Monitor logs and update stats
            self.monitor_logs()

            # Print status every check_interval seconds
            if time.time() - last_stats_print >= check_interval:
                print(self.get_progress_string())
                last_stats_print = time.time()

            time.sleep(1)

        # Process finished
        return_code = self.process.returncode
        print(f"\n{'=' * 70}")
        print(f"PROCESS FINISHED")
        print(f"{'=' * 70}")
        print(f"Exit code: {return_code}")
        print(f"Final statistics:")
        print(f"  - Embeddings generated: {self.stats['embeddings_generated']}")
        print(f"  - Documents indexed: {self.stats['documents_indexed']}")
        print(f"  - Batches completed: {self.stats['batches_completed']}")
        print(f"  - Errors: {self.stats['errors']}")

        if self.error_log:
            print(f"\n⚠️  All errors ({len(self.error_log)}):")
            for i, error in enumerate(self.error_log[:10], 1):
                print(f"  {i}. {error[:100]}...")
            if len(self.error_log) > 10:
                print(f"  ... and {len(self.error_log) - 10} more")

        print(f"{'=' * 70}\n")

        return return_code == 0


if __name__ == "__main__":
    monitor = PipelineMonitor()
    pid = monitor.start_pipeline()
    success = monitor.monitor_process(check_interval=10)

    # Also tail the log for final output
    print("\nFinal log entries:")
    print("-" * 70)
    with open(monitor.log_file, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
        # Print last 30 lines
        for line in lines[-30:]:
            print(line.rstrip())
    print("-" * 70)

    sys.exit(0 if success else 1)
