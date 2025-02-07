import numpy as np
from scipy.integrate import ode


def equations(t, state, G, M):
    r, theta, drdt, dthetadt = state
    d2rdt2 = r * dthetadt ** 2 - G * M / r ** 2
    d2thetadt2 = -2 * drdt * dthetadt / r
    return [drdt, dthetadt, d2rdt2, d2thetadt2]


G = 6.67430e-11
M = 1.989e30
r0 = 1.496e11
drdt0 = 0
theta0 = 0
t0 = 0
dt = 80000
dthetadt0 = 2 * np.pi / (365.25 * 24 * 3600)
state0 = [r0, theta0, drdt0, dthetadt0]

solver = ode(equations)
solver.set_integrator('dopri5')
solver.set_initial_value(state0, t0)
solver.set_f_params(G, M)

import pygame as pg
import sys
import time


class InputBox:
    def __init__(self, x, y, w, h, text=0, chg=None):
        self.rect = pg.Rect(x, y, w, h)
        self.w = w
        self.color = pg.Color('black')
        self.num = float(text)
        self.text = str(self.num)
        self.last_text = self.text
        self.txt_surface = pg.font.Font(None, 32).render(self.text, True, [150, 150, 150])
        self.active = False
        self.cursor_position = len(self.text)
        self.cursor_visible = True
        self.cursor_time = time.time()
        self.blink_interval = 0.5
        self.font = pg.font.Font(None, 32)
        self.delete_timer = None
        self.delete_interval = 0.1
        self.delete_before = 0.3
        self.can_delete = False
        self.adjust_width()
        self.chg = chg
        self.timer_type = None

    def handle_event(self, event):
        global kepler
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.active = True
                self.cursor_position = len(self.text)
                self.adjust_width()
            else:
                self.active = False
                self.delete_timer = None
                self.can_delete = False
                self.text = self.last_text
            self.color = pg.Color([150, 150, 150]) if self.active else pg.Color('black')

        if event.type == pg.KEYDOWN:
            if self.active:
                if event.key == pg.K_LEFT:
                    if self.delete_timer is None:
                        self.timer_type = 1
                        self.delete_timer = time.time()
                        self.move(0)
                elif event.key == pg.K_RIGHT:
                    if self.delete_timer is None:
                        self.timer_type = 2
                        self.delete_timer = time.time()
                        self.move(1)
                elif event.key == pg.K_RETURN:
                    self.active = False
                    self.delete_timer = None
                    self.can_delete = False
                    try:
                        self.num = float(self.text)
                        self.text = str(self.num)
                        self.last_text = self.text
                        self.chg(self.num)
                        self.adjust_width()
                    except ValueError:
                        if self.text.lower() == "kepler":
                            kepler = True
                        if self.text.lower() == "bye,kepler":
                            kepler = False
                        self.text = str(self.num)
                        self.adjust_width()
                    self.color = pg.Color('black')
                elif event.key == pg.K_BACKSPACE:
                    if self.delete_timer is None:
                        self.timer_type = 3
                        self.delete_timer = time.time()
                        self.delete_character()
                else:
                    char = event.unicode
                    if char.isalnum() or char in ['.', '+', '-',',']:
                        if self.cursor_position < 28:
                            self.text = self.text[:self.cursor_position] + event.unicode + self.text[
                                                                                           self.cursor_position:]
                            self.cursor_position += 1
                            self.adjust_width()
        if event.type == pg.KEYUP and self.active:
            if event.key == pg.K_BACKSPACE and self.timer_type == 3:
                self.delete_timer = None
                self.can_delete = False
            if event.key == pg.K_RIGHT and self.timer_type == 2:
                self.delete_timer = None
                self.can_delete = False
            if event.key == pg.K_LEFT and self.timer_type == 1:
                self.delete_timer = None
                self.can_delete = False

    def enter(self):
        self.active = False
        self.delete_timer = None
        self.can_delete = False
        self.text = self.last_text

    def set_text(self, text):
        self.num = float(text)
        self.text = str(self.num)
        self.last_text = self.text

    def adjust_width(self):
        width = max(self.w, self.font.size(self.text)[0] + 10)
        self.rect.w = width

    def move(self, t):
        if t == 0:
            self.cursor_position = max(0, self.cursor_position - 1)
        else:
            self.cursor_position = min(len(self.text), self.cursor_position + 1)

    def delete_character(self):
        if self.cursor_position > 0:
            self.text = self.text[:self.cursor_position - 1] + self.text[self.cursor_position:]
            self.cursor_position -= 1
            self.adjust_width()
            self.txt_surface = self.font.render(self.text, True, self.color)

    def update(self):
        if self.active:
            current_time = time.time()
            if current_time - self.cursor_time > self.blink_interval:
                self.cursor_time = current_time
                self.cursor_visible = not self.cursor_visible
            if self.delete_timer is not None and current_time - self.delete_timer > self.delete_interval and self.can_delete:
                self.delete_timer = current_time
                if self.timer_type == 1:
                    self.move(0)
                elif self.timer_type == 2:
                    self.move(1)
                else:
                    self.delete_character()
            if self.delete_timer is not None and current_time - self.delete_timer > self.delete_before and not self.can_delete:
                self.delete_timer = current_time
                self.can_delete = True

    def draw(self, screen):
        self.txt_surface = pg.font.Font(None, 32).render(self.text, True, [150, 150, 150])
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))
        if self.active:
            pg.draw.rect(screen, self.color, self.rect, 2)

        if self.active and self.cursor_visible:
            text_width = self.font.size(self.text[:self.cursor_position])[0]
            cursor_x = self.rect.x + 5 + text_width
            cursor_rect = pg.Rect(cursor_x, self.rect.y, 2, self.rect.height)
            pg.draw.rect(screen, self.color, cursor_rect)


