from functools import cmp_to_key
import urllib.request
import urllib.parse
import json
import time

clientURL = "http://127.0.0.1:8000/game"

faceToValue = {
    "2" : 2,
    "3" : 3,
    "4" : 4,
    "5" : 5,
    "6" : 6,
    "7" : 7,
    "8" : 8,
    "9" : 9,
    "10" : 10,
    "J" : 11,
    "Q" : 12,
    "K" : 13,
    "A" : 14,
    "BlackJoker" : 15,
    "RedJoker" : 16,
}


def compareCard(card1, card2):
    if card1.value == card2.value:
        if card1.suit > card2.suit:
            return -1
        elif card1.suit == card2.suit:
            return 0
        else:
            return 1
    elif card1.value > card2.value:
        return -1
    else:
        return 1

class Card():
    # face由字符串
    def __init__(self, face, suit):
        self.face = face # 2-K统一以".x"表示，A-RedJoker正常字符串
        self.value = faceToValue[face]
        self.suit = suit # Heart, Spade, Diamond, Club, Joker
    def __repr__(self):
        return "Card({}, {})".format(self.face, self.suit)

class Deck():
    # deck是牌堆，一种牌型
    def __init__(self, cards): # 抛进来一堆牌，自动检查牌型
        self.cards = sorted(cards, key=cmp_to_key(compareCard))
        self.check()
        if self.type == None:
            raise Exception('Wrong Deck!')
    def check(self):
        def faceSame(cards):
            for each in cards:
                if each.face != cards[0].face:
                    return False
            return True
        def faceStraight(cards):
            if len(cards) != 5:
                return False
            for i in range(0, len(cards)):
                if cards[i].value - cards[0].value != i:
                    return False
            if cards[i].value >= 11:
                return False
            return True
        def suitFlush(cards):
            if len(cards) != 5:
                return False
            for i in len(cards):
                if cards[i].suit != cards[0].suit:
                    return False
            return True
        number = len(self.cards)
        cards = self.cards
        if number == 1:
            self.type = "Solo"
            self.value = cards[0].value
        elif number == 2 and faceSame(cards):
            self.type = "Pair"
            self.value = cards[0].value
        elif number == 3 and faceSame(cards):
            self.type = "Triple"
            self.value = cards[0].value
        elif number == 4:
            if faceSame(cards):
                self.type = "Bomb"
                self.value = cards[0].value
            elif cards[0].suit == "Joker" and cards[1].suit == "Joker" and cards[1].suit == "Joker" and cards[1].suit == "Joker":
                self.type = "Rocket"
                self.value = cards[0].value
            else:
                self.type = None
        elif number == 5:
            if faceSame(cards):
                self.type = "Bomb"
                self.value = cards[0].value
            elif faceStraight(cards):
                if suitFlush(cards):
                    self.type = "StraightFlush"
                    self.value = cards[0].value
                else:
                    self.type = "Straight"
                    self.value = cards[0].value
            elif faceSame(cards[0:3]) and faceSame(cards[3:5]):
                self.type = "TripleWithPair"
                self.value = cards[0].value
            elif faceSame(cards[0:2]) and faceSame(cards[2:5]):
                self.type = "TripleWithPair"
                self.value = cards[2].value
            else:
                self.type = None
        elif number <= 8 and faceSame(cards):
            self.type = "Bomb"
            self.value = cards[0].value
        else:
            self.type = None
    def __repr__(self):
        return "Deck(\"{}\", {})".format(self.type, self.cards)
def larger(deck1, deck2): # deck1 大于 deck2
    if deck1.type == "Rocket":
        return True
    elif deck1.type == "Bomb":
        if deck2.type == "Bomb":
            if len(deck1.cards) == len(deck2.cards):
                return deck1.value > deck2.value
            else:
                return len(deck1.cards) > len(deck2.cards)
        elif deck2.type == "StraightFlush":
            return len(deck1.cards) > 5
        else:
            return deck2.type != "Rocket"
    elif deck1.type == "StraightFlush":
        if deck2.type == "StraightFlush":
            return deck1.value > deck2.value;
        elif deck2.type == "Bomb":
            return len(deck2.cards) < 6;
        else:
            return deck2.type != "Rocket";
    else:
        return deck1.type == deck2.type and deck1.value > deck2.value

def cardsToData(cards): # 传出一个列表
    data = []
    for each in cards:
        data.append([each.face, each.suit])
    return data

def dataToCards(data): # 传入一个列表，传出一个card列表
    cards = []
    for each in data:
        cards.append(Card(each[0], each[1]))
    return cards

class Player():
    def __init__(self):
        self.cards = []
        self.select = []
        self.roomID = None
        self.key = ""

    def discard(self): #注意，最好这里要是同一个指针
        for each in self.select:
            self.cards.remove(each)

    def get(self):
        response = urllib.request.urlopen(clientURL)
        roomData = json.loads(response.read().decode("utf-8"))
        self.roomID = roomData["roomID"]
        self.key = roomData["key"]

    def update(self):
        data = {
            "roomID": self.roomID,
            "key": self.key,
            "func": "update", 
        }
        postData = urllib.parse.urlencode(data, doseq=True).encode("utf-8")
        req = urllib.request.Request(clientURL, postData)
        data = json.loads(urllib.request.urlopen(req).read().decode("utf-8"))
        self.cards = sorted(dataToCards(data["cards"]), key=cmp_to_key(compareCard))
        print(self.cards)

a = Player()
a.get()
a.get()
a.get()
a.get()
a.update()
#start = time.perf_counter()
#while True:
#    if time.perf_counter() - start >= 0.25:
#        start = time.perf_counter()
#        a.update()
