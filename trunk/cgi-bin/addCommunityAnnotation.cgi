#!/usr/local/bin/perl -wT
# Add a Community Annotation annotation.
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
use widgets;
use auth;
use CommunityAnnotation;
use AnnotateitConfig;
use User;
use CGI;
our $C = CGI->new;

my $config = $AnnotateitConfig::C;
our ($dbh, $authInfo, $scriptdir, $serverURL);
$scriptdir = $config->{server}{scriptdirectory};
$serverURL = $config->{server}{url};
$dbh = &widgets::dbConnect($config);
$authInfo = &auth::authenticated($dbh,\$C);
my $Title = &widgets::scrub($C->param("Title") || "");
my $Description = &widgets::scrub("keeplinks",$C->param("Description") || "");
my $Category = &widgets::scrub($C->param("Category") || "");
my $template = Template->new( RELATIVE => 1,
			      INCLUDE_PATH => "../templates" );
unless ($authInfo->{LoggedIn}) {
  my $vars = {scriptdir => $scriptdir,
	      randomValue => &auth::randomValue(),
	      formAction => "manageCommunityAnnotations.cgi",
	      hiddenVar => [ { name => "Title", value => $Title},
			     { name => "Description", value => $Description},
			     { name => "Category", value => $Category} ]
	     };
  print $C->header();
  $template->process("loginScriptForm.html",$vars );
  exit;
}
my $user = User->load(dbh => $dbh,
		      ID => $authInfo->{UserID});
if ($user->hasPrivilege("Other.AddCommunityAnnotation")) {
  my $cA = CommunityAnnotation->new( dbh => $dbh );
  $cA->setTitle($Title);
  $cA->setDescription($Description);
  $cA->setCategory($Category);
  $cA->save;
  print $C->redirect(-url => $serverURL . $scriptdir . "manageCommunityAnnotations.cgi",
			   -cookie => $authInfo->{cookie});
} else {
  my $vars = { Error => "NoPrivilegeToAddCommunityAnnotation",
	       scriptdir => $scriptdir,
	       serverurl => $serverURL,
	       EnglishError => "Unauthorized",
	       BackPage => "manageCommunityAnnotations.cgi" };
  print $C->header(-cookie => $authInfo->{cookie});
  $template->process("Error.html",$vars) or die ($template->error);
}
exit;


