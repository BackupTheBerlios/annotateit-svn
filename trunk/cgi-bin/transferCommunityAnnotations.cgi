#!/usr/local/bin/perl -wT
##############################################
## This transfers the values of community annotations to a
## user's predefined annotations list.
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
# use Config::Simple qw( -strict );
use lib ("../site_perl");
use AnnotateitConfig;
use widgets;
use auth;
use User;
use CommunityAnnotation;
use PredefinedAnnotation;
use CGI;
our $C = CGI->new;

my $config = $AnnotateitConfig::C;
our ($dbh, $authInfo,$scriptdir,$cgiDir);
$scriptdir = $config->{server}{scriptdirectory};
$cgiDir = $config->{server}{url} . $scriptdir;
$dbh = &widgets::dbConnect($config);
$authInfo = &auth::authenticated($dbh,\$C);
our $action = $C->param("action") || "";
my @ids = $C->param("ID");
my $template = Template->new( RELATIVE => 1,
			      INCLUDE_PATH => "../templates" );

unless ($authInfo->{LoggedIn}) {
  my $vars = { formAction => "manageCommunityAnnotations.cgi",
	       scriptdir => $scriptdir,
	       randomValue => &auth::randomValue(),
	       };
  print $C->header;
  $template->process("loginScriptForm.html",$vars) or die $template->error;
  exit;
}
my $user = User->load(ID => $authInfo->{UserID},
		      dbh => $dbh);

for my $id (@ids) {
  my $ca = CommunityAnnotation->load( dbh => $dbh,
				      ID => $id);
  my $pda = PredefinedAnnotation->new(dbh => $dbh);
  $pda->setValue($ca->getDescription);
  $pda->setLabel($ca->getTitle);
  $pda->setUserID($user->getID);
  $pda->save;
}

my $vars = { scriptdir => $scriptdir,
	     serverurl => $config->{server}{url} };
print $C->header(-cookie=>$authInfo->{cookie});
$template->process("TransferCommunityAnnotations.html",$vars) or die $template->error;
exit;
