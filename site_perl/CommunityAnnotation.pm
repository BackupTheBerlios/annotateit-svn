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
package CommunityAnnotation;
use strict;

sub new {

  my ($class,%params) = @_;
  my $self = \%params;
  bless $self, $class;
  return $self;

}
sub getTitle {
  my ($self) = @_;
  my $v = $self->{Title};
  $v =~ s/'/\\'/g;
  $v =~ s/\\+/\\/g;
  $v =~ s/\s+$//s;
  return $v;
}
sub getDescription {
  my ($self) = @_;
  my $v = $self->{Description};
  $v =~ s/'/\\'/g;
  $v =~ s/\\+/\\/g;
  $v =~ s/\s+$//s;
  return $v;
}
sub getCategory {
  my ($self) = @_;
  my $v = $self->{Category};
  return $v;
}

sub getID {
  my ($self) = @_;
  my $v = $self->{ID};
  return $v;
}
sub setTitle {
  my ($self,$v) = @_;
  $self->{Title} = $v;
}
sub setDescription {
  my ($self,$v) = @_;
  $self->{Description} = $v;
}
sub setCategory {
  my ($self, $v) = @_;
  $self->{Category} = $v;
}
sub setID {
  my ($self,$v) = @_;
  $self->{ID} = $v;
}
sub load {

  my ($class, %params) = @_;
  my $self = \%params;
  bless $self, $class;
  my $sth = $self->{dbh}->prepare("SELECT Title, Description, Category FROM CommunityAnnotation WHERE ID = ?");

  $sth->execute($self->{ID});
  my ($Title,$Description,$Category) = $sth->fetchrow_array;
  $self->{Title} = $Title;
  $self->{Description} = $Description;
  $self->{Category} = $Category;
  $self->{ID} = $self->{ID};
  return $self;
}

sub save {
  my ($self) = @_;
  my $sth = $self->{dbh}->prepare("INSERT INTO CommunityAnnotation (Title,Description,Category) VALUES (?,?,?)");
  $sth->execute($self->getTitle,
		$self->getDescription,
		$self->getCategory);
  $self->setID($self->{dbh}->{mysql_insertid});
  return $self;
}
sub update {
  my ($self) = @_;
  my $sth = $self->{dbh}->prepare("UPDATE CommunityAnnotation SET Title = ?, Description = ?, Category = ? WHERE ID = ?");
  $sth->execute($self->getTitle,
		$self->getDescription,
		$self->getCategory,
		$self->getID);
  return $self;
}
sub delete {
  my ($self) = @_;
  my $sth = $self->{dbh}->prepare("DELETE FROM CommunityAnnotation WHERE ID = ?");
  $sth->execute($self->getID);
}
sub getDisplayData {
  my ($self) = @_;
  my $rv = { ID => $self->getID,
	     Title => $self->getTitle,
	     Description => $self->getDescription,
	     Category => $self->getCategory};
  return $rv;
}
sub getAllDisplayData {
  my ($self) = @_;
  my $sth = $self->{dbh}->prepare("SELECT ID, Title, Description, Category FROM CommunityAnnotation ORDER BY Category, Title");
  $sth->execute;
  
  my $rv2 = [];
  while (my ($ID, $t, $d, $c) = $sth->fetchrow_array) {
    my $rv1 = { ID => $ID,
		Title => $t,
		Description => $d,
		Category => $c};
    push @{$rv2}, $rv1;
  }
  return $rv2;
}
1;
