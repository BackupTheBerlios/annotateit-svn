#!/usr/local/bin/perl
# Copyright 2004, Buzzmaven Co.

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
use CGI qw(:debug);
use LWP::UserAgent;
use URI;
use HTTP::Request;
use HTTP::Request::Common;
use Carp;
use HTML::TokeParser::Simple;
use Data::Dumper;
use lib qw(../site_perl);
use auth;
use widgets;
use Annotation;
use AnnotatedURL;
use Config::Simple;
use Template;
use File::Basename;
my $config = Config::Simple->new("../etc/annie.conf");
$CGI::POST_MAX = 1024*100;
our $C = CGI->new;

our $test = $C->param("test") || "";
our $template=Template->new( RELATIVE => 1,
			    INCLUDE_PATH => "../templates");
if ($test) { &run_tests; exit };
our $output = ""; # the html output from this script
our $dbh = &widgets::dbConnect($config);
our $authInfo = &auth::authenticated($dbh,\$C);

our $images_dir = $config->param("server.imagesdirectory");
our $scriptdir = $config->param("server.scriptdirectory");
our $vars = { scriptdir => $scriptdir,
	     LoggedIn => $authInfo->{LoggedIn},
	     imagesdir => $images_dir};

our $selfURL = $C->url;

# check to see if we need to redirect.  We get our information from the
# path info for the script, so it is important to do it right.

&checkAction();

# get the URL whose annotation we are requesting.

our $requestURI = &getRequestURI();


our $request_method = lc($C->request_method);

our $vars_passed = $C->Vars || {};
our $http_response = &getResponse($requestURI->clone(),
				 $vars_passed,
				 $request_method);
# change the links
our $content = &insertLinks({content => $http_response->content,
			    selfURL => $selfURL,
			    requestURL => $requestURI->clone});

my ($bodyStart,$bodyEnd) = &getBodyOffset($content);
$content = &makeRawContent($content);

$content = &insertAnnotationHolders($content);
&printContent($content,$http_response);

sub printContent {
  my ($content,$http_response) = @_;
#  my $io = IO::Handle->new();
#  $io->fdopen(fileno(STDOUT),"w");
  my $headers = $http_response->headers;
  my $header_key = "";
  my %header_args = ();
  for my $key (keys %{$headers}) {
    $header_key = "-$key";
    $header_args{$header_key} = $headers->{$key};
  }
  $header_args{'-content-length'} = length($content);
  $header_args{'-type'} ||= "text/html";
  $header_args{'-expires'} = "-1d"; # so we make sure
                                         # not to cache anything

  # oddly, a simple print statement doesn't print like we want it to.
  # This may be a problem with Template taking over the IO streams,
  # but I haven't the foggiest idea when or why it happens. [shrug]

  print $C->header(%header_args);
  print $content;
#  $io->print($C->header(%header_args));
#  $io->print($content);
#  $io->close();
#  undef $io;
  exit;
}


