-- MySQL dump 9.07
--
-- Host: localhost    Database: annie
---------------------------------------------------------
-- Server version	4.0.4-beta

--
-- Table structure for table 'EvalVectorValueNames'
--

DROP TABLE IF EXISTS EvalVectorValueNames;
CREATE TABLE EvalVectorValueNames (
  EvalVectorID bigint(20) unsigned NOT NULL default '0',
  Value int(11) NOT NULL default '0',
  Name varchar(80) default NULL,
  PRIMARY KEY  (EvalVectorID,Value)
) TYPE=MyISAM;

