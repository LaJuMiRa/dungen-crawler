# Imports

import os
import random
import time

import readchar
from colorist import BgColor, Color

###############################################################################################
# classes


class Entity:
    #:datentyp zeigt nur an welchen Datentyp die jeweilige Variable hat
    def __init__(
        self,
        sign: str,
        pos_x: int,
        pos_y: int,
        level: int,
        health: int,
        attack: int,
        defense: int,
        alive: bool,
        is_monster: bool,
        sense,
        color,
        side,
    ):
        self.sign = sign
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.level = level
        self.health = health
        self.attack = attack
        self.defense = defense
        self.alive = alive
        self.is_monster = is_monster
        self.sense = sense
        self.color = color
        self.side = side

    def get_health(
        self,
    ) -> int:  # -> zeigt an welchen Datentypen die funktion zurück gibt.
        return self.health

    @property  # wird bei jedem Tick ausgeführt
    def is_alive(self) -> bool:
        return self.health > 0


class Player(Entity):
    def __init__(
        self,
        sign: str,
        pos_x: int,
        pos_y: int,
        level: int,
        health: int,
        attack: int,
        defense: int,
        alive: bool,
        is_monster: bool,
        sense,
        color,
        side,
    ):
        super().__init__(
            sign,
            pos_x,
            pos_y,
            level,
            health,
            attack,
            defense,
            alive,
            is_monster,
            sense,
            color,
            side,
        )


class Item:
    def __init__(
        self,
        sign: str,
        pos_x: int,
        pos_y: int,
        type: str,
        taken: bool,
        color,
        bonus: int,
    ):
        self.sign = sign
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.type = type
        self.taken = taken
        self.color = color
        self.bonus = bonus


class Trap:
    def __init__(
        self,
        sign: str,
        pos_x: int,
        pos_y: int,
        stat: str,
        triggered: bool,
        color,
    ):
        self.sign = sign
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.stat = stat
        self.triggered = triggered
        self.color = color

    @property
    def is_triggered(self) -> bool:
        return self.triggered


class Queue:
    def __init__(self):
        self.data = []
        self.kopf = 0

    def enqueue(self, item):
        self.data.append(item)

    def dequeue(self):
        item = self.data[self.kopf]
        self.kopf += 1
        return item

    def is_empty(self):
        return self.kopf >= len(self.data)


###############################################################################################
# initialize variables


FLOOR = 0
WALL = 1
DOOR_P1 = 2
DOOR_P2 = 3
door_pos_p1 = None
door_pos_p2 = None

# Colors
RED = Color.RED
GREEN = Color.GREEN
MAGENTA = Color.MAGENTA
CYAN = Color.CYAN
BLACK = Color.BLACK
BLUE = Color.BLUE
WHITE = Color.WHITE
BG_BLUE = BgColor.BLUE
BG_GREEN = BgColor.GREEN
BG_WHITE = BgColor.WHITE

monster = []
monster_placed = []
dragon = Entity("D", 0, 0, 4, 20, 6, 3, True, True, 12, RED, "b")
gremlin = Entity("g", 0, 0, 2, 6, 2, 1, True, True, 8, RED, "b")
gnome = Entity("G", 0, 0, 1, 5, 2, 2, True, True, 6, RED, "b")
jelly = Entity("J", 0, 0, 3, 8, 3, 0, True, True, 10, RED, "b")
monster.append(dragon)
monster.append(gremlin)
monster.append(gnome)
monster.append(jelly)

traps = []
falltuer = []
giftwolke = []
items = []

player = Player("@", 1, 1, 1, 10, 3, 1, True, False, None, BLUE, "l")
p2 = None
p2_phase = 1  # sagt uns ob Items gesammel, Monster gejagt oder Spieler gejagt wird
p2_ziel_item = None
p2_ziel_monster = None
player_monster_killed = 0
player_items_collected = 0

terminal = os.get_terminal_size()
TERMINAL_X = terminal.columns
TERMINAL_Y = terminal.lines

if TERMINAL_X < 80 or TERMINAL_Y < 30:
    print(
        f"Terminal ist zu klein {RED}({TERMINAL_X}x{TERMINAL_Y}){Color.OFF}. Mindestens {GREEN}80x30{Color.OFF} Pixel nötig"
    )
    exit()  # Terminal Größe muss stimmen --> nicht play

