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
use CGI;
our $C = CGI->new;

my $config = Config::Simple->new("../etc/annie.conf");
our ($dbh, $authInfo, $scriptdir, $user);
my $template= Template->new( RELATIVE => 1,
			     INCLUDE_PATH => "../templates");

$scriptdir = $config->param("server.scriptdirectory");
$dbh = &widgets::dbConnect($config);
$authInfo = &auth::authenticated($dbh,\$C);
unless ($authInfo->{LoggedIn}) {
  my $vars = {scriptdir => $scriptdir,
	      randomValue => &auth::randomValue(),
	      formAction => "manageGroups.cgi"};
  print $C->header;
  $template->process("loginScriptForm.html",$vars) or die $template->error;
  exit;
}
$user = User->load(dbh => $dbh,
		   ID => $authInfo->{UserID});
my $vars = {};
$vars->{ManageUserInfoLink} = "manageUserInfo.cgi";
$vars->{User} = $user->getDisplayData;
$vars->{Groups} =  $user->getGroupDisplayData;
$vars->{ViewGroupDetailsLink} = "viewGroupDetails.cgi?GroupID=";
$vars->{DeleteLink} = "deleteGroup.cgi?GroupID=";
$vars->{scriptdir} = $scriptdir;
$vars->{formAction} = "manageGroups.cgi";
print $C->header(-cookie=>$authInfo->{cookie});
$template->process("manageGroups.html",$vars) or die $template->error;

exit;

