-- Copyright 2003, Buzzmaven Co.
-- This file is part of Annotateit.

-- Annotateit is free software; you can redistribute it and/or modify
-- it under the terms of the GNU General Public License as published by
-- the Free Software Foundation; either version 2 of the License, or
-- (at your option) any later version.

-- Annotateit is distributed in the hope that it will be useful,
-- but WITHOUT ANY WARRANTY; without even the implied warranty of
-- MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
-- GNU General Public License for more details.

-- You should have received a copy of the GNU General Public License
-- along with Annotateit (see GNU-GPL.txt); if not, write to the Free Software
-- Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA.
-- The GNU General Public License may also be found on the Web at:
--   http://www.gnu.org/licenses/gpl.txt

--
---- MySQL dump 8.23
--
-- Host: localhost    Database: annotateit_com
---------------------------------------------------------
-- Server version	3.23.58

--
-- Table structure for table `AnnotationRequest`
--

DROP TABLE IF EXISTS AnnotationRequest;
CREATE TABLE AnnotationRequest (
  ID bigint(20) unsigned NOT NULL auto_increment,
  RemoteAddress varchar(30) default NULL,
  RequestURI varchar(255) default NULL,
  RequestURIDirectory varchar(255) default NULL,
  Timestamp timestamp(14) NOT NULL,
  PRIMARY KEY  (ID)
) TYPE=MyISAM;

/*!40000 ALTER TABLE `AnnotationRequest` DISABLE KEYS */;

--
-- Table structure for table `Assignment`
--

DROP TABLE IF EXISTS Assignment;
CREATE TABLE Assignment (
  ID int(10) unsigned NOT NULL auto_increment,
  GroupID varchar(255) default NULL,
  UserID int(10) unsigned default NULL,
  Title varchar(255) default NULL,
  Description text,
  DueDate date default NULL,
  Deleted char(1) default '0',
  Weight int(11) default NULL,
  PRIMARY KEY  (ID)
) TYPE=MyISAM;

/*!40000 ALTER TABLE `Assignment` DISABLE KEYS */;

--
-- Table structure for table `Clickthrough`
--

DROP TABLE IF EXISTS Clickthrough;
CREATE TABLE Clickthrough (
  ID int(10) unsigned NOT NULL auto_increment,
  UserID int(10) unsigned default NULL,
  AnnotationID int(10) unsigned default NULL,
  PRIMARY KEY  (ID)
) TYPE=MyISAM;

/*!40000 ALTER TABLE `Clickthrough` DISABLE KEYS */;

--
-- Table structure for table `Comment`
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

/*!40000 ALTER TABLE `Comment` DISABLE KEYS */;

--
-- Table structure for table `CommunityAnnotation`
--

DROP TABLE IF EXISTS CommunityAnnotation;
CREATE TABLE CommunityAnnotation (
  ID int(10) unsigned NOT NULL auto_increment,
  Title varchar(80) default NULL,
  Category varchar(40) default NULL,
  Description text,
  PRIMARY KEY  (ID)
) TYPE=MyISAM;

/*!40000 ALTER TABLE `CommunityAnnotation` DISABLE KEYS */;

--
-- Table structure for table `CustomAnnotation`
--

DROP TABLE IF EXISTS CustomAnnotation;
CREATE TABLE CustomAnnotation (
  ID int(10) unsigned NOT NULL auto_increment,
  UserID int(10) unsigned default NULL,
  label varchar(255) default NULL,
  value text,
  PRIMARY KEY  (ID)
) TYPE=MyISAM;

/*!40000 ALTER TABLE `CustomAnnotation` DISABLE KEYS */;

--
-- Table structure for table `Document`
--

DROP TABLE IF EXISTS Document;
CREATE TABLE Document (
  ObjectID bigint(20) unsigned NOT NULL default '0',
  UploadDate datetime default NULL,
  Type varchar(30) default NULL,
  AssignmentID int(11) default NULL,
  Filename varchar(20) default NULL,
  OwnerID int(10) unsigned default NULL,
  Security enum('Private','Group','Public') default NULL,
  State enum('Rough Draft','Final Draft') default NULL,
  PRIMARY KEY  (ObjectID)
) TYPE=MyISAM;

/*!40000 ALTER TABLE `Document` DISABLE KEYS */;

--
-- Table structure for table `DocumentAccess`
--

DROP TABLE IF EXISTS DocumentAccess;
CREATE TABLE DocumentAccess (
  GroupID varchar(150) NOT NULL default '',
  DocumentID int(10) unsigned NOT NULL default '0',
  PRIMARY KEY  (GroupID,DocumentID)
) TYPE=MyISAM;

/*!40000 ALTER TABLE `DocumentAccess` DISABLE KEYS */;

--
-- Table structure for table `EvalVectorDesc`
--

DROP TABLE IF EXISTS EvalVectorDesc;
CREATE TABLE EvalVectorDesc (
  ObjectID bigint(20) unsigned NOT NULL default '0',
  MinimumValue int(10) unsigned default NULL,
  MaximumValue int(10) unsigned default NULL,
  Increment int(11) default NULL,
  Type enum('Select','Radio','Box') default NULL,
  OwnerID int(10) unsigned default NULL,
  PRIMARY KEY  (ObjectID)
) TYPE=MyISAM;

/*!40000 ALTER TABLE `EvalVectorDesc` DISABLE KEYS */;

--
-- Table structure for table `EvalVectorValueNames`
--

