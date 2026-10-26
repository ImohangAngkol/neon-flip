"""NEON FLIP — a tiny one-file arcade game. Requires only Python's Tkinter.

Run: python neon_flip.py
Controls: SPACE or click = flip lane; A/D or arrows = choose lane; R = restart.
"""

import json
import math
import random
import time
import tkinter as tk
from pathlib import Path


WIDTH, HEIGHT = 480, 720
LANES = (157, 323)
PLAYER_Y = 579
BACKGROUND = "#080a1d"
CYAN = "#51e9ff"
PINK = "#ff4e94"
GOLD = "#ffda68"


def clamp(number, low, high):
    return max(low, min(number, high))


class NeonFlip:
    def __init__(self, root):
        self.root = root
        root.title("NEON FLIP  ✦  One More Run")
        root.resizable(False, False)
        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg=BACKGROUND,
                                highlightthickness=0)
        self.canvas.pack()
        root.bind("<KeyPress>", self.on_key)
        root.bind("<KeyRelease-space>", self.on_space_release)
        self.canvas.bind("<Button-1>", self.on_click)
        self.space_held = False
        self.high_score = self.load_high_score()
        self.stars = [[random.randrange(WIDTH), random.randrange(HEIGHT),
                       random.uniform(18, 70), random.choice((1, 1, 2))]
                      for _ in range(70)]
        self.particles = []
        self.state = "ready"
        self.reset()
        self.last_tick = time.perf_counter()
        self.tick()

    @staticmethod
    def score_file():
        return Path(__file__).with_name("neon_flip_highscore.json")

    def load_high_score(self):
        try:
            data = json.loads(self.score_file().read_text(encoding="utf-8"))
            return max(0, int(data.get("high_score", 0)))
        except (OSError, ValueError, TypeError):
            return 0

    def save_high_score(self):
        try:
            self.score_file().write_text(
                json.dumps({"high_score": self.high_score}), encoding="utf-8"
            )
        except OSError:
            pass  # The game still works if the folder is read-only.

    def reset(self):
        self.elapsed = 0.0
        self.score = 0.0
        self.hearts = 3
        self.combo = 0
        self.combo_age = 0.0
        self.crystals = 0
        self.fever = 0.0
        self.invulnerable = 0.0
        self.shake = 0.0
        self.target_lane = 0
        self.player_x = float(LANES[0])
        self.objects = []
        self.particles.clear()
        self.spawn_clock = 0.4
        self.popups = []
        self.space_held = False

    def start(self):
        self.reset()
        self.state = "playing"

    def on_space_release(self, _event):
        self.space_held = False

    def on_key(self, event):
        key = event.keysym.lower()
        if key in ("return", "r") and self.state != "playing":
            self.start()
            return
        if key == "space":
            if self.space_held:
                return
            self.space_held = True
            if self.state != "playing":
                self.start()
                self.space_held = True  # Ignore key-repeat until SPACE is released.
            else:
                self.switch_lane(1 - self.target_lane)
        elif self.state == "playing":
            if key in ("a", "left"):
                self.switch_lane(0)
            elif key in ("d", "right"):
                self.switch_lane(1)

    def on_click(self, _event):
        if self.state == "playing":
            self.switch_lane(1 - self.target_lane)
        else:
            self.start()

    def switch_lane(self, lane):
        if lane == self.target_lane:
            return
        old_lane = self.target_lane
        # Reward a risky dodge: switch just before an obstacle reaches you.
        for obj in self.objects:
            if (obj["kind"] == "hazard" and obj["lane"] == old_lane
                    and not obj["near_miss"]
                    and PLAYER_Y - 140 < obj["y"] < PLAYER_Y - 50):
                obj["near_miss"] = True
                self.score += 15
                self.popup("CLOSE CALL +15", LANES[old_lane], PLAYER_Y - 75, CYAN)
                self.burst(self.player_x, PLAYER_Y, CYAN, 9)
                break
        self.target_lane = lane
        self.burst(self.player_x, PLAYER_Y + 18, CYAN, 8)

    def spawn_wave(self):
        hazard_lane = random.randrange(2)
        self.objects.append({
            "kind": "hazard", "lane": hazard_lane, "y": -45.0,
            "shape": random.choice(("block", "block", "spike")),
            "near_miss": False, "hit": False,
        })
        # Most waves put a gem in the safe lane. Other gems are bonus-only.
        if random.random() < 0.77:
            self.objects.append({
                "kind": "gem", "lane": 1 - hazard_lane, "y": -45.0,
                "hit": False,
            })
        if random.random() < 0.18:
            self.objects.append({
                "kind": "gem", "lane": random.randrange(2), "y": -200.0,
                "hit": False,
            })

    def burst(self, x, y, color, count=14):
        for _ in range(count):
            angle = random.uniform(0, math.tau)
            speed = random.uniform(55, 215)
            self.particles.append({
                "x": x, "y": y, "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed, "life": random.uniform(0.22, 0.65),
                "size": random.uniform(1.5, 4.5), "color": color,
            })

    def popup(self, text, x, y, color):
        self.popups.append({"text": text, "x": x, "y": y,
                            "age": 0.0, "color": color})

    def hit_hazard(self, obj):
        obj["hit"] = True
        x = LANES[obj["lane"]]
        if self.fever > 0:
            self.score += 20
            self.popup("SMASH +20", x, obj["y"], GOLD)
            self.burst(x, obj["y"], PINK, 17)
        elif self.invulnerable <= 0:
            self.hearts -= 1
            self.combo = 0
            self.invulnerable = 1.25
            self.shake = 0.28
            self.popup("OUCH!", self.player_x, PLAYER_Y - 45, PINK)
            self.burst(self.player_x, PLAYER_Y, PINK, 23)
            if self.hearts <= 0:
                self.end_game()

    def collect_gem(self, obj):
        obj["hit"] = True
        x = LANES[obj["lane"]]
        self.combo += 1
        self.combo_age = 0.0
        points = 25 * min(self.combo, 5) * (2 if self.fever > 0 else 1)
        self.score += points
        self.popup(f"+{points}  x{min(self.combo, 5)}", x, obj["y"], GOLD)
        self.burst(x, obj["y"], GOLD, 13)
        if self.fever <= 0:
            self.crystals += 1
            if self.crystals >= 7:
                self.crystals = 0
                self.fever = 5.0
                self.invulnerable = max(self.invulnerable, 0.2)
                self.popup("★ OVERDRIVE! ★", WIDTH / 2, HEIGHT / 2, CYAN)
                self.burst(self.player_x, PLAYER_Y, CYAN, 35)

    def end_game(self):
        self.state = "over"
        if int(self.score) > self.high_score:
            self.high_score = int(self.score)
            self.save_high_score()

    def update(self, dt):
        for star in self.stars:
            star[1] = (star[1] + star[2] * dt) % HEIGHT
        for p in self.particles:
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            p["vy"] += 150 * dt
            p["life"] -= dt
        self.particles = [p for p in self.particles if p["life"] > 0]
        for p in self.popups:
            p["y"] -= 40 * dt
            p["age"] += dt
        self.popups = [p for p in self.popups if p["age"] < 0.8]

        if self.state != "playing":
            return

        self.elapsed += dt
        self.score += 10 * dt
        self.combo_age += dt
        if self.combo_age > 2.5:
            self.combo = 0
        self.fever = max(0.0, self.fever - dt)
        self.invulnerable = max(0.0, self.invulnerable - dt)
        self.shake = max(0.0, self.shake - dt)
        movement = min(1.0, dt * 15)
        self.player_x += (LANES[self.target_lane] - self.player_x) * movement

        speed = min(490, 245 + self.elapsed * 6.1)
        self.spawn_clock -= dt
        if self.spawn_clock <= 0:
            self.spawn_wave()
            self.spawn_clock += max(0.49, 0.92 - self.elapsed * 0.006)

        for obj in self.objects:
            obj["y"] += speed * dt
            if obj["hit"] or abs(obj["y"] - PLAYER_Y) > 35:
                continue
            if abs(self.player_x - LANES[obj["lane"]]) < 52:
                if obj["kind"] == "gem":
                    self.collect_gem(obj)
                else:
                    self.hit_hazard(obj)
                if self.state == "over":
                    break
        self.objects = [o for o in self.objects if o["y"] < HEIGHT + 65
                        and not o["hit"]]

    def text(self, x, y, value, size=16, color="#ffffff", bold=False,
             anchor="center"):
        weight = "bold" if bold else "normal"
        self.canvas.create_text(x, y, text=value, font=("Consolas", size, weight),
                                fill=color, anchor=anchor)

    def draw_background(self):
        c = self.canvas
        for i in range(18):
            blue = 27 + i // 2
            c.create_rectangle(0, i * 40, WIDTH, (i + 1) * 40,
                               fill=f"#080a{blue:02x}", outline="")
        for x, y, _, radius in self.stars:
            c.create_oval(x - radius, y - radius, x + radius, y + radius,
                          fill="#343c69", outline="")
        c.create_rectangle(71, 93, 409, 693, fill="#101330", outline="#34365f", width=2)
        c.create_line(WIDTH // 2, 93, WIDTH // 2, 693, fill="#33385d",
                      width=2, dash=(8, 12))
        grid_offset = (self.elapsed * 90) % 48
        for n in range(14):
            y = 100 + (n * 48 + grid_offset) % 592
            c.create_line(75, y, 405, y, fill="#1a2044")
        for x in (79, 401):
            c.create_line(x, 102, x, 689, fill="#674aff", width=3)

    def draw_objects(self):
        c = self.canvas
        for obj in self.objects:
            x, y = LANES[obj["lane"]], obj["y"]
            if obj["kind"] == "gem":
                c.create_oval(x - 27, y - 27, x + 27, y + 27,
                              outline="#7f6a3b", width=2)
                c.create_polygon(x, y - 20, x + 17, y, x, y + 20, x - 17, y,
                                 fill=GOLD, outline="#fff6be", width=2)
                c.create_line(x - 6, y - 7, x + 1, y - 13, fill="#fff9db", width=3)
            else:
                c.create_oval(x - 40, y - 40, x + 40, y + 40,
                              outline="#5b254d", width=2)
                if obj["shape"] == "block":
                    c.create_rectangle(x - 28, y - 27, x + 28, y + 27,
                                       fill="#aa255b", outline=PINK, width=3)
                    c.create_line(x - 15, y - 14, x + 15, y + 14,
                                  fill="#ff9fbd", width=4)
                    c.create_line(x + 15, y - 14, x - 15, y + 14,
                                  fill="#ff9fbd", width=4)
                else:
                    c.create_polygon(x, y - 33, x + 32, y + 28, x - 32, y + 28,
                                     fill="#a32a5e", outline=PINK, width=3)
                    self.text(x, y + 10, "!", 22, "#ffe1ed", True)

    def draw_player(self):
        if self.state not in ("playing", "over"):
            return
        c = self.canvas
        x, y = self.player_x, PLAYER_Y
        if self.invulnerable > 0 and self.fever <= 0 and int(self.elapsed * 13) % 2:
            return
        color = GOLD if self.fever > 0 else CYAN
        if self.fever > 0:
            c.create_oval(x - 48, y - 48, x + 48, y + 48,
                          outline=GOLD, width=3)
            c.create_oval(x - 39, y - 39, x + 39, y + 39,
                          outline="#8c70ff", width=2)
        c.create_oval(x - 34, y - 34, x + 34, y + 34,
                      outline="#256e93", width=2)
        c.create_polygon(x, y - 29, x + 24, y + 25, x, y + 16, x - 24, y + 25,
                         fill="#207aa8", outline=color, width=3)
        c.create_polygon(x, y - 16, x + 8, y + 10, x, y + 5, x - 8, y + 10,
                         fill=color, outline="")
        flame_height = random.randrange(16, 27)
        c.create_polygon(x - 8, y + 23, x, y + 23 + flame_height, x + 8, y + 23,
                         fill=GOLD if self.fever > 0 else "#ff7d6c", outline="")

    def draw_particles_and_popups(self):
        c = self.canvas
        for p in self.particles:
            x, y, r = p["x"], p["y"], p["size"] * min(1, p["life"] * 3)
            c.create_oval(x - r, y - r, x + r, y + r,
                          fill=p["color"], outline="")
        for p in self.popups:
            self.text(p["x"], p["y"], p["text"], 13, p["color"], True)

    def draw_hud(self):
        c = self.canvas
        c.create_rectangle(0, 0, WIDTH, 91, fill="#0b0d26", outline="")
        self.text(20, 17, "SCORE", 10, "#7984bf", True, "w")
        self.text(20, 50, str(int(self.score)).zfill(5), 28, "#ffffff", True, "w")
        self.text(459, 18, f"BEST {self.high_score}", 11, "#a6b0d6", True, "e")
        self.text(459, 51, "♥ " * self.hearts + "♡ " * (3 - self.hearts),
                  18, PINK, True, "e")
        c.create_rectangle(0, 693, WIDTH, 720, fill="#0b0d26", outline="")
        self.text(19, 707, "OVERDRIVE", 10, "#b0b7dc", True, "w")
        for i in range(7):
            x = 110 + i * 27
            color = GOLD if i < self.crystals or self.fever > 0 else "#292e50"
            c.create_rectangle(x, 700, x + 19, 713, fill=color, outline="")
        if self.fever > 0:
            self.text(456, 706, f"FEVER {self.fever:.1f}s", 11, GOLD, True, "e")
        elif self.combo > 1:
            self.text(456, 706, f"COMBO x{min(self.combo, 5)}", 11, GOLD, True, "e")

    def draw_overlay(self, title, subtitle, extra):
        c = self.canvas
        c.create_rectangle(41, 211, 439, 524, fill="#0d112d",
                           outline="#6b58d9", width=3)
        c.create_rectangle(53, 222, 427, 234, fill="#aa3dff", outline="")
        self.text(WIDTH / 2, 285, title, 36, CYAN, True)
        self.text(WIDTH / 2, 336, subtitle, 14, "#f0f1ff", True)
        self.text(WIDTH / 2, 383, extra, 12, "#a5abd5")
        c.create_rectangle(108, 433, 372, 486, fill="#2d2563",
                           outline=GOLD, width=2)
        self.text(WIDTH / 2, 459, "SPACE / CLICK TO PLAY", 15, GOLD, True)

    def draw(self):
        self.canvas.delete("all")
        self.draw_background()
        self.draw_objects()
        self.draw_player()
        self.draw_particles_and_popups()
        if self.shake > 0 and int(self.elapsed * 25) % 2:
            self.canvas.create_rectangle(82, 105, 398, 687,
                                         outline=PINK, width=5)
        self.draw_hud()
        if self.state == "ready":
            self.draw_overlay("NEON FLIP", "DODGE RED  ·  GRAB GOLD",
                              "SPACE / CLICK: flip lanes   |   A / D: steer")
            self.text(WIDTH / 2, 550, "7 gems = 5 seconds of OVERDRIVE!", 12, GOLD)
        elif self.state == "over":
            self.draw_overlay("GAME OVER", f"SCORE: {int(self.score)}  •  BEST: {self.high_score}",
                              "Risky last-second flips earn bonus points")
            self.text(WIDTH / 2, 550, "Press R to restart, too!", 12, "#b7c4ff")
        elif self.fever > 0:
            self.text(WIDTH / 2, 121, "★  OVERDRIVE  ★", 18, GOLD, True)

    def tick(self):
        now = time.perf_counter()
        dt = clamp(now - self.last_tick, 0.0, 0.04)
        self.last_tick = now
        self.update(dt)
        self.draw()
        self.root.after(16, self.tick)


if __name__ == "__main__":
    try:
        window = tk.Tk()
        NeonFlip(window)
        window.mainloop()
    except tk.TclError as exc:
        print("Could not open the game window:", exc)
        print("Run this on a desktop computer with Python and Tkinter installed.")
