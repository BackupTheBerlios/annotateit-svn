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
use Config::Simple qw( -strict );
use lib ("../site_perl");
use widgets;
use auth;
use User;
use IO::File;
use Assignment;
use Date::Calc qw(Today Delta_Days );
use CGI;
our $C = CGI->new;

$ENV{TMPDIR} = "/tmp";
my @chars = ('A'..'Z','a'..'z',0..9);
my $config = Config::Simple->new("../etc/annie.conf");
my $dbh = &widgets::dbConnect($config);
my $authInfo = &auth::authenticated($dbh,\$C);
my $scriptdir = $config->param("server.scriptdirectory");
our $serverURL = $config->param("server.url");
our $docURL = $config->param("server.documenturl");
my $action = $C->param("action") || "";
our $docDir = $config->param("server.documentdirectory");
my $template = Template->new( RELATIVE => 1,
			       INCLUDE_PATH => "../templates");
my $ID = $C->param("ID");
if (!$authInfo->{LoggedIn}) {
  my $vars = { scriptdir => $scriptdir,
	       randomValue => &auth::randomValue(),
	       formAction => "assignmentDetail.cgi",
	       hiddenVar => [ 
			     {paramName => "action",paramValue => $action}]
	       };
  print $C->header();
  $template->process("loginScriptForm.html",$vars) || die $template->error();
  exit;
}

my $assignment = Assignment->load( dbh => $dbh,
				   ID => $ID);
my $user = User->load( dbh => $dbh,
		       ID => $authInfo->{UserID} );

my $aGID = $assignment->getGroupID;
my $aUID = $assignment->getUserID;
my $vars = { scriptdir => $scriptdir,
	     formAction => 'assignmentDetails.cgi',
	     Assignment => $assignment->getDisplayData,
	     Stats => $assignment->getStats($user) };
unless (&checkAuth) { $vars->{Unauthorized} = 1 };


print $C->header(-cookie => $authInfo->{cookie});
$template->process("AssignmentStatistics.html",$vars) || die $template->error;
exit;

sub checkAuth {
  if (
      (
       ( $user->getID == $aUID 
	 or $user->hasGroup($aGID)
       )
       and $user->hasPrivilege("Own.AssignmentStatistics")
      ) or $user->hasPrivilege("Other.AssignmentStatistics")
     ) {
    return 1;
  } else {
    return 0;
  }
}
