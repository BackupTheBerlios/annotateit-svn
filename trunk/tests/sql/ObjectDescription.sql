-- MySQL dump 9.07
--
-- Host: localhost    Database: annie
---------------------------------------------------------
-- Server version	4.0.4-beta

--
-- Table structure for table 'ObjectDescription'
--

DROP TABLE IF EXISTS ObjectDescription;
CREATE TABLE ObjectDescription (
  ID bigint(20) unsigned NOT NULL auto_increment,
  ObjectClass varchar(40) NOT NULL default '',
  Title varchar(255) default NULL,
  OwnerID int unsigned default NULL,
  PRIMARY KEY  (ID,ObjectClass)
) TYPE=MyISAM;

