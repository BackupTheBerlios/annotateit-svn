#!/usr/local/bin/perl -w
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
use MIME::Lite;
use Date::Calc qw(Today_and_Now);
use CGI;
our $C = CGI->new;

my $config = Config::Simple->new("../etc/annie.conf");
our ($dbh, $scriptdir, $serverURL, $action, $loc, $url);
$scriptdir = $config->param("server.scriptdirectory");
$serverURL = $config->param("server.url");
my $emailFrom = $config->param("email.from");
$dbh = &widgets::dbConnect($config);
$action = $http::C->param("action");
$loc = $http::C->param("location") || "login.cgi";
$url = $http::C->param("url") || "";

my $template = Template->new( RELATIVE => 1,
			      INCLUDE_PATH => "../templates");
if (defined $action and $action eq "Save My Info") {
  my $email = &widgets::scrub($http::C->param("email"));
  my $firstName = &widgets::scrub($http::C->param("FirstName"));
  my $lastName = &widgets::scrub($http::C->param("LastName"));
  my $noteType = &widgets::scrub($http::C->param("NoteType"));
  my $school = &widgets::scrub($http::C->param("School"));
  my $error = &createUser(dbh => $dbh,
			  email => $email,
			  firstName => $firstName,
			  lastName => $lastName,
			  noteType => $noteType,
			  school => $school,
			 );
  unless ($error) {
    my $redir = $serverURL . $scriptdir . $loc;
    $redir .= "?url=$url" if ($url);
    my %rd = ( -url => $redir );
    $rd{-cookie} = &auth::expireAuthTokens if ($loc eq "login.cgi");
    print $http::C->redirect(%rd);
    exit;
  }
  &printUsernameForm(error => $error);
} else {
  &printUsernameForm();
}

sub printUsernameForm {
  my %args = @_;
  my $vars = { formAction => "createUser.cgi",
	       scriptdir => $scriptdir,
	       location => $loc,
	       error => $args{error},
	       url => $url,
	       EnglishAction => "Make a New "};

  print $http::C->header();
  $template->process("createUser.html",$vars) or die $template->error();
  exit;
}
sub createUser {

  my (%params) = @_;
  my $dbh = $params{"dbh"};
  my $email = $params{"email"};
  my $firstName = $params{"firstName"};
  my $lastName = $params{"lastName"};
  my $noteType = $params{"noteType"};
  my $school = $params{"school"};
  my $scriptdir = &http::scriptdir;
  my $name = "$firstName $lastName";
  my @chars = ('A'..'Z','a'..'z',1..9);
  my $password = "";
  for (1..10) {
    $password .= $chars[rand(@chars)];
  }
  return "You must have a first name" unless (defined $firstName and $firstName and $firstName !~ /^\s+$/);
  return "You must have a last name" unless (defined $lastName and $lastName and $lastName !~ /^\s+$/);
  return "That user already exists.  We can <a href=\"$scriptdir" ."sendPassword.cgi\">send you your password</a>." unless (&_checkUser($dbh));
  my $sth = $dbh->prepare("INSERT INTO user (email,name,password,DateRegistered,FirstName, LastName, NoteType, School,AccessLevel,Status) VALUES (?,?,?,?,?,?,?,?,?,?)");
  my ($y,$m,$d,$h,$min,$s) = Today_and_Now;
  my $date = "$y-$m-$d $h:$min:$s";
  $sth->execute($email,$name,$password,$date,$firstName,$lastName,$noteType,$school,4,'Trial');
  &sendWelcomeEmail($email,$password);
  return 0;
}

sub _checkUser {

  my ($dbh) = (@_);
  my $email = $http::C->param("email");
  my $sth = $dbh->prepare("SELECT ID FROM user WHERE email = ?");
  $sth->execute($email);
  my ($id) = $sth->fetchrow_array();
  return 0 if ($id);
  return 1;
}

sub sendWelcomeEmail {

  my ($email,$password) = @_;
  my $message = qq(
You are receiving this email because someone entered it on a form
at http://www.annotateit.com.  If this is not you, please accept our
apologies and disregard this message.

Greetings!  Welcome to AnnotateIt! You have successfully registered to
use the system.  Before you do, you have to login.  Please go to

$serverURL${scriptdir}login.cgi

You registered using 

$email

as the email address.  The password generated for you was

$password

After you login, please go to the preferences menu and change your
password to something you can remember easily.

Thanks!

);

  my $msg = MIME::Lite->new(To => $email,
			    From => $emailFrom,
			    Subject => "AnnotateIt! Password",
			    Type => "TEXT",
			    Data => $message);
  $msg->send;
}
