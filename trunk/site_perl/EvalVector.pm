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
package EvalVector;
use strict;
use base qw( Object );
use fields qw( MinimumValue MaximumValue Increment Type );


sub new {
  my ($class, %args) = @_;
  my $self = bless {}, ref($class) || $class;
  $self->Object::_init(%args);
  $self->_init(%args);
  return $self;
}
sub _init {
  my ($self, %args) = @_;
  return if ($self->{_init}{__EvalVector__}++);
  $self->mk_accessors($self->show_fields);
  for ($self->show_fields) {
    next if $self->is_inherited($_);
    $self->{$_} = $args{$_};
  }
  return $self;

}

sub setValueName {
  my ($self,$value,$name) = @_;
  $self->{ValueNames}{$value} = $name;
}
sub getValueName {
  my ($self,$value) = @_;
  my $name = $self->{ValueNames}{$value} || "";
  return $name;
}
sub load {

  my ($class, %params) = @_;
  my $self = bless {}, $class;
  $self->Object::_init(%params);
  $self->_init(%params);
  $self->loadDescription;
  my $sth = $self->{dbh}->prepare("SELECT MaximumValue, MinimumValue, Increment, Type, OwnerID FROM EvalVectorDesc WHERE ObjectID = ?");
  $sth->execute($self->{ID});
  my ($MaxValue,$MinValue,$Increment,$Type,$OwnerID) = $sth->fetchrow_array;
  $self->MaximumValue($MaxValue);
  $self->MinimumValue($MinValue);
  $self->Increment($Increment);
  $self->Type($Type);
  $self->OwnerID($OwnerID);
  $sth = $self->{dbh}->prepare("SELECT Value, Name FROM EvalVectorValueNames WHERE EvalVectorID = ? ORDER BY Value");
  $sth->execute($self->{ID});
  while (my ($value, $name) = $sth->fetchrow_array) {
    $self->setValueName($value,$name);
  }
  return $self;
}

sub save {
  my ($self) = @_;
  $self->saveDescription;
  my $id = $self->ID;
  my ($min, $max, $incr) = ($self->MinimumValue, $self->MaximumValue, $self->Increment);
  my $sth = $self->{dbh}->prepare("INSERT INTO EvalVectorDesc (ObjectID,MaximumValue, MinimumValue, Increment, Type, OwnerID) VALUES (?,?,?,?,?,?)");
  $sth->execute($id, $max, $min, $incr,
		$self->Type,
		$self->OwnerID);
  $sth = $self->{dbh}->prepare("DELETE FROM EvalVectorValueNames WHERE EvalVectorID = ?");
  $sth->execute($id);
  $sth = $self->{dbh}->prepare("INSERT INTO EvalVectorValueNames (EvalVectorID, Value, Name) VALUES (?,?,?)");
  for (my $i = $min; $i <= $max; $i += $incr) {
    my $name = $self->getValueName($i);
    $sth->execute($id,$i,$name);
  }
  return $self;
}
sub update {
  my ($self) = @_;
  $self->updateDescription;
  my ($min, $max, $incr) = ($self->MinimumValue, $self->MaximumValue, $self->Increment);
  my $id = $self->ID;
  my $sth = $self->{dbh}->prepare("UPDATE EvalVectorDesc SET MaximumValue = ?, MinimumValue = ?, Increment = ?, Type = ?, OwnerID = ? WHERE ObjectID = ?");
  $sth->execute($max, $min, $incr,
		$self->Type,
		$self->OwnerID,
		$id);
  $sth = $self->{dbh}->prepare("DELETE FROM EvalVectorValueNames WHERE EvalVectorID = ?");
  $sth->execute($id);
  $sth = $self->{dbh}->prepare("INSERT INTO EvalVectorValueNames (EvalVectorID, Value, Name) VALUES (?,?,?)");
  for (my $i = $min; $i <= $max; $i+= $incr) {
    my $name = $self->getValueName($i);
    $sth->execute($id,$i,$name);
  }
  return $self;
}
sub delete {
  my ($self) = @_;
  my $dbh = $self->{dbh};
  my $evid = $self->ID;
  $dbh->do("DELETE FROM EvalVectorDesc WHERE ObjectID = ?",undef,$evid);
  $dbh->do("DELETE FROM EvalVectorValueNames WHERE EvalVectorID = ?",undef,$evid);
  $dbh->do("DELETE FROM ObjectMap WHERE ToObjectID = ? AND ToObjectClass='EvalVector'",undef,$evid);
  $dbh->do("DELETE FROM ObjectMap WHERE FromObjectID = ? AND FromObjectClass='EvalVector'",undef,$evid);
  $dbh->do("DELETE FROM Evaluation WHERE EvalVectorID = ?",undef,$evid);
  $dbh->do("DELETE FROM ObjectDescription WHERE ID = ? AND ObjectClass = 'EvalVector'",undef,$evid);

}
sub getDisplayData {
  my ($self, $param) = @_;
  my $sth = $self->{dbh}->prepare("SELECT FirstName, LastName FROM user WHERE ID = ?");
  $sth->execute($self->OwnerID);
  my ($fn,$ln) = $sth->fetchrow_array;
  my $ownerName = "$fn $ln";
  my $rv = { MaximumValue => $self->MaximumValue,
	     MinimumValue => $self->MinimumValue,
	     Increment => $self->Increment,
	     Title => $self->Title,
	     Type => $self->Type,
	     OwnerName => $ownerName,
	     ID => $self->ID };
  $rv->{Table} = $self->getValuesTable;
  $rv->{Rubric} = $self->getRubricTable;
  return $rv;
}

sub getValuesTable {

  my ($self) = @_;
  my @ary = ();
  my $min = $self->MinimumValue;
  my $max = $self->MaximumValue;
  my $incr = $self->Increment;
  for (my $i = $min; $i <= $max; $i+= $incr) {
    my $h = { Value => $i,
	      Name => $self->getValueName($i) };
    push @ary, $h;
  }
  return \@ary;
}
sub getRubricTable {

  my ($self) = @_;
  my @ary = ();
  my $min = $self->MinimumValue;
  my $max = $self->MaximumValue;
  my $incr = $self->Increment;
  for (my $i = $min; $i <= $max; $i+= $incr) {
    next unless $self->getValueName($i);
    my $h = { Value => $i,
	      Name => $self->getValueName($i) };
    push @ary, $h;
  }
  return \@ary;
}



sub isOwner {
  my ($self, $user) = @_;
  return 1 if ($user->getID == $self->OwnerID);
  return 0;
}


1;
