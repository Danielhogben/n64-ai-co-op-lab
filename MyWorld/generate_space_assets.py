#!/usr/bin/env python3
"""AI-designed space shooter assets for Zelda mod"""
from PIL import Image, ImageDraw
import os
import json

os.makedirs("assets_generated", exist_ok=True)

# Load game design
with open("ai_game_design.json") as f:
    design = json.load(f)

def create_player_ship():
    """Star Ocarina ship - sleek, green, triforce emblem"""
    img = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # Main body (green triangle)
    draw.polygon([(16, 2), (4, 28), (28, 28)], fill=(0, 200, 0, 255))
    # Wings
    draw.polygon([(4, 28), (0, 32), (8, 32)], fill=(0, 150, 0, 255))
    draw.polygon([(28, 28), (24, 32), (32, 32)], fill=(0, 150, 0, 255))
    # Triforce emblem
    draw.polygon([(16, 12), (12, 20), (20, 20)], fill=(255, 215, 0, 255))
    img.save('assets_generated/player_ship.png')
    print("[AI] Generated player ship: Star Ocarina")

def create_skulltula_fighter():
    """Fast swarm enemy - red with skull pattern"""
    img = Image.new('RGBA', (24, 24), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # Body (red circle)
    draw.ellipse([2, 2, 22, 22], fill=(200, 0, 0, 255))
    # Skull pattern
    draw.ellipse([8, 6, 16, 14], fill=(255, 255, 255, 255))
    draw.ellipse([9, 8, 11, 10], fill=(0, 0, 0, 255))
    draw.ellipse([13, 8, 15, 10], fill=(0, 0, 0, 255))
    draw.arc([10, 11, 14, 15], 0, 180, fill=(0, 0, 0, 255), width=1)
    img.save('assets_generated/enemy_skulltula.png')
    print("[AI] Generated enemy: Skulltula Fighter")

def create_gohma_carrier():
    """Boss enemy - large, purple, menacing"""
    img = Image.new('RGBA', (48, 48), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # Main body
    draw.ellipse([4, 4, 44, 44], fill=(128, 0, 128, 255))
    # Eye
    draw.ellipse([16, 16, 32, 32], fill=(255, 255, 0, 255))
    draw.ellipse([20, 20, 28, 28], fill=(0, 0, 0, 255))
    # Legs
    for i in range(6):
        angle = i * 60
        x1 = 24 + int(20 * __import__('math').cos(__import__('math').radians(angle)))
        y1 = 24 + int(20 * __import__('math').sin(__import__('math').radians(angle)))
        draw.line([(24, 24), (x1, y1)], fill=(100, 0, 100, 255), width=3)
    img.save('assets_generated/enemy_gohma.png')
    print("[AI] Generated boss: Gohma Carrier")

def create_dark_link():
    """Elite enemy - black with red glow"""
    img = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # Ship body (sleek, dark)
    draw.polygon([(16, 2), (6, 28), (26, 28)], fill=(30, 30, 30, 255))
    # Red accent lines
    draw.line([(16, 2), (6, 28)], fill=(255, 0, 0, 255), width=2)
    draw.line([(16, 2), (26, 28)], fill=(255, 0, 0, 255), width=2)
    # Red glow eyes
    draw.ellipse([10, 12, 14, 16], fill=(255, 0, 0, 255))
    draw.ellipse([18, 12, 22, 16], fill=(255, 0, 0, 255))
    img.save('assets_generated/enemy_darklink.png')
    print("[AI] Generated elite: Dark Link Interceptor")

def create_laser_weapon():
    """Laser bullet - cyan beam"""
    img = Image.new('RGBA', (8, 16), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rectangle([2, 0, 6, 16], fill=(0, 255, 255, 255))
    draw.rectangle([3, 0, 5, 16], fill=(255, 255, 255, 200))
    img.save('assets_generated/bullet_laser.png')
    print("[AI] Generated weapon: Laser Z-targeting")

def create_missile():
    """Homing missile - yellow with red tip"""
    img = Image.new('RGBA', (12, 20), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.polygon([(6, 0), (2, 16), (10, 16)], fill=(255, 255, 0, 255))
    draw.rectangle([4, 16, 8, 20], fill=(255, 0, 0, 255))
    img.save('assets_generated/bullet_missile.png')
    print("[AI] Generated weapon: Ocarina Pulse Missile")

def create_explosion():
    """Explosion effect - orange/yellow"""
    img = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    for r in range(16, 4, -2):
        color = (255, 200 - r*8, 0, 255 - r*10) if r < 15 else (255, 255, 0, 255)
        draw.ellipse([16-r, 16-r, 16+r, 16+r], fill=color)
    img.save('assets_generated/explosion.png')
    print("[AI] Generated effect: Explosion")

# Generate all assets
create_player_ship()
create_skulltula_fighter()
create_gohma_carrier()
create_dark_link()
create_laser_weapon()
create_missile()
create_explosion()

print("\n[AI] All space shooter assets generated in assets_generated/")
