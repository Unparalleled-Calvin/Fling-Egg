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
MY_WIDTH_RATE = 3 # 上下遮住显示的牌和正常牌的宽度比
TOP_WIDTH_RATE = 5
HEIGHT_RATE = 8 # 两侧遮住显示的牌和正常牌的高度比
SELECT_RATE = 1/3 # 选中的牌高出1/3

BOTTOM_MARGIN_RATE = 1/10 # 页边距
TOP_MARGIN_RATE = 1/10
LEFT_MARIGIN_RATE = 1/8
RIGHT_MARIGIN_RATE = 1/8

ARROW_WIDTH_RATE = 1/18
ARROW_LENGTH_RATE = 1/10
ARROW_CENTRE_MARGIN = 1/15


#以下是一些关于字体的常量设定
SYS_FONT='Verdana'#字体
FONT_COLOR = SQUASH_BLOSSOM#颜色

Surfaces = {}
def cardsInit():
    path = PATH + "cards\\"
    fileNames = os.listdir(path)
    for each in fileNames:
        Surfaces[each.split('.')[0]] = pygame.image.load(PATH + "cards\\" + each).convert_alpha()

cardsInit()

def drawCards(cards, select, fbs, screen):
    ret = [] # 返回牌渲染的四元组矩形
    width = int(fbs[0]/(27+MY_WIDTH_RATE-1)/2*MY_WIDTH_RATE)
    height = int(CARD_SURFACE_RATE * width)
    top = int((1 - BOTTOM_MARGIN_RATE) * fbs[1] - height)
    left = (fbs[0] - (len(cards) + MY_WIDTH_RATE - 1) * (width / MY_WIDTH_RATE))//2
    for i in range(0, len(cards)):
        card = pygame.transform.smoothscale(Surfaces[cards[i].face + cards[i].suit[0]], [int(width), int(CARD_SURFACE_RATE * width)])
        cardLeft = left + i * (width/MY_WIDTH_RATE)
        cardTop = top if cards[i] not in select else top - SELECT_RATE * height
        screen.blit(card, (cardLeft, cardTop))
        ret.insert(0, [cardLeft, cardLeft + width, cardTop, cardTop + height])
    return ret
            
def drawTimeAndArrow(player, fbs, screen):
    time = player.time
    FONT = pygame.font.SysFont(SYS_FONT, int(30 * fbs[0] / 1066))
    timeFont = FONT.render(str(time), True, FONT_COLOR)
    timeFontSize=FONT.size(str(time))
    screen.blit(timeFont, [(fbs[0]-timeFontSize[0])//2, (fbs[1]-timeFontSize[1])//2])
    focus_index = [each[0] for each in player.cardNumbers].index(player.focus)
    my_index = [each[0] for each in player.cardNumbers].index(player.key)
    offset = (my_index - focus_index + 4) % 4
    if offset == 0:
        arrow = pygame.transform.smoothscale(pygame.transform.rotate(Surfaces["arrow"], 270), [int(ARROW_WIDTH_RATE * fbs[0]), int(ARROW_LENGTH_RATE * fbs[1])])
        screen.blit(arrow, (int((1 - ARROW_WIDTH_RATE) * fbs[0] / 2), int((0.5 + ARROW_CENTRE_MARGIN) * fbs[1])))
    elif offset == 1:
        arrow = pygame.transform.smoothscale(pygame.transform.rotate(Surfaces["arrow"], 0), [int(ARROW_LENGTH_RATE * fbs[1]), int(ARROW_WIDTH_RATE * fbs[1])])
        screen.blit(arrow, (int((0.5 + ARROW_CENTRE_MARGIN) * fbs[0]), int((0.5 - ARROW_WIDTH_RATE / 2) * fbs[1])))
    elif offset == 2:
        arrow = pygame.transform.smoothscale(pygame.transform.rotate(Surfaces["arrow"], 90), [int(ARROW_WIDTH_RATE * fbs[0]), int(ARROW_LENGTH_RATE * fbs[1])])
        screen.blit(arrow, (int((1 - ARROW_WIDTH_RATE) * fbs[0] / 2), int((0.5 - ARROW_CENTRE_MARGIN - ARROW_LENGTH_RATE) * fbs[1])))
    elif offset == 3:
        arrow = pygame.transform.smoothscale(pygame.transform.rotate(Surfaces["arrow"], 180), [int(ARROW_LENGTH_RATE * fbs[1]), int(ARROW_WIDTH_RATE * fbs[1])])
        screen.blit(arrow, (int((0.5 - ARROW_CENTRE_MARGIN - ARROW_LENGTH_RATE) * fbs[0]), int((0.5 - ARROW_WIDTH_RATE / 2) * fbs[1])))
    
def drawOthers(player, fbs, screen):
    width = int(fbs[0]/(27+MY_WIDTH_RATE-1)/2*MY_WIDTH_RATE)
    height = int(CARD_SURFACE_RATE * width)
    card = pygame.transform.smoothscale(Surfaces["back"], [int(width), int(CARD_SURFACE_RATE * width)])
    def drawLeftRight(leftCardNumber, rightCardNumber):
        cardLeft = LEFT_MARIGIN_RATE * fbs[0]
        top = (fbs[1] - (leftCardNumber[1] + HEIGHT_RATE - 1) * (height / HEIGHT_RATE))//2
        for i in range(0, leftCardNumber[1]):
            cardTop = top + i * (height/HEIGHT_RATE)
            screen.blit(card, (cardLeft, cardTop))
        cardLeft = (1 - RIGHT_MARIGIN_RATE) * fbs[0] - width
        top = (fbs[1] - (rightCardNumber[1] + HEIGHT_RATE - 1) * (height / HEIGHT_RATE))//2
        for i in range(0, rightCardNumber[1]):
            cardTop = top + i * (height/HEIGHT_RATE)
            screen.blit(card, (cardLeft, cardTop))
    
    def drawTop(topCardNumber):
        cardTop = int(TOP_MARGIN_RATE * fbs[1])
        left = (fbs[0] - (topCardNumber[1] + TOP_WIDTH_RATE - 1) * (width / TOP_WIDTH_RATE))//2
        for i in range(0, topCardNumber[1]):
            cardLeft = left + i * (width/TOP_WIDTH_RATE)
            screen.blit(card, (cardLeft, cardTop))

    index = player.cardNumbers.index([player.key, len(player.cards)])
    drawLeftRight(player.cardNumbers[(index - 1 + 4) % 4], player.cardNumbers[(index + 1) % 4])
    drawTop(player.cardNumbers[(index + 2) % 4])

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
    if player.state == READY:
        drawOthers(player, fbs, screen)
        drawTimeAndArrow(player, fbs, screen)
        cardsPos = drawCards(player.cards, player.select, fbs, screen)
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
