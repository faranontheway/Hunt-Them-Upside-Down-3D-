from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import heapq
import random

WIN_W, WIN_H = 1000, 800
fovY = 50

camera_pos = [0, 900, 1300]
show_split = False

player_pos = [0.0, 0.0, 30.0]
player_facing = 180
vecna_power = 50.0

cheat_mode = False
demogorgons = []
MAX_DEMOS = 5

game_over = False
game_message = ""
game_restart = False
RESPAWN_DELAY = 80

maze = [
    [1,2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,1,1],
    [1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0,0,0,1],
    [1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,1,1,0,1],
    [1,0,1,0,0,0,1,0,0,0,1,0,0,0,0,0,1,0,1],
    [1,0,1,1,1,0,1,1,1,0,1,1,1,1,1,0,1,0,1],
    [1,0,0,0,1,0,0,0,1,0,0,0,0,0,1,0,0,0,1],
    [1,1,1,0,1,1,1,0,1,1,1,1,1,0,1,1,1,0,1],
    [1,0,0,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0,1],
    [1,0,1,1,1,0,1,1,1,0,1,0,1,1,1,0,1,0,1],
    [1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0,1,0,1],
    [1,1,1,0,1,1,1,0,1,1,1,0,1,1,1,0,1,0,1],
    [1,0,0,0,1,0,0,0,0,0,1,0,0,0,1,0,0,0,1],
    [1,0,1,1,1,0,1,1,1,0,1,1,1,0,1,1,1,0,1],
    [1,0,0,0,0,0,1,0,0,0,1,0,0,0,0,0,1,0,1],
    [1,1,1,1,1,0,1,0,1,1,1,0,1,0,1,1,1,0,1],
    [1,0,0,0,0,0,0,0,1,0,0,0,1,0,0,0,0,0,1],
    [1,0,1,1,1,1,1,0,1,1,1,0,1,1,1,1,1,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,1,1,1,1,1,1,1,1,1,2,1,1,1,1,1,1,1,1],
]

CELL = 60
WALL_HEIGHT = 120
ROWS = len(maze)
COLS = len(maze[0])

ORIGIN_X = -COLS * CELL / 2 + CELL / 2
ORIGIN_Y = -ROWS * CELL / 2 + CELL / 2

# Sticky floor
Count = 20
sticky_slow = 0.75

def is_path_cell(r, c):
    return 0 <= r < ROWS and 0 <= c < COLS and maze[r][c] == 0

sticky_cells = []

while len(sticky_cells) < Count:
    rr = random.randint(1, ROWS - 2)
    cc = random.randint(1, COLS - 2)

    if is_path_cell(rr, cc):
        if (rr, cc) not in sticky_cells:   #duplicates baad
            sticky_cells.append((rr, cc))


def cell_to_world(r, c):
    x = ORIGIN_X + c * CELL
    y = ORIGIN_Y + r * CELL
    return x, y

def world_to_cell(x, y):
    c = int(math.floor((x - ORIGIN_X) / CELL + 0.5))
    r = int(math.floor((y - ORIGIN_Y) / CELL + 0.5))
    r = max(0, min(ROWS - 1, r))
    c = max(0, min(COLS - 1, c))
    return r, c

def walkable(r, c):
    return 0 <= r < ROWS and 0 <= c < COLS and maze[r][c] != 1

def snap_to_nearest_path(x, y):
    r0, c0 = world_to_cell(x, y)
    if walkable(r0, c0):
        return cell_to_world(r0, c0)
    for rad in range(1, 7):
        for dr in range(-rad, rad + 1):
            for dc in range(-rad, rad + 1):
                rr = r0 + dr
                cc = c0 + dc
                if walkable(rr, cc):
                    return cell_to_world(rr, cc)
    return x, y

def random_path_cell_world():
    while True:
        r = random.randint(1, ROWS - 2)
        c = random.randint(1, COLS - 2)
        if walkable(r, c):
            return cell_to_world(r, c)

