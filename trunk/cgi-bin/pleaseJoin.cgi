#!/usr/local/bin/perl -wT
#############################################
## Sends email to those who have been invited to join
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
# use Config::Simple qw( -strict );
use lib ("../site_perl");
use AnnotateitConfig;
use widgets;
use auth;
use User;
use Group;
use MIME::Lite;
use CGI;
$ENV{PATH} = "/usr/bin:/usr/sbin:/usr/local/bin";
our $C = CGI->new;
my $config = $AnnotateitConfig::C;
our ($dbh, $authInfo,$scriptdir,$cgiDir, $docDir, $serverURL,$docURL);
$scriptdir = $config->{server}{scriptdirectory};
$serverURL = $config->{server}{url};
$cgiDir = $serverURL  . $scriptdir;
$docDir = $config->{server}{documentdirectory};
$docURL = $config->{server}{documenturl};
$dbh = &widgets::dbConnect($config);
$authInfo = &auth::authenticated($dbh,\$C);
my $template = Template->new( RELATIVE => 1,
			      INCLUDE_PATH => "../templates" );
my $GroupID = $C->param("GID");
my $action = $C->param("a") || "";

my $vars = { scriptdir => $scriptdir,
	     serverurl => $serverURL,
	     randomValue => &auth::randomValue(),
	     formAction => 'pleaseJoin.cgi',
	     a => $action
	   };
if (!$authInfo->{LoggedIn}) {
  $vars->{hiddenVar} = [
			{paramName => 'GID', paramValue => $GroupID},
			{paramName => 'a',paramValue => $action}
		       ];
  print $C->header();
  $template->process("loginScriptForm.html",$vars) || die $template->error;
  exit;
}
my $group = Group->load(dbh => $dbh, GroupID => $GroupID);
my $user = User->load(dbh => $dbh, ID => $authInfo->{UserID});
if (!$action) {
  $vars->{Group} = $group->getDisplayData($user);
  $vars->{User} = $user->getDisplayData;
  print $C->header(-cookie=>$authInfo->{cookie});
  $template->process("InviteToJoinGroup.html",$vars) || die $template->error;
  exit;
} elsif ($action eq "i") { # invite
  $vars->{Group} = $group->getDisplayData($user);
  $vars->{User} = $user->getDisplayData;
  my $emailAddresses = $C->param("EmailAddresses") || "";
  $emailAddresses = &widgets::scrub($emailAddresses);
  &emptyForm unless ($emailAddresses);
  my @emailAddresses = split /\s*,\s*/, $emailAddresses;
  my $sth = $dbh->prepare("SELECT ID FROM user WHERE email = ?");
  my @failures = ();
  my @successes = ();
  for my $address (@emailAddresses) {
    $sth->execute($address);
    my ($id) = $sth->fetchrow_array;
    if (defined $id and $id) {
      push @successes, {Address => $address};
    } else {
      push @failures, {Address => $address};
    }
  }
  $vars->{GroupID} = $GroupID;
  my $message = "";
  $template->process('GroupInvitationEmail',$vars, \$message) || die $template->error;
  for my $address (@successes) {
    my $msg = MIME::Lite->new(To => $address->{Address},
			      From => $user->getEmail,
			      Subject => "Join A Group at Annotateit.com",
			      Type => "TEXT",
			      Data => $message);
    $msg->send;
  }
  $vars->{Success} = \@successes;
  $vars->{Failure} = \@failures;

  print $C->header(-cookie => $authInfo->{cookie});
  $template->process('InviteToJoinGroup.html',$vars) || die $template->error;
  exit;
} elsif ($action eq "s") { # sign me up
  my $group = Group->load( dbh => $dbh, GroupID => $GroupID);
  if ($group->getState ne "Closed") {
    if ($user->hasPrivilege("Own.JoinGroup")) {
      $group->addGroupMember($user);
      $vars->{success} = 1;
    } else {
      $vars->{error} = "NotPrivileged";
    }
  } else {
    $vars->{error} = "GroupClosed";
  }
  $vars->{User} = $user->getDisplayData;
  $vars->{Group} = $group->getDisplayData($user);
  print $C->header(-cookie => $authInfo->{cookie});
  $template->process("InviteToJoinGroup.html",$vars) || die $template->error;
  exit;
}



