from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import time
import random
import sys
sys.path.append('.\\game')
from constants import *
from gadgat import *
# Create your views here.
# 该服务器暂时只开启一个房间
# 游戏逻辑是：用一个{key,cards}维护四个用户的信息，每个用户一秒钟进行四次请求，进行各项信息的维护，要保证服务器信息不出错


Rooms = [] #data中"key":cards
# {"roomID":0, "state":WATTING, "focus":, "time":, "data":{}}
def initGame(ID):
    suit = ["Heart", "Spade", "Diamond", "Club"]
    face = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
    cards = []
    for each1 in face:
        for each2 in suit:
            cards.append([each1, each2])
            cards.append([each1, each2])
    cards.append(["RedJoker", "Joker"])
    cards.append(["BlackJoker", "Joker"])
    cards.append(["RedJoker", "Joker"])
    cards.append(["BlackJoker", "Joker"])
    random.shuffle(cards)
    i = 0
    for each in Rooms[ID]["data"].keys():
        Rooms[ID]["data"][each] = cards[i:i+27]
        i += 27
    Rooms[ID]["players"] = [i for i in Rooms[ID]["data"].keys()]
    Rooms[ID]["focus"] = random.randint(0,3)
    Rooms[ID]["time"] = time.perf_counter()
    Rooms[ID]["discard"] = ['', '', '', '']

def checkRooms():
    for each in Rooms:
        if each["state"] == WATTING:
            return each["roomID"]
    Rooms.append({"roomID":len(Rooms), "state":WATTING, "data":{}})
    return len(Rooms) - 1

@csrf_exempt
def game(request): #第一次是get请求，之后是post请求
    if request.method == "GET": # get请求只管加入房间
        key = generateRandomStr(10)
        roomID = checkRooms()
        Rooms[roomID]["data"][key] = ""
        return JsonResponse({"roomID":roomID, "key":key}) # 将房间号和请求一起返回
    if request.method == "POST": # post请求在有了房间号之后发出，用于同步本机和服务器之间的信息
        roomID = int(request.POST["roomID"])
        key = request.POST["key"]
        room = Rooms[roomID]
        ret = {}
        if request.POST["func"] == "update": # 用户仅仅是想获得信息
            if room["state"] == WATTING:
                if len(Rooms[roomID]["data"]) == 4:
                    room["state"] = READY
                    initGame(roomID)
                else:
                    ret["state"] = "wait"
            if room["state"] == READY:
                ret["state"] = "ready"
                ret["cards"] = room["data"][key]
                ret["players"] = room["players"]
                now = time.perf_counter()
                if now - room["time"] > ROUNDTIME:
                    room["time"] = time.perf_counter()
                    room["focus"] = (room['focus'] + 1) % 4
                ret["time"] = int(now - room["time"])
                ret["focus"] = room["players"][room["focus"]]
                ret["discard"] = room["discard"]
        return JsonResponse(ret)
                    