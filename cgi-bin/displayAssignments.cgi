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
use CGI;
use lib ("../site_perl");
use Group;
use widgets;
use auth;
use User;
use Date::Calc qw(Today Delta_Days Add_Delta_YM Month_to_Text);
use Calendar::Simple;
use Data::Dumper;
our $C = CGI->new;
$ENV{TMPDIR} = "/tmp";
my @chars = ('A'..'Z','a'..'z',0..9);
my $config = Config::Simple->new("../etc/annie.conf");
our $dbh = &widgets::dbConnect($config);
my $authInfo = &auth::authenticated($dbh,\$C);
my $scriptdir = $config->param("server.scriptdirectory");
my $serverURL = $config->param("server.url");
my $docURL = $config->param("server.documenturl");
my $action = $C->param("action") || "";
my $docDir = $config->param("server.documentdirectory");
my $template = Template->new( RELATIVE => 1,
			       INCLUDE_PATH => "../templates");
my $GroupID = $C->param("GroupID") || "";
our $monthAdjustment = $C->param("mAdj") || 0;


if (!$authInfo->{LoggedIn}) {
  my $vars = { scriptdir => $scriptdir,
	       randomValue => &auth::randomValue(),
	       formAction => "displayAssignments.cgi",
	       hiddenVar => [ 
			     {paramName => "GroupID",paramValue => $GroupID}]
	       };
  print $C->header();
  $template->process("loginScriptForm.html",$vars) || die $template->error();
  exit;
}

if (!$action) {


  my $user = User->load( dbh => $dbh,
			 ID => $authInfo->{UserID});
  my $udd = $user->getDisplayData;
  my $gdd = &getGroups($user);
  my $detailURL = "";
  my $detail = "";
  my $vars = { 
	       GroupsWithAssignments => $gdd,
	       mAdj => $monthAdjustment,
	       User => $udd,
	       scriptdir => $scriptdir,
	       DetailURL => "assignmentDetails.cgi",
	       CloneURL => "addAssignment.cgi",
	       DeleteURL => "deleteAssignment.cgi",
	       EditURL => "editAssignment.cgi",
	       AddURL => "addAssignment.cgi",
	       EditLink => $user->hasPrivilege("Own.EditAssignment"),
	       DetailsLink => $user->hasPrivilege("Own.ViewAssignment"),
	       DeleteLink => $user->hasPrivilege("Own.DeleteAssignment"),
	       AddLink => $user->hasPrivilege("Own.AddAssignment"),
	       SuppressAssignments => 1};
  print $C->header(-cookie=>$authInfo->{cookie});
  $template->process("DisplayAssignments.html",$vars) || die $template->error();
  exit;
} elsif ($action eq "show_group") {
  my $user = User->load( dbh => $dbh,
			 ID => $authInfo->{UserID});
  my $groupID = $C->param("GroupID");
  my $gdd = &getGroups($user);
  my $udd = $user->getDisplayData;
  my $add = $user->getAssignmentDisplayData($groupID);
  my $calendar = &getCalendar($add);
  my $detailURL = "";
  my $detail = "";
  my $vars = { GroupID => $groupID,
	       Calendar => $calendar,
	       GroupsWithAssignments => $gdd,
	       mAdj => $monthAdjustment,
	       Assignments => $add,
	       User => $udd,
	       scriptdir => $scriptdir,
	       DetailURL => "assignmentDetails.cgi",
	       DeleteURL => "deleteAssignment.cgi",
	       CloneURL => "addAssignment.cgi",
	       EditURL => "editAssignment.cgi",
	       AddURL => "addAssignment.cgi",
	       EditLink => $user->hasPrivilege("Own.EditAssignment"),
	       DetailsLink => $user->hasPrivilege("Own.ViewAssignment"),
	       DeleteLink => $user->hasPrivilege("Own.DeleteAssignment"),
	       AddLink => $user->hasPrivilege("Own.AddAssignment")};
  print $C->header(-cookie=>$authInfo->{cookie});
  $template->process("DisplayAssignments.html",$vars) || die $template->error();
  
} 

sub getCalendar {
  my $add = shift;
  my ($y,$m,$d)= ();
  my ($yp,$mp,$dp) = ();
  my ($ym,$mm,$dm) = ();
  ($y,$m,$d) = Add_Delta_YM(Today,0,$monthAdjustment);
  ($yp,$mp,$dp) = Add_Delta_YM(Today,0,$monthAdjustment + 1);
  ($ym,$mm,$dm) = Add_Delta_YM(Today,0,$monthAdjustment - 1);
  my $calendar = {};
  $calendar->{$ym}{$mm} = calendar($mm,$ym);
  $calendar->{$y}{$m} = calendar($m,$y);
  $calendar->{$yp}{$mp} = calendar($mp,$yp);
  
  #   { Year => { Label => 2003,
  # 	      Months => [ { Label => 1,
  # 			    Weeks => [ [,1,2,3,4],[5,6,...]]}]}}
  my $rv = [];
  for my $year (sort { $a <=> $b } keys %{$calendar}) {
    my %year = ();
    $year{Label} = $year;
    for my $month (sort {$a <=> $b } keys %{$calendar->{$year}}) {
      my %month = ();
      $month{Label} = Month_to_Text($month);
      for my $week ( @{$calendar->{$year}{$month}}) {
	my @weekAry = ();
	for my $day (@{$week}) {
	  my %day = ();
	  $day{DayNumber} = $day;
	  my ($d,$m) = ();
	  if (defined $day) {$d =  sprintf "%02u", $day;};
	  $m = sprintf "%02u", $month;
	  for my $a (@{$add}) {
	    next unless defined $d;
	    if ($a->{DueDate} eq "$year-$m-$d") {
	      push @{$day{Assignment}}, {ID => $a->{ID},
					 Title => $a->{Title}};
	      $day{HasAssignments} = 1;
	    }
	  }
	  push @weekAry, \%day;
	}
	push @{$month{Weeks}}, \@weekAry;
      }
      push @{$year{Months}}, \%month;
    }
    push @{$rv}, \%year;
  }
  return $rv;

}
sub getGroups {
  my $user = shift;
  $user->loadGroups;
  my $groups = $user->getGroups;
  my @groupIDs = ();
  for my $group (@{$groups}) {
    push @groupIDs, $group->getGroupID;
  }
  my $sth = $dbh->prepare("SELECT ID FROM Assignment WHERE GroupID = ?");
  my $gdd = [];
  for my $gid (@groupIDs) {
    $sth->execute($gid);
    my $hasAssignments = 0;
    while (my ($id) = $sth->fetchrow_array) {
      $hasAssignments = 1;
    }
    if ($hasAssignments) {
      my $g = Group->load(dbh => $dbh,
			  GroupID => $gid);
      push @{$gdd}, $g->getDisplayData($user);
    }
  }
  return $gdd;
}
