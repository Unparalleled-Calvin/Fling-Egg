from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import time
import json
import random
import sys
sys.path.append(".\\game")
from constants import *
from gadgat import *
# Create your views here.
# 该服务器暂时只开启一个房间
# 游戏逻辑是：用一个{key,cards}维护四个用户的信息，每个用户一秒钟进行四次请求，进行各项信息的维护，要保证服务器信息不出错


Rooms = [] #data中"key":cards
# {"roomID":0, "state":WAITTING, "focus":, "time":, "data":{}}
def initGame(ID):
    suit = ["Heart", "Spade", "Diamond", "Club"]
    face = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
    cards = []
    for each1 in face:
        for each2 in suit:
            cards.append([each1, each2, 0])
            cards.append([each1, each2, 1])
    cards.append(["RedJoker", "Joker", 0])
    cards.append(["BlackJoker", "Joker", 1])
    cards.append(["RedJoker", "Joker", 0])
    cards.append(["BlackJoker", "Joker", 1])
    random.shuffle(cards)
    i = 0
    for each in Rooms[ID]["data"].keys():
        Rooms[ID]["data"][each] = cards[i:i+27]
        i += 27
    Rooms[ID]["players"] = [i for i in Rooms[ID]["data"].keys()]
    players = Rooms[ID]["players"]
    focus = random.randint(0,3)
    Rooms[ID]["focus"] = focus
    Rooms[ID]["time"] = time.perf_counter()
    Rooms[ID]["discard"] = [[[], players[focus]], [[], players[(focus+1)%4]], [[], players[(focus+2)%4]], [[], players[(focus+3)%4]]]

def newRoom():
    return {
            "roomID":len(Rooms), 
            "state":WAITTING, 
            "data":{},
            "time":0,
           }

def checkRooms():
    for each in Rooms:
        if each["state"] == WAITTING:
            return each["roomID"]
    Rooms.append(newRoom())
    return len(Rooms) - 1

@csrf_exempt
def game(request): #第一次是get请求，之后是post请求
    def roomRoundChange(room, data):
        room["discard"] = room["discard"][1:4] + [data]
        room["time"] = time.perf_counter()
        room["focus"] = (room["focus"] + 1) % 4
    def roomInfo(room):
        ret = {}
        ret["state"] = room["state"]
        ret["players"] = [i for i in room["data"].keys()]
        ret["time"] = ROUNDTIME - int(time.perf_counter() - room["time"])
        if room["state"] == READY:
            ret["focus"] = room["players"][room["focus"]]
            ret["discard"] = room["discard"]
        ret["winner"] = "None"
        for key in room["data"]:
            if len(room["data"][key]) == 0:
                ret["winner"] = key
                break
        return ret
    if request.method == "GET": # get请求只管加入房间
        key = generateRandomStr(10)
        roomID = checkRooms()
        Rooms[roomID]["data"][key] = ""
        return JsonResponse({"roomID":roomID, "key":key, "state":Rooms[roomID]["state"]}) # 将房间号和请求一起返回
    if request.method == "POST": # post请求在有了房间号之后发出，用于同步本机和服务器之间的信息
        body = json.loads(request.body)
        roomID = int(body["roomID"])
        key = body["key"]
        room = Rooms[roomID]
        ret = {}
        if body["func"] == "update": # 用户仅仅是想获得信息
            if room["state"] == WAITTING:
                if len(Rooms[roomID]["data"]) == 4:
                    room["state"] = READY
                    initGame(roomID)
            if room["state"] == READY:
                if time.perf_counter() - room["time"] > ROUNDTIME:
                    roomRoundChange(room, [[],key])
            ret = roomInfo(room)
            ret["cards"] = room["data"][key]
        elif body["func"] == "discard":
            room["data"][key] = body["cards"]
            roomRoundChange(room,[body["discard"], key])
            ret = roomInfo(room)
            ret["cards"] = room["data"][key]
        return JsonResponse(ret)
                    