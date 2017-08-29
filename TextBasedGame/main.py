import sys

enc = sys.getdefaultencoding()
mapText = open("map.txt", "r", encoding=enc).read()

delimA = "Î±Å§"
delimB = "Å¦Î²"
delimW = "Ï‰Å·"
delimP = "Æ…Ï†"
delimO = "ÏƒÆ²"
delimU = "Å¿Î¼"

roomCodes = mapText.split(delimA)
rooms = []
tickItems = []


def item(name, type, amount, desc, data):
    return {"name": name, "type": type, "amount": amount, "desc": desc, "data": data}


def boolToString(bool):
    if bool:
        return "y"
    else:
        return "n"


def stringToBool(string):
    if string == "y":
        return True
    else:
        return False


for roomCode in roomCodes:
    if roomCode == "":
        rooms.append(0)
        continue

    roomAttributes = roomCode.split(delimB)

    index = int(roomAttributes[0])
    desc = roomAttributes[1]

    coords = roomAttributes[2].split(delimW)
    pos = {'x': int(coords[0]), 'y': int(coords[1])}

    doors = roomAttributes[3].split(delimW)
    doorObj = {'e': 0, 'n': 0, 'w': 0, 's': 0}
    doorObj['e'] = int(doors[0])
    doorObj['n'] = int(doors[1])
    doorObj['w'] = int(doors[2])
    doorObj['s'] = int(doors[3])

    locks = roomAttributes[4].split(delimW)
    locksObj = {'e': 0, 'n': 0, 'w': 0, 's': 0}
    locksObj['e'] = stringToBool(locks[0])
    locksObj['n'] = stringToBool(locks[1])
    locksObj['w'] = stringToBool(locks[2])
    locksObj['s'] = stringToBool(locks[3])

    items = roomAttributes[5].split(delimW)
    itemsObj = []
    for itemText in items:
        if itemText == "":
            break

        itemAttributes = itemText.split(delimP)

        itemType = itemAttributes[0]
        itemAmount = int(itemAttributes[1])
        itemName = itemAttributes[2]
        itemDesc = itemAttributes[3]

        itemDatas = itemAttributes[4].split(delimO)
        datasObj = []
        for itemDataText in itemDatas:
            if itemDataText == "":
                continue

            dataParts = itemDataText.split(delimU)

            dataKey = dataParts[0]
            dataValue = 0

            try:
                dataValue = float(dataParts[1])
            except ValueError:
                dataValue = dataParts[1]

            dataObj = {'k': dataKey, 'v': dataValue}
            datasObj.append(dataObj)

        itemObj = item(itemName, itemType, itemAmount, itemDesc, datasObj)
        itemsObj.append(itemObj)

    roomObj = {'i': index, "pos": pos, "doors": doorObj, "locks": locksObj, "items": itemsObj, "desc": desc}
    rooms.append(roomObj)

player = {"index": 0, "newRoom": True, "items":[]}


def itemWithData(key, value, items, lower=False):
    if (lower):
        for item in items:
            if item[key].lower() == value.lower():
                return item
    else:
        for item in items:
            if item[key] == value:
                return item
    return None


def dataForKey(key, item):
    for data in item["data"]:
        if data['k'] == key:
            return data

    return None

def haveKeyForDoor(room, direction):
    for item in player["items"]:
        if item["type"] == "key":
            dirData = dataForKey("dir", item)
            roomData = dataForKey("room", item)
            if not(dirData is None) and not(roomData is None):
                dir = dirData['v']
                roomNum = int(roomData['v'])
                if dir == direction and roomNum == room["i"]:
                    return True

    return False

