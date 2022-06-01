
class Inventory:
    def __init__(self,holder,capacity):
        self.items = []
        self.capacity = capacity
        self.holder = holder

    def addItem(self,item):
        if item.stackable and (item in self.items):
            self.findItem(item).amount += 1
        elif len(self.items) < self.capacity:
            self.items.append(item)

    def addItems(self,items):
        for item in items:
            if item.stackable and (item in self.items):
                self.findItem(item).amount += 1
            elif len(self.items) < self.capacity:
                self.items.append(item)

    def displayInventory(self):
        print('Inventory (%i):' % len(self.items))
        for item in self.items:
            print('%s (%i)' % (item.name,item.amount))

    def findItem(self,item):
        for i in self.items:
            if i.name == item.name:
                return i

    def useItem(self,item):
        if item in self.items:
            if item.type == 'equipment':
                current_equip = self.holder.stats.equipment[item.equipment_type]
                if current_equip:
                    current_equip.unequip(self.holder)
                    self.addItem(current_equip)

                self.holder.stats.equipment[item.equipment_type] = item
                item.use(self.holder)
                self.removeItem(item)
            else:
                item.use(self.holder)
                # if item is stackable remove by amount else remove the item completely
                if item.stackable:
                    item.amount -= 1
                    if item.amount <= 0:
                        self.removeItem(item)
                else:
                    self.removeItem(item)

        self.displayInventory()

    def removeItem(self,index):
        self.items.pop(index)

    def removeItem(self,item):
        self.items.remove(item)

    def getItemData(self,index):
        try:
            return (self.items[index].image,self.items[index].amount)
        except:
            return (None,0)
