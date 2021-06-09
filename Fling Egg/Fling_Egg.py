from Player import *
from Color import *
import time
import os
import sys
import pygame
from ctypes import windll


SCREEN_SIZE=[windll.user32.GetSystemMetrics(0), windll.user32.GetSystemMetrics(1)]#用tkinter获当前屏幕大小
SCREEN_RATE = 5/6
PATH = (os.path.dirname(sys.executable) if hasattr(sys, 'frozen') else os.path.dirname(__file__)) + "\\"
pygame.init()
pygame.display.set_caption('Fling Egg')
fbs = (int(SCREEN_SIZE[0]*SCREEN_RATE), int(SCREEN_SIZE[1]*SCREEN_RATE))
screen = pygame.display.set_mode(fbs, pygame.RESIZABLE | pygame.DOUBLEBUF | pygame.HWSURFACE)

player = Player()
start = time.perf_counter()
FRAME = 0.5 # 0.5s做一次数据更新
CARD_SURFACE_RATE = 1056/691
WIDTH_RATE = 3 # 遮住显示的牌和正常牌的宽度比

cardsSurfaces = {}
def cardsInit():
    path = PATH + "cards\\"
    fileNames = os.listdir(path)
    for each in fileNames:
        cardsSurfaces[each.split('.')[0]] = pygame.image.load(PATH + "cards\\" + each).convert_alpha()


def cardsToSurfaces(cards, fbs, screen):
    width = int(fbs[0]/(27+WIDTH_RATE-1)/2*WIDTH_RATE)
    height = int(CARD_SURFACE_RATE * width)
    top = int(fbs[1] - 1.25 * height)
    left = (fbs[0] - (len(cards) + WIDTH_RATE) * (width / WIDTH_RATE))//2
    for i in range(0, len(cards)):
        card = pygame.transform.smoothscale(cardsSurfaces[cards[i].face + cards[i].suit[0]], [int(width), int(CARD_SURFACE_RATE * width)])
        screen.blit(card, (left + i * (width/WIDTH_RATE), top))

cardsInit()
while True:
    screen.fill(IVORY) # 底图：白色
    now = time.perf_counter()
    if now - start > FRAME:
        start = now
        if player.state == IDLE:
            player.get()
            player.get()
            player.get()
            player.get()
        else:
            player.update()
    cardsToSurfaces(player.cards, fbs, screen)
    pygame.display.flip()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN: # 点击事件立即响应
            pass
        elif event.type == pygame.VIDEORESIZE:
            fbs = (event.w, event.h)
    pygame.time.delay(30)
