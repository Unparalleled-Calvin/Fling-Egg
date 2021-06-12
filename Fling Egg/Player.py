from functools import cmp_to_key
import requests
import json

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

IDLE = 0
WAITTING = 1
READY = 2

REQUEST_INTERNAL = 0.5

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
    def __init__(self, face, suit, ID):
        self.face = face # 2-K统一以".x"表示，A-RedJoker正常字符串
        self.value = faceToValue[face]
        self.suit = suit # Heart, Spade, Diamond, Club, Joker
        self.ID = ID
    def __repr__(self):
        return "Card({}, {}, {})".format(self.face, self.suit, self.ID)

class Deck():
    # deck是牌堆，一种牌型
    def __init__(self, cards): # 抛进来一堆牌，自动检查牌型
        self.cards = Select(sorted(cards, key=cmp_to_key(compareCard)))
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
        if number == 0:
            self.type = "None"
        elif number == 1:
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
        elif number == 6:
            if faceSame(cards):
                self.type = "Bomb"
                self.value = cards[0].value
            elif faceStraight([cards[0]. cards[2], cards[4]]) and faceSame(cards[0:2]) and faceSame(cards[2:4]) and faceSame(cards[4:6]):
                self.type = "Triplet"
                self.value = cards[0].value
            elif faceStraight(cards[3:5]) and faceSame(cards[0:3]) and faceSame(cards[3:6]):
                self.type = "Steel"
                self.value = cards[0].value
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
        data.append([each.face, each.suit, each.ID])
    return data

def dataToCards(data): # 传入一个列表，传出一个card列表
    cards = []
    for each in data:
        cards.append(Card(each[0], each[1], each[2]))
    return cards

class Select(list):
    def __contains__(self, card):
        for each in self:
            if each.face == card.face and each.suit == card.suit and each.ID == card.ID:
                return True
        return False
    
    def Remove(self, card):
        for each in self:
            if each.face == card.face and each.suit == card.suit and each.ID == card.ID:
                self.remove(each)
                break

class Player():
    def __init__(self):
        self.cards = Select()
        self.select = Select()
        self.roomID = None
        self.key = ""
        self.state = IDLE
        self.start = 0
        self.time = 0
        self.winner = "None"
        self.focus = "None"

    def get(self):
        response = requests.get(clientURL)
        roomData = json.loads(response.text)
        self.roomID = roomData["roomID"]
        self.key = roomData["key"]
        self.state = roomData["state"]

    def update(self):
        data = {
            "roomID": self.roomID,
            "key": self.key,
            "func": "update", 
        }
        response = requests.post(clientURL, data = json.dumps(data), headers={'Content-Type':'application/json'})
        roomData = json.loads(response.text)
        self.cards = Select(sorted(dataToCards(roomData["cards"]), key=cmp_to_key(compareCard)))
        self.state = roomData["state"]
        self.winner = roomData["winner"]
        self.time = roomData["time"]
        self.cardNumbers = roomData["cardNumbers"]
        if self.state == READY:
            self.focus = roomData["focus"]
            self.history = roomData["discard"]

    def discard(self): #注意，最好这里要是同一个指针
        try:
            deck = Deck(self.select)
            flag = 0
            deck1, deck2, deck3 = (Deck(dataToCards(i[0])) for i in self.history[1:4])
            if deck3.type != "None":
                flag = larger(deck, deck3)
            elif deck2.type != "None":
                flag = larger(deck, deck2)
            elif deck1.type != "None":
                flag = larger(deck, deck1)
            else:
                flag = 1
            for each in self.select:
                self.cards.Remove(each)
            data = {
                "roomID": self.roomID,
                "key": self.key,
                "func": "discard", 
                "discard": cardsToData(self.select if flag else []),
                "cards": cardsToData(self.cards)
            }
            if flag == 0:
                print(self.key, "smaller!")
            else:
                response = requests.post(clientURL, data = json.dumps(data), headers={'Content-Type':'application/json'})
            self.update()
        except Exception as e:
             print("Can not discard!", e)
        self.select.clear()