CREATE TABLE Drone(
    ID INT PRIMARY KEY NOT NULL,
    name VARCHAR(100) NOT NULL,
    classType INT NOT NULL,
    rescue BOOL NOT NULL,
    operatorID INT NULL,
    mapID INT NULL,
    FOREIGN KEY(operatorID) REFERENCES Operator(ID),
    FOREIGN KEY(mapID) REFERENCES Map(ID)
);

CREATE TABLE Operator(
    ID INT PRIMARY KEY NOT NULL,
    firstName VARCHAR(100) NOT NULL,
    lastName VARCHAR(100) NULL,
    dateOfBirth DATE NULL,
    droneLicense INT DEFAULT 0,
    rescueEndorsement BOOL,
    operations INT NULL,
    droneID INT NULL,
    FOREIGN KEY(droneID) REFERENCES Drone(ID)
);

CREATE TABLE Map(
    ID INT PRIMARY KEY NOT NULL,
    name VARCHAR(100) NOT NULL,
    fileName VARCHAR(100) NOT NULL,
    droneID INT NULL,
    FOREIGN KEY(droneID) REFERENCES Drone(ID)
);