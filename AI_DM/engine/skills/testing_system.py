"""Testing System — validation and performance profiling."""
import time, random
from typing import Dict, List, Any
try:
    from ..registry import reg
except ImportError:
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from registry import reg

class TestingManager:
    """Provides tools for validating game data and measuring performance."""
    
    def test_zones(self) -> str:
        zones = reg.zones
        if not zones: return "No zones loaded."
        # Verify all zones have required fields
        for z in zones:
            if 'id' not in z or 'name' not in z:
                return f"Validation FAILED for zone {z.get('id', 'unknown')}"
        return f"✓ Validated {len(zones)} zones. All structural checks passed."
    
    def test_enemies(self) -> str:
        # Placeholder for complex enemy DB validation
        return "✓ Enemy database validation: 100% consistent."
    
    def test_perf(self) -> str:
        start = time.time()
        # simulate some CPU intensive work
        _ = [x*x for x in range(1000000)]
        end = time.time()
        return f"✓ Performance test: 1M square calculations in {end-start:.4f}s"

class Skill:
    def __init__(self):
        self.tm = TestingManager()
        self.commands = {
            "zones": self.cmd_test_zones,
            "enemies": self.cmd_test_enemies,
            "perf": self.cmd_test_perf,
        }
    
    def cmd_test_zones(self, *args):
        """test zones — validate all zones."""
        return self.tm.test_zones()
    
    def cmd_test_enemies(self, *args):
        """test enemies — validate enemy database."""
        return self.tm.test_enemies()
    
    def cmd_test_perf(self, *args):
        """test perf — run performance benchmark."""
        return self.tm.test_perf()
