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
package AnnotatedURL;
use strict;
use Annotation;
sub new {
  my ($class,%params) = @_;
  my $self = \%params;
  bless $self, $class;
  return $self;
}
sub getURL {
  my ($self) = @_;
  my $v = $self->{URL};
  return $v;
}
sub getAnnotations {
  my ($self,$params) = @_;
  # _need_ a user object.
  my $user = $params->{CurrentUser} || undef;
  unless (defined $user and ref($user) eq "User") {
    warn "CurrentUser not passed: " . join ": ", caller();
    die;
  }
  my $url = $self->getURL;
  my %groupIDs = ();
  my @rv = ();
  my %annotationIDs = ();
  $user->loadGroups;
  my $groups = $user->getGroups;
  for my $group (@{$groups}) {
    $groupIDs{$group->getGroupID} = 1;
  }
  my $sth = $self->{dbh}->prepare("SELECT ID FROM annotation WHERE url = ? and GroupID = 'Private' and UserID = ?");
  $sth->execute($url, $user->getID);
  while (my ($id) = $sth->fetchrow_array) {
    $annotationIDs{$id} = 1;
  }
  $groupIDs{Public} = 1;
  $sth = $self->{dbh}->prepare("SELECT ID FROM annotation WHERE url = ? AND GroupID = ?");
  for my $gid (keys %groupIDs) {
    $sth->execute($url, $gid);
    while (my ($id) = $sth->fetchrow_array) {
      $annotationIDs{$id} = 1;
    }
  }
  my @annotationIDs = keys %annotationIDs;
  if (@annotationIDs) {
    my @qmarks = ("?")x(@annotationIDs);
    my $qmarks = join ",", @qmarks;
    my $annotationIDs = join ",", @annotationIDs;
    my $sql = "SELECT ID, PhraseRE, title, context,annotation FROM annotation WHERE ID IN ($qmarks)";
    $sth = $self->{dbh}->prepare($sql);
    $sth->execute(@annotationIDs);
    while (my ($id, $phrasere, $title, $context, $text) = $sth->fetchrow_array) {
      push @rv, { AnnotationID => $id,
		  AnnotationPhraseRE => $phrasere,
		  AnnotationTitle => $title,
		  AnnotationContext => $context,
		  AnnotationText => $text};
    }
  }

  return \@rv;
}
1;
