#!/usr/local/bin/perl -wT
##############################################
## This manages the user's documents
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
use Document;
use User;
use CGI;
our $C = CGI->new;
my $config = $AnnotateitConfig::C;
our ($dbh, $authInfo,$scriptdir,$cgiDir, $docDir, $serverURL,$docURL);
$scriptdir = $config->{server}{scriptdirectory};
$serverURL = $config->{server}{url};
$cgiDir = $serverURL  . $scriptdir;
$docDir = $config->{server}{documentdirectory};
$docURL = $config->{server}{documenturl};
$dbh = &widgets::dbConnect($config);
$authInfo = &auth::authenticated($dbh,\$C);
my $docID = $C->param("DocumentID");
our $action = $C->param("action") || "";
my $template = Template->new( RELATIVE => 1,
			      INCLUDE_PATH => "../templates" );

unless ($authInfo->{LoggedIn}) {
  my $vars = { formAction => "evaluateDocument.cgi",
	       scriptdir => $scriptdir,
	       randomValue => &auth::randomValue(),
	     };
  print $C->header;
  $template->process("loginScriptForm.html",$vars) or die $template->error;
  exit;
}
my $user = User->load(dbh => $dbh,
		      ID => $authInfo->{UserID});
my $doc = Document->load(dbh => $dbh,
			 ID => $docID);
unless (
	($user->hasRole("Admin") 
	 || $user->hasRole("Teacher") 
	 || $user->hasRole("Researcher"))
	 || 
	($user->getID eq $doc->OwnerID)
       ) {
  my $vars = { scriptdir => $scriptdir,
	       Error => "NotAuthorized",
	       EnglishError => "You are not authorized to view that document's evaluations" };
  print $C->header(-cookie => $authInfo->{cookie});
  $template->process("Error.html",$vars) or die $template->error;
  exit;
}
	
	
	
my @params = $C->param;
my %evals = ();

for my $param (grep /^EV_/, @params) {
  my $value = &widgets::scrub($C->param($param));
  my ($evID) = $param =~ /^EV_(\d+)$/; 
  $evals{$evID} = $value;
}
my $docEval = $doc->getEvaluations;
my $userEvals = {};
for my $userEval (@{$docEval}) {
  my $title = $userEval->{Title};
  my $value = $userEval->{EvaluationValue};
  my $evaluatorID = $userEval->{EvaluatorID};
  $evaluatorID ||= " ";
  push @{$userEvals->{$evaluatorID}{Evaluations}}, { Title => $title,
						     EvaluationValue => $value };
}

for my $userID (keys %{$userEvals}) {
  if ($userID eq " ") {
    $userEvals->{$userID}{EvaluatorName} = " ";
  } else {
    my $user = User->load(dbh => $dbh,
			  ID => $userID);
    $userEvals->{$userID}{EvaluatorName} = $user->getFirstName . " " .$user->getLastName;
  }
}

my $evals = [];
for my $userID (keys %{$userEvals}) {
  push @{$evals}, $userEvals->{$userID};
}

my $vars = { scriptdir => $scriptdir,
	     Document => $doc->getDisplayData(Config => $config),
	     Title => "Evaluations",
	     Evaluations => $evals,
	     Screen => 2};
print $C->header(-cookie => $authInfo->{cookie});
$template->process("viewDocumentEvaluations.html",$vars) or die $template->error;
exit;
	




