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
package Group;
use strict;
use User;
my $GroupTypes = { 64 => { Parent => "Parent",
			   Child => "Child" },
		   8 => { Parent => "Class",
			  Child => "Peer Group" }};
my $GroupClasses = { Parent       => "Parent",
		     Child        => "Child",
		     Class        => "Parent",
		     "Peer Group" => "Child" };
sub new {

  my ($class,%params) = @_;
  my $self = \%params;
  bless $self, $class;
  return $self;

}
sub getState {
  my ($self) = @_;
  my $v = $self->{State};
  return $v;
}
sub getParentID {
  my ($self) = @_;
  my $v = $self->{ParentID};
  return $v;
}
sub getType {
  my ($self) = @_;
  my $v = $self->{Type};
  return $v;
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
sub getOwnerID {
  my ($self) = @_;
  my $v = $self->{OwnerID};
  return $v;
}
sub getGroupName {
  my ($self) = @_;
  my $v = $self->{GroupName};
  return $v;
}
sub getActive {
  my ($self) = @_;
  my $v = $self->{Active};
  return $v;
}
sub setState {
  my ($self,$v) = @_;
  $self->{State} = $v;
}
sub setType {
  my ($self) = @_; # can only be called if there is an owner id.
  die "No Owner ID defined" unless (defined $self->getOwnerID and $self->getOwnerID);
  my $user = User->load(dbh => $self->{dbh},
			ID => $self->getOwnerID);
  my $al = $user->getAccessLevel;
  if ($self->isParent) {
    $self->{Type} = $GroupTypes->{$al}{Parent};
  } else {
    $self->{Type} = $GroupTypes->{$al}{Child};
  }

}
sub setActive {
  my ($self, $v) = @_;
  $self->{Active} = $v;
}
sub setParentID {
  my ($self, $v) = @_;
  $self->{ParentID} = $v;
}
sub setID {
  my ($self, $ID) = @_;
  $self->{ID} = $ID;
}
sub setGroupID {
  my ($self, $ID) = @_;
  $self->{GroupID} = $ID;
}
sub setOwnerID {
  my ($self, $ID) = @_;
  $self->{OwnerID} = $ID;
}
sub setGroupName {
  my ($self, $ID) = @_;
  $self->{GroupName} = $ID;
}
sub getClass {
  my ($self) = @_;
  my $v = $GroupClasses->{$self->getType};
  return $v;
}
sub getOwnerEmail {
  my ($self) = @_;
  my $user = User->load(dbh => $self->{dbh},
			ID => $self->getOwnerID);
  my $rv = $user->getEmail;
  return $rv;
}
sub getOwnerName {
  my ($self) = @_;
  my $user = User->load(dbh => $self->{dbh},
			ID => $self->getOwnerID);
  my $rv = $user->getName;
  return $rv;
}
sub addGroupMember {
  my ($self, $member) = @_;
  if ($self->getState ne "Closed") {
    my $sth = $self->{dbh}->prepare("SELECT MemberID FROM GroupMember WHERE GroupID = ? AND MemberID = ?");
    $sth->execute($self->getGroupID,$member->getID);
    my ($id) = $sth->fetchrow_array;
    unless (defined $id and $id) {
      $sth = $self->{dbh}->prepare("INSERT INTO GroupMember (MemberID, GroupID) VALUES (?,?)");
      $sth->execute($member->getID, $self->getGroupID);
      push @{$self->{GroupMembers}}, $self->getGroupMembers;
    }
    return 1;
  } else {
    return 0;
  }
}
sub deleteGroupMember {
  my ($self, $member) = @_;
  my $sth = $self->{dbh}->prepare("DELETE FROM GroupMember WHERE MemberID = ? AND GroupID = ?");
  $sth->execute($member->getID,$self->getGroupID);
}
sub getGroupMembers {
  my ($self) = @_;
  my $sth = $self->{dbh}->prepare("SELECT MemberID FROM GroupMember WHERE GroupID = ?");
  $sth->execute($self->{GroupID});
  my @rv = ();
  while (my ($MemberID) = $sth->fetchrow_array) {
    my $user = User->load(dbh => $self->{dbh},
			  ID => $MemberID);
    push @rv, $user;
  }
  $self->{GroupMembers} = \@rv;
  return \@rv;
}
sub getGroupMemberDisplayData {
  my ($self) = @_;
  my @rv = ();
  for my $gm (@{$self->{GroupMembers}}) {
    my $dd = $gm->getDisplayData;
    push @rv, $dd;
  }
  return \@rv;
}
sub load {
  my ($class, %params) = @_;
  my $self = \%params;
  bless $self, $class;
  my $sth = $self->{dbh}->prepare("SELECT ID, GroupName, OwnerID, ParentID, Type, State, Active FROM GroupDefs WHERE GroupID = ?");
  $sth->execute($self->{GroupID});
  my ($ID, $GroupName, $OwnerID, $ParentID, $Type, $State, $Active) = $sth->fetchrow_array();
  $self->{ID} = $ID;
  $self->{Active} = $Active;
  $self->{State} = $State;
  $self->{GroupName} = $GroupName;
  $self->{OwnerID} = $OwnerID;
  $self->{GroupMembers} = &getGroupMembers($self);
  $self->{ParentID} = $ParentID;
  $self->{Type} = $Type;
  if ($self->isParent) {
    $self->{ChildGroups} = $self->loadChildren;
    $self->{numChildGroups} = $#{$self->{ChildGroups}} +1;
  } else {
    $self->{numChildGroups} = 0;
  }
  return $self;
}
sub delete {
  my ($self) = @_;
  my $sth = $self->{dbh}->prepare("DELETE FROM GroupMember WHERE GroupID = ?");
  $sth->execute($self->getGroupID);
  $sth = $self->{dbh}->prepare("DELETE FROM GroupDefs WHERE GroupID = ?");
  $sth->execute($self->getGroupID);
}
sub update {
  my ($self) = @_;
  my $sth = $self->{dbh}->prepare("UPDATE GroupDefs SET GroupName = ?, GroupID = ?, OwnerID = ?, ParentID = ?, Type = ?, State = ?, Active = ? WHERE ID = ?");
  $self->setType;
  $sth->execute($self->getGroupName,
		$self->getGroupID,
		$self->getOwnerID,
		$self->getParentID,
		$self->getType,
		$self->getState,
		$self->getActive,
		$self->getID);
}
sub save {
  my ($self) = @_;
  $self->setType;
  my $sth = $self->{dbh}->prepare("INSERT INTO GroupDefs (GroupName, GroupID, OwnerID, ParentID, Type, State, Active) VALUES (?,?,?,?,?,?,?)");
  
   

  $sth->execute($self->getGroupName,
		$self->getGroupID,
		$self->getOwnerID,
		$self->getType,
		$self->getParentID,
		"Open","Active");
  $self->setID($self->{dbh}->{mysql_insertid});
  unless (defined $self->getGroupID and $self->getGroupID) {
      my $gid = $g->getID;
      my $groupId = "";
      $groupName = $self->getGroupName;
      unless (defined $groupName and $groupName) {
	  warn "You must set the group name prior to saving: \n";
	  warn "   " . join ": ", caller();
	  die;
      }
      ($groupId = $groupName) =~ s/[^\w]/_/g;
      $groupId .= "_$gid";
      ($groupId = "No Name" . rand(10000)) if ($groupId =~ /^_\d+/);
      $g->setGroupID($groupId);
      $g->update;
  }
}

sub getDisplayData {
  my ($self,$owner) = @_;
  unless (defined $owner) {
    my ($a, $b, $c) = caller;
    die "No user Passed (scalar argument): $a: $b: $c";
  }
  my $ownerID = $self->getOwnerID || "";
  my $childGroups = $self->_childrenDisplayData($owner);
  my $type = $self->getType;
  my $class = defined $self->getType ? $GroupClasses->{$self->getType} : "NA";
  my $rv = {
	    Class => $class,
	    ID => $self->getID,
	    Type => $self->getType,
	    ParentID => $self->getParentID,
	    GroupName => $self->getGroupName,
	    GroupID => $self->getGroupID,
	    OwnerID => $self->getOwnerID,
	    OwnerEmail => $self->getOwnerEmail,
	    OwnerName => $self->getOwnerName,
	    UserIsOwner => $self->isOwner($owner),
	    Type => $self->getType,
	    ChildGroups => $childGroups,
	    State => $self->getState,
	    Active => $self->getActive,
	    numChildGroups => $#{$childGroups} + 1
};
  return $rv;
}
sub isOwner {
  my ($self,$owner) = @_;
  unless (defined $owner) {
    my ($a,$b,$c) = caller();
    die "No Owner passed: $a, $b, $c" unless defined $owner;
  }
  return (defined $self->getOwnerID and defined $owner->getID and ($self->getOwnerID eq $owner->getID));
}
sub isChild {
  my ($self) = @_;
  return (defined $self->{ParentID} and $self->{ParentID});
}
sub isParent {
  my ($self) = @_;
  return (!(defined $self->{ParentID} and $self->{ParentID}));
}

sub loadChildren {

  my ($self) = @_;
  my @rv = ();
  my $sth = $self->{dbh}->prepare("SELECT GroupID FROM GroupDefs WHERE ParentID = ?");
  $sth->execute($self->getGroupID);
  while (my ($id) = $sth->fetchrow_array) {
    my $object = Group->load(dbh => $self->{dbh},
			     GroupID => $id);
    push @rv, $object;
  }
  return \@rv;
}
sub addChild {
  my ($self, $child) = @_;
  push @{$self->{ChildGroups}}, $child;
  $child->setParentID($self->getID);
  $child->update();
}
sub deleteChild {
  my ($self, $child) = @_;
  $child->delete;
  my $cid = $child->getID;
  my @tmpAry = ();
  for my $c (@{$self->{ChildGroups}}) {
    if ($c->getID != $cid) {
      push @tmpAry, $c;
    }
  }
  $self->{ChildGroups} = \@tmpAry;
}
sub _childrenDisplayData {
  my ($self, $owner) = @_;
  my @rv = ();
  for my $child (@{$self->{ChildGroups}}) {
    my $dd = $child->getDisplayData($owner);
    push @rv, $dd;
  }
  return \@rv;
}
sub getAnnotatedURLs {
  my ($self,$params) = @_;
  require Annotation;
  my $cu = $params->{CurrentUser};
  unless (defined $cu and ref($cu) eq "User") {
    warn "CurrentUser is not defined: " . join ": ", caller();
    die;
  }
  my $sth = $self->{dbh}->prepare("SELECT ID, url  FROM annotation WHERE type = 'Group' and GroupID = ?");
  $sth->execute($self->getGroupID);
  my %uniqueURLs = ();
  while (my ($id, $url) = $sth->fetchrow_array) {
    $uniqueURLs{$url} = $id;
  }
  my @rv = ();
  for my $url (sort keys %uniqueURLs) {
    my $id = $uniqueURLs{$url};
    my $an = Annotation->load(dbh => $self->{dbh},
			      ID => $id);
    push @rv, $an->getDisplayData({CurrentUser => $cu});
  }
  return \@rv;
}
sub getAssignmentsDisplayData {
  my ($self) = @_;
  require Assignment;
  my $sth = $self->{dbh}->prepare("SELECT ID FROM Assignment WHERE GroupID = ? ORDER BY DueDate");
  $sth->execute($self->getGroupID);
 my @rv = ();
  while (my ($id) = $sth->fetchrow_array) {
    my $assignment = Assignment->load( dbh => $self->{dbh},
				       ID => $id);
    push @rv, $assignment->getDisplayData;
  }
  return \@rv;
}
sub getDocumentEvalTable {
  my ($self) = @_;
  require Assignment;
  require Document;
  my $sth = $self->{dbh}->prepare("SELECT ID FROM Assignment WHERE GroupID = ? ORDER BY DueDate");
  $sth->execute($self->getGroupID);
  my @assignmentIDs = ();
  while (my ($a) = $sth->fetchrow_array) {
    push @assignmentIDs, $a;
  }
  my @rv = ();
  my $gms = $self->getGroupMembers;
  my $gmdd = $self->getGroupMemberDisplayData;
  $sth = $self->{dbh}->prepare("SELECT ObjectID FROM Document WHERE OwnerID = ? AND AssignmentID = ?");
  for my $gm (@{$gmdd}) {
    # get the user from the group member display data
    my $UserID = $gm->{ID};
    my @assignment = ();
    # get all the assignments for the user
    my $aScoreAccumulator = 0;
    my $gScoreMax = $self->getAssignmentWeightSum;
    my $aScoreSums = 0;
    for my $a (@assignmentIDs) {
      $sth->execute($UserID,$a);
      my $assignment = Assignment->load( dbh => $self->{dbh},
					 ID => $a);
      my @docEvals = ();
      # get all the documents from the assignment;
      my $aWeightDecimal = $assignment->getWeightDecimal;
      my $aWeight = $assignment->getWeight;
      my $aScoreSum = 0;
      my $aScoreCount = 0;
      my $noEval = 1;
      while (my ($docID) = $sth->fetchrow_array) {
	my $doc = Document->load( dbh => $self->{dbh},
				  ID => $docID);
	my $overallScore = $doc->getOverallScore;
	$aScoreSum += $overallScore;
	$aScoreCount++;
	$noEval = 0;
	push @docEvals, {Title => $doc->Title,
			 Eval => $overallScore};
      }
      if ($noEval) {
	push @docEvals, {Title => "No Documents",
			 Eval => 0};
      }
      my $assignmentdd = $assignment->getDisplayData;
      my $weightedEval = eval{($aScoreSum / $aScoreCount) * $aWeightDecimal };
      if ($@) {
	$weightedEval = 0;
      }
      $aScoreAccumulator += $weightedEval;
      $aScoreSums += eval{$aWeight * $aScoreSum/$aScoreCount};
      $assignmentdd->{WeightedOverallScore} = $weightedEval;
      push @assignment, {DisplayData => $assignmentdd,
			 DocEvals => \@docEvals,
			 EvalWeighted => $weightedEval};
    }

    $gm->{FinalEvalWeighted} = $aScoreAccumulator;
    $gm->{FinalEvalOutOf} = $aScoreSums . "/" . $gScoreMax;
    $gm->{Assignment} = \@assignment;
    push @rv, $gm;
  }
  return \@rv;
}
sub getAssignmentWeightSum {
  my ($self) = @_;
  my $sth = $self->{dbh}->prepare("SELECT SUM(Weight) FROM Assignment WHERE GroupID = ?");
  $sth->execute($self->getGroupID);
  my ($rv) = $sth->fetchrow_array;
  return $rv;
}
1;
