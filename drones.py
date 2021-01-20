"""
Name: Meghana Moturu
ID: 938805776
UPI: mmot335
"""
import mysql.connector
import sqlite3
from operators import Operator, OperatorStore
from maps import Map, MapStore
class Drone(object):
    """ Stores details on a drone. """

    def __init__(self, name, class_type=1, rescue=False):
        self.id = 0
        self.name = name
        self.class_type = class_type
        self.rescue = rescue
        self.operator = None
        self.map = None


class DroneAction(object):
    """ A pending action on the DroneStore. """

    def __init__(self, drone, operator, commit_action):
        self.drone = drone
        self.operator = operator
        self.messages = []
        self._commit_action = commit_action
        self._committed = False

    def add_message(self, message):
        """ Adds a message to the action. """
        self.messages.append(message)

    def is_valid(self):
        """ Returns True if the action is valid, False otherwise. """
        return len(self.messages) == 0

    def commit(self):
        """ Commits (performs) this action. """
        if self._committed:
            raise Exception("Action has already been committed")

        self._commit_action(self.drone, self.operator)
        self._committed = True


class DroneStore(object):
    """ DroneStore stores all the drones for DALSys. """

    def __init__(self, conn=None):
        self._drones = {}
        self._last_id = 0
        self._conn = conn
        self._operators = OperatorStore(conn)

    def add(self, drone):
        self._conn.row_factory = sqlite3.Row
        cursor = self._conn.cursor()
        q_id = 'SELECT MAX(ID) as maxx From Drone'
        cursor.execute(q_id)
        result = cursor.fetchone()
        self._last_id = result['maxx']
        self._last_id += 1
        drone.id = self._last_id
        self._drones[drone.id] = drone
        query = 'INSERT INTO Drone(ID, name, classType, rescue) VALUES(?, ?, ?, ?)'
        cursor.execute(query, (drone.id, drone.name, drone.class_type, drone.rescue))
        self._conn.commit()
        cursor.close()
        
        """ Adds a new drone to the store. """
        """if drone.id in self._drones:
            raise Exception('Drone already exists in store')
        else:
            self._last_id += 1
            drone.id = self._last_id
            self._drones[drone.id] = drone"""

    def remove(self, drone):
        """ Removes a drone from the store. """
        self._conn.row_factory = sqlite3.Row
        cursor = self._conn.cursor()
        if drone != None:
            query = 'DELETE FROM Drone WHERE Drone.ID = %?'
            cursor.execute(query, (drone.id,))
            self._conn.commit()
        else:
            print '!! Unknown drone !!'
        cursor.close()


    def get(self, id):
        self._conn.row_factory = sqlite3.Row
        cursor = self._conn.cursor()
        query = 'SELECT Drone.id AS droneID,Drone.name, classType, rescue, o.ID as operatorID, firstName, lastName, m.id as Mid, mapName, fileName FROM Drone LEFT OUTER JOIN Operator o ON Drone.operatorID = o.ID LEFT OUTER JOIN Map m ON Drone.mapID = m.ID WHERE Drone.id = ?'
        cursor.execute(query, (id,))
        results = cursor.fetchone()
        if results is None:
            print "is still none"
            return None
        print results['name']
        d = Drone(results['name'], results['classType'], results['rescue'])
        d.id = results['droneID']
        d.operator = Operator()
        d.operator.id = results['operatorID']
        d.operator.first_name = results['firstName']
        d.operator.last_name = results['lastName']
        if results['Mid']== None:
            d.map = None
        else:
            d.map = Map(results['mapName'], results['fileName'])
        cursor.close()
        return d
    
        
        """ Retrieves a drone from the store by its ID. """
        """if not id in self._drones:
            return None
        else:
            return self._drones[id]"""

    def list_maps(self):
        cursor = self._conn.cursor()
        query = ('SELECT d.ID, d.name, classType, rescue, mapID, mapName, m.fileName FROM Drone d INNER JOIN Map m on d.mapID = m.ID ORDER BY d.name')
        cursor.execute(query)
        for (id, name,classT, rescue, mapId, mapN, fname) in cursor:
            d = Drone(name)
            d.id = id
            d.rescue = rescue
            d.class_type = classT
            d.map = Map(mapN, fname)
            yield d
        cursor.close()
        

    def list_all(self):
        """ Lists all the drones in the system. """
        cursor = self._conn.cursor()
        query = ('SELECT d.ID, name, classType, rescue, d.operatorID, o.id, o.firstName, o.lastName FROM Drone d LEFT OUTER JOIN Operator o on d.operatorID = o.ID ORDER BY name')
        cursor.execute(query)
        for (id, name,classT, rescue, dopid, opid, opfn, opln) in cursor:
            d = Drone(name)
            d.id = id
            d.rescue = rescue
            d.class_type = classT
            if dopid == None:
                o = Operator()
                o.first_name = '<None>'
                o.last_name = ''
                o.id = opid
                d.operator = o
            elif opln == None:
                o = Operator()
                o.first_name = opfn
                o.last_name = ''
                o.id = opid
                d.operator = o
            else:
                o = Operator()
                o.first_name = opfn
                o.last_name = opln
                o.id = opid
                d.operator = o
            yield d
        cursor.close()

    def allocate(self, drone, operator):
        """ Starts the allocation of a drone to an operator. """
        action = DroneAction(drone, operator, self._allocate)
        if drone.operator.first_name != None:
            action.add_message("Drone already allocated to " +str(drone.operator.first_name))
        if operator.drone is not None:
            action.add_message("Operator can only control one drone")
        if operator.drone_license != drone.class_type:
            action.add_message("Operator does not have correct drone license")
        if drone.rescue == True and operator.rescue_endorsement == False:
            action.add_message("Operator does not have rescue endorsement")
        return action

    def _allocate(self, drone, operator):
        """ Performs the actual allocation of the operator to the drone. """
        if operator.drone is not None:
            #operator.drone.operator.id = None
            cursor = self._conn.cursor()
            query = 'UPDATE Drone SET operatorID = Null WHERE ID = ?'
            cursor.execute(query, (operator.drone,))
            query_2 = 'UPDATE Operator SET DroneID = Null WHERE ID = ?'
            cursor.execute(query_2,(operator.id,))
            cursor.close()
            # If the operator had a drone previously, we need to clean it so it does not
            # hold an incorrect reference
        operator.drone = drone
        drone.operator = operator
        self.allocateop(drone)

    def allocateop(self, drone):
        cursor = self._conn.cursor()
        query_2 = 'UPDATE Operator SET droneID = ? WHERE id = ?'
        cursor.execute(query_2, (drone.id, drone.operator.id))
        query = 'UPDATE Drone SET operatorID = ? WHERE id = ?'
        cursor.execute(query, (drone.operator.id, drone.id))
        self._conn.commit()
        cursor.close()
        """ Saves the drone to the database. """
           # TODO: we don't have a database yet

    def save(self, drone):
        cursor = self._conn.cursor()
        dname = drone.name
        dclass = drone.class_type
        dresc = drone.rescue
        query = 'UPDATE Drone SET name = ?, classType = ?, rescue = ? WHERE id = ?'
        cursor.execute(query, (drone.name, drone.class_type, drone.rescue, drone.id))
        self._conn.commit()
        cursor.close()
        
