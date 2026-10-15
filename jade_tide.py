#!/usr/bin/env python3
"""Jade Tide — neon tide-hopper arcade for ElbowOS. Python 3 + pygame."""
import os, sys, math, random, subprocess
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame
W, H, FPS, SECS = 1080, 1920, 30, 15
OUT = os.environ.get("ELBOWOS_MP4", "/home/workdir/artifacts/JADE_TIDE_ElbowOS.mp4")
TITLE, HANDLE = "JADE TIDE", "x.com/ElbowOS"
NAVY = (8, 18, 42)
TEAL = (0, 80, 90)
JADE = (0, 220, 120)
CYAN = (0, 255, 255)
MAGENTA = (255, 40, 180)
GOLD = (255, 210, 60)
WHITE = (240, 250, 255)
DARK = (4, 8, 20)
LANES = 9
LANE_H = 140
class Game:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        self.font_lg = pygame.font.SysFont("arial", 72, bold=True)
        self.font_md = pygame.font.SysFont("arial", 48, bold=True)
        self.font_sm = pygame.font.SysFont("arial", 32)
        flags = 0 if "--play" in sys.argv else pygame.HIDDEN
        try:
            self.screen = pygame.display.set_mode((W, H), flags)
        except pygame.error:
            os.environ["SDL_VIDEODRIVER"] = "dummy"
            self.screen = pygame.display.set_mode((W, H), pygame.HIDDEN)
        self.clock = pygame.time.Clock()
        self.reset()
    def reset(self):
        self.px, self.py = W // 2, H - 180
        self.lane = 0
        self.score = 0
        self.orbs = []
        self.obstacles = []
        self.spawn_obstacles()
        self.spawn_orbs()
        self.hopping = False
        self.hop_t = 0
        self.tx, self.ty = self.px, self.py
        self.alive = True
        self.time = 0
    def spawn_obstacles(self):
        self.obstacles = []
        for ln in range(LANES):
            speed = random.uniform(1.5, 4.0) * (1 if ln % 2 == 0 else -1)
            y = H - 220 - ln * LANE_H
            for i in range(4):
                x = random.randint(0, W)
                w = random.randint(80, 180)
                col = random.choice([MAGENTA, CYAN, (255, 80, 40)])
                self.obstacles.append({"x": x, "y": y, "w": w, "h": 36, "spd": speed, "col": col, "lane": ln})
    def spawn_orbs(self):
        self.orbs = []
        for ln in range(1, LANES):
            if random.random() < 0.6:
                y = H - 220 - ln * LANE_H
                x = random.randint(100, W - 100)
                self.orbs.append({"x": x, "y": y, "r": 18, "got": False})
    def hop_to(self, dx, dy):
        if self.hopping or not self.alive:
            return
        self.tx = max(40, min(W - 40, self.px + dx))
        self.ty = max(80, min(H - 120, self.py + dy))
        self.hopping = True
        self.hop_t = 0
    def autoplay(self):
        if not self.alive:
            self.reset()
            return
        if self.hopping:
            return
        if random.random() < 0.4 and self.lane < LANES - 1:
            self.hop_to(random.randint(-80, 80), -LANE_H)
            self.lane += 1
        elif random.random() < 0.3:
            self.hop_to(random.choice([-120, 120]), 0)
        else:
            self.hop_to(0, random.choice([-LANE_H // 2, 0, LANE_H // 2]))
    def tick(self):
        self.time += 1
        for o in self.obstacles:
            o["x"] += o["spd"]
            if o["x"] < -200:
                o["x"] = W + 50
            if o["x"] > W + 200:
                o["x"] = -150
        if self.hopping:
            self.hop_t += 0.18
            t = min(1.0, self.hop_t)
            self.px = self.px * (1 - t) + self.tx * t
            arc = math.sin(t * math.pi) * 40
            self.py = self.py * (1 - t) + self.ty * t - arc
            if t >= 1.0:
                self.hopping = False
                self.px, self.py = self.tx, self.ty
                for orb in self.orbs:
                    if not orb["got"] and math.hypot(self.px - orb["x"], self.py - orb["y"]) < 40:
                        orb["got"] = True
                        self.score += 10
                for o in self.obstacles:
                    if abs(self.py - o["y"]) < 50 and o["x"] < self.px < o["x"] + o["w"]:
                        self.alive = False
                        self.score = max(0, self.score - 5)
        if not self.hopping:
            self.py += math.sin(self.time * 0.05) * 0.3
    def draw(self, surf):
        surf.fill(NAVY)
        for ln in range(LANES):
            y = H - 220 - ln * LANE_H
            c = (0, 40 + ln * 8, 60 + ln * 6)
            pygame.draw.rect(surf, c, (0, y - 20, W, LANE_H))
            for i in range(0, W, 40):
                pygame.draw.line(surf, TEAL, (i, y), (i + 20, y + 8), 2)
        for o in self.obstacles:
            pygame.draw.rect(surf, o["col"], (int(o["x"]), int(o["y"] - 18), o["w"], o["h"]), border_radius=8)
            pygame.draw.rect(surf, WHITE, (int(o["x"]), int(o["y"] - 18), o["w"], o["h"]), 2, border_radius=8)
        for orb in self.orbs:
            if not orb["got"]:
                pygame.draw.circle(surf, GOLD, (int(orb["x"]), int(orb["y"])), orb["r"])
                pygame.draw.circle(surf, WHITE, (int(orb["x"]), int(orb["y"])), orb["r"], 2)
        if self.alive:
            pygame.draw.ellipse(surf, JADE, (int(self.px - 28), int(self.py - 22), 56, 44))
            pygame.draw.ellipse(surf, (0, 180, 90), (int(self.px - 28), int(self.py - 22), 56, 44), 3)
            pygame.draw.circle(surf, WHITE, (int(self.px - 12), int(self.py - 8)), 8)
            pygame.draw.circle(surf, WHITE, (int(self.px + 12), int(self.py - 8)), 8)
            pygame.draw.circle(surf, DARK, (int(self.px - 12), int(self.py - 8)), 4)
            pygame.draw.circle(surf, DARK, (int(self.px + 12), int(self.py - 8)), 4)
        else:
            pygame.draw.circle(surf, (180, 40, 40), (int(self.px), int(self.py)), 20)
        title = self.font_lg.render(TITLE, True, JADE)
        surf.blit(title, title.get_rect(center=(W // 2, 80)))
        sc = self.font_md.render(f"SCORE  {self.score}", True, GOLD)
        surf.blit(sc, sc.get_rect(center=(W // 2, 160)))
        handle = self.font_sm.render(HANDLE, True, CYAN)
        surf.blit(handle, handle.get_rect(center=(W // 2, H - 60)))
        if not self.alive:
            msg = self.font_md.render("SPLASH!", True, MAGENTA)
            surf.blit(msg, msg.get_rect(center=(W // 2, H // 2)))
    def play_interactive(self):
        running = True
        while running:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT or (ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE):
                    running = False
                if ev.type == pygame.KEYDOWN:
                    if ev.key in (pygame.K_UP, pygame.K_w):
                        self.hop_to(0, -LANE_H); self.lane = min(LANES - 1, self.lane + 1)
                    elif ev.key in (pygame.K_DOWN, pygame.K_s):
                        self.hop_to(0, LANE_H); self.lane = max(0, self.lane - 1)
                    elif ev.key in (pygame.K_LEFT, pygame.K_a):
                        self.hop_to(-140, 0)
                    elif ev.key in (pygame.K_RIGHT, pygame.K_d):
                        self.hop_to(140, 0)
                    elif ev.key == pygame.K_r:
                        self.reset()
            self.tick()
            self.draw(self.screen)
            pygame.display.flip()
            self.clock.tick(FPS)
        pygame.quit()
    def record(self):
        frames = FPS * SECS
        cmd = [
            "ffmpeg", "-y", "-f", "rawvideo", "-vcodec", "rawvideo",
            "-s", f"{W}x{H}", "-pix_fmt", "rgb24", "-r", str(FPS),
            "-i", "-", "-an", "-vcodec", "libx264", "-pix_fmt", "yuv420p",
            "-crf", "20", "-movflags", "+faststart", OUT
        ]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        canvas = pygame.Surface((W, H))
        try:
            for i in range(frames):
                self.autoplay()
                self.tick()
                self.draw(canvas)
                raw = pygame.image.tostring(canvas, "RGB")
                proc.stdin.write(raw)
                if i % 60 == 0:
                    print(f"frame {i}/{frames}", flush=True)
        finally:
            proc.stdin.close()
        err = proc.stderr.read().decode("utf-8", "ignore")
        rc = proc.wait()
        if rc != 0:
            raise SystemExit(f"ffmpeg failed ({rc}):\n{err[-1500:]}")
        print("Wrote", OUT)
        pygame.quit()
def main():
    g = Game()
    if "--play" in sys.argv and "--record" not in sys.argv:
        g.play_interactive()
    else:
        g.record()
if __name__ == "__main__":
    main()