sub insertAnnotationHolders {
  my $userID = $authInfo->{UserID} if (ref $authInfo eq "HASH");
  $userID ||= "";
  my $user;
  if ($userID) {
      $user = User->load( dbh => $dbh,
			  ID => $userID );
  } else {
      $user = User->new(dbh => $dbh);
  }
  my $ru = $requestURI->as_string;
  my $aURL = AnnotatedURL->new(dbh => $dbh,
			       URL => $ru);
  my $ad = $aURL->getAnnotations({CurrentUser => $user});
  my $right_arrow = "$images_dir/right_arrow.gif";
  my $left_arrow = "$images_dir/left_arrow.gif";
  my $discussion_icon = "$images_dir/discussion.gif";
  my $noteType = $user->getNoteType;
  for my $annotation (@{$ad}) {
    my $id = $annotation->{AnnotationID};
    my $phraseRE = $annotation->{AnnotationPhraseRE};
    my $title = $annotation->{AnnotationTitle};
    my $context = $annotation->{AnnotationContext};
    my $annotation = $annotation->{AnnotationText};
    next if ($phraseRE eq "(Whole Page)");
    my ($href,$javascript,$sig1,$sig2) = ("","","","");
    $href = $scriptdir ."displayAnnotation.cgi?AnnotationID=$id";
    $javascript = "javascript:newWindow=window.open('$href','viewAnnotation','height=500,width=500,resizable=yes,scrollbars=yes,status=yes'); newWindow.focus();";
    if ($noteType eq "Popup") {
      $sig1 = qq(<a href="$javascript"><img src="$right_arrow" border="0" title="$title" alt=" -[$title]- "  /></a>);
      $sig2 = qq(<a href="$javascript"><img src="$left_arrow" border="0" title="$title" alt=" -[$title]- "  /></a>);
    } elsif ($noteType eq "FulltextBefore") {
      $sig1 = qq({{<a href="$javascript"><img src="$discussion_icon" border="0" title="$title" alt=" -[$title]- " /></a> $annotation}}<img src="$right_arrow" border="0" alt=" -[$title]- " />);
      $sig2 = qq(<img src="$left_arrow" border="0" alt=" -[$title]- " />)
    } elsif ($noteType eq "FulltextAfter") {
      $sig1 = qq(<img src="$right_arrow" border="0" alt=" -[$title]- " />);
      $sig2 = qq(<img src="$left_arrow" border="0" alt=" -[$title]- " />{{<a href="$javascript"><img src="$discussion_icon" border="0" title="$title" alt=" -[$title]- " /></a> $annotation}});
    }
    my ($cMatch) = $content =~ /($context)/s; 
    my $newContent = $cMatch; 
    $newContent =~ s/($phraseRE)/$sig1$1$sig2/s;
    my $len = length($cMatch);
    my $index = index($content,$cMatch);
    substr($content,$index,$len,$newContent);
  }
  return $content;
}



sub makeRawContent {
  my $content = shift;
  my ($bodyStart,$bodyEnd) = &getBodyOffset($content);
  return unless ((defined $bodyStart and $bodyStart < 900000) or (defined $bodyEnd and $bodyEnd > -900000));
  $bodyStart = 0 unless defined $bodyStart;
  $bodyEnd = 0 unless defined $bodyEnd;
  my $sth = $dbh->prepare("SELECT ID FROM annotation WHERE url = ?");
  $sth->execute($requestURI->as_string);
  my $hasAnnotations = 0;
  while (my ($id) = $sth->fetchrow_array) {
    $hasAnnotations++;
  }
  $vars->{currentURL} = $requestURI->as_string;
  
  $vars->{HasAnnotations} = $hasAnnotations;
  $vars->{WholePageNoteLink} = "displayWholePageNotes.cgi";
  my $annotateitToolbar = "";
  $template->process("url-bar-header.html",$vars, \$annotateitToolbar) || die $template->error;
  substr($content,$bodyStart,0,$annotateitToolbar);
  return $content;
}

