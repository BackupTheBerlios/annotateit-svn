#!/usr/local/bin/perl -w
# Add a pre defined annotation.

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
use CGI;
use auth;
use PredefinedAnnotation;
our $C = CGI->new;
our $config = Config::Simple->new("../etc/annie.conf");
our ($dbh, $authInfo, $scriptdir, $serverURL);
$scriptdir = $config->param("server.scriptdirectory");
$serverURL = $config->param("server.url");
$dbh = &widgets::dbConnect($config);
$authInfo = &auth::authenticated($dbh,\$C);

our $value = $C->param("value") || "";
our $title = $C->param("label") || "No Title";
$value=&widgets::scrub($value);
$title=&widgets::scrub($title);

unless ($authInfo->{LoggedIn}) {
  my $template = Template->new( RELATIVE => 1,
				INCLUDE_PATH => "../templates" );
  my $vars = {scriptdir => $scriptdir,
	      randomValue => &auth::randomValue(),
	      formAction => "manageAnnotations.cgi",
	      hiddenVar => [ { name => "value", value => $value},
			     { name => "label", value => $title } ]
	     };
  print $C->header();
  $template->process("loginScriptForm.html",$vars );
  exit;
}
our $pA = PredefinedAnnotation->new( dbh => $dbh );
$pA->setUserID($authInfo->{UserID});
$pA->setValue($value);
$pA->setLabel($title);
$pA->save;

print $C->redirect(-url => $serverURL . $scriptdir . "manageAnnotations.cgi",
			 -cookie => $authInfo->{cookie});
exit;


