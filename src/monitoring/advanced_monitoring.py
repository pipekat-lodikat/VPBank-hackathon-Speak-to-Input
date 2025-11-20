"""
Advanced Monitoring System
- Real-time metrics tracking
- Performance monitoring
- Error tracking
- Alerting
"""

import time
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import deque
from loguru import logger
import boto3


class MetricsCollector:
    """Collect and track metrics"""
    
    def __init__(self, window_size: int = 1000):
        self.window_size = window_size
        self.metrics = {
            "response_times": deque(maxlen=window_size),
            "error_counts": deque(maxlen=window_size),
            "cache_hits": deque(maxlen=window_size),
            "cache_misses": deque(maxlen=window_size),
        }
        self.counters = {
            "total_requests": 0,
            "total_errors": 0,
            "total_cache_hits": 0,
            "total_cache_misses": 0,
        }

    
    def record_response_time(self, duration_ms: float):
        """Record response time"""
        self.metrics["response_times"].append(duration_ms)
        self.counters["total_requests"] += 1
    
    def record_error(self):
        """Record error"""
        self.metrics["error_counts"].append(1)
        self.counters["total_errors"] += 1
    
    def record_cache_hit(self):
        """Record cache hit"""
        self.metrics["cache_hits"].append(1)
        self.counters["total_cache_hits"] += 1
    
    def record_cache_miss(self):
        """Record cache miss"""
        self.metrics["cache_misses"].append(1)
        self.counters["total_cache_misses"] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current statistics"""
        response_times = list(self.metrics["response_times"])
        
        if not response_times:
            return {"error": "No data"}
        
        sorted_times = sorted(response_times)
        
        return {
            "response_time": {
                "mean": sum(response_times) / len(response_times),
                "median": sorted_times[len(sorted_times) // 2],
                "p95": sorted_times[int(len(sorted_times) * 0.95)],
                "p99": sorted_times[int(len(sorted_times) * 0.99)],
                "min": min(response_times),
                "max": max(response_times),
            },
            "error_rate": self.counters["total_errors"] / max(self.counters["total_requests"], 1),
            "cache_hit_rate": self.counters["total_cache_hits"] / max(
                self.counters["total_cache_hits"] + self.counters["total_cache_misses"], 1
            ),
            "total_requests": self.counters["total_requests"],
            "total_errors": self.counters["total_errors"],
        }


class AlertManager:
    """Manage alerts and notifications"""
    
    def __init__(self):
        self.alerts = []
        self.thresholds = {
            "error_rate": 0.05,  # 5%
            "response_time_p95": 5000,  # 5s
            "cache_hit_rate": 0.80,  # 80%
        }
    
    def check_thresholds(self, stats: Dict[str, Any]) -> List[str]:
        """Check if any thresholds are exceeded"""
        alerts = []
        
        # Check error rate
        if stats.get("error_rate", 0) > self.thresholds["error_rate"]:
            alerts.append(f"High error rate: {stats['error_rate']:.2%}")
        
        # Check response time
        rt = stats.get("response_time", {})
        if rt.get("p95", 0) > self.thresholds["response_time_p95"]:
            alerts.append(f"Slow response time (P95): {rt['p95']:.2f}ms")
        
        # Check cache hit rate
        if stats.get("cache_hit_rate", 1) < self.thresholds["cache_hit_rate"]:
            alerts.append(f"Low cache hit rate: {stats['cache_hit_rate']:.2%}")
        
        return alerts


# Global instances
metrics_collector = MetricsCollector()
alert_manager = AlertManager()
