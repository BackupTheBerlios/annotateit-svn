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
use CommunityAnnotation;
use CGI;
our $C = CGI->new;
my $config = Config::Simple->new("../etc/annie.conf");
our ($dbh, $user, $authInfo, $scriptdir);
$scriptdir = $config->param("server.scriptdirectory");
$dbh = &widgets::dbConnect($config);
$authInfo = &auth::authenticated($dbh,\$C);
my $vars = {};
my $template = Template->new( RELATIVE => 1,
			      INCLUDE_PATH => "../templates");
unless ($authInfo->{LoggedIn}) {
  $vars = {formAction => "manageCommunityAnnotations.cgi",
	   randomValue => &auth::randomValue(),
	   scriptdir => $scriptdir};
  print $C->header;
  $template->process("loginScriptForm.html",$vars);
  exit;
}
$user = User->load(ID => $authInfo->{UserID},
		   dbh => $dbh);
my $ca = CommunityAnnotation->new( dbh => $dbh);
$vars->{User} = $user->getDisplayData;
$vars->{CommunityAnnotation} = $ca->getAllDisplayData;
$vars->{scriptdir} = $scriptdir;
print $C->header(-cookie => $authInfo->{cookie});
$template->process("ManageCommunityAnnotations.html",$vars);
exit;

