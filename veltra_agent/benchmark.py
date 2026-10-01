import time
import subprocess
import json
import sys
from pathlib import Path

def run_benchmark(iterations: int = 50):
    print(f"[veltra-benchmark] Starting latency tests ({iterations} iterations)...")
    
    # Test target command
    test_cmd = ["python3", "-m", "veltra_agent.cli", "run", "--", "echo", "benchmark_ping"]
    
    latencies = []
    
    for i in range(iterations):
        start_time = time.perf_counter()
        result = subprocess.run(
            test_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        end_time = time.perf_counter()
        
        if result.returncode != 0:
            print(f"[veltra-benchmark] Error during benchmark iteration {i}: {result.stderr}", file=sys.stderr)
            return
            
        latency_ms = (end_time - start_time) * 1000
        latencies.append(latency_ms)

    avg_latency = sum(latencies) / len(latencies)
    min_latency = min(latencies)
    max_latency = max(latencies)

    print("\n--- Benchmark Results ---")
    print(f"Total Iterations : {iterations}")
    print(f"Average Overhead : {avg_latency:.2f} ms")
    print(f"Min Overhead     : {min_latency:.2f} ms")
    print(f"Max Overhead     : {max_latency:.2f} ms")
    print("-------------------------\n")

    benchmark_data = {
        "iterations": iterations,
        "avg_overhead_ms": round(avg_latency, 2),
        "min_overhead_ms": round(min_latency, 2),
        "max_overhead_ms": round(max_latency, 2)
    }

    with open("veltra_benchmark.json", "w", encoding="utf-8") as f:
        json.dump(benchmark_data, f, indent=4)
        
    print("[veltra-benchmark] Metrics exported to 'veltra_benchmark.json'")

if __name__ == "__main__":
    run_benchmark()
