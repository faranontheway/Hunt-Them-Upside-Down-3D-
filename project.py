"""
3D Solar System Simulator (single-file)
Dependencies: PyOpenGL, pygame, numpy

Controls:
 - Mouse drag (left) : orbit camera around center
 - Mouse wheel       : zoom in/out
 - Space             : pause / resume simulation
 - + (plus)          : speed up time
 - - (minus)         : slow down time
 - r                 : reset time and camera
 - Esc or close      : quit
"""

import sys
import math
import random


from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
from time import perf_counter

# ---------- Configuration ----------
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
FPS_CAP = 60

# Planets configuration
# name, distance_from_sun, radius, orbit_period (seconds at speed=1), color (r,g,b), spin_period
PLANETS = [
    ("Mercury", 3.8, 0.2, 10.0, (0.7, 0.6, 0.5), 10.0),
    ("Venus",   5.8, 0.35, 15.0, (0.9, 0.7, 0.2), 20.0),
    ("Earth",   8.0, 0.45, 20.0, (0.2, 0.4, 0.9), 1.0),
    ("Mars",    10.5, 0.32, 30.0, (0.9, 0.3, 0.2), 1.03),
    ("Jupiter", 14.0, 1.0,  60.0, (0.9, 0.6, 0.4), 0.4),
    ("Saturn",  18.0, 0.85, 80.0, (0.95, 0.9, 0.6), 0.45),
    ("Uranus",  21.0, 0.6,  120.0, (0.6, 0.85, 0.9), 0.72),
    ("Neptune", 24.0, 0.6,  160.0, (0.3, 0.55, 0.9), 0.67),
]

# Add a moon for Earth (demonstrates hierarchical transform)
MOONS = [
    # parent_idx (planet index in PLANETS), distance_from_parent, radius, orbit_period, color
    (2, 0.9, 0.12, 4.0, (0.8, 0.8, 0.8)),  # Moon orbiting Earth
]

# Starfield config
NUM_STARS = 800

# GLU quadric for spheres
quad = None

# ---------- Helper functions ----------
def normalize(v):
    v = np.array(v, dtype=float)
    n = np.linalg.norm(v)
    if n == 0:
        return v
    return v / n

def setup_light():
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    # Light positioned at the Sun
    light_pos = [0.0, 0.0, 0.0, 1.0]  # positional light at origin
    glLightfv(GL_LIGHT0, GL_POSITION, light_pos)
    # bright warm light
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 0.98, 0.92, 1.0])
    glLightfv(GL_LIGHT0, GL_SPECULAR, [0.8, 0.8, 0.8, 1.0])
    glLightfv(GL_LIGHT0, GL_AMBIENT, [0.03, 0.03, 0.03, 1.0])
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

def init_gl():
    global quad
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LEQUAL)
    glShadeModel(GL_SMOOTH)
    glEnable(GL_NORMALIZE)
    setup_light()
    quad = gluNewQuadric()
    gluQuadricNormals(quad, GLU_SMOOTH)
    gluQuadricTexture(quad, GL_FALSE)
    # Nice perspective
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0, (WINDOW_WIDTH / WINDOW_HEIGHT), 0.1, 200.0)
    glMatrixMode(GL_MODELVIEW)

# ---------- Camera ----------
class Camera:
    def __init__(self, distance=35.0, yaw=0.0, pitch=20.0):
        self.distance = distance
        self.yaw = yaw    # degrees
        self.pitch = pitch  # degrees
        self.min_distance = 5.0
        self.max_distance = 100.0

    def apply(self):
        # Transform camera: translate back, then rotate to yaw/pitch
        glLoadIdentity()
        # first move back
        glTranslatef(0.0, 0.0, -self.distance)
        # then rotate pitch then yaw (because camera looks toward origin)
        glRotatef(self.pitch, 1.0, 0.0, 0.0)
        glRotatef(self.yaw, 0.0, 1.0, 0.0)

    def zoom(self, delta):
        self.distance -= delta
        if self.distance < self.min_distance:
            self.distance = self.min_distance
        if self.distance > self.max_distance:
            self.distance = self.max_distance

# ---------- Starfield ----------
def generate_stars(num):
    # generate points in sphere shell
    stars = []
    for _ in range(num):
        # random direction
        theta = random.random() * 2.0 * math.pi
        phi = math.acos(2.0 * random.random() - 1.0)
        r = random.uniform(60.0, 95.0)
        x = r * math.sin(phi) * math.cos(theta)
        y = r * math.sin(phi) * math.sin(theta)
        z = r * math.cos(phi)
        stars.append((x, y, z))
    return stars

