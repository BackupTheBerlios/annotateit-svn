-- MySQL dump 9.07
--
-- Host: localhost    Database: annie
---------------------------------------------------------
-- Server version	4.0.4-beta

--
-- Table structure for table 'Clickthrough'
--

DROP TABLE IF EXISTS Clickthrough;
CREATE TABLE Clickthrough (
  ID bigint(20) unsigned NOT NULL auto_increment,
  UserID int(10) unsigned default NULL,
  AnnotationID int(10) unsigned default NULL,
  PRIMARY KEY  (ID)
) TYPE=MyISAM;

--
-- Dumping data for table 'Clickthrough'
--

/*!40000 ALTER TABLE Clickthrough DISABLE KEYS */;
LOCK TABLES Clickthrough WRITE;
INSERT INTO Clickthrough VALUES (1,14,76),(2,14,76),(3,14,74),(4,18,74),(5,18,76),(6,10,76),(7,14,76),(8,14,76),(9,14,76),(10,14,76),(11,14,76),(12,14,76),(13,14,76),(14,14,76),(15,14,76),(16,14,76),(17,14,76),(18,14,76),(19,14,76),(20,14,115),(21,14,115),(22,14,43),(23,14,38),(24,14,43),(25,14,74),(26,22,119),(27,22,119),(28,22,119),(29,22,120),(30,22,125),(31,22,122),(32,22,121),(33,22,124),(34,22,123),(35,22,126),(36,22,127),(37,22,127),(38,22,128),(39,22,129),(40,22,130),(41,22,131),(42,22,132),(43,22,133),(44,22,134),(45,22,135),(46,22,136),(47,22,137);
UNLOCK TABLES;
/*!40000 ALTER TABLE Clickthrough ENABLE KEYS */;

