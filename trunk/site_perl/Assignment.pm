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
package Assignment;
use strict;	
use Document;
use Rubric;
use Carp;
sub new {

  my ($class,%params) = @_;
  my $self = \%params;
  bless $self, $class;
  return $self;

}

sub getID {
  my ($self) = @_;
  my $v = $self->{ID};
  return $v;
}
sub getGroupID {
  my ($self) = @_;
  my $v = $self->{GroupID};
  return $v;
}
sub getTitle {
  my ($self) = @_;
  my $v = $self->{Title};
  return $v;
}
sub getUserID {
  my ($self) = @_;
  my $v = $self->{UserID};
  return $v;
}
sub getDescription {
  my ($self) = @_;
  my $v = $self->{Description};
  return $v;
}
sub getDueDate {
  my ($self) = @_;
  my $v = $self->{DueDate};
  return $v;
}
sub getDeleted {
  my ($self) = @_;
  my $v = $self->{Deleted};
  return $v;
}
sub getWeight {
  my ($self) = @_;
  my $v = $self->{Weight};
  return $v;
}
sub getOwnerID {
  my ($self) = @_;
  my $v = $self->{OwnerID};
  return $v;
}
sub setWeight {
  my ($self,$p) = @_;
  $self->{Weight} = $p;
}
sub setID {
  my ($self, $p) = @_;
  $self->{ID} = $p;
}
sub setUserID {
  my ($self, $p) = @_;
  $self->{UserID} = $p;
}
sub setTitle {
  my ($self, $p) = @_;
  $self->{Title} = $p;
}
sub setGroupID {
  my ($self, $p) = @_;
  $self->{GroupID} = $p;
}

sub setDescription {
  my ($self, $p) = @_;
  $self->{Description} = $p;
}
sub setDueDate {
  my ($self, $p) = @_;
  $self->{DueDate} = $p;
}
sub setEvalVectors {
  my ($self, $p) = @_;
  unless (defined $p and ref($p) eq "HASH") {
    carp "VectorIDs sent to Assignment::setEvalVectors must be a HASH ref.";
    carp "ID => Weight";
    return;
  }
  my $sth = $self->{dbh}->prepare("DELETE FROM ObjectMap WHERE ToObjectID = ? AND ToObjectClass = 'Assignment'");
  $sth->execute($self->getID);
  $sth = $self->{dbh}->prepare("INSERT INTO ObjectMap (ToObjectID, ToObjectClass, FromObjectID, FromObjectClass, VectorWeight) VALUES (?, 'Assignment', ?, 'EvalVector',?)");
  my $aid = $self->getID;
  for my $id (keys %{$p}) {
    $sth->execute($aid, $id, $p->{$id});
  }
}
sub getEvalVectorIDs {
  my ($self) = @_;
  my $sth = $self->{dbh}->prepare("SELECT FromObjectID, VectorWeight FROM ObjectMap WHERE ToObjectID = ? AND ToObjectClass = 'Assignment' AND FromObjectClass = 'EvalVector'");
  $sth->execute($self->getID);
  my @rv1 = ();
  my %rv2 = ();
  while (my ($id,$weight) = $sth->fetchrow_array) {
    push @rv1, $id;
    $rv2{$id} = $weight;
  }
  return \@rv1,\%rv2;
}

sub load {

  my ($class, %params) = @_;
  my $self = \%params;
  bless $self, $class;
  my $sth = $self->{dbh}->prepare("SELECT A.UserID, A.GroupID, A.Title, A.Description, A.DueDate, A.Deleted, G.GroupName, A.Weight FROM Assignment as A, GroupDefs as G WHERE A.ID = ? AND G.GroupID = A.GroupID");
  $sth->execute($self->{ID});
  my ($UserID, $GroupID, $Title,$Description, $DueDate, $Deleted, $GroupName, $Weight) = $sth->fetchrow_array;
  $self->{UserID} = $UserID;
  $self->{GroupID} = $GroupID;
  $self->{Title} = $Title;
  $self->{Description} = $Description;
  $self->{DueDate} = $DueDate;
  $self->{Deleted} = $Deleted;
  $self->{GroupName} = $GroupName;
  $self->{Weight} = $Weight;
  return $self;
}

sub save {
  my ($self) = @_;
  my $sth = $self->{dbh}->prepare("INSERT INTO Assignment (UserID, GroupID, Title, Description, DueDate, Weight) VALUES (?,?,?,?,?,?)");
  $sth->execute($self->getUserID,
		$self->getGroupID,
		$self->getTitle,
		$self->getDescription,
		$self->getDueDate,
		$self->getWeight);
  $self->setID($self->{dbh}->{mysql_insertid});
  return $self;
}
sub update {
  my ($self) = @_;
  my $sth = $self->{dbh}->prepare("UPDATE Assignment SET UserID = ?, Title = ?, Description = ?, GroupID = ?, DueDate = ?, Weight = ? WHERE ID = ?");
  $sth->execute($self->getUserID,
		$self->getTitle,
		$self->getDescription,
		$self->getGroupID,
		$self->getDueDate,
		$self->getWeight,
		$self->getID,
	       );
  return $self;
}
sub getDisplayData {
  my ($self) = @_;
  my %rv = %{$self};
  delete $rv{dbh};
  my ($y, $m, $d) = split /-/, $self->getDueDate;
  $rv{YearDue} = $y;
  $rv{MonthDue} = $m;
  $rv{MDayDue} = $d;
  $rv{Deleted} = "Deleted" if ($self->getDeleted);
  my $weightDD = $self->getWeightDisplayData;
  for my $key (keys %{$weightDD}) {
    $rv{$key} = $weightDD->{$key};
  }
 return \%rv;
}

sub delete {
  my ($self) = @_;
  my $sth = $self->{dbh}->prepare("DELETE FROM Assignment WHERE ID = ?");
  $sth->execute($self->getID);
  $sth = $self->{dbh}->prepare("DELETE FROM ObjectMap WHERE ToObjectID = ? AND ToObjectClass = ?");
  $sth->execute($self->getID,"Assignment");
  $sth = $self->{dbh}->prepare("DELETE FROM ObjectMap WHERE FromObjectID = ? AND FromObjectClass = ?");
  $sth->execute($self->getID,"Assignment");
  $sth = $self->{dbh}->prepare("UPDATE Document SET AssignmentID = NULL WHERE AssignmentID = ?");
  $sth->execute($self->getID);
}

sub undelete {
  my ($self) = @_;
  my $sth = $self->{dbh}->prepare("UPDATE Assignment SET DELETED = '0' WHERE ID = ?");
  $sth->execute($self->getID);
}
sub getDocumentsDisplayData {
  my ($self, $user) = @_;
  croak "no user object passed" unless (defined $user and ref $user eq "User");
  my $sth = $self->{dbh}->prepare("SELECT ObjectID FROM Document WHERE AssignmentID = ? ORDER BY OwnerID");
  $sth->execute($self->getID);
  my @rv = ();
  my $uid = $user->getID;
  my $aid = $self->getUserID;
  while (my ($id) = $sth->fetchrow_array) {
    my $doc = Document->load( ID => $id,
			      dbh => $self->{dbh} );
    my $dd = $doc->getDisplayData;
    if ($uid == $aid or $user->hasPrivilege("Other.ViewAssignment")) {
      push @rv, $dd;
    } else {
      if ($uid == $doc->OwnerID) {
	push @rv, $dd;
      }
    }
  }
  return \@rv;
}
sub getStats {
  my ($self, $user) = @_;
  croak "no user object passed" unless (defined $user and ref $user eq "User");
  my $sth = $self->{dbh}->prepare("SELECT ObjectID FROM Document WHERE AssignmentID = ? ORDER BY OwnerID");
  $sth->execute($self->getID);
  my $dummy = undef;
  my $averages = {};
  my $counter = 0;
  my $add = [];
  if (($user->hasPrivilege("Own.AssignmentStatistics") and $self->getUserID == $user->getID) or
      $user->hasPrivilege("Other.AssignmentStatistics")) {
    while (my ($id) = $sth->fetchrow_array) {
      my $doc = Document->load( ID => $id,
				dbh => $self->{dbh} );
      my ($statsdd, $statshr) = $doc->getStyleStatistics;
      next if ($statsdd->[0]{Name} eq "No stats for this file");
      $dummy = $statsdd unless defined $dummy; 
      $counter++;
      for my $category (keys %{$statshr}) {
	for my $stat (keys %{$statshr->{$category}}) {
	  if (defined $averages->{$category}{$stat}) {
	    $averages->{$category}{$stat}+=$statshr->{$category}{$stat};
	  } else {
	    $averages->{$category}{$stat}=$statshr->{$category}{$stat};
	  }
	}
      }
    }
    return [{ Name => "No averages could be calculated"}] if $counter == 0;
    for my $category (@{$dummy}) {
      my $c = $category->{Name};
      my $hr = { Name => $c };
      for my $stat (@{$category->{Values}}) {
	my $s = $stat->{Label};
	my $av = $averages->{$c}{$s} / $counter;
	$av = sprintf "%4.1f", $av;
	push @{$hr->{Values}}, {Label => $s, Value => $av};
      }
      push @{$add}, $hr;
    }
    unshift @{$add}, {Name => "Number of Papers Analyzed",
		      Values => [{ Label => "", Value => $counter}]}
  }
  return $add;
}
sub setRubricIDs {
  my ($self,$param) = @_;
  my $userID;
  if (defined $param->{User} and ref($param->{User}) eq "User") {
    $userID = $param->{User}->getID;
  } else {
    croak "You must pass a {User} param to this method";
  }
  my $aid = $self->getID;
  my $sth = $self->{dbh}->prepare("DELETE FROM ObjectMap WHERE FromObjectClass = 'Rubric' AND ToObjectClass = 'Assignment' AND ToObjectID = ? AND OwnerID = ?");
  $sth->execute($aid,$userID);
  $sth = $self->{dbh}->prepare("INSERT INTO ObjectMap (FromObjectClass,FromObjectID,ToObjectClass,ToObjectID,OwnerID) VALUES ('Rubric',?,'Assignment',?,?)");
  for my $id (@{$param->{RubricIDs}}) {
    $sth->execute($id,$aid,$userID);
  }
}

