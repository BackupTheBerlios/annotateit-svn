#!/usr/local/bin/perl -wT
##############################################
## This edits the predefined annotations... not the site annotations
##
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
use CommunityAnnotation;
our $C = CGI->new;
my $config = Config::Simple->new("../etc/annie.conf");
our ($dbh, $authInfo,$scriptdir,$cgiDir);
$scriptdir = $config->param("server.scriptdirectory");
$cgiDir = $config->param("server.url") . $scriptdir;
$dbh = &widgets::dbConnect($config);
$authInfo = &auth::authenticated($dbh,\$C);
our $action = $C->param("action") || "";
our $ID = $C->param("ID") || "";
my $template = Template->new( RELATIVE => 1,
			      INCLUDE_PATH => "../templates" );

unless ($authInfo->{LoggedIn}) {
  my $vars = { formAction => "editCommunityAnnotation.cgi",
	       scriptdir => $scriptdir,
	       randomValue => &auth::randomValue(),
	       hiddenVars => [
			      { name => "ID", value => $ID },
			      { name => "action", value => $action }
			     ]
	       };
  print $C->header;
  $template->process("loginScriptForm.html",$vars) or die $template->error;
  exit;
}
my $user = User->load(ID => $authInfo->{UserID},
		      dbh => $dbh);
unless ($user->hasPrivilege("Other.EditCommunityAnnotation")) {
  my $vars = { Error => "NoPrivilegeToEditCommunityAnnotation",
	       EnglishError => "Unauthorized",
	       scriptdir => $scriptdir,
	       serverurl => $config->param("server.url"),
	       BackPage => "manageCommunityAnnotations.cgi" };
  print $C->header(-cookie=>$authInfo->{cookie});
  $template->process("Error.html",$vars) or die $template->error;
}

if ($action eq "saveChanges") {
  &saveChanges;
} else {
  &printEditForm;
}
sub saveChanges {
  my $ca = CommunityAnnotation->new(dbh => $dbh,
				    ID => $ID);
  my $desc = &widgets::scrub(($C->param("Description") || "No Description"));
  $ca->setDescription($desc);
  my $title = &widgets::scrub(($C->param("Title") || "No Title"));
  $ca->setTitle($title);
  my $category = &widgets::scrub(($C->param("Category") || "No Category"));
  $ca->setCategory($category);
  $ca->update;
  print $C->redirect($cgiDir . "manageCommunityAnnotations.cgi");
  exit;
}
sub printEditForm {
  my $ca = CommunityAnnotation->load(dbh => $dbh,
				     ID => $ID);
  my $vars = $ca->getDisplayData;
  $vars->{scriptdir} = $scriptdir;
  $vars->{action} = "saveChanges";
  $vars->{editURL} = "editAnnotaiton.cgi?ID=";
  $vars->{deleteURL} = "deleteAnnotation.cgi?ID=";
  print $C->header(-cookie=>$authInfo->{cookie});
  $template->process("EditCommunityAnnotation.html",$vars) or die $template->error;
  exit;
}

