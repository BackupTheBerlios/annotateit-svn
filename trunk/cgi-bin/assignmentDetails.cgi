#!/usr/local/bin/perl -wT
# Copyright 2003, Buzzmaven
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
use CGI;
use auth;
use User;
use Rubric;
use IO::File;
use Assignment;
use EvalVector;
use Date::Calc qw(Today Delta_Days );
$ENV{TMPDIR} = "/tmp";
our $C = CGI->new();
my @chars = ('A'..'Z','a'..'z',0..9);
my $config = $AnnotateitConfig::C;
our $dbh = &widgets::dbConnect($config);
our $authInfo = &auth::authenticated($dbh,\$C);
our $scriptdir = $config->{server}{scriptdirectory};
our $serverURL = $config->{server}{url};
our $docURL = $config->{server}{documenturl};
our $docDir = $config->{server}{documentdirectory};
my $action = $C->param("action") || "";

our $template = Template->new( RELATIVE => 1,
			       INCLUDE_PATH => "../templates");
my $ID = $C->param("ID");
if (!$authInfo->{LoggedIn}) {
  my $vars = { scriptdir => $scriptdir,
	       randomValue => &auth::randomValue(),
	       formAction => "assignmentDetails.cgi",
	       hiddenVar => [{name => "action", value => $action},
			     {name => 'ID', value => $ID}]
	       };
  print $C->header();
  $template->process("loginScriptForm.html",$vars) || die $template->error();
  exit;
}
our $user = User->load( dbh => $dbh,
		       ID => $authInfo->{UserID} );
my $groups = $user->getGroupDisplayData;
my $udd = $user->getDisplayData;
our $assignment = Assignment->load( dbh => $dbh,
				   ID => $ID );
&checkAuth();
my ($evalVectorIDs,$evalVectorWeights) = $assignment->getEvalVectorIDs;
my @vectors = ();
for my $id (@{$evalVectorIDs}) {
  my $ev = EvalVector->load(ID => $id,
			    dbh => $dbh);
  my $dd = $ev->getDisplayData;
  $dd->{Weight} = $evalVectorWeights->{$id};
  push @vectors, $dd;
}
my $rubrics = $assignment->getRubricIDs({Secure => 1});
my $revdd = [];
for my $id (@{$rubrics}) {
  my $r = Rubric->load(dbh => $dbh,
		       ID => $id);
  my $evdd = $r->getEvalVectorDisplayData({Secure => 1});
  push @{$revdd}, @{$r->getEvalVectorDisplayData({Secure => 1})};
}
my $add = $assignment->getDisplayData;
my $docDD = $assignment->getDocumentsDisplayData($user);
our $vars = { scriptdir => $scriptdir,
	     serverurl => $serverURL,
	     formAction => "assignmentDetails.cgi",
	     action => "save",
	     Document => $docDD,
	     BackPage => "editAssignment.cgi",
	     Groups => $groups,
	     isOwner => ($assignment->getUserID == $user->getID),
	     User => $udd,
	     Assignment => $add,
	     RubricEvalVectors => $revdd,
	     Rubrics => $assignment->getRubricDisplayData({Secure => 1}),
	     EvalVectors => \@vectors,
	     Title => "Assignment Details",
	     CanUpload => $user->hasPrivilege("Own.UploadDocument"),
	     CanViewStats => $user->hasPrivilege("Own.ViewStatistics") || $user->hasPrivilege("Other.ViewStatistics"),
	     CanViewAssignmentStats => $user->hasPrivilege("Own.AssignmentStatistics") || $user->hasPrivilege("Other.AssignmentStatistics")
	};
if (@{$docDD}) {
  $vars->{HasDocuments} = 1;
}

print $C->header(-cookie => $authInfo->{cookie});
$template->process("AssignmentDetails.html",$vars) || die $template->error;
exit;

sub checkAuth {
  my $aGID = $assignment->getGroupID;
  my $aUID = $assignment->getUserID;
  if (
      (
       ( $user->getID == $aUID 	 or $user->hasGroup($aGID)
       )
       and $user->hasPrivilege("Own.ViewAssignment")
      ) or $user->hasPrivilege("Other.ViewAssignment")
     ) {
    $vars->{Assignment} = $assignment->getDisplayData;
  } else {
    my $vars = { EnglishError => "Unauthorized",
		 Error => 'NotAuthorizedDisplayAssignment',
		 BackPage => 'displayAssignments.cgi',
		 serverurl => $serverURL,
		 scriptdir => $scriptdir };
    print $C->header(-cookie => $authInfo->{cookie});
    $template->process("Error.html",$vars) || die $template->error;
    exit;
  }
}
