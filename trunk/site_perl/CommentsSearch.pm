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
package CommentsSearch;
use strict;
use Annotation;
use Data::Dumper;
sub new {
  my ($class,%params) = @_;
  my $self = \%params;
  bless $self, $class;
  return $self;
}

sub getResults {
  my ($self) = @_;
  my $UserID = $self->{UserID} || "";
  my $ParentID = $self->{ParentID} || "";
  my $AnnotationTitle = $self->{AnnotationTitle} || "";
  my $Comment = $self->{Comment} || "";
  my $auth = $self->{auth} || "";
  my $URL = $self->{URL} || "";
  my $GroupID = $self->{GroupID} || "";
  my $sql = "SELECT DISTINCT(C.ID) FROM Comment AS C, annotation as A";
  my $user = $self->{User} or die "User object must be passed due to security restrictions.";
  my (@params,@whereCond) = ();
  if (!$user->hasPrivilege("Other.SearchComments") 
      and !$user->hasPrivilege("Own.SearchComments")) {
    return [];
  } elsif ($user->hasPrivilege("Own.SearchComments") 
	   and !$user->hasPrivilege("Other.SearchComments")) {
    $user->loadGroups;
    my $groups = $user->getGroups;
    my @gids = ();
    for my $group (@{$groups}) {
      push @gids, $group->getGroupID;
    }
    push @gids, "Public";
    my @quoted = map { "'$_'" } @gids;
    my $gids = join ", ", @quoted;
    push @params, $user->getID;
    push @whereCond, "((A.GroupID IN ($gids)) OR (A.GroupID = 'Private' AND C.UserID = ?))";
  }
  if ($GroupID) {
    push @params, $GroupID;
    push @whereCond, "A.GroupID = ?";
  }
	
  if ($URL) {
    push @params, $URL;
    push @whereCond, "A.url RLIKE ?";
  }
  
  if ($UserID) {
    push @params, $UserID;
    push @whereCond, "C.UserID = ?";
  }
  if ($AnnotationTitle) {
    push @params, $AnnotationTitle;
    push @whereCond, "A.title RLIKE ?";
  }
  if ($Comment) {
    push @params, $Comment;
    push @whereCond, "C.Comment RLIKE ?";
  }
  if (@params) {
    $sql .= " WHERE " . join " AND ", @whereCond;
  }
  warn "\n\n\n";
  warn $sql;
  warn "\n\n\n";

  my $sth = $self->{dbh}->prepare($sql);
  $sth->execute(@params);
  my @rv = ();
  while (my ($id) = $sth->fetchrow_array) {
    my $c = Comment->load(dbh => $self->{dbh},
			  ID => $id,
			  CurrentUser => $user);
    push @rv, $c->getDisplayData;
  }
  return \@rv;
}













1;