children = [ {'pos': list(random_path_cell_world()), 'color': (0.2, 0.4, 0.8),'alive': True, 'path': [], 'pi': 0,'health': 100, 'trap_hits': 0, 'respawn_timer': 0, 'dead': False, 'escaped': False},

             {'pos': list(random_path_cell_world()), 'color': (0.9, 0.3, 0.2), 'alive': True, 'path': [], 'pi': 0,'health': 100, 'trap_hits': 0,'respawn_timer': 0, 'dead': False, 'escaped': False},

             {'pos': list(random_path_cell_world()), 'color': (0.2, 0.8, 0.3), 'alive': True, 'path': [], 'pi': 0,'health': 100, 'trap_hits': 0, 'respawn_timer': 0, 'dead': False, 'escaped': False}
           ]

def h(a, b):
    return abs(a[0]-b[0]) + abs(a[1]-b[1])

def astar(start, goal):
    if start == goal:
        return [start]
    open_heap = []
    heapq.heappush(open_heap, (h(start, goal), 0, start))
    came = {}
    g = {start: 0}
    closed = set()

    while open_heap:
        prio,gcost,cur = heapq.heappop(open_heap)
        if cur in closed:
            continue
        closed.add(cur)

        if cur == goal:
            path = [cur]
            while cur in came:
                cur = came[cur]
                path.append(cur)
            path.reverse()
            return path

        r, c = cur
        for nr, nc in ((r+1,c),(r-1,c),(r,c+1),(r,c-1)):
            if not walkable(nr, nc):
                continue
            nxt = (nr, nc)
            ng = gcost + 1
            if nxt not in g or ng < g[nxt]:
                g[nxt] = ng
                came[nxt] = cur
                heapq.heappush(open_heap, (ng + h(nxt, goal), ng, nxt))

    return []


door_cells = []
for r in range(ROWS):
    for c in range(COLS):
        if maze[r][c] == 2:
            door_cells.append((r, c))

def compute_child_path_to_nearest_door(ch):
    sr, sc = world_to_cell(ch['pos'][0], ch['pos'][1])
    if not walkable(sr, sc):
        sx, sy = snap_to_nearest_path(ch['pos'][0], ch['pos'][1])
        ch['pos'][0], ch['pos'][1] = sx, sy
        sr, sc = world_to_cell(sx, sy)

    best = None
    for door in door_cells:
        path = astar((sr, sc), door)

        if path:
            if best is None:
                best = path
            else:
                if len(path) < len(best):
                    best = path


    if best is None:
        ch['path'] = []
    else:
        ch['path'] = best

    ch['pi'] = 0



# Draw
def draw_text(x, y, text):
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, WIN_W, 0, WIN_H)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glColor3f(1, 1, 1)
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)


def draw_bar(x, y, w, h, percent, fill_rgb, outline_rgb=(1,1,1)):

    if percent < 0:
        percent = 0
    elif percent > 100:
        percent = 100

    p = percent / 100.0

    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, WIN_W, 0, WIN_H)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    # outline
    glColor3f(*outline_rgb)
    glBegin(GL_LINE_LOOP)
    glVertex2f(x, y)
    glVertex2f(x + w, y)
    glVertex2f(x + w, y + h)
    glVertex2f(x, y + h)
    glEnd()

    # fill
    glColor3f(*fill_rgb)
    glBegin(GL_QUADS)
    glVertex2f(x, y)
    glVertex2f(x + w * p, y)
    glVertex2f(x + w * p, y + h)
    glVertex2f(x, y + h)
    glEnd()

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)



def draw_block(sx, sy, sz, r, g, b):
    glColor3f(r, g, b)
    glPushMatrix()
    glScalef(sx, sy, sz)
    glutSolidCube(1)
    glPopMatrix()