def updateTickItems():
    for item in tickItems:
        on = dataForKey("lit", item)
        if not(on is None):
            if (on['v'] == "False"):
                continue

        tickDataVal = dataForKey("roomTick", item)
        tickDataNames = tickDataVal['v'].split(",")

        for tickDataName in tickDataNames:
            tickData = dataForKey(tickDataName, item)

            if tickDataName == "uses":
                if tickData['v'] == 0:
                    item["amount"] -= 1
                    on['v'] = "False"
                    if item["amount"] == 0:
                        print("You used your last " + item["name"] + ".")
                        player["items"].remove(item)
                    else:
                        print("You have " + str(item["amount"]) + " " + item["name"] + " remaining.")

                    continue

            tickData['v'] -= 1

def move(room, direction):
    if room["doors"][direction] > -1:
        if room["locks"][direction]:
            if haveKeyForDoor(room, direction):
                player["index"] = room["doors"][direction]
                player["newRoom"] = True
                print("You use the your key to unlock the door.")
                updateTickItems()
            else:
                print("This door is locked.")
        else:
            player["index"] = room["doors"][direction]
            player["newRoom"] = True
            updateTickItems()

    else:
        print("There's no door on this wall.")

def printRoom(room):
    if canSee(room):
        print(room["desc"])
        printItems(room)
    else:
        print("It's too dark to see anything.")


def canSee(room):
    for item in player["items"]:
        if item["type"] == "torch":
            onData = dataForKey("lit", item)
            if onData['v'] == "True":
                return True

    visItem = itemWithData("type", "light", room["items"])
    if visItem is None:
        return False
    else:
        visData = dataForKey("bright", visItem)
        if visData is None:
            return False
        elif visData['v'] == "True":
            return True
        elif visData['v'] == "False":
            return False
        else:
            print("Invalid visibility boolean")
            return False


def printItems(room, on=None):
    viewableItems = []

    if on is None:
        for item in room["items"]:
            itemOn = dataForKey("on", item)
            if item["type"] != "light" and itemOn is None:
                viewableItems.append(item["name"])

        if len(viewableItems) != 0:
            print("You can see these items in the room:")

    else:
        onItem = itemWithData("name", on, room["items"], True)

        for item in room["items"]:
            itemOn = dataForKey("on", item)
            if item["type"] != "light" and not(itemOn is None) and itemOn['v'] == on:
                viewableItems.append(item["name"])

        if len(viewableItems) == 0:
            if onItem is None:
                print(on + " isn't here")
            else:
                print("  There's nothing on " + on + ".")
        else:
            if onItem is None:
                print("  The " + on + " has these items:")
            else:
                print(onItem["name"] + ", " + str(onItem["amount"]))
                print("  " + onItem["desc"])
                print("  The " + onItem["name"] + " has these items:")

    for name in viewableItems:
        print("    " + name)

def doorInfo(room, direction):
    index = room["doors"][direction]
    locked = room["locks"][direction]

    if (index > -1):
        if (locked):
            if haveKeyForDoor(room, direction):
                print("You have the key for this door.")
            else:
                print("This door is locked.")
        else:
            print("This door is unlocked.")
    else:
        print("There's no door there.")

def printItem(room, itemName):
    for item in room["items"] + player["items"]:
        if item["name"].lower() == itemName:
            print(item["name"] + ", " + str(item["amount"]))
            print("  " + item["desc"])
            return

    print("That isn't here.")

def takeItem(room, itemName):
    for item in room["items"]:
        if item["name"].lower() == itemName:
            canTake = dataForKey("canTake", item)
            if not(canTake is None) and canTake['v'] == "False":
                print("You can't take that.")
                return
            else:
                player["items"].append(item)
                tickItem = dataForKey("roomTick", item)
                if not(tickItem is None):
                    tickItems.append(item)

                room["items"].remove(item)
                itemOn = dataForKey("on", item)
                if not(itemOn is None):
                    item["data"].remove(itemOn)

                print("Added " + item["name"] + " to your 'items'.")
                return

    print("That isn't here.")

def dropItem(room, itemName, on=None):
    item = itemWithData("name", itemName, player["items"], True)

    if item is None:
        print("You don't have " + itemName + " in your 'items'.")
        return
    else:
        player["items"].remove(item)
        tickItem = dataForKey("roomTick", item)
        if not (tickItem is None):
            tickItems.remove(item)

    if on is None:
        room["items"].append(item)
        print("Dropped " + item["name"] + ".")
    else:
        if on != "ground":
            onItem = itemWithData("name", on, room["items"], True)
            if onItem is None:
                print(on + " isn't here or doesn't exist.")
                return

        room["items"].append(item)
        item["data"].append({'k':"on", 'v':on.lower()})
        print("Dropped " + item["name"] + " on " + on + ".")

def useItemOnItem(room, itemName, onItemName):
    item = itemWithData("name", itemName, player["items"], True)
    onItem = itemWithData("name", onItemName, player["items"], True)
    if item is None:
        print("You don't have " + itemName)
        return
    if onItem is None:
        print("You don't have " + onItemName)
        return

    if onItem["type"] == "torch" and item["type"] == "lighter":
        onData = dataForKey("lit", onItem)
        if onData['v'] == "True":
            print("Your torch is already lit.")
            return

        lighterUses = dataForKey("uses", item)
        if lighterUses['v'] == 0:
            print("Your " + item["name"] + " doesn't have any more uses.")
            return

        maxTime = dataForKey("maxFireTime", onItem)
        fireTime = dataForKey("uses", onItem)

        fireTime['v'] = maxTime['v']
        lighterUses['v'] -= 1

        if lighterUses['v'] == 0:
            print("Your " + item["name"] + " doesn't have any more uses.")
        else:
            print("Your " + item["name"] + " has " + str(lighterUses['v']) + " uses remaining.")
            onData['v'] = "True"
            print("Your torch illuminates the room.")
            printRoom(room)

def useItem(room, itemName):
    item = itemWithData("name", itemName, player["items"], True)
    if item is None:
        print("You don't have that.")
        return

while True:
    room = rooms[player["index"]]
    if player["newRoom"]:
        printRoom(room)

    player["newRoom"] = False

    cmd = input(">>").lower()
    cmdParts = cmd.split()
    cmd = cmdParts[0]

    if len(cmdParts) < 2:
        if cmd == "look":
            printRoom(room)
        elif cmd == "items":
            if cmd == "items":
                if len(player["items"]) == 0:
                    print("You have no items.")
                else:
                    print("You have these items:")
                    for item in player["items"]:
                        print("  " + item["name"])
        else:
            print("That doesn't make sense.")
    else:
        mod = cmdParts[1]

        if cmd == "go":
            if mod == "e" or mod == "east":
                move(room, "e")
            elif mod == "n" or mod == "north":
                move(room, "n")
            elif mod == "w" or mod == "west":
                move(room, "w")
            elif mod == "s" or mod == "south":
                move(room, "s")
        elif cmd == "use":
            if "on" in cmdParts:
                index = cmdParts.index("on")
                itemName = " ".join(cmdParts[1:index])
                useItemName = " ".join(cmdParts[index + 1:])
                useItemOnItem(room, itemName, useItemName)
            else:
                useItem(room, " ".join(cmdParts[1:]))
        elif canSee(room):
            if cmd == "look":
                if mod == "e" or mod == "east":
                    doorInfo(room, "e")
                elif mod == "n" or mod == "north":
                    doorInfo(room, "n")
                elif mod == "w" or mod == "west":
                    doorInfo(room, "w")
                elif mod == "s" or mod == "south":
                    doorInfo(room, "s")
                elif mod == "on":
                    printItems(room, cmdParts[2])
                else:
                    printItem(room, " ".join(cmdParts[1:]))

            elif cmd == "take":
                takeItem(room, " ".join(cmdParts[1:]))
            elif cmd == "drop":
                if "on" in cmdParts:
                    index = cmdParts.index("on")
                    itemName = " ".join(cmdParts[1:index])
                    dropName = " ".join(cmdParts[index+1:])
                    dropItem(room, itemName, dropName)
                else:
                    dropItem(room, mod)

            else:
                print("That doesn't make sense.")
        else:
            print("It's too dark to see anything.")