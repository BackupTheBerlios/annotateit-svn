-- MySQL dump 9.07
--
-- Host: localhost    Database: annie
---------------------------------------------------------
-- Server version	4.0.4-beta

--
-- Table structure for table 'ObjectMap'
--

DROP TABLE IF EXISTS ObjectMap;
CREATE TABLE ObjectMap (
  FromObjectID bigint(20) unsigned NOT NULL default '0',
  FromObjectClass varchar(40) NOT NULL default '',
  ToObjectID bigint(20) unsigned NOT NULL default '0',
  ToObjectClass varchar(40) NOT NULL default '',
  PRIMARY KEY  (FromObjectID,ToObjectID)
) TYPE=MyISAM;

--
-- Dumping data for table 'ObjectMap'
--

/*!40000 ALTER TABLE ObjectMap DISABLE KEYS */;
LOCK TABLES ObjectMap WRITE;
UNLOCK TABLES;
/*!40000 ALTER TABLE ObjectMap ENABLE KEYS */;