# ---------- Drawing ----------
def draw_starfield(stars):
    glDisable(GL_LIGHTING)
    glPointSize(1.2)
    glBegin(GL_POINTS)
    for s in stars:
        glColor3f(1.0, 1.0, 1.0)
        glVertex3f(*s)
    glEnd()
    glEnable(GL_LIGHTING)

def draw_sun(radius=2.5):
    # Sun emits light: draw as emissive sphere
    glPushMatrix()
    glDisable(GL_LIGHTING)
    # simple bright yellow disc (billboard) + sphere
    glColor3f(1.0, 0.9, 0.2)
    # Use full-bright by enabling emission material then disabling lighting
    glut_sphere(radius, (1.0, 0.9, 0.2), emissive=True)
    glEnable(GL_LIGHTING)
    glPopMatrix()

def glut_sphere(radius, color=(1,1,1), emissive=False):
    # set material color
    glColor3f(*color)
    if emissive:
        glMaterialfv(GL_FRONT_AND_BACK, GL_EMISSION, list(color) + [1.0])
    else:
        glMaterialfv(GL_FRONT_AND_BACK, GL_EMISSION, [0.0, 0.0, 0.0, 1.0])
    gluSphere(quad, radius, 36, 18)
    # reset emission
    if emissive:
        glMaterialfv(GL_FRONT_AND_BACK, GL_EMISSION, [0.0, 0.0, 0.0, 1.0])

def draw_planet(planet, orbit_angle, spin_angle):
    # planet: (name, dist, radius, orbit_period, color, spin_period)
    name, dist, radius, orbit_period, color, spin_period = planet
    # move to orbit position (on xz-plane; y=0)
    x = dist * math.cos(math.radians(orbit_angle))
    z = dist * math.sin(math.radians(orbit_angle))
    glPushMatrix()
    glTranslatef(x, 0.0, z)
    # rotate about tilt axis for spin (here we keep tilt 0)
    glRotatef(spin_angle, 0.0, 1.0, 0.0)
    # set color and draw sphere
    glut_sphere(radius, color, emissive=False)
    glPopMatrix()

# ---------- HUD text rendering (pygame surface -> texture) ----------
def text_to_texture(text, font, color=(255,255,255)):
    surface = font.render(text, True, color)
    data = pygame.image.tostring(surface, "RGBA", True)
    w, h = surface.get_size()
    texid = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texid)
    glPixelStorei(GL_UNPACK_ALIGNMENT,1)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE, data)
    return texid, w, h

def draw_textured_quad(texid, w, h, x, y):
    # Assumes orthographic projection and modelview identity
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, texid)
    glColor3f(1,1,1)
    glBegin(GL_QUADS)
    glTexCoord2f(0,1); glVertex2f(x, y)
    glTexCoord2f(1,1); glVertex2f(x + w, y)
    glTexCoord2f(1,0); glVertex2f(x + w, y + h)
    glTexCoord2f(0,0); glVertex2f(x, y + h)
    glEnd()
    glDeleteTextures([texid])
    glDisable(GL_TEXTURE_2D)