maze = []
maze_wall = (TERMINAL_X - 1, TERMINAL_X + 1)


###############################################################################################
# Maze-Gen
def fill_maze_with_walls(col_x, row_y):
    return [
        [WALL] * col_x for _ in range(row_y)
    ]  # schreibt in eine Liste WALL col_x mal und das macht es row_y mal


def maze_creation(grid, terminal_x, terminal_y):
    start_col = 1
    start_row = 1
    grid[start_row][start_col] = FLOOR
    weg = [
        (start_row, start_col)
    ]  # weg merkt sich den breits gegangen Weg mit (x,y) werten

    richtungen = [
        (0, -2),  # nach oben um 2 Felder
        (0, 2),  # nach unten um 2 Felder
        (-2, 0),  # nach links um 2 Felder
        (2, 0),  # nach rechts um 2 Felder
    ]

    while len(weg) > 0:
        jetzt_col, jetzt_row = weg[-1]
        nachbar = []  # hier werden die Nachbarn gespeichert, die potentiell ein FLOOR sein können

        for richtung_x, richtung_y in richtungen:
            nachbar_col = jetzt_col + richtung_x
            nachbar_row = jetzt_row + richtung_y

            innerhalb_grid = (
                1 <= nachbar_col < terminal_x - 1 and 1 <= nachbar_row < terminal_y - 1
            )  # true or false wert ob innerhalb des Grids befindet

            if not innerhalb_grid:
                continue  # geht zur nächsten Iteration

            noch_nicht_besucht = grid[nachbar_row][nachbar_col] == WALL

            if noch_nicht_besucht:
                nachbar.append(
                    (nachbar_col, nachbar_row)
                )  # sucht nach nachbarn und schaut ob WALL or FLOOR

        if len(nachbar) == 0:
            weg.pop()
            continue

        ziel_col, ziel_row = random.choice(
            nachbar
        )  # wird als Ziel ausgewählt (noch kein FLOOR)

        # die Wand zwischen Ziel und Jetzt zu Floor machen (Path)
        wand_col = (jetzt_col + ziel_col) // 2
        wand_row = (jetzt_row + ziel_row) // 2
        grid[wand_row][wand_col] = FLOOR  # hier wird Path gesetzt (FLOOR)

        grid[ziel_row][ziel_col] = FLOOR  # Ziel auch auf FLOOR setzen

        weg.append((ziel_col, ziel_row))  # neuer ausgang


def room_creation(grid, terminal_x, terminal_y):
    # anzahl der Räume bestimmen
    grid_flaeche = terminal_x * terminal_y
    anzahl_rooms = grid_flaeche // 300

    for _ in range(anzahl_rooms):
        row_room = random.randint(2, terminal_y - 3)
        col_room = random.randint(2, terminal_x - 3)
        radius_room = random.randint(
            1, 4
        )  # wie weit sich der Raum vom Mittelpunkt ausbreitet

        # hier werden die Spalten und Zeilen des Raumes berechnet (Eckpunkte)
        row_room_start = row_room - radius_room
        row_room_end = row_room + radius_room
        col_room_start = col_room - radius_room
        col_room_end = col_room + radius_room

        for row in range(row_room_start, row_room_end + 1):
            for col in range(col_room_start, col_room_end + 1):
                innerhalb_grid = (
                    1 <= col < terminal_x - 2 and 1 <= row < terminal_y - 2
                )  # true or false wert ob innerhalb des Grids befindet

                if not innerhalb_grid:
                    continue  # geht zur nächsten Iteration

                grid[row][col] = FLOOR


def wall_creation(grid, terminal_x):
    half = terminal_x // 2

    for row in range(len(grid)):
        for col in range(half - 1, half + 2):
            grid[row][col] = WALL


def arena_creation(grid, terminal_x, terminal_y):
    # max() stellt sicher, dass die Arena mind. 5 breit ist, ansonsten übernimmt es term_x * 15% (15% von der Term breit)
    arena_breite = max(int(terminal_x * 0.15), 5)
    arena_hoehe = max(int(terminal_y * 0.15), 5)

    row_half = terminal_y // 2
    col_half = terminal_x // 2

    # // 2 damit von der hälfte nach links gegangen wird
    # - 1 weil die Arenawand mitgezählt wird und sonst zu lang wäre um 1 (Arenabreite = 10 | 1 (Wand) + 10 = 11 - daher - 1)
    col_start = col_half - arena_breite // 2
    col_end = col_start + arena_breite - 1
    row_start = row_half - arena_hoehe // 2
    row_end = row_start + arena_hoehe - 1

    # Arena erstellen
    for row in range(row_start, row_end + 1):
        for col in range(col_start, col_end + 1):
            arena_wand = (
                row == row_start or row == row_end or col == col_start or col == col_end
            )

            if arena_wand:
                grid[row][col] = WALL
            else:
                grid[row][col] = FLOOR

    # Tür reinschneiden
    grid[row_half][col_start] = DOOR_P1  # linke  Wand
    grid[row_half][col_end] = DOOR_P2  # rechte Wand

    # Dead-End Prävention
    wall_cutter = col_start - 1
    for _ in range(1, 4):
        grid[row_half][wall_cutter] = FLOOR
        wall_cutter -= 1

    wall_cutter = col_end + 1
    for _ in range(1, 4):
        grid[row_half][wall_cutter] = FLOOR
        wall_cutter += 1

    global door_pos_p1, door_pos_p2  # global verwendet globale varibalen, ohne "global" würden neue lokale Varibalen erstellt werden
    door_pos_p1 = (row_half, col_start)
    door_pos_p2 = (row_half, col_end)


def remove_random_walls(grid, terminal_x, terminal_y):
    anzahl = (terminal_x * terminal_y) // 50  # ca. 2% der Zellen

    for _ in range(anzahl):
        row = random.randint(1, terminal_y - 2)
        col = random.randint(1, terminal_x - 2)

        if grid[row][col] == WALL:
            grid[row][col] = FLOOR


def remove_walls_near_wall(grid, terminal_x, terminal_y):
    half = terminal_x // 2

    for row in range(1, terminal_y - 1):
        grid[row][half - 2] = FLOOR
        grid[row][half + 2] = FLOOR


###############################################################################################
# Placing Items & Traps & Monsters


def is_pos_in_arena(row, col, terminal_x, terminal_y) -> bool:
    # max() stellt sicher, dass die Arena mind. 5 breit ist, ansonsten übernimmt es term_x * 15% (15% von der Term breit)
    arena_breite = max(int(terminal_x * 0.15), 5)
    arena_hoehe = max(int(terminal_y * 0.15), 5)

    row_half = terminal_y // 2
    col_half = terminal_x // 2

    # // 2 damit von der hälfte nach links gegangen wird
    # - 1 weil die Arenawand mitgezählt wird und sonst zu lang wäre um 1 (Arenabreite = 10 | 1 (Wand) + 10 = 11 - daher - 1)
    col_start = col_half - arena_breite // 2
    col_end = col_start + arena_breite - 1
    row_start = row_half - arena_hoehe // 2
    row_end = row_start + arena_hoehe - 1

    return col_start <= col <= col_end and row_start <= row <= row_end


def get_random_floor_in_half(grid, terminal_x, terminal_y, side, besetzt):
    # side = rechte / linke Hälfte grid
    half = terminal_x // 2
    if side == "l":
        col_min = 1
    else:
        col_min = half + 2
    if side == "l":
        col_max = half - 2
    else:
        col_max = terminal_x - 2

    for _ in range(200):  # 200 versuche FLOOR zu finden
        row = random.randint(1, terminal_y - 2)
        col = random.randint(col_min, col_max)
        if (
            grid[row][col] == FLOOR
            and (row, col) not in besetzt
            and not is_pos_in_arena(row, col, terminal_x, terminal_y)
        ):
            return (row, col)
    return None


def place_items(grid, terminal_x, terminal_y, besetzt):
    anzahl = random.randint(6, 8)

    for _ in range(anzahl):
        bonus = random.randint(1, 5)
        typ = random.choice(["w", "r"])  # Waffe oder Rüstung auswählen
        if typ == "w":
            zeichen = ")"
            farbe = MAGENTA
        else:
            zeichen = "["
            farbe = CYAN

        for side in ["l", "r"]:
            pos = get_random_floor_in_half(grid, terminal_x, terminal_y, side, besetzt)
            if pos:
                item = Item(zeichen, pos[1], pos[0], typ, False, farbe, bonus)
                items.append(item)
                besetzt.add(pos)


