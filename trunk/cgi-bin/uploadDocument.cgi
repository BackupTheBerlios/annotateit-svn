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
use User;
use IO::File;
use Document;
use DocumentAccess;
use Date::Calc qw(Today_and_Now);
use CGI::Carp 'fatalsToBrowser';
use CGI;
our $C = CGI->new;
$ENV{TMPDIR} = "/tmp";
our @chars = ('A'..'Z','a'..'z',0..9);
our $config = Config::Simple->new("../etc/annie.conf");
our $dbh = &widgets::dbConnect($config);
our $authInfo = &auth::authenticated($dbh,\$C);
our $scriptdir = $config->param("server.scriptdirectory");
our $serverURL = $config->param("server.url");
our $docURL = $config->param("server.documenturl");
our $action = $C->param("action") || "";
our $docDir = $config->param("server.documentdirectory");
our $template = Template->new( RELATIVE => 1,
			       INCLUDE_PATH => "../templates");
our $docID = $C->param("DocumentID") || 0; # coming from manageDocuments.cgi
our $document = "";
our $outboxStatus = $C->param("OutboxStatus") || "";
if ($docID) {
  $document = Document->load(dbh => $dbh, ID=> $docID);
}
our $AssignmentID = $C->param("AssignmentID") || "";
if (!$authInfo->{LoggedIn}) {
  my $vars = { scriptdir => $scriptdir,
	       randomValue => &auth::randomValue(),
	       formAction => "uploadDocument.cgi",
	       hiddenVar => [ 
			     {paramName => "action",paramValue => $action}]
	       };
  print $C->header();
  $template->process("loginScriptForm.html",$vars) || die $template->error();
  exit;
}
our $user = User->load( dbh => $dbh,
		       ID => $authInfo->{UserID} );
&unauthorized("uploadGeneral") if (! $user->hasPrivilege("Other.UploadDocument")
		  and ! $user->hasPrivilege("Own.UploadDocument") );
if ($action eq "Save File") {
  &saveFile;
} elsif ($action eq "edit") {
  &editDocument;
} elsif ($action eq "Save Edit") {
  &saveFile;
} elsif ($action eq "outboxMod") {
  &saveFile;
} else {
  &blankForm;
}
sub saveDocument {
  my $vars = { scriptdir => $scriptdir,
	       formAction => "uploadDocument.cgi",
	       };
  my $user = User->load( dbh => $dbh,
			 ID => $authInfo->{UserID} );
  if ($AssignmentID) {
    my $assignment = Assignment->load( dbh => $dbh,
				       ID => $AssignmentID );
    $vars->{Assignment} = $assignment->getDisplayData;
    $vars->{HasAssignmentID} = 1;
  } else {

    my $assignments = $user->getAssignmentDisplayData;
    $vars->{Assignments} = $assignments;
    $vars->{HasAssignmentID} = "";
  }
  $vars->{Groups} = $user->getGroupDisplayData;
  $vars->{Action} = "Blank Form";
  print $C->header(-cookie=>$authInfo->{cookie});
  $template->process("UploadDocumentForm.html",$vars) or die $template->error();
  exit;
}


sub uploadDocument {
  my $rv = {};
  my $filename = $C->param("File");
  my $fh = $C->upload("File");
  my $contentType = $C->uploadInfo($filename)->{'Content-Type'};
  if ($contentType eq "application/msword"
      or $filename =~ /\.doc$/ ) {
    $rv = &wordDocument(filename => $filename,
			fh => $fh);
  } elsif ($contentType eq "application/rtf"
	   or $contentType eq "text/rtf"
	   or $filename =~ /\.rtf$/ ) {
    $rv = &rtfDocument(filename => $filename,
		       fh => $fh);
  } elsif ($contentType eq "text/html"
	   or $filename =~ /\.(html|htm)$/) {
    $rv = &htmlDocument(filename => $filename,
			fh => $fh);
  } elsif ($contentType eq "text/plain" or
	   $filename =~ /\.(asc|txt)$/ ) {
    $rv = &textDocument(filename => $filename,
			fh => $fh);
  } else {
    &documentNotRecognized;
  }
  return $rv;
}

