"""Story campaign with chapters, cutscenes, and objectives."""
from ursina import *

STORY_CHAPTERS = [
    {
        'id': 'ch1', 'title': 'Awakening', 'desc': 'You wake up in the Nexus Command Station. Explore the nearby city.',
        'objectives': [
            {'text': 'Talk to the Commander', 'type': 'talk', 'target': 'Commander', 'done': False},
            {'text': 'Scan 3 ROMs', 'type': 'scan', 'count': 3, 'progress': 0, 'done': False},
            {'text': 'Build your first base', 'type': 'build', 'count': 1, 'progress': 0, 'done': False},
        ],
        'reward_cr': 500, 'reward_xp': 100,
    },
    {
        'id': 'ch2', 'title': 'First Contact', 'desc': 'Enemy drones have been spotted. Clear the sector.',
        'objectives': [
            {'text': 'Kill 5 drones', 'type': 'kill', 'count': 5, 'progress': 0, 'done': False},
            {'text': 'Discover an enemy outpost', 'type': 'discover', 'target': 'enemy_outpost', 'done': False},
            {'text': 'Upgrade your weapon', 'type': 'upgrade', 'done': False},
        ],
        'reward_cr': 800, 'reward_xp': 200,
    },
    {
        'id': 'ch3', 'title': 'The Dig', 'desc': 'Ancient ROM caches are buried deep. Mine to uncover them.',
        'objectives': [
            {'text': 'Mine 50 minerals', 'type': 'mine', 'count': 50, 'progress': 0, 'done': False},
            {'text': 'Open 3 loot crates', 'type': 'loot', 'count': 3, 'progress': 0, 'done': False},
            {'text': 'Craft an item', 'type': 'craft', 'done': False},
        ],
        'reward_cr': 1000, 'reward_xp': 300,
    },
    {
        'id': 'ch4', 'title': 'Shadow of Eldoria', 'desc': 'A boss named Eldoria commands the drone swarm. Defeat it.',
        'objectives': [
            {'text': 'Find the boss arena', 'type': 'discover', 'target': 'boss_arena', 'done': False},
            {'text': 'Defeat Eldoria', 'type': 'boss_kill', 'target': 'Eldoria', 'done': False},
        ],
        'reward_cr': 2000, 'reward_xp': 500,
    },
    {
        'id': 'ch5', 'title': 'Galaxy-wide', 'desc': 'Travel to all 8 galaxies and establish bases.',
        'objectives': [
            {'text': 'Visit all 8 galaxies', 'type': 'visit', 'count': 8, 'progress': 0, 'done': False},
            {'text': 'Build a base in each galaxy', 'type': 'build_per_galaxy', 'count': 8, 'progress': 0, 'done': False},
            {'text': 'Discover 100 ROMs', 'type': 'scan', 'count': 100, 'progress': 0, 'done': False},
        ],
        'reward_cr': 5000, 'reward_xp': 1000,
    },
    {
        'id': 'ch6', 'title': 'The Final Key', 'desc': 'Collect all 362 ROMs to unlock the secrets of the universe.',
        'objectives': [
            {'text': 'Discover all 362 ROMs', 'type': 'scan', 'count': 362, 'progress': 0, 'done': False},
            {'text': 'Defeat the Final Boss', 'type': 'boss_kill', 'target': 'Nexus Prime', 'done': False},
        ],
        'reward_cr': 10000, 'reward_xp': 5000,
    },
]

class StoryManager:
    def __init__(self, player, hud):
        self.player = player
        self.hud = hud
        self.chapters = [dict(ch) for ch in STORY_CHAPTERS]
        for ch in self.chapters:
            ch['objectives'] = [dict(obj) for obj in ch['objectives']]
        self.current_idx = 0
        self.completed = []
        self.visited_galaxies = set()
        self.built_galaxies = set()

    def get_current(self):
        if self.current_idx < len(self.chapters):
            return self.chapters[self.current_idx]
        return None

    def update(self, event_type, amount=1, target=None):
        ch = self.get_current()
        if not ch:
            return
        updated = False
        for obj in ch['objectives']:
            if obj['done']:
                continue
            if obj['type'] == event_type:
                match = True
                if 'target' in obj and target and obj['target'] != target:
                    match = False
                if match:
                    if 'count' in obj:
                        obj['progress'] += amount
                        if obj['progress'] >= obj['count']:
                            obj['progress'] = obj['count']
                            obj['done'] = True
                            updated = True
                    else:
                        obj['done'] = True
                        updated = True
        if updated and all(o['done'] for o in ch['objectives']):
            self.complete_chapter()

    def complete_chapter(self):
        ch = self.chapters[self.current_idx]
        self.current_idx += 1
        self.completed.append(ch)
        self.player.credits += ch['reward_cr']
        self.player.xp += ch['reward_xp']
        self.hud.set_message(f"CHAPTER COMPLETE: {ch['title']}! +{ch['reward_cr']}CR +{ch['reward_xp']}XP")
        if self.current_idx < len(self.chapters):
            next_ch = self.chapters[self.current_idx]
            self.hud.set_message(f"Next: {next_ch['title']} — {next_ch['desc']}")

    def visit_galaxy(self, name):
        self.visited_galaxies.add(name)
        self.update('visit', target=name)
        self.update('visit', amount=len(self.visited_galaxies))

    def build_in_galaxy(self, name):
        self.built_galaxies.add(name)
        self.update('build_per_galaxy', amount=len(self.built_galaxies))

    def get_log(self):
        lines = ["=== STORY ==="]
        for i, ch in enumerate(self.chapters):
            status = "✓" if i < self.current_idx else "→" if i == self.current_idx else "○"
            lines.append(f"{status} {ch['title']}")
            if i == self.current_idx:
                for obj in ch['objectives']:
                    prog = f" ({obj.get('progress', 0)}/{obj.get('count', 1)})" if 'count' in obj else ""
                    done = "✓" if obj['done'] else "○"
                    lines.append(f"   {done} {obj['text']}{prog}")
        return "\n".join(lines)