def place_traps(grid, terminal_x, terminal_y, besetzt):
    anzahl = random.randint(3, 6)

    trap_type = ["t", "g", "f"]

    for _ in range(anzahl):
        for side in ["l", "r"]:
            for type in trap_type:
                pos = get_random_floor_in_half(
                    grid, terminal_x, terminal_y, side, besetzt
                )
                if pos:
                    if type == "t":
                        trap = Trap("^", pos[1], pos[0], "health", False, MAGENTA)
                        traps.append(trap)
                    elif type == "g":
                        trap = Trap("&", pos[1], pos[0], "defense", False, MAGENTA)
                        giftwolke.append(trap)
                    else:
                        trap = Trap("_", pos[1], pos[0], "health", False, MAGENTA)
                        falltuer.append(trap)
                    besetzt.add(pos)


def place_monster(grid, terminal_x, terminal_y, besetzt):
    anzahl = random.randint(6, 10)

    for i in range(anzahl):
        for side in ["l", "r"]:
            if i < len(monster):
                used_monster = monster[i]
            else:
                used_monster = random.choice(monster)

            pos = get_random_floor_in_half(grid, terminal_x, terminal_y, side, besetzt)
            if pos:
                m = Entity(
                    used_monster.sign,
                    pos[1],
                    pos[0],
                    used_monster.level,
                    used_monster.health,
                    used_monster.attack,
                    used_monster.defense,
                    True,
                    True,
                    used_monster.sense,
                    used_monster.color,
                    side,
                )
                monster_placed.append(m)
                besetzt.add(pos)


###############################################################################################
# Pathfinding


def pathfinding(grid, start_x, start_y, ziel_x, ziel_y):
    queue = Queue()
    queue.enqueue((start_x, start_y))
    came_from = {(start_x, start_y): None}

    while not queue.is_empty():
        x, y = queue.dequeue()

        if x == ziel_x and y == ziel_y:
            # Pfad zurückverfolgen
            pos = (x, y)
            while came_from[pos] is not None and came_from[pos] != (start_x, start_y):
                pos = came_from[pos]
            return pos

        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            new_x, new_y = dx + x, dy + y
            if grid[new_y][new_x] != WALL and (new_x, new_y) not in came_from:
                came_from[(new_x, new_y)] = (x, y)
                queue.enqueue((new_x, new_y))

    return None


###############################################################################################
# Combat


def level_up(entity):
    entity.level += 1
    entity.health += 10
    entity.attack += 2
    entity.defense += 1


def combat(striker, defender):
    dmg = max(striker.attack - defender.defense, 1)
    defender.health -= dmg

    if defender.health <= 0:
        defender.alive = False
        if defender.is_monster and striker.alive:
            level_up(striker)


###############################################################################################
# Movement


def try_move(entity, dx, dy, grid):
    global player_monster_killed, player_items_collected

    ziel_x = entity.pos_x + dx
    ziel_y = entity.pos_y + dy

    zelle = grid[ziel_y][ziel_x]
    if zelle == WALL:
        return

    if p2.alive and p2.pos_x == ziel_x and p2.pos_y == ziel_y:
        combat(entity, p2)
        return

    for m in monster_placed:
        if m.alive and m.pos_x == ziel_x and m.pos_y == ziel_y:
            combat(entity, m)
            if entity is player and not m.alive:
                player_monster_killed += 1
            return

    for item in items:
        if not item.taken and item.pos_x == ziel_x and item.pos_y == ziel_y:
            item.taken = True
            if entity is player:
                player_items_collected += 1
            if item.type == "w":
                entity.attack += item.bonus
            else:
                entity.defense += item.bonus

    for trap in traps + giftwolke + falltuer:
        if not trap.triggered and trap.pos_x == ziel_x and trap.pos_y == ziel_y:
            trap.triggered = True
            if trap.stat == "health":
                entity.health -= 3
            else:
                entity.defense -= 2

    entity.pos_x = ziel_x
    entity.pos_y = ziel_y

    if (
        grid[door_pos_p1[0]][door_pos_p1[1]] == DOOR_P1
        and entity.pos_y == door_pos_p1[0]
        and entity.pos_x == door_pos_p1[1] + 1
    ):
        entity.level += 1
        entity.health += 10
        entity.attack += 1
        entity.defense += 1
        grid[door_pos_p1[0]][door_pos_p1[1]] = WALL
        grid[door_pos_p2[0]][door_pos_p2[1]] = FLOOR


def move_monsters(grid):
    richtungen = [(0, 1), (0, -1), (1, 0), (-1, 0)]

    for m in monster_placed:
        if not m.alive:
            continue

        if m.side == "r":
            distanz_player = abs(m.pos_x - player.pos_x) + abs(m.pos_y - player.pos_y)
            distanz_p2 = abs(m.pos_x - p2.pos_x) + abs(m.pos_y - p2.pos_y)

            ziel = None
            if distanz_player <= m.sense and distanz_p2 <= m.sense:
                if distanz_player <= distanz_p2:
                    ziel = player
                else:
                    ziel = p2
            elif distanz_player <= m.sense:
                ziel = player
            elif distanz_p2 <= m.sense:
                ziel = p2
        else:
            distanz_player = abs(m.pos_x - player.pos_x) + abs(m.pos_y - player.pos_y)
            ziel = None
            if distanz_player <= m.sense:
                ziel = player

        if ziel is None:
            dx, dy = random.choice(richtungen)
            new_x, new_y = m.pos_x + dx, m.pos_y + dy
        else:
            schritt = pathfinding(grid, m.pos_x, m.pos_y, ziel.pos_x, ziel.pos_y)
            if schritt is None:
                continue
            new_x, new_y = schritt

        if grid[new_y][new_x] != WALL:
            if ziel is not None and new_x == ziel.pos_x and new_y == ziel.pos_y:
                combat(m, ziel)
            else:
                m.pos_x = new_x
                m.pos_y = new_y


def move_p2(grid):
    global p2_phase, p2_ziel_item, p2_ziel_monster

    if p2_phase == 1:
        offene_items = []
        for item in items:
            if not item.taken and item.pos_x > TERMINAL_X // 2:
                offene_items.append(item)

        if len(offene_items) == 0:
            p2_phase = 2
            return

        # nähestes Item von P2 gesucht
        if p2_ziel_item is None or p2_ziel_item.taken:
            p2_ziel_item = offene_items[0]
            kuerzeste_distanz = abs(p2_ziel_item.pos_x - p2.pos_x) + abs(
                p2_ziel_item.pos_y - p2.pos_y
            )

            for item in offene_items:
                i_distanz = abs(item.pos_x - p2.pos_x) + abs(item.pos_y - p2.pos_y)
                if i_distanz < kuerzeste_distanz:
                    p2_ziel_item = item
                    kuerzeste_distanz = i_distanz

        schritt = pathfinding(
            grid, p2.pos_x, p2.pos_y, p2_ziel_item.pos_x, p2_ziel_item.pos_y
        )
        if schritt is None:
            return

        new_x, new_y = schritt

        for m in monster_placed:
            if m.alive and m.pos_x == new_x and m.pos_y == new_y:
                combat(p2, m)
                return

        if grid[new_y][new_x] == WALL:
            return

        p2.pos_x = new_x
        p2.pos_y = new_y

        for trap in traps + giftwolke + falltuer:
            if not trap.triggered and trap.pos_x == p2.pos_x and trap.pos_y == p2.pos_y:
                trap.triggered = True
                if trap.stat == "health":
                    p2.health -= 3
                else:
                    p2.defense -= 2

        for item in items:
            if not item.taken and item.pos_x == p2.pos_x and item.pos_y == p2.pos_y:
                item.taken = True
                if item.type == "w":
                    p2.attack += item.bonus
                else:
                    p2.defense += item.bonus

    elif p2_phase == 2:
        lebende_monster = []
        for m in monster_placed:
            if m.alive and m.side == "r":
                lebende_monster.append(m)

        if len(lebende_monster) == 0:
            p2_phase = 3
            return

        if p2_ziel_monster is None or not p2_ziel_monster.alive:
            p2_ziel_monster = lebende_monster[0]
            k_monster_distanz = abs(p2_ziel_monster.pos_x - p2.pos_x) + abs(
                p2_ziel_monster.pos_y - p2.pos_y
            )
            for m in lebende_monster:
                m_distanz = abs(m.pos_x - p2.pos_x) + abs(m.pos_y - p2.pos_y)
                if m_distanz < k_monster_distanz:
                    p2_ziel_monster = m
                    k_monster_distanz = m_distanz

        schritt = pathfinding(
            grid, p2.pos_x, p2.pos_y, p2_ziel_monster.pos_x, p2_ziel_monster.pos_y
        )

        if schritt is None:
            return

        new_x, new_y = schritt

        for m in monster_placed:
            if m.alive and m.pos_x == new_x and m.pos_y == new_y:
                combat(p2, m)
                return

        if grid[new_y][new_x] == WALL:
            return

        p2.pos_x = new_x
        p2.pos_y = new_y

        for trap in traps + giftwolke + falltuer:
            if not trap.triggered and trap.pos_x == p2.pos_x and trap.pos_y == p2.pos_y:
                trap.triggered = True
                if trap.stat == "health":
                    p2.health -= 3
                else:
                    p2.defense -= 2

    elif p2_phase == 3:
        tuer_zu = grid[door_pos_p2[0]][door_pos_p2[1]] == DOOR_P2

        if tuer_zu:
            ziel_x = door_pos_p2[1] - 1
            ziel_y = door_pos_p2[0]
        else:
            ziel_x = player.pos_x
            ziel_y = player.pos_y

        schritt = pathfinding(grid, p2.pos_x, p2.pos_y, ziel_x, ziel_y)
        if schritt is None:
            return

        new_x, new_y = schritt

        if new_x == player.pos_x and new_y == player.pos_y:
            combat(p2, player)
            return

        if grid[new_y][new_x] == WALL:
            return

        p2.pos_x = new_x
        p2.pos_y = new_y

        for trap in traps + giftwolke + falltuer:
            if not trap.triggered and trap.pos_x == p2.pos_x and trap.pos_y == p2.pos_y:
                trap.triggered = True
                if trap.stat == "health":
                    p2.health -= 3
                else:
                    p2.defense -= 2

        if (
            grid[door_pos_p2[0]][door_pos_p2[1]] == DOOR_P2
            and p2.pos_x == door_pos_p2[1] - 1
            and p2.pos_y == door_pos_p2[0]
        ):
            level_up(p2)
            grid[door_pos_p2[0]][door_pos_p2[1]] = WALL
            grid[door_pos_p1[0]][door_pos_p1[1]] = FLOOR


###############################################################################################
# Win/Loss Screen


def zentriert(text):
    freiraum = max(TERMINAL_X - len(text), 0)
    return " " * (freiraum // 2) + text


def end_stats():
    print("\033[H\033[2J", end="", flush=True)

    if player.health <= 0:
        health = f"HP übrig:         {RED}{max(player.health, 0)}{Color.OFF}"
    else:
        health = f"HP übrig:         {GREEN}{max(player.health, 0)}{Color.OFF}"

    if player_monster_killed <= 0:
        monster_stat = f"Monster besiegt:  {RED}{player_monster_killed}{Color.OFF}"
    else:
        monster_stat = f"Monster besiegt:  {GREEN}{player_monster_killed}{Color.OFF}"

    if player_items_collected <= 0:
        item_stat = f"Items gesammelt:  {RED}{player_items_collected}{Color.OFF}"
    else:
        item_stat = f"Items gesammelt:  {GREEN}{player_items_collected}{Color.OFF}"

    zeilen = [
        health,
        monster_stat,
        item_stat,
        "",
        "Drücke eine beliebige Taste zum Beenden...",
    ]

    oben_versatz = max((TERMINAL_Y - len(zeilen)) // 2, 0)
    print("\n" * oben_versatz, end="")

    for zeile in zeilen:
        print(zentriert(zeile))

    readchar.readkey()


def game_over_screen():
    # \033[2J löscht screen
    print("\033[H\033[2J", end="", flush=True)
    row = TERMINAL_Y // 2
    text = "YOU DIED - GAME OVER"
    col = (TERMINAL_X // 2) - (len(text) // 2)
    print("\n" * row + " " * col + f"{RED}{text}{Color.OFF}")
    time.sleep(2)
    end_stats()
    readchar.readkey()


def win_screen():
    # \033[2J löscht screen
    print("\033[H\033[2J", end="", flush=True)
    row = TERMINAL_Y // 2
    text = "YOU BEATED THE ENEMY"
    col = (TERMINAL_X // 2) - (len(text) // 2)
    print("\n" * row + " " * col + f"{GREEN}{text}{Color.OFF}")
    time.sleep(2)
    end_stats()
    readchar.readkey()


def loading_screen(nachricht, fortschritt):
    print("\033[H\033[2J", end="", flush=True)

    banner = [
        "██████╗ ██╗   ██╗███╗   ██╗ ██████╗ ███████╗ ██████╗ ███╗   ██╗",
        "██╔══██╗██║   ██║████╗  ██║██╔════╝ ██╔════╝██╔═══██╗████╗  ██║",
        "██║  ██║██║   ██║██╔██╗ ██║██║  ███╗█████╗  ██║   ██║██╔██╗ ██║",
        "██║  ██║██║   ██║██║╚██╗██║██║   ██║██╔══╝  ██║   ██║██║╚██╗██║",
        "██████╔╝╚██████╔╝██║ ╚████║╚██████╔╝███████╗╚██████╔╝██║ ╚████║",
        "╚═════╝  ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝ ╚══════╝ ╚═════╝ ╚═╝  ╚═══╝",
        "                          A R E N A",
    ]

    banner_breite = 0
    for zeile in banner:
        if len(zeile) > banner_breite:
            banner_breite = len(zeile)

    links_versatz = (TERMINAL_X - banner_breite) // 2
    inhalt_hoehe = (
        len(banner) + 4
    )  # Banner + Leerzeile + Balken + Leerzeile + Nachricht
    oben_veratz = max((TERMINAL_Y - inhalt_hoehe) // 2, 0)
    print("\n" * oben_veratz, end="")

    for zeile in banner:
        print(" " * links_versatz + zeile)

    gefuellt = int(banner_breite * fortschritt / 100)
    balken = "█" * gefuellt + "░" * (banner_breite - gefuellt)

    print()
    print(" " * links_versatz + balken)
    print()
    print(zentriert(nachricht))

    time.sleep(1)


def generierung_stats():
    print("\033[H\033[2J", end="", flush=True)

    zeilen = [
        "Dungeon generiert!",
        "",
        f"Items:   {len(items)}",
        f"Monster: {len(monster_placed)}",
        f"Traps:   {len(traps) + len(giftwolke) + len(falltuer)}",
        "",
        "Drücke eine beliebige Taste zum Starten...",
    ]

    oben_versatz = max((TERMINAL_Y - len(zeilen)) // 2, 0)
    print("\n" * oben_versatz, end="")

    for zeile in zeilen:
        print(zentriert(zeile))

    readchar.readkey()


###############################################################################################
# main programm


def generate_maze(terminal_x, terminal_y):
    loading_screen("Maze wird generiert", 25)
    grid = fill_maze_with_walls(terminal_x, terminal_y)
    maze_creation(grid, terminal_x, terminal_y)
    room_creation(grid, terminal_x, terminal_y)
    remove_random_walls(grid, terminal_x, terminal_y)
    remove_random_walls(grid, terminal_x, terminal_y)
    wall_creation(grid, terminal_x)
    remove_walls_near_wall(grid, terminal_x, terminal_y)

    loading_screen("Arena wird generiert", 50)
    arena_creation(grid, terminal_x, terminal_y)

    besetzt = set()  # set() entfernt duplicate

    loading_screen("Items, Monster und Traps werden platziert", 75)
    place_items(grid, terminal_x, terminal_y, besetzt)
    place_traps(grid, terminal_x, terminal_y, besetzt)
    place_monster(grid, terminal_x, terminal_y, besetzt)

    loading_screen("Spieler werden platziert", 100)
    pos_player = get_random_floor_in_half(grid, terminal_x, terminal_y, "l", besetzt)
    player.pos_x = pos_player[1]
    player.pos_y = pos_player[0]

    global p2
    pos_p2 = get_random_floor_in_half(grid, terminal_x, terminal_y, "r", besetzt)
    p2 = Player("*", pos_p2[1], pos_p2[0], 1, 10, 3, 1, True, False, None, GREEN, "r")

    generierung_stats()
    return grid


def print_maze(grid):
    # \033[H setzt Cursor nach Oben Links (1,1)
    # \033[2J löscht Bildschirminhalt, ansonsten würde Maze immer unten dran gesetzt werden und nicht ERSETZT
    # end="" verhindert Zeilenumbruch
    # flush=True schickt Output sofort an Terminal ohne auf Buffer zu warten
    # diese Zeile wird eben gebraucht damit sich das Maze nach jedem Move immer wieder resettet
    print("\033[H", end="", flush=True)

    # item und trap positionen werden in structs (dictionaries) gespeichert um O(1) suche zu ermöglichen
    # und nicht über jede Liste zu laufen und immer bei jedem "Kästchen" durchlaufen zu müssen nur um zu
    # checken ob an der Stelle ein Item oder eine Trap liegt
    item_positionen = {}
    for item in items:
        if not item.taken:
            item_positionen[(item.pos_x, item.pos_y)] = item

    trap_positionen = {}
    for trap in traps + giftwolke + falltuer:
        if trap.triggered:
            trap_positionen[(trap.pos_x, trap.pos_y)] = trap

    monster_positionen = {}
    for m in monster_placed:
        if m.alive:
            monster_positionen[(m.pos_x, m.pos_y)] = m

    # enumerate() gibt den index und den inhalt zurück
    for row_idx, row in enumerate(grid):
        text = ""

        for col_idx, z in enumerate(row):
            position = (col_idx, row_idx)

            if position == (player.pos_x, player.pos_y):
                zeichen = f"{BG_WHITE}{player.color}{player.sign}{Color.OFF}"
            elif position == (p2.pos_x, p2.pos_y):
                zeichen = f"{BG_WHITE}{p2.color}{p2.sign}{Color.OFF}"
            elif position in monster_positionen:
                monster_obj = monster_positionen[position]
                zeichen = f"{BG_WHITE}{monster_obj.color}{monster_obj.sign}{Color.OFF}"
            elif position in item_positionen:
                item = item_positionen[position]
                zeichen = f"{BG_WHITE}{item.color}{item.sign}{Color.OFF}"
            elif position in trap_positionen:
                trap = trap_positionen[position]
                zeichen = f"{BG_WHITE}{trap.color}{trap.sign}{Color.OFF}"
            elif z == WALL:
                zeichen = f"{BLACK}█{Color.OFF}"
            elif z == DOOR_P1:
                zeichen = f"{BG_WHITE}{BLUE}|{Color.OFF}"
            elif z == DOOR_P2:
                zeichen = f"{BG_WHITE}{GREEN}|{Color.OFF}"
            else:
                zeichen = f"{BG_WHITE} {Color.OFF}"

            text = text + zeichen

        print(text)

    p1_statusbar = f"Level: {player.level} HP: {player.health} ATK: {player.attack} DEF: {player.defense}"
    p2_statusbar = (
        f"Level: {p2.level} HP: {p2.health} ATK: {p2.attack} DEF: {p2.defense}"
    )
    luecke = " " * (TERMINAL_X - len(p1_statusbar) - len(p2_statusbar) - 3)

    p1_statusbar = f"{BG_BLUE}{p1_statusbar}{Color.OFF}"
    p2_statusbar = f"{BG_GREEN}{p2_statusbar}{Color.OFF}"

    print(f"{p1_statusbar}{luecke}{p2_statusbar}\033[K")


# print(terminal_x, terminal_y)

# taste = readchar.readkey()
# print("Du hast: " + taste + " gedrückt")
# print(tmaze[0][1])

# problem with double wall if terminal height is uneven
maze_height = TERMINAL_Y - 1
if maze_height % 2 == 0:
    maze_height -= 1

maze = generate_maze(TERMINAL_X, maze_height)

###############################################################################################
# Game Logic

while True:
    print_maze(maze)
    taste = readchar.readkey()

    if taste == "q":
        break
    elif taste == "w" or taste == readchar.key.UP:
        try_move(player, 0, -1, maze)
    elif taste == "s" or taste == readchar.key.DOWN:
        try_move(player, 0, 1, maze)
    elif taste == "a" or taste == readchar.key.LEFT:
        try_move(player, -1, 0, maze)
    elif taste == "d" or taste == readchar.key.RIGHT:
        try_move(player, 1, 0, maze)

    if not player.alive:
        game_over_screen()
        break

    move_monsters(maze)
    move_p2(maze)

    if not p2.alive:
        win_screen()
        break

    if not player.alive:
        game_over_screen()
        break
