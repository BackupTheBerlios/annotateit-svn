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
use Carp;
use diagnostics;
use strict;
use Template;
# use Config::Simple qw( -strict );
use lib ("../site_perl");
use AnnotateitConfig;
use widgets;
use auth;
use User;
use CGI;
our $C = CGI->new;
our $config = $AnnotateitConfig::C;
our ($dbh, $authInfo, $scriptdir) = ();
$scriptdir = $config->{server}{scriptdirectory};
$dbh = &widgets::dbConnect($config);
$authInfo = &auth::authenticated($dbh,\$C);
our $template=Template->new( RELATIVE => 1,
			    INCLUDE_PATH => "../templates" );
our $action = $C->param("action") || "";
our $npw1 = $C->param("password1") || "";
our $npw2 = $C->param("password2") || "";
our $newFirstName = &widgets::scrub($C->param("FirstName") || "");
our $newLastName = &widgets::scrub($C->param("LastName") || "");
our $newEmail = &widgets::scrub($C->param("email") || "");
our $newNoteType = &widgets::scrub($C->param("NoteType") || "");
our $newAutoReload = &widgets::scrub($C->param("AutoReload") || "");
our $newSchool = &widgets::scrub($C->param("School") || "");
our $newName = $newFirstName . " " . $newLastName;
if (!$authInfo->{LoggedIn}) {
  my $vars = {scriptdir => $scriptdir,
	      formAction => "editUserInfo.cgi",
	      randomValue => &auth::randomValue(),
	      hiddenVar => [
			    {name=>"action", value=>$action},
			    {name=>"password1",value=>$npw1},
			    {name=>"password2",value=>$npw2},
			    {name=>"name", value=>$newName},
			    {name=>"FirstName", value=>$newFirstName},
			    {name=>"LastName", value=>$newLastName},
			    {name=>"email", value=>$newEmail},
			    {name=>"AutoReload", value=>$newAutoReload},
			    {name=>"NoteType", value=>$newNoteType},
			    {name=>"School", value=>$newSchool}],
	      };
  print $C->header;
  $template->process("loginScriptForm.html",$vars) or die $template->error;
  exit;
} else {
  if ($action eq "Save My Info") {
    &saveInfo();
  } else {
    &printEditForm();
  }
}
sub saveInfo {
  my $user = User->load(dbh => $dbh,
			ID => $authInfo->{UserID});
  my $oldEmail = $user->getEmail;
  my $oldName = $user->getName;
  my $oldFirstName = $user->getFirstName;
  my $oldLastName = $user->getLastName;
  my $oldPassword = $user->getPassword;
  my $oldSchool = $user->getSchool;
  my $changed = 0;
  my $deleteHeaders = 0;
  if ($oldEmail ne $newEmail) {
    my $user2 = User->loadFromEmail(dbh => $dbh,
				    Email => $newEmail);
    if ($user2->getID) {
      &printEditForm(error => "That email address is already in use.");
    } else {
      $user->setEmail($newEmail);
      $changed = 1;
      $deleteHeaders = 1;
    }
  }
  if ($oldFirstName ne $newFirstName) {
    if ($newFirstName) {
      $user->setFirstName($newFirstName);
      $changed = 1;
    } else {
      &printEditForm(error => "You must have a first name.");
    }
  }
  if ($oldLastName ne $newLastName) {
    if ($newLastName) {
      $user->setLastName($newLastName);
      $changed=1;
    } else {
      &printEditForm(error => "You must have a last name.");
    }
  }
  if ($npw1 and $npw1 eq $npw2) {
    if ($oldPassword ne $npw1) {
      $user->setPassword($npw1);
      $changed = 1;
      $deleteHeaders = 1;
    }
  } elsif ($npw1 or $npw2 and $npw1 ne $npw2) {
    &printEditForm(error => "Your passwords do not match.");
  }
  if ($newAutoReload eq 'Yes' or $newAutoReload eq 'No') {
    if ($user->getAutoReload ne $newAutoReload) {
      $user->setAutoReload($newAutoReload);
      $changed = 1;
    }
  }
  if ($newNoteType ne $user->getNoteType) {
    $user->setNoteType($newNoteType);
    $changed = 1;
  }
  if ($newSchool ne $oldSchool) {
    $user->setSchool($newSchool);
    $changed = 1;
  }
  if ($changed) {
    $user->update;
  }
  &printEditForm(Updated => $changed,
		 DeleteHeaders => $deleteHeaders);
}
sub printEditForm {
  my (%args) = @_;
  my $user = User->load(dbh => $dbh,
			ID => $authInfo->{UserID});
  my $vars = $user->getDisplayData;
  $vars->{Groups} = $user->getGroupDisplayData;
  for my $key (keys %args) {
    $vars->{$key} = $args{$key};
  }
  $vars->{EnglishAction} = "Edit";
  $vars->{formAction} = "editUserInfo.cgi";
  $vars->{scriptdir} = $scriptdir;
  $vars->{editUserInfo} = 1;
  if ($args{DeleteHeaders}) {
    print $C->header(-cookie => &auth::expireAuthTokens);
  } else {
    print $C->header(-cookie => $authInfo->{cookie});
  }
  $template->process("createUser.html",$vars);

  exit;
}

