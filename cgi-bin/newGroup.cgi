#!/usr/local/bin/perl -w
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
use Config::Simple qw(-strict);
use lib ("../site_perl");
use widgets;
use CGI;
use auth;
use Group;
our $C = CGI->new;
our $config = Config::Simple->new("../etc/annie.conf");
our $scriptdir = $config->param("server.scriptdirectory");
our $serverURL = $config->param("server.url");
our $parentID = $C->param("ParentID") || 0;
our $submit = $C->param("submit") || "";
our $fromLocation = $C->param("FromLocation") || "";
our ($dbh, $authInfo);

$dbh = &widgets::dbConnect($config);
$authInfo = &auth::authenticated($dbh,\$C);
our $template = Template->new( RELATIVE => 1,
			      INCLUDE_PATH => "../templates");

unless ($authInfo->{LoggedIn}) {
  my $vars = {scriptdir => $scriptdir,
	      randomValue => &auth::randomValue(),
	      formAction => "newGroup.cgi"};
  print $C->header;
  $template->process("loginScriptForm.html",$vars) or die $template->error;
  exit;
}
if ($submit eq "Make a New Group" or $submit eq "Add Child Group") {
  &makeGroup();
  my $redir = $serverURL . $scriptdir;
  $redir .= $fromLocation ? $fromLocation : "manageGroups.cgi";
  $redir .= $parentID ? "?GroupID=$parentID" : "";
  print $C->redirect(-url=>$redir,
			   -cookie=>$authInfo->{cookie});
  exit;
} else {
  my $vars = { scriptdir => $scriptdir,
	       formAction => "newGroup.cgi" };

  print $C->header(-cookie=>$authInfo->{cookie});
  $template->process("newGroup.html",$vars);
  exit;
}
sub makeGroup {
  my $groupName = $C->param("GroupName") || $C->param("name") || "";
  $groupName = &widgets::scrub($groupName);
  unless ($groupName) {
    print $C->redirect($serverURL . $scriptdir . "manageGroups.cgi");
    exit;
  }

  my $g = Group->new( dbh => $dbh);
  $g->setGroupName($groupName);
  $g->setOwnerID($authInfo->{UserID});
  $g->setParentID($parentID);
  $g->setActive("Active");
  $g->setState("Open");
  my $user = User->load( dbh => $dbh,
			 ID => $authInfo->{UserID});
  my $check = 0;
  if ($parentID) {
    my $group = Group->load( dbh => $dbh,
			   GroupID => $parentID);
    if ( ($group->isOwner($user) and 
	 $user->hasPrivilege("Own.AddChildGroup"))
	or 
	$user->hasPrivilege("Other.AddChildGroup")) {
      $check = 1;
    }
  } else {
    if ($user->hasPrivilege("Own.AddParentGroup") or 
	$user->hasPrivilege("Other.AddParentGroup")) {
      $check = 1;
    }
  }
  if ($check) {
    $g->save;
    my $gid = $g->getID;
    my $groupId;
    ($groupId = $groupName) =~ s/[^\w]/_/g;
    $groupId .= "_$gid";
    ($groupId = "No Name" . rand(10000)) unless $groupId;
    $g->setGroupID($groupId);
    $g->update;
  }

}
