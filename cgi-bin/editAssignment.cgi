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
use CGI;
use auth;
use User;
use Assignment;
use Date::Calc qw(Today Delta_Days );
our $C = CGI->new;
$ENV{TMPDIR} = "/tmp";
my @chars = ('A'..'Z','a'..'z',0..9);
my $config = Config::Simple->new("../etc/annie.conf");
my $dbh = &widgets::dbConnect($config);
my $authInfo = &auth::authenticated($dbh,\$C);
my $scriptdir = $config->param("server.scriptdirectory");
my $serverURL = $config->param("server.url");
my $docURL = $config->param("server.documenturl");
my $action = $C->param("action") || "";
my $docDir = $config->param("server.documentdirectory");
my $ID = $C->param("ID");
my $vars = {};
my $template = Template->new( RELATIVE => 1,
			       INCLUDE_PATH => "../templates");

if (!$authInfo->{LoggedIn}) {
  $vars = { scriptdir => $scriptdir,
	       randomValue => &auth::randomValue(),
	       formAction => "addAssignment.cgi",
	       hiddenVar => [ 
			     {paramName => "action",paramValue => $action}]
	       };
  print $C->header();
  $template->process("loginScriptForm.html",$vars) || die $template->error();
  exit;
}
if ($action eq "save") {
    &save;
} else {
    &noParams();
}
print $C->header(-cookie=>$authInfo->{cookie});
$template->process("Assignments.html", $vars) or die $template->error();

exit;
sub noParams {
    my $user = User->load( dbh => $dbh,
			   ID => $authInfo->{UserID} );
    my $groups = $user->getGroupDisplayData;
    my $udd = $user->getDisplayData;
    my $assignment = Assignment->load( dbh => $dbh,
				       ID => $ID );
    my ($evalVectorIDs,$evalVectorWeights) = $assignment->getEvalVectorIDs;
    my %assignedVectors = ();
    @assignedVectors{@{$evalVectorIDs}} = (1)x@{$evalVectorIDs};
    my $add = $assignment->getDisplayData;
    $vars = { Title => "Edit an Assignment", 
	      scriptdir => $scriptdir,
	      formAction => "editAssignment.cgi",
	      action => "save",
	      BackPage => "editAssignment.cgi",
	      Groups => $groups,
	      User => $udd,
	      Assignment => $add,
	      Rubrics => $user->getRubricDisplayData,
	      AssignedRubricHash => $assignment->getRubricIDsHash({User => $user}),
	      AssignedEvalVectors => \%assignedVectors,
	      AssignedEvalVectorWeights => $evalVectorWeights,
	      AvailableEvalVectors => $user->getEvalVectorDisplayData
	      };
    
}
sub save {
    my $user = User->load( dbh => $dbh,
			   ID => $authInfo->{UserID} );
    my $groups = $user->getGroupDisplayData;
    my $udd = $user->getDisplayData;
    
    $vars = { Title => "Changes saved",
	      scriptdir => $scriptdir,
	      formAction => "addAssignments.cgi",
	      Groups => $groups,
	      User => $udd};
    my @EvalVectorIDs = &widgets::scrub($C->param("EvalVector"));
    my @RubricIDs = &widgets::scrub($C->param("RubricID"));
    my %evHash = ();
    for my $evid (@EvalVectorIDs) {
      $evHash{$evid} = &widgets::scrub($C->param("Weight_$evid")) || 1;
    }
    my $GroupID = $C->param("GroupID") || "";
    my $Title = &widgets::scrub($C->param("Title") || "");
    my $Description = &widgets::scrub("keeplinks",$C->param("Description") || "");
    my $YearDue = $C->param("YearDue") || "";
    $YearDue =~ s/[^\d]//g;
    my $MonthDue = $C->param("MonthDue") || "";
    $MonthDue =~ s/[^\d]//g;
    my $MDayDue = $C->param("MDayDue") || "";
    $MDayDue =~ s/[^\d]//g;
    my $Weight = $C->param("Weight") || 1;
    $Weight =~ s/[^\d]//g;
    my $BackPage = $C->param("BackPage") || "";
    my @errors = ();
    my $deltaDays = eval { (Delta_Days(Today,$YearDue,$MonthDue,$MDayDue) < 1) };
    my $assignment = Assignment->load( dbh => $dbh,
				       ID => $ID );
    my ($evalVectorIDs,$evalVectorWeights) = $assignment->getEvalVectorIDs;
    my %assignedVectors = ();
    @assignedVectors{@{$evalVectorIDs}} = (1)x@{$evalVectorIDs};
    if  (! defined $deltaDays ) { # error from delta days
	push @errors, {Value => "That is not a valid date."};
    } elsif ($deltaDays ) { 
	push @errors, {Value => "There is not enough time to complete the assignment."};
    }
    if (! $GroupID ) {
	push @errors, {Value => "No group was assigned."};
    }
    if (! $Title ) {
	push @errors, {Value => "No title was recorded."};
    }
    if (! $Description) {
	push @errors, {Value => "No description was recorded."};
    }
    $vars->{Error} = \@errors;
    $vars->{Assignment}{ID} = $ID if (defined $ID and $ID);
    $vars->{Assignment}{GroupID} = $GroupID;
    $vars->{Assignment}{Title} = $Title;
    $vars->{Assignment}{Description} = $Description;
    $vars->{Assignment}{YearDue} = $YearDue;
    $vars->{Assignment}{MonthDue} = $MonthDue;
    $vars->{Assignment}{MDayDue} = $MDayDue;
    $vars->{Assignment}{Weight} = $Weight;
    $vars->{BackPage} = $BackPage;
    if (@errors) {
	$vars->{Errors} = 1;
	$vars->{Success} = 0;
	$vars->{formAction} = $BackPage;
	$vars->{action} = $action;
	$vars->{AssignedEvalVectors} = \%assignedVectors;
	$vars->{AssignedEvalVectorWeights} = $evalVectorWeights;
	$vars->{AvailableEvalVectors} = $user->getEvalVectorDisplayData;
	$vars->{Rubrics} = $user->getRubricDisplayData;
    } else {
	$vars->{Success} = 1;
	$YearDue = sprintf "%04u", $YearDue;
	$MonthDue = sprintf "%02u", $MonthDue;
	$MDayDue = sprintf "%02u", $MDayDue;
	my $dueDate = "$YearDue-$MonthDue-$MDayDue";
	my $assignment = Assignment->load( dbh => $dbh,
					   ID => $ID );
	$assignment->setGroupID($GroupID);
	$assignment->setTitle($Title);
	$assignment->setUserID($authInfo->{UserID});
	$assignment->setDescription($Description);
	$assignment->setDueDate($dueDate);
	$assignment->setWeight($Weight);
	$assignment->setEvalVectors(\%evHash);
	$assignment->setRubricIDs({User => $user,
				   RubricIDs => \@RubricIDs});
	$assignment->update;
	
    }
    $vars->{displayAssignmentsQuery} = 	"action=show_group&GroupID=" . $assignment->getGroupID,
}