def draw_child(x, y, shirt_color):
    glPushMatrix()
    glTranslatef(x, y, 30)

    draw_block(16, 10, 24, *shirt_color)  # torso

    glPushMatrix()
    glTranslatef(0, 0, 22)
    draw_block(14, 12, 14, 0.95, 0.85, 0.75)  # head
    glPopMatrix()

    glPushMatrix()
    glTranslatef(0, 0, 30)
    draw_block(16, 14, 6, 0.15, 0.1, 0.05)  # hair
    glPopMatrix()

    for side in (-1, 1):  # arms
        glPushMatrix()
        glTranslatef(side * 14, 0, 6)
        draw_block(5, 5, 22, 0.95, 0.85, 0.75)
        glPopMatrix()

    for side in (-1, 1):  # legs
        glPushMatrix()
        glTranslatef(side * 6, 0, -20)
        draw_block(5, 5, 30, 0.2, 0.2, 0.4)
        glPopMatrix()

    glPopMatrix()


def draw_vecna():
    x, y, z = player_pos

    glPushMatrix()
    glTranslatef(x, y, z)
    glRotatef(player_facing, 0, 0, 1)


    # Legs
    glColor3f(0.4, 0.0, 0.0)
    glTranslatef(0, -10, 0)
    gluCylinder(gluNewQuadric(), 2, 5, 30, 30, 30)

    glTranslatef(0, 20, 0)
    gluCylinder(gluNewQuadric(), 2, 5, 30, 30, 30)

    # Body
    glColor3f(0.6, 0.0, 0)
    glTranslatef(0, -10, 55)
    glScalef(1, 1.5, 2.5)
    glutSolidCube(20)

    # Head
    glColor3f(0.4, 0, 0)
    glScalef(1, 0.7, 0.5)
    glTranslatef(0, 0, 30)
    gluSphere(gluNewQuadric(), 11, 50, 50)

    # Hands
    glColor3f(0.9, 0.0, 0.0)
    glTranslatef(0, -10, -20)
    glRotatef(90, 0, 1, 0)
    gluCylinder(gluNewQuadric(), 5, 2, 60, 30, 30)
    glTranslatef(0, 20, 0)
    gluCylinder(gluNewQuadric(), 5, 2, 60, 30, 30)


    glPopMatrix()


def draw_demogorgon(x, y):

        glPushMatrix()
        glTranslatef(x, y, 0)

        #BODY
        glColor3f(0.45, 0.35, 0.2)
        glPushMatrix()
        glTranslatef(0, 0, 45)
        glScalef(25, 18, 70)
        glutSolidCube(1)
        glPopMatrix()

        #HEAD CORE
        glColor3f(0.6, 0.2, 0.2)
        glPushMatrix()
        glTranslatef(0, 0, 95)
        glScalef(20, 20, 20)
        glutSolidCube(1)
        glPopMatrix()

        #flower mouth
        glColor3f(0.8, 0.3, 0.3)
        for angle in range(0, 360, 60):
            glPushMatrix()
            glRotatef(angle, 0, 0, 1)
            glTranslatef(18, 0, 95)
            glScalef(12, 6, 6)
            glutSolidCube(1)
            glPopMatrix()

        glPopMatrix()


#Draw maze
CELL_HALF = CELL / 2.0

def draw_floor():
    glColor3f(0.15, 0.15, 0.18)
    z = -5
    glBegin(GL_QUADS)
    glVertex3f(-3000,  3000, z)
    glVertex3f( 3000,  3000, z)
    glVertex3f( 3000, -3000, z)
    glVertex3f(-3000, -3000, z)
    glEnd()

def draw_maze():
    for r in range(ROWS):
        for c in range(COLS):
            x, y = cell_to_world(r, c)

            # base floor for paths + doors
            if maze[r][c] != 1:

                glColor3f(0.45, 0.15, 0.18)

                glBegin(GL_QUADS)
                glVertex3f(x - CELL_HALF, y - CELL_HALF, 0)
                glVertex3f(x + CELL_HALF, y - CELL_HALF, 0)
                glVertex3f(x + CELL_HALF, y + CELL_HALF, 0)
                glVertex3f(x - CELL_HALF, y + CELL_HALF, 0)
                glEnd()

            # sticky floor
            if (r, c) in sticky_cells:
                glColor3f(0.02, 0.02, 0.05)
                z = 2.0

                glBegin(GL_QUADS)
                glVertex3f(x - CELL_HALF + 6, y - CELL_HALF + 6, z)
                glVertex3f(x + CELL_HALF - 6, y - CELL_HALF + 6, z)
                glVertex3f(x + CELL_HALF - 6, y + CELL_HALF - 6, z)
                glVertex3f(x - CELL_HALF + 6, y + CELL_HALF - 6, z)
                glEnd()

            # door
            if maze[r][c] == 2:
                if (r, c) == safe_door:
                    glColor3f(0.1, 0.8, 0.2)  #my safe door
                else:
                    glColor3f(0.85, 0.05, 0.05)
                glBegin(GL_QUADS)
                glVertex3f(x - 18, y, 0)
                glVertex3f(x + 18, y, 0)
                glVertex3f(x + 18, y, 70)
                glVertex3f(x - 18, y, 70)
                glEnd()

            # wall
            if maze[r][c] == 1:
                glColor3f(0.25, 0.03, 0.05)
                for dx1, dy1, dx2, dy2 in [
                    (-1, -1,  1, -1),
                    (-1,  1,  1,  1),
                    (-1, -1, -1,  1),
                    ( 1, -1,  1,  1),
                ]:
                    glBegin(GL_QUADS)
                    glVertex3f(x + dx1 * CELL_HALF, y + dy1 * CELL_HALF, 0)
                    glVertex3f(x + dx2 * CELL_HALF, y + dy2 * CELL_HALF, 0)
                    glVertex3f(x + dx2 * CELL_HALF, y + dy2 * CELL_HALF, WALL_HEIGHT)
                    glVertex3f(x + dx1 * CELL_HALF, y + dy1 * CELL_HALF, WALL_HEIGHT)
                    glEnd()

                glColor3f(0.35, 0.08, 0.10)  # lighter top edge
                glBegin(GL_QUADS)
                glVertex3f(x - CELL_HALF, y - CELL_HALF, WALL_HEIGHT)
                glVertex3f(x + CELL_HALF, y - CELL_HALF, WALL_HEIGHT)
                glVertex3f(x + CELL_HALF, y + CELL_HALF, WALL_HEIGHT)
                glVertex3f(x - CELL_HALF, y + CELL_HALF, WALL_HEIGHT)
                glEnd()



# Camera
def setupCamera(w, h):
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, 1.25, 1.0, 5000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

def bird_eye_camera():
    x, y, z = camera_pos
    gluLookAt(x, y, z, 0, 0, 0, 0, 0, 1)

def first_person_camera():
    rad = math.radians(player_facing)
    fx, fy = math.cos(rad), math.sin(rad)
    gluLookAt(
        player_pos[0], player_pos[1], 55,
        player_pos[0] + fx * 100, player_pos[1] + fy * 100, 55,
        0, 0, 1
    )


def change_vecna_power(mult):
    global vecna_power

    vecna_power = vecna_power * mult
    if vecna_power < 0:
        vecna_power = 0
    elif vecna_power > 100:
        vecna_power = 100

