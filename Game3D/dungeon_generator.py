import random, math
from ursina import *
from ursina import distance

class Dungeon:
    def __init__(self, entrance_pos):
        self.entrance_world_pos = entrance_pos
        self.root = Entity(model=None)
        self.rooms = []
        self.chests = []
        self.exit_portal = None
        self.active = False
        self.generate()

    def generate(self):
        for c in self.root.children: destroy(c)
        self.rooms.clear(); self.chests.clear(); self.exit_portal = None
        tile, gw, gh = 4, 20, 20
        occupied = [[False]*gh for _ in range(gw)]
        def place_room(x,y,w,h):
            for i in range(x, x+w):
                for j in range(y, y+h):
                    if i<0 or j<0 or i>=gw or j>=gh or occupied[i][j]: return False
            for i in range(x, x+w):
                for j in range(y, y+h): occupied[i][j] = True
            return True
        start = {'x':8,'y':8,'w':4,'h':4}
        if not place_room(start['x'],start['y'],start['w'],start['h']): return
        self.rooms.append(start)
        for _ in range(random.randint(6,12)):
            w=random.randint(3,6); h=random.randint(3,6)
            x=random.randint(0,gw-w); y=random.randint(0,gh-h)
            if place_room(x,y,w,h): self.rooms.append({'x':x,'y':y,'w':w,'h':h})
        def room_center(r):
            return Vec3((r['x']+r['w']/2)*tile, 0, (r['y']+r['h']/2)*tile)
        for room in self.rooms:
            c = room_center(room); room['_center'] = c
            Entity(parent=self.root, model='plane', scale=(room['w']*tile,1,room['h']*tile),
                   position=c+Vec3(0,-0.5,0), color=color.rgb(100,100,110), texture='brick', collider='box')
            minx=room['x']*tile; maxx=(room['x']+room['w'])*tile; minz=room['y']*tile; maxz=(room['y']+room['h'])*tile
            for dx in range(room['w']):
                Entity(parent=self.root, model='cube', scale=(1,3,1), position=Vec3(minx+dx*tile,1,minz-0.5), color=color.rgb(70,70,80), collider='box')
                Entity(parent=self.root, model='cube', scale=(1,3,1), position=Vec3(minx+dx*tile,1,maxz+0.5), color=color.rgb(70,70,80), collider='box')
            for dz in range(room['h']):
                Entity(parent=self.root, model='cube', scale=(1,3,1), position=Vec3(minx-0.5,1,minz+dz*tile), color=color.rgb(70,70,80), collider='box')
                Entity(parent=self.root, model='cube', scale=(1,3,1), position=Vec3(maxx+0.5,1,minz+dz*tile), color=color.rgb(70,70,80), collider='box')
        for i in range(len(self.rooms)-1):
            a=self.rooms[i]['_center']; b=self.rooms[i+1]['_center']; mid=Vec3(b.x,0,a.z)
            self._corridor(a,mid,tile); self._corridor(mid,b,tile)
        for room in self.rooms[1:]:
            if random.random()<0.7:
                self.chests.append(Chest(parent=self.root, position=room['_center']+Vec3(0,0,1)))
        far=self.rooms[-1]; self.exit_portal = PortalExit(parent=self.root, position=far['_center']+Vec3(0,0,-2), dungeon=self)
        self.active = True

    def _corridor(self,a,b,tile):
        length=distance(Vec2(a.x,a.z),Vec2(b.x,b.z)); center=(a+b)/2; center.y=-0.5
        dirv=(b-a); dirv.y=0; dirv=dirv.normalized(); width=tile
        Entity(parent=self.root,model='plane',scale=(length,1,width),position=center,
               rotation_y=math.degrees(math.atan2(dirv.x,dirv.z)),color=color.rgb(90,90,100),collider='box')

    def enter_dungeon(self, player, audio=None):
        player.dungeon_exit_pos = self.entrance_world_pos
        spawn = self.rooms[0]['_center'] + Vec3(0,1,0)
        player.position = spawn
        self.root.visible = True
        if audio: audio.play('portal_enter')
        return "Entered dungeon. Find the exit portal."

    def exit_to_surface(self, player, audio=None):
        player.position = self.entrance_world_pos + Vec3(0,1,2)
        self.root.visible = False
        if audio: audio.play('portal_enter')
        return "Exited to surface."

class Chest(Entity):
    def __init__(self, parent, position):
        super().__init__(parent=parent, model='cube', color=color.rgb(180,150,70), scale=(1,0.6,0.6), position=position, collider='box')
        self.opened=False; self.rotate_speed=20
    def update(self):
        self.rotation_y += self.rotate_speed * time.dt
    def interact(self, player, audio=None):
        if self.opened: return "Already empty."
        self.opened=True
        loot=random.choice([
            {'type':'credits','amount':random.randint(50,200)},
            {'type':'minerals','amount':random.randint(30,100)},
            {'type':'weapon_part','amount':1},
            {'type':'shield_boost','amount':25},
        ])
        if loot['type']=='credits': player.credits += loot['amount']
        elif loot['type']=='minerals': player.minerals += loot['amount']
        elif loot['type']=='weapon_part': player.weapon_damage += 3
        elif loot['type']=='shield_boost':
            player.shield_strength = min(getattr(player,'max_shield',100), player.shield_strength + loot['amount'])
        if audio: audio.play('crate_open')
        self.color=color.gray; self.scale_y=0.3
        return f"Found: {loot['amount']} {loot['type']}!"

class PortalExit(Entity):
    def __init__(self, parent, position, dungeon):
        super().__init__(parent=parent, model='ring', color=color.rgba(255,200,0,220), scale=2, position=position, collider='box', billboard=True)
        self.dungeon=dungeon; self.cooldown=0; self.timer=0
    def update(self):
        self.timer += time.dt
        if self.cooldown>0: self.cooldown -= time.dt
        self.scale = 2 + 0.15*math.sin(self.timer*3)
    def interact(self, player, audio=None):
        if self.cooldown>0: return "Portal recharging..."
        return self.dungeon.exit_to_surface(player, audio)
