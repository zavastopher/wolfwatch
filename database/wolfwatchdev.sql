UNLOCK TABLES;
CREATE DATABASE IF NOT EXISTS wolfwatch;
USE wolfwatch;

# Allows for tables to be dropped in any order as the schema is being regenerated
SET FOREIGN_KEY_CHECKS=0;

#
# Table structure for table frequency
#

DROP TABLE IF EXISTS scanResult;
DROP TABLE IF EXISTS keyPhrase;
DROP TABLE IF EXISTS assignment;
DROP TABLE IF EXISTS instructor;
DROP TABLE IF EXISTS frequency;

CREATE TABLE frequency (
	frequencyId int NOT NULL AUTO_INCREMENT,
    term VARCHAR(120),
    PRIMARY KEY (frequencyId)
);

# Frequency data dump
LOCK TABLES frequency WRITE;
INSERT INTO frequency(term) VALUES ("MONTHLY");
INSERT INTO frequency(term) VALUES ("WEEKLY");
INSERT INTO frequency(term) VALUES ("DAILY");
UNLOCK TABLES;

#
# Table structure for instructor
#

CREATE TABLE instructor (
	instructorId int NOT NULL AUTO_INCREMENT,
    lastName VARCHAR(120),
    firstName VARCHAR(120),
    email VARCHAR(120),
    userPassword VARCHAR(120),
    passwordSalt VARCHAR(120),
    frequencyId INT,
    created DATETIME DEFAULT NOW(),
    lastLogin DATETIME DEFAULT NULL,
    verified BOOLEAN DEFAULT 1,
    PRIMARY KEY (instructorId),
    KEY FK_frequencyId (frequencyId),
    CONSTRAINT FK_frequencyId FOREIGN KEY (frequencyId)
    REFERENCES frequency (frequencyId)
    ON UPDATE CASCADE
    ON DELETE CASCADE
);

# Lock tables to ensure data dump is successful
LOCK TABLES instructor WRITE;
INSERT INTO instructor(lastName, firstName, email, userPassword, passwordSalt, frequencyId) VALUES ("Test", "Test", "test@test.com", "311107cebf23e06ba1eefb0b252b2df0645ce5607000e1ccfae08c6f53744d84", "TXnWyGeLkVnjrzdjpSsTLUnJJpUVSoyynMHCGCOIxisNVVKRPcfedKwIyAheXsMTXkAodVjWXtGKfmdmfREGSIhiwjGDoeSydqGQWHXjbnNexEEpYotQboSQ", 0);
UNLOCK TABLES;

#
# Table structure for table assignment
#

CREATE TABLE assignment (
	assignmentId int NOT NULL AUTO_INCREMENT,
    assignmentActive BOOLEAN,
    dueDate DATETIME,
    contents LONGTEXT,
    courseName VARCHAR(120),
    title VARCHAR(120),
    lastNotificationCheck DATETIME,
    instructorId INT,
    PRIMARY KEY (assignmentId),
    KEY FK_instructorId (instructorId),
    CONSTRAINT FK_instructorId FOREIGN KEY (instructorId)
    REFERENCES instructor (instructorId)
    ON UPDATE CASCADE
    ON DELETE CASCADE
);

# Assignment Dummy Data dump
LOCK TABLES assignment WRITE;
INSERT INTO assignment(assignmentActive, dueDate, contents, courseName, title, lastNotificationCheck, instructorId) VALUES (FALSE, NOW(), "Some Dummy Text", "DummyCourseName", "DummyTitle", NOW(), 1);
UNLOCK TABLES;

#
# Table structure for table keyPhrase
#

CREATE TABLE keyPhrase (
	keyPhraseId int NOT NULL AUTO_INCREMENT,
    keyPhraseText LONGTEXT,
    assignmentId INT,
    PRIMARY KEY (keyPhraseId),
    KEY FK_assignmentId (assignmentId),
    CONSTRAINT FK_assigmentId FOREIGN KEY (assignmentId)
    REFERENCES assignment (assignmentId)
    ON UPDATE CASCADE
    ON DELETE CASCADE
);

# Assignment Rule Dummy Data Dump
LOCK TABLES keyPhrase WRITE;
INSERT INTO keyPhrase(keyPhraseText, assignmentId) VALUES ("Hello World", 1);
UNLOCK TABLES;

#
# Table structure for table scanResult
#

CREATE TABLE scanResult (
	scanId int NOT NULL AUTO_INCREMENT,
    confidenceProbability FLOAT,
    url LONGTEXT,
    assignmentId INT,
    scantime DATETIME DEFAULT NOW(),
    PRIMARY KEY (scanId),
    KEY FK_assignmentId (assignmentId),
    CONSTRAINT FK_assignmentId FOREIGN KEY (assignmentId)
    REFERENCES assignment (assignmentId)
    ON UPDATE CASCADE
    ON DELETE CASCADE
);

# scanResult Dummy Data Dump
LOCK TABLES scanResult WRITE;
INSERT INTO scanResult(confidenceProbability, url, assignmentId) VALUES (42.069, 'a/dummy.url', 1);
UNLOCK TABLES;


SET FOREIGN_KEY_CHECKS=1;

# Trigger for preventing duplicate scan results on add
DROP TRIGGER IF EXISTS scanResultPreventDuplicate;
DELIMITER $$
CREATE TRIGGER scanResultPreventDuplicate BEFORE INSERT ON scanResult
FOR EACH ROW
BEGIN
    IF (SELECT COUNT(*) FROM scanResult WHERE url = NEW.url AND assignmentId = NEW.assignmentId) > 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Duplicate scan result';
    END IF;
END$$
DELIMITER ;
