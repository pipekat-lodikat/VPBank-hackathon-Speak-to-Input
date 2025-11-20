#!/usr/bin/env python3
"""
Performance Benchmark Tool
Measure and report performance metrics
"""

import time
import asyncio
import statistics
import sys
from typing import List, Dict, Any, Callable
from datetime import datetime

# Add src to path
sys.path.insert(0, '.')

from src.utils.date_parser import parse_vietnamese_date
from src.utils.field_mapper import map_vietnamese_to_english, FieldMapper
from src.utils.pronoun_resolver import get_resolver, resolve_pronouns


class PerformanceBenchmark:
    """Performance benchmarking tool"""
    
    def __init__(self):
        self.results = {}
    
    def benchmark(
        self,
        name: str,
        func: Callable,
        iterations: int = 1000,
        warmup: int = 100
    ) -> Dict[str, Any]:
        """
        Benchmark a function
        
        Args:
            name: Benchmark name
            func: Function to benchmark
            iterations: Number of iterations
            warmup: Warmup iterations
            
        Returns:
            Benchmark results
        """
        print(f"\n🔥 Warming up {name}...")
        for _ in range(warmup):
            func()
        
        print(f"⚡ Benchmarking {name} ({iterations} iterations)...")
        
        times = []
        for _ in range(iterations):
            start = time.perf_counter()
            func()
            elapsed = time.perf_counter() - start
            times.append(elapsed * 1000)  # Convert to ms
        
        results = {
            "name": name,
            "iterations": iterations,
            "total_time_ms": sum(times),
            "mean_ms": statistics.mean(times),
            "median_ms": statistics.median(times),
            "min_ms": min(times),
            "max_ms": max(times),
            "stdev_ms": statistics.stdev(times) if len(times) > 1 else 0,
            "p95_ms": sorted(times)[int(len(times) * 0.95)],
            "p99_ms": sorted(times)[int(len(times) * 0.99)],
        }
        
        self.results[name] = results
        return results
    
    async def benchmark_async(
        self,
        name: str,
        func: Callable,
        iterations: int = 1000,
        warmup: int = 100
    ) -> Dict[str, Any]:
        """Benchmark async function"""
        print(f"\n🔥 Warming up {name}...")
        for _ in range(warmup):
            await func()
        
        print(f"⚡ Benchmarking {name} ({iterations} iterations)...")
        
        times = []
        for _ in range(iterations):
            start = time.perf_counter()
            await func()
            elapsed = time.perf_counter() - start
            times.append(elapsed * 1000)
        
        results = {
            "name": name,
            "iterations": iterations,
            "total_time_ms": sum(times),
            "mean_ms": statistics.mean(times),
            "median_ms": statistics.median(times),
            "min_ms": min(times),
            "max_ms": max(times),
            "stdev_ms": statistics.stdev(times) if len(times) > 1 else 0,
            "p95_ms": sorted(times)[int(len(times) * 0.95)],
            "p99_ms": sorted(times)[int(len(times) * 0.99)],
        }
        
        self.results[name] = results
        return results
    
    def print_results(self, results: Dict[str, Any]):
        """Print benchmark results"""
        print(f"\n{'='*60}")
        print(f"  {results['name']}")
        print(f"{'='*60}")
        print(f"Iterations:    {results['iterations']:,}")
        print(f"Total Time:    {results['total_time_ms']:.2f} ms")
        print(f"Mean:          {results['mean_ms']:.4f} ms")
        print(f"Median:        {results['median_ms']:.4f} ms")
        print(f"Min:           {results['min_ms']:.4f} ms")
        print(f"Max:           {results['max_ms']:.4f} ms")
        print(f"Std Dev:       {results['stdev_ms']:.4f} ms")
        print(f"P95:           {results['p95_ms']:.4f} ms")
        print(f"P99:           {results['p99_ms']:.4f} ms")
        print(f"Throughput:    {1000/results['mean_ms']:.0f} ops/sec")
    
    def print_summary(self):
        """Print summary of all benchmarks"""
        print(f"\n{'='*60}")
        print(f"  BENCHMARK SUMMARY")
        print(f"{'='*60}\n")
        
        print(f"{'Benchmark':<40} {'Mean (ms)':<12} {'P95 (ms)':<12} {'Ops/sec':<12}")
        print(f"{'-'*76}")
        
        for name, results in self.results.items():
            mean = results['mean_ms']
            p95 = results['p95_ms']
            ops = 1000 / mean
            print(f"{name:<40} {mean:<12.4f} {p95:<12.4f} {ops:<12.0f}")
    
    def export_results(self, filename: str = "benchmark_results.json"):
        """Export results to JSON"""
        import json
        
        with open(filename, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "results": self.results
            }, f, indent=2)
        
        print(f"\n✅ Results exported to {filename}")


def benchmark_date_parser(bench: PerformanceBenchmark):
    """Benchmark date parser"""
    print("\n" + "="*60)
    print("  DATE PARSER BENCHMARKS")
    print("="*60)
    
    # Test 1: Simple slash format
    results = bench.benchmark(
        "Date Parser - Slash Format (15/03/1990)",
        lambda: parse_vietnamese_date("15/03/1990"),
        iterations=10000
    )
    bench.print_results(results)
    
    # Test 2: Vietnamese format
    results = bench.benchmark(
        "Date Parser - Vietnamese Format",
        lambda: parse_vietnamese_date("15 tháng 3 năm 1990"),
        iterations=10000
    )
    bench.print_results(results)
    
    # Test 3: Multiple formats
    dates = [
        "15/03/1990",
        "15-03-1990",
        "15.03.1990",
        "15 tháng 3 năm 1990",
        "15/3/90",
    ]
    
    def parse_multiple():
        for date in dates:
            parse_vietnamese_date(date)
    
    results = bench.benchmark(
        "Date Parser - Multiple Formats (5 dates)",
        parse_multiple,
        iterations=2000
    )
    bench.print_results(results)


def benchmark_field_mapper(bench: PerformanceBenchmark):
    """Benchmark field mapper"""
    print("\n" + "="*60)
    print("  FIELD MAPPER BENCHMARKS")
    print("="*60)
    
    # Test 1: Exact match
    results = bench.benchmark(
        "Field Mapper - Exact Match",
        lambda: map_vietnamese_to_english("họ và tên"),
        iterations=10000
    )
    bench.print_results(results)
    
    # Test 2: Fuzzy match
    results = bench.benchmark(
        "Field Mapper - Fuzzy Match",
        lambda: map_vietnamese_to_english("họ tên"),
        iterations=10000
    )
    bench.print_results(results)
    
    # Test 3: Best match selection
    available = ["fullName", "phoneNumber", "email", "dateOfBirth"]
    
    results = bench.benchmark(
        "Field Mapper - Best Match Selection",
        lambda: FieldMapper.get_best_match("họ và tên", available),
        iterations=10000
    )
    bench.print_results(results)
    
    # Test 4: Multiple fields
    fields = ["họ và tên", "số điện thoại", "email", "ngày sinh", "địa chỉ"]
    
    def map_multiple():
        for field in fields:
            map_vietnamese_to_english(field)
    
    results = bench.benchmark(
        "Field Mapper - Multiple Fields (5 fields)",
        map_multiple,
        iterations=2000
    )
    bench.print_results(results)


def benchmark_pronoun_resolver(bench: PerformanceBenchmark):
    """Benchmark pronoun resolver"""
    print("\n" + "="*60)
    print("  PRONOUN RESOLVER BENCHMARKS")
    print("="*60)
    
    resolver = get_resolver()
    resolver.clear_context()
    resolver.update_person("Nguyễn Văn An", "male")
    
    # Test 1: Simple pronoun resolution
    results = bench.benchmark(
        "Pronoun Resolver - Simple Resolution",
        lambda: resolver.resolve_pronoun("Anh ấy sinh năm 1990"),
        iterations=10000
    )
    bench.print_results(results)
    
    # Test 2: Extract and update
    results = bench.benchmark(
        "Pronoun Resolver - Extract and Update",
        lambda: resolver.extract_and_update("Tên là Nguyễn Văn An"),
        iterations=10000
    )
    bench.print_results(results)
    
    # Test 3: Multiple pronouns
    texts = [
        "Anh ấy sinh năm 1990",
        "Ông ấy làm việc tại VPBank",
        "Anh ta có thu nhập cao",
    ]
    
    def resolve_multiple():
        for text in texts:
            resolver.resolve_pronoun(text)
    
    results = bench.benchmark(
        "Pronoun Resolver - Multiple Pronouns (3 texts)",
        resolve_multiple,
        iterations=3000
    )
    bench.print_results(results)