sub getRubricIDs {
  my ($self,$param) = @_;
  my $userID = "";
  my $sql = "";
  my @values = ();
  my $aid = $self->getID;
  unless (defined $param->{Secure} and $param->{Secure}) {
    if (defined $param->{User} and ref($param->{User}) eq "User") {
      $userID = $param->{User}->getID;
    } else {
      croak "You must pass a {User} param to this method";
    }
    $sql = "SELECT FromObjectID FROM ObjectMap WHERE FromObjectClass = 'Rubric' AND ToObjectClass = 'Assignment' AND ToObjectID = ? AND OwnerID = ?";
    @values = ($aid,$userID);
  } else {
    $sql = "SELECT FromObjecTID FROM ObjectMap WHERE FromObjectClass = 'Rubric' AND ToObjectClass = 'Assignment' AND ToObjectID = ?";
    @values = ($aid);
  }

  my $sth = $self->{dbh}->prepare($sql);
  $sth->execute(@values);
  my @rv = ();
  while (my ($id) = $sth->fetchrow_array) {
    push @rv, $id;
  }
  return \@rv;
}
sub getRubricDisplayData {
  my ($self,$param) = @_;
  my $ids = $self->getRubricIDs($param);
  my @rv = ();
  for my $id (@{$ids}) {
    my $r = Rubric->load( dbh => $self->{dbh},
			  ID => $id);
    push @rv, $r->getDisplayData;
  }
  return \@rv;

}
sub getRubricIDsHash {
  my ($self, $param) = @_;
  my $ids = $self->getRubricIDs($param);
  my %rv = ();
  for my $id (@{$ids}) {
    $rv{$id} = 1;
  }
  return \%rv;
}
sub getGroupWeightSum {
  my ($self) = @_;
  my $sth = $self->{dbh}->prepare("SELECT SUM(Weight) FROM Assignment WHERE GroupID = ?");
  $sth->execute($self->getGroupID);
  my ($sum) = $sth->fetchrow_array;
  return $sum;
}
sub getWeightDecimal {
  my ($self) = @_;
  my $weightDecimal = eval{$self->getWeight / $self->getGroupWeightSum};
  if ($@) {
    $weightDecimal = 0;
  }
  return $weightDecimal;
}
sub getWeightDisplayData {
  my ($self) = @_;
  my $sum = $self->getGroupWeightSum;
  my $dec = $self->getWeightDecimal;
  my $weight = $self->getWeight;
  my $weightPercent = sprintf("%2.2f",(100*$dec));
  my $rv = { Weight => $weight,
	     SumOfWeightsForGrup => $sum,
	     WeightOutOf => "$weight/$sum",
	     WeightPercent => "$weightPercent %",
	     WeightDecimal => $dec };
  return $rv;
}

1;
