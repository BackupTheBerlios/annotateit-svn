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
use Config::Simple qw( -strict );
use lib ("../site_perl");
use widgets;
use CGI;
use auth;
use User;
use Assignment;
use Date::Calc qw(Today Delta_Days );
use Template;
our $C = CGI->new();
$ENV{TMPDIR} = "/tmp";
my @chars = ('A'..'Z','a'..'z',0..9);
my $config = Config::Simple->new("../etc/annie.conf");
my $dbh = &widgets::dbConnect($config);
my $authInfo = &auth::authenticated($dbh,\$C);
my $scriptdir = $config->param("server.scriptdirectory");
my $serverURL = $config->param("server.url");
my $docURL = $config->param("server.documenturl");
my $action = $C->param("action") || "";
my $docDir = $config->param("server.documentdirectory");
my $ID = $C->param("ID");
my $template = Template->new( RELATIVE => 1,
			       INCLUDE_PATH => "../templates");


if (!$authInfo->{LoggedIn}) {
  my $vars = { scriptdir => $scriptdir,
	       randomValue => &auth::randomValue(),
	       formAction => "addAssignment.cgi",
	       hiddenVar => [ 
			     {paramName => "action",paramValue => $action},
			     {paramName => "ID", paramValue => $ID}]
	       };
  print $C->header();
  $template->process("loginScriptForm.html",$vars) || die $template->error();
  exit;
}

if ($action eq "delete") {
  my $user = User->load( dbh => $dbh,
			 ID => $authInfo->{UserID} );
  my $groups = $user->getGroupDisplayData;
  my $udd = $user->getDisplayData;
  my $vars = { DeletionSuccessful => 1,
	       scriptdir => $scriptdir,
	       formAction => "deleteAssignment.cgi",
	       Groups => $groups,
	       User => $udd};
  my $Assignment= Assignment->load( dbh => $dbh,
				    ID => $ID );
  $Assignment->delete($docDir);

  print $C->redirect(-cookie=>$authInfo->{cookie},
			   -url => "$serverURL$scriptdir"."displayAssignments.cgi");
  exit;
} elsif ($action eq "undelete") {
  my $user = User->load( dbh => $dbh,
			 ID => $authInfo->{UserID} );

  my $assignment = Assignment->load( dbh => $dbh,
				     ID => $ID );
  $assignment->undelete;

  print $C->redirect(-url=>"$serverURL$scriptdir"."displayAssignments.cgi",
			  -cookie=>$authInfo->{cookie});

}
exit;