sub wordDocument {
  my (%args) = @_;
  my $Type = "MS-Word";
  my $fh = $args{fh};
  my $filename = $args{filename};
  my $filenameRoot = &rfg();
  my $WordFilename = "$docDir/nat/$filenameRoot.doc";
  &readFile($fh, $WordFilename);
  my $HtmlFilename = "$filenameRoot.html";
  my $TextFilename = "$docDir/text/$filenameRoot.txt";
  `/usr/local/bin/wvHtml $WordFilename --targetdir=$docDir/html $HtmlFilename`;
  `/usr/local/bin/wvText $WordFilename $TextFilename`;
  return [$filenameRoot, $Type];
}
sub rtfDocument {
  my (%args) = @_;
  my $Type = "RTF";
  my $fh = $args{fh};
  my $filename = $args{filename};
  my $filenameRoot = &rfg();
  my $RTFFilename = "$docDir/nat/$filenameRoot.rtf";
  &readFile($fh, $RTFFilename);
  my $HTMLFilename = "$docDir/html/$filenameRoot.html";
  my $TextFilename = "$docDir/text/$filenameRoot.txt";
  my $HTML = `/usr/local/bin/unrtf --html --nopict $RTFFilename`;
  $HTML =~ s/\<!--.*?--\>//sg;
  my $HTMLTempFH = IO::File->new($HTMLFilename, "w");
  if (defined $HTMLTempFH) {
    print $HTMLTempFH $HTML;
    $HTMLTempFH->close();
  } else {
    die "Could not open $HTMLFilename for write";
  }
  my $text = `/usr/local/bin/unrtf --text --nopict $RTFFilename`;
  my @lines = split /\n/, $text;
  $text = "";
  for my $line (@lines) {
    next if ($line =~ /^\#\#\# /);
    $text .= "$line\n";
  }
  my $TextFH = IO::File->new($TextFilename, "w");
  if (defined $TextFH) {
    print $TextFH $text;
    $TextFH->close();
  } else {
    die "Could not open $TextFilename for write";
  }
  return [$filenameRoot, $Type];
}
sub htmlDocument {
  my %args = @_;
  my $Type = "HTML";
  my $fh = $args{fh};
  my $filename = $args{filename};
  my $filenameRoot = &rfg();
  my $natName = "$docDir/nat/$filenameRoot.html";
  my $textName = "$docDir/text/$filenameRoot.txt";
  my $htmlName = "$docDir/html/$filenameRoot.html";
  &readFile($fh, $natName);
  `cp $natName $htmlName`;
  system("/usr/bin/lynx -dump $htmlName > $textName");
  return [$filenameRoot, $Type];
}
sub textDocument {
  my %args = @_;
  my $Type = "Text";
  my $fh = $args{fh};
  my $filename = $args{filename};
  my $filenameRoot = &rfg();
  my $natName = "$docDir/nat/$filenameRoot.txt";
  my $htmlName = "$docDir/html/$filenameRoot.html";
  my $textName = "$docDir/text/$filenameRoot.txt";
  &readFile($fh, $natName);
  `cp $natName $textName`;
  &TextToHTML($textName,$htmlName);
  return [$filenameRoot, $Type];
}
sub makeDoc {
  my ($ft) = @_;
  my ($filename, $Type) = @{$ft};
  my $isOwner = 0;
  if (defined $document and ref($document) eq "Document") {
    if ($document->OwnerID == $user->getID) {
      $isOwner = 1;
    }
  } else {
    $document = Document->new(dbh => $dbh);
    $isOwner = 1;
  }
  my $docAccess = DocumentAccess->new(dbh => $dbh);
  $document->AssignmentID($AssignmentID);
  my $documentTitle = $C->param("DocumentTitle") || "untitled";
  $documentTitle = &widgets::scrub($documentTitle);
  my @security = $C->param("DocumentSecurity");
  unless (@security) { @security = ("Private"); }
  my $GroupID = '';
  my $overallSec = "";
  for my $security (@security) {
    if ($security ne "Private" and $security ne "Public") {
      $overallSec = "Group";
    }
  }
  if (!$overallSec) {
    for my $security (@security) {
      if ($security eq "Private") {
	$overallSec = "Private";
      }
    }
    if (!$overallSec) {
      $overallSec = "Public";
    }
  }
  my $state = $C->param("DocumentState") || "---";
  if ($isOwner) {
    $document->Security($overallSec);
    $document->UploadDate(&UploadDate());
    $document->State($state);
    $document->Filename($filename);
    $document->Type($Type);
    $document->OwnerID($authInfo->{UserID});
    $document->Title($documentTitle);
    warn "Document Title: " . $document->Title;
    if ($docID) {
      warn "Hello!";
      $document->update;
    } else {
      $document->save;
    }
    my $docID = $document->ID;
    $docAccess->setDocumentID($docID);
    $docAccess->setGroups(User => $user,Groups=>\@security);

    for my $security (@security) {
      $docAccess->setGroupID($security);
      $docAccess->addAccess;
    }
  }
  if ($outboxStatus eq "Outbox") {
    $document->MoveToOutbox(UserID => $user->getID);
  } else {
    $document->MoveToInbox(UserID => $user->getID);
  }
  $document->update; # have to have a docID to be here, 
                # which is why I don't need to save first.

  my $rv = $document->getDisplayData( UserID => $user->getID,
				      Config => $config);

  return $rv;
}
sub UploadDate {

  my ($year, $month, $day, $hour, $min, $sec) = Today_and_Now();
  my $date = "$year-$month-$day $hour:$min:$sec";
  return $date;

}
sub readFile {
  my ($fhIn, $newFilename) = @_;
  my $fhOut = IO::File->new($newFilename,'w');
  if (defined $fhOut) {
    my ($totalbytes, $bytesread, $buffer) = (0,0,"");
    while ($bytesread=read($fhIn, $buffer, 1024)) {
      print $fhOut $buffer;
    }
  } else {
    die "Couldn't open $newFilename";
  }
}


sub TextToHTML {
  my ($TextFN, $HTMLFN) = @_;
  my $textFH = IO::File->new($TextFN,'r');
  my $htmlFH = IO::File->new($HTMLFN,'w');
  if (defined $textFH) {
    my $text = "";
    while (defined (my $line = <$textFH>)) {
      $text .= $line;
    }
    $text =~ s/(?:\r)?\n/<br \/>/sg;
    $text = qq(<html><head></head><body>$text</body></html>);
    if (defined $htmlFH) {
      print $htmlFH $text;
    } else {
      die "Couldn't open $HTMLFN for write";
    }
  } else {
    die "Couldn't open $TextFN for write";
  }
}



sub rfg {
  # Raw Filename Generator
   my $rv = "";
   if ($docID) {
     my $document= Document->load(dbh => $dbh,ID => $docID);
     $rv = $document->getFilename;
   } else {
     while (! $rv or -e "$docDir/$rv.html") {
       for (1..12) {
	 $rv .= $chars[rand(@chars)];
       }
     }
   }
   return $rv;
}

sub unauthorized {
  my ($error) = @_;
  my %errors = ( uploadGeneral => qq(You do not have privileges to
				     upload documents to assignments. You can
				     remedy that by purchasing privileges.),
		 NotMemberOrOwner => qq(You are not a member of the group that
					assignment belongs to.  You can 
					probably join the group, though.)
	       );
  my $vars = {};
  $vars->{ErrorText} = $errors{$error};
  $vars->{Error} = "UploadError";
  $vars->{EnglishError} = 'Not Authorized';
  print $C->header(-cookie=>$authInfo->{cookie});
  $template->process("Error.html",$vars) or die $template->error;
  exit;
}

sub editDocument {
  
  my $doc = Document->load(dbh => $dbh, ID => $docID);
  my $vars = {};
  $vars->{Groups} = $user->getGroupDisplayData;
  $vars->{Action} = "SaveEdit";
  $vars->{Assignments} = $user->getAssignmentDisplayData;
  $vars->{scriptdir} = $scriptdir;
  $vars->{serverurl} = $serverURL;
  $vars->{formAction} = "uploadDocument.cgi";
  $vars->{Document} = $document->getDisplayData(UserID => $user->getID,
						Config=>$config);
  $vars->{isOwner} = ($document->OwnerID == $user->getID);
  print $C->header(-cookie=>$authInfo->{cookie});
  $template->process("UploadDocumentForm.html",$vars) || die $template->error;
  exit;
}

sub saveFile {
  if ($AssignmentID) {
    my $assignment = Assignment->load(ID => $AssignmentID,
				      dbh => $dbh);
    if (! $user->hasGroup($assignment->getGroupID)
	and $user->getID != $assignment->getUserID) {
      &unauthorized("NotMemberOrOwner");
    }
  }
  my $ft;
  if ($C->param("File")) {
    $ft = &uploadDocument;
  } else {
    $ft = [$document->Filename,$document->Type];
  }
  my $rv2 = &makeDoc($ft);
  my %resultValues = ( outboxMod => "Outbox Modification" );
  my $vars = { scriptdir => $scriptdir,
	       formAction => "uploadDocument.cgi",
	       Result => "Success",
	       ResultValue => $resultValues{$action},
	       Document => $rv2};
  print $C->header(-cookie=>$authInfo->{cookie});
  $template->process("UploadDocumentForm.html", $vars) or die $template->error();
  exit;
}
sub blankForm {
  my $vars = {};
  if ($AssignmentID) {
    my $assignment = Assignment->load(dbh => $dbh, ID=>$AssignmentID);
    $vars->{Assignment} = $assignment->getDisplayData;
  }
  $vars->{Groups} = $user->getGroupDisplayData;
  $vars->{Action} = "Blank Form";
  $vars->{scriptdir} = $scriptdir;
  $vars->{serverurl} = $serverURL;
  $vars->{formAction} = "uploadDocument.cgi";
  $vars->{HasAssignmentID} = $AssignmentID;
  $vars->{Assignments} = $user->getAssignmentDisplayData;
  print $C->header(-cookie=>$authInfo->{cookie});
  $template->process("UploadDocumentForm.html",$vars) || die $template->error;

  
}
