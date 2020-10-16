import sys
from time import sleep, localtime
from weakref import WeakKeyDictionary

from PodSixNet.Server import Server
from PodSixNet.Channel import Channel

class ClientChannel(Channel):
    """
    This is the server representation of a single connected client.
    """
    def __init__(self, nickname, board_state_original, board_state_filled, *args, **kwargs):
        self.nickname = nickname
        self.board_state_original = []
        self.board_state_filled = []
        Channel.__init__(self, *args, **kwargs)

    def Close(self):
        self._server.DelPlayer(self)

    ##################################
    ### Network specific callbacks ###
    ##################################

    def Network_move(self, data):
        self.board_state_filled = data["board_state_filled"]
        self._server.SendToOpponent({"action": "move", "board_state": data, "who": self.nickname})

    def Network_nickname(self, data):
        self.nickname = data['nickname']
        self._server.InformPlayerPresence()

class SudokuServer(Server):
    channelClass = ClientChannel

    def __init__(self, *args, **kwargs):
        Server.__init__(self, *args, **kwargs)
        self.players = WeakKeyDictionary()
        print('Server launched')

    def Connected(self, channel, addr):
        if len(self.players) == 2:
            return
        self.AddPlayer(channel)

    def AddPlayer(self, player):
        print("New Player" + str(player.addr))
        self.players[player] = True
        self.InformPlayerPresence()
        print("players", [p for p in self.players])

    def DelPlayer(self, player):
        print("Deleting Player" + str(player.addr))
        del self.players[player]
        self.InformPlayerPresence()

    def InformPlayerPresence(self):
        p1, p2 = self.players[0], self.players[1]
        p1.Send({"action": "informPlayerPresence", "opponent": p2.nickname})
        p2.Send({"action": "informPlayerPresence", "opponent": p1.nickname})

    def SendToAll(self, data):
        [p.Send(data) for p in self.players]

    def Launch(self):
        while True:
            self.Pump()
            sleep(0.0001)

# get command line argument of server, port
if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage:", sys.argv[0], "host:port")
        print("e.g.", sys.argv[0], "localhost:31425")
    else:
        host, port = sys.argv[1].split(":")
        s = SudokuServer(localaddr=(host, int(port)))
        s.Launch()
