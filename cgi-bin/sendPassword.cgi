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
use MIME::Lite;
use Template;
use Config::Simple qw( -strict );
use lib "../site_perl";
use http;
use widgets;
use User;
use CGI;
our $C = CGI->new;
my $config = Config::Simple->new("../etc/annie.conf");
my $template = Template->new( RELATIVE => 1,
			      INCLUDE_PATH => "../templates");
my $serverURL = $config->param("Server.URL");
my $dbh = &widgets::dbConnect($config);
my $action = $C->param("action") || "";
my $scriptdir = $config->param("server.scriptdirectory");
if ($action eq "Send My Password") {
  &sendEmail;
} else {
  &printForm;
}


sub sendEmail {

  my $address = $C->param("address") || "";
  $address = &widgets::scrub($address);
  &printForm(error => "You must supply an email address.") if ($address eq "");
  &printForm(error => "I don't consider that a valid email address") if ($address !~ /^[^\@]+\@[^\@\.]+\.([^\@\.]+\.?)+$/ );
  my $user = User->loadFromEmail(dbh => $dbh,
				 Email => $address);
  &printForm(error => "I don't have a record of $address.") unless $user->getID;
  my $pw = $user->getPassword;
  my $vars = { password => $pw,
	       FromAddress => $config->param("email.from"),
	       ServerURL => $serverURL };
  my $message = "";
  $template->process("PasswordEmail.txt",$vars,\$message);

  my $msg = MIME::Lite->new( To => $user->getEmail,
			     Subject => "Lost Annotation Password",
			     Type => 'TEXT',
			     Data => $message );
  $msg->send();
  &printForm("noForm" => 1);
}
sub printForm {
  my (%args) = @_;
  my $vars = \%args;
  $vars->{formAction} = "sendPassword.cgi";
  $vars->{scriptdir} = $scriptdir;
  print $C->header();
  $template->process("sendPasswordForm.html",$vars);

  exit;
}
