-- MySQL dump 9.07
--
-- Host: localhost    Database: annie
---------------------------------------------------------
-- Server version	4.0.4-beta

--
-- Table structure for table 'EvalVectorDesc'
--

DROP TABLE IF EXISTS EvalVectorDesc;
CREATE TABLE EvalVectorDesc (
  ObjectID bigint(20) unsigned NOT NULL default '0',
  MinimumValue int(10) unsigned default NULL,
  MaximumValue int(10) unsigned default NULL,
  Increment int(11) default NULL,
  Title varchar(80) default NULL,
  Type enum('Select','Radio','Box') default NULL,
  OwnerID int(10) unsigned default NULL,
  PRIMARY KEY  (ObjectID)
) TYPE=MyISAM;

