from .ui import Button

class UnequipButton(Button):
    def __init__(self,pos,size,string,ui):
        super().__init__(pos,size,string)
        self.ui = ui

    def use(self):
        self.ui.unequipSlot()

class UseButton(Button):
    def __init__(self,pos,size,string,ui):
        super().__init__(pos,size,string)
        self.ui = ui

    def use(self):
        self.ui.useSlot()

class DestroyButton(Button):
    def __init__(self,pos,size,string,ui):
        super().__init__(pos,size,string)
        self.ui = ui

    def use(self):
        self.ui.destroyItem()