def child_hit_trap(ch):
    global game_over, game_message, game_restart

    if ch['dead'] or ch['escaped']:
        return

    ch['trap_hits'] += 1
    ch['health'] -= 50

    # health doesn't go below 0
    if ch['health'] < 0:
        ch['health'] = 0
    change_vecna_power(1.2)

    # Second trap or zero health
    if ch['trap_hits'] >= 2 or ch['health'] <= 0:
        ch['alive'] = False
        ch['dead'] = True
        ch['respawn_timer'] = 0


        game_message = "ONE CHILD FELL ON THE TRAP AND DIED"
        game_restart = False

        check_game_over_conditions()
    else:
        # first trap only
        ch['alive'] = False
        ch['respawn_timer'] = RESPAWN_DELAY


safe_door = None
trap_doors = []

def update_doors():
    global safe_door, trap_doors
    ds = door_cells[:]
    random.shuffle(ds)
    safe_door = ds[0]
    trap_doors = [ds[1], ds[2]]

def child_escape(ch):
    global game_over
    if ch['dead'] or ch['escaped']:
        return

    ch['escaped'] = True
    ch['alive'] = False
    ch['respawn_timer'] = 0
    change_vecna_power(0.8)

    check_game_over_conditions()

def child_killed_by_vecna_or_demo(ch):
    if ch['dead'] or ch['escaped']:
        return
    ch['health'] = 0
    ch['alive'] = False
    ch['dead'] = True
    ch['respawn_timer'] = 0
    check_game_over_conditions()

def vecna_move(move):
    rad = math.radians(player_facing)
    fx, fy = math.cos(rad), math.sin(rad)
    nx = player_pos[0] + fx * move
    ny = player_pos[1] + fy * move
    r, c = world_to_cell(nx, ny)
    if walkable(r, c):
        player_pos[0], player_pos[1] = nx, ny

def update_children():
    global game_message

    base_speed = 1.25
    reach_eps = 8.0

    kill_dist = 40.0
    kill2 = kill_dist * kill_dist
    vx, vy = player_pos[0], player_pos[1]

    for ch in children:
        if ch['respawn_timer'] > 0:
            ch['respawn_timer'] -= 1
            if ch['respawn_timer'] == 0 and (not ch['dead']) and (not ch['escaped']):
                # respawn at random path
                px, py = random_path_cell_world()
                ch['pos'][0], ch['pos'][1] = px, py
                ch['alive'] = True
                compute_child_path_to_nearest_door(ch)
            continue

        if ch['dead'] or ch['escaped']:
            continue

        if not ch['alive']:
            continue

        # vecna kills child
        dxv = ch['pos'][0] - vx
        dyv = ch['pos'][1] - vy
        if dxv*dxv + dyv*dyv <= kill2:
            child_killed_by_vecna_or_demo(ch)
            continue


        if not ch['path']:
            compute_child_path_to_nearest_door(ch)
            if not ch['path']:
                continue


        # If child is already at last node(door)
        if ch['pi'] >= len(ch['path']) - 1:
            rr, cc = ch['path'][-1]
            if maze[rr][cc] == 2:
                if (rr, cc) == safe_door:
                    child_escape(ch)
                else:
                    child_hit_trap(ch)
            continue


        #  Sticky speed slow
        cr, cc = world_to_cell(ch['pos'][0], ch['pos'][1])
        speed = base_speed
        if (cr, cc) in sticky_cells:
            speed = base_speed * sticky_slow

        # move toward next path cell
        nxt = ch['path'][ch['pi'] + 1]
        tx, ty = cell_to_world(nxt[0], nxt[1])

        cx, cy = ch['pos'][0], ch['pos'][1]
        dx = tx - cx
        dy = ty - cy
        dist = math.sqrt(dx*dx + dy*dy)

        if dist < reach_eps:
            ch['pi'] += 1

            # if stepped into a door cell
            rr, cc2 = ch['path'][ch['pi']]
            if maze[rr][cc2] == 2:
                if (rr, cc2) == safe_door:
                    child_escape(ch)
                else:
                    child_hit_trap(ch)

            continue

        # normal movement
        ch['pos'][0] += (dx / dist) * speed
        ch['pos'][1] += (dy / dist) * speed


def update_demogorgons():
    if not cheat_mode:
        return

    demo_speed = 3.5
    catch_dist = 35.0
    catch2 = catch_dist * catch_dist

    for d in demogorgons:
        if not d.get('alive', True):
            continue

        # always find nearest child
        target = None
        bestd = 10**18
        for ch in children:
            if not ch['alive']:
                continue
            dx = ch['pos'][0] - d['pos'][0]
            dy = ch['pos'][1] - d['pos'][1]
            dist2 = dx*dx + dy*dy
            if dist2 < bestd:
                bestd = dist2
                target = ch

        if target is None:
            continue
        dx = target['pos'][0] - d['pos'][0]
        dy = target['pos'][1] - d['pos'][1]

        # dhore felle child dead
        if dx * dx + dy * dy <= catch2:
            child_killed_by_vecna_or_demo(target)
            continue

        dist = math.sqrt(dx*dx + dy*dy)
        if dist > 0.0001:
            d['pos'][0] += (dx / dist) * demo_speed
            d['pos'][1] += (dy / dist) * demo_speed

def check_game_over_conditions():
    global game_over, game_restart, game_message

    escaped = 0
    dead = 0
    alive = 0

    for ch in children:
        if ch['escaped']:
            escaped += 1
        elif ch['dead']:
            dead += 1
        else:
            alive += 1

    if alive > 0:
        return


    # possible cases
    if escaped >= 2 and dead >= 1:
        game_over = True
        game_restart = True
        game_message = "GAME OVER! You lost. Press R to restart"
        return

    if escaped == 1 and dead == 2:
        game_over = True
        game_restart = True
        game_message = "GAME OVER! You won. Press R to restart"
        return

    if escaped == len(children):
        game_over = True
        game_restart = True
        game_message = "GAME OVER! You lost. Press R to restart"
        return

    if dead == len(children):
        game_over = True
        game_restart = True
        if cheat_mode:
            game_message = "CONGRATULATIONS YOU WON! Press R to restart"
        else:
            game_message = "GAME OVER! You won. Press R to restart"
        return


def restart_game():
    global cheat_mode, demogorgons, vecna_power, game_over, game_restart, game_message
    global player_pos, player_facing

    cheat_mode = False
    demogorgons = []

    vecna_power = 50.0
    player_pos[0], player_pos[1] = random_path_cell_world()
    player_facing = 180

    game_over = False
    game_restart = False
    game_message = ""

    update_doors()

    for ch in children:
        ch['pos'] = list(random_path_cell_world())
        ch['alive'] = True
        ch['dead'] = False
        ch['escaped'] = False
        ch['health'] = 100
        ch['trap_hits'] = 0
        ch['respawn_timer'] = 0
        ch['path'] = []
        ch['pi'] = 0
        compute_child_path_to_nearest_door(ch)

def keyboardListener(key, x, y):
    global show_split, player_facing, cheat_mode, demogorgons

    step = 12.0
    rot_step = 6.0

    if key == b'v' or key == b'V':
        show_split = not show_split
        return
    if key == b'r' or key == b'R':
        if game_over or game_restart:
            restart_game()
        return

    if key == b'c' or key == b'C':
        cheat_mode = not cheat_mode
        if cheat_mode:
            demogorgons = []
            count = 0
            while count < MAX_DEMOS:
                px, py = random_path_cell_world()
                demogorgons.append({'pos': [px, py], 'alive': True})
                count += 1
        else:
            demogorgons = []
        return

    if key == b'a' or key == b'A':
        player_facing += rot_step
        return
    if key == b'd'or key == b'D':
        player_facing -= rot_step
        return

    if key == b'w' or key == b'W':
        vecna_move(step)
        return
    if key == b's' or key == b'S':
        vecna_move(-step)
        return

