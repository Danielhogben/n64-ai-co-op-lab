import json
import random
import os
from pathlib import Path
from typing import Dict, List, Any

# Try to import constants from pokemon_data.py
try:
    from pokemon_data import POKEMON_REGIONS, POKEMON_STORY_ARCHETYPES
except ImportError:
    # Fallback if the file is missing
    POKEMON_REGIONS = []
    POKEMON_STORY_ARCHETYPES = []

# Global path for mod data
MOD_PATH = Path("~/HylianModding/AI_DM/engine/content/pokemon").expanduser()

class PokemonRegionGenerator:
    """Generates all 9 Pokemon regions with uniquely random storylines."""
    
    def __init__(self):
        self.regions = POKEMON_REGIONS
        self.story_templates = POKEMON_STORY_ARCHETYPES
        
    def generate_region(self, region_idx: int, rom_fragment: str = None) -> Dict[str, Any]:
        """Build full region data for region #idx."""
        region_template = self.regions[region_idx]
        region_id = region_template["id"]
        
        # Random seeds so stories differ between regions
        rng = random.Random(region_id + "v2")  # deterministic per region
        
        # Pick story archetype
        archetype = rng.choice(self.story_templates)
        
        # Fill in archetype placeholders
        fills = {
            "villain": rng.choice(["Aqua", "Magma", "Galactic", "Neo", "Cyrus", "Lysandre", "Guzma", "Rose", "Geets", "Sada", "Turo"]),
            "legend": self._random_legend(rng, region_idx),
            "goal": rng.choice(["awaken", "control", "destroy", "reshape", "dominate", "flood", "freeze", "burn", "rule"]),
            "disease": rng.choice(["Petrification", "Freeze", "Burn", "Poison", "Sleep", "Confusion", "Curse"]),
            "artifact": rng.choice(["Time Flower", "Red Chain", "Adamant Orb", "Lustrous Globe", "Griseous Orb", "Poké Ball seal", "Dynamax Band"]),
            "guardian": rng.choice(["Regigigas", "Regice", "Registeel", "Regieleki", "Regidrago", "Arceus", "Rayquaza", "Groudon", "Kyogre"]),
            "cult": rng.choice(["Team Skull", "Team Yell", "Team Star", "Team Plasma", "Team Flare", "Team Magma", "Team Aqua", "Team Galactic", "Team Skiffle"]),
            "purge": rng.choice(["erase", "remove", "exterminate", "banish", "purify", "replace"]),
            "type": rng.choice(["Fire", "Water", "Grass", "Electric", "Psychic", "Ghost", "Dragon", "Dark", "Fairy"]),
            "oak": rng.choice(["Oak", "Elm", "Birch", "Rowan", "Juniper", "Sycamore", "Kukui", "Magnolia", "Sada", "Turo"]),
            "ruins": rng.choice(["Silph Co.", "Pokemon Mansion", "New Mauville", "Stark Mountain", "Turnback Cave", "Ultra Space"]),
            "chosen_one": rng.choice(["Aura Guardian", "Time Traveler", "Dragon Whisperer", "Sky Warrior", "Void Walker", "Light of Kalos"]),
            "mythical": rng.choice(["Mew", "Celebi", "Jirachi", "Deoxys", "Shaymin", "Arceus", "Victini", "Keldeo", "Meloetta"]),
            "malfunction": rng.choice(["become aggressive", "lose memories", "shrink", "duplicate", "speak human language", "change type"]),
            "facility": rng.choice(["S.S. Anne", "Pokemon Lab", "Battle Frontier", "Pokemon League", "Mansion Lab"]),
        }
        
        story = archetype.format(**fills)
        
        # Generate quest chain (6–10 main story quests)
        quests = self._generate_quest_chain(region_id, rng)
        
        # Gyms: 8 gyms + champion
        gyms = self._generate_gyms(region_id, rng)
        
        # Wild Pokémon pool: blend this region + random other region
        other_region = rng.choice([r for r in self.regions if r["id"] != region_id])
        wild_dex = self._blend_pokedex(region_template, other_region, rng)
        
        return {
            "region_id": region_id,
            "name": region_template["name"],
            "generation": region_template["generation"],
            "dex_count": region_template["dex"],
            "starters": region_template["starter_trio"],
            "story_archetype": archetype,
            "story_filled": fills,
            "story_summary": story,
            "quests": quests,
            "gyms": gyms,
            "wild_pokemon_pool": wild_dex,
            "legends_available": self._legendaries_for_region(region_template, rng),
            "regional_variant": rng.choice([True, False]),
            "dynamax_enabled": region_idx >= 7,  # Galar+
        }
    
    def _random_legend(self, rng, region_idx: int) -> str:
        legends = {
            0: ["Mewtwo", "Mew", " Articuno", "Zapdos", "Moltres"],
            1: ["Raikou", "Entei", "Suicune"],
            2: ["Kyogre", "Groudon", "Rayquaza", "Deoxys"],
            3: ["Dialga", "Palkia", "Giratina", "Arceus"],
            4: ["Reshiram", "Zekrom", "Kyurem"],
            5: ["Xerneas", "Yveltal", "Zygarde"],
            6: ["Solgaleo", "Lunala", "Necrozma", "Tapu Koko"],
            7: ["Eternatus", "Cinderace", "Rillaboom", "Inteleon"],
            8: ["Miraidon", "Koraidon", "Terapagos", "Arceus"],
        }
        pool = legends.get(region_idx % 9, legends[0])
        return rng.choice(pool)
    
    def _generate_quest_chain(self, region_id: str, rng) -> List[Dict]:
        """Generate 6–12 main story quests for this region."""
        quest_count = rng.randint(6, 12)
        templates = [
            "Start your journey in {town}, choose your starter.",
            "Battle your rival {rival} for the first time.",
            "Obtain {badge_count} Gym Badges by defeating leaders.",
            "Team {villain} attacks the {location}! Stop them.",
            "Discover the legendary {legend} in the {ruins}.",
            "Uncover the truth about the {artifact}.",
            "Final battle against Team {villain} at their {base}.",
            "Challenge the Elite Four and become Champion.",
            "Post-game: Battle the {champion} in an ultimate rematch.",
        ]
        quests = []
        for i in range(quest_count):
            tmpl = rng.choice(templates)
            quest = {
                "id": f"{region_id}_q{i+1:02d}",
                "title": tmpl.format(
                    town=f"Town_{i+1}",
                    rival=rng.choice(["Blue", "Silver", "May", "Brendan", "Barry", "Hilbert", "Calem", "Hau", "Kieran"]),
                    badge_count=min(i+1, 8),
                    villain=rng.choice(["Aqua", "Magma", "Galactic", "Plasma", "Flare", "Skull", "Star", "Yell"]),
                    location=f"Route_{i*3+1}",
                    legend=self._random_legend(rng, random.randint(0,8)),
                    ruins=rng.choice(["Cave", "Temple", "Tower", "Shrine", "Lab"]),
                    artifact=rng.choice(["Stone", "Orb", "Plate", "Gem", "Flute"]),
                    base=rng.choice(["Hideout", "Base", "Airship", "Submarine", "Tower"]),
                    champion=rng.choice(["Cynthia", "Steven", "Alder", "Cheren", "Diantha", "Lance", "Leon", "Geets"]),
                ),
                "objectives": self._gen_objectives(tmpl),
                "rewards": {"xp": 1000*(i+1), "credits": 500*i, "item": rng.choice(["Potion","Ether","Rare Candy","TM"])},
                "required_level": 5 + i*3,
            }
            quests.append(quest)
        return quests
    
    def _gen_objectives(self, tmpl: str) -> List[str]:
        if "starter" in tmpl.lower(): return ["Choose starter Pokémon"]
        if "rival" in tmpl.lower(): return ["Battle rival", "Defeat rival's team"]
        if "Gym Badges" in tmpl: return [f"Earn {random.randint(1,8)} Gym Badges"]
        if "Team" in tmpl and "attack" in tmpl: return ["Defeat grunts", "Rescue civilians", "Find the hideout entrance"]
        if "legendary" in tmpl.lower(): return ["Solve the puzzle", "Battle the legendary", "Capture/defeat"]
        if "artifact" in tmpl.lower(): return ["Collect fragments", "Assemble the artifact", "Use it"]
        if "Elite Four" in tmpl: return ["Win all 4 battles", "Battle Champion", "Claim title"]
        return ["Explore the area", "Talk to NPCs", "Complete tasks"]
    
    def _generate_gyms(self, region_id: str, rng) -> List[Dict]:
        gyms = []
        types = ["Normal","Fighting","Flying","Poison","Ground","Rock","Bug","Ghost","Steel","Fire","Water","Grass","Electric","Psychic","Ice","Dragon","Dark","Fairy"]
        rng.shuffle(types)
        for i in range(8):
            gyms.append({
                "gym_id": f"{region_id}_gym_{i+1}",
                "leader": rng.choice(["Brock","Misty","Giovanni","Blaine","Sabrina","Koga","Erika","Janine","Falkner","Bugsy","Whitney","Morty","Chuck","Jasmine","Pryce","Clair","Roxanne","Brawly","Wattson","Flannery","Norman","Tate&Liza","Wallace","Juan","Gardenia","Maylene","Crasher Wake","Fantina","Byron","Candice","Burgh","Elesa","Clay","Skyla","Drayden","Marlon","Viola","Grant","Ramos","Clem","Olympia","Shane"]),
                "type": types[i % len(types)],
                "level_range": [10 + i*5, 15 + i*5],
                "reward_item": f"TM{types[i % len(types)][:2].upper()}{i+1:02d}",
                "special_mechanic": rng.choice(["double battles","rotation","triple battles","inverse battles","weather","terrain"]),
            })
        return gyms
    
    def _blend_pokedex(self, region_a: Dict, region_b: Dict, rng) -> List[Dict]:
        """Create hybrid Pokémon pool (70% from current region, 30% from another)."""
        # Simulate: return list of dex entries with species IDs
        pool = []
        # Current region species: simulate 60–120 species
        base_count = region_a["dex"]
        for i in range(1, base_count + 1):
            species_id = (region_a["generation"] - 1) * 100 + i
            pool.append({"species_id": species_id, "name": f"SPECIES_{species_id}", "region_origin": region_a["id"]})
        # Add some from other region
        foreign_count = int(base_count * 0.3)
        for i in range(foreign_count):
            species_id = (region_b["generation"] - 1) * 100 + (rng.randint(1, region_b["dex"]))
            pool.append({"species_id": species_id, "name": f"SPECIES_{species_id}_exotic", "region_origin": region_b["id"], "exotic": True})
        return pool
    
    def _legendaries_for_region(self, region: Dict, rng) -> List[Dict]:
        """Identify legendaries available in this region's storyline."""
        # Simplified: each region gets its box legendary + 2 others
        box_leg = self._random_legend(rng, region["generation"]-1)
        others = [self._random_legend(rng, random.randint(0,8)) for _ in range(2)]
        return [{"name": box_leg, "role": "box"}, *[{"name": o, "role": "side"} for o in others]]

