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
use CGI;
use auth;
use User;
our $C = CGI->new;
our $config = Config::Simple->new("../etc/annie.conf");
our ($template,$dbh, $authInfo, $scriptdir) = ();
$scriptdir = $config->param("server.scriptdirectory");
our $serverURL = $config->param("server.url");
our $noReload = $C->param("noReload") || "";
$dbh = &widgets::dbConnect($config);;
$authInfo = &auth::authenticated($dbh,\$C);
$template = Template->new( INCLUDE_PATH => "../templates",
			   RELATIVE => 1);
# if we are not logged in ...... or
# if we are trying to log out
if (!(defined $authInfo->{LoggedIn} and $authInfo->{LoggedIn}) || 
    (defined $C->param("action") and $C->param("action") eq "logout")) {
  my $vars = {scriptdir => $scriptdir,
	      formAction => "login.cgi",
	      randomValue => &auth::randomValue(),
	      hiddenVar => [{name => "noReload", value =>$noReload}]};
  my $loginAttempts = $C->param("LoginAttempts") || 0;

  if ($loginAttempts > 0) {
    $vars->{"LoginAttempts"} = $loginAttempts + 1;
    $vars->{"LoginFailed"} = 1;
  } elsif ($loginAttempts == 0) {
    $vars->{"LoginAttempts"} = 1;
    $vars->{"LoginFailed"} = 0;
  }
  print $C->header(-cookie=>&auth::expireAuthTokens);
  $template->process("loginScriptForm.html",$vars) or die $template->error();
  exit;
} else {
  my $redir = $serverURL . $scriptdir ."manageUserInfo.cgi";
  $redir .= "?reload=1" unless ($noReload);
  print $C->redirect(-cookie=>$authInfo->{cookie},
			   -url=>"$redir");
  exit;
}

