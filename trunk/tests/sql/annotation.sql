-- MySQL dump 9.07
--
-- Host: localhost    Database: annie
---------------------------------------------------------
-- Server version	4.0.4-beta

--
-- Table structure for table 'annotation'
--

DROP TABLE IF EXISTS annotation;
CREATE TABLE annotation (
  ID int(10) unsigned NOT NULL auto_increment,
  PhraseRE text,
  url varchar(255) default NULL,
  annotation text,
  title varchar(255) default NULL,
  UserID int(10) unsigned default NULL,
  Time timestamp(14) NOT NULL,
  context text,
  type varchar(10) default NULL,
  GroupID varchar(40) default NULL,
  phrase text,
  Anonymous char(3) default 'No',
  Font varchar(40) default NULL,
  Color varchar(40) default NULL,
  Style varchar(40) default NULL,
  PRIMARY KEY  (ID)
) TYPE=MyISAM;

