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
use widgets;
use auth;
use User;
use AnnotateitConfig;
use Date::Calc qw(Today_and_Now);
use CGI;
our $C = CGI->new;
my $config = $AnnotateitConfig::C;
our ($template,$dbh, $authInfo, $scriptdir) = ();
$scriptdir = $config->{server}{scriptdirectory};
my $serverURL = $config->{server}{url};
my $var;
$var->{scriptdir} = $scriptdir;
my $action = $C->param("action") || "";
$dbh = &widgets::dbConnect($config);;
$authInfo = &auth::authenticated($dbh,\$C);
$template = Template->new( INCLUDE_PATH => "../templates",
			   RELATIVE => 1);
if (!$authInfo->{LoggedIn}) {
  my $vars = {scriptdir => $scriptdir,
	      formAction => "register.cgi",
	      randomValue => &auth::randomValue() };
  print $C->header();
  $template->process("loginScriptForm.html",$vars) or die $template->error();
  exit;
}
if ($action eq "Register") {
  my $ActivationCode = $C->param("ActivationCode") || "";
  unless ($ActivationCode) {
    $var->{Title} = "No Activation Code";
    $var->{Message} = "No activation code was entered. Please try again.";
    $var->{Form} = 1;
    sleep 10;
    &printForm;
  }
  my $sth = $dbh->prepare("SELECT ID, Type FROM License WHERE ActivationCode = ?");
  $sth->execute($ActivationCode);
  my ($id,$type) = $sth->fetchrow_array;
  if (defined $type and $type) {
    my %typesToAccessLevels = (Admin => 64,
			       Researcher => 32,
			       ResearchAssociate => 16,
			       Teacher => 8,
			       Student => 4,
			       Participant => 2,
			       User => 1);
    my $user = User->load(ID => $authInfo->{UserID},
			  dbh => $dbh);
    $user->setAccessKey($ActivationCode);
    $user->setStatus($type);
    $user->setAccessLevel($typesToAccessLevels{$type});
    my ($y,$m,$d,$h,$mi,$s) = Today_and_Now;
    $user->setDatePaid("$y-$m-$d $h:$mi:$s");
    $user->update;
    $sth = $dbh->prepare("DELETE FROM License WHERE ID = ?");
    $sth->execute($id);
    $var->{Title} = "Thanks!";
    $var->{Message} = "Thank you for registering! Your support means continued development of this project.";
    $var->{Form} = 0;
    $var->{Success} = 1;
    &printForm;
  } else {
    $var->{Title} = "Invalid Code";
    $var->{Message} = "The activation code you entered doesn't appear to be valid.  Please try again.";
    $var->{Form} = 1;
    $var->{ActivationCode} = $ActivationCode;
    sleep 10;
    &printForm;
  }
} else {
  $var->{Form} = 1;
  &printForm;
}


sub printForm {
  print $C->header(-cookie=>$authInfo->{cookie});
  $template->process("RegistrationForm.html",$var) or die $template->error;
  exit;
}
