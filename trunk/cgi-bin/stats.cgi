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
use AnnotateitConfig;
use widgets;
use auth;
use Data::Dumper;
use User;
use CGI;
our $C = CGI->new;

my $config = $AnnotateitConfig::C;
our ($dbh, $scriptdir, $serverURL, $action);
$scriptdir = $config->{server}{scriptdirectory};
$serverURL = $config->{server}{url};
$dbh = &widgets::dbConnect($config);
$action = $C->param("action");
my $authInfo= &auth::authenticated($dbh,\$C);
my $template = Template->new( RELATIVE => 1,
			      INCLUDE_PATH => "../templates");

unless ($authInfo->{LoggedIn}) {
  my $vars = {randomValue => &auth::randomValue(),
	      scriptdir => $scriptdir,
	      formAction => "stats.cgi" };
  print $C->header;
  $template->process("loginScriptForm.html",$vars) or die $template->error;
  exit;
}

my $user=User->load(ID => $authInfo->{UserID},
		    dbh => $dbh);
$user->loadGroups;
my $groups = $user->getGroups;
my $sth = $dbh->prepare("SELECT count(a.title), a.title, g.GroupName FROM annotation as a, GroupDefs as g WHERE a.GroupID = ? AND a.GroupID = g.GroupID GROUP BY title");
my $totals = {};
my $groupResults = {};
my $groupNames = {};
for my $group (@{$groups}) {
  my $groupID = $group->getGroupID;
  $sth->execute($groupID);
  while (my ($count, $title,$groupName) = $sth->fetchrow_array) {
    $groupResults->{$groupID}{$title} = $count;
    if (defined $totals->{$title}) {
      $totals->{$title} += $count;
    } else {
      $totals->{$title} = $count;
    }
    $groupNames->{$groupID} = $groupName;
  }
}
my @rvTotals;
for my $key (sort {$totals->{$b} <=> $totals->{$a}} keys %{$totals}) {
  push @rvTotals, { title=> $key, count => $totals->{$key} };
}
my $rvGroups = [];
for my $groupID (keys %{$groupResults}) {
  my $groupRV = { GroupName => $groupNames->{$groupID} };
  for my $title (sort { $groupResults->{$groupID}{$b} 
			  <=>
			    $groupResults->{$groupID}{$a}
			  } keys %{$groupResults->{$groupID}}) {
    push @{$groupRV->{Count}}, { title => $title,
				 count => $groupResults->{$groupID}{$title}, 
				 GroupName => $groupNames->{$groupID} };
  }
  push @{$rvGroups}, $groupRV;
}

my $vars = { Totals => \@rvTotals,
	     GroupCounts => $rvGroups };
print $C->header;
$template->process("Stats.html",$vars) or die $template->error;
exit;
