"""Pokemon System — capture, train, and evolve space creatures."""
import json, os, random
from typing import Dict, List, Any
try:
    from ..registry import reg
except ImportError:
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from registry import reg
try:
    from ..events import POKEMON_EVOLVE
except ImportError:
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from events import POKEMON_EVOLVE

class PokemonManager:
    """Manages the player's collection of space-faring creatures."""
    
    def __init__(self):
        self.state = reg.player_state
        self.pokedex = self.state.setdefault("pokemon", [])
    
    def list_pokemon(self) -> str:
        if not self.pokedex:
            return "No Pokemon in your party."
        lines = ["Your Pokemon:"]
        for i, p in enumerate(self.pokedex):
            lines.append(f"  [{i}] {p['name']} (Lv.{p['level']} {p['species']}) — HP: {p.get('hp',100)}/{p.get('max_hp',100)}")
        return "\n".join(lines)
    
    def capture(self, species: str, name: str = None) -> str:
        p = {
            "species": species,
            "name": name or species,
            "level": random.randint(1, 5),
            "xp": 0,
            "hp": 100,
            "max_hp": 100
        }
        self.pokedex.append(p)
        return f"Caught {p['name']} the {species}!"
    
    def evolve(self, index: int) -> str:
        if index < 0 or index >= len(self.pokedex):
            return f"Invalid index: {index}. You have {len(self.pokedex)} Pokemon."
        p = self.pokedex[index]
        old_species = p['species']
        # Simple evolution logic: prefix with 'Mega'
        if old_species.startswith("Mega "):
            new_species = f"Ultimate {old_species[5:]}"
        else:
            new_species = f"Mega {old_species}"
            
        p['species'] = new_species
        p['level'] += 5
        p['max_hp'] += 50
        p['hp'] = p['max_hp']
        
        reg.emit(POKEMON_EVOLVE, pokemon_id=index, old_species=old_species, new_species=new_species)
        return f"✨ {p['name']} evolved from {old_species} to {new_species}! ✨"

    def heal_all(self) -> str:
        for p in self.pokedex:
            p['hp'] = p.get('max_hp', 100)
        return "All Pokemon in your party have been healed."

class Skill:
    def __init__(self):
        self.pm = PokemonManager()
        self.commands = {
            "list": self.cmd_list,
            "capture": self.cmd_capture,
            "evolve": self.cmd_evolve,
            "heal": self.cmd_heal,
            "status": self.cmd_list,
        }
    
    def cmd_list(self, *args):
        """pokemon list — show your team."""
        return self.pm.list_pokemon()
    
    def cmd_capture(self, species: str, name: str = None, *args):
        """pokemon capture <species> [name] — catch a creature."""
        return self.pm.capture(species, name)
    
    def cmd_evolve(self, index: str, *args):
        """pokemon evolve <index> — trigger evolution."""
        try:
            idx = int(index)
        except ValueError:
            return f"Invalid index: {index}"
        return self.pm.evolve(idx)
    
    def cmd_heal(self, *args):
        """pokemon heal — restore all party HP."""
        return self.pm.heal_all()
