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
use Annotation;
use User;
use CGI;
our $C = CGI->new;

my $config = Config::Simple->new("../etc/annie.conf");
our ($dbh, $authInfo, $scriptdir, $serverurl);
$scriptdir = $config->param("server.scriptdirectory");
$serverurl = $config->param("server.url");
$dbh = &widgets::dbConnect($config);
$authInfo = &auth::authenticated($dbh,\$C);
my $template = Template->new( RELATIVE => 1,
			      INCLUDE_PATH => "../templates");
unless ($authInfo->{LoggedIn}) {
  my $vars = {scriptdir => $scriptdir,
	      randomValue => &auth::randomValue(),
	      formAction => "viewGroupDetails.cgi"};
  print $C->header;
  $template->process("loginScriptForm.html",$vars);
  exit;
}

my $user = User->load( dbh => $dbh,
		       ID => $authInfo->{UserID});
my $sth = $dbh->prepare("SELECT ID FROM annotation WHERE UserID = ?");
$sth->execute($user->getID);
my @annotations =();
my %annotatedURLS = ();
while (my ($id) = $sth->fetchrow_array) {
  my $annotation = Annotation->load(dbh => $dbh,
				    ID => $id);
  my $url = $annotation->getURL();
  next if (defined $annotatedURLS{$url} and $annotatedURLS{$url} == 1);
  $annotatedURLS{$url} = 1;
  push @annotations, $annotation->getDisplayData({CurrentUser => $user});
}


my $vars = {User  => $user->getDisplayData,
	 AnnotatedURLs => \@annotations,
	 Title => "View URLs You have Annotated",
	 scriptdir => $scriptdir,
	 ServerURL => $serverurl,
	 ProxyLink => "annotateit.cgi",
	 formAction => "viewGroupDetails.cgi",
	 FromLocation => "viewGroupDetails.cgi",
	 ViewDetailsURL => "viewGroupDetails.cgi"};
print $C->header(-cookie=>$authInfo->{cookie});
$template->process("viewAnnotatedURLs.html",$vars) or die $template->error;
exit;