class AngleDisplay:
    def __init__(self, screen, center, radius):
        self.screen = screen
        self.center = center
        self.radius = radius
        self.angle_radians = 0
        self.dragging = False

    def draw(self):
        if not self.dragging:
            self.angle_radians = np.arctan2(solver.y[0] * solver.y[3], solver.y[2]) + solver.y[1]
        x = int(self.center[0] + (self.radius - 1) * np.cos(self.angle_radians))
        y = int(self.center[1] - (self.radius - 1) * np.sin(self.angle_radians))
        pg.draw.line(self.screen, (244, 50, 50), self.center, (x, y), 3)
        pg.draw.circle(self.screen, (150, 150, 150), self.center, self.radius, 3)

    def update_angle(self, event):
        global area
        if event.type == pg.MOUSEBUTTONDOWN:
            dx = event.pos[0] - self.center[0]
            dy = event.pos[1] - self.center[1]
            if (dx) ** 2 + (dy) ** 2 < self.radius ** 2:
                if (np.abs(np.arctan2(-dy, dx) - self.angle_radians) < 0.08):
                    self.dragging = True
        elif event.type == pg.MOUSEMOTION and self.dragging:
            area = []
            dx = event.pos[0] - self.center[0]
            dy = event.pos[1] - self.center[1]
            self.angle_radians = np.arctan2(-dy, dx)
            theta0 = self.angle_radians - solver.y[1]
            v0 = np.sqrt((solver.y[0] * solver.y[3]) ** 2 + solver.y[2] ** 2)
            state0 = solver.y
            t0 = 0
            state0[2] = v0 * np.cos(theta0)
            state0[3] = v0 * np.sin(theta0) / state0[0]
            solver.set_initial_value(state0, t0)


        elif event.type == pg.MOUSEBUTTONUP and self.dragging:
            self.dragging = False


