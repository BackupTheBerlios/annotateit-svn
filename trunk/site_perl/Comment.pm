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
package Comment;
use strict;
use User;
sub new {

  my ($class,%params) = @_;
  my $self = \%params;
  bless $self, $class;
  return $self;

}
sub getID {
  my ($self) = @_;
  my $v = $self->{ID} || "";
  return $v;
}
sub getParentID {
  my ($self) = @_;
  my $v = $self->{ParentID} || "";
  return $v;
}
sub getComment {
  my ($self) = @_;
  my $v = $self->{Comment} || "";
  return $v;
}
sub getEntered {
  my ($self) = @_;
  my $v = $self->{Entered} || "";
  return $v;
}
sub getUserID {
  my ($self) = @_;
  my $v = $self->{UserID} || "";
  return $v;
}
sub setID {
  my ($self,$p) = @_;
  $self->{ID} = $p;
}
sub setParentID {
  my ($self,$p) = @_;
  $self->{ParentID} = $p;
}
sub setComment {
  my ($self,$p) = @_;
  $self->{Comment} = $p;
}
sub setEntered {
  my ($self,$p) = @_;
  $self->{Entered} = $p;
}
sub setUserID {
  my ($self,$p) = @_;
  $self->{UserID} = $p;
}
sub load {

  my ($class, %params) = @_;
  my $self = \%params;
  bless $self, $class;
  my $sth = $self->{dbh}->prepare("SELECT C.ParentID, C.Comment, C.Entered, C.UserID, A.title FROM Comment as C, annotation as A WHERE C.ParentID = A.ID AND C.ID = ?");
  $sth->execute($self->{ID});
  my ($ParentID,$Comment,$Entered,$UserID,$AnnotationTitle) = $sth->fetchrow_array;
  unless (defined $Comment) {
    $sth = $self->{dbh}->prepare("SELECT ParentID, Comment, Entered, UserID FROM Comment WHERE ID = ?");
    $sth->execute($self->{ID});
    ($ParentID, $Comment, $Entered, $UserID) = $sth->fetchrow_array;
    $self->{Orphan} = "Yes";
  }
  $self->setParentID($ParentID);
  $self->setComment($Comment);
  $self->setEntered($Entered);
  $self->setUserID($UserID);
  if (defined $AnnotationTitle) {
    $self->{"ParentTitle"} = $AnnotationTitle;
  }
  return $self;
}

sub save {
  my ($self) = @_;
  my $sth = $self->{dbh}->prepare("INSERT INTO Comment (ParentID, Comment, UserID) VALUES (?,?,?)");
  $sth->execute($self->getParentID,
		$self->getComment,
		$self->getUserID);
  $self->setID($self->{dbh}->{mysql_insertid});
  return $self;
}
sub update {
  my ($self) = @_;
  my $sth = $self->{dbh}->prepare("UPDATE Comment SET Comment = ? WHERE ID = ?");
  $sth->execute($self->getComment,
		$self->getID);
  return $self;
}
sub delete {
  my ($self) = @_;
  my $sth = $self->{dbh}->prepare("DELETE FROM Comment WHERE ID = ?");
  $sth->execute($self->getID);
}
sub getDisplayData {
  my ($self, $param) = @_;
  my $cu = undef;
  if (defined $param and ref($param) eq "HASH" and 
      defined $param->{CurrentUser} and ref($param->{CurrentUser}) eq "User"){
    $cu = $param->{CurrentUser};
  } elsif (defined $self->{CurrentUser} 
	   and ref($self->{CurrentUser}) eq "User"){
    $cu = $self->{CurrentUser};
  } else {
    warn join ': ', caller();
    die 'No current user object passed';
  }
  my $rv = { CommentText => $self->getComment,
	     CommentID => $self->getID,
	     CommentParentID => $self->getParentID,
	     CommentEntered => $self->getEntered,
	     CommentUserID => $self->getUserID,
	     ParentTitle => $self->{ParentTitle}
	     };
  my $user = User->load(dbh => $self->{dbh},
			ID => $self->getUserID);
  $rv->{CommentUserName} = $user->getName;
  if (defined $cu and ref($cu) eq "User" and $cu->getID eq $self->getUserID) {
    $rv->{CommentCanEdit} = 1;
    $rv->{CommentCanDelete} = 1;
  }
  return $rv;
}

1;