def specialKeyListener(key, x, y):
    move_speed = 70
    rot_speed = 9.0

    if key == GLUT_KEY_UP:
        camera_pos[2] += move_speed
    if key == GLUT_KEY_DOWN:
        camera_pos[2] -= move_speed

    if key == GLUT_KEY_LEFT:
        a = math.radians(rot_speed)
        camera_pos[0], camera_pos[1] = (
            camera_pos[0] * math.cos(a) - camera_pos[1] * math.sin(a),
            camera_pos[0] * math.sin(a) + camera_pos[1] * math.cos(a)
        )

    if key == GLUT_KEY_RIGHT:
        a = math.radians(-rot_speed)
        camera_pos[0], camera_pos[1] = (
            camera_pos[0] * math.cos(a) - camera_pos[1] * math.sin(a),
            camera_pos[0] * math.sin(a) + camera_pos[1] * math.cos(a)
        )

def idle():
    update_children()
    update_demogorgons()
    glutPostRedisplay()


def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    if show_split:
        glViewport(0, 0, WIN_W // 2, WIN_H)
        setupCamera(WIN_W // 2, WIN_H)
        bird_eye_camera()
        draw_floor()
        draw_maze()

        for ch in children:
            if ch['alive']:
                draw_child(ch['pos'][0], ch['pos'][1], ch['color'])

        draw_vecna()

        if cheat_mode:
            for d in demogorgons:
                if d.get('alive', True):
                    draw_demogorgon(d['pos'][0], d['pos'][1])
        glViewport(WIN_W // 2, 0, WIN_W // 2, WIN_H)
        setupCamera(WIN_W // 2, WIN_H)
        first_person_camera()
        draw_floor()
        draw_maze()
        for ch in children:
            if ch['alive']:
                draw_child(ch['pos'][0], ch['pos'][1], ch['color'])


        if cheat_mode:
            for d in demogorgons:
                if d.get('alive', True):
                    draw_demogorgon(d['pos'][0], d['pos'][1])

    else:
        glViewport(0, 0, WIN_W, WIN_H)
        setupCamera(WIN_W, WIN_H)
        bird_eye_camera()
        draw_floor()
        draw_maze()
        draw_vecna()
        for ch in children:
            if ch['alive']:
                draw_child(ch['pos'][0], ch['pos'][1], ch['color'])

        if cheat_mode:
            for d in demogorgons:
                if d.get('alive', True):
                    draw_demogorgon(d['pos'][0], d['pos'][1])

    for i, j in enumerate(children):
        draw_text(10, 700 - i * 30 + 18, f"Child {i + 1} Health:" )
        draw_bar(10 + 140, 700 - i * 30 + 15, 180, 15,
                 j['health'], fill_rgb=(0.8, 0.05, 0.05), outline_rgb=(1, 1, 1))

    draw_text(WIN_W - 240 -18, WIN_H-100 +20,"Vecna Power:")
    draw_bar(WIN_W -240-18, WIN_H-100, 240, 16, vecna_power,
             fill_rgb=(0.2, 0.85, 0.25), outline_rgb=(1, 1, 1))

    status = "ACTIVATED" if cheat_mode else "DEACTIVATED"
    draw_text(400, WIN_H - 100, f" Cheat Mode :{status}")

    if game_over and game_message:
        draw_text(250, WIN_H // 2, game_message)

    if game_restart and game_over:
        draw_text(350, WIN_H // 2 - 30, "PRESS R TO RESTART")


    glutSwapBuffers()


def main():

    player_pos[0], player_pos[1] = snap_to_nearest_path(player_pos[0], player_pos[1])
    for ch in children:
        compute_child_path_to_nearest_door(ch)

    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(WIN_W, WIN_H)
    glutCreateWindow(b"Hunt them Upside Down")

    glEnable(GL_DEPTH_TEST)
    glClearColor(0.05, 0.05, 0.1, 1)

    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutIdleFunc(idle)
    restart_game()

    glutMainLoop()



if __name__ == "__main__":
    main()


