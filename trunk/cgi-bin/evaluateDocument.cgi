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
use Config::Simple qw( -strict );
use lib ("../site_perl");
use widgets;
use auth;
use Document;
use User;
use Assignment;
use CGI;
our $C = CGI->new;

our $config = Config::Simple->new("../etc/annie.conf");
our ($dbh, $authInfo,$scriptdir,$cgiDir, $docDir, $serverURL,$docURL);
$scriptdir = $config->param("server.scriptdirectory");
$serverURL = $config->param("server.url");
$cgiDir = $serverURL  . $scriptdir;
$docDir = $config->param("server.documentdirectory");
$docURL = $config->param("server.documenturl");
$dbh = &widgets::dbConnect($config);
$authInfo = &auth::authenticated($dbh,\$C);
our $docID = $C->param("DocumentID");
our $action = $C->param("action") || "";
our $template = Template->new( RELATIVE => 1,
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
our $user = User->load(dbh => $dbh,
		     ID => $authInfo->{UserID});
unless ($user->hasRole("Admin") || $user->hasRole("Teacher") || $user->hasRole("Researcher")) {
 my $vars = { scriptdir => $scriptdir,
	      Error => "NotAuthorized",
	      EnglishError => "You are not authorized to evaluate documents"};
 print $C->header(-cookie => $authInfo->{cookie});
 $template->process("Error.html",$vars) or die $template->error;
 exit;
}

if ($action eq 'save') {
  &saveEvaluation;
} elsif ($action eq "") {
  &noParams;
}
sub noParams {

  my $doc = Document->load(dbh => $dbh,
			   ID => $docID);
  my $evIDs = $doc->getEvalVectorIDs;
  my $noEvalVectors = 1;
  if (@{$evIDs}) {
    $noEvalVectors = 0;
  }
  my $vars = {noEvalVectors => $noEvalVectors,
	      User => $user->getDisplayData,
	      Document => $doc->getDisplayData(Config=>$config),
	       scriptdir => $scriptdir,
	       Title => "Evaluate Document",
	       Screen => 1};
  print $C->header( -cookie=>$authInfo->{cookie});
  $template->process("EvaluateDocument.html",$vars) or die $template->error;
  exit;
}

sub saveEvaluation {
  my @params = $C->param;
  my @evals = ();
  for my $param (grep /^EV_/, @params) {
    my $value = &widgets::scrub($C->param($param));
    my ($evID,$weight) = $param =~ /^EV_(\d+)_Weight_(\d+)$/;
    push @evals, {ID => $evID,
		  Value => $value,
		  Weight => $weight};
  }
  my $doc = Document->load(dbh => $dbh,
			   ID => $docID);
  $doc->setEvaluation({CurrentUser => $user,
		       Evaluation => \@evals});
  my $evaluations = $doc->getEvaluations;
  my $vars = { scriptdir => $scriptdir,
	       Title => "Evaluation Saved",
	       Evaluations => $doc->getEvaluations,
	       Screen => 2};
  print $C->header(-cookie => $authInfo->{cookie});
  $template->process("EvaluateDocument.html",$vars) or die $template->error;
  exit;
}




