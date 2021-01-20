INSERT INTO Operator(ID,firstName,lastName, dateOfBirth, droneLicense,rescueEndorsement, operations)
VALUES(1, 'John', 'Doe', DATE("1989-06-15"),0, False, 2);

INSERT INTO Operator(ID,firstName,lastName, dateOfBirth, droneLicense,rescueEndorsement, operations)
VALUES(2, 'Jake', 'Smith', DATE("1992-09-20"),1, False, 1);

INSERT INTO Operator(ID,firstName,lastName, dateOfBirth, droneLicense,rescueEndorsement, operations)
VALUES(3, 'Michelle', 'Jones', DATE("1990-07-08"),2, False, 3);


INSERT INTO Operator(ID,firstName,lastName, dateOfBirth, droneLicense,rescueEndorsement, operations)
VALUES(4, 'Carolina', 'Baker', DATE("1988-01-20"),2, False, 4);


INSERT INTO Map(ID, name, fileName)
VALUES(1,'Abel Tasman', 'map_abel_tasman_3.gif');

INSERT INTO Map(ID, name, fileName)
VALUES(2, 'Ruatiti', 'map_ruatiti.gif');


INSERT INTO Drone(ID, name, classType, rescue,mapID)
VALUES(1, 'Drone 1', 1, False, 2);

INSERT INTO Drone(ID, name, classType, rescue,mapID)
VALUES(2, 'Drone 2', 2, False, 1);

INSERT INTO Drone(ID, Name, classType, rescue)
VALUES(3, 'Drone 3', 1, True);

INSERT INTO Drone(ID, Name, classType, rescue, operatorID, mapID)
VALUES(4, 'Drone 4', 1, False, 2, 1);


INSERT INTO Drone(ID, Name, classType, rescue, operatorID, mapID)
VALUES(5, 'Drone 5', 2, True, 4, 2);