#!/usr/local/bin/perl -wT
# This edits the text annotations, not the predefined annotations.
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
# use Config::Simple qw( -strict );
use lib ("../site_perl");
use AnnotateitConfig;
use auth;
use widgets;
use User;
use Annotation;
use CGI;
our $C = CGI->new;
my $config = $AnnotateitConfig::C;
our $dbh = &widgets::dbConnect($config);
our $annotationID = $C->param("AnnotationID");
our $authInfo = &auth::authenticated($dbh,\$C);
our $user = User->load(dbh => $dbh,
		       ID => $authInfo->{UserID});
our $annotation = Annotation->load(dbh => $dbh,
				   ID => $annotationID);
my $anonymous = $C->param("Anonymous") || "";
my $template = Template->new( RELATIVE => 1,
			      INCLUDE_PATH => "../templates" );
my $scriptdir = $config->{server}{scriptdirectory};
my $serverURL = $config->{server}{url};
if (!($authInfo->{LoggedIn})) {
  my $vars = { hiddenVar => [{name => "AnnotationID", value => $annotationID}],
	       scriptdir => $scriptdir,
	       randomValue => &auth::randomValue(),
	       formAction => "editAnnotations.cgi" };
  print $C->header;
  $template->process("loginScriptForm.html",$vars) or die $template->error;
  exit;
}

&unauthorized($user->deniedRead($annotation)) if ($user->deniedRead($annotation));

if (defined $C->param("submit") and $C->param("submit") eq "Save Edit") {
  &unauthorized($user->deniedWrite($annotation)) if ($user->deniedWrite($annotation));
  my $title = &widgets::scrub($C->param("Title"));
  my $text = &widgets::scrub("keeplinks",$C->param("Annotation"));
  $annotation->setTitle($title);
  my $groupID = "";
  my $type = "";
  my $sec = $C->param("Security");
  if ($sec eq "Private" or
      $sec eq "Public" ) {
    $type = $groupID = $sec;
  } else {
    $type = "Group";
    $groupID = $sec;
  }
			      
  $annotation->setType($type);
  $annotation->setGroupID($groupID);
  $annotation->setAnnotation($text);
  $annotation->setAnonymous($anonymous);
  $annotation->update;
  &sendNotice($annotation);
  my $redir = $serverURL . $scriptdir . "displayAnnotation.cgi?AnnotationID=$annotationID";
  print $C->redirect(-cookie=>$authInfo->{cookie},
			   -url => $redir);

} else {
  my $vars = $annotation->getDisplayData({CurrentUser => $user});
  $vars->{Groups} = $user->getGroupDisplayData;
  $vars->{scriptdir} = $scriptdir;
  $vars->{formAction} = "editAnnotations.cgi";
  print $C->header(-cookie=>$authInfo->{cookie});
  $template->process("EditAnnotations.html",$vars) or die $template->error;

  exit;
}
sub unauthorized {
  my ($type) = @_;
  warn join ": ", (caller());
  my $vars = {EnglishAction => "edit that annotation"};
  $vars->{Private} = 1 if ($type eq "Private");
  $vars->{Group} = 1 if ($type eq "Group");
  $vars->{Error} = 'NotAuthorizedDisplayAnnotation';
  $vars->{EnglishError} = 'Not Authorized';
  print $C->header();
  $template->process("Error.html",$vars) or die $template->error;
  exit;
}

sub sendNotice {
  my ($an) = @_;
  my $sth = $dbh->prepare("SELECT email FROM user WHERE AccessLevel = 64");
  $sth->execute();
  my @adminEmails = ();
  while (my ($adminEmail) = $sth->fetchrow_array) {
    push @adminEmails, $adminEmail;
  }
  my $to = shift @adminEmails;
  my $cc = join ", ", @adminEmails if (@adminEmails);
  my $message = "";
  $to ||= $config->{email}{from};
  my $from = $user->getEmail || $config->{email}{from};
  $template->process("AnnotationNotification.txt",$an->getDisplayData({CurrentUser => $user}),\$message) or die $template->error;
  my $msg = MIME::Lite->new( To => $to,
			     Cc => $cc,
			     From => $from,
			     Subject => "Annotateit.com Annotation",
			     Type => 'TEXT',
			     Data => $message );
  
  $msg->send;
}
