
class Zone:
    def __init__(self):
        self.realms = set()

class Realm:
    def __init__(self):
        self.arenas = set()
        self.teams = {}

class Arena:
    def __init__(self, realm):
        self.players = set()
        self.realm = realm

class Game:
    def __init__(self, realm):
        self.realm = realm

class Team:
    def __init__(self, arena, freq, players=None):
        self.arena = arena
        self.freq = int(freq)
        if players:
            self.players = set(players)
        else:
            self.players = set()

    def add(self, p):
        if isinstance(p, Player):
            return self.players.add(p)
        else:
            raise TypeError("argument not a player!")

    def remove(self, p):
        return self.players.remove(p)

    def __contains__(self, p):
        return self.players.__contains__(p)
    
    def __iter__(self):
        return self.players.__iter__()
    
    def __len__(self):
        return self.players.__len__()

    def __repr__(self):
        return "Team({}, {}, {})".format(self.arena, self.freq, self.players)

    def __str__(self):
        return "Team on freq {}".format(self.freq)

class Player:
    """Represents a player within the zone."""
    def __init__(self, gid, name=None):
        self.gid = int(gid)
        self.name = name
        self.data = {}

    def __repr__(self):
        return "Player({}, {})".format(self.gid, self.name)
    
    def __str__(self):
        if self.name:
            return self.name
        else:
            return "[gid={}]".format(self.gid)

    def __getitem__(self, key):
        return self.data.__getitem__(key)
    
    def __setitem__(self, key, value):
        return self.data.__setitem__(key, value)
    
    def __delitem__(self, key):
        return self.data.__delitem__(key)
    
    def __contains__(self, key):
        return self.data.__contains__(key)
