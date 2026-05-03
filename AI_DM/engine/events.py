"""Event types and event data structures."""
from dataclasses import dataclass
from typing import Optional

@dataclass
class Event:
    type: str
    data: dict
    
# Event types
ZONE_ENTER = "zone.enter"
ZONE_LEAVE = "zone.leave"
ENEMY_DEATH = "enemy.death"
ITEM_PICKUP = "item.pickup"
QUEST_UPDATE = "quest.update"
QUEST_COMPLETE = "quest.complete"
LEVEL_UP = "player.levelup"
FACTION_REP_CHANGE = "faction.rep.change"
FACTORY_JOB_COMPLETE = "factory.job_complete"
BASE_BUILT = "base.built"
SHIP_MODIFIED = "ship.modified"
COMBAT_START = "combat.start"
COMBAT_END = "combat.end"
WARP_INITIATE = "warp.initiate"
WARP_COMPLETE = "warp.complete"
AI_SPEAK = "ai.speak"
POKEMON_EVOLVE = "pokemon.evolve"
PERK_UNLOCKED = "perk.unlocked"
ACHIEVEMENT_UNLOCKED = "achievement.unlocked"
ENGINE_SECOND = "engine.second"
