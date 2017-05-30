class Polygon:

    def __init__(self,vertices):
        self.vertices = vertices

    def update(self,vertices):
        self.vertices = vertices

    def collide(self,pos):
        j = len(self.vertices) - 1
        c = 0
        for i in range(len(self.vertices)):
            if ( ((self.vertices[i][1] > pos[1]) != (self.vertices[j][1] > pos[1])) and
                     (pos[0] < (self.vertices[j][0] - self.vertices[i][0]) * (pos[1] - self.vertices[i][1]) / (self.vertices[j][1] - self.vertices[i][1]) + self.vertices[i][0]) ):
                c = not c
            j = i

        return c




