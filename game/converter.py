import items as item
import json

def main():
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

main()