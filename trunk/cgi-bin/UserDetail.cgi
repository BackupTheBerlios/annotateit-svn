#!/usr/local/bin/perl -wT
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

use strict;
use Template;
use Config::Simple qw( -strict );
use lib ("../site_perl");
use widgets;
use auth;
use Group;
use User;
use Data::Dumper;
use CGI;
our $C = CGI->new;
our $config = Config::Simple->new("../etc/annie.conf");
our ($dbh, $authInfo, $scriptdir, $serverurl);
$scriptdir = $config->param("server.scriptdirectory");
our $docDir = $config->param("server.documentdirectory");
$serverurl = $config->param("server.url");
$dbh = &widgets::dbConnect($config);
$authInfo = &auth::authenticated($dbh,\$C);
our $action = $C->param("action") || "";
our $ID = $C->param("ID") || "";
our $template = Template->new( RELATIVE => 1,
			      INCLUDE_PATH => "../templates");
unless ($authInfo->{LoggedIn}) {
  my $vars = {scriptdir => $scriptdir,
	      randomValue => &auth::randomValue(),
	      formAction => "UserDetail.cgi"};
	      
  print $C->header;
  $template->process("loginScriptForm.html",$vars) or die $template->error;
  exit;
}
our $user = User->load(dbh => $dbh,
		      ID => $authInfo->{UserID});

unless ($user->hasPrivilege("Other.EditUserInfo")) {
  my $vars = {scriptdir => $scriptdir,
	      serverurl => $serverurl,
	      Error => "NoPrivilegeToEditUser",
	      EnglishError => "Not Authorized",
	      BackPage => 0};
  print $C->header(-cookie=>$authInfo->{cookie});
  $template->process("Error.html") or die $template->error;
  exit;
}

our $vars = {};

if ($action eq "Edit" and $ID) {
  &edit();
} elsif ($action eq "Save" and $ID) {
  &save();
} elsif ($action eq "Delete" and $ID) {
  &delete();
} else {
  &display();
}
print $C->header(-cookie=>$authInfo->{cookie});
$template->process("UserDetail.html",$vars) or die $template->error;
exit;
	
sub edit {
  my $u = User->load(ID => $ID,
		     dbh => $dbh);
  $u->loadGroups;
  my $groups = $u->getGroupDisplayData;
  my $annotations = $u->getAnnotationsDisplayData;
  $vars = { UserToEdit => $u->getDisplayData,
	    Annotations => $u->getAnnotationsDisplayData,
	    Groups => $u->getGroupDisplayData,
	    scriptdir => $scriptdir,
	    serverURL => $serverurl,
	    FormPart => "Edit" };

}
sub save {
  my $ID = $C->param("ID") || "";
  my $FirstName = $C->param("FirstName") || "";
  $FirstName = &widgets::scrub($FirstName);
  my $LastName = $C->param("LastName") || "";
  $LastName = &widgets::scrub($LastName);
  my $Password = $C->param("Password") || "";
  my $AccessKey = $C->param("AccessKey") || "";
  my $AccessLevel = $C->param("AccessLevel") || "";
  my $Status = $C->param("Status") || "";
  my $DatePaid = $C->param("DatePaid") || "";
  return unless $ID;
  my $u = User->load(dbh=>$dbh,
		     ID => $ID);
  $u->setPassword($Password) if (defined $Password and $Password ne $u->getPassword);
  $u->setAccessKey($AccessKey) if (defined $AccessKey and $AccessKey ne $u->getAccessKey);
  $u->setAccessLevel($AccessLevel) if (defined $AccessLevel and $AccessLevel ne $u->getAccessLevel);
  $u->setStatus($Status) if (defined $Status and $Status ne $u->getStatus);
  $u->setDatePaid($DatePaid) if (defined $DatePaid and $DatePaid ne $u->getDatePaid and $DatePaid ne "---");
  $u->setFirstName($FirstName) if (defined $FirstName and $FirstName ne $u->getFirstName);
  $u->setLastName($LastName) if (defined $LastName and $LastName ne $u->getLastName);
  $u->update;
  &display;
}
sub display {
  my $sth = $dbh->prepare("SELECT ID, email, name, AccessLevel, Status, DateRegistered, DatePaid FROM user ORDER BY DateRegistered DESC, ID");
  $sth->execute();
  my @rv = ();
  while (my ($id, $email, $name, $accessLevel, $status, $dateRegistered, $datePaid) = $sth->fetchrow_array) {
    my $r = { ID => $id, Email => $email, AccessLevel => $accessLevel,
	      Status => $status, DateRegistered => $dateRegistered,
	      DatePaid => $datePaid, Name => $name};
    push @rv, $r;
  }
  $vars = { Users => \@rv,
	    scriptdir => $scriptdir,
	    serverURL => $serverurl,
	    EditLink => "UserDetail.cgi",
	    FormPart => "Display"};
}
sub delete {
  my @unlink = ();
  my $sth = $dbh->prepare("DELETE FROM Assignment WHERE UserID = ?");
  $sth->execute($ID);
  $sth = $dbh->prepare("DELETE FROM GroupMember WHERE MemberID = ?");
  $sth->execute($ID);
  $sth = $dbh->prepare("DELETE FROM annotation WHERE UserID = ?");
  $sth->execute($ID);
  $sth= $dbh->prepare("DELETE FROM user where ID = ?");
  $sth->execute($ID);

  $sth = $dbh->prepare("SELECT GroupID FROM GroupDefs WHERE OwnerID = ?");
  $sth->execute($ID);
  my $sth2 = $dbh->prepare("DELETE FROM GroupMember WHERE GroupID = ?");
  my $sth3 = $dbh->prepare("DELETE FROM Assignment WHERE GroupID = ?");
  while (my ($id) = $sth->fetchrow_array) {
    $sth2->execute($id);
    $sth3->execute($id);
  }
  $sth = $dbh->prepare("DELETE FROM Clickthrough where UserID = ?");
  $sth->execute($ID);
  $sth = $dbh->prepare("DELETE FROM GroupDefs WHERE OwnerID = ?");
  $sth->execute($ID);
  $sth = $dbh->prepare("SELECT ID FROM Comment WHERE UserID = ?");
  $sth->execute($ID);
  $sth2 = $dbh->prepare("DELETE FROM Comment WHERE ParentID = ?");
  while (my ($id) = $sth->fetchrow_array) {
    $sth2->execute($id);
  }
  $sth = $dbh->prepare("DELETE FROM Comment WHERE UserID = ?");
  $sth->execute($ID);
  $sth = $dbh->prepare("DELETE FROM CustomAnnotation WHERE UserID = ?");
  $sth->execute($ID);
  $sth = $dbh->prepare("SELECT Filename, Type FROM Document WHERE OwnerID = ?");
  $sth->execute($ID);
  my %ext = ( "MS-Word" => ".doc",
	      "HTML" => ".html",
	      "Text" => ".txt",
	      "RTF" => ".rtf" );
  while (my ($Filename, $Type) = $sth->fetchrow_array) {
    push @unlink, "$docDir/text/$Filename.txt";
    push @unlink, "$docDir/html/$Filename.html";
    push @unlink, "$docDir/html/$Filename" . $ext{$Type};
  }
  unlink @unlink;
  $sth = $dbh->prepare("DELETE FROM Document WHERE OwnerID = ?");
  $sth->execute($ID);
  $sth = $dbh->prepare("CHECK TABLE Assignment, Clickthrough, Comment, CommunityAnnotation, CustomAnnotation, Document, GroupDefs, GroupMember, License, annotation, user");
  $sth->execute();
  while (my ($table, $op, $msg_type, $msg_text) = $sth->fetchrow_array) {
    if ($msg_text ne "OK") {
      my $sth2 = $dbh->prepare("REPAIR TABLE $table");
      $sth2->execute;
      my ($t, $o, $m, $mt) = $sth2->fetchrow_array;
      if ($mt ne "OK") {
	print $C->header;
	my $vars = { Error => "DatabaseError",
		     EnglishError => "Database Error",
		     Table => $table,
		     scriptdir => $scriptdir,
		     serverurl => $serverurl,
		     backpage => 0 };
	$template->process("Error.html",$vars) or die ($template->error);
	exit;
      }
    }
  }
  print $C->header;
  $vars = {scriptdir => $scriptdir,
	      serverurl => $serverurl,
	      Message => "UserDeleteSuccess",
	      EnglishMessage => "Successfully Deleted User",
	      BackPage => "UserDetail.cgi"};
  $template->process("Success.html", $vars) or die ($template->error);
  exit;
}
