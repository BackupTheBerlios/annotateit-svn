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
# use Config::Simple qw( -strict );
use lib ("../site_perl");
use AnnotateitConfig;
use widgets;
use auth;
use User;
use CGI;
our $C = CGI->new;
our $config = $AnnotateitConfig::C;
our ($dbh, $user, $authInfo, $scriptdir);
$scriptdir = $config->{server}{scriptdirectory};
$dbh = &widgets::dbConnect($config);
$authInfo = &auth::authenticated($dbh,\$C);
our $template = Template->new( RELATIVE => 1,
			      INCLUDE_PATH => "../templates");
unless ($authInfo->{LoggedIn}) {
  my $vars = {formAction => "manageAnnotations.cgi",
	      randomValue => &auth::randomValue(),
	      scriptdir => $scriptdir};
  print $C->header;
  $template->process("loginScriptForm.html",$vars);
  exit;
}
$user = User->load(ID => $authInfo->{UserID},
		   dbh => $dbh);
our $vars = $user->getDisplayData;
$vars->{Groups} = $user->getGroupDisplayData;
$vars->{ManageInfoLink} = "manageUserInfo.cgi";
$vars->{editURL} = "editAnnotation.cgi?ID=";
$vars->{deleteURL} = "deleteAnnotation.cgi?ID=";
$vars->{scriptdir} = $scriptdir;
print $C->header(-cookie => $authInfo->{cookie});
$template->process("manageCustomAnnotations.html",$vars);
exit;

