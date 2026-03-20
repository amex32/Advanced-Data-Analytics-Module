"""
╔══════════════════════════════════════════════════════════════╗
║           ALPINE FURY — Mountain Rain Racer                  ║
║      First-Person Perspective · Python + Pygame              ║
║                                                              ║
║  Install:  pip install pygame numpy                          ║
║  Run:      python alpine_fury.py                             ║
║                                                              ║
║  Controls:                                                   ║
║    W / ↑      Accelerate                                     ║
║    S / ↓      Brake / Reverse                                ║
║    A / ←      Steer Left                                     ║
║    D / →      Steer Right                                    ║
║    SPACE       Handbrake                                     ║
║    ESC         Quit                                          ║
╚══════════════════════════════════════════════════════════════╝
"""

import pygame
import numpy as np
import math
import random
import sys
import time

# ──────────────────────────────────────────────
#  CONSTANTS
# ──────────────────────────────────────────────
WIDTH, HEIGHT = 1280, 720
FPS = 60
TOTAL_LAPS = 3
NPC_COUNT = 5
ROAD_WIDTH = 220          # world units
FOV = 90                  # degrees
CAMERA_HEIGHT = 1.2       # metres above road
DRAW_DISTANCE = 300       # track segments ahead rendered
SEG_LENGTH = 8.0          # world units per track segment
RUMBLE_SEGS = 6
HORIZON = 0.45            # fraction of screen = sky/mountain split

# Colours
SKY_TOP    = (22, 28, 45)
SKY_BOT    = (55, 70, 90)
MOUNTAIN_1 = (38, 52, 42)
MOUNTAIN_2 = (28, 40, 32)
MOUNTAIN_3 = (20, 30, 25)
FOG_COLOR  = (80, 100, 115)

ROAD_DARK  = (52, 52, 58)
ROAD_LIGHT = (60, 60, 66)
RUMBLE_W   = (200, 200, 205)
RUMBLE_R   = (180, 40, 40)
GRASS_DARK = (28, 70, 35)
GRASS_LT   = (35, 85, 42)
LINE_WHITE  = (230, 230, 230)

RAIN_COL   = (140, 180, 220, 90)
SPLASH_COL = (160, 200, 240, 120)

NPC_COLORS = [
    (220, 50, 50),
    (50, 180, 220),
    (230, 160, 30),
    (160, 50, 220),
    (50, 220, 100),
]
NPC_NAMES = ["VASQUEZ", "CHEN", "MÜLLER", "OKAFOR", "PETROV"]


# ──────────────────────────────────────────────
#  TRACK BUILDER — mountain road with hills/curves
# ──────────────────────────────────────────────
class Track:
    def __init__(self):
        self.segments = []
        self._build()
        self.length = len(self.segments) * SEG_LENGTH

    def _add_straight(self, n=25, pitch=0.0):
        for _ in range(n):
            self.segments.append({
                'curve': 0.0, 'pitch': pitch,
                'x': 0.0, 'y': 0.0, 'z': len(self.segments) * SEG_LENGTH,
                'clip': 0.0, 'scale': 0.0,
                'grass': self._grass(len(self.segments)),
                'rumble': self._rumble(len(self.segments)),
                'objects': []
            })

    def _add_curve(self, n=40, curve=0.003, pitch=0.0):
        for i in range(n):
            t = i / n
            ease = math.sin(t * math.pi)  # ease in/out
            self.segments.append({
                'curve': curve * ease, 'pitch': pitch * ease,
                'x': 0.0, 'y': 0.0, 'z': len(self.segments) * SEG_LENGTH,
                'clip': 0.0, 'scale': 0.0,
                'grass': self._grass(len(self.segments)),
                'rumble': self._rumble(len(self.segments)),
                'objects': []
            })

    def _add_hill(self, n=30, pitch=0.0025, curve=0.0):
        half = n // 2
        for i in range(half):
            t = i / half
            self.segments.append({
                'curve': curve, 'pitch': pitch * t,
                'x': 0.0, 'y': 0.0, 'z': len(self.segments) * SEG_LENGTH,
                'clip': 0.0, 'scale': 0.0,
                'grass': self._grass(len(self.segments)),
                'rumble': self._rumble(len(self.segments)),
                'objects': []
            })
        for i in range(half):
            t = 1 - i / half
            self.segments.append({
                'curve': curve, 'pitch': pitch * t,
                'x': 0.0, 'y': 0.0, 'z': len(self.segments) * SEG_LENGTH,
                'clip': 0.0, 'scale': 0.0,
                'grass': self._grass(len(self.segments)),
                'rumble': self._rumble(len(self.segments)),
                'objects': []
            })

    def _grass(self, i):
        return GRASS_DARK if (i // 6) % 2 == 0 else GRASS_LT

    def _rumble(self, i):
        return RUMBLE_R if (i // RUMBLE_SEGS) % 2 == 0 else RUMBLE_W

    def _build(self):
        """Mountain circuit: winding alpine pass with hills"""
        self._add_straight(30)
        self._add_curve(50, 0.0025)
        self._add_hill(40, 0.003)
        self._add_curve(60, -0.003, 0.001)
        self._add_straight(20)
        self._add_hill(50, 0.004, 0.002)
        self._add_curve(70, 0.004)
        self._add_straight(25)
        self._add_curve(55, -0.005, -0.001)
        self._add_hill(35, -0.003)
        self._add_curve(45, 0.003)
        self._add_straight(30)
        self._add_hill(60, 0.005, 0.003)
        self._add_curve(50, -0.004)
        self._add_straight(20)
        self._add_hill(40, 0.003, -0.002)
        self._add_curve(65, 0.005, 0.002)
        self._add_straight(15)
        self._add_curve(45, -0.003)
        self._add_hill(30, 0.002)
        self._add_straight(25)

        # Precompute world positions
        x = y = 0.0
        dx = dy = 0.0
        for seg in self.segments:
            seg['x'] = x
            seg['y'] = y
            dx += seg['curve']
            dy += seg['pitch']
            x += dx
            y += dy

        # Add pine tree objects on sides
        for i, seg in enumerate(self.segments):
            if i % 8 == 0:
                seg['objects'].append({'x': random.uniform(1.2, 2.5), 'type': 'tree',
                                       'size': random.uniform(0.8, 1.4)})
            if i % 7 == 0:
                seg['objects'].append({'x': random.uniform(-2.5, -1.2), 'type': 'tree',
                                       'size': random.uniform(0.8, 1.4)})
            if i % 25 == 0:
                seg['objects'].append({'x': random.uniform(-1.1, 1.1), 'type': 'rock',
                                       'size': random.uniform(0.2, 0.5)})


# ──────────────────────────────────────────────
#  CAR (Player)
# ──────────────────────────────────────────────
class PlayerCar:
    def __init__(self, track):
        self.track = track
        self.z = 50.0          # position along track
        self.x = 0.0           # lateral offset (-1 to +1 = road edges)
        self.speed = 0.0
        self.max_speed = 28.0  # m/s ≈ 100 km/h
        self.accel = 14.0
        self.brake_force = 20.0
        self.reverse_max = 6.0
        self.steer_speed = 1.8
        self.drag = 0.94
        self.wet_grip = 0.78   # reduced in rain
        self.lateral_vel = 0.0
        self.camera_x = 0.0   # smooth camera lag
        self.lap = 1
        self.lap_times = []
        self._lap_start = time.time()
        self._prev_seg = 0
        self.gear = 1
        self.engine_rpm = 800
        self.handbrake = False

    @property
    def seg_index(self):
        n = len(self.track.segments)
        return int(self.z / SEG_LENGTH) % n

    @property
    def current_seg(self):
        return self.track.segments[self.seg_index]

    def update(self, keys, dt):
        seg = self.current_seg
        curve = seg['curve']
        pitch = seg['pitch']

        # Input
        accel   = keys[pygame.K_w] or keys[pygame.K_UP]
        braking = keys[pygame.K_s] or keys[pygame.K_DOWN]
        left    = keys[pygame.K_a] or keys[pygame.K_LEFT]
        right   = keys[pygame.K_d] or keys[pygame.K_RIGHT]
        self.handbrake = keys[pygame.K_SPACE]

        # Drive force
        if accel:
            if self.speed < 0:
                self.speed += self.brake_force * dt
            else:
                self.speed += self.accel * dt
        elif braking:
            if self.speed > 0.5:
                self.speed -= self.brake_force * dt * (2 if self.handbrake else 1)
            else:
                self.speed = max(-self.reverse_max, self.speed - self.accel * 0.5 * dt)
        else:
            self.speed *= (self.drag ** dt)

        # Hill effect
        self.speed -= pitch * 5 * dt

        # Speed limits
        self.speed = max(-self.reverse_max, min(self.max_speed, self.speed))

        # Steering (wet traction reduces grip)
        steer = 0.0
        if left:  steer = -1
        if right: steer = 1
        grip = self.wet_grip if self.handbrake else 1.0
        self.x += steer * self.steer_speed * dt * (self.speed / self.max_speed + 0.1) * grip

        # Centrifugal drift on curves
        self.x -= curve * self.speed * 0.008 * dt * 60

        # Road boundary bounce
        if abs(self.x) > 1.0:
            self.speed *= 0.65
            self.x = max(-1.0, min(1.0, self.x))

        # Off-road slowdown (if on grass/rumble)
        if abs(self.x) > 0.85:
            self.speed *= 0.97

        # Advance position
        self.z += self.speed * dt
        total = self.track.length
        if self.z >= total:
            self.z -= total
            prev = self._prev_seg
            if self.lap < TOTAL_LAPS:
                self.lap += 1
            self._prev_seg = self.seg_index

        if self.z < 0:
            self.z += total

        # Smooth camera X
        self.camera_x += (self.x - self.camera_x) * 0.08

        # Gear / RPM simulation
        speed_norm = max(0, self.speed) / self.max_speed
        gear_thresholds = [0.0, 0.12, 0.25, 0.42, 0.60, 0.80, 1.0]
        self.gear = 1
        for g, th in enumerate(gear_thresholds[1:], 1):
            if speed_norm > th:
                self.gear = g + 1
        self.gear = min(6, self.gear)

        g_low = gear_thresholds[self.gear - 1]
        g_high = gear_thresholds[self.gear]
        ratio = (speed_norm - g_low) / max(0.001, g_high - g_low)
        self.engine_rpm = int(1200 + ratio * 5800)
        if self.handbrake:
            self.engine_rpm = random.randint(3000, 5500)

    @property
    def kmh(self):
        return abs(int(self.speed * 3.6))


# ──────────────────────────────────────────────
#  NPC CAR
# ──────────────────────────────────────────────
class NPC:
    def __init__(self, color, name, start_z, track):
        self.track = track
        self.z = start_z
        self.x = random.uniform(-0.4, 0.4)
        self.color = color
        self.name = name
        self.base_speed = random.uniform(14.0, 22.0)
        self.speed = self.base_speed
        self.lap = 1
        self._wobble_t = random.uniform(0, 100)
        self.lap_total = 0

    def update(self, dt, player_z):
        self._wobble_t += dt
        self.x += math.sin(self._wobble_t * 0.7) * 0.003
        self.x = max(-0.9, min(0.9, self.x))

        seg = self.track.segments[int(self.z / SEG_LENGTH) % len(self.track.segments)]
        pitch = seg['pitch']
        self.speed = self.base_speed - pitch * 3 + random.uniform(-0.5, 0.5)
        self.speed = max(8, min(24, self.speed))

        self.z += self.speed * dt
        total = self.track.length
        if self.z >= total:
            self.z -= total
            self.lap += 1
            self.lap_total += 1

        if self.z < 0:
            self.z += total

    @property
    def seg_index(self):
        n = len(self.track.segments)
        return int(self.z / SEG_LENGTH) % n


# ──────────────────────────────────────────────
#  RAIN SYSTEM
# ──────────────────────────────────────────────
class Rain:
    def __init__(self, count=600):
        self.drops = []
        for _ in range(count):
            self.drops.append(self._new_drop())
        self.splash_particles = []
        self.surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

    def _new_drop(self):
        return {
            'x': random.randint(0, WIDTH),
            'y': random.randint(0, HEIGHT),
            'len': random.randint(10, 28),
            'speed': random.uniform(14, 26),
            'alpha': random.randint(80, 180),
            'width': random.choice([1, 1, 1, 2]),
        }

    def _add_splash(self, x, y):
        for _ in range(random.randint(2, 5)):
            self.splash_particles.append({
                'x': x, 'y': y,
                'vx': random.uniform(-2, 2),
                'vy': random.uniform(-4, -1),
                'life': random.uniform(0.2, 0.5),
                'max_life': 0.5
            })

    def update(self, dt, wind=1.8):
        for d in self.drops:
            d['y'] += d['speed']
            d['x'] += wind
            if d['y'] > HEIGHT + 30:
                if random.random() < 0.3:
                    self._add_splash(d['x'], HEIGHT - random.randint(10, 60))
                d.update(self._new_drop())
                d['y'] = random.randint(-20, 0)

        for p in self.splash_particles[:]:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['vy'] += 9 * dt
            p['life'] -= dt
            if p['life'] <= 0:
                self.splash_particles.remove(p)

    def draw(self, surf):
        self.surface.fill((0, 0, 0, 0))
        for d in self.drops:
            alpha = d['alpha']
            color = (160, 200, 240, alpha)
            ex = int(d['x'] + 4)
            ey = int(d['y'] + d['len'])
            pygame.draw.line(self.surface, color,
                             (int(d['x']), int(d['y'])),
                             (ex, ey), d['width'])
        for p in self.splash_particles:
            ratio = p['life'] / p['max_life']
            a = int(120 * ratio)
            pygame.draw.circle(self.surface, (180, 210, 240, a),
                                (int(p['x']), int(p['y'])), max(1, int(ratio * 3)))
        surf.blit(self.surface, (0, 0))


# ──────────────────────────────────────────────
#  MOUNTAIN / SKY PAINTER
# ──────────────────────────────────────────────
def draw_sky(surf, camera_x_offset, t):
    """Gradient sky with moving clouds and mountain silhouettes."""
    horizon_y = int(HEIGHT * HORIZON)

    # Sky gradient
    for y in range(horizon_y + 1):
        ratio = y / horizon_y
        r = int(SKY_TOP[0] + (SKY_BOT[0] - SKY_TOP[0]) * ratio)
        g = int(SKY_TOP[1] + (SKY_BOT[1] - SKY_TOP[1]) * ratio)
        b = int(SKY_TOP[2] + (SKY_BOT[2] - SKY_TOP[2]) * ratio)
        pygame.draw.line(surf, (r, g, b), (0, y), (WIDTH, y))

    # Storm clouds (layered)
    _draw_clouds(surf, t, horizon_y, camera_x_offset)

    # Mountain layers (parallax)
    ox = camera_x_offset * WIDTH * 0.5
    _draw_mountains(surf, horizon_y, ox)


def _draw_clouds(surf, t, horizon_y, cx):
    cloud_surf = pygame.Surface((WIDTH, horizon_y), pygame.SRCALPHA)
    for layer, (speed, alpha, size, y_off) in enumerate([
        (18, 55, 1.4, 0.25),
        (30, 40, 1.0, 0.55),
        (45, 25, 0.7, 0.80),
    ]):
        scroll = (t * speed * 0.4 + cx * 80 * (layer + 1)) % (WIDTH * 2.5)
        for i in range(6):
            bx = int((i * 240 - scroll + WIDTH * 1.2) % (WIDTH * 2.5)) - 120
            by = int(horizon_y * y_off - 20)
            w = int(180 * size + math.sin(t * 0.1 + i) * 15)
            h = int(55 * size)
            col = (120, 130, 145, alpha)
            _draw_cloud_blob(cloud_surf, bx, by, w, h, col)
    surf.blit(cloud_surf, (0, 0))


def _draw_cloud_blob(surf, x, y, w, h, col):
    for dx in range(-w // 2, w // 2, 15):
        for dy in range(-h // 2, h // 2, 12):
            r = int(h // 2 - abs(dx / w * h // 2))
            if r > 0:
                a = col[3] if len(col) == 4 else 255
                pygame.draw.circle(surf, col, (x + dx, y + dy), r)


def _draw_mountains(surf, horizon_y, ox):
    """Three-layer mountain silhouette with snow caps."""
    layers = [
        (MOUNTAIN_3, 0.55, 0.90, 220, True),
        (MOUNTAIN_2, 0.45, 0.80, 180, True),
        (MOUNTAIN_1, 0.35, 0.70, 140, False),
    ]
    for col, top_f, bot_f, amp, snow in layers:
        pts = [(0, horizon_y)]
        seed = hash(col)
        for xi in range(0, WIDTH + 80, 25):
            height = int(amp * (0.5 + 0.5 * math.sin(
                (xi + ox * 0.3) * 0.006 + seed +
                math.sin((xi + ox * 0.3) * 0.013 + seed * 2) * 0.5 +
                math.sin((xi + ox * 0.3) * 0.025 + seed * 3) * 0.25
            )))
            py = int(horizon_y * top_f - height)
            pts.append((xi, py))
        pts.append((WIDTH + 80, horizon_y))
        pygame.draw.polygon(surf, col, pts)

        if snow:
            # Snow on peaks
            snow_pts = []
            for i in range(1, len(pts) - 1):
                x, y = pts[i]
                if y < int(horizon_y * bot_f):
                    snow_pts.append((x, y))
                    if not snow_pts or snow_pts[-1][0] != x - 25:
                        snow_pts.append((x, min(y + 30, horizon_y)))
            if len(snow_pts) >= 3:
                for p in snow_pts:
                    pygame.draw.circle(surf, (220, 230, 240), p, 2)


# ──────────────────────────────────────────────
#  PSEUDO-3D ROAD RENDERER
# ──────────────────────────────────────────────
def project(world_x, world_y, world_z, cam_x, cam_y, cam_z, depth):
    """Project world point to screen."""
    if depth <= 0:
        return None
    scale = CAMERA_HEIGHT / depth  # simplified
    screen_x = int((0.5 + (world_x - cam_x) * scale) * WIDTH)
    screen_y = int((HORIZON + (-world_y + cam_y) * scale) * HEIGHT)
    return screen_x, screen_y, scale


def lerp_color(a, b, t):
    t = max(0, min(1, t))
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def fog_color(color, fog_amount):
    return lerp_color(color, FOG_COLOR, fog_amount)


def draw_road(surf, track, player, npcs):
    """Main pseudo-3D road renderer."""
    horizon_y = int(HEIGHT * HORIZON)
    n_segs = len(track.segments)

    start_idx = player.seg_index
    cam_z_offset = player.z - start_idx * SEG_LENGTH  # sub-segment offset

    # Camera position
    cam_x = player.camera_x
    cam_y = 0.0  # y from track height
    prev_x1 = None
    prev_x2 = None
    prev_y = horizon_y

    # Build visible segment list (back to front)
    visible = []
    track_x = 0.0
    track_y = 0.0
    curve_acc = 0.0
    pitch_acc = 0.0

    for i in range(DRAW_DISTANCE, -1, -1):
        idx = (start_idx + i) % n_segs
        seg = track.segments[idx]
        visible.append((i, idx, seg, curve_acc, pitch_acc, track_x, track_y))
        if i > 0:
            curve_acc  += seg['curve']
            pitch_acc  += seg['pitch']
            track_x    += curve_acc * 0.5
            track_y    += pitch_acc * 0.5

    max_i = DRAW_DISTANCE
    drawn_segments = []

    for (dist, idx, seg, ca, pa, sx, sy) in visible:
        fog = min(1.0, (dist / max_i) ** 1.2)
        depth = dist * SEG_LENGTH - cam_z_offset
        if depth <= 0.1:
            continue

        scale = (HEIGHT * CAMERA_HEIGHT) / (depth * 1.0)

        # Horizon projection
        center_x = WIDTH // 2 - int(cam_x * scale * WIDTH * 0.5) + int(sx * scale * 200)
        road_w = int(ROAD_WIDTH * scale)
        y_screen = horizon_y - int((sy - cam_y) * scale * 100)

        if y_screen < horizon_y - 10 or y_screen > HEIGHT + 50:
            continue

        y_screen = max(horizon_y, min(HEIGHT - 1, y_screen))

        l_road = center_x - road_w // 2
        r_road = center_x + road_w // 2
        screen_w = max(1, r_road - l_road)

        drawn_segments.append({
            'y': y_screen, 'ly': l_road, 'ry': r_road,
            'seg': seg, 'fog': fog, 'dist': dist,
            'cx': center_x, 'scale': scale, 'depth': depth
        })

    # Sort front to back
    drawn_segments.sort(key=lambda s: s['y'], reverse=True)

    prev_y = HEIGHT

    for ds in drawn_segments:
        y = ds['y']
        l = ds['ly']
        r = ds['ry']
        seg = ds['seg']
        fog = ds['fog']
        dist = ds['dist']

        if y >= prev_y:
            continue

        strip_h = max(1, prev_y - y)

        # Grass
        gc = fog_color(seg['grass'], fog)
        pygame.draw.rect(surf, gc, (0, y, WIDTH, strip_h))

        # Road
        rc = fog_color(ROAD_DARK if (dist // 2) % 2 == 0 else ROAD_LIGHT, fog)
        road_rect = (max(0, l), y, max(1, r - l), strip_h)
        pygame.draw.rect(surf, rc, road_rect)

        # Rumble strips
        rw = max(2, int((r - l) * 0.07))
        rub_c = fog_color(seg['rumble'], fog)
        pygame.draw.rect(surf, rub_c, (max(0, l), y, rw, strip_h))
        pygame.draw.rect(surf, rub_c, (min(WIDTH - rw, r - rw), y, rw, strip_h))

        # Centre dashes
        if strip_h > 2 and (dist // 4) % 2 == 0:
            cw = max(2, int((r - l) * 0.02))
            lc = fog_color(LINE_WHITE, fog)
            cx = (l + r) // 2
            pygame.draw.rect(surf, lc, (cx - cw // 2, y, cw, strip_h))

        # Wet sheen on road (reflection highlight)
        if strip_h >= 2:
            shine_alpha = max(0, int(40 * (1 - fog) * (1 - dist / max_i)))
            if shine_alpha > 5:
                shine_surf = pygame.Surface((r - l, strip_h), pygame.SRCALPHA)
                shine_surf.fill((180, 210, 230, shine_alpha))
                surf.blit(shine_surf, (l, y))

        prev_y = y

        # Draw roadside objects (trees, rocks)
        if dist < DRAW_DISTANCE * 0.75:
            for obj in seg['seg']['objects'] if 'objects' in seg else []:
                pass  # handled separately
            for obj in seg.get('objects', []):
                ox = ds['cx'] + int(obj['x'] * ds['scale'] * ROAD_WIDTH * 1.5)
                oy = y
                sz = max(2, int(obj['size'] * 60 * ds['scale'] * 12))
                if obj['type'] == 'tree':
                    _draw_tree(surf, ox, oy, sz, fog)
                elif obj['type'] == 'rock':
                    _draw_rock(surf, ox, oy, sz // 3, fog)

    # Draw NPCs (simple coloured boxes in pseudo-3D)
    for npc in npcs:
        _draw_npc(surf, npc, player, drawn_segments, max_i, cam_x)


def _get_obj_from_seg(ds):
    return ds['seg'].get('objects', [])


def _draw_tree(surf, x, y, size, fog):
    if size < 4 or y > HEIGHT or y < HEIGHT * HORIZON:
        return
    trunk_h = max(2, size // 4)
    trunk_w = max(2, size // 8)
    trunk_col = fog_color((80, 55, 35), fog)
    pygame.draw.rect(surf, trunk_col, (x - trunk_w // 2, y - trunk_h, trunk_w, trunk_h))
    # Three tiers of foliage
    for tier, (scale, y_off) in enumerate([(1.0, 0), (0.8, -size // 3), (0.6, -size * 2 // 3)]):
        w = max(2, int(size * scale * 0.8))
        h = max(2, int(size * scale * 0.5))
        ty = y - trunk_h - y_off - h // 2
        # Dark pine colour with fog
        base_g = (28, 75, 38)
        dark_g  = (18, 55, 25)
        col = fog_color(base_g if tier % 2 == 0 else dark_g, fog)
        pts = [(x, ty - h // 2), (x - w // 2, ty + h // 2), (x + w // 2, ty + h // 2)]
        if all(HEIGHT * 0.1 < p[1] < HEIGHT + 30 for p in pts):
            pygame.draw.polygon(surf, col, pts)
            # Snow on top
            snow = fog_color((210, 220, 230), fog * 0.5)
            snow_pts = [(x, ty - h // 2),
                        (x - w // 6, ty - h // 6),
                        (x + w // 6, ty - h // 6)]
            pygame.draw.polygon(surf, snow, snow_pts)


def _draw_rock(surf, x, y, size, fog):
    if size < 2 or y > HEIGHT:
        return
    col = fog_color((100, 100, 105), fog)
    pts = [(x - size, y), (x, y - size * 2), (x + size, y)]
    pygame.draw.polygon(surf, col, pts)
    pygame.draw.polygon(surf, fog_color((130, 130, 138), fog),
                        [(x - size + 2, y), (x - size // 3, y - size * 1.5), (x + size // 2, y)])


def _draw_npc(surf, npc, player, drawn_segments, max_i, cam_x):
    """Draw NPC car as a 3D box at its position."""
    rel_z = npc.z - player.z
    total = player.track.length
    # Wrap
    if rel_z > total / 2: rel_z -= total
    if rel_z < -total / 2: rel_z += total

    if rel_z <= 0 or rel_z > DRAW_DISTANCE * SEG_LENGTH * 0.9:
        return

    dist_seg = rel_z / SEG_LENGTH
    fog = min(1.0, (dist_seg / max_i) ** 1.2)
    depth = rel_z
    scale = (HEIGHT * CAMERA_HEIGHT) / (depth + 0.001)

    # Approximate screen position
    npc_seg_idx = npc.seg_index
    npc_seg = npc.track.segments[npc_seg_idx]
    offset_x = (npc.x - cam_x) * scale * ROAD_WIDTH * 0.5
    cx = WIDTH // 2 + int(offset_x)
    cy = int(HEIGHT * HORIZON + 0.5 * scale * 50)
    cy = max(int(HEIGHT * HORIZON), min(HEIGHT - 1, cy))

    car_w = max(4, int(70 * scale))
    car_h = max(3, int(45 * scale))

    if car_w < 3 or cy >= HEIGHT or cx < -car_w or cx > WIDTH + car_w:
        return

    body_col = fog_color(npc.color, fog)
    # Body
    pygame.draw.rect(surf, body_col, (cx - car_w // 2, cy - car_h, car_w, car_h))
    # Windshield
    ws_col = fog_color((160, 195, 220), fog)
    ws_w = max(2, int(car_w * 0.55))
    ws_h = max(1, int(car_h * 0.45))
    pygame.draw.rect(surf, ws_col, (cx - ws_w // 2, cy - car_h + 2, ws_w, ws_h))
    # Wheels
    wh_col = fog_color((25, 25, 28), fog)
    ww = max(2, int(car_w * 0.15))
    wh = max(1, int(car_h * 0.25))
    pygame.draw.rect(surf, wh_col, (cx - car_w // 2, cy - wh, ww, wh))
    pygame.draw.rect(surf, wh_col, (cx + car_w // 2 - ww, cy - wh, ww, wh))
    # Tail lights
    tl_col = fog_color((255, 60, 60), fog)
    pygame.draw.rect(surf, tl_col, (cx - car_w // 2, cy - car_h + car_h // 4, max(2, car_w // 6), max(1, car_h // 4)))
    pygame.draw.rect(surf, tl_col, (cx + car_w // 2 - car_w // 6, cy - car_h + car_h // 4, max(2, car_w // 6), max(1, car_h // 4)))


# ──────────────────────────────────────────────
#  DASHBOARD / STEERING WHEEL
# ──────────────────────────────────────────────
def draw_dashboard(surf, player, t):
    """Realistic-ish cockpit interior."""
    bw = WIDTH
    bh = HEIGHT

    # Dash panel
    dash_h = int(bh * 0.22)
    dash_y = bh - dash_h
    dash_col = (18, 18, 22)
    dash_surf = pygame.Surface((bw, dash_h), pygame.SRCALPHA)
    dash_surf.fill((*dash_col, 240))
    surf.blit(dash_surf, (0, dash_y))
    pygame.draw.line(surf, (60, 65, 80), (0, dash_y), (bw, dash_y), 2)

    # Interior door pillars (A-pillars)
    pillar_w = int(bw * 0.07)
    pillar_col = (15, 16, 20)
    pygame.draw.polygon(surf, pillar_col, [
        (0, 0), (pillar_w, 0), (int(bw * 0.04), bh)
    ])
    pygame.draw.polygon(surf, pillar_col, [
        (bw, 0), (bw - pillar_w, 0), (int(bw * 0.96), bh)
    ])

    # Steering wheel
    wheel_cx = bw // 2
    wheel_cy = dash_y + int(dash_h * 0.4)
    steer_angle = player.x * 35  # degrees
    _draw_steering_wheel(surf, wheel_cx, wheel_cy, 70, steer_angle, t, player.handbrake)

    # RPM bar (left of wheel)
    _draw_rpm_bar(surf, wheel_cx - 180, dash_y + 10, 120, dash_h - 20, player)

    # Speedometer arc (right of wheel)
    _draw_speedometer(surf, wheel_cx + 180, dash_y + dash_h // 2, 55, player)

    # Gear indicator
    font_big = pygame.font.SysFont("consolas", 36, bold=True)
    gear_s = "R" if player.speed < 0 else str(player.gear)
    gear_col = (255, 140, 0) if player.handbrake else (0, 220, 255)
    gt = font_big.render(gear_s, True, gear_col)
    surf.blit(gt, (wheel_cx - gt.get_width() // 2, dash_y + int(dash_h * 0.6)))

    # Lap indicator top
    font_sm = pygame.font.SysFont("consolas", 22, bold=True)
    lap_txt = font_sm.render(f"LAP  {player.lap} / {TOTAL_LAPS}", True, (180, 240, 180))
    surf.blit(lap_txt, (bw // 2 - lap_txt.get_width() // 2, 18))


def _draw_steering_wheel(surf, cx, cy, r, angle, t, handbrake):
    # Shadow
    pygame.draw.circle(surf, (10, 10, 14), (cx + 3, cy + 4), r)
    # Outer ring
    rim_col = (40, 40, 46) if not handbrake else (60, 20, 20)
    pygame.draw.circle(surf, rim_col, (cx, cy), r, 10)
    # Spokes
    for spoke_angle in [0, 120, 240]:
        a = math.radians(spoke_angle + angle)
        x1 = cx + int((r - 10) * math.cos(a))
        y1 = cy + int((r - 10) * math.sin(a))
        x2 = cx + int(12 * math.cos(a))
        y2 = cy + int(12 * math.sin(a))
        pygame.draw.line(surf, (50, 50, 58), (x1, y1), (x2, y2), 6)
    # Hub
    pygame.draw.circle(surf, (30, 30, 36), (cx, cy), 14)
    pygame.draw.circle(surf, (50, 52, 60), (cx, cy), 10)


def _draw_rpm_bar(surf, x, y, w, h, player):
    font = pygame.font.SysFont("consolas", 11)
    t = font.render("RPM", True, (80, 80, 100))
    surf.blit(t, (x + w // 2 - t.get_width() // 2, y))
    y += 18

    bar_h = h - 28
    ratio = min(1.0, player.engine_rpm / 7000)
    pygame.draw.rect(surf, (25, 28, 35), (x, y, w, bar_h))
    # Colour gradient: green → yellow → red
    for seg_i in range(10):
        sr = seg_i / 10
        if sr > ratio:
            break
        if sr < 0.6:
            c = lerp_color((0, 200, 80), (220, 200, 0), sr / 0.6)
        else:
            c = lerp_color((220, 200, 0), (220, 40, 40), (sr - 0.6) / 0.4)
        seg_y = y + bar_h - int(bar_h * (seg_i + 1) / 10)
        pygame.draw.rect(surf, c, (x + 2, seg_y, w - 4, bar_h // 12))

    rpm_t = font.render(f"{player.engine_rpm}", True, (100, 120, 140))
    surf.blit(rpm_t, (x + w // 2 - rpm_t.get_width() // 2, y + bar_h + 4))


def _draw_speedometer(surf, cx, cy, r, player):
    # Background arc
    pygame.draw.circle(surf, (22, 24, 30), (cx, cy), r)
    pygame.draw.circle(surf, (40, 44, 55), (cx, cy), r, 2)

    max_kmh = int(player.max_speed * 3.6)
    speed = player.kmh
    angle_start = math.radians(210)
    angle_range = math.radians(240)
    needle_a = angle_start - (speed / max_kmh) * angle_range

    # Tick marks
    for i in range(11):
        a = angle_start - (i / 10) * angle_range
        ix1 = cx + int((r - 6) * math.cos(a))
        iy1 = cy - int((r - 6) * math.sin(a))
        ix2 = cx + int((r - 14) * math.cos(a))
        iy2 = cy - int((r - 14) * math.sin(a))
        pygame.draw.line(surf, (100, 110, 130), (ix1, iy1), (ix2, iy2), 2)

    # Needle
    nx = cx + int((r - 10) * math.cos(needle_a))
    ny = cy - int((r - 10) * math.sin(needle_a))
    pygame.draw.line(surf, (0, 210, 255), (cx, cy), (nx, ny), 2)
    pygame.draw.circle(surf, (0, 210, 255), (cx, cy), 4)

    font = pygame.font.SysFont("consolas", 14, bold=True)
    t = font.render(f"{speed}", True, (0, 220, 255))
    surf.blit(t, (cx - t.get_width() // 2, cy + 12))
    t2 = pygame.font.SysFont("consolas", 9).render("KM/H", True, (70, 80, 100))
    surf.blit(t2, (cx - t2.get_width() // 2, cy + 28))


def lerp_color(a, b, t):
    t = max(0, min(1, t))
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


# ──────────────────────────────────────────────
#  MINIMAP
# ──────────────────────────────────────────────
def draw_minimap(mm_surf, track, player, npcs):
    mm_surf.fill((10, 12, 16))
    segs = track.segments
    if not segs:
        return

    xs = [s['x'] for s in segs]
    ys = [s['y'] for s in segs]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    rng = max(max_x - min_x, max_y - min_y, 1)
    pad = 10
    mw = mm.get_width()  # use global mm
    mh = mm.get_height()

    def to_mm(sx, sy):
        nx = int(pad + (sx - min_x) / rng * (mw - pad * 2))
        ny = int(pad + (sy - min_y) / rng * (mh - pad * 2))
        return (nx, ny)

    # Draw road
    pts = [to_mm(s['x'], s['y']) for s in segs[::3]]
    if len(pts) > 2:
        pygame.draw.lines(mm_surf, (60, 65, 80), True, pts, 3)
        pygame.draw.lines(mm_surf, (90, 100, 120), True, pts, 1)

    # Draw NPCs
    for npc in npcs:
        ns = segs[npc.seg_index]
        px, py = to_mm(ns['x'], ns['y'])
        pygame.draw.circle(mm_surf, npc.color, (px, py), 4)

    # Draw player
    ps = segs[player.seg_index]
    ppx, ppy = to_mm(ps['x'], ps['y'])
    pygame.draw.circle(mm_surf, (0, 220, 255), (ppx, ppy), 5)
    pygame.draw.circle(mm_surf, (255, 255, 255), (ppx, ppy), 5, 1)


# ──────────────────────────────────────────────
#  STANDINGS PANEL
# ──────────────────────────────────────────────
def get_standings(player, npcs):
    """Return list of (name, lap, z) sorted by progress."""
    entries = [("YOU", player.lap, player.z, True)]
    for npc in npcs:
        entries.append((npc.name, npc.lap, npc.z, False))
    # Sort by lap desc, then z desc
    entries.sort(key=lambda e: (e[1], e[2]), reverse=True)
    return entries


def draw_standings(surf, standings, font):
    panel_x, panel_y = 20, 70
    pygame.draw.rect(surf, (10, 12, 18, 180), (panel_x, panel_y, 175, len(standings) * 22 + 30))
    pygame.draw.rect(surf, (50, 55, 70), (panel_x, panel_y, 175, len(standings) * 22 + 30), 1)
    title = font.render("STANDINGS", True, (70, 80, 100))
    surf.blit(title, (panel_x + 8, panel_y + 8))
    for i, (name, lap, z, is_player) in enumerate(standings):
        col = (0, 220, 255) if is_player else (180, 185, 200)
        pos_t = font.render(f"P{i+1}", True, (120, 130, 150))
        name_t = font.render(name[:8], True, col)
        surf.blit(pos_t, (panel_x + 8, panel_y + 28 + i * 22))
        surf.blit(name_t, (panel_x + 38, panel_y + 28 + i * 22))


# ──────────────────────────────────────────────
#  LIGHTNING / ATMOSPHERE FLASH
# ──────────────────────────────────────────────
class Lightning:
    def __init__(self):
        self.flash_timer = 0
        self.next_flash = random.uniform(4, 12)
        self.bolt_pts = []
        self.bolt_timer = 0

    def update(self, dt):
        self.next_flash -= dt
        if self.next_flash <= 0:
            self.flash_timer = random.uniform(0.08, 0.18)
            self.next_flash = random.uniform(5, 15)
            self._gen_bolt()
        if self.flash_timer > 0:
            self.flash_timer -= dt
        if self.bolt_timer > 0:
            self.bolt_timer -= dt

    def _gen_bolt(self):
        self.bolt_timer = 0.25
        x = random.randint(WIDTH // 4, 3 * WIDTH // 4)
        y_start = random.randint(20, int(HEIGHT * 0.3))
        pts = [(x, y_start)]
        cy = y_start
        for _ in range(random.randint(6, 12)):
            cy += random.randint(20, 50)
            cx = pts[-1][0] + random.randint(-40, 40)
            pts.append((cx, cy))
            if cy > HEIGHT * HORIZON:
                break
        self.bolt_pts = pts

    def draw(self, surf):
        if self.flash_timer > 0:
            alpha = int(min(60, self.flash_timer * 400))
            flash_s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            flash_s.fill((200, 220, 255, alpha))
            surf.blit(flash_s, (0, 0))

        if self.bolt_timer > 0 and len(self.bolt_pts) >= 2:
            alpha = int(min(255, self.bolt_timer * 600))
            for i in range(len(self.bolt_pts) - 1):
                p1, p2 = self.bolt_pts[i], self.bolt_pts[i + 1]
                pygame.draw.line(surf, (220, 230, 255), p1, p2, 2)
                pygame.draw.line(surf, (180, 200, 255), p1, p2, 1)


# ──────────────────────────────────────────────
#  FINISH SCREEN
# ──────────────────────────────────────────────
def draw_finish(surf, standings, t):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 190))
    surf.blit(overlay, (0, 0))

    font_big = pygame.font.SysFont("consolas", 72, bold=True)
    font_med = pygame.font.SysFont("consolas", 28, bold=True)
    font_sm  = pygame.font.SysFont("consolas", 20)

    pulse = abs(math.sin(t * 2))
    col = lerp_color((0, 200, 100), (0, 255, 150), pulse)
    title = font_big.render("RACE COMPLETE", True, col)
    surf.blit(title, (WIDTH // 2 - title.get_width() // 2, 120))

    player_pos = next((i + 1 for i, (n, l, z, ip) in enumerate(standings) if ip), 1)
    pos_msg = ["🏆 VICTORY!", "P2 — WELL DONE!", "P3 — PODIUM!",
               "P4", "P5", "P6"][min(player_pos - 1, 5)]
    pos_t = font_med.render(pos_msg, True, (255, 220, 60))
    surf.blit(pos_t, (WIDTH // 2 - pos_t.get_width() // 2, 220))

    for i, (name, lap, z, is_player) in enumerate(standings):
        col = (0, 220, 255) if is_player else (160, 165, 180)
        t_line = font_sm.render(f"P{i+1}  {name}", True, col)
        surf.blit(t_line, (WIDTH // 2 - 100, 300 + i * 36))

    restart_t = font_sm.render("Press R to RESTART  ·  ESC to QUIT", True, (100, 110, 130))
    surf.blit(restart_t, (WIDTH // 2 - restart_t.get_width() // 2, HEIGHT - 80))


# ──────────────────────────────────────────────
#  MAIN GAME
# ──────────────────────────────────────────────
def run():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("ALPINE FURY — Mountain Rain Racer")
    clock = pygame.time.Clock()

    font_hud = pygame.font.SysFont("consolas", 13, bold=True)

    def new_game():
        track = Track()
        player = PlayerCar(track)
        npcs = []
        for i in range(NPC_COUNT):
            start_z = random.uniform(60, 400)
            npc = NPC(NPC_COLORS[i % len(NPC_COLORS)],
                      NPC_NAMES[i % len(NPC_NAMES)],
                      start_z, track)
            npcs.append(npc)
        rain = Rain(700)
        lightning = Lightning()
        return track, player, npcs, rain, lightning

    track, player, npcs, rain, lightning = new_game()

    game_state = "title"   # title | racing | finish
    t = 0.0
    lap_notify_timer = 0.0

    # Title screen
    title_font = pygame.font.SysFont("consolas", 80, bold=True)
    sub_font   = pygame.font.SysFont("consolas", 18)
    ctrl_font  = pygame.font.SysFont("consolas", 15)

    running = True
    while running:
        dt = min(clock.tick(FPS) / 1000.0, 0.05)
        t += dt
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if game_state == "title" and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    game_state = "racing"
                if game_state == "finish" and event.key == pygame.K_r:
                    track, player, npcs, rain, lightning = new_game()
                    game_state = "racing"
                if game_state == "finish" and event.key == pygame.K_ESCAPE:
                    running = False

        # ── TITLE SCREEN ──
        if game_state == "title":
            screen.fill((8, 10, 18))
            # Animated mountain background
            draw_sky(screen, math.sin(t * 0.1) * 0.05, t)
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            screen.blit(overlay, (0, 0))
            rain.update(dt)
            rain.draw(screen)
            lightning.update(dt)
            lightning.draw(screen)

            pulse = abs(math.sin(t * 1.5))
            col = lerp_color((0, 180, 255), (0, 255, 180), pulse)
            title_surf = title_font.render("ALPINE FURY", True, col)
            screen.blit(title_surf, (WIDTH // 2 - title_surf.get_width() // 2, HEIGHT // 2 - 160))

            sub = sub_font.render("MOUNTAIN RAIN CHAMPIONSHIP", True, (100, 120, 140))
            screen.blit(sub, (WIDTH // 2 - sub.get_width() // 2, HEIGHT // 2 - 60))

            blink = int(t * 2) % 2 == 0
            if blink:
                st = sub_font.render("[ PRESS ENTER TO RACE ]", True, (0, 220, 255))
                screen.blit(st, (WIDTH // 2 - st.get_width() // 2, HEIGHT // 2 + 20))

            controls = [
                "W / ↑   ACCELERATE",
                "S / ↓   BRAKE / REVERSE",
                "A / ←   STEER LEFT",
                "D / →   STEER RIGHT",
                "SPACE   HANDBRAKE",
            ]
            for i, line in enumerate(controls):
                ct = ctrl_font.render(line, True, (60, 70, 90))
                screen.blit(ct, (WIDTH // 2 - 120, HEIGHT // 2 + 100 + i * 24))

            pygame.display.flip()
            continue

        # ── RACING ──
        prev_lap = player.lap
        player.update(keys, dt)
        if player.lap > prev_lap and player.lap <= TOTAL_LAPS:
            lap_notify_timer = 2.0

        for npc in npcs:
            npc.update(dt, player.z)

        rain.update(dt, wind=1.5 + player.speed * 0.05)
        lightning.update(dt)

        if lap_notify_timer > 0:
            lap_notify_timer -= dt

        # ── CHECK RACE END ──
        if player.lap > TOTAL_LAPS:
            game_state = "finish"

        # ─── DRAW ───
        # Sky + mountains
        cam_x_norm = player.camera_x / 1.0
        draw_sky(screen, cam_x_norm, t)

        # Road
        draw_road(screen, track, player, npcs)

        # Rain
        rain.draw(screen)

        # Lightning
        lightning.draw(screen)

        # Dashboard
        draw_dashboard(screen, player, t)

        # Minimap
        mm_surf = pygame.Surface((140, 140))
        draw_minimap(mm_surf, track, player, npcs)
        screen.blit(mm_surf, (WIDTH - 155, 15))
        pygame.draw.rect(screen, (50, 55, 70), (WIDTH - 155, 15, 140, 140), 1)

        # Standings
        standings = get_standings(player, npcs)
        draw_standings(screen, standings, font_hud)

        # Lap notification
        if lap_notify_timer > 0:
            alpha = min(255, int(lap_notify_timer * 200))
            pulse = abs(math.sin(t * 6))
            col = lerp_color((100, 255, 100), (200, 255, 200), pulse)
            lf = pygame.font.SysFont("consolas", 52, bold=True)
            lt = lf.render(f"LAP {player.lap - 1} COMPLETE!", True, col)
            screen.blit(lt, (WIDTH // 2 - lt.get_width() // 2, HEIGHT // 2 - 60))

        # Weather bar top
        wf = pygame.font.SysFont("consolas", 13)
        wt = wf.render("⛈  ALPINE PASS  ·  WET TRACK  ·  4°C  ·  VISIBILITY LOW", True, (80, 100, 120))
        screen.blit(wt, (WIDTH // 2 - wt.get_width() // 2, 8))

        # Finish screen overlay
        if game_state == "finish":
            draw_finish(screen, standings, t)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    run()