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

package User;
use strict;
use PredefinedAnnotation;
use Group;
use Assignment;
use EvalVector;
use Rubric;
my %accessLevel = ( Admin => 64,
		    Researcher => 32,
		    ResearchAssociate => 16,
		    Teacher => 8,
		    Student => 4,
		    Participant => 2,
		    User => 1 );
my $privileges = { 64 => { Own => { AddParentGroup => 1,
				    EditParentGroup => 1,
				    DeleteParentGroup => 1,
				    AddChildGroup => 1,
				    EditChildGroup => 1,
				    DeleteChildGroup => 1,
				    AddUserToGroup => 1,
				    DeleteUserFromGroup => 1,
				    JoinParentGroup => 1,
				    JoinChildGroup => 1,
				    SearchAnnotations => 1,
				    ViewStatistics => 1,
				    ViewAssignment => 1,
				    AddAssignment => 1,
				    EditAssignment => 1,
				    DeleteAssignment => 1,
				    UploadDocument => 1,
				    AddAnnotation => 1,
				    EditAnnotation => 1,
				    DeleteAnnotation => 1,
				    AssignmentStatistics => 1,
				    SearchComments => 1,
				    ViewDeletedAssignments => 1,
				    SeeAnonymousAuthors => 1,
				    ViewChildGroups => 1,
				    CloseGroup => 1,
				    JoinGroup => 1,
				    ManageDocuments => 1,
				  AddEvalVectors =>1,
				  AddRubrics => 1},

			   Other => { AddParentGroup => 1,
				      ViewChildGroups => 1,
				      EditParentGroup => 1,
				      DeleteParentGroup => 1,
				      AddChildGroup => 1,
				      EditChildGroup => 1,
				      DeleteChildGroup => 1,
				      AddUserToGroup => 1,
				      DeleteUserFromGroup => 1,
				      JoinParentGroup => 1,
				      JoinChildGroup => 1,
				      SearchAnnotations => 1,
				      EditUserInfo=> 1,
				      ViewStatistics => 1,
				      ViewAssignment => 1,
				      AddAssignment => 1,
				      EditAssignment => 1,
				      DeleteAssignment => 1,
				      UploadDocument => 1,
				      AssignmentStatistics => 1,
				      AddAnnotation => 1,
				      EditAnnotation => 1,
				      DeleteAnnotation => 1,
				      SearchComments => 1,
				      ViewDeletedAssignments => 1,
				      SeeAnonymousAuthors => 1,
				      CloseGroup => 1,
				      AddCommunityAnnotation => 1,
				      DeleteCommunityAnnotation => 1,
				      EditCommunityAnnotation => 1,
				      ManageDocuments => 1,
				      AddEvalVectors => 1,
				    },
			 }, 
		   8 => { Own => { ViewChildGroups => 1, 
				  AddParentGroup => 1,
				   EditParentGroup => 1,
				   DeleteParentGroup => 1,
				   AddChildGroup => 1,
				   EditChildGroup => 1,
				   DeleteChildGroup => 1,
				   AddUserToGroup => 1,
				   DeleteUserFromGroup => 1,
				   SearchAnnotations => 1,
				   ViewStatistics => 1,
				   ViewAssignment => 1,
				   AddAssignment => 1,
				   EditAssignment => 1,
				   DeleteAssignment => 1,
				   UploadDocument => 1,
				   AddAnnotation => 1,
				   EditAnnotation => 1,
				   DeleteAnnotation => 1,
				   AssignmentStatistics => 1,
				   SearchComments=> 1,
				   ViewDeletedAssignments => 1,
				   SeeAnonymousAuthors => 1,
				   CloseGroup => 1,
				   JoinParentGroup => 1,
				   JoinGroup => 1,
				   ManageDocuments => 1,
				   AddEvalVectors => 1,
				   AddRubrics => 1
				 },
			  Other => { ViewStatistics => 1,
				     ManageDocuments => 1},
			},
		   4 => { Own => { JoinParentGroup => 1,
				   JoinGroup => 1,
				   SearchAnnotations => 1,
				   ViewStatistics => 1,
				   ViewAssignment => 1,
				   UploadDocument => 1,
				   AddAnnotation => 1,
				   EditAnnotation => 1,
				   DeleteAnnotation => 1,
				   ManageDocuments => 1} }};
				

