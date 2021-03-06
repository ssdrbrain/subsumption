import zone
import collections

class PlayerManager:
    """Stores players and keep gids unique."""
    def __init__(self):
        self.players = set()
        self.player_gid = {}

    def new_player(self):
        """Creates a new player with unique gid."""
        for gid in range(0, 2**16):
            if gid not in self.player_gid:
                p = zone.Player(gid)
                self.player_gid[gid] = p
                self.players.add(p)
                return p

    def remove_player(self, player):
        """Removes a player from the list."""
        assert(player in self.players)
        self.players.remove(player)
        del self.player_gid[player.gid]
    
    def __len__(self):
        return self.players.__len__()

    def __iter__(self):
        return self.players.__iter__()

class _ChainedMapping(collections.MutableMapping):
    def __init__(self, parent, key, primary, *args):
        self.parent = parent
        self.key = key
        self.primary = primary
        self.dict = dict()
        for d in reversed(args):
            self.dict.update(d)
        self.dict.update(primary)

    def __len__(self):
        return self.dict.__len__()

    def __iter__(self):
        return self.dict.__iter__()

    def __contains__(self, key):
        return self.dict.__contains__(key)

    def __getitem__(self, key):
        return self.dict.__getitem__(key)

    def __setitem__(self, key, value):
        return self.primary.__setitem__(key, value)
    
    def __delitem__(self, key):
        retval = self.primary.__delitem__(key)
        
        #check for empty and notify the parent ZoneMapping
        if not len(self.primary):
            self.parent._empty(self.key)

        return retval

class ZoneMapping:
    def __init__(self):
        self._top_level = {}
        self._realm = {}
        self._arena = {}
        self._game = {}

    def _empty(self, key):
        if isinstance(key, zone.Game):
            del self._game[key]
        elif isinstance(key, zone.Arena):
            del self._arena[key]
        elif isinstance(key, zone.Realm):
            del self._realm[key]
        elif isinstance(key, zone.Zone) or key is None:
            pass # nothing in _top_level to remove
        else:
            raise TypeError("Key not a zone.py type ({})".format(type(key).__name__))

    def __getitem__(self, key):            
        if isinstance(key, zone.Game):
            return _ChainedMapping(self, key,
                                   self._game.setdefault(key, {}),
                                   self._realm.get(key.realm, {}),
                                   self._top_level)
        elif isinstance(key, zone.Arena):
            return _ChainedMapping(self, key,
                                   self._arena.setdefault(key, {}),
                                   self._realm.get(key.realm, {}),
                                   self._top_level)
        elif isinstance(key, zone.Realm):
            return _ChainedMapping(self, key,
                                   self._realm.setdefault(key, {}),
                                   self._top_level)
        elif isinstance(key, zone.Zone) or key is None:
            return _ChainedMapping(self, key, self._top_level)
        else:
            raise TypeError("Key not a zone.py type ({})".format(type(key).__name__))