# ---------- Main ----------
def main():
    pygame.init()
    pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("3D Solar System Simulator - PyOpenGL + Pygame")
    clock = pygame.time.Clock()
    init_gl()

    font = pygame.font.SysFont("Arial", 18)

    # stars
    stars = generate_stars(NUM_STARS)

    cam = Camera(distance=35.0, yaw=30.0, pitch=20.0)
    dragging = False
    last_mouse = (0,0)

    # simulation timing
    sim_time = 0.0
    paused = False
    time_speed = 1.0  # multiplier; 1.0 is normal
    last_t = perf_counter()

    running = True
    while running:
        # event handling
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
                elif event.key == K_SPACE:
                    paused = not paused
                elif event.key == K_PLUS or event.key == K_EQUALS:
                    time_speed *= 2.0
                    if time_speed > 64.0:
                        time_speed = 64.0
                elif event.key == K_MINUS or event.key == K_UNDERSCORE:
                    time_speed /= 2.0
                    if time_speed < 0.03125:
                        time_speed = 0.03125
                elif event.key == K_r:
                    sim_time = 0.0
                    cam.distance = 35.0
                    cam.yaw, cam.pitch = 30.0, 20.0
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    dragging = True
                    last_mouse = event.pos
                elif event.button == 4:  # wheel up
                    cam.zoom(-2.0)
                elif event.button == 5:  # wheel down
                    cam.zoom(2.0)
            elif event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    dragging = False
            elif event.type == MOUSEMOTION and dragging:
                x, y = event.pos
                dx = x - last_mouse[0]
                dy = y - last_mouse[1]
                last_mouse = (x, y)
                cam.yaw += dx * 0.3
                cam.pitch += dy * 0.3
                if cam.pitch > 89.0: cam.pitch = 89.0
                if cam.pitch < -89.0: cam.pitch = -89.0

        # timing
        now = perf_counter()
        dt = now - last_t
        last_t = now
        if not paused:
            sim_time += dt * time_speed

        # clear
        glClearColor(0.02, 0.02, 0.03, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # camera
        cam.apply()

        # Draw starfield (far away)
        draw_starfield(stars)

        # Draw Sun at origin
        glPushMatrix()
        draw_sun(radius=2.6)
        glPopMatrix()

        # Draw planets
        # compute orbit angle (degrees) for each planet
        for idx, planet in enumerate(PLANETS):
            name, dist, radius, orbit_period, color, spin_period = planet
            # orbit angle in degrees (full revolution = 360)
            if orbit_period <= 0:
                orbit_angle = 0.0
            else:
                orbit_angle = (sim_time / orbit_period) * 360.0
            # spin angle (planet rotation on axis)
            if spin_period <= 0:
                spin_angle = 0.0
            else:
                spin_angle = (sim_time / spin_period) * 360.0
            # optionally, make different inclinations or speeds by offsetting orbit angle by idx*somevalue
            draw_planet(planet, orbit_angle + idx * 7.0, spin_angle)

        # Draw moons (hierarchical transforms)
        for moon in MOONS:
            parent_idx, m_dist, m_radius, m_orbit_period, m_color = moon
            # parent's angle and position:
            pname, pdist, pradius, porbit_period, pcolor, pspin_period = PLANETS[parent_idx]
            parent_angle = (sim_time / porbit_period) * 360.0 if porbit_period > 0 else 0.0
            px = pdist * math.cos(math.radians(parent_angle + parent_idx * 7.0))
            pz = pdist * math.sin(math.radians(parent_angle + parent_idx * 7.0))
            # moon orbit angle
            m_angle = (sim_time / m_orbit_period) * 360.0
            mx = px + m_dist * math.cos(math.radians(m_angle))
            mz = pz + m_dist * math.sin(math.radians(m_angle))
            glPushMatrix()
            glTranslatef(mx, 0.0, mz)
            glut_sphere(m_radius, m_color, emissive=False)
            glPopMatrix()

        # Simple orbit rings (wire loops) for visualization
        glDisable(GL_LIGHTING)
        glColor3f(0.5, 0.5, 0.5)
        for idx, p in enumerate(PLANETS):
            name, dist, radius, orbit_period, color, spin_period = p
            glBegin(GL_LINE_LOOP)
            for a in range(0, 360, 6):
                x = dist * math.cos(math.radians(a + idx * 7.0))
                z = dist * math.sin(math.radians(a + idx * 7.0))
                glVertex3f(x, 0.0, z)
            glEnd()
        glEnable(GL_LIGHTING)

        # HUD: draw time speed & instructions using texture quads
        hud_lines = [
            f"Time speed: {time_speed:.3f}x {'(paused)' if paused else ''}",
            "Controls: Drag mouse = rotate camera | Wheel = zoom | Space = pause",
            "Press + / - to change speed, R to reset, Esc to quit"
        ]
        # switch to orthographic for HUD
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, WINDOW_WIDTH, WINDOW_HEIGHT, 0, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        glDisable(GL_DEPTH_TEST)
        # render text lines
        x = 10
        y = 10
        for i, line in enumerate(hud_lines):
            texid, w, h = text_to_texture(line, font, (255,255,255))
            draw_textured_quad(texid, w, h, x, y + i * (h + 4))
        glEnable(GL_DEPTH_TEST)
        # restore projection/modelview
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)

        # swap
        pygame.display.flip()
        clock.tick(FPS_CAP)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
