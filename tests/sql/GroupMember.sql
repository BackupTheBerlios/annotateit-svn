-- MySQL dump 9.07
--
-- Host: localhost    Database: annie
---------------------------------------------------------
-- Server version	4.0.4-beta

--
-- Table structure for table 'GroupMember'
--

DROP TABLE IF EXISTS GroupMember;
CREATE TABLE GroupMember (
  ID int(10) unsigned NOT NULL auto_increment,
  MemberID int(10) unsigned NOT NULL default '0',
  GroupID varchar(40) default NULL,
  PRIMARY KEY  (ID)
) TYPE=MyISAM;

--
-- Dumping data for table 'GroupMember'
--

/*!40000 ALTER TABLE GroupMember DISABLE KEYS */;
LOCK TABLES GroupMember WRITE;
INSERT INTO GroupMember VALUES (23,22,'foobar_52'),(22,28,'foobar_52');
UNLOCK TABLES;
/*!40000 ALTER TABLE GroupMember ENABLE KEYS */;

