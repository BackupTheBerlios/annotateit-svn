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
use auth;
use widgets;
use User;
use Annotation;
use CGI;
our $C = CGI->new;

my $config = Config::Simple->new("../etc/annie.conf");
our $dbh = &widgets::dbConnect($config);
my $currentURL = $http::C->param("url") || "";
$currentURL =~ s/[<>]//g;
our $authInfo = &auth::authenticated($dbh,\$C);
our $user = User->load(dbh => $dbh,
		       ID => $authInfo->{UserID});

my $template = Template->new( RELATIVE => 1,
			      INCLUDE_PATH => "../templates");
my $scriptdir = $config->param("server.scriptdirectory");
if (!($authInfo->{LoggedIn})) {
  my $vars = { scriptdir => $scriptdir,
	       randomValue => &auth::randomValue(),
	       formAction => "displayWholePageNotes.cgi",
	       hiddenVar => [{ name => "url",
			       value => $currentURL }] };
  print $http::C->header;
  $template->process("loginScriptForm.html",$vars) or die $template->error;
  exit;
}
$user->loadGroups;
my $dd;

$dd->{Annotations} = $user->getAnnotationsDisplayData({URL => $currentURL});
$dd->{User} = $user->getDisplayData;
$dd->{DisplayAnnotationURL} = "displayAnnotation.cgi";
$dd->{scriptdir} = $scriptdir;
$dd->{currentURL} = $currentURL;

print $http::C->header(-cookie=>$authInfo->{cookie});
$template->process("DisplayWholePageNotes.html",$dd) or die $template->error;
exit;

