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
#!/usr/local/bin/perl -w
use strict;
package auth;
use Digest::MD5;
use Date::Calc qw(Today_and_Now);
sub expireAuthTokens {
    my $C_ref = shift;
    my $C = "";
    if (defined $C_ref and ref($C_ref) eq 'REF') {
	$C = $$C_ref;
    } else {
	warn "CGI Object not passed to expireAuthTokens\n";
	die "caller: " . join ": ", caller();
    }
  my $nmCookie = $C->cookie(-name=>"name",
				  -value=>"",
				  -expires=>"-1h");
  my $ahCookie = $C->cookie(-name=>"authHash",
				  -value=>"",
				  -expires=>"-1h");
  my $rvCookie = $C->cookie(-name=>"randomValue",
				  -value=>"",
				  -expires=>"-1h");
  my $eaCookie = $C->cookie(-name=>"emailAddress",
				  -value=>"",
				  -expires=>"-1h");
  return [$nmCookie, $ahCookie, $rvCookie, $eaCookie];


}
sub authenticated {
  my ($dbh,$C_ref) = @_;
  my ($authHash, $randomValue, $emailAddress, $sth, $UserID) = ();
  my ($password,$name, $cookie) = ();
  my ($ctx, $data, $digest, $nmCookie, $ahCookie, $rvCookie, $eaCookie) = ();
  my ($C) = ();
  if (defined ($C) and ref($C) eq 'REF') {
      $C = $$C;
  } else {
      warn "The CGI object was not passed. \n";
      die "  Caller: " . join ": ", caller();
  }
  
  $authHash = $C->cookie("authHash") || $C->param("authHash") || "";
  return {cookie => 0, LoggedIn => 0} unless $authHash;
  $randomValue = $C->cookie("randomValue") || $C->param("randomValue") || "";
  return {cookie => 0, LoggedIn => 0} unless $randomValue;
  $emailAddress = $C->cookie("emailAddress") || $C->param("emailAddress") || "";
  $sth = $dbh->prepare("SELECT ID,password,name FROM user WHERE email = ?");
  $sth->execute($emailAddress);
  ($UserID, $password,$name) = $sth->fetchrow_array();
  if (! $UserID and ! $password and ! $name) {
      return {cookie => 0, LoggedIn => 0 };
  }
  $ctx = Digest::MD5->new;
  $data = $password . $randomValue;
  $ctx->add($data);
  $digest = $ctx->hexdigest;
  return {cookie => 0, LoggedIn => 0} unless ($digest eq $authHash);
  $nmCookie = $C->cookie(-name=>"name",
				  -value=>$name,
				  -expires=> "+1d");
  $ahCookie = $C->cookie(-name=>"authHash",
				  -value => $authHash,
				  -expires => "+1d");
  $rvCookie = $C->cookie(-name => "randomValue",
				  -value => $randomValue,
				  -expires => "+1d");
  $eaCookie = $C->cookie(-name => "emailAddress",
				  -value => $emailAddress,
				  -expires => "+1d");
  $cookie = [$ahCookie,$rvCookie,$eaCookie];
  return {cookie => $cookie,
	  LoggedIn => 1,
	  name => $name,
	  UserID => $UserID} if ($digest eq $authHash);
}
sub randomValue {
  my @alpha = ('A'..'Z','a'..'z',0..9);
  my $rand = "";
  for (1..40) {
    $rand .= $alpha[rand(@alpha)];
  }
  return $rand;
}


1;
