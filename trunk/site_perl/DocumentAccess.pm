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
package DocumentAccess;
use strict;
use Carp;
sub new {
  my ($class, %params) = @_;
  my $self = \%params;
  bless $self, $class;
  return $self;
}

sub setGroupID {
  my ($self, $v) = @_;
  $self->{GroupID} = $v;
}
sub setDocumentID {
  my ($self, $v) = @_;
  $self->{DocumentID} = $v;
}
sub setAuthorID {
  my ($self, $v) = @_;
  $self->{AuthorID} = $v;
}
sub setOutboxStatus {
  my ($self, $v) = @_;
  $self->{OutboxStatus} = $v;
}
sub setAuthorLastLetter {
  my ($self, $v) = @_;
  $v =~ s/[^A-Z]//g;
  $v =~ s/^(.)/$1/;
  $self->{AuthorLastLetter} = $v;
}
sub setUserID {
  my ($self, $v) = @_;
  $self->{UserID} = $v;
}
sub setGroups {
  my ($self, %params) = @_;
  my $sth = $self->{dbh}->prepare("SELECT GroupID FROM DocumentAccess WHERE DocumentID = ?");
  my @deleteGroups = ();
  $sth->execute($self->{DocumentID});
  while (my ($groupID) = $sth->fetchrow_array) {
    if ($params{User}->hasGroup($groupID)) {
      push @deleteGroups, $groupID;
    }
  }
  push @deleteGroups, ("Private","Public");
  $sth = $self->{dbh}->prepare("DELETE FROM DocumentAccess WHERE DocumentID = ? AND GroupID = ?");
  for my $group (@deleteGroups) {
    $sth->execute($self->{DocumentID},$group);
  }
  for my $group (@{$params{Groups}}) {
    $self->setGroupID($group);
    $self->addAccess;
  }
}
sub checkAccess {
  my ($self) = @_;
  my $sth = $self->{dbh}->prepare("SELECT DocumentID FROM DocumentAccess WHERE GroupID = ? AND DocumentID = ?");
  $sth->execute($self->{GroupID},$self->{DocumentID});
  my ($ID) = $sth->fetchrow_array;
  return (defined($ID) and $ID) ? 1 : 0;
}
sub addAccess {
  my ($self) = @_;
  unless ($self->checkAccess) {
    my $sth = $self->{dbh}->prepare("INSERT INTO DocumentAccess (GroupID,DocumentID) VALUES (?,?)");
    $sth->execute($self->{GroupID},$self->{DocumentID});
  }
}
sub setUser {
  my ($self,$user) = @_;
  $self->{User} = $user;
}
sub removeAccess {
  my ($self) = @_;
  if ($self->checkAccess) {
    my $sth = $self->{dbh}->prepare("DELETE FROM DocumentAccess WHERE GroupID = ? AND DocumentID = ?");
    $sth->execute($self->{GroupID},$self->{DocumentID});
  }
}
sub getDocumentIDs {
  my ($self,%params) = @_;
  my $sth = "";
  my @params;
  unless (defined $self->{GroupID} and $self->{GroupID}) {
    croak "DocumentAccess->{GroupID} must be set for this operation";
  }
  @params = ($self->{GroupID});
  if (defined ($self->{docIDsSth})) {
    $sth = $self->{docIDsSth};
  } else {
    my $sql = "SELECT DA.DocumentID FROM DocumentAccess AS DA, user as U, Document as D WHERE DA.DocumentID = D.ObjectID and D.OwnerID = U.ID and DA.GroupID = ?";
    if (defined($self->{GroupID}) and $self->{GroupID} eq 'Private') {
	# if the user is not an administrator, add to the query making it
	# so that only the user's own private documents are viewable.
	unless (defined $self->{User}
	    and ref($self->{User}) eq "User"
	    and $self->{User}->hasRole("Admin")) {
	    $sql .= " AND D.OwnerID = ?";
	    push @params, $self->{UserID};
	} 
    } 
    if  (defined $self->{AuthorID} and $self->{AuthorID}) {
	$sql .= " AND D.OwnerID = ?";
	push @params, $self->{AuthorID};
    } 
    if (defined $self->{AuthorLastLetter} and $self->{AuthorLastLetter}) {
	$sql .= " AND U.LastName RLIKE \"^" . $self->{AuthorLastLetter} . "\"";
    }
    $sql .= " ORDER BY U.LastName";
    $sth = $self->{dbh}->prepare($sql);
    $self->{docIDsSth} = $sth;
  }
  $sth->execute(@params);
  my @rv = ();
  while (my ($docID) = $sth->fetchrow_array) {
    push @rv, $docID;
    warn "$docID \n";
  }
  my @rv1 = ();
  if (defined $self->{OutboxStatus} and $self->{OutboxStatus}) {
    if (! defined $params{UserID}) {
      warn join ": ", caller;
      die "UserID is required for this operation";
    }
    $sth = $self->{dbh}->prepare("SELECT DocumentID FROM Outbox where DocumentID = ? AND UserID = ?");
    if ($self->{OutboxStatus} eq "Finished") {
      for my $docID (@rv) {
	$sth->execute($docID,$params{UserID});
	my ($r) = $sth->fetchrow_array;
	if (defined $r and $r) {
	  push @rv1, $r;
	}
      }
    } elsif ($self->{OutboxStatus} eq "Not Finished") {
      for my $docID (@rv) {
	$sth->execute($docID,$params{UserID});
	my ($r) = $sth->fetchrow_array;
	if (!defined $r) {
	  push @rv1, $docID;
	}
      }
    } else {
      @rv1 = @rv;
    }
  }
  return \@rv1;
}
sub getGroupInfo {
  my ($self) = @_;
  my ($sth1,$sth2) = ("","");
  my @rv = ();
  if (defined ($self->{groupIDsSth})) {
    $sth1 = $self->{docIDsSth};
    $sth2 = $self->{groupNamesSth};
  } else {
    $sth1 = $self->{dbh}->prepare("SELECT GroupID FROM DocumentAccess WHERE DocumentID = ?");
    $self->{docIDsSth} = $sth1;
    $sth2 = $self->{dbh}->prepare("SELECT GroupName FROM GroupDefs WHERE GroupID = ?");
    $self->{groupNamesSth} = $sth2;
  }
  $sth1->execute($self->{DocumentID});
  while (my ($groupID) = $sth1->fetchrow_array) {
    my $groupName = "";
    if ($groupID eq "Public") {
      $groupName = "Public (everyone)";
    } elsif ($groupID eq "Private") {
      $groupName = "Private (only author)";
    } else {
      $sth2->execute($groupID);
      ($groupName) = $sth2->fetchrow_array;
    }
    push @rv, {GroupID=>$groupID, GroupName => $groupName}
  }
  return \@rv;
}
1;
