"""Game clock: fixed timestep game loop at 60Hz."""
import time

class GameClock:
    def __init__(self, tick_rate=60):
        self.tick_rate = tick_rate
        self.tick_duration = 1.0 / tick_rate
        self.running = False
        self.last_time = 0.0
        self.accumulator = 0.0
        
    def start(self):
        self.running = True
        self.last_time = time.time()
        
    def stop(self):
        self.running = False
        
    def tick(self):
        """Returns True if a game tick occurred."""
        now = time.time()
        delta = now - self.last_time
        self.last_time = now
        self.accumulator += delta
        
        if self.accumulator >= self.tick_duration:
            self.accumulator -= self.tick_duration
            return True
        return False
