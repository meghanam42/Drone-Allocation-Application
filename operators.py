"""
Name: Meghana Moturu
ID: 938805776
UPI: mmot335
"""

import mysql.connector
import sqlite3
from datetime import date


class Operator(object):
    """ Stores details on an operator. """

    def __init__(self):
        self.id = 0
        self.first_name = None
        self.family_name = None
        self.date_of_birth = None
        self.drone_license = None
        self.rescue_endorsement = False
        self.operations = 0
        self.drone = None


class OperatorAction(object):
    """ A pending action on the OperatorStore. """

    def __init__(self, operator, commit_action):
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

        self._commit_action(self.operator)
        self._committed = True


class OperatorStore(object):
    """ Stores the operators. """

    def __init__(self, conn=None):
        self._operators = {}
        self._last_id = 0
        self._conn = conn

    def add(self, operator):
        """ Starts adding a new operator to the store. """
        action = OperatorAction(operator, self._add)
        check_age = True
        if operator.first_name is None:
            action.add_message("First name is required")
        if operator.date_of_birth is None:
            action.add_message("Date of birth is required")
            check_age = False
        if operator.drone_license is None:
            action.add_message("Drone license is required")
        if operator.operations < 5 and operator.rescue_endorsement == True:
            action.add_message("To hold a rescue endorsement, the operator has to have been involved in five prior rescue operations.")
        else:
            if check_age and operator.drone_license == 2:
                today = date.today()
                age = today.year - operator.date_of_birth.year - \
                    ((today.month, today.day) < (
                        operator.date_of_birth.month, operator.date_of_birth.day))
                if age < 20:
                    action.add_message(
                        "Operator should be at least twenty to hold a class 2 license")
        return action

    def _add(self, operator):
        """ Adds a new operator to the store. """
        self._conn.row_factory = sqlite3.Row
        cursor = self._conn.cursor()
        q_id = 'SELECT MAX(ID) as maxx From Operator'
        cursor.execute(q_id)
        result = cursor.fetchone()
        self._last_id = result['maxx']
        self._last_id += 1
        operator.id = self._last_id
        self._operators[operator.id] = operator
        query = 'INSERT INTO Operator(ID,firstName,lastName,dateOfBirth, droneLicense, rescueEndorsement, operations, droneID) VALUES(?,?,?,?,?,?,?,?)'
        cursor.execute(query, (operator.id, operator.first_name, operator.last_name, operator.date_of_birth, operator.drone_license, operator.rescue_endorsement, operator.operations, operator.drone))
        self._conn.commit()
        cursor.close()
        
        """if operator.id in self._operators:
            raise Exception('Operator already exists in store')
        else:
            self._last_id += 1
            operator.id = self._last_id
            self._operators[operator.id] = operator"""

    def remove(self, operator):
        """ Removes a operator from the store. """
        if not operator.id in self._operators:
            raise Exception('Operator does not exist in store')
        else:
            del self._operators[operator.id]

    def get(self, id = None, first_n = None, last_n = None):
        self._conn.row_factory = sqlite3.Row
        cursor = self._conn.cursor()
        if id is None:
            if first_n is not None and last_n is not None:
                query = 'SELECT Operator.id AS opID,firstName, lastName, droneLicense, rescueEndorsement, operations, droneID, Drone.ID as drid FROM Operator LEFT OUTER JOIN Drone ON Drone.operatorID = Operator.ID WHERE lower(firstName) = lower(?) AND lower(lastName) = lower(?)'
                cursor.execute(query,(first_n,last_n))
                results = cursor.fetchone()
                if results is None:
                    return None
                o = Operator()
                o.id = results['opID']
                o.first_name = results['firstName']
                o.last_name = results['lastName']
                o.drone_license = results['droneLicense']
                o.rescue_endorsement = results['rescueEndorsement']
                o.operations = results['operations']
                o.drone = results['drid']
                return o
                cursor.close()
            elif first_n is not None and last_n is None:
                self._conn.row_factory = sqlite3.Row
                cursor = self._conn.cursor()
                print 'here'
                query = 'SELECT Operator.id AS opID,firstName, lastName, droneLicense, rescueEndorsement, operations, droneID, Drone.ID as drid FROM Operator LEFT OUTER JOIN Drone ON Drone.operatorID = Operator.ID WHERE lower(firstName) = lower(?)'
                cursor.execute(query,(first_n,))
                results = cursor.fetchone()
                if results['opID'] is None and results is None:
                    return None
                o = Operator()
                o.id = results['opID']
                o.first_name = results['firstName']
                o.last_name = results['lastName']
                o.drone_license = results['droneLicense']
                o.rescue_endorsement = results['rescueEndorsement']
                o.operations = results['operations']
                o.drone = results['drid']
                return o
                
        elif id is not None:
            query = 'SELECT Operator.id AS opID,firstName, lastName, droneLicense, rescueEndorsement, operations, droneID, Drone.ID as drid FROM Operator LEFT OUTER JOIN Drone ON Drone.operatorID = Operator.ID WHERE Operator.id = ?'
            cursor.execute(query,(id,))
            results = cursor.fetchone()
            if results is None:
                return None
            o = Operator()
            o.id = results['opID']
            o.first_name = results['firstName']
            o.last_name = results['lastName']
            o.drone_license = results['droneLicense']
            o.rescue_endorsement = results['rescueEndorsement']
            o.operations = results['operations']
            o.drone = results['drid']
            return o
        cursor.close()
        """ Retrieves a operator from the store by its ID or name. """
        """if isinstance(id, basestring):
            for op in self._operators:
                if (op.first_name + ' ' + op.family_name) == id:
                    return op
            return None
        else:
            if not id in self._operators:
                return None
            else:
                return self._operators[id]"""

    def list_all(self):
        """ Lists all the _operators in the system. """
        cursor = self._conn.cursor()
        query = ('SELECT o.ID, firstName, lastName, droneLicense, rescueEndorsement, operations, d.id as DroneID, name FROM Operator o LEFT OUTER JOIN Drone d on o.ID = d.operatorID ORDER BY firstName, lastName')
        cursor.execute(query)
        for (opid, opfn, opln, droneLicense, rescueEndo, operations, droneID, drname) in cursor:
            o = Operator()
            o.first_name = opfn
            o.last_name = opln
            o.id = opid
            o.operations = operations
            o.rescue_endorsement = False if rescueEndo == 0 else True
            o.drone_license = droneLicense
            if droneID == None:
                o.drone = '<None>'
            else:
                o.drone = str(droneID) + ': ' + drname
            yield o
        cursor.close()

    def save(self, operator):
        """ Saves the store to the database. """
        cursor = self._conn.cursor()
        query = 'UPDATE Operator SET firstName = ?, lastName = ?, droneLicense = ?, rescueEndorsement = ?, operations = ? WHERE id = ?'
        cursor.execute(query, (operator.first_name, operator.last_name, operator.drone_license, operator.rescue_endorsement, operator.operations, operator.id))
        self._conn.commit()
        cursor.close()
        #pass    # TODO: we don't have a database yet