class PokemonRegionSkill:
    """Skill plugin: `pokerun generate_all_regions` creates all 9 regions."""
    
    def __init__(self):
        self.generator = PokemonRegionGenerator()
        self.out_dir = MOD_PATH / "pokemon_regions"
        self.out_dir.mkdir(parents=True, exist_ok=True)
        
    def generate_all(self, overwrite: bool = False) -> str:
        all_data = {}
        for i, region_template in enumerate(POKEMON_REGIONS):
            region_id = region_template["id"]
            out_file = self.out_dir / f"{region_id}.json"
            if out_file.exists() and not overwrite:
                all_data[region_id] = json.loads(out_file.read_text())
                print(f"  [pokemon] {region_id}: already exists (use --overwrite)")
            else:
                data = self.generator.generate_region(i)
                out_file.write_text(json.dumps(data, indent=2))
                all_data[region_id] = data
                print(f"  [pokemon] {region_id}: OK — {len(data['quests'])} quests, {len(data['gyms'])} gyms, {len(data['wild_pokemon_pool'])} species")
        # Generate master index
        index = {
            "regions": list(all_data.keys()),
            "total_regions": len(all_data),
            "generated_at": str(Path().cwd()),
        }
        (self.out_dir / "index.json").write_text(json.dumps(index, indent=2))
        return f"Generated {len(all_data)} Pokemon regions in {self.out_dir}"
    
    def get_story_summary(self, region_id: str) -> str:
        path = self.out_dir / f"{region_id}.json"
        if not path.exists():
            return f"Region {region_id} not generated. Run 'pokerun generate_all_regions' first."
        data = json.loads(path.read_text())
        lines = [
            f"=== {data['name']} ===",
            data["story_summary"],
            f"Starters: {', '.join(data['starters'])}",
            f"Gyms: {', '.join(g['leader']+' ('+g['type']+')' for g in data['gyms'][:3])}... ({len(data['gyms'])} total)",
            f"Wild Pokémon pool: {len(data['wild_pokemon_pool'])} species",
            f"Legendaries: {', '.join(l['name'] for l in data['legends_available'])}",
        ]
        return "\n".join(lines)

# Quick test
if __name__ == "__main__":
    gen = PokemonRegionGenerator()
    region = gen.generate_region(0)  # Kanto
    print(json.dumps(region, indent=2)[:800])
    print("\n\n--- Summary ---")
    pskill = PokemonRegionSkill()
    print(pskill.get_story_summary("kanto"))