def benchmark_integrated_workflow(bench: PerformanceBenchmark):
    """Benchmark integrated workflow"""
    print("\n" + "="*60)
    print("  INTEGRATED WORKFLOW BENCHMARKS")
    print("="*60)
    
    resolver = get_resolver()
    
    # Complete workflow
    def complete_workflow():
        resolver.clear_context()
        
        # Step 1: Extract name
        resolver.extract_and_update("Tên là Nguyễn Văn An")
        
        # Step 2: Resolve pronoun and parse date
        text = resolver.resolve_pronoun("Anh ấy sinh ngày 15 tháng 3 năm 1990")
        date = parse_vietnamese_date("15 tháng 3 năm 1990")
        
        # Step 3: Map field
        field = map_vietnamese_to_english("ngày sinh")
        
        # Step 4: Map phone field
        phone_field = map_vietnamese_to_english("số điện thoại")
    
    results = bench.benchmark(
        "Integrated Workflow - Complete Flow",
        complete_workflow,
        iterations=1000
    )
    bench.print_results(results)


async def benchmark_concurrent_operations(bench: PerformanceBenchmark):
    """Benchmark concurrent operations"""
    print("\n" + "="*60)
    print("  CONCURRENT OPERATIONS BENCHMARKS")
    print("="*60)
    
    # Concurrent date parsing
    async def concurrent_date_parsing():
        dates = ["15/03/1990"] * 100
        tasks = [asyncio.create_task(asyncio.to_thread(parse_vietnamese_date, date)) for date in dates]
        await asyncio.gather(*tasks)
    
    results = await bench.benchmark_async(
        "Concurrent - Date Parsing (100 concurrent)",
        concurrent_date_parsing,
        iterations=100,
        warmup=10
    )
    bench.print_results(results)
    
    # Concurrent field mapping
    async def concurrent_field_mapping():
        fields = ["họ và tên"] * 100
        tasks = [asyncio.create_task(asyncio.to_thread(map_vietnamese_to_english, field)) for field in fields]
        await asyncio.gather(*tasks)
    
    results = await bench.benchmark_async(
        "Concurrent - Field Mapping (100 concurrent)",
        concurrent_field_mapping,
        iterations=100,
        warmup=10
    )
    bench.print_results(results)


def benchmark_memory_usage():
    """Benchmark memory usage"""
    import tracemalloc
    
    print("\n" + "="*60)
    print("  MEMORY USAGE BENCHMARKS")
    print("="*60)
    
    # Date parser memory
    tracemalloc.start()
    for _ in range(1000):
        parse_vietnamese_date("15/03/1990")
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    print(f"\nDate Parser (1000 operations):")
    print(f"  Current: {current / 1024:.2f} KB")
    print(f"  Peak:    {peak / 1024:.2f} KB")
    
    # Field mapper memory
    tracemalloc.start()
    for _ in range(1000):
        map_vietnamese_to_english("họ và tên")
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    print(f"\nField Mapper (1000 operations):")
    print(f"  Current: {current / 1024:.2f} KB")
    print(f"  Peak:    {peak / 1024:.2f} KB")
    
    # Pronoun resolver memory
    resolver = get_resolver()
    tracemalloc.start()
    for _ in range(1000):
        resolver.resolve_pronoun("Anh ấy sinh năm 1990")
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    print(f"\nPronoun Resolver (1000 operations):")
    print(f"  Current: {current / 1024:.2f} KB")
    print(f"  Peak:    {peak / 1024:.2f} KB")


async def main():
    """Main benchmark function"""
    print("\n" + "="*60)
    print("  🚀 PERFORMANCE BENCHMARK SUITE")
    print("  VPBank Voice Agent v2.0")
    print("="*60)
    
    bench = PerformanceBenchmark()
    
    try:
        # Run benchmarks
        benchmark_date_parser(bench)
        benchmark_field_mapper(bench)
        benchmark_pronoun_resolver(bench)
        benchmark_integrated_workflow(bench)
        await benchmark_concurrent_operations(bench)
        benchmark_memory_usage()
        
        # Print summary
        bench.print_summary()
        
        # Export results
        bench.export_results()
        
        print("\n" + "="*60)
        print("  ✅ BENCHMARK COMPLETE")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Benchmark error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
