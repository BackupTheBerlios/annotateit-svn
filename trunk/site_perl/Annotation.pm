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
package Annotation;
use strict;
use User;
use Comment;
use Clickthrough;
my %shortMonth = ( "01" => "Jan",
		   "02" => "Feb",
		   "03" => "Mar",
		   "04" => "Apr",
		   "05" => "May",
		   "06" => "Jun",
		   "07" => "Jul",
		   "08" => "Aug",
		   "09" => "Sep",
		   "10" => "Oct",
		   "11" => "Nov",
		   "12" => "Dec");
sub new {

  my ($class,%params) = @_;
  my $self = \%params;
  bless $self, $class;
  return $self;

}
sub getPhrase {
  my ($self) = @_;
  my $phrase = $self->{Phrase} || "";
  return $phrase;
}
sub getPhraseRE {
  my ($self) = @_;
  my $v = $self->{PhraseRE} || "";
  return $v;
}
sub getURL {
  my ($self) = @_;
  my $url = $self->{URL} || "";
  return $url;
}
sub getAnnotation {
  my ($self) = @_;
  my $annotation = $self->{Annotation} || "";
  return $annotation;
}
sub getTitle {
  my ($self) = @_;
  my $title = $self->{Title} || "";
  return $title;
}
sub getUserID {
  my ($self) = @_;
  my $UserID = $self->{UserID} || "";
  return $UserID;
}
sub getContext {
  my ($self) = @_;
  my $Context = $self->{Context} || "";
  return $Context;
}
sub getType {
  my ($self) = @_;
  my $type = $self->{Type} || "";
  return $type;
}
sub getGroupID {
  my ($self) = @_;
  my $GroupID = $self->{GroupID} || "";
  return $GroupID;
}
sub getID {
  my ($self) = @_;
  my $ID = $self->{ID} || "";
  return $ID;
}
sub getAnonymous {
  my ($self) = @_;
  my $A = $self->{Anonymous} || "";
  return $A;
}
sub getTime {
  my ($self) = @_;
  my $Time = $self->{Time} || "";
  return $Time;
}
# settor methods
sub setPhrase {
  my ($self,$p) = @_;
  $self->{Phrase} = $p;
}
sub setPhraseRE {
  my ($self, $p) = @_;
  $self->{PhraseRE} = $p;
}
sub setURL {
  my ($self,$p) = @_;
  $self->{URL} = $p;
}
sub setAnnotation {
  my ($self,$p) = @_;
  $self->{Annotation} = $p;
}
sub setTitle {
  my ($self,$p) = @_;
  $self->{Title} = $p;
}
sub setUserID {
  my ($self,$p) = @_;
  $self->{UserID} = $p;
}
sub setContext {
  my ($self,$p) = @_;
  $self->{Context} = $p;
}
sub setType {
  my ($self,$p) = @_;
  $self->{Type} = $p;
}
sub setGroupID {
  my ($self,$p) = @_;
  $self->{GroupID} = $p;
}
sub setID {
  my ($self,$p) = @_;
  $self->{ID} =$p;
}
sub setTime {
  my ($self,$p) = @_;
  $self->{Time} = $p;
}
sub setAnonymous {
  my ($self,$p) = @_;
  $self->{Anonymous} = $p;
}
sub load {

  my ($class, %params) = @_;
  my $self = \%params;
  bless $self, $class;
  my $sth = $self->{dbh}->prepare("SELECT phrase,url,annotation,title,UserID,Time,context,type,GroupID,PhraseRE,Anonymous FROM annotation WHERE ID = ?");
  $sth->execute($self->{ID});
  my ($phrase,$url,$annotation,$title,$UserID,$Time,$context,$type,$GroupID, $PhraseRE,$anonymous) = $sth->fetchrow_array;
  $self->{Phrase} = $phrase;
  $self->{URL} = $url;
  $self->{Annotation} = $annotation;
  $self->{Title} = $title;
  $self->{UserID} = $UserID;
  $self->{Time} = $Time;
  $self->{Context} = $context;
  $self->{Type} = $type;
  $self->{GroupID} = $GroupID;
  $self->{PhraseRE} = $PhraseRE;
  $self->{Anonymous} = $anonymous;
  return $self;
}
sub clean {
  my ($self) = @_;
  my $url = $self->getURL;
  die "When Cleaning, bad url $url" unless $url =~ /^http:\/\//;
  my $title = $self->getTitle;
  $title =~ s/[<>]//msg;
  $self->setTitle($title);
  my $annotation = $self->getAnnotation;
  $annotation =~ s/javascript/Java Script/imsg;
  $self->setAnnotation($annotation);

}
sub save {
  my ($self) = @_;
  my $sth = $self->{dbh}->prepare("INSERT INTO annotation (phrase,url,annotation,title,UserID,context,type,GroupID, PhraseRE,Anonymous) VALUES (?,?,?,?,?,?,?,?,?,?)");
  $self->clean();
  $sth->execute($self->getPhrase,
		$self->getURL,
		$self->getAnnotation,
		$self->getTitle,
		$self->getUserID,
		$self->getContext,
		$self->getType,
		$self->getGroupID,
		$self->getPhraseRE,
		$self->getAnonymous);
  $self->setID($self->{dbh}->{mysql_insertid});
  return $self;
}
sub update {
  my ($self) = @_;
  $self->clean();
  my $sth = $self->{dbh}->prepare("UPDATE annotation SET phrase = ?, url = ?, annotation = ?, title = ?, UserID = ?, context = ?, type = ?, GroupID = ?, PhraseRE = ?, Anonymous = ? WHERE ID = ?");
  $sth->execute($self->getPhrase,
		$self->getURL,
		$self->getAnnotation,
		$self->getTitle,
		$self->getUserID,
		$self->getContext,
		$self->getType,
		$self->getGroupID,
		$self->getPhraseRE,
		$self->getAnonymous,
		$self->getID
	       );
  return $self;
}
sub getDisplayData {
  my ($self,$param) = @_;
  my $cu = $param->{CurrentUser};
  unless (defined $cu and ref($cu) eq "User") {
      warn join ": ", caller();
      die "no current user passed";
  }
  my $mTime = $self->getTime;
  my ($year,$month,$day,$hour,$minute,$second) = $mTime =~/(\d\d\d\d)(\d\d)(\d\d)(\d\d)(\d\d)(\d\d)/;
  my $dTime = "";
  if (defined $year) {
    $month = $shortMonth{$month};
    $dTime = "$day $month $year $hour:$minute:$second";
  }
  my $groupName ="";
  if ($self->getType eq "Group") {
    my $sth = $self->{dbh}->prepare("SELECT GroupName FROM GroupDefs WHERE GroupID = ?");
    $sth->execute($self->getGroupID);
    ($groupName) = $sth->fetchrow_array;
  } else {
    $groupName = $self->getType;
  }
  my $anonBool = (defined $self->getAnonymous and $self->getAnonymous eq "Yes") ? 1 : 0;
  my $Clickthrough = Clickthrough->getDisplayData( dbh => $self->{dbh},
						   AnnotationID => $self->getID,
						   CurrentUser => $cu);
  my $has_clickthroughs = 0;
  $has_clickthroughs = 1 if (@{$Clickthrough});

  my $rv = { AnnotationIsAnonymous => $anonBool,
	     AnnotationAnonymous => $self->getAnonymous,
	     AnnotationGroupName => $groupName,
	     AnnotationURL => $self->getURL,
	     AnnotationText => $self->getAnnotation,
	     AnnotationTitle => $self->getTitle,
	     AnnotationType => $self->getType,
	     AnnotationID => $self->getID,
	     AnnotationGroupID => $self->getGroupID,
	     AnnotationUserID => $self->getUserID,
	     AnnotationTime => $dTime,
	     AnnotationPhrase => $self->getPhrase,
	     AnnotationPhraseRE => $self->getPhraseRE,
	     AnnotationContext => $self->getContext,
	     Clickthrough => $Clickthrough,
	     has_clickthroughs => $has_clickthroughs};
  
  my $user = User->load(ID => $self->getUserID,
			dbh => $self->{dbh});
  $rv->{AnnotationUserName} = $user->getName;
  $rv->{AnnotationComments} = $self->getCommentsDisplayData({CurrentUser => $cu});
  if (defined $cu and ref($cu) eq "User") {
    if (($cu->getID eq $self->getUserID) or 
       ($cu->hasPrivilege("Other.EditAnnotation"))) {
      $rv->{AnnotationCanEdit} = 1;
    }
  }
  return $rv;
}
sub getCommentsDisplayData {
  my ($self,$param) = @_;
  my $cu = $param->{CurrentUser};
  my $deleteOk = 0;
  if (defined $cu and ref($cu) eq "User") {
    if ($cu->getID eq $self->getUserID) {
      $deleteOk = 1;
    }
  }
  my $sth = $self->{dbh}->prepare("SELECT ID FROM Comment WHERE ParentID = ? ORDER BY ID");
  $sth->execute($self->getID);
  my @rv = ();
  while (my ($cid) = $sth->fetchrow_array) {
    my $comment = Comment->load(ID => $cid,
				dbh => $self->{dbh});
    my $r = $comment->getDisplayData({CurrentUser => $cu});
    $r->{CommentCanDelete} = $deleteOk unless $r->{CommentCanDelete};
    push @rv, $comment->getDisplayData({CurrentUser => $cu});
  }
  return \@rv;
}
sub delete {
  my ($self) = @_;
  my $sth = $self->{dbh}->prepare("DELETE FROM Comment WHERE ParentID = ?");
  $sth->execute($self->getID);
  $sth = $self->{dbh}->prepare("DELETE FROM annotation WHERE ID = ?");
  $sth->execute($self->getID);
}
1;
