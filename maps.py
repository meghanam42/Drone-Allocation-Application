import sqlite3
class Map(object):
    """ Stores details on a map. """

    def __init__(self, name, filepath):
        self.name = name
        self.filepath = filepath

class MapStore(object):
    """ MapStore stores all the maps for DALSys. """

    def __init__(self, conn=None):
        self._maps = {}
        self._conn = conn

    def add(self, map):
        if map.name in self._maps:
            raise Exception('Map already exists in store')
        else:
            self._maps [map.name] = map
        """ Adds a new map to the store. """
        #pass  # TODO

    def remove(self, map):
        if not map.name in self._maps:
            raise Exception('Map does not exist in store')
        else:
            del self._maps[map.name]
        """ Removes a map from the store. """
        #pass  # TODO

    def get(self, name):
        if not name in self._maps:
            return None
        else:
            return self._maps[name]
        """ Retrieves a map from the store by its name. """
        #pass  # TODO

    def list_all(self):
        cursor = self._conn.cursor()
        query = ('SELECT mapName, fileName FROM Map m ORDER BY mapName')
        cursor.execute(query)
        for (name,fileName) in cursor:
            m = Map(name, fileName)
            yield m
        cursor.close()
        """for map in self._maps:
            yield map"""
        """ Lists all the maps in the store. """
        #pass  # TODO

    def save(self):
        cursor = self._connection.cursor()
        """for _map in self.maps:
            query = 'INSERT INTO Map VALUES(ID,name, fileName)(%s,%s,%s)'
            cursor.execute(query, (_map.id, _map.name, _map.filepath))
        cursor.close()"""
        """ Saves the store to the database. """
        pass    # TODO: we don't have a database yet