sub new {

  my ($class,%params) = @_;
  my $self = \%params;
  bless $self, $class;
  return $self;

}
sub getFirstName {
  my ($self) = @_;
  my $v = $self->{FirstName};
  return $v;
}
sub getLastName {
  my ($self) = @_;
  my $v = $self->{LastName};
  return $v;
}
sub getAutoReload {
  my ($self) = @_;
  my $v = $self->{AutoReload};
  return $v;
}
sub hasRole {
  my ($self,$role) = @_;
  
  return (($self->getAccessLevel & $accessLevel{$role}) == $accessLevel{$role});
}
sub isLockedOut {
  my ($self) = @_;
  return ($self->getAccessLevel == 0);
}
sub getAccessLevel {
  my ($self) = @_;
  my $v = $self->{AccessLevel} || 0;
  return $v;
}
sub getDateRegistered {
  my ($self) = @_;
  my $v = $self->{DateRegistered};
  return $v;
}
sub getDatePaid {
  my ($self) = @_;
  my $v = $self->{DatePaid};
  return $v;
}
sub getAccessKey {
  my ($self) = @_;
  my $v = $self->{AccessKey};
  return $v;
}
sub getStatus {
  my ($self) = @_;
  my $v = $self->{Status};
  return $v;
}
sub getNoteType {
  my ($self) = @_;
  my $v = $self->{NoteType};
  return $v;
}
sub hasPrivilege {
  my ($self, $privilege) = @_;
  my ($group,$priv) = split /\./, $privilege;
  my $al = $self->getAccessLevel || 0;
  if (defined $privileges->{$al} and
      defined $privileges->{$al}{$group} and
      defined $privileges->{$al}{$group}{$priv} and
      $privileges->{$al}{$group}{$priv}) {
    return 1;
  } else { 
    return 0;
  }
}
sub getEmail {
  my ($self) = @_;
  my $v = $self->{Email} || "";
  return $v;
}
sub getSchool {
  my ($self) = @_;
  my $v = $self->{School};
  return $v;
}
sub getName {
  my ($self) = @_;
  my $v = $self->getFirstName . " " . $self->getLastName;
  return $v;
}
sub getPassword {
  my ($self) = @_;
  my $v = $self->{Password};
  return $v;
}
sub getID {
  my ($self) = @_;
  my $v = $self->{ID};
  return $v;
}
sub getGroups {
  my ($self) = @_;
  my $v = $self->{Groups};
  return $v;
}
sub getDocuments {
  my ($self) = @_;
  my $sth = $self->{dbh}->prepare("SELECT ObjectID FROM Document WHERE OwnerID = ?");
  $sth->execute($self->getID);
  my ($id,@row) = ();
  while ($id = $sth->fetchrow_array) {
    push @row, $id;
  }
  return \@row;
}
sub setDateRegistered {
  my ($self, $p) = @_;
  $self->{DateRegistered} = $p;
}
sub setAutoReload {
  my ($self, $p) = @_;
  $self->{AutoReload} = $p;
}
sub setDatePaid {
  my ($self, $p) = @_;
  $self->{DatePaid} = $p;
}
sub setAccessKey {
  my ($self, $p) = @_;
  $self->{AccessKey} = $p;
}
sub setStatus {
  my ($self, $p) = @_;
  $self->{Status} = $p;
}
sub setAccessLevel {
  my ($self, $p) = @_;
  $self->{AccessLevel} = $p;
}
sub setEmail {
  my ($self,$p) = @_;
  $self->{Email} = $p;
}
sub setSchool {
  my ($self, $p) = @_;
  $self->{School} = $p;
}
sub setFirstName {
  my ($self,$p) = @_;
  $self->{FirstName} = $p;
}
sub setLastName {
  my ($self,$p) = @_;
  $self->{LastName} = $p;
}
sub setName {
  my ($self,$p) = @_;
  $self->{Name} = $p;
}
sub setPassword {
  my ($self,$p) = @_;
  $self->{Password} = $p;
}
sub setID {
  my ($self, $p) = @_;
  $self->{ID} = $p;
}
sub addMemberGroup {
  my ($self, $p) = @_;
  push @{$self->{MemberedGroups}}, $p;
}
sub addOwnedGroup {
  my ($self, $p) = @_;
  push @{$self->{OwnedGroups}}, $p;
}
sub setNoteType {
  my ($self, $p) = @_;
  # Footnote, FulltextBefore FulltextAfter
  $self->{NoteType} = $p;
}
sub deniedWrite {
  my ($self, $annotation) = @_;
  my $aGID = $annotation->getGroupID;
  my $aUserID = $annotation->getUserID;
  my $rv = 0;
  my $aType = $annotation->getType;
  if ($aType eq "Private") {
    $rv = "Private" unless ($aUserID eq $self->getID);
  } elsif ($aType eq "Group") {
    $rv = "Group" unless ($self->hasGroup($aGID));
  } 
  if ($self->hasPrivilege("Other.EditAnnotation")) {
    $rv = 0;
  }
  return $rv;
}
sub deniedRead {
  my ($self, $annotation) = @_;
  return $self->deniedWrite($annotation);
}
sub hasGroup {
  my ($self, $target) = @_;
  my $rv = 0;
  $self->loadGroups;
  if (defined $target and $target) {
    for my $group (@{$self->{MemberedGroups}},@{$self->{OwnedGroups}}) {
      $rv = 1 if ($group->getGroupID eq $target);
    }
  }
  return $rv;
}
sub hasGroups {
  # just checks to see if the person owns or is a member of any groups

  my ($self) = @_;
  my $rv = 0;
  $self->loadGroups;
  $rv = 1 if (@{$self->{Groups}});
  return $rv;
}
sub ownsGroup {
  my ($self, $target) = @_;
  my $rv = 0;
  $self->loadGroups;
  for my $group (@{$self->{OwnedGroups}}) {
    $rv = 1 if ($group->getGroupID eq $target);
  }
  return $rv;
}
sub groupsOwned {
  my ($self) = @_;
  my $rv = [];
  $self->loadGroups;
  for my $group (@{$self->{OwnedGroups}}) {
    push @{$rv},$group->getGroupID;
  }
  return $rv;
}
sub loadFromEmail {
  my ($class, %params) = @_;
  
  my $sth = $params{dbh}->prepare("SELECT ID FROM user WHERE email = ?");
  $sth->execute($params{Email});
  my ($ID) = $sth->fetchrow_array;
  my $rv = &load($class,
		 ID => $ID,
		 dbh => $params{dbh});
  bless $rv, $class;
  return $rv;

}
sub load {

  my ($class, %params) = @_;
  my $self = \%params;
  bless $self, $class;
  my $sth = $self->{dbh}->prepare("SELECT email, name, password, AccessLevel, DateRegistered, DatePaid, AccessKey, Status, AutoReload, NoteType, FirstName, LastName, School FROM user WHERE ID = ?");
  $sth->execute($self->{ID});
  my ($email,$name, $password, $accessLevel, $dateRegistered, $datePaid, $accessKey, $status,$autoReload, $noteType,$firstName, $lastName, $school) = $sth->fetchrow_array;
  $self->{Email} = $email;
  $self->{AutoReload} = $autoReload;
  $self->{Name} = $name;
  $self->{Password} = $password;
  $self->{AccessLevel} = $accessLevel;
  $self->{DateRegistered} = $dateRegistered;
  $self->{DatePaid} = $datePaid;
  $self->{AccessKey} = $accessKey;
  $self->{Status} = $status;
  $self->{NoteType} = $noteType;
  $self->{FirstName} = $firstName;
  $self->{LastName} = $lastName;
  $self->{School} = $school;
  return $self;
}