sub getBodyOffset {
  my $content = shift;
  my ($bodyStart,$bodyEnd) = (900000,-900000);
  my $p = HTML::Parser->new(api_version => 3);
  # at the end of the <body> tag
  my $start = sub { my $bodyStartTemp = shift;
		    if ($bodyStartTemp < $bodyStart) {
			$bodyStart = $bodyStartTemp;
		    }
		    };
  my $end = sub {my $bodyEndTemp = shift; 
		 if ($bodyEndTemp > $bodyEnd) {
		     $bodyEnd = $bodyEndTemp;
		 }
		 };
  $p->handler(start => $start, 'offset_end');
  # at the beginning of the </body> tag
  $p->handler(end => $end,'offset');
  $p->report_tags('body');
  $p->parse($content);
  $p->eof();
  
  # what if there are no <body> tags?
  # one possible case is for a frameset.
  if ( $bodyStart == 900000 and $bodyEnd == -900000) {
    my @accum = ();
    $p->handler(start => \@accum, 'tag');
    $p->report_tags('frameset');
    $p->parse($content);
    $p->eof();
    
    # we don't really want to annotate a frameset, do we?
    
    return (-1,-1) if (@accum);
  }
  # if we still have no bodyStart/bodyEnd;
  if (! $bodyStart and ! $bodyEnd) {
    return (0,length($content));
  } else {
    return ($bodyStart,$bodyEnd);
  }
}
sub insertLinks {

  my ($args) = @_;
  my $content = $args->{content};
  my $p = HTML::TokeParser::Simple->new(\$content);
  my $rv = "";
  # save the request to the filesystem.  We do this for future requests from
  # the same address that we just can't track (things like javascript).
  # this doesn't work with some distributed proxy clients

  my $request_host = "http://" . $requestURI->authority;
  my $request_host_with_directory = $request_host . dirname($requestURI->path);
  $request_host_with_directory =~ s/\.$//; # in case there is no path
  my $request = $requestURI->as_string;
  my $selfURL = $args->{selfURL};
  my $taintedReqfile = $request .  $C->remote_addr;
  $taintedReqfile =~ s/[^\w]+/_/g;
  $taintedReqfile = "../requests/" . $taintedReqfile;
  my $reqfile = "";
  if ($taintedReqfile =~ /^[\w_\.\/]+$/) {
      $reqfile = $1;
  } else {
      warn "$taintedReqfile\n";
  }
  open REQ, ">$reqfile";
  print REQ $request;
  close REQ;

  my %attrHash = (
		  a => "href",
		  base => "href",
		  link => "href",
		  img => "src",
		  script => "src",
		  form => "action",
		  area => "href"
		 );

  while (my $token = $p->get_token ) {
    if ( $token->is_start_tag(qr/^(?:base)|(?:a)|(?:area)|(?:link)|(?:img)|(?:script)|(?:form)$/ )) {
      my $old_href = "";
      my $tag = $token->return_tag;
      my $attr = $attrHash{$tag};
      my $attribute_values = $token->return_attr;
      $old_href = $token->return_attr->{$attr};
      # return_attr() returns a hashref of the attribute values
      my $new_href = '';
      
      if (defined $old_href and $old_href) {
	if ($old_href =~ /^http:\/\//) {
	  # http://foobar/blah.html 
	  $new_href = $old_href;
	} elsif ($old_href =~ /^\/\//) {
	  # //foobar/blah.html 
	  $new_href = "http:$old_href";
	} elsif ($old_href =~ /^\/[\w~]+/) {
	  # /dir/blah.html
	  $new_href = $request_host . $old_href;
	} elsif ($old_href =~ /^\?/) {
	  # ?blah=bar
	  $new_href = $request . $old_href;
	} elsif ($old_href =~ /^\w+/) {
	  # boo.html
	  $new_href = $request_host_with_directory . "/". $old_href;
      } elsif ($old_href =~ /^\.\.\//) {
	# ../../foo.html
	my $request_uri = URI->new($request);
	my $old_uri = URI->new($old_href);
	my @old_uri_segments = $old_uri->path_segments;
	my @request_uri_segments = $request_uri->path_segments;
	pop @request_uri_segments; # this is a hack
	# a more elegant way to get at the next directory up is probably
	# a good idea.

	for my $segment (@old_uri_segments) {
	  if ($segment =~ /^\.\./) {
	    pop @request_uri_segments;
	    shift @old_uri_segments;
	  }
	}
	$new_href = $request_host ;
	$new_href .= join '/', @request_uri_segments;
	$new_href .= "/";
	$new_href .= join '/', @old_uri_segments;
      }
	unless (lc($tag) eq "img") {
	  $new_href = $selfURL ."/". $new_href;
	}
	$token->set_attr($attr,$new_href);
      }
    }
    $rv .= $token->as_is;
  }
  return $rv;
}	

