#!/usr/local/bin/perl -wT
# deletes predefined annotations and redirects
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
use CommunityAnnotation;
use User;
use CGI;
our $C = CGI->new;
my $config = Config::Simple->new("../etc/annie.conf");
our ($dbh, $authInfo, $cgiDir,$scriptdir);
my $template = Template->new( RELATIVE => 1,
			      INCLUDE_PATH => "../templates");
$dbh = &widgets::dbConnect($config);
$scriptdir = $config->param("server.scriptdirectory");
$cgiDir = $config->param("server.url") .  $scriptdir;
$authInfo = &auth::authenticated($dbh,\$C);
our $action = $C->param("action") || "";
our $ID = $C->param("ID") || "";
unless ($authInfo->{LoggedIn}) {
  my $vars = { scriptdir => $scriptdir,
	       formAction => "manageAnnotations.cgi",
	       randomValue => &auth::randomValue(),
	       hiddenVar => [{name=>"action", value=>$action},
			     {name=>"ID",value=>$ID}]};
  print $C->header();
  $template->process("loginScriptForm.html",$vars);
  exit;
}
my $user = User->load( dbh => $dbh,
		       ID => $authInfo->{UserID});
unless ($user->hasPrivilege("Other.DeleteCommunityAnnotation")) {
  my $vars = { scriptdir => $scriptdir,
	       serverurl => $config->param("server.url"),
	       Error => "NoPrivilegeToDeleteCommunityAnnotation",
	       EnglishError => "Unauthorized",
	       BackPage => "manageCommunityAnnotations.cgi" };
  print $C->header(-cookie=>$authInfo->{cookie});
  $template->process("Error.html",$vars) or die $template->error;
  exit;
}
my $ca = CommunityAnnotation->load( dbh => $dbh,
				    ID => $ID );
if ($action eq "DELETE") {
  $ca->delete;
  print $C->redirect($cgiDir."manageCommunityAnnotations.cgi");
  exit;
} else {
  my $vars = $ca->getDisplayData;
  $vars->{scriptdir} = $scriptdir;
  $vars->{action} = "DELETE";
  print $C->header(-cookie=>$authInfo->{cookie});
  $template->process("DeleteCommunityAnnotation.html",$vars) or die $template->error;
  exit;
}