sub save {
  my ($self) = @_;
  my $sth = $self->{dbh}->prepare("INSERT INTO user (email,name,password,DateRegistered,DatePaid,AccessKey,Status,NoteType,FirstName,LastName,School) VALUES (?,?,?,?,?,?,?,?,?)");
  $sth->execute($self->getEmail,
		$self->getName,
		$self->getPassword,
		$self->getDateRegistered,
		$self->getDatePaid,
		$self->getAccessKey,
		$self->getStatus,
		$self->getNoteType,
		$self->getFirstName,
		$self->getLastName,
		$self->getSchool);
  $self->setID($self->{dbh}->{mysql_insertid});
  return $self;
}
sub update {
  my ($self) = @_;
  my $sth = $self->{dbh}->prepare("UPDATE user SET email = ?, name = ?, password = ?, AccessLevel = ?, DateRegistered = ?, DatePaid = ?, AccessKey = ?, Status = ?, AutoReload = ?, NoteType = ?, FirstName = ?, LastName = ?, School = ? WHERE ID = ?");
  $sth->execute($self->getEmail,
		$self->getName,
		$self->getPassword,
		$self->getAccessLevel,
		$self->getDateRegistered,
		$self->getDatePaid,
		$self->getAccessKey,
		$self->getStatus,
		$self->getAutoReload,
		$self->getNoteType,
		$self->getFirstName,
		$self->getLastName,
		$self->getSchool,
		$self->getID);
  return $self;
}
sub getDisplayData {
  my ($self) = @_;
  my $rv = { ID => $self->getID,
	     Status => $self->getStatus,
	     School => $self->getSchool,
	     AutoReload => $self->getAutoReload,
	     DateRegistered => $self->getDateRegistered,
	     DatePaid => $self->getDatePaid,
	     AccessKey => $self->getAccessKey,
	     AccessLevel => $self->getAccessLevel,
	     Name => $self->getName,
	     NoteType => $self->getNoteType,
	     Email => $self->getEmail,
	     Password => $self->getPassword,
	     isAdmin => $self->hasRole("Admin"),
	     isResearcher => $self->hasRole("Researcher"),
	     isResearchAssociate => $self->hasRole("ResearchAssociate"),
	     isTeacher => $self->hasRole("Teacher"),
	     isStudent => $self->hasRole("Student"),
	     isUser => $self->hasRole("User"),
	     isParticipant => $self->hasRole("Participant"),
	     isLockedOut => $self->isLockedOut,
	     Privileges => $privileges->{$self->getAccessLevel},
	     FirstName => $self->getFirstName,
	     LastName => $self->getLastName,
	     AdaptiveHelp => $self->getAdaptiveHelp,
	   };
  ($rv->{textAry},$rv->{customAnnotations}) = $self->getPreDefAnnotations;
  $rv->{Privileges} = $privileges->{$self->getAccessLevel};
  return $rv;
}
sub loadGroups {
  my ($self) = @_;
  $self->{Groups} = [];
  my $sth = $self->{dbh}->prepare("SELECT GroupID FROM GroupDefs WHERE OwnerID = ? ORDER by GroupName");
  $sth->execute($self->getID);
  my $allGroups = {};
  while (my ($id) = $sth->fetchrow_array) {
    my $group = Group->load(dbh => $self->{dbh},
			    GroupID => $id);
    push @{$self->{OwnedGroups}}, $group;
    $allGroups->{$group->getGroupID} = $group;
#   push @{$self->{Groups}}, $group;

  }
  $sth = $self->{dbh}->prepare("SELECT GD.GroupID FROM GroupDefs AS GD, GroupMember AS GM WHERE (GM.MemberID = ? AND GM.GroupID = GD.GroupID) ORDER BY GD.GroupName");
  $sth->execute($self->getID);
  while (my ($gid) = $sth->fetchrow_array) {
    my $group = Group->load( dbh => $self->{dbh},
			     GroupID => $gid);
    push @{$self->{MemberedGroups}}, $group;
    $allGroups->{$group->getGroupID} = $group;
#   push @{$self->{Groups}}, $group;
  }

  for my $gid (sort {$a cmp $b} keys %{$allGroups}) {
    push @{$self->{Groups}}, $allGroups->{$gid};
  }
}
sub getGroupDisplayData {
  my ($self,$args) = @_;
  unless (defined $self->{Groups} and @{$self->{Groups}} ) {
    $self->loadGroups;
  }
  my $active = "";
  if (defined $args and ref($args) eq "HASH") {
    $active = $args->{Active};
  }
  my @owned = ();
  my @membered = ();
  my %groupIDs = ();
  my @groups = ({GroupID => "Public",
		 GroupName => "Public (everyone)"});
  for my $group (@{$self->{OwnedGroups}}) {
    my $dd = $group->getDisplayData($self);
    if ($active) {
      next unless ($dd->{Active} eq $active);
    }
    push @owned, $dd;
    next if (defined $groupIDs{$dd->{GroupID}} 
	     and $groupIDs{$dd->{GroupID}});
    $groupIDs{$dd->{GroupID}} = 1;
    push @groups, $dd;
  }
  for my $group (@{$self->{MemberedGroups}}) {
    my $dd = $group->getDisplayData($self);

    if ($active) {
      next unless ($dd->{Active} eq $active);
    }
    push @membered, $dd;
    next if (defined $groupIDs{$dd->{GroupID}} and $groupIDs{$dd->{GroupID}});
    $groupIDs{$dd->{GroupID}} = 1;
    push @groups, $dd;

  }
  push @groups, {GroupID => "Private",
		 GroupName => "Private (only author)"};
  return {AllGroups => \@groups,
	  OwnedGroups => \@owned,
	  MemberedGroups => \@membered,
	  numAllGroups => $#groups + 1,
	  numOwnedGroups => $#owned + 1,
	  numMemberedGroups => $#membered + 1};
		      
}
sub getPreDefAnnotations {
  my ($self) = @_;
  my $sth = $self->{dbh}->prepare("SELECT ID FROM CustomAnnotation WHERE UserID = ? ORDER BY label");
  $sth->execute($self->getID);
  my $i = 1;

  my @rv1 = ({index => 0,
	      Label => "Predefined Annotations",
	      Value => "Predefined Annotations"});
  my @rv2 = ();
  while (my ($ID) = $sth->fetchrow_array) {
    my $ca = PredefinedAnnotation->load( dbh => $self->{dbh},
					 ID => $ID,
					 UserID => $self->getID);
    my $dd = $ca->getDisplayData;
    $dd->{index} = $i++;
    push @rv1, $dd;
    push @rv2, $dd;
  }
  return (\@rv1,\@rv2);
}
sub getAnnotationsDisplayData {
  my ($self, $args) = @_;
  my $url = $args->{URL};
  $self->loadGroups unless defined ($self->{Groups});
  my $sth = $self->{dbh}->prepare("SELECT ID,PhraseRE FROM annotation WHERE UserID = ? AND type = 'Private' AND url = ?");
  $sth->execute($self->getID,$url);
  my ($wholePageIDs,$phraseIDs);
  ($wholePageIDs,$phraseIDs) = &splitAnnotations($sth);
  


  $sth = $self->{dbh}->prepare("SELECT ID, PhraseRE FROM annotation WHERE type = 'Group' and GroupID = ? and url = ?");
  for my $group (@{$self->{Groups}}) {
    $sth->execute($group->getGroupID, $url);
    ($wholePageIDs,$phraseIDs) = &splitAnnotations($sth,$wholePageIDs, $phraseIDs);

  }
  $sth = $self->{dbh}->prepare("SELECT ID, PhraseRE FROM annotation WHERE type='Public' and url = ?");
  $sth->execute($url);
  ($wholePageIDs,$phraseIDs) = &splitAnnotations($sth,$wholePageIDs, $phraseIDs);

  my $rv = {};
  $rv = $self->loadAnnotations($rv,$wholePageIDs, "WholePage");
  $rv = $self->loadAnnotations($rv,$phraseIDs,"Phrase");

}
sub loadAnnotations {
    my ($self,$rv,$annotationIDs,$key) = @_;
    for my $id (keys %{$annotationIDs}) {
      my $an = Annotation->load(dbh => $self->{dbh},
				ID => $id);
      push @{$rv->{$key}}, $an->getDisplayData({CurrentUser => $self});
    }
    return $rv;
  }
sub splitAnnotations {
  my ($sth, $wholePageIDs,$phraseIDs) = @_;
  while (my ($id,$phrase) = $sth->fetchrow_array) {
    if ($phrase eq "(Whole Page)") {
      $wholePageIDs->{$id} = 1;
    } else {
      $phraseIDs->{$id} = 1;
    }
  }
  return ($wholePageIDs, $phraseIDs);
}
sub getAssignmentDisplayData {
  my ($self,$groupID) = @_;
  my @groups = ();
  my @qmarks = ();
  my @params = ();
  my $sth = "";
  if (defined $groupID and $groupID) {
      # we are getting assignment information for a particular group
    $sth = $self->{dbh}->prepare("SELECT Assignment.ID, GroupDefs.GroupName, user.name FROM Assignment,GroupDefs,user WHERE GroupDefs.GroupID = Assignment.GroupID AND user.ID = Assignment.UserID AND GroupDefs.GroupID = ?");
    $sth->execute($groupID);
  } else {
      # we are getting assignment information for all the groups that a user
      # is a member of
    $self->loadGroups;
    for my $group (@{$self->{Groups}}) {
      push @groups, $group->getGroupID;
      push @qmarks, "?";
    }
    my $uid = $self->getID;
    my $qmarks = join ",", @qmarks ;
    $qmarks = "Assignment.GroupID IN ($qmarks) OR" if (defined $qmarks and $qmarks);
    $sth = $self->{dbh}->prepare("SELECT DISTINCT(Assignment.ID), GroupDefs.GroupName, user.name FROM Assignment, user, GroupDefs WHERE GroupDefs.GroupID = Assignment.GroupID AND user.ID = Assignment.UserID AND ($qmarks Assignment.UserID = ?) ORDER BY Assignment.DueDate, GroupDefs.GroupID");
    @params = @groups if (@groups);
    push @params, $self->getID;
    $sth->execute(@params);
  }
  my @rv = ();
  while (my ($id, $GroupName, $UserName) = $sth->fetchrow_array) {
    my $a = Assignment->load(dbh => $self->{dbh},
			     ID => $id);
    my $rv = $a->getDisplayData;
    $rv->{UserName} = $UserName;
    $rv->{GroupName} = $GroupName;
    push @rv, $rv;
  }
  return \@rv;
}
sub getEvalVectorIDs {
  my ($self) = @_;
  my $sth = $self->{dbh}->prepare("SELECT ObjectID FROM EvalVectorDesc WHERE OwnerID = ? ORDER BY ObjectID");
  $sth->execute($self->getID);
  my @rv = ();
  while (my ($ID) = $sth->fetchrow_array) {
    push @rv, $ID;
  }
  return \@rv;
}
sub getEvalVectorDisplayData {
  my ($self) = @_;
  my $ids = $self->getEvalVectorIDs;

  my @rv = ();
  for my $id (@{$ids}) {
    my $ev = EvalVector->load( dbh => $self->{dbh},
			       ID => $id );
    push @rv, $ev->getDisplayData;
  }
  return \@rv;
}
sub getRubricIDs {
  my ($self) = @_;
  my $sth = $self->{dbh}->prepare("SELECT ID FROM ObjectDescription WHERE ObjectClass = 'Rubric' AND OwnerID = ?");
  $sth->execute($self->getID);
  my @rv = ();
  while (my ($id) = $sth->fetchrow_array) {
    push @rv, $id;
  }
  return \@rv;
}
sub getRubricDisplayData {
  my ($self) = @_;
  my $ids = $self->getRubricIDs;
  my @rv = ();
  for my $id (@{$ids}) {
    my $r = Rubric->load( dbh => $self->{dbh},
			  ID => $id );
    push @rv,$r->getDisplayData;
  }
  return \@rv;
}
sub getEvaluationIDsCount {
  my ($self) = @_;
  my $sth = $self->{dbh}->prepare("SELECT COUNT(*) FROM Evaluation WHERE OwnerID = ?");
  $sth->execute($self->getID);
  my ($rv) = $sth->fetchrow_array;
  return $rv;
}
sub getAdaptiveHelp {
  my ($self) = @_;
  my $rv = {};
  if ($self->hasRole("Teacher") or $self->hasRole("Admin")) {
    my $rids = $self->getRubricIDs;
    if (@{$rids} < 4) {
      $rv->{Rubric} = 1;
    } else {
      $rv->{Rubric} = 0;
    }
    my $evs = $self->getEvalVectorIDs;
    if (@{$evs} < 10 ) {
      $rv->{EvalVectors} = 1;
    } else {
      $rv->{EvalVectors} = 0;
    }
    my $assignments = $self->getAssignmentDisplayData;
    if (@{$assignments} < 10) {
      $rv->{Assignments} = 1;
    } else {
      $rv->{Assignments} = 0;
    }
    my $docIDs = $self->getDocuments;
    if (@{$docIDs} < 5) {
      $rv->{Documents} = 1;
    } else {
      $rv->{Documents} = 0;
    }
    my $evIDs = $self->getEvaluationIDsCount;
    if ($evIDs < 100) {
      $rv->{Evaluations} = 1;
    } else {
      $rv->{Evaluations} = 0;
    }

  }
  if ($self->hasRole("Student")) {
    my $docIDs = $self->getDocuments;
    if (@{$docIDs} < 5) {
      $rv->{Assignments} = 1;
      $rv->{Rubrics} = 1;
      $rv->{EvalVectors} = 1;
      $rv->{Documents} = 1;
    } else {
      $rv->{Assignments} = 0;
      $rv->{Rubrics} = 0;
      $rv->{EvalVectors} = 0;
      $rv->{Documents} = 0;
    }
  }
  return $rv;
}
1;
