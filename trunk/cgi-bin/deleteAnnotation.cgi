#!/usr/local/bin/perl -wT

# Copyright 2003, Buzzmaven Co.

# deletes predefined annotations and redirects
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
use CGI;
use auth;
use PredefinedAnnotation;
our $C = CGI->new;
our $config = $AnnotateitConfig::C;
our ($dbh, $authInfo, $serverURL,$scriptdir);
our $template = Template->new( RELATIVE => 1,
			      INCLUDE_PATH => "../templates");
$dbh = &widgets::dbConnect($config);
$scriptdir = $config->{server}{scriptdirectory};
$serverURL = $config->{server}{url};
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
my $pda = PredefinedAnnotation->load( dbh => $dbh,
				      ID => $ID,
				      UserID => $authInfo->{UserID});
if ($action eq "DELETE") {

  $pda->delete if ($pda->getUserID eq $authInfo->{UserID});
  print $C->redirect($serverURL.$scriptdir."manageAnnotations.cgi");
  exit;
} else {
  my $vars = $pda->getDisplayData;
  $vars->{scriptdir} = $scriptdir;
  $vars->{action} = "DELETE";
  print $C->header(-cookie=>$authInfo->{cookie});
  $template->process("deleteCustom.html",$vars) or die $template->error;
  exit;
}


