#!/usr/local/bin/perl -wT
##############################################
## This manages the user's documents
##
# Copyright 2003, Buzzmaven Co.

# This file is part of Annotateit.

# Annotateit is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# Annotateit is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Annotateit (see GNU-GPL.txt); if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA.
# The GNU General Public License may also be found on the Web at:
#   http://www.gnu.org/licenses/gpl.txt

use strict;
use Template;
use Config::Simple qw( -strict );
use lib ("../site_perl");
use widgets;
use auth;
use Document;
use User;
use Group;
use CGI;
our $C = CGI->new;
my $config = Config::Simple->new("../etc/annie.conf");
our ($dbh, $authInfo,$scriptdir,$cgiDir, $docDir, $serverURL,$docURL);
$scriptdir = $config->param("server.scriptdirectory");
$serverURL = $config->param("server.url");
$cgiDir = $serverURL  . $scriptdir;
$docDir = $config->param("server.documentdirectory");
$docURL = $config->param("server.documenturl");
$dbh = &widgets::dbConnect($config);
$authInfo = &auth::authenticated($dbh,\$C);
our $authorID = $C->param("AuthorID") || 0;
$authorID =~ s/[^\d]//g;
our $outboxStatus = $C->param("OutboxStatus");
our $docID = $C->param("DocumentID");
defined ($docID) && $docID =~ s/[^\d]//g;
our $authorLastName = $C->param("AuthorLastName") || "";

our $action = $C->param("action") || "";
our $ID = $C->param("ID") || "";
our $startAt = $C->param("StartAt") || 0;
our $template = Template->new( RELATIVE => 1,
			      INCLUDE_PATH => "../templates" );
our $documentSet = $C->param("DocumentSet") || "Owned";

unless ($authInfo->{LoggedIn}) {
  my $vars = { formAction => "manageDocuments.cgi",
	       scriptdir => $scriptdir,
	       randomValue => &auth::randomValue(),
	     };
  print $C->header;
  $template->process("loginScriptForm.html",$vars) or die $template->error;
  exit;
}

our $user = User->load(dbh => $dbh,
		     ID => $authInfo->{UserID});
our $Documents = [];
our $gmDD = [];
if ($documentSet eq "Owned") {
  $Documents = $user->getDocuments;
} else {
  my $docAccess = DocumentAccess->new( dbh => $dbh);
  if ($documentSet eq "Public" or $documentSet eq "Private") {
    $docAccess->setGroupID($documentSet);
    $docAccess->setUser($user);
  } else {
    my $group = Group->load( dbh => $dbh, GroupID => $documentSet);
    $group->getGroupMembers;
    $gmDD = $group->getGroupMemberDisplayData;
    if ($user->hasGroup($documentSet)) {
      $docAccess->setGroupID($documentSet);
    }
  }
  $docAccess->setOutboxStatus($outboxStatus);
  $docAccess->setAuthorID($authorID);
  $docAccess->setUserID($user->getID);
  $docAccess->setAuthorLastLetter($authorLastName);
  $Documents = $docAccess->getDocumentIDs(UserID => $user->getID);
}
my $vars = {};
my $userID = $user->getID || 0;
for my $docID (@{$Documents}) {
  my $doc = Document->load(dbh => $dbh,
			   ID => $docID);
  push @{$vars->{Documents}}, $doc->getDisplayData(UserID => $userID,
						   Config => $config);
}
$vars->{AuthorLastName} = $authorLastName;
$vars->{StartAt} = $startAt;
$vars->{DocumentSet} = $documentSet;
$vars->{Groups} = $user->getGroupDisplayData;
$vars->{Author} = $gmDD;
$vars->{scriptdir} = $scriptdir;
$vars->{serverURL} = $serverURL;
$vars->{OutboxStatus} = $outboxStatus;
$vars->{User} = ($user->getDisplayData);
print $C->header(-cookie=>$authInfo->{cookie});
$template->process("displayDocuments.html",$vars) || die $template->error;


exit;


