#!/usr/local/bin/perl -wT
# Copyright 2003, Buzzmaven Co.

# deletes predefined annotations and redirects
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
use IO::File;
use Assignment;
use Group;
use Date::Calc qw(Today Delta_Days );
use CGI;
our $C = CGI->new;
$ENV{TMPDIR} = "/tmp";
my @chars = ('A'..'Z','a'..'z',0..9);
our $config = Config::Simple->new("../etc/annie.conf");
our $dbh = &widgets::dbConnect($config);
our $authInfo = &auth::authenticated($dbh,\$C);
my $scriptdir = $config->param("server.scriptdirectory");
my $serverURL = $config->param("server.url");
my $docURL = $config->param("server.documenturl");
my $action = $C->param("action") || "";
my $docDir = $config->param("server.documentdirectory");
my $template = Template->new( RELATIVE => 1,
			       INCLUDE_PATH => "../templates");
my $GroupID = $C->param("GroupID") || "";
my $user = User->load( dbh => $dbh,
		       ID => $authInfo->{UserID});
if (! $user->hasPrivilege("Own.AddAssignment") 
    and ! $user->hasPrivilege("Other.AddAssignment") ) {
  &unauthorized("NoAddAssignmentGen");
}
if (!$authInfo->{LoggedIn}) {

  my $vars = { scriptdir => $scriptdir,
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
  my $groups = $user->getGroupDisplayData;
  my $udd = $user->getDisplayData;
  my $vars = { Title => "Assignment Saved",
	       scriptdir => $scriptdir,
	       formAction => "addAssignments.cgi",
	       Groups => $groups,
	       User => $udd};
  my $GroupID = &widgets::scrub($C->param("GroupID") || "");
  my $Title = &widgets::scrub($C->param("Title") || "");
  my $Description = &widgets::scrub('keeplinks',$C->param("Description") || "");
  my $YearDue = $C->param("YearDue") || "";
  $YearDue =~ s/[^\d]//;
  my $MonthDue = $C->param("MonthDue") || "";
  $MonthDue =~ s/[^\d]//;
  my $MDayDue = $C->param("MDayDue") || "";
  $MDayDue =~ s/[^\d]//;
  my $Weight = $C->param("Weight") || 1;
  $Weight =~ s/[^\d]//;
  my $BackPage = &widgets::scrub($C->param("BackPage") || "");
  my @evalVectorIDs = &widgets::scrub($C->param("EvalVector"));
  my @errors = ();
  my $deltaDays = eval { (Delta_Days(Today,$YearDue,$MonthDue,$MDayDue) < 1) };
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
  $vars->{SelectedGroup} = $GroupID;
  $vars->{Assignment}{Weight} = $Weight;
  $vars->{Assignment}{Title} = $Title;
  $vars->{Assignment}{Description} = $Description;
  $vars->{Assignment}{YearDue} = $YearDue;
  $vars->{Assignment}{MonthDue} = $MonthDue;
  $vars->{Assignment}{MDayDue} = $MDayDue;
  $vars->{BackPage} = $BackPage;
  if (@errors) {
    $vars->{Errors} = 1;
    $vars->{Success} = 0;
    $vars->{formAction} = $BackPage;
    $vars->{action} = $action;
  } else {
    $vars->{Success} = 1;
    $YearDue = sprintf "%04u", $YearDue;
    $MonthDue = sprintf "%02u", $MonthDue;
    $MDayDue = sprintf "%02u", $MDayDue;
    my $dueDate = "$YearDue-$MonthDue-$MDayDue";
    my $assignment = Assignment->new(dbh => $dbh);
    $assignment->setGroupID($GroupID);
    $assignment->setWeight($Weight);
    $assignment->setTitle($Title);
    $assignment->setUserID($authInfo->{UserID});
    $assignment->setDescription($Description);
    $assignment->setDueDate($dueDate);
    $assignment->save;
    $assignment->setEvalVectors(\@evalVectorIDs);
  }
  print $C->header(-cookie=>$authInfo->{cookie});
  $template->process("Assignments.html", $vars) or die $template->error();
  exit;
} else {
  my $assignmentID = $C->param("ID") || "";
  my $a = "";
  my $add = "";
  my %assignedVectors = ();
  my $title = "";
  if ($assignmentID) {
    $title = "Clone an Assignment";
    $a = Assignment->load(dbh => $dbh,
			  ID => $assignmentID);
    $add = $a->getDisplayData();
    my ($evalVectorIDs,$weights) = $a->getEvalVectorIDs;
    @assignedVectors{@{$evalVectorIDs}} = (1)x@{$evalVectorIDs};
  } else {
    $title = "Add an Assignment";
  }
  my $evdd = $user->getEvalVectorDisplayData;
  my $GroupName = "";
  if ($GroupID) {
    my $group = Group->load(dbh => $dbh,
			    GroupID => $GroupID);
    $GroupName = $group->getGroupName;
  }
  my $user = User->load( dbh => $dbh,
			 ID => $authInfo->{UserID} );
  my $groups = $user->getGroupDisplayData;
  my $udd = $user->getDisplayData;
  my $vars = { Title => $title,
	       scriptdir => $scriptdir,
	       Rubrics => $user->getRubricDisplayData,
	       AssignedRubricHash => {},
	       formAction => "addAssignment.cgi",
	       Assignment => $add,
	       AvailableEvalVectors => $evdd,
	       AssignedEvalVectors => \%assignedVectors,
	       action => "save",
	       BackPage => "addAssignment.cgi",
	       Groups => $groups,
	       User => $udd,
	       GroupID => $GroupID,
	       GroupName => $GroupName
	       };
  print $C->header(-cookie=>$authInfo->{cookie});
  $template->process("Assignments.html",$vars) or die $template->error();
}

exit;
sub unauthorized {
  my $error = @_;
  my $vars = {};
  $vars->{Error} = 'NotAuthorizedCreateAssignment';
  $vars->{EnglishError} = 'Not Authorized';

  print $C->header(-cookie=>$authInfo->{cookie});
  $template->process("Error.html",$vars) or die $template->error;
  exit;
}
