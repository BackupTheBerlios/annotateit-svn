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
package Clickthrough;
use strict;

sub new {

  my ($class,%params) = @_;
  my $self = \%params;
  bless $self, $class;
  my $sth = $self->{dbh}->prepare("INSERT INTO Clickthrough (AnnotationID, UserID) VALUES (?,?)");
  $sth->execute($self->{AnnotationID},
		$self->{UserID});
  $self->setID($self->{dbh}->{mysql_insertid});
  return $self;
}
sub getAnnotationID {
  my ($self) = @_;
  my $v = $self->{AnnotationID};
  return $v;
}
sub getUserID {
  my ($self) = @_;
  my $v = $self->{UserID};
  return $v;
}
sub getID {
  my ($self) = @_;
  my $v = $self->{ID};
  return $v;
}

sub setAnnotationID {
  my ($self,$v) = @_;
  $self->{AnnotationID} = $v;
}
sub setUserID {
  my ($self,$v) = @_;
  $self->{UserID} = $v;
}
sub setID {
  my ($self,$v) = @_;
  $self->{ID} = $v;
}
sub save { warn join ': ', caller(); die 'save not implemented'; }
sub load { warn join ': ', caller(); die 'load not implemented'; }
sub update { warn join ': ', caller(); die 'update not implemented'; }
sub delete { warn join ': ', caller(); die 'delete not implemented'; }

sub getDisplayData {

  my ($class, %params) = @_;
  my $self = \%params;
  bless $self, $class;
  unless (defined $self->{dbh}) {
    warn "No DBH passed: " . join ": ", caller();
    die;
  }
  unless (defined $self->{CurrentUser} and ref($self->{CurrentUser}) eq "User") {
    warn "No CurrentUser passed: " . join ": ", caller();
    die;
  }
  my $ownedGroups = $self->{CurrentUser}->groupsOwned;
  my @params = ();
  my @qmarks = ();
  for my $gid (@{$ownedGroups}) {
    push @params, $gid;
    push @qmarks, "?";
  }
  my $qmarks = "";
  if (@qmarks) {
    $qmarks = "OR A.GroupID IN (" . (join ",", @qmarks) . ")";
  }
  my $sth = $self->{dbh}->prepare("SELECT U.name, COUNT(U.name) FROM Clickthrough as C, user as U, annotation as A WHERE C.UserID = U.ID AND A.ID = AnnotationID AND C.UserID != A.UserID AND C.AnnotationID = ? AND (A.UserID = ? $qmarks) GROUP BY U.name ");
  $sth->execute($self->{AnnotationID},$self->{CurrentUser}->getID,@params);
  my @rv = ();
  while (my ($name,$count) = $sth->fetchrow_array) {
    push @rv, { UserName => $name,
		Clickthroughs => $count };
  }
  return \@rv;
}





1;
