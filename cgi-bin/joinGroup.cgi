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
use Config::Simple qw( -strict);
use lib ("../site_perl");
use widgets;
use auth;
use Group;
use CGI;
our $C = CGI->new;

my $config = Config::Simple->new("../etc/annie.conf");
our ($dbh, $authInfo, $scriptdir, $serverURL);
$scriptdir = $config->param("server.scriptdirectory");
$serverURL = $config->param("server.url");
$dbh = &widgets::dbConnect($config);
$authInfo = &auth::authenticated($dbh,\$C);
my $groupID = $C->param("GroupID") || "";
my $template = Template->new (RELATIVE => 1,
			      INCLUDE_PATH => "../templates");
unless ($authInfo->{LoggedIn}) {
  my $vars = {randomValue => &auth::randomValue(),
	      scriptdir => $scriptdir,
	      formAction => "joinGroup.cgi",
	      hiddenVar => [{name=>"GroupID",value=>$groupID}]};
  print $C->header;
  $template->process("loginScriptForm.html",$vars) or die $template->error;
  exit;
}
if ($C->param("submit") eq "Join Group") {
  &joinGroup();
}

print $C->redirect(-url=>$serverURL .$scriptdir . "manageGroups.cgi",
			 -cookie=>$authInfo->{cookie});
exit;

sub joinGroup {

  unless ($groupID) {
    my $vars = {Error => "NoGroupIDPassed",
		scriptdir => $config->param("server.scriptdirectory"),
		serverurl => $config->param("server.url"),
		EnglishError => "You have to specify a group to join.",
		BackPage => "manageGroups.cgi" };
    print $C->header(-cookie=>$authInfo->{cookie});
    $template->process("Error.html",$vars) or die $template->error;
    exit;
  }
  my $group = Group->load(dbh => $dbh,
			  GroupID => $groupID);
  unless ($group->getGroupName) {
    print $C->header(-cookie=>$authInfo->{cookie});
    my $vars = {Error => "NoSuchGroupToJoin",
		scriptdir => $config->param("server.scriptdirectory"),
		serverurl => $config->param("server.url"),
		GroupID => $groupID,
		EnglishError => "Can't find specified group",
		BackPage => "manageGroups.cgi"};
    $template->process("Error.html",$vars) or die $template->error;
    exit;
  }
  my $user = User->load(dbh => $dbh,
			ID => $authInfo->{UserID});
  if ($user->hasGroup($group->getGroupID)) {
    my $vars = { Error => "AlreadyMember",
		 scriptdir => $config->param("server.scriptdirectory"),
		 serverurl => $config->param("server.url"),
		 GroupID => $groupID,
		 EnglishError => "You are already a member!",
		 BackPage => "manageGroups.cgi"};
    print $C->header(-cookie=>$authInfo->{cookie});
    $template->process("Error.html",$vars) or die $template->error;
    exit;
  }
  my $priv = "Own.Join" . $group->getClass . "Group";
  if ($user->hasPrivilege($priv)) {
    unless ($group->addGroupMember($user)) {
      my $vars = { Error => "GroupIsClosed",
		   scriptdir => $config->param("server.scriptdirectory"),
		   serverurl => $config->param("server.url"),
		   GroupID => $groupID,
		   EnglishError => "That group is closed to joining",
		   BackPage => "manageGroups.cgi"};
      print $C->header(-cookie=>$authInfo->{cookie});
      $template->process("Error.html",$vars) or die $template->error;
      exit;
    }
  } else {
    print $C->header(-cookie=> $authInfo->{cookie});
    my $vars = { Error => "NoPrivilegeToJoinGroup",
		 scriptdir => $config->param("server.scriptdirectory"),
		 serverurl => $config->param("server.url"),
		 GroupID => $groupID,
		 EnglishError => "Unauthorized",
		 BackPage => "manageGroups.cgi"};
    $template->process("Error.html",$vars) or die $template->error;
    exit;
  }
}
