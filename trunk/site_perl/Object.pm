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
package Object;
use strict;
use base qw(Class::Fields Class::Accessor);
use fields qw( ObjectClass Title ID OwnerID dbh _init);
use Carp;


sub new {
  my ($class, %args) = @_;
  my $self = bless {}, ref($class) || $class;
  $self->_init(%args);
  return $self;
}
sub _init {
  my ($self, %args) = @_;
  return if ($self->{_init}{__Object__}++);
  $self->mk_accessors($self->show_fields("Public"));
  unless (defined $args{dbh} and ref($args{dbh}) eq "DBI::db") {
    confess "No database handle (dbh) parameter passed.";
  }
  for ($self->show_fields) {
    $self->{$_} = $args{$_};
  }
  my $oc = ref($self) || $self;
  $self->ObjectClass($oc);
  return $self;
}

sub saveDescription {
  my ($self) = @_;
  my $rv = $self->{dbh}->do("INSERT INTO ObjectDescription (ObjectClass,Title,OwnerID) VALUES (?,?,?)",undef, $self->ObjectClass,$self->Title, $self->OwnerID);
  $self->ID($self->{dbh}->{mysql_insertid});
}
sub updateDescription {
  my ($self) = @_;
  my $rv = $self->{dbh}->do("UPDATE ObjectDescription SET ObjectClass = ?, Title = ? WHERE ID = ?", undef, $self->ObjectClass, $self->Title, $self->ID);
}
sub deleteDescription {
  my ($self) = @_;
  my $rv = $self->{dbh}->do("DELETE FROM ObjectDescription WHERE ID = ?",undef, $self->ID);
}
sub loadDescription {
  my ($self,%params) = @_;
  my $id = $self->{ID} || ($self->ID($params{ID}));
  my $sth = $self->{dbh}->prepare("SELECT ObjectClass, Title, OwnerID FROM ObjectDescription WHERE ID = ?");
  $sth->execute($id);
  ($self->{ObjectClass},$self->{Title},$self->{OwnerID}) = $sth->fetchrow_array;
  return $self;
}
sub getDisplayData {
  my ($self) = @_;
  my $rv = { ID => $self->ID,
	     Title => $self->Title,
	     ObjectClass => $self->ObjectClass,
	     OwnerID => $self->OwnerID};
  return $rv;
}
sub mapTo {

  my ($self, %params) = @_;
  my $toObj = $params{Object};
  my $toID = $toObj->{ID};
  my $toObjectClass = ref($toObj) || $toObj;
  my $fromID = $self->ID;
  my $fromObjectClass = $self->ObjectClass;
  my $sth = $self->{dbh}->do("DELETE FROM ObjectMap WHERE FromObjectID = ? AND ToObjectID = ? AND FromObjectClass = ? AND ToObjectClass = ?",undef,$fromID,$toID,$fromObjectClass, $toObjectClass);
  $sth = $self->{dbh}->do("INSERT INTO ObjectMap (FromObjectID, FromObjectClass, ToObjectID, ToObjectClass) VALUES (?,?,?,?)",undef,$fromID,$fromObjectClass, $toID, $toObjectClass);
  return;

}
sub getObjectEvalVectorIDs {
  my ($self,$params) = @_;
  my $userID = "";
  my $oID = $self->ID;
  my $oClass = $self->ObjectClass;
  my $tClass = 'EvalVector';
  my $sth = "";
  my @values = ();
  my $sql = "";
  if (defined $params->{Secure} and $params->{Secure} eq "1") {
    $sql = "SELECT DISTINCT(FromObjectID) FROM ObjectMap WHERE FromObjectClass = 'EvalVector' AND ToObjectClass = ? AND ToObjectID = ?";
    $sth = $self->{dbh}->prepare($sql);
    @values = ($oClass,$oID);
  } else {
    unless (defined $params->{User} and ref($params->{User}) eq "User") {
      croak "You must pass a {User} parameter that is a valid user.";
    }
    $userID = $params->{User}->getID;
    $sql = "SELECT DISTINCT(FromObjectID) FROM ObjectMap WHERE FromObjectClass = 'EvalVector' AND ToObjectClass = ? AND ToObjectID = ? AND OwnerID = ?";
    $sth = $self->{dbh}->prepare($sql);
    @values = ($oClass,$oID,$userID);
  }
  my @rv = ();
  $sth->execute(@values);
  while (my ($id) = $sth->fetchrow_array) {
    push @rv, $id;
  }
  return \@rv;
}
sub getObjectEvalVectorIDHash {
  my ($self,$params) = @_;
  my $userID = "";
  unless (defined $params->{Secure} and $params->{Secure}) {
    unless (defined $params->{User} and ref($params->{User}) eq "User") {
      warn "At " .join ": ", caller();
      croak "You must pass a {User} parameter that is a valid user.";
    }
    $userID = $params->{User}->getID;
  }
  my $eids = $self->getObjectEvalVectorIDs($params);
  my %aHash = ();
  @aHash{@{$eids}} = 1x@{$eids};
  return \%aHash;
}
sub getObjectEvalVectorWeightsHash {
  my ($self,$params) = @_;
  my $userID = "";
  my $sql = "";
  my @values = ();
  my $tID = $self->ID;
  my $tObject = $self->ObjectClass;
  unless (defined $params->{Secure} and $params->{Secure}) {
    unless (defined $params->{User} and ref($params->{User}) eq "User") {
      croak "You must pass a {User} parameter that is a valid user.";
    }
    $userID = $params->{User}->getID;
    $sql = "SELECT VectorWeight FROM ObjectMap WHERE FromObjectClass = 'EvalVector' AND FromObjectID = ? AND ToObjectClass = ? AND ToObjectID = ? AND OwnerID = ?";
    @values = ($tObject,$tID,$userID);
  } else {
    $sql = "SELECT VectorWeight FROM ObjectMap WHERE FromObjectClass = 'EvalVector' AND FromObjectID = ? AND ToObjectClass = ? AND ToObjectID = ?";
    @values = ($tObject,$tID);
  }
  my $eids = $self->getObjectEvalVectorIDs($params);
  my $wHash = ();

  my $sth = $self->{dbh}->prepare($sql);
  my %weights = ();
  for my $id (@{$eids}) {
    $sth->execute($id, @values);
    my ($weight) = $sth->fetchrow_array;
    $weights{$id} = $weight;
  }
  return \%weights;
}
sub setObjectEvalVectors {
  my ($self,$params) = @_;
  my $oID = $self->ID;
  my $oClass = $self->ObjectClass;
  my $tClass= 'EvalVector';
  my $userID = "";
  if (defined $params->{User} and ref($params->{User}) eq "User") {
    $userID = $params->{User}->getID;
  } else {
    croak "You must pass a user object as a {User} parameter to use this method.";
  }
  my $sth = $self->{dbh}->prepare("DELETE FROM ObjectMap WHERE FromObjectClass = 'EvalVector' AND ToObjectClass = ? AND ToObjectID = ? AND OwnerID = ?");
  $sth->execute($self->ObjectClass,$self->ID,$userID);
  $sth = $self->{dbh}->prepare("INSERT INTO ObjectMap (FromObjectID, FromObjectClass, ToObjectID, ToObjectClass, OwnerID, VectorWeight) VALUES (?,'EvalVector',?,?,?,?)");
  my $evs = $params->{AssociatedEvalVectors};
  for my $ev (@{$evs}) {
    my $id = $ev->{ID};
    my $weight = $ev->{Weight};
    $sth->execute($id,$self->ID,$self->ObjectClass,$userID,$weight);
  }
}
1;
