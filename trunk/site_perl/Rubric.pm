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
#   http://www.gnu.org/licenses/gpl.txtpackage Object;
package Rubric;
use strict;
use base qw( Object );
use fields qw( Type );
use Carp;
use EvalVector;
sub load {
  my ($class,%params) = @_;
  my $self = bless {}, $class;
  $self->Object::_init(%params);
  $self->_init(%params);
  $self->loadDescription(%params);
  my $sth = $self->{dbh}->prepare("SELECT Type FROM Rubric WHERE ID = ?");
  $sth->execute($self->ID);
  my ($type) = $sth->fetchrow_array;
  $self->Type($type);
  return $self;
}
sub _init {
  my ($self,%args) = @_;
  return if ($self->{_init}{__Rubric__}++);
  my $rv = $self->SUPER::_init(%args);
  my $class = ref($self) || $self;
  bless ($self,$class);
  $self->mk_accessors($self->show_fields);
  for ($self->show_fields) {
    next if $self->is_inherited($_);
    $self->{$_} = $args{$_};
  }
  return $self;
}
sub save {
  my ($self) = @_;
  $self->saveDescription;
  my $sql = "INSERT INTO Rubric (ID, Type) VALUES (?,?)";
  my $sth = $self->{dbh}->prepare($sql);
  $sth->execute($self->ID,$self->Type);
}
sub update {
  my ($self) = @_;
  $self->updateDescription;
  my $sql = "UPDATE Rubric SET Type = ? WHERE ID = ?";
  my $sth = $self->{dbh}->prepare($sql);
  $sth->execute($self->Type,$self->ID);
}

sub getDisplayData {
  my ($self) = @_;
  my $rv = { ID => $self->ID,
	     OwnerID => $self->OwnerID,
	     Title => $self->Title,
	     Type => $self->Type,
	     };
  return $rv;
}
sub getEvalVectorDisplayData {
  my ($self,$param) = @_;
  my $eIDs = $self->getObjectEvalVectorIDs($param);
  my $weights = $self->getObjectEvalVectorWeightsHash({Secure => 1});
  my @rv = ();
  for my $id (@{$eIDs}) {
    my $ev = EvalVector->load(dbh => $self->{dbh},
			      ID => $id);
    my $hash = $ev->getDisplayData;
    $hash->{Weight} = $weights->{$ev->ID};
    push @rv, $hash;
  }
  return \@rv;
}
1;
