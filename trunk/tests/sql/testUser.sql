-- MySQL dump 9.07
--
-- Host: localhost    Database: annie
---------------------------------------------------------
-- Server version	4.0.4-beta

--
-- Table structure for table 'user'
--

DROP TABLE IF EXISTS user;
CREATE TABLE user (
  ID int(10) unsigned NOT NULL auto_increment,
  email varchar(255) default NULL,
  name varchar(255) default NULL,
  password varchar(255) default NULL,
  AccessLevel int(10) unsigned default '1',
  DateRegistered datetime default NULL,
  DatePaid datetime default NULL,
  AccessKey varchar(255) default NULL,
  Status varchar(20) default 'Free',
  AutoReload char(3) default 'Yes',
  NoteType varchar(20) default 'FulltextAfter',
  LastName varchar(40) default NULL,
  FirstName varchar(40) default NULL,
  School varchar(250) default NULL,
  PRIMARY KEY  (ID)
) TYPE=MyISAM;

--
-- Dumping data for table 'user'
--

/*!40000 ALTER TABLE user DISABLE KEYS */;
LOCK TABLES user WRITE;
INSERT INTO user VALUES (1,'jnerad@bellsouth.net','Jack Nerad','bourque',64,'2003-02-07 12:57:08','2003-01-01 00:00:00','334433','Staff','Yes','FulltextAfter','Nerad','Jack','Georgia State University');
UNLOCK TABLES;
/*!40000 ALTER TABLE user ENABLE KEYS */;

