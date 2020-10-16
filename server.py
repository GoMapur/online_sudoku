import sys
from time import sleep, localtime
from weakref import WeakKeyDictionary

from PodSixNet.Server import Server
from PodSixNet.Channel import Channel

from sudoku_alg import generate_board

class ClientChannel(Channel):
    """
    This is the server representation of a single connected client.
    """
    def __init__(self, nickname, board_state_original, board_state_filled, *args, **kwargs):
        self.nickname = nickname
        self.board_state_original = []
        self.board_state_correct = []
        self.board_state_filled = []
        Channel.__init__(self, *args, **kwargs)

    def Close(self):
        self._server.DelPlayer(self)

    ##################################
    ### Network specific callbacks ###
    ##################################
    def Network_Nickname(self, data):
        self.nickname = data['nickname']
        self._server.InformPlayerPresence()

    def Network_OpponentWin(self, data):
        self._server.SendToOpponent({"action": "OpponentWin"})

    def Network_OpponentLeft(self, data):
        self._server.DelPlayer(self)

    def Network_OpponentMove(self, data):
        self.board_state_filled = data["board_state_filled"]
        self._server.SendToOpponent({"action": "OpponentMove", "board_state_correct": data["board_state_correct"], "board_state_filled": data["board_state_filled"], "board_state_original": data["board_state_original"], "current_selection": data["current_selection"], "selection_color": data["selection_color"]}, self.nickname)

class SudokuServer(Server):
    channelClass = ClientChannel

    def __init__(self, *args, **kwargs):
        Server.__init__(self, *args, **kwargs)
        self.players = WeakKeyDictionary()
        self.initial_board_state = generate_board()
        print('Server launched')

    def Connected(self, channel, addr):
        if len(self.players) == 2:
            return
        self.AddPlayer(channel)

    def AddPlayer(self, player):
        if len(self.players) < 2:
            print("New Player" + str(player.addr))
            self.players[player] = True
            self.InformPlayerPresence()
            print("players", [p for p in self.players])
        if len(self.players) == 2:
            for p in self.players:
                p.Send({"action": "CompetitionInit", "initial_board_state": self.initial_board_state})

    def DelPlayer(self, player):
        print("Deleting Player" + str(player.addr))
        del self.players[player]
        self.InformPlayerLeft()

    def InformPlayerPresence(self):
        p1, p2 = self.players[0], self.players[1]
        p1.Send({"action": "InformPlayerPresence", "opponent": p2.nickname})
        p2.Send({"action": "InformPlayerPresence", "opponent": p1.nickname})

    def InformPlayerLeft(self):
        if len(self.players) == 1:
            self.players[0].Send({"action": "InformPlayerLeft"})

    def SendToOpponent(self, data, nickname):
        opponent = self.reverse_player(nickname)
        if opponent:
            opponent.send(data)

    def reverse_player(self, nickname):
        p1, p2 = self.players[0], self.players[1]
        if nickname == p1.nickname:
            return p2
        elif nickname == p2.nickname:
            return p1
        return None

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