def change_v(v):
    global solver,area
    area = []
    t0 = 0
    state0 = solver.y
    cs = v / np.sqrt((solver.y[0] * solver.y[3]) ** 2 + solver.y[2] ** 2)
    state0[2] *= cs
    state0[3] *= cs
    solver.set_initial_value(state0, t0)


pg.init()
screen = pg.display.set_mode((600, 600))
pg.display.set_caption('Orbit')

icon_surface = pg.Surface([64, 64])
k = 0.5
icon_surface.fill([0, 0, 0])
pg.draw.circle(icon_surface, [28, 0, 0], [32, 32], 29 * k)
pg.draw.circle(icon_surface, [36, 3, 3], [32, 32], 28 * k)
pg.draw.circle(icon_surface, [45, 7, 6], [32, 32], 27 * k)
pg.draw.circle(icon_surface, [53, 11, 10], [32, 32], 26 * k)
pg.draw.circle(icon_surface, [62, 15, 13], [32, 32], 25 * k)
pg.draw.circle(icon_surface, [66, 17, 15], [32, 32], 24 * k)
pg.draw.circle(icon_surface, [75, 21, 19], [32, 32], 23 * k)
pg.draw.circle(icon_surface, [79, 25, 23], [32, 32], 22 * k)
pg.draw.circle(icon_surface, [84, 29, 27], [32, 32], 21 * k)
pg.draw.circle(icon_surface, [88, 33, 31], [32, 32], 20 * k)
pg.draw.circle(icon_surface, [95, 39, 37], [32, 32], 19 * k)
pg.draw.circle(icon_surface, [100, 44, 42], [32, 32], 18 * k)
pg.draw.circle(icon_surface, [107, 47, 45], [32, 32], 17 * k)
pg.draw.circle(icon_surface, [112, 49, 48], [32, 32], 16 * k)
pg.draw.circle(icon_surface, [119, 53, 52], [32, 32], 15 * k)
pg.draw.circle(icon_surface, [127, 57, 56], [32, 32], 14 * k)
pg.draw.circle(icon_surface, [205, 106, 82], [32, 32], 11 * k)
pg.draw.circle(icon_surface, [251, 168, 130], [32, 32], 9 * k)
pg.draw.circle(icon_surface, [252, 220, 167], [32, 32], 8 * k)
pg.draw.circle(icon_surface, [254, 255, 250], [32, 32], 6 * k)
t = list([i / 20 - 6.2 + 2 * np.pi + 3.8 for i in range(0, 125, 1)])
for i, theta in enumerate(t):
    color = (int(255 * (i / len(t))), int(255 * (i / len(t))), int(255 * (i / len(t))))
    pg.draw.circle(icon_surface, color, [32 + 27 * np.cos(theta), 32 - 27 * np.sin(theta)], 2 * k)
theta = 3.8
pg.draw.circle(icon_surface, [0, 64, 115], [32 + 27 * np.cos(theta), 32 - 27 * np.sin(theta)], 6 * k)
pg.draw.circle(icon_surface, [32, 134, 185], [32 + 27 * np.cos(theta), 32 - 27 * np.sin(theta)], 5 * k)
pg.draw.circle(icon_surface, [102, 204, 255], [32 + 27 * np.cos(theta), 32 - 27 * np.sin(theta)], 4 * k)

pg.display.set_icon(icon_surface)

screen.fill([0, 0, 0])

paused = False
v_show = False

clock = pg.time.Clock()

zoom = 8.586e-10
k = 1
trajectory = []
area = []
a_length = 600
t_length = 1000
x = solver.y[0] * np.cos(solver.y[1])
y = solver.y[0] * np.sin(solver.y[1])
dragging = None
kepler = False

input_boxes = [InputBox(45, 20, 140, 32, np.sqrt((dthetadt0 * r0) ** 2 + drdt0 ** 2), change_v)]
angle_display = AngleDisplay(screen, (60, 90), 32)

