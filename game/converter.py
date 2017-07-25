
import json, random

def jsonConverter():
    items = {0:serialize(item.Potion()),
            1:serialize(item.Sword())}

    with open('data/items.json','w') as f:
        json.dump(items,f)

    with open('data/items.json','r') as f:
        print(json.load(f))


def serialize(obj):
    data = {'class':type(obj).__name__}
    data.update(vars(obj))
    return data

class Map():
    def __init__(self,size):
        self.map = []
        self.size = size

        self.map = [[0 for x in range(size[1])] for y in range(size[0])]

        self.createDungeon()

    def create_room(self,room):
        for y in range(room.y1,room.y2 + 1):
            for x in range(room.x1,room.x2 + 1):
                self.map[y][x] = 1

    def create_h_tunnel(self,x1,x2,y):
        for x in range(min(x1,x2),max(x1,x2) + 1):
            self.map[y][x] = 1

    def create_v_tunnel(self,y1,y2,x):
        for y in range(min(y1,y2),max(y1,y2) + 1):
            self.map[y][x] = 1

    def createDungeon(self):
        ROOM_MAX_SIZE = 6
        ROOM_MIN_SIZE = 2
        MAX_ROOMS = 30

        rooms = []
        num_rooms = 0

        for r in range(MAX_ROOMS):
            w = random.randint(ROOM_MIN_SIZE,ROOM_MAX_SIZE)
            h = random.randint(ROOM_MIN_SIZE,ROOM_MAX_SIZE)

            x = random.randint(0,self.size[0] - w -1)
            y = random.randint(0,self.size[1] - h -1)

            new_room = Map.Room(x,y,w,h)

            failed = False
            for other_room in rooms:
                if new_room.intersect(other_room):
                    failed = True
                    break

            if not failed:
                self.create_room(new_room)
                (new_x,new_y) = new_room.center()

                if num_rooms == 0:
                    print('player spawn at:', (new_x,new_y))
                else:
                    # If another room, create a tunnel passage
                    (prev_x,prev_y) = rooms[num_rooms-1].center()
                    if random.randint(0,1) == 1:
                        self.create_h_tunnel(prev_x, new_x, prev_y)
                        self.create_v_tunnel(prev_y, new_y, new_x)
                    else:
                        self.create_v_tunnel(prev_y, new_y, prev_x)
                        self.create_h_tunnel(prev_x, new_x, new_y)

                rooms.append(new_room)
                num_rooms += 1

        spawn_pos = rooms[0].center()
        exit_pos = rooms[num_rooms - 1].center()
        self.map[spawn_pos[1]][spawn_pos[0]] = 8
        self.map[exit_pos[1]][exit_pos[0]] = 9

    class Room():
        def __init__(self,x,y,w,h):
            self.x1 = x
            self.y1 = y
            self.x2 = x + w
            self.y2 = y + h

        def center(self):
            x = (self.x1 + self.x2) // 2
            y = (self.y1 + self.y2) // 2
            return (x,y)

        def intersect(self,other):
            return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                    self.y1 <= other.y2 and self.y2 >= other.y1)

def test():
    x = Map([32,32])
    for y in range(x.size[1]):
        print(x.map[y])

test()