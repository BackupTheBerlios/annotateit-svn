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
package AnnotationsSearch;
use strict;
use Annotation;
sub new {
  my ($class,%params) = @_;
  unless ($params{CurrentUser} and ref($params{CurrentUser}) eq "User") {
    warn "No CurrentUser passed:" . join ": ", caller();
    die;
  }
  my $self = \%params;
  bless $self, $class;
  return $self;
}

sub getResults {
  my ($self) = @_;
  my $UserID = $self->{UserID} || "";
  my $GroupID = $self->{GroupID} || "";
  my $URL = $self->{URL} || "";
  my $Title = $self->{Title} || "";
  my $FromDate = $self->{FromDate} || "";
  my $ToDate = $self->{ToDate} || "";
  my $phrase = $self->{Phrase} || "";
  my $auth = $self->{auth} || "";
  my $annotation = $self->{Annotation} || "";
  my $sql = "SELECT ID FROM annotation";
  my $user = $self->{CurrentUser} or die "User object must be passed due to security restrictions.";
  my (@params,@whereCond) = ();
  if (!$user->hasPrivilege("Other.SearchAnnotations") and 
      !$user->hasPrivilege("Own.SearchAnnotations")) {
    return [];
  } elsif ($user->hasPrivilege("Own.SearchAnnotations")) {
    $user->loadGroups;
    my $groups = $user->getGroups;
    my @gids = ();
    for my $group (@{$groups}) {
      push @gids, $group->getGroupID;
    }
    push @gids, "Public";
    my @quoted = map { "'$_'" } @gids;
    my $gids = join ", ", @quoted;
    push @params, $user->getID;
    push @whereCond, "((GroupID IN ($gids)) OR (GroupID = 'Private' AND UserID = ?))";
  }
  if ($annotation) {
    push @params, $annotation;
    push @whereCond, "annotation RLIKE ?";
  }
  if ($UserID) {
    push @params, $UserID;
    push @whereCond, "UserID = ?";
  }
  if ($GroupID and $GroupID ne "Private") {
    push @params, $GroupID;
    push @whereCond, "GroupID = ?";
  }
  if ($URL) {
    push @params, $URL;
    push @whereCond, "url RLIKE ?";
  }
  if ($Title) {
    push @params, $Title;
    push @whereCond, "title RLIKE ?";
  }
  if ($FromDate) {
    push @params, $FromDate;
    push @whereCond, "Time >= ?";
  }
  if ($ToDate) {
    push @params, $ToDate;
    push @whereCond, "Time <= ?";
  }
  if ($phrase) {
    push @params, $phrase;
    push @whereCond, "phrase RLIKE ?";
  }
  if (@params) {
    $sql .= " WHERE " . join " AND ", @whereCond;
  }
  my $sth = $self->{dbh}->prepare($sql);
  $sth->execute(@params);
  my @rv = ();
  while (my ($id) = $sth->fetchrow_array) {
    my $a = Annotation->load(dbh => $self->{dbh},
			     ID => $id);
    push @rv, $a->getDisplayData({CurrentUser => $self->{CurrentUser}});
  }
  return \@rv;
}













1;
