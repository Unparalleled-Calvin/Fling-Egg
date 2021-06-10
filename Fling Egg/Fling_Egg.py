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
SELECT_RATE = 1/3 # 选中的牌冒出去1/3

BOTTOM_MARGIN_RATE = 1/10 # 下页边距占页面高度的1/10

#以下是一些关于字体的常量设定
SYS_FONT='Verdana'#字体
FONT = pygame.font.SysFont(SYS_FONT,30)#字号
FONT_COLOR = SQUASH_BLOSSOM#颜色

cardsSurfaces = {}
def cardsInit():
    path = PATH + "cards\\"
    fileNames = os.listdir(path)
    for each in fileNames:
        cardsSurfaces[each.split('.')[0]] = pygame.image.load(PATH + "cards\\" + each).convert_alpha()


def cardsToSurfaces(cards, select, fbs, screen):
    ret = [] # 返回牌渲染的四元组矩形
    width = int(fbs[0]/(27+WIDTH_RATE-1)/2*WIDTH_RATE)
    height = int(CARD_SURFACE_RATE * width)
    top = int((1 - BOTTOM_MARGIN_RATE) * fbs[1] - height)
    left = (fbs[0] - (len(cards) + WIDTH_RATE) * (width / WIDTH_RATE))//2
    for i in range(0, len(cards)):
        card = pygame.transform.smoothscale(cardsSurfaces[cards[i].face + cards[i].suit[0]], [int(width), int(CARD_SURFACE_RATE * width)])
        cardLeft = left + i * (width/WIDTH_RATE)
        cardTop = top if cards[i] not in select else top - SELECT_RATE * height
        screen.blit(card, (cardLeft, cardTop))
        ret.insert(0, [cardLeft, cardLeft + width, cardTop, cardTop + height])
    return ret
            
def timeToSurface(time, fbs, screen):
    timeFont = FONT.render(str(time), True, FONT_COLOR)
    timeFontSize=FONT.size(str(time))
    screen.blit(timeFont, [(fbs[0]-timeFontSize[0])//2, (fbs[1]-timeFontSize[1])//2,])
    

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
    cardsPos = cardsToSurfaces(player.cards, player.select, fbs, screen)
    timeToSurface(player.time, fbs, screen)
    pygame.display.flip()    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN: # 点击事件立即响应
            cardsCount = len(cardsPos)
            for i in range(0, cardsCount):
                each = cardsPos[i]
                if event.pos[0] > each[0] and event.pos[0] < each[1] and event.pos[1] > each[2] and event.pos[1] < each[3]:
                    luckyCard = player.cards[cardsCount - i -1]
                    if luckyCard in player.select:
                        player.select.Remove(luckyCard)
                    else:
                        player.select.append(luckyCard)
                    break
        elif event.type == pygame.VIDEORESIZE:
            fbs = (event.w, event.h)
    pygame.time.delay(30)
