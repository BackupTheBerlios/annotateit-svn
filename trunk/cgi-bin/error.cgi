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
use CGI;
use Template;
# use Config::Simple;
use MIME::Lite;
use strict;
use Data::Dumper;
use lib qw(../site_perl);
use AnnotateitConfig;
use auth;
use User;
use widgets;

$ENV{PATH} = "/usr/bin:/usr/local/bin";

my $config = $AnnotateitConfig::C;
our $dbh = &widgets::dbConnect($config);

my $C = CGI->new();
our $authInfo = &auth::authenticated($dbh,\$C);


my $t = Template->new( RELATIVE => 1,
		    INCLUDE_PATH => "../templates");
my $time = scalar localtime;
my $errorLogPath = $config->{general}{error_logs};
my $errorLogTail = `tail -n 5 $errorLogPath`;
my $vars = { Error => "ScriptError",
	     EnglishError => "Programming Defect Found",
	     time => $time,
	     ErrorNotes => $ENV{REDIRECT_ERROR_NOTES},
	     ScriptURI => $ENV{REDIRECT_URL},
	     ServerName => $ENV{REDIRECT_SERVER_NAME},
	     ServerAdmin => $ENV{REDIRECT_SERVER_ADMIN},
	     ENV => Dumper(\%ENV),
	     ErrorLogTail => $errorLogTail};
if ($authInfo->{LoggedIn}) {
    our $user = User->load(dbh => $dbh,
			   ID => $authInfo->{UserID});
    $vars->{User} = $user->getDisplayData;
} 

print $C->header;
my $messageText = "";
$t->process("Error.html",$vars) || die $t->error;
$t->process("ErrorEmailToDev.txt", $vars, \$messageText) or die $t->error();


my $message = MIME::Lite->new( To => 'jack@buzzmaven.com',
			       From => 'annotateit-dev@buzzmaven.com',
			       Subject => "Programming Defect: $time",
			       Type => 'TEXT',
			       Data => $messageText );
$message->send;

warn "--- Error trapping occurred ---\n\n";
exit;
