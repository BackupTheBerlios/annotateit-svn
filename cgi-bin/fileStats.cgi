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
use Document;
use CGI;
our $C = CGI->new;

my $config = Config::Simple->new("../etc/annie.conf");
my $dbh = &widgets::dbConnect($config);
my $authInfo = &auth::authenticated($dbh,\$C);
my $scriptdir = $config->param("server.scriptdirectory");
our $serverURL = $config->param("server.url");
our $docURL = $config->param("server.documenturl");
my $action = $C->param("action") || "";
our $docDir = $config->param("server.documentdirectory");
my $template = Template->new( RELATIVE => 1,
			       INCLUDE_PATH => "../templates");
my $ID = $C->param("ID");
if (!$authInfo->{LoggedIn}) {
  my $vars = { scriptdir => $scriptdir,
	       randomValue => &auth::randomValue(),
	       formAction => "assignmentDetail.cgi",
	       hiddenVar => [ 
			     {paramName => "action",paramValue => $action}]
	       };
  print $C->header();
  $template->process("loginScriptForm.html",$vars) || die $template->error();
  exit;
}

my $document = Document->load( dbh => $dbh,
				   ID => $ID);
my $user = User->load( dbh => $dbh,
		       ID => $authInfo->{UserID} );
my $vars = { scriptdir => $scriptdir,
	     formAction => 'assignmentDetails.cgi'};

if (! &checkAuth) {
  $vars->{Unauthorized} = 1;
} else {
  $vars->{Document} = $document->getDisplayData;
  $vars->{Stats} = $document->getStyleStatistics;
}

print $C->header(-cookie => $authInfo->{cookie});
$template->process("FileStatistics.html",$vars) || die $template->error;
exit;

sub checkAuth {
  if ( $user->getID == $document->OwnerID
       and $user->hasPrivilege("Own.ViewStatistics")
       )
    {
      return 1;
    }
  if ( $user->hasPrivilege("Other.ViewStatistics")
       and !$user->hasRole("Admin") ) {
    my $documentUserID = $document->OwnerID;
    my $documentUser = User->load( ID => $documentUserID,
				   dbh => $dbh);
    $user->loadGroups;
    $documentUser->loadGroups;
    for my $group (@{$user->{Groups}}) {
      return 1 if ($documentUser->hasGroup($group->getGroupID));
    } 
  } elsif ($user->hasPrivilege("Other.ViewStatistics")
	   and $user->isAdmin) {
    return 1;
  }
  return 0;

}
