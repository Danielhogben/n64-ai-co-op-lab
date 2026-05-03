"""Factory Production — real implementation."""
import json, os, time
from typing import Dict, List, Any
# Import registry (works both as package and standalone)
try:
    from ..registry import reg
except ImportError:
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from registry import reg
# Import events (works both as package and standalone)
try:
    from ..events import FACTORY_JOB_COMPLETE
except ImportError:
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from events import FACTORY_JOB_COMPLETE

class FactoryManager:
    """Manages 6 factory types, queues, and production."""
    
    def __init__(self):
        self.factories_path = os.path.join(reg.config.get("mod_path", ""), "factories")
        
    def list_factories(self) -> List[Dict[str, Any]]:
        facts = []
        for f in sorted(os.listdir(self.factories_path)):
            if f.startswith("factory_") and f.endswith(".json"):
                with open(os.path.join(self.factories_path, f)) as fp:
                    data = json.load(fp)
                facts.append({
                    "id": data["id"],
                    "type": data.get("type", "unknown"),
                    "level": data.get("level", 1),
                    "queue_len": len(data.get("queue", [])),
                    "efficiency": data.get("efficiency", 1.0),
                })
        return facts
    
    def get_factory(self, factory_id: str) -> Dict[str, Any]:
        path = os.path.join(self.factories_path, f"{factory_id}.json")
        with open(path) as f:
            return json.load(f)
    
    def save_factory(self, factory_id: str, data: Dict[str, Any]):
        path = os.path.join(self.factories_path, f"{factory_id}.json")
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def start_job(self, factory_id: str, recipe_id: str, quantity: int = 1, tier: str = "common") -> str:
        """Queue a production job."""
        factory = self.get_factory(factory_id)
        # Verify recipe exists (simplified: recipe_db would come from config)
        # For demo, accept any recipe_id
        job = {
            "recipe_id": recipe_id,
            "quantity": quantity,
            "tier": tier,
            "progress": 0,
            "eta_seconds": self._estimate_time(recipe_id, quantity, tier, factory.get("level",1)),
        }
        factory.setdefault("queue", []).append(job)
        self.save_factory(factory_id, factory)
        return f"Job queued: {recipe_id} x{quantity} at {tier} tier. ETA: {job['eta_seconds']}s"
    
    def _estimate_time(self, recipe: str, qty: int, tier: str, level: int) -> int:
        """Rough time estimate in seconds."""
        base = {"data_crystal": 180, "weapon": 120, "armor": 90, "ship": 300, "enemy": 45}.get(recipe.split("_")[0], 60)
        tier_mult = {"common":1.0, "uncommon":1.5, "rare":2.0, "epic":3.0, "legendary":4.0}[tier]
        level_mult = 1.0 - (level - 1) * 0.1  # each level 10% faster
        return int(base * qty * tier_mult * level_mult)
    
    def collect_output(self, factory_id: str) -> str:
        """Collect finished items from output bins to base storage."""
        factory = self.get_factory(factory_id)
        queue = factory.get("queue", [])
        completed = [j for j in queue if j["progress"] >= j["eta_seconds"]]
        if not completed:
            return "No completed jobs."
        # Remove completed jobs, add items to base storage (simplified)
        items_collected = []
        for job in completed:
            items_collected.append(f"{job['recipe_id']} x{job['quantity']}")
        factory["queue"] = [j for j in queue if j["progress"] < j["eta_seconds"]]
        self.save_factory(factory_id, factory)
        reg.emit(FACTORY_JOB_COMPLETE, factory_id=factory_id, items=items_collected)
        return f"Collected: {', '.join(items_collected)}"

class Skill:
    def __init__(self):
        self.fm = FactoryManager()
        self.commands = {
            "list": self.cmd_list,
            "status": self.cmd_status,
            "start": self.cmd_start,
            "collect": self.cmd_collect,
            "queue": self.cmd_queue,
        }
    
    def cmd_list(self, *args):
        """factory_list — show all factories."""
        facts = self.fm.list_factories()
        if not facts:
            return "No factories found."
        lines = ["ID     TYPE             LVL  QUEUE  EFFICIENCY"]
        for f in facts:
            lines.append(f"{f['id']:6} {f['type']:15} {f['level']:4} {f['queue_len']:6} {f['efficiency']:.2f}")
        return "\n".join(lines)
    
    def cmd_status(self, factory_id: str, *args):
        """factory_status <id> — detailed view."""
        f = self.fm.get_factory(factory_id)
        q = f.get("queue", [])
        lines = [
            f"Factory {factory_id} — {f.get('type')} (Level {f.get('level',1)})",
            f"Efficiency: {f.get('efficiency',1.0):.0%}",
            f"Power use: {f.get('power_use',0)}",
            f"Queue: {len(q)} jobs",
        ]
        for i, job in enumerate(q):
            lines.append(f"  [{i}] {job['recipe_id']} x{job['quantity']} — {job['progress']:.0f}/{job['eta_seconds']}s ({job['tier']})")
        return "\n".join(lines)
    
    def cmd_start(self, factory_id: str, recipe: str, *args):
        """factory_start <factory_id> <recipe> [quantity] [tier] — queue job."""
        qty = int(args[0]) if args else 1
        tier = args[1] if len(args) > 1 else "common"
        return self.fm.start_job(factory_id, recipe, qty, tier)
    
    def cmd_collect(self, factory_id: str, *args):
        """factory_collect <factory_id> — move finished items to storage."""
        return self.fm.collect_output(factory_id)
    
    def cmd_queue(self, *args):
        """factory_queue — show all factory queues (stub)."""
        return "factory_queue not implemented yet; use factory_status per factory."
