#!/usr/local/bin/perl -wT

# Copyright 2003, Buzzmaven
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
use User;
use Annotation;
use Match;
use MIME::Lite;
use URI;
use CGI;
use LWP::UserAgent;
our $C = CGI->new;
$ENV{PATH} = "/usr/bin:/bin:/usr/local/bin";
our $config = Config::Simple->new("../etc/annie.conf");
our $dbh = &widgets::dbConnect($config);
our $authInfo = &auth::authenticated($dbh,\$C);
our $scriptdir = $config->param("server.scriptdirectory");
our $serverURL = $config->param("server.url");
our $annotation = &widgets::scrub("keeplinks",$C->param("annotation") || "");

our $url = $C->param("url") || "";
$url =~ s/[<>]/ /g;

our $security = $C->param("Security") || "";
$security =~ s/[<>]/ /g;
our $selectedtext = $C->param("selectedtext") || "";
$selectedtext =~ s/^\s+//s;
$selectedtext =~ s/\s+$//s;
our $context = $C->param("context") || $selectedtext;
$context =~ s/^\s+//s;
$context =~ s/\s+$//s;
our $anonymous = $C->param("Anonymous") || "";
our $template = Template->new( RELATIVE => 1,
			      INCLUDE_PATH => "../templates" );

if (!$authInfo->{LoggedIn}) {
  my $vars = {scriptdir => $scriptdir,
	      randomValue => &auth::randomValue(),
	      formAction => "getAnnotationInfo.cgi",
	      hiddenVars => [
			     {name => "url", value => $url},
			     {name => "annotation", value => $annotation},
			     {name => "Security", value => $security},
			     {name => "selectedtext", value => $selectedtext},
			     {name => "context", value=> $context}
			    ],
	      url => $url };
  print $C->header;
  $template->process("loginScriptForm.html", $vars) or die $template->error;
  exit;
}
our $user = User->load( dbh => $dbh,
		       ID => $authInfo->{UserID} );
our $query = "";
our $reqParams = {};
($url,$query) = split /\?/, $url;

if (defined $query and $query) {
  my @pairs = split /;/, $query;
  for my $pair (@pairs) {
    my ($key, $value) = split /=/, $pair;
    $reqParams->{$key} = $value;
  }
}
&reprintForm({error => "No URL was passed."}) unless (defined $url and $url);
&reprintForm({error => "No annotation was passed."}) unless (defined $annotation and $annotation);
if (&checkURLExclusion()) {
  my $vars= { Error => "URLExcludedFromAnnotation",
	      EnglishError => "Annotation of this site is not permitted" };
  print $C->header;
  $template->process("Error.html",$vars) or die $template->error;
  exit;
}



our $type = "";
our $groupID = "";
if ($security eq "Private" or $security eq "Public") {
  $type = $groupID = $security;
} else {
  $type = "Group";
  $groupID  = $security;
}
our $title = &widgets::scrub($C->param("title"));

&saveAnnotation({selectedtextRE => $selectedtext,
		 contextRE => $selectedtext })if ($selectedtext eq "(Whole Page)");
our $response = &getResponse({url => $url,
			      vars => $reqParams});
our $content = $response->content();
my $result = Match::checkPhrase({content => $content,
				selectedtext => $selectedtext,
				context => $context});
&reprintForm($result) unless ($result->{Ok});
&saveAnnotation($result);
sub reprintForm {
  my ($parms) = @_;
  my $dd = $user->getDisplayData;
  for my $key ( keys %{$parms}) {
    $dd->{$key} = $parms->{$key};
  }
  $dd->{title} = $title;
  $dd->{StateGroupID} = $groupID;
  $dd->{context} = $context;
  $dd->{annotation} = $annotation;
  $dd->{scriptdir} = $scriptdir;
  $dd->{anonymous} = $anonymous;
  $dd->{Username} = $user->getName;
  $dd->{Groups} = $user->getGroupDisplayData({Active => "Active"});
  $dd->{url} = $url;
  $dd->{url} = "$url?$query" if (defined $query and $query);
  print $C->header(-cookie => $authInfo->{cookie});
  $template->process("AnnotationForm.html",$dd) or die $template->error;
  exit;
}

sub saveAnnotation {
  my ($result) = @_;
  $url = "$url?$query" if (defined $query and $query);
  my $selectedTextRE = $result->{selectedtextRE};
  my $contextRE = $result->{contextRE};
  my $an = Annotation->new(dbh => $dbh);
  $an->setPhraseRE($selectedTextRE);
  $an->setPhrase($selectedtext);
  $an->setURL($url);
  $an->setAnnotation($annotation);
  $an->setContext($contextRE);
  $an->setTitle($title);
  $an->setUserID($authInfo->{UserID});
  $an->setType($type);
  $an->setGroupID($groupID);
  $an->setAnonymous($anonymous);
  $an->save();
  my $user = User->load( dbh => $dbh,
			 ID => $authInfo->{UserID});
  &sendNotice($an) if ($config->param("general.notification") eq "Yes");
  my $vars = { url => $url,
	       title => $title,
	       annotation => $annotation,
	       User=>$user->getDisplayData};
  print $C->header();
  $template->process("AnnotationSuccess.html",$vars) || die $template->error;
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
  $to ||= $config->param("email.from");
  my $vars = { Annotation => $an->getDisplayData({CurrentUser => $user}),
	       serverurl => $serverURL,
	       scriptdir => $scriptdir };
  $template->process("AnnotationNotification.txt",$vars,\$message) or die $template->error;
  my $msg = MIME::Lite->new( To => $to,
			     Cc => $cc,
			     From => $user->getEmail,
			     Subject => "Annotateit.com Annotation",
			     Type => 'TEXT',
			     Data => $message );
  $msg->send;

}
sub checkURLExclusion {
  my $sth = $dbh->prepare("SELECT URL FROM Exclude WHERE URL LIKE ?");
  if (defined $url and $url) {
    my $uri = URI->new($url);
    my $eCheck = "http://" . $uri->host . "%";
    $sth->execute($eCheck);
    my ($rc) = $sth->fetchrow_array;
    if (defined $rc and $rc) {
      return 1;
    } else {
      return 0;
    }
  } else {
    return 1;
  }
}

sub getResponse {
    my $args = shift;
    my $url = $args->{url};
    my $vars_passed = $args->{vars};
    my $ua = LWP::UserAgent->new();
    my $response = "";
    my @request_vars = ();
    if (defined $vars_passed and ref($vars_passed) eq "HASH") {
	my @request_vars = %{$vars_passed};
    } 
    my $canonical_request = "";
    if (ref $url eq "URI") {
	$canonical_request->clone->canonical();
    } else {
	$canonical_request = URI->new($url)->canonical;
    }
    return $ua->get($canonical_request,
		   @request_vars,
		    Referer => $canonical_request);
}
