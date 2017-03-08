class Subscriber:

    def __init__(self, id, notify):
        self.id = id
        self.notify = notify

    def setID(self, id):
        self.id = id

    def getID(self):
        return self.id

    def setTarget(self, notify):
        self.notify = notify

    def getNotify(self):
        return self.notify