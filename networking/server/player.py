class Player:
    def __init__(self, username, connection):
        self.username = username
        self.x = 0
        self.y = 0
        self.connection = connection
        self.current_room = None
        self.colour = None

    def send(self, data):
        self.connection.sendall(data)
