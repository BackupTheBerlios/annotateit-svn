#!/usr/local/bin/perl -w
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
use Group;
use CGI;
our $C = CGI->new;
my $config = Config::Simple->new("../etc/annie.conf");
our ($dbh, $authInfo, $scriptdir, $serverURL);
$scriptdir = $config->param("server.scriptdirectory");
$serverURL = $config->param("server.url");
$dbh = &widgets::dbConnect($config);
$authInfo = &auth::authenticated($dbh,\$C);
my $ownerID = $authInfo->{UserID};
my $groupID = $C->param("GroupID");
my $template = Template->new( RELATIVE => 1,
			      INCLUDE_PATH => "../templates");

unless ($authInfo->{LoggedIn}) {
  my $vars = {scriptdir => $scriptdir,
	      formAction => 'deleteGroup.cgi',
	      randomValue => &auth::randomValue(),
	      hiddenVar => [
			    { name => "GroupID", value=> $groupID }
			   ]};
  print $C->header;
  $template->process("loginScriptForm.html",$vars);
}
&deleteGroup();
print $C->redirect(-cookie=>$authInfo->{cookie},
			 -url=>"$serverURL$scriptdir"."manageGroups.cgi");
exit;
sub deleteGroup {
  my $gr = Group->load( dbh => $dbh,
			GroupID => $groupID );
  $gr->delete if ($gr->getOwnerID == $authInfo->{UserID});


}

