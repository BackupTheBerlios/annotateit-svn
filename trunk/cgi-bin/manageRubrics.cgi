#!/usr/local/bin/perl -wT
# Rubric management
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
use Rubric;
use Data::Dumper;
use CGI;
our $C = CGI->new;

our $config = $AnnotateitConfig::C;
our ($template,$dbh, $authInfo, $scriptdir) = ();
$scriptdir = $config->{server}{scriptdirectory};
$dbh = &widgets::dbConnect($config);
$authInfo = &auth::authenticated($dbh,\$C);
$template = Template->new( INCLUDE_PATH => "../templates",
			   RELATIVE => 1);

if (!$authInfo->{LoggedIn}) {
  my $vars = {scriptdir => $scriptdir,
	      randomValue => &auth::randomValue,
	      formAction => "login.cgi" };
  print $C->header;
  $template->process("loginScriptForm.html",$vars) or die $template->error();
  exit;
}

our $action = $C->param("action");
our $user = User->load(dbh => $dbh,
		      ID => $authInfo->{UserID});
our $vars = {};
$vars->{User} = $user->getDisplayData;
$vars->{AvailableEvalVectors} = $user->getEvalVectorDisplayData();
$vars->{Rubrics} = $user->getRubricDisplayData;
$vars->{scriptdir} = $scriptdir;
if (!(defined $action and $action) ) {
  &noParams();
} elsif ($action eq "add") {
  &add();
} elsif ($action eq "edit") {
  &edit();
} elsif ($action eq "delete") {
  &delete();
} elsif ($action eq "save") {
  &save();
} elsif ($action eq "deleteConfirmed") {
  &noParams();
}
exit;
sub noParams {
  $vars->{Title} = "Manage Rubrics";
  $vars->{Screen} = "Default";
  print $C->header;
  $template->process("ManageRubrics.html",$vars) or die $template->error();
  exit;
}
sub add {
  $vars->{Title} = "Add A Rubric";
  $vars->{Screen} = "Add";
  print $C->header;
  $template->process("ManageRubrics.html",$vars) or die $template->error();
}
sub edit {
  $vars->{Title} = "Edit A Rubric";
  $vars->{Screen} = "Edit";
  my $rid = $C->param("ID") || "";
  unless (defined $rid and $rid) {
    warn "No ID passed";
    &noParams;
  }
  my $r = Rubric->load( dbh => $dbh,
			ID => $rid );
  $vars->{Rubric} = $r->getDisplayData;
  $vars->{AssignedEvalVectors} = $r->getObjectEvalVectorIDHash({User => $user});
  $vars->{AssignedEvalVectorWeights} = $r->getObjectEvalVectorWeightsHash({User => $user });
  print $C->header;
  $template->process("ManageRubrics.html",$vars) or die $template->error();
}
sub delete {
  my $rid = $C->param("ID") || "";
  &noParams unless $rid;
  my $r = Rubric->load( dbh => $dbh,
			ID => $rid);
  $vars->{Rubric} = $r->getDisplayData;
  $vars->{Title} = "Delete Rubric";
  $vars->{Screen} = "Delete";
  $vars->{EvalVectors} = $r->getEvalVectorDisplayData({Secure => "1"});
  print $C->header;
  $template->process("ManageRubrics.html",$vars) or die $template->error();
}
sub save {
  $vars->{Screen} = "Save";
  my $rid = $C->param("ID") || "";
  my $r = "";
  if ($rid) {
    $r = Rubric->load( dbh => $dbh,
		       ID => $rid);
  } else {
    $r = Rubric->new( dbh => $dbh );
  }
  my $title = widgets::scrub($C->param("Title"));
  my $type = widgets::scrub($C->param("Type"));
  $r->Type($type);
  $r->Title($title);
  $r->OwnerID($user->getID);
  if ($rid) {
    $r->update;
  } else {
    $r->save;
  }
  my @evIDs = $C->param("EvalVector");
  my $associatedEVs = [];
  for my $evID (@evIDs) {
    my $weight = $C->param("Weight_$evID");
    push @{$associatedEVs}, { ID => $evID,
			      Weight => $weight };
  }
  $r->setObjectEvalVectors({AssociatedEvalVectors => $associatedEVs,
			   User => $user});
  $vars->{Title} = "Rubric Saved";
  print $C->header;
  $template->process("ManageRubrics.html",$vars) or die $template->error();

}



$vars->{Groups} = $user->getGroupDisplayData;
$vars->{scriptdir} = $scriptdir;
$vars->{searchAnnotationsLink} = "searchAnnotations.cgi";
print $C->header;
$template->process("manageUserInfo.html",$vars) or die $template->error();
exit;



