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
# use Config::Simple qw(-strict);
use lib ("../site_perl");
use AnnotateitConfig;
use widgets;
use auth;
use User;
use URI;
use CGI;
our $C = CGI->new;

our $urlExcluded = 0;

our $config = $AnnotateitConfig::C;
our ($template,$dbh, $authInfo, $scriptdir) = ();
$scriptdir = $config->{server}{scriptdirectory};
$dbh = &widgets::dbConnect($config);;
$authInfo = &auth::authenticated($dbh,\$C);
$template = Template->new(RELATIVE => 1,
			  INCLUDE_PATH => "../templates");
our $url = &getLocation();
if (!$authInfo->{LoggedIn}) {
  my $vars = { 
	      randomValue => &auth::randomValue(),
	      scriptdir => $scriptdir,
	       formAction => "getAnnotationInfo.cgi",
	       hiddenVar => [{name => "url", value=> $url }]};
  print $C->header();
  $template->process("loginScriptForm.html",$vars) or die $template->error();
  exit;

} elsif (!$urlExcluded) {
  &printAnnotationForm;
} elsif ($urlExcluded) {
  my $vars = {Error => "URLExcludedFromAnnotation",
	      EnglishError => "Annotation is not Permitted",
	     };
  print $C->header();
  $template->process("Error.html",$vars) or die $template->error();
}
sub printAnnotationForm {
  my $user = User->load(dbh => $dbh,
			ID => $authInfo->{UserID});
  my $dd = $user->getDisplayData;
  $dd->{Groups} = $user->getGroupDisplayData({Active => "Active"});
  $dd->{url} = $url;
  $dd->{scriptdir} = $scriptdir;
  print $C->header(-cookie => $authInfo->{cookie});
  $template->process("AnnotationForm.html",$dd) or die $template->error();
  exit;

}
sub getLocation {
  my $vars = $C->Vars;
  my $queryString = "";
  my @qs = ();
  for my $key (keys %{$vars}) {
    next if $key eq "authHash";
    next if $key eq "randomValue";
    next if $key eq "emailAddress";
    next if $key eq "password";
    next if $key eq "url";
    push @qs, "$key=$vars->{$key}";
  }
  $queryString = join ";", @qs;
  my $tUrl = $C->param("url");
  $tUrl =~ s/[<>]//g;
  my $location = $tUrl . "?$queryString";
  $location =~ s/\?$//;
  
  if (defined $location and $location) {
    my $uri = URI->new($location);
    my $eCheck = "http://" . $uri->host . "%";
    my $sth = $dbh->prepare("SELECT URL FROM Exclude WHERE URL LIKE ?");
    $sth->execute($eCheck);
    my ($rc) = $sth->fetchrow_array;
    if (defined $rc and $rc) {
      $urlExcluded = 1;
    } else {
      $urlExcluded = 0;
    }
  } else {
    $urlExcluded = 1;
  }
  return $location;
}

