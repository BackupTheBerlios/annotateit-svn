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
use MIME::Lite;
use Template;
use Config::Simple qw( -strict );
use lib ("../site_perl");
use widgets;
use auth;
use Comment;
use User;
use CGI;
our $C = CGI->new;

my $config = Config::Simple->new("../etc/annie.conf");
our $dbh = &widgets::dbConnect($config);
our $authInfo = &auth::authenticated($dbh,\$C);
our $scriptdir = $config->param("server.scriptdirectory");
our $serverURL = $config->param("server.url");
our $parentID = $C->param("ParentID") || "";
our $commentID = &widgets::scrub($C->param("CommentID") || "");
our $commentText = &widgets::scrub('keeplinks',$C->param("CommentText") || "");
our $action = $C->param("action") || "";
our $template = Template->new( RELATIVE => 1,
			       INCLUDE_PATH => "../templates");
my $user = User->load( ID => $authInfo->{UserID},
		       dbh => $dbh );
if (!$authInfo->{LoggedIn}) {
  my $vars = { scriptdir => $scriptdir,
	       randomValue => &auth::randomValue(),
	       formAction => "comments.cgi",
	       hiddenVar => [ 
			     {paramName => "ParentID",paramValue => $parentID},
			     {paramName => "CommentID",paramValue => $commentID},
			     {paramName => "CommentText",paramValue => $commentText},
			     {paramName => "action",paramValue => $action}]
	       };
  print $C->header();
  $template->process("loginScriptForm.html",$vars) || die $template->error();
}

if ($action eq "add") {
  &addComment;
} elsif ($action eq "edit1") {
  &editComment1;
} elsif ($action eq "edit2") {
  &editComment2;
} elsif ($action eq "delete") {
  &deleteComment;
}

sub addComment {

  my $comment = Comment->new(dbh => $dbh,
			     ParentID => $parentID,
			     Comment => $commentText,
			     UserID => $authInfo->{UserID});
  $comment->save;
  &sendNotice($comment);
  print $C->redirect(-url => $serverURL . $scriptdir . "displayAnnotation.cgi?AnnotationID=$parentID",
			   -cookie=>$authInfo->{cookie});
  exit;
}

sub editComment1 {
  my $co = Comment->load( dbh => $dbh,
			  ID => $commentID);
  my $commentText = $co->getComment;
  my $var = { CommentText => $commentText,
	      CommentID => $commentID,
	      PageTitle => "Edit Comment",
	      scriptdir => $scriptdir,
	      formAction => "comments.cgi",
	      EnglishAction => "Save Changes",
	      action => "edit2",
	      ParentID => $parentID};
  print $C->header(-cookie => $authInfo->{cookie});
  $template->process("comment.html",$var) or die $template->error();

  exit;


}

sub editComment2 {

  my $co = Comment->load( dbh => $dbh,
			  ID => $commentID );
  $co->setComment($commentText) if ($co->getUserID eq $authInfo->{UserID});
  $co->update;
  &sendNotice($co);
  print $C->redirect($serverURL . $scriptdir . "displayAnnotation.cgi?AnnotationID=$parentID");
  exit;

}

sub deleteComment {

  my $comment = Comment->load(dbh => $dbh,
			      ID => $commentID);
  $parentID = $comment->getParentID;
  $comment->delete if ($authInfo->{UserID} == $comment->getUserID);
  print $C->redirect($serverURL . $scriptdir . "displayAnnotation.cgi?AnnotationID=$parentID");
  exit;

}

sub sendNotice {
  my ($ct) = @_;
  my $sth = $dbh->prepare("SELECT email FROM user WHERE AccessLevel = 64");
  $sth->execute();
  my @adminEmails = ();
  while (my ($adminEmail) = $sth->fetchrow_array) {
    push @adminEmails, $adminEmail;
  }
  my $to = shift @adminEmails;
  my $cc = join ", ", @adminEmails if (@adminEmails);
  my $message = "";
  $template->process("CommentNotification.txt",$ct->getDisplayData({CurrentUser => $user}),\$message) or die $template->error;
  my $msg = MIME::Lite->new( To => $to,
			     Cc => $cc,
			     From => $user->getEmail,
			     Subject => "Annotateit.com Comment",
			     Type => 'TEXT',
			     Data => $message );
  $msg->send;

}
