#!/usr/local/bin/perl -w
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


my $config = Config::Simple->new("../etc/annie.conf");
our ($dbh, $authInfo, $scriptdir, $serverURL);
$scriptdir = $config->param("server.scriptdirectory");
$serverURL = $config->param("server.url");
$dbh = &widgets::dbConnect($config);
$authInfo = &auth::authenticated($dbh,\$C);
my $template = Template->new( RELATIVE => 1,
			      INCLUDE_PATH => "../templates" );

unless ($authInfo->{LoggedIn}) {
  my $vars = {scriptdir => $scriptdir,
	      randomValue => &auth::randomValue(),
	      formAction => "manageEvalVectors.cgi",
	     };
  print $C->header();
  $template->process("loginScriptForm.html",$vars );
  exit;
}
my $user = User->load(dbh => $dbh,
		      ID => $authInfo->{UserID});
my $action = $C->param("action") || "";
if ($action eq "") {
  &printList;
} elsif ($action eq "Edit") {
  &printEditForm;
} elsif ($action eq "setValueNames") {
  &printValueNamesForm;
} elsif ($action eq "save") {
  &save;
} elsif ($action eq "Delete") {
    &previewDelete;
} elsif ($action eq "ConfirmDelete") {
    &confirmDelete;
}

exit;

sub printList {
  my $vars = { User => $user->getDisplayData, 
	      scriptdir => $scriptdir,
	       Screen => "List",
	       AvailableEvalVectors => $user->getEvalVectorDisplayData,
	       Title => "Edit An Evaluation Vector"};
  print $C->header(-cookie=>$authInfo->{cookie});
  $template->process("AddEvalVector.html",$vars) or die $template->error;
  exit;
}
sub printEditForm {
  my $evID = $C->param("EvalVectorID");
  $evID =~ s/[^\d]//g;
  my $ev = EvalVector->load( dbh => $dbh,
			     ID => $evID );
  &checkOwnership($ev);
  my $edd = $ev->getDisplayData;
  my $title = $ev->Title;
  my $vars = { scriptdir => $scriptdir,
	       Screen => "One",
	       FormAction => "manageEvalVectors.cgi",
	       Title => "Edit $title (Evaluation Vector)",
	       EV => $edd };
  print $C->header(-cookie=>$authInfo->{cookie});
  $template->process("AddEvalVector.html",$vars) or die $template->error;
  exit;
}
sub printValueNamesForm {
  my $Title = &widgets::scrub($C->param("Title") || "Untitled");
  my $MinValue = $C->param("MinimumValue") || 0;
  $MinValue =~ s/[^\d]//g;
  my $MaxValue = $C->param("MaximumValue") || 5;
  $MaxValue =~ s/[^\d]//g;
  my $Increment = $C->param("Increment") || 1;
  $Increment =~ s/[^\d]//g;
  $Increment ||= 1;
  my $Type = $C->param("Type") || "Radio";
  my $EvalVectorID = $C->param("EvalVectorID");
  $EvalVectorID =~ s/[^\d]//g;
  my $user = User->load(dbh => $dbh,
			ID => $authInfo->{UserID});
  my $ev = EvalVector->load( dbh => $dbh,
			     ID => $EvalVectorID);
  &checkOwnership($ev);
  $ev->Title($Title);
  $ev->MinimumValue($MinValue);
  $ev->MaximumValue($MaxValue);
  $ev->Increment($Increment);
  $ev->Type($Type);
  $ev->OwnerID($user->getID);
  $ev->update;
  my $dd = $ev->getDisplayData;
  my $vars = { scriptdir => $scriptdir,
	       EV => $dd,
	       Title => "Assign Words to Values",
	       FormAction => "manageEvalVectors.cgi",
	       Screen => "Two" };
  print $C->header(-cookie =>$authInfo->{cookie});
  $template->process("AddEvalVector.html",$vars) or die $template->error;
  exit;
}

sub save {
  my $ID = $C->param("ID");
  $ID =~ s/[^\d]//g;
  my $user = User->load(dbh => $dbh,
			ID => $authInfo->{UserID});
  my $ev = EvalVector->load( dbh => $dbh,
			     ID => $ID );
  &checkOwnership($ev);
  my @params = $C->param;
  foreach my $param (grep /ValueName_/, @params) {
    my ($value) = $param =~ /_(\d+)$/;
    my $name = &widgets::scrub($C->param($param));
    $ev->setValueName($value,$name);
  }
  $ev->update;
  my $vars = { EV => $ev->getDisplayData,
	       Screen => "Three",
	       Title => "Adding Evaluation Vector Complete",
	       scriptdir => $scriptdir };
  print $C->header(-cookie => $authInfo->{cookie});
  $template->process("AddEvalVector.html",$vars) or die $template->error;
  exit;
}
sub previewDelete {
    my $evid = $C->param("EvalVectorID") || "";
    $evid =~ s/[^\d]//g;
    &checkEvid($evid);

    my $ev = EvalVector->load( ID => $evid,
			       dbh => $dbh);
    
    &checkOwnership($ev);    
    # deleting an eval vector can cause havoc.  Make sure that the user is
    # aware:
    # Check object map table both ways:
    my $sth = $dbh->prepare("SELECT ToObjectID,ToObjectClass FROM ObjectMap WHERE FromObjectID = ? AND FromObjectClass = 'EvalVector'");
    $sth->execute($evid);
    my @Objects = ();
    while (my ($oid,$oclass) = $sth->fetchrow_array) {
	push @Objects, {ID => $oid, Class=>$oclass};
    }
    
    $sth = $dbh->prepare("SELECT FromObjectID,FromObjectClass FROM ObjectMap WHERE ToObjectID = ? AND ToObjectClass = 'EvalVector'");
    $sth->execute($evid);
    while (my ($oid,$oclass) = $sth->fetchrow_array) {
	push @Objects, {ID => $oid, Class=>$oclass};
    }
    # check the Evaluation Table

    $sth = $dbh->prepare("SELECT ObjectID FROM Evaluation WHERE EvalVectorID = ?");
    $sth->execute($evid);
    while (my ($oid) = $sth->fetchrow_array) {
	push @Objects, {ID => $oid, Class=>"Evaluation"};
    }
    my $vars = {};
    $vars->{User} = $user->getDisplayData;
    $vars->{AffectedObjects} = \@Objects;
    $vars->{EV} = $ev->getDisplayData;
    $vars->{Screen} = "One";
    $vars->{Title} = "Deleting Evaluation Vector (Preview)";
    $vars->{scriptdir} = $scriptdir ;
    print $C->header(-cookie => $authInfo->{cookie});
    $template->process("DeleteEvalVector.html",$vars) or die $template->error;
    exit;
    
}
sub confirmDelete {
    my $evid = $C->param("EvalVectorID") || "";
    $evid =~ s/[^\d]//g;
    &checkEvid($evid);
    my $ev = EvalVector->load(dbh => $dbh,
			   ID => $evid);
    &checkOwnership($ev);
    $ev->delete;
    my $vars = { Screen => "Two",
		 Title => "Evaluation Vector Successfully Deleted",
		 scriptdir => $scriptdir };
    print $C->header;
    $template->process("DeleteEvalVector.html",$vars) or die $template->error;
    exit;
	
}
sub checkEvid {
    my $evid = shift;
    unless ($evid) {
	my $vars = { scriptdir => $scriptdir,
		     Error => "NoEVIDPassed",
		     EnglishError => "You didn't pass an evaluation vector to the script.  Something must be broken." };
	
	print $C->header(-cookie => $authInfo->{cookie});
	$template->process("Error.html",$vars) or die $template->error;
	exit;
    }
}

sub checkOwnership {
    my $ev = shift;
    my $user = User->load(dbh => $dbh,
			  ID => $authInfo->{UserID});
    
    unless ($ev->isOwner($user)) {
	my $vars = { scriptdir => $scriptdir,
		     Error => "NotAuthorized",
		     EnglishError => "You are not the Owner of this Evaluation Vector" };
	
	print $C->header(-cookie => $authInfo->{cookie});
	$template->process("Error.html",$vars) or die $template->error;
	exit;
    }   
} 
