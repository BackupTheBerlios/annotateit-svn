#!/usr/local/bin/perl -wT
# Main menu for actions
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
use Data::Dumper;
use CGI;
our $C = CGI->new();
my $config = $AnnotateitConfig::C;
our ($template,$dbh, $authInfo, $scriptdir) = ();
$scriptdir = $config->{server}{scriptdirectory};
$dbh = &widgets::dbConnect($config);
$authInfo = &auth::authenticated($dbh,\$C);
$template = Template->new( INCLUDE_PATH => "../templates",
			   RELATIVE => 1);
my $reload = $C->param("reload") || 0;

if (!$authInfo->{LoggedIn}) {
  my $vars = {scriptdir => $scriptdir,
	      randomValue => &auth::randomValue,
	      formAction => "login.cgi" };
  print $C->header;
  $template->process("loginScriptForm.html",$vars) or die $template->error();
  exit;
} else {
  my $user = User->load(dbh => $dbh,
			ID => $authInfo->{UserID});
  my $vars = $user->getDisplayData;
  if ($user->hasPrivilege("Own.ViewAssignment")) {
    $vars->{CanViewAssignments} = 1;
    if ($user->hasGroups) {
      $vars->{CanHaveAssignments} = 1;
    } else {
      $vars->{CanHaveAssignments} = 0;
    }
  } else {
    $vars->{CanHaveAssignments} = 0;
  }

  $vars->{Groups} = $user->getGroupDisplayData;
  $vars->{scriptdir} = $scriptdir;
  $vars->{searchAnnotationsLink} = "searchAnnotations.cgi";
  $vars->{reload} = $reload;
  print $C->header;
  $template->process("manageUserInfo.html",$vars) or die $template->error();
  exit;

}