sub getResponse {
  my $requestURI = shift;
  my $vars_passed = shift;
  my $request_method = shift;
  my $ua = LWP::UserAgent->new();
  # slight of hand so that the user's browser is reported rather than the
  # library's
  my $toBe = $C->user_agent();
  $ua->agent($toBe);
  my $response = "";
  my @request_vars = %{$vars_passed};
  my $canonical_request = $requestURI->clone->canonical();
  if ($request_method eq 'post') {
    $response = $ua->post($canonical_request,
			  \@request_vars,
			  Referer => $canonical_request);
  } elsif ($request_method eq 'get') {
    $response = $ua->get($canonical_request,
			 \@request_vars,
			 Referer => $canonical_request);
  } else {
    $vars->{EnglishError} = "Invalid Request Method";
    $vars->{RequestMethod} = $request_method;
    $vars->{Error} = "InvalidRequestMethod";
    print $C->header;
    $template->process("Error.html",$vars) or die $template->error,"\n";
    exit;
  }
  return $response;
}
sub getRequestURI {

  my $request = $C->path_info;
  $request =~ s/^\///;
  my $uri = URI->new($request);
  if ($request_method eq "get") {
    my $query_string = $C->query_string || undef;
    $uri->query($query_string) if (defined $query_string);
  }
  unless (defined $request and $request) {
    $vars->{EnglishError} = "No URL Specified";
    $vars->{Error} = "NoURLSpecified";
    print $C->header;
    $template->process("Error.html",$vars) or die $template->error(),"\n";
    exit;
  }
  unless ($request !~ /(\.jpg|\.gif|\.jpeg|\.png|\.pdf|\.mpeg|\.mpg|\.ico)/) {
    $vars->{EnglishError} = "Not an Annotatable Resource";
    $vars->{Error} = "CannotAnnotate";
    $vars->{Resource} = $request;
    print $C->header;
    $template->process("Error.html",$vars) or die $template->error(),"\n";
    exit;
  }
  return $uri;
}

sub checkAction {
  if (defined $C->param("action") and
      $C->param("action") eq "redirect") {
    my $newURL = $C->url. "/" . $C->param("url");
    print $C->redirect("$newURL");
    exit;
  }
}

sub run_tests {

  print $C->header(-type=>"text/plain");
  my $scripturl = "http://www.annotateit.com/cgi-bin/annotateit.cgi";
  for my $file ("ahrefs.html",
		"imgsrc.html",
		"linkhref.html",
		"links.html","scriptsrc.html") {
    my $request = "http://testing.buzzmaven.com/tests/$file";
    my $request_host = "http://testing.buzzmaven.com";
    my $request_host_with_directory = "http://testing.buzzmaven.com/tests";
    my $ua = LWP::UserAgent->new(agent => "Annotateit/0.4.8 (+http://www.annotateit.com/content_owners.shtml)",
				 from => "support\@buzzmaven.com" );
    my $r = "";
    $r = HTTP::Request->new(GET => $request);
    $r = $ua->prepare_request($r);
    
    my $result = "";
    $result = $ua->request($r);
    
    my $content = "";
    $content = $result->content;
    
    my $p=HTML::TokeParser::Simple->new(\$content);
    my $html = "";
    my %attrHash = ( a => "href",
		     link => "href",
		     img => "src",
		     script => "src",
		     form => "action");
    while (my $token = $p->get_token ) {
      if ( $token->is_start_tag(qr/^(?:a)|(?:link)|(?:img)|(?:script)$/ )) {
	my $old_href = "";
	my $attr = $attrHash{$token->return_tag};
	$old_href = $token->return_attr->{$attr};
	# return_attr() returns a hashref of the attribute values
	my $new_href = '';
	if (defined $old_href and $old_href) {
	  if ($old_href =~ /^http:\/\//) {
	    $new_href = $old_href;
	  } elsif ($old_href =~ /^\/\//) {
	    $new_href = "http:$old_href";
	  } elsif ($old_href =~ /^\/[\w~]+/) {
	    $new_href = $request_host . $old_href;
	  } elsif ($old_href =~ /^\?/) {
	    $new_href = $request . $old_href;
	  } elsif ($old_href =~ /^\w+/) {
	    $new_href = $request_host_with_directory . "/". $old_href;
	  }
	  $new_href = $scripturl ."/". $new_href;
	  $token->set_attr($attr,$new_href);
	}
      }
      $html .= $token->as_is;
    }	
    
    print $html;
  }
}
exit;
