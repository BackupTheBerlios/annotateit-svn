-- MySQL dump 9.07
--
-- Host: localhost    Database: annie
---------------------------------------------------------
-- Server version	4.0.4-beta

--
-- Table structure for table 'Comment'
--

DROP TABLE IF EXISTS Comment;
CREATE TABLE Comment (
  ID bigint(20) unsigned NOT NULL auto_increment,
  ParentID int(10) unsigned default NULL,
  Comment text,
  Entered timestamp(14) NOT NULL,
  UserID int(10) unsigned default NULL,
  PRIMARY KEY  (ID)
) TYPE=MyISAM;

--
-- Dumping data for table 'Comment'
--

/*!40000 ALTER TABLE Comment DISABLE KEYS */;
LOCK TABLES Comment WRITE;
UNLOCK TABLES;
/*!40000 ALTER TABLE Comment ENABLE KEYS */;