DROP TABLE IF EXISTS EvalVectorValueNames;
CREATE TABLE EvalVectorValueNames (
  EvalVectorID bigint(20) unsigned NOT NULL default '0',
  Value int(11) NOT NULL default '0',
  Name varchar(80) default NULL,
  PRIMARY KEY  (EvalVectorID,Value)
) TYPE=MyISAM;

/*!40000 ALTER TABLE `EvalVectorValueNames` DISABLE KEYS */;

--
-- Table structure for table `Evaluation`
--

DROP TABLE IF EXISTS Evaluation;
CREATE TABLE Evaluation (
  ObjectID bigint(20) unsigned NOT NULL default '0',
  EvalVectorID bigint(20) unsigned NOT NULL default '0',
  Value int(11) default NULL,
  OwnerID int(10) unsigned NOT NULL default '0',
  GroupID varchar(80) default NULL,
  ObjectClass varchar(40) NOT NULL default '',
  Weight int(11) default NULL,
  PRIMARY KEY  (ObjectID,EvalVectorID,OwnerID)
) TYPE=MyISAM;

/*!40000 ALTER TABLE `Evaluation` DISABLE KEYS */;

--
-- Table structure for table `Exclude`
--

DROP TABLE IF EXISTS Exclude;
CREATE TABLE Exclude (
  URL varchar(250) NOT NULL default '',
  OwnerEmail varchar(80) NOT NULL default '',
  RobotsFile varchar(255) NOT NULL default '',
  KEY URL (URL,OwnerEmail)
) TYPE=MyISAM;

/*!40000 ALTER TABLE `Exclude` DISABLE KEYS */;

--
-- Table structure for table `GroupDefs`
--

DROP TABLE IF EXISTS GroupDefs;
CREATE TABLE GroupDefs (
  ID int(10) unsigned NOT NULL auto_increment,
  GroupName varchar(255) default NULL,
  GroupID varchar(40) default NULL,
  OwnerID int(10) unsigned NOT NULL default '0',
  ParentID varchar(255) default NULL,
  Type varchar(20) default NULL,
  State varchar(8) default 'Open',
  Active enum('Active','Inactive') default 'Active',
  PRIMARY KEY  (ID)
) TYPE=MyISAM;

/*!40000 ALTER TABLE `GroupDefs` DISABLE KEYS */;

--
-- Table structure for table `GroupMember`
--

DROP TABLE IF EXISTS GroupMember;
CREATE TABLE GroupMember (
  ID int(10) unsigned NOT NULL auto_increment,
  MemberID int(10) unsigned NOT NULL default '0',
  GroupID varchar(40) default NULL,
  PRIMARY KEY  (ID)
) TYPE=MyISAM;

/*!40000 ALTER TABLE `GroupMember` DISABLE KEYS */;

--
-- Table structure for table `License`
--

DROP TABLE IF EXISTS License;
CREATE TABLE License (
  ID int(10) unsigned NOT NULL auto_increment,
  Type varchar(20) default NULL,
  ActivationCode varchar(25) default NULL,
  PRIMARY KEY  (ID)
) TYPE=MyISAM;

/*!40000 ALTER TABLE `License` DISABLE KEYS */;

--
-- Table structure for table `ObjectDescription`
--

DROP TABLE IF EXISTS ObjectDescription;
CREATE TABLE ObjectDescription (
  ID bigint(20) unsigned NOT NULL auto_increment,
  ObjectClass varchar(40) NOT NULL default '',
  Title varchar(255) default NULL,
  OwnerID int(10) unsigned default NULL,
  PRIMARY KEY  (ID,ObjectClass)
) TYPE=MyISAM;

/*!40000 ALTER TABLE `ObjectDescription` DISABLE KEYS */;

--
-- Table structure for table `ObjectMap`
--

DROP TABLE IF EXISTS ObjectMap;
CREATE TABLE ObjectMap (
  FromObjectID bigint(20) unsigned NOT NULL default '0',
  FromObjectClass varchar(40) NOT NULL default '',
  ToObjectID bigint(20) unsigned NOT NULL default '0',
  ToObjectClass varchar(40) NOT NULL default '',
  VectorWeight int(11) default NULL,
  OwnerID int(10) unsigned default NULL,
  PRIMARY KEY  (FromObjectID,ToObjectID)
) TYPE=MyISAM;

/*!40000 ALTER TABLE `ObjectMap` DISABLE KEYS */;

--
-- Table structure for table `Outbox`
--

DROP TABLE IF EXISTS Outbox;
CREATE TABLE Outbox (
  DocumentID int(10) unsigned NOT NULL default '0',
  UserID int(10) unsigned NOT NULL default '0',
  PRIMARY KEY  (DocumentID,UserID)
) TYPE=MyISAM;

/*!40000 ALTER TABLE `Outbox` DISABLE KEYS */;

--
-- Table structure for table `Rubric`
--

DROP TABLE IF EXISTS Rubric;
CREATE TABLE Rubric (
  ID bigint(20) unsigned NOT NULL default '0',
  Type varchar(9) default NULL,
  PRIMARY KEY  (ID)
) TYPE=MyISAM;

/*!40000 ALTER TABLE `Rubric` DISABLE KEYS */;

--
-- Table structure for table `annotation`
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
  PRIMARY KEY  (ID)
) TYPE=MyISAM;

/*!40000 ALTER TABLE `annotation` DISABLE KEYS */;

--
-- Table structure for table `user`
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
  NoteType varchar(20) default 'FulltextBefore',
  LastName varchar(40) default NULL,
  FirstName varchar(40) default NULL,
  School varchar(250) default NULL,
  PRIMARY KEY  (ID)
) TYPE=MyISAM;

/*!40000 ALTER TABLE `user` DISABLE KEYS */;

