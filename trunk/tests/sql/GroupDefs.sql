-- MySQL dump 9.07
--
-- Host: localhost    Database: annie
---------------------------------------------------------
-- Server version	4.0.4-beta

--
-- Table structure for table 'GroupDefs'
--

DROP TABLE IF EXISTS GroupDefs;
CREATE TABLE GroupDefs (
  ID int(10) unsigned NOT NULL auto_increment,
  GroupName varchar(255) default NULL,
  GroupID varchar(255) default NULL,
  OwnerID int(10) unsigned NOT NULL default '0',
  ParentID varchar(255) default NULL,
  Type varchar(20) default NULL,
  State varchar(8) default 'Open',
  Active enum('Active','Inactive') NOT NULL default 'Active',
  PRIMARY KEY  (ID)
) TYPE=MyISAM;

--
-- Dumping data for table 'GroupDefs'
--

/*!40000 ALTER TABLE GroupDefs DISABLE KEYS */;
LOCK TABLES GroupDefs WRITE;
INSERT INTO GroupDefs VALUES (52,'foobar','foobar_52',22,'0','Parent','Open','Inactive');
UNLOCK TABLES;
/*!40000 ALTER TABLE GroupDefs ENABLE KEYS */;