while True:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()
        elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1 and paused:
            px, py = event.pos
            px = (px - 300) / zoom
            py = (300 - py) / zoom
            if np.sqrt((px - x) ** 2 + (py - y) ** 2) < 6 / 8.586e-10:
                dragging = (px - x, py - y)
        elif event.type == pg.MOUSEMOTION and paused:
            if dragging is not None:
                area = []
                trajectory = []
                rx, ry = event.pos
                rx = (rx - 300) / zoom
                ry = (300 - ry) / zoom
                x = rx - dragging[0]
                y = ry - dragging[1]
        elif event.type == pg.MOUSEBUTTONUP:
            dragging = None
            t00 = 0
            state00 = solver.y.copy()
            state00[0] = np.sqrt(x ** 2 + y ** 2)
            state00[1] = np.arctan2(y, x)
            theta00 = np.arctan2(solver.y[0] * solver.y[3], solver.y[2])
            v00 = np.sqrt((solver.y[0] * solver.y[3]) ** 2 + solver.y[2] ** 2)
            theta00 = theta00 + solver.y[1] - state00[1]
            state00[2] = v00 * np.cos(theta00)
            state00[3] = v00 * np.sin(theta00) / state00[0]
            solver.set_initial_value(state00, t00)
        elif event.type == pg.MOUSEWHEEL:
            if (k * (1.1 if event.y > 0 else 1 / 1.1)) > 0.5 and (k * (1.1 if event.y > 0 else 1 / 1.1)) < 10:
                zoom *= 1.1 if event.y > 0 else 1 / 1.1
                k *= 1.1 if event.y > 0 else 1 / 1.1
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_v:
                if not paused:
                    if v_show:
                        input_boxes[0].enter()
                    v_show = not v_show
            if event.key == pg.K_SPACE:
                if paused:
                    input_boxes[0].enter()
                    v_show = False
                if dragging is not None:
                    dragging = None
                    t00 = 0
                    state00 = solver.y.copy()
                    state00[0] = np.sqrt(x ** 2 + y ** 2)
                    state00[1] = np.arctan2(y, x)
                    theta00 = np.arctan2(solver.y[0] * solver.y[3], solver.y[2])
                    v00 = np.sqrt((solver.y[0] * solver.y[3]) ** 2 + solver.y[2] ** 2)
                    theta00 = theta00 + solver.y[1] - state00[1]
                    state00[2] = v00 * np.cos(theta00)
                    state00[3] = v00 * np.sin(theta00) / state00[0]
                    solver.set_initial_value(state00, t00)
                paused = not paused
                if paused and not v_show:
                    input_boxes[0].set_text(np.sqrt((solver.y[0] * solver.y[3]) ** 2 + solver.y[2] ** 2))
            elif event.mod & pg.KMOD_CTRL and event.key == pg.K_r:
                input_boxes[0].enter()
                solver.set_initial_value(state0, t0)
                input_boxes[0].set_text(np.sqrt((solver.y[0] * solver.y[3]) ** 2 + solver.y[2] ** 2))
                x = solver.y[0] * np.cos(solver.y[1])
                y = solver.y[0] * np.sin(solver.y[1])
                trajectory = []
        if paused or v_show:
            angle_display.update_angle(event)
            for box in input_boxes:
                box.handle_event(event)

    screen.fill([0, 0, 0])
    pg.draw.circle(screen, [28, 0, 0], [300, 300], k * 29)
    pg.draw.circle(screen, [36, 3, 3], [300, 300], k * 28)
    pg.draw.circle(screen, [45, 7, 6], [300, 300], k * 27)
    pg.draw.circle(screen, [53, 11, 10], [300, 300], k * 26)
    pg.draw.circle(screen, [62, 15, 13], [300, 300], k * 25)
    pg.draw.circle(screen, [66, 17, 15], [300, 300], k * 24)
    pg.draw.circle(screen, [75, 21, 19], [300, 300], k * 23)
    pg.draw.circle(screen, [79, 25, 23], [300, 300], k * 22)
    pg.draw.circle(screen, [84, 29, 27], [300, 300], k * 21)
    pg.draw.circle(screen, [88, 33, 31], [300, 300], k * 20)
    pg.draw.circle(screen, [95, 39, 37], [300, 300], k * 19)
    pg.draw.circle(screen, [100, 44, 42], [300, 300], k * 18)
    pg.draw.circle(screen, [107, 47, 45], [300, 300], k * 17)
    pg.draw.circle(screen, [112, 49, 48], [300, 300], k * 16)
    pg.draw.circle(screen, [119, 53, 52], [300, 300], k * 15)
    pg.draw.circle(screen, [127, 57, 56], [300, 300], k * 14)
    if kepler:
        for i, (x_1, y_1) in enumerate(area):
            color = (
                int(255 * (np.ceil(i / 30) / np.ceil(len(area) / 30))),
                int(255 * (np.ceil(i / 30) / np.ceil(len(area) / 30))),
                int(255 * (np.ceil(i / 30) / np.ceil(len(area) / 30))))
            pg.draw.line(screen, color, [300, 300], [300 + x_1 * zoom, 300 - y_1 * zoom], int(k * 4))
            pg.draw.circle(screen, color, [300 + x_1 * zoom, 300 - y_1 * zoom], k * 2)
    pg.draw.circle(screen, [205, 106, 82], [300, 300], k * 11)
    pg.draw.circle(screen, [251, 168, 130], [300, 300], k * 9)
    pg.draw.circle(screen, [252, 220, 167], [300, 300], k * 8)
    pg.draw.circle(screen, [254, 255, 250], [300, 300], k * 6)
    if not paused:
        solver.integrate(solver.t + dt)
        if v_show and not input_boxes[0].active:
            input_boxes[0].set_text(np.sqrt((solver.y[0] * solver.y[3]) ** 2 + solver.y[2] ** 2))
        x = solver.y[0] * np.cos(solver.y[1])
        y = solver.y[0] * np.sin(solver.y[1])
        for i, (x_1, y_1) in enumerate(trajectory):
            color = (
                int(255 * (i / len(trajectory))), int(255 * (i / len(trajectory))), int(255 * (i / len(trajectory))))
            if not kepler:
                pg.draw.circle(screen, color, [300 + x_1 * zoom, 300 - y_1 * zoom], k * 2)
        trajectory.append((x, y))
        area.append((x, y))
        pg.draw.circle(screen, [0, 64, 115], [300 + x * zoom, 300 - y * zoom], k * 6)
        pg.draw.circle(screen, [32, 134, 185], [300 + x * zoom, 300 - y * zoom], k * 5)
        pg.draw.circle(screen, [102, 204, 255], [300 + x * zoom, 300 - y * zoom], k * 4)
        if len(trajectory) > t_length:
            trajectory.pop(0)
        if len(area) > a_length:
            for i in range(30):
                area.pop(0)
    else:
        for i, (x_1, y_1) in enumerate(trajectory):
            color = (
                int(255 * (i / len(trajectory))), int(255 * (i / len(trajectory))), int(255 * (i / len(trajectory))))
            if not kepler:
                pg.draw.circle(screen, color, [300 + x_1 * zoom, 300 - y_1 * zoom], k * 2)

        pg.draw.circle(screen, [0, 64, 115], [300 + x * zoom, 300 - y * zoom], k * 6)
        pg.draw.circle(screen, [32, 134, 185], [300 + x * zoom, 300 - y * zoom], k * 5)
        pg.draw.circle(screen, [102, 204, 255], [300 + x * zoom, 300 - y * zoom], k * 4)
    if paused or v_show:
        screen.blit(pg.font.Font(None, 32).render("v:", True, [150, 150, 150]), (25, 25))
        for box in input_boxes:
            box.update()
            angle_display.draw()

        for box in input_boxes:
            box.draw(screen)

    pg.display.flip()
    clock.tick(30)
