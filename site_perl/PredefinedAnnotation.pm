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
package PredefinedAnnotation;
use strict;

sub new {

  my ($class,%params) = @_;
  my $self = \%params;
  bless $self, $class;
  return $self;

}
sub getLabel {
  my ($self) = @_;
  my $v = $self->{Label} || "";
  $v =~ s/'/\\'/g;
  $v =~ s/\\+/\\/g;
  $v =~ s/\s+$//s;
  return $v;
}
sub getValue {
  my ($self) = @_;
  my $v = $self->{Value} || "";
  $v =~ s/'/\\'/g;
  $v =~ s/\\+/\\/g;
  $v =~ s/\s+$//s;
  return $v;
}
sub getShortValue {
  my ($self) = @_;
  my $v = $self->{ShortValue} || "";
  return $v;
}
sub getUserID {
  my ($self) = @_;
  my $v = $self->{UserID} || "";
  return $v;
}

sub getID {
  my ($self) = @_;
  my $v = $self->{ID} || "";
  return $v;
}
sub setLabel {
  my ($self,$v) = @_;
  $self->{Label} = $v;
}
sub setValue {
  my ($self,$v) = @_;
  $self->{Value} = $v;
}
sub setShortValue {
  my ($self,$v) = @_;
  $self->{ShortValue} = $v;
}
sub setUserID {
  my ($self,$v) = @_;
  $self->{UserID} = $v;
}
sub setID {
  my ($self,$v) = @_;
  $self->{ID} = $v;
}
sub load {

  my ($class, %params) = @_;
  my $self = \%params;
  bless $self, $class;
  my $sth = $self->{dbh}->prepare("SELECT label, value FROM CustomAnnotation WHERE UserID = ? AND ID = ?");

  $sth->execute($self->{UserID},$self->{ID});
  my ($label,$value) = $sth->fetchrow_array;
  $self->{Label} = $label;
  $self->{Value} = $value;
  $self->{ShortValue} = length($value) > 25 ? substr($value,0,25) . " . . ." : $value;
  $self->{ID} = $self->{ID};
  $self->{UserID} = $self->{UserID};
  return $self;
}

sub save {
  my ($self) = @_;
  my $sth = $self->{dbh}->prepare("INSERT INTO CustomAnnotation (label,value,UserID) VALUES (?,?,?)");
  $sth->execute($self->getLabel,
		$self->getValue,
		$self->getUserID);
  $self->setID($self->{dbh}->{mysql_insertid});
  return $self;
}
sub update {
  my ($self) = @_;
  my $sth = $self->{dbh}->prepare("UPDATE CustomAnnotation SET label = ?, value = ? WHERE ID = ? AND UserID = ?");
  $sth->execute($self->getLabel,
		$self->getValue,
		$self->getID,
		$self->getUserID);
  return $self;
}
sub delete {
  my ($self) = @_;
  my $sth = $self->{dbh}->prepare("DELETE FROM CustomAnnotation WHERE ID = ?");
  $sth->execute($self->getID);
}
sub getDisplayData {
  my ($self) = @_;
  my $rv = { ID => $self->getID,
	     Label => $self->getLabel,
	     Value => $self->getValue,
	     ShortValue => $self->getShortValue,
	     UserID => $self->getUserID};
  return $rv;
}

1;
