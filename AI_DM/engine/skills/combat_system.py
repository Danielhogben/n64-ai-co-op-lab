"""Combat System — turn-based battle engine."""
import json, os, time
from typing import Dict, List, Any
try:
    from ..registry import reg
except ImportError:
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from registry import reg
try:
    from ..events import COMBAT_START, COMBAT_END, ENEMY_DEATH, ITEM_PICKUP
except ImportError:
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from events import COMBAT_START, COMBAT_END, ENEMY_DEATH, ITEM_PICKUP

class CombatManager:
    """Handles multiple enemies, combat resolution, looting."""
    
    def __init__(self):
        self.mod_path = reg.config.get("mod_path", "")
        self.enemies_path = os.path.join(self.mod_path, "enemies", "generated")
        os.makedirs(self.enemies_path, exist_ok=True)
        self.active_enemies: Dict[str, Dict] = {}  # enemy_id -> enemy data (including 'dead', 'looted')
        self.enemy_counter = 0
        self.combat_started = False
    
    def _next_id(self, enemy_type: str) -> str:
        self.enemy_counter += 1
        return f"{enemy_type}_{self.enemy_counter}"
    
    def _load_enemy_template(self, enemy_type: str) -> Dict[str, Any]:
        """Load enemy JSON if exists, else create generic."""
        path = os.path.join(self.enemies_path, f"{enemy_type}.json")
        if os.path.exists(path):
            with open(path) as f:
                data = json.load(f)
            # Ensure keys
            data.setdefault('name', enemy_type.replace('_', ' ').title())
            data.setdefault('stats', {'health': 100, 'damage': 10, 'speed': 5})
            data.setdefault('drops', [{'item_id': 'coin', 'chance': 0.8, 'quantity': [1,3]}])
            data.setdefault('type', enemy_type)
            return data
        else:
            return {
                'id': enemy_type,
                'name': enemy_type.replace('_', ' ').title(),
                'type': enemy_type,
                'stats': {'health': 100, 'damage': 10, 'speed': 5},
                'drops': [{'item_id': 'coin', 'chance': 0.8, 'quantity': [1,3]}],
            }
    
    def spawn(self, enemy_type: str, count: int = 1) -> str:
        """Spawn count enemies of given type."""
        spawned = []
        for i in range(count):
            enemy_id = self._next_id(enemy_type)
            template = self._load_enemy_template(enemy_type)
            enemy = dict(template)
            enemy['id'] = enemy_id
            enemy['current_hp'] = enemy['stats']['health']
            enemy['dead'] = False
            enemy['looted'] = False
            self.active_enemies[enemy_id] = enemy
            spawned.append(enemy_id)
        if not self.combat_started:
            self.combat_started = True
            reg.emit(COMBAT_START, enemy_ids=spawned, zone_id=reg.player_state.get('current_zone'))
        return f"Spawned {count} x {enemy_type}: {', '.join(spawned)}"
    
    def attack(self, enemy_id: str, damage: int = 10) -> str:
        """Player attacks a specific enemy."""
        if enemy_id not in self.active_enemies:
            return f"Enemy {enemy_id} not found."
        enemy = self.active_enemies[enemy_id]
        if enemy['dead']:
            return f"Enemy {enemy_id} is already dead."
        # Apply damage with small variance
        dmg = damage + random.randint(-2, 2)
        enemy['current_hp'] -= dmg
        if enemy['current_hp'] <= 0:
            enemy['dead'] = True
            enemy['current_hp'] = 0
            # Emit death
            reg.emit(ENEMY_DEATH, enemy_id=enemy_id, enemy_type=enemy.get('type'), drops=enemy.get('drops', []))
            # Check if combat ended
            if not any(not e['dead'] for e in self.active_enemies.values()):
                self.combat_started = False
                reg.emit(COMBAT_END, result='victory')
            return f"Hit {enemy_id} for {dmg} — defeated!"
        # Enemy counterattack if alive (and maybe only if enemy is aggressive)
        enemy_dmg = max(1, enemy['stats']['damage'] + random.randint(-3, 3))
        reg.player_state['current_hp'] = max(0, reg.player_state.get('current_hp', 100) - enemy_dmg)
        if reg.player_state['current_hp'] <= 0:
            self.combat_started = False
            reg.emit(COMBAT_END, result='defeat')
            return f"Hit {enemy_id} for {dmg}. Enemy hits for {enemy_dmg}. You are incapacitated!"
        return f"Hit {enemy_id} for {dmg}. Enemy HP: {enemy['current_hp']}/{enemy['stats']['health']}. Enemy hits for {enemy_dmg}. Your HP: {reg.player_state['current_hp']}/{reg.player_state.get('max_hp',100)}"
    
    def kill(self, enemy_id: str) -> str:
        """Instantly kill a specific enemy (debug)."""
        if enemy_id not in self.active_enemies:
            return f"Enemy {enemy_id} not active."
        enemy = self.active_enemies[enemy_id]
        if enemy['dead']:
            return f"Enemy {enemy_id} already dead."
        enemy['current_hp'] = 0
        enemy['dead'] = True
        reg.emit(ENEMY_DEATH, enemy_id=enemy_id, enemy_type=enemy.get('type'), drops=enemy.get('drops', []))
        # Check combat end
        if not any(not e['dead'] for e in self.active_enemies.values()):
            self.combat_started = False
            reg.emit(COMBAT_END, result='victory')
        return f"{enemy_id} killed."
    
    def enemy_info(self, enemy_id: str) -> str:
        """Show detailed info about an enemy."""
        if enemy_id not in self.active_enemies:
            # Try to load from file (even if not active)
            for e in self.active_enemies.values():
                if e.get('id') == enemy_id:
                    enemy = e
                    break
            else:
                return f"Enemy {enemy_id} not found in active combat."
        else:
            enemy = self.active_enemies[enemy_id]
        name = enemy.get('name', enemy_id)
        stats = enemy.get('stats', {})
        drops = enemy.get('drops', [])
        status = "DEAD" if enemy['dead'] else f"HP {enemy['current_hp']}/{stats['health']}"
        lines = [
            f"Enemy: {name} ({enemy_id})",
            f"Status: {status}",
            f"Stats: HP={stats.get('health')}, DMG={stats.get('damage')}, SPD={stats.get('speed')}",
            f"Drops: {drops}",
        ]
        return "\n".join(lines)
    
    def loot(self, enemy_id: str) -> str:
        """Loot a dead enemy."""
        if enemy_id not in self.active_enemies:
            return f"Enemy {enemy_id} not found."
        enemy = self.active_enemies[enemy_id]
        if not enemy['dead']:
            return f"Enemy {enemy_id} still alive."
        if enemy.get('looted', False):
            return f"Enemy {enemy_id} already looted."
        drops = enemy.get('drops', [])
        if not drops:
            enemy['looted'] = True
            return f"No loot from {enemy_id}."
        # Add drops to player inventory
        inv = reg.player_state.setdefault('inventory', {'items': []})
        items_list = inv.setdefault('items', [])
        acquired = []
        for drop in drops:
            chance = drop.get('chance', 1.0)
            if random.random() < chance:
                qty = random.randint(drop['quantity'][0], drop['quantity'][1])
                item_id = drop['item_id']
                # find existing
                found = next((i for i in items_list if i['item_id'] == item_id), None)
                if found:
                    found['quantity'] += qty
                else:
                    items_list.append({'item_id': item_id, 'quantity': qty})
                acquired.append(f"{qty}x {item_id}")
        enemy['looted'] = True
        # Emit ITEM_PICKUP? Not automatically since it's from loot, not direct pickup. Could emit.
        reg.emit(ITEM_PICKUP, item_id="loot", quantity=len(acquired), source=enemy_id)
        return f"Looted {enemy_id}: {', '.join(acquired) if acquired else 'nothing'}"
    
    def status(self) -> str:
        if not self.active_enemies:
            return "No active enemies."
        lines = []
        for eid, e in self.active_enemies.items():
            if not e['dead']:
                lines.append(f"{eid}: {e['current_hp']}/{e['stats']['health']} HP")
        return "Active enemies:\n" + "\n".join(lines) if lines else "No living enemies."

class Skill:
    def __init__(self):
        self.cm = CombatManager()
        self.commands = {
            "spawn": self.cmd_spawn,
            "kill": self.cmd_kill,
            "enemy_info": self.cmd_enemy_info,
            "loot": self.cmd_loot,
            "attack": self.cmd_attack,
            "flee": self.cmd_flee,
            "status": self.cmd_status,
        }
    
    def cmd_spawn(self, enemy_type: str, *args):
        """spawn <enemy_type> [count] — spawn enemies."""
        count = int(args[0]) if args else 1
        return self.cm.spawn(enemy_type, count)
    
    def cmd_kill(self, enemy_id: str, *args):
        """kill <enemy_id> — instantly kill that enemy."""
        return self.cm.kill(enemy_id)
    
    def cmd_enemy_info(self, enemy_id: str, *args):
        """enemy_info <enemy_id> — show enemy stats."""
        return self.cm.enemy_info(enemy_id)
    
    def cmd_loot(self, enemy_id: str, *args):
        """loot <enemy_id> — loot a dead enemy."""
        return self.cm.loot(enemy_id)
    
    def cmd_attack(self, enemy_id: str = None, *args):
        """attack [enemy_id] [damage] — attack an enemy."""
        if not self.cm.active_enemies:
            return "No enemies to attack."
        if not enemy_id:
            # Attack first living enemy
            for eid, e in self.cm.active_enemies.items():
                if not e['dead']:
                    enemy_id = eid
                    break
            if not enemy_id:
                return "No living enemies."
        dmg = int(args[0]) if args else 10
        return self.cm.attack(enemy_id, dmg)
    
    def cmd_flee(self, *args):
        """flee — attempt to escape combat."""
        if not self.cm.combat_started:
            return "Not in combat."
        success = random.random() < 0.7
        if success:
            self.cm.active_enemies.clear()
            self.cm.combat_started = False
            reg.emit(COMBAT_END, result='fled')
            return "Fled successfully."
        return "Failed to escape!"
    
    def cmd_status(self, *args):
        """combat_status — show combat state."""
        return self.cm.status()
