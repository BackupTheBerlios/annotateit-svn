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
use Config::Simple qw( -strict );
use lib ("../site_perl");
use widgets;
use auth;
use Group;
use User;
use Data::Dumper;
use CGI;
our $C = CGI->new;
my $config = Config::Simple->new("../etc/annie.conf");
our ($dbh, $authInfo, $scriptdir, $serverurl);
$scriptdir = $config->param("server.scriptdirectory");
$serverurl = $config->param("server.url");
$dbh = &widgets::dbConnect($config);
$authInfo = &auth::authenticated($dbh,\$C);
my $groupID = $C->param("GroupID") || "";
my $action = $C->param("action") || "";
my $template = Template->new( RELATIVE => 1,
			      INCLUDE_PATH => "../templates");
unless ($authInfo->{LoggedIn}) {
  my $vars = {scriptdir => $scriptdir,
	      randomValue => &auth::randomValue(),
	      formAction => "viewGroupDetails.cgi",
	      hiddenVar => [{name=>"GroupID",value=>$groupID},
			    {name=>"action", value=>$action}]};
  print $C->header;
  $template->process("loginScriptForm.html",$vars);
  exit;
}

unless ($groupID) {
  print $C->redirect(-url => "$serverurl$scriptdir" . "manageGroups.cgi",
			   -cookie => $authInfo->{cookie});
  exit;
}
if ($action eq "AddGroupMembers") {
  my $owner = User->load(dbh => $dbh,
			 ID => $authInfo->{UserID});
  my @NewUserIDs = $C->param("NewUserID");
  my @NewGroupIDs = $C->param("NewGroupID");
  for my $GroupID (@NewGroupIDs) {
    my $group = Group->load(dbh => $dbh,
			    GroupID => $GroupID);
    if ($owner->hasPrivilege("Other.AddUserToGroup") or
	($group->isOwner($owner) and
	 $owner->hasPrivilege("Own.AddUserToGroup")
	)
       ){
      for my $ID (@NewUserIDs) {
	my $user = User->load(dbh => $dbh,
			      ID => $ID);
	$group->addGroupMember($user);
      }
    }
  }
} elsif ($action eq "DeleteGroupMember") {
  my $UserID = $C->param("UserID");
  my $group = Group->load(dbh => $dbh,
			  GroupID => $groupID);
  my $owner = User->load( dbh => $dbh,
			  ID => $authInfo->{UserID});
  if ($owner->hasPrivilege("Other.DeleteUserFromGroup") or
      ($group->isOwner($owner) 
       and $owner->hasPrivilege("Own.DeleteUserFromGroup"))) {
    my $user = User->load(dbh => $dbh,
			  ID => $UserID);
    $group->deleteGroupMember($user);
  }
} elsif ($action eq "Closed" or $action eq "Open") {
  my $group = Group->load(dbh => $dbh,
			  GroupID => $groupID);
  my $owner = User->load( dbh => $dbh,
			  ID => $authInfo->{UserID});
  if ($owner->hasPrivilege("Other.CloseGroup") or
      ($group->isOwner($owner)
       and $owner->hasPrivilege("Own.CloseGroup"))) {
    $group->setState($action);
    $group->update;
  }
} elsif ($action eq "Activate" or $action eq "Deactivate") {
  my %active = ( Activate => "Active",
		 Deactivate => "Inactive" );
  my $group = Group->load(dbh => $dbh,
			 GroupID => $groupID);
  my $owner = User->load( dbh => $dbh,
			  ID => $authInfo->{UserID});
  if ($owner->hasPrivilege("Other.CloseGroup") or
      ($group->isOwner($owner)
       and $owner->hasPrivilege("Own.CloseGroup"))) {
    $group->setActive($active{$action});
    $group->update;
  }
}

my $group = Group->load(dbh => $dbh,
			GroupID => $groupID);



my $user = User->load(dbh => $dbh,
		      ID => $authInfo->{UserID});
my $gmDD = [];
my $parentAssignments = [];
if ($group->getClass eq "Parent") {
  my $groupMembers = $group->getGroupMembers;
  for my $member (@{$groupMembers}) {
    my $groups = $member->getGroupDisplayData;
    my $dd = $member->getDisplayData;
    $dd->{Groups} = $groups;
    push @{$gmDD}, $dd;
  }
} else {
  $gmDD = $group->getGroupMemberDisplayData;
  my $g2 = Group->load( dbh => $dbh,
			GroupID => $group->getParentID );
  $parentAssignments = $g2->getAssignmentsDisplayData
}
my $vars = {};

my $deleteFromGroup = 0;
if (($group->isOwner($user) and $user->hasPrivilege("Own.DeleteUserFromGroup")) or
    $user->hasPrivilege("Other.DeleteUserFromGroup")) {
  $deleteFromGroup = 1;
}
my $viewChildGroups = 0;
if (($group->isOwner($user) and $user->hasPrivilege("Own.ViewChildGroups")) or
    $user->hasPrivilege("Other.ViewChildGroups")) {
  $viewChildGroups = 1;
}
$vars = {User  => $user->getDisplayData,
	 Group => $group->getDisplayData($user),
	 
	 AnnotatedURLs => $group->getAnnotatedURLs({CurrentUser => $user}),
	 UserEvals => $group->getDocumentEvalTable,
	 ThisGroupsAssignments => $group->getAssignmentsDisplayData,
	 ParentGroupsAssignments => $parentAssignments,
	 GroupMembers => $gmDD,
	 DeleteGroupMemberURL => "viewGroupDetails.cgi?action=DeleteGroupMember",
	 scriptdir => $scriptdir,
	 ServerURL => $serverurl,
	 ProxyLink => "annotateit.cgi",
	 formAction => "viewGroupDetails.cgi",
	 FromLocation => "viewGroupDetails.cgi",
	 ViewDetailsURL => "viewGroupDetails.cgi",
	 AddChildURL => "newGroup.cgi",
	 CanViewChildGroups => $viewChildGroups,
	 CanEditAssignment => $user->hasPrivilege("Own.EditAssignment"),
	 CanSeeAssignmentDetails => $user->hasPrivilege("Own.ViewAssignment"),
	 CanDeleteAssignment => $user->hasPrivilege("Own.DeleteAssignment"),
	 CanAddAssignments => $user->hasPrivilege("Own.AddAssignment"),
	 CanDeleteUsersFromGroup => $deleteFromGroup,
	CanViewDeletedAssignments => $user->hasPrivilege("Own.ViewDeletedAssignments") || $user->hasPrivilege("Other.ViewDeletedAssignments")};
if ($user->hasPrivilege("Other.AddUserToGroup") or
    ($user->hasPrivilege("Own.AddUserToGroup") 
     and $group->isOwner($user))) {
  $vars->{PrintAddFormElements} = 1;
}
if ($user->hasPrivilege("Other.CloseGroup") or
    ($user->hasPrivilege("Own.CloseGroup")
     and $group->isOwner($user))) {
  $vars->{CanCloseGroup} = 1;
}
$vars->{scriptdir} = $scriptdir;
print $C->header(-cookie=>$authInfo->{cookie});
$template->process("viewGroupDetails.html",$vars) or die $template->error;
exit;
