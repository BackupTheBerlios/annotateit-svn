#!/usr/local/bin/perl -wT
# Add an evaluation vector

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
use EvalVector;
use CGI;
our $C = CGI->new;


our $config = Config::Simple->new("../etc/annie.conf");
our ($dbh, $authInfo, $scriptdir, $serverURL);
$scriptdir = $config->param("server.scriptdirectory");
$serverURL = $config->param("server.url");
$dbh = &widgets::dbConnect($config);
$authInfo = &auth::authenticated($dbh,\$C);
our $template = Template->new( RELATIVE => 1,
			       INCLUDE_PATH => "../templates",
			       ERROR => "Error.html");

unless ($authInfo->{LoggedIn}) {
  my $vars = {scriptdir => $scriptdir,
	      randomValue => &auth::randomValue(),
	      formAction => "addEvaluationVector.cgi",
	     };
  print $C->header();
  $template->process("loginScriptForm.html",$vars );
  exit;
}
our $user = User->load( dbh => $dbh,
			ID => $authInfo->{UserID});
our $action = $C->param("action") || "";
if ($action eq "") {
  &printNewForm;
} elsif ($action eq "setValueNames") {
  &printValueNamesForm;
} elsif ($action eq "save") {
  &save;
}

exit;

sub printNewForm {
  my $vars = {User => $user->getDisplayData,
	      FormAction => "addEvaluationVector.cgi", 
	      scriptdir => $scriptdir,
	      Screen => "One",
	      Title => "Add An Evaluation Vector"};
  print $C->header(-cookie=>$authInfo->{cookie});
  $template->process("AddEvalVector.html",$vars) or die $template->error;
  exit;
}
sub printValueNamesForm {
  my $Title = &widgets::scrub($C->param("Title") || "Untitled");
  my $vars = {};
  $vars->{Error} = "";
  $vars->{EnglishError} = "";
  my $MinValue = &widgets::scrub($C->param("MinimumValue") || 0);
  if ($MinValue < 0 ) {
      $vars->{Error} = "AddEvalVectorMinValue";
      $vars->{EnglishError} = "Minimum value must be 0 or greater";
  }
  my $MaxValue = &widgets::scrub($C->param("MaximumValue") || 5);
  if ($MaxValue < 0 ) {
      $vars->{Error} = "AddEvalVectorMaxValue";
      $vars->{EnglishError} = "Maximum value must be 0 or greater";
  }
  my $Increment = &widgets::scrub($C->param("Increment") || 1);
  if ($Increment < 0 ) {
      $vars->{Error} = "AddEvalVectorIncrement";
      $vars->{EnglishError} = "Increment must be 0 or greater";
  }
  if ($vars->{Error}) {
      print $C->header;
      $template->process("Error.html", $vars) or die $template->error;
      exit;
  }
  $Increment ||= 1;
  my $Type = &widgets::scrub($C->param("Type") || "Radio");
  my $user = User->load(dbh => $dbh,
			ID => $authInfo->{UserID});
  my $ev = EvalVector->new( dbh => $dbh );
  $ev->Title($Title);
  $ev->MinimumValue($MinValue);
  $ev->MaximumValue($MaxValue);
  $ev->Increment($Increment);
  $ev->Type($Type);
  $ev->OwnerID($user->getID);
  $ev->save;
  my $dd = $ev->getDisplayData;
  $vars->{User} = $user->getDisplayData;
  $vars->{scriptdir} = $scriptdir;
  $vars->{FormAction} = "addEvaluationVector.cgi";
  $vars->{EV} = $dd;
  $vars->{Title} = "Assign Words to Values";
  $vars->{Screen} = "Two" ;
  print $C->header(-cookie =>$authInfo->{cookie});
  $template->process("AddEvalVector.html",$vars) or die $template->error;
  exit;
}

sub save {
  my $ID = $C->param("ID");
  my $user = User->load(dbh => $dbh,
			ID => $authInfo->{UserID});
  my $ev = EvalVector->load( dbh => $dbh,
			     ID => $ID );
  unless ($ev->isOwner($user)) {
    my $vars = { scriptdir => $scriptdir,
		 Error => "NotAuthorized",
		 EnglishError => "You are not the Owner of this Evaluation Vector" };
    print $C->header(-cookie => $authInfo->{cookie});
    $template->process("Error.html",$vars) or die $template->error;
    exit;
  }
  my @params = $C->param;
  foreach my $param (grep /ValueName_/, @params) {
    my ($value) = $param =~ /_(\d+)$/;
    my $name = &widgets::scrub($C->param($param));
    $ev->setValueName($value,$name);
  }
  $ev->update;
  my $vars = { EV => $ev->getDisplayData,
	       Screen => "Three",
	       FormAction => "addEvaluationVector.cgi",
	       Title => "Adding Evaluation Vector Complete",
	       scriptdir => $scriptdir };
  print $C->header(-cookie => $authInfo->{cookie});
  $template->process("AddEvalVector.html",$vars) or die $template->error;
  exit;
}
