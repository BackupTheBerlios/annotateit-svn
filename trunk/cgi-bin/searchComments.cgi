#!/usr/local/bin/perl -wT
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
use auth;
use Group;
use User;
use CommentsSearch;
use CGI;
our $C = CGI->new;
my $config = Config::Simple->new("../etc/annie.conf");
my $scriptdir = $config->param("server.scriptdirectory");
my $serverURL = $config->param("server.url");
my $action = $C->param("action") || "";
our ($dbh, $authInfo);

$dbh = &widgets::dbConnect($config);
$authInfo = &auth::authenticated($dbh,\$C);
my $template = Template->new( RELATIVE => 1,
			      INCLUDE_PATH => "../templates");

unless ($authInfo->{LoggedIn}) {
  my $vars = {scriptdir => $scriptdir,
	      randomValue => &auth::randomValue(),
	      formAction => "searchComments.cgi"};
  print $C->header;
  $template->process("loginScriptForm.html",$vars) or die $template->error;
  exit;
}
my $user = User->load( dbh => $dbh,
		       ID => $authInfo->{UserID} );
unless ($user->hasPrivilege("Other.SearchComments") or
	$user->hasPrivilege("Own.SearchComments")) {
  my $vars = {scriptdir => $scriptdir,
	      randomValue => &auth::randomValue(),
	      formAction => "searchComments.cgi",
	      Error => 'UnauthorizedSearch',
	      EnglishError => 'Unauthorized Search'};
  print $C->header;
  $template->process("Error.html",$vars) or die $template->error;
  exit;
}
unless ($action eq "Search") {
  my @user = &getUsers;
  my @groups = &getGroups;
  
  my $vars = { Users => \@user,
	       Groups => \@groups,
	       User => $user->getDisplayData,
	       scriptdir => $scriptdir,
	       formAction => "searchComments.cgi" };
  print $C->header(-cookie => $authInfo->{cookie});
  $template->process("SearchCommentsForm.html",$vars) or die $template->error;
  exit;
}
my $search = CommentsSearch->new( User => $user, 
				  dbh => $dbh,
				  UserID => $C->param("UserID") || "",
				  GroupID => $C->param("GroupID") || "",
				  URL => $C->param("URL") || "",
				  AnnotationTitle => $C->param("AnnotationTitle") || "",
				  Comment => $C->param("Comment") || "",
				);
my $results = $search->getResults;
my $vars = {};
$vars->{Results} = $results;
if ($#{$results} > -1) {
  $vars->{HasResults} = 1;
}
$vars->{scriptdir} = $scriptdir;
$vars->{viewAnnotationLink} = "displayAnnotation.cgi";
$vars->{serverURL} = $serverURL;
$vars->{showURLLink} = "annotateit.cgi";
print $C->header;
$template->process("SearchCommentsResults.html",$vars) or die $template->error;
exit;

				     
sub getGroups {
  my @rv = ();
  if ($user->hasPrivilege("Other.SearchAnnotations")) {
    my $sth = $dbh->prepare("SELECT DISTINCT(GroupID) FROM annotation");
    $sth->execute;
    while (my ($GroupID) = $sth->fetchrow_array) {
      my $g = Group->load(GroupID => $GroupID,
			  dbh => $dbh);
      push @rv, $g->getDisplayData($user);
    }
  } else {
    $user->loadGroups;
    my $groups = $user->getGroups;
    for my $group (@{$groups}) {
      push @rv, $group->getDisplayData($user);
    }
    push @rv, { GroupID => "Public",
		GroupName => "Public" };
  }
  return @rv;
}
sub getUsers {
  my @rv = ();
  if ($user->hasPrivilege("Other.SearchAnnotations")) {
    my $sth = $dbh->prepare("SELECT DISTINCT(UserID) FROM annotation");
    $sth->execute;
    while (my ($userID) = $sth->fetchrow_array) {
      my $u = User->load( dbh => $dbh,
			  ID => $userID);
      my $dd = { ID => $u->getID,
		 Name => $u->getName };
      push @rv, $dd;
    }
  } else {
    $user->loadGroups;
    my $groups = $user->getGroups;
    my $sth = $dbh->prepare("SELECT DISTINCT(UserID) FROM annotation WHERE (GroupID = ?) or (GroupID = 'Public')");
    my %userIDs;
    for my $group (@{$groups}) {
      $sth->execute($group->getGroupID);
      while (my ($userID) = $sth->fetchrow_array) {
	$userIDs{$userID} = 1;
      }
    }
    for my $userID (keys %userIDs) {
      my $u = User->load( dbh => $dbh,
			  ID => $userID);
      my $dd = { ID => $u->getID,
		 Name => $u->getName };
      push @rv, $dd;
    }
  }
  return @rv;
}
      
