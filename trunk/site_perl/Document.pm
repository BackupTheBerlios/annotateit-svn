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
package Document;
use strict;
use Digest::MD5 qw(md5_hex);
use DocumentAccess;
use Rubric;			
use Assignment;
use EvalVector;
use IO::File;
use base qw( Object );
use Carp;
use fields qw( Type AssignmentID UploadDate Filename Security State );
sub new {

  my ($class,%args) = @_;
  my $self = bless {}, ref($class) || $class;
  $self->Object::_init(%args);
  $self->_init(%args);
  return $self;
}
sub _init {
  my ($self, %args) = @_;
  return if ($self->{_init}{__Document__}++);
  $self->mk_accessors($self->show_fields);
  for ($self->show_fields) {
    next if $self->is_inherited($_);
    $self->{$_} = $args{$_};
  }
  return $self;
}

sub setSecurity {
  my ($self, $p) = @_;
  $p =~ s/[^A-Za-z0-9_ \?-]//g;
  $self->{Security} = $p;
}
sub setState {
  my ($self, $p) = @_;
  $p =~ s/[^A-Za-z0-9_ \?-]//g;
  $self->{State} = $p;
}


sub load {

  my ($class, %params) = @_;
  my $self = bless {}, ref($class) || $class;
  $self->Object::_init(%params);
  $self->_init(%params);
  $self->loadDescription;
  my $sth = $self->{dbh}->prepare("SELECT CONCAT(user.LastName,', ',user.FirstName), d.OwnerID, d.AssignmentID, d.UploadDate, d.Filename, d.Type, d.Security, d.State FROM Document as d, user WHERE d.ObjectID = ? AND d.OwnerID = user.ID");
  $sth->execute($self->ID);
  ($self->{UserName},
   $self->{OwnerID},
   $self->{AssignmentID},
   $self->{UploadDate},
   $self->{Filename},
   $self->{Type},
   $self->{Security},
   $self->{State}) =  $sth->fetchrow_array;
  if ($self->{AssignmentID}) {
    $sth = $self->{dbh}->prepare("SELECT a.Title, a.DueDate FROM Assignment as a WHERE a.ID = ?");
    $sth->execute($self->AssignmentID);
    ($self->{AssignmentTitle},
     $self->{DueDate}) = $sth->fetchrow_array;
  } else {
    $self->{AssignmentTitle} = "";
    $self->{DueDate} = "";
  }
  return $self;
}
sub MoveToOutbox {
  my ($self,%params) = @_;
  my $userID = $params{UserID};
  return if ($self->outboxStatus($userID) eq "Finished");
  my $sth = $self->{dbh}->prepare("INSERT INTO Outbox (DocumentID,UserID) VALUES (?,?)");
  $sth->execute($self->ID,$userID);
}
sub MoveToInbox {
  my ($self,%params) = @_;
  unless ($self->ID and $params{UserID}) {
    croak "DocumentID and UserID are both necessary";
  }
  my $userID = $params{UserID};
  my $sth = $self->{dbh}->prepare("DELETE FROM Outbox WHERE DocumentID = ? AND UserID = ?");
  $sth->execute($self->ID,$userID);
}
sub save {
  my ($self) = @_;
  $self->saveDescription;
  my $sql = "INSERT INTO Document (ObjectID, OwnerID, AssignmentID, UploadDate, Filename, Type, Security, State) VALUES (?,?,?,?,?,?,?,?)";
  my $sth = $self->{dbh}->prepare($sql);
  $sth->execute($self->ID,
		$self->OwnerID,
		$self->AssignmentID,
		$self->UploadDate,
		$self->Filename,
		$self->Type,
		$self->Security,
		$self->State);
  return $self;
}
sub update {
  my ($self) = @_;
  $self->updateDescription;
  my $sth = $self->{dbh}->prepare("UPDATE Document SET OwnerID = ?, AssignmentID = ?, UploadDate = ?, Filename = ?, Security = ?, State = ? WHERE ObjectID = ?");
  $sth->execute($self->OwnerID,
		$self->AssignmentID,
		$self->UploadDate,
		$self->Filename,
		$self->Security,
		$self->State,
		$self->ID);
  return $self;
}
sub outboxStatus {
  my ($self, $userID) = @_;
  unless ($userID) {
    warn join ': ', caller;
    die "No userID passed to outboxStatus";
  }
  my $sth = $self->{dbh}->prepare("SELECT DocumentID FROM Outbox WHERE UserID = ? AND DocumentID = ?");
  $sth->execute($userID,$self->ID);
  my ($rv) = $sth->fetchrow_array;
  $rv ||= 0;
  return ($rv == $self->ID) ? "Finished" : "Not Finished";
}
sub getRubricType {
  my ($self) = @_;
  my $aid = $self->AssignmentID;
  if (defined $aid and $aid) {
    my $a = Assignment->load( dbh => $self->{dbh},
			      ID => $aid );
    my $rIDs = $a->getRubricIDs({Secure => 1});
    my %types = ();
    for my $rid (@{$rIDs}) {
      my $r = Rubric->load( dbh => $self->{dbh},
			    ID => $rid);
      $types{$r->Type}++;
    }
    my $type = "";
    for my $key (keys %types) {
      if ($type) {
	if ($types{$type} < $types{$key}) {
	  $type = $key;
	}
      } else {
	$type = $key;
      }
    }
    return $type;
  }
  return "Average";
}
sub getDisplayData {
  my ($self, %args) = @_;
  my $userID = $args{UserID};
  my $outboxStatus = "";
  if (defined $userID) {
    $outboxStatus = $self->outboxStatus($userID);
  }
  croak "Please pass a config object to Document.pm for doc->getDisplayData" unless (defined $args{Config});
  my $serverURL = $args{Config}->{server}{url};
  my $docURL = $args{Config}->{server}{documenturl};
  my $docDir = $args{Config}->{server}{documentdirectory};
  my $htmlDoc = $self->Filename . ".html";
  my $textDoc = $self->Filename . ".txt";
  my $type = $self->Type;
  my $natName = $self->Filename;
  my $docAccess = DocumentAccess->new(dbh => $self->{dbh});
  my $rubricType = $self->getRubricType;
  $docAccess->setDocumentID($self->ID);
  if ($type eq "MS-Word") {
    $natName .= ".doc";
  } elsif ($type eq "RTF") {
    $natName .= ".rtf";
  } elsif ($type eq "HTML") {
    $natName .= ".html";
  } elsif ($type eq "Text") {
    $natName .= ".txt";
  }
  my $fh = IO::File->new("$docDir/nat/$natName","r");
  my $ud = $self->UploadDate;
  my $sysSig = md5_hex("$htmlDoc$ud");
  my $ctx = Digest::MD5->new();
  eval {$ctx->addfile($fh)};
  my $docSig = $ctx->hexdigest;
  my $rv = {ID => $self->ID,
	    OutboxStatus => $outboxStatus,
	    AccessGroups => $docAccess->getGroupInfo, 
	    Security => $self->Security,
	    State => $self->State,
	    OwnerName => $self->{UserName},
	    RawFilename => $self->Filename,
	    AssignmentTitle => $self->{AssignmentTitle},
	    AssignmentID => $self->AssignmentID,
	    Type => $type,
	    DueDate => $self->{DueDate},
	    Title => $self->{Title},
	    OwnerID => $self->OwnerID,
	    HTMLURL => "$serverURL$docURL/html/$htmlDoc",
	    TextURL => "$serverURL$docURL/text/$textDoc",
	    NativeURL => "$serverURL$docURL/nat/$natName",
	    UploadDate => $self->UploadDate,
	    SystemSignature => $sysSig,
	    DocumentSignature => $docSig,
	    EvalVectors => $self->getEvalVectorDisplayData,
	    RubricType => $rubricType};
  return $rv;
}
sub setEvaluation {
  my ($self, $p) = @_;

  my $sth = $self->{dbh}->prepare("DELETE FROM Evaluation WHERE OwnerID = ? AND ObjectID = ? AND ObjectClass = 'Document'");
  my $uID = $p->{CurrentUser}->getID;
  my $oID = $self->ID;
  my $objectType = 'Document';

  $sth->execute($uID,$oID);
  $sth = $self->{dbh}->prepare("INSERT INTO Evaluation (OwnerID, ObjectID, ObjectClass, EvalVectorID, Value, Weight) VALUES (?,?,?,?,?,?)");

  for my $ev (@{$p->{Evaluation}}) {
    my $value = $ev->{Value};
    my $weight = $ev->{Weight};
    my $evID = $ev->{ID};
    $weight ||=1;
    $sth->execute($uID,$oID,$objectType, $evID,$value,$weight);
  }
}

sub getEvaluations {
  my ($self, $p) = @_;
  my $aid = $self->AssignmentID;
  return [] unless (defined $aid and $aid);
  my $sth = $self->{dbh}->prepare("SELECT EvalVectorID, Value, OwnerID, Weight FROM Evaluation WHERE ObjectID = ? AND ObjectClass = 'Document'");
  $sth->execute($self->ID);
  my $rubricType = $self->getRubricType;
  my @rv = ();
  my $count = 0;
  my $sum = 0;
  my $maxValueSum = 0;
  while (my ($evID, $value, $userID,$weight) = $sth->fetchrow_array) {
    my $ev = EvalVector->load( dbh => $self->{dbh},
			       ID => $evID);
    my $hash = $ev->getDisplayData;
    $sum += $value * $weight;
    $count += $weight;
    my $maxValue = $ev->MaximumValue;
    $maxValueSum += $maxValue * $weight;
    $hash->{Weight} = $weight;
    $hash->{EvaluatorID} = $userID;
    $hash->{EvaluationValue} = $value;
    push @rv, $hash;
  }
  if ($rubricType eq "Average") {
    my $overallScore = 0;
    eval { $overallScore = $sum / $count };
    unless ($@) {
      $overallScore = sprintf "%4.1f",$overallScore;
    }
    push @rv, {  "Title" => "Overall Score",
		 "EvaluationValue" => $overallScore,
		 MaxPossible => $maxValueSum / $count
	      };
  } else {
    push @rv, { Title => "Overall Score",
		EvaluationValue => $sum,
		MaxPossible => $maxValueSum
	      };
  }
  return \@rv;
}
sub getOverallScore {
  my ($self) = @_;
  my $dd = $self->getEvaluations;
  my $rv="";
  for my $eval (@{$dd}) {
    if ($eval->{Title} eq "Overall Score") {
      $rv = $eval->{EvaluationValue};
    }
  }
  return $rv;
}
sub getEvalVectorDisplayData {
  my ($self) = @_;
  my $aid = $self->AssignmentID;
  my $a = Assignment->load( dbh => $self->{dbh},
			    ID => $aid );
  my $rIDs = $a->getRubricIDs({Secure => 1});
  my @rQmarks = ("?")x@{$rIDs};
  my $rQmarks = "(" . (join ",", @rQmarks) . ")";
  my $ids = $self->getEvalVectorIDs;
  my @rv = ();

  # first the rubric eval vectors
  if (@{$rIDs}) {
    my $sth_rubric = $self->{dbh}->prepare("SELECT VectorWeight FROM ObjectMap WHERE FromObjectClass = 'EvalVector' AND FromObjectID = ? AND ToObjectClass = 'Rubric' and ToObjectID IN $rQmarks");
    for my $id (@{$ids}) {
      my $ev = EvalVector->load(dbh => $self->{dbh},
				ID => $id);
      my $hash = $ev->getDisplayData;
      $sth_rubric->execute($id,@{$rIDs});
      while (my ($weight) = $sth_rubric->fetchrow_array) {
	my %nHash = %{$hash};
	$nHash{Weight} = $weight;
	push @rv, \%nHash;
      }
    }
  }
  # get eval vector stringers associated with assignment;
  my $sth_weight = $self->{dbh}->prepare("SELECT VectorWeight FROM ObjectMap WHERE FromObjectClass = 'EvalVector' AND FromObjectID = ? AND ToObjectClass = 'Assignment' AND ToObjectID = ?");
  for my $id (@{$ids}) {
    my $ev = EvalVector->load(dbh => $self->{dbh},
			      ID => $id);
    my $hash = $ev->getDisplayData;
    $sth_weight->execute($id,$aid);
    my $weight = $sth_weight->fetchrow_array;
    next unless (defined $weight and $weight != 0);
    $hash->{Weight} = $weight;
    push @rv, $hash;
  }
  # get eval vector stringers associated with document;
  $sth_weight = $self->{dbh}->prepare("SELECT VectorWeight FROM ObjectMap WHERE FromObjectClass = 'EvalVector' AND FromObjectID = ? AND ToObjectClass = 'Document' AND ToObjectID = ?");
  for my $id (@{$ids}) {
    my $ev = EvalVector->load(dbh => $self->{dbh},
			      ID => $id);
    my $hash = $ev->getDisplayData;
    $sth_weight->execute($id,$self->ID);
    my ($weight) = $sth_weight->fetchrow_array;
    next unless (defined $weight and $weight != 0);
    $hash->{Weight} = $weight;
    push @rv, $hash;
  }
   
  return \@rv;
}

sub getEvalVectorIDs {
  my ($self) = @_;
  # first get evals associated with the assignment
  my $aid = $self->AssignmentID;
  my $docID = $self->ID;
  my $evalVectorIDs = [];
  my $evWeights = {};
  my $rEVIDs = [];
  if (defined $aid and $aid) {
    my $a = Assignment->load( dbh => $self->{dbh},
			      ID => $aid );
    ($evalVectorIDs,$evWeights) = $a->getEvalVectorIDs;
    my $rIDs = $a->getRubricIDs({Secure => 1});
    for my $rID (@{$rIDs}) {
      my $r = Rubric->load( dbh => $self->{dbh},
			    ID => $rID );
      push @{$rEVIDs}, @{$r->getObjectEvalVectorIDs({Secure => 1})};
    }
  }
  my ($evIDs) = $self->getObjectEvalVectorIDs({Secure => 1});
  my @evs = (@{$evIDs},@{$evalVectorIDs},@{$rEVIDs});
  my %distinctVectors = ();
  @distinctVectors{@evs} = (1)x@evs;
  my @distinctVectorIDs = sort {$a <=> $b} ( keys %distinctVectors );
  # Note! These vector ids are not the same as the map.  These are content
  # only and have no relationship information in them.
  return \@distinctVectorIDs;
}
sub getStyleStatistics {
  my ($self) = @_;
  my $docDir = $main::docDir;
  my $filename = "$docDir/text/" . $self->Filename . ".txt";
  my $stats = `/usr/bin/style $filename`;
  my @lines = split /\n/, $stats;
  return [ { Name => "No stats for this file"} ] unless (defined $lines[5]);
  my $holder={};
  my ($Kincaid) = $lines[1] =~ /\s+Kincaid: ([\d\.]+)/;
  my ($ARI) = $lines[2] =~ /\s+ARI: ([\d\.]+)/;
  my ($Coleman) = $lines[3] =~ /\s+Coleman-Liau: ([\d\.]+)/;
  my ($Flesch) = $lines[4] =~ /\s+Flesch Index: ([\d\.]+)/;
  my ($Fog) = $lines[5] =~ /\s+Fog Index: ([\d\.]+)/;
  my ($Lix, $LixSchoolYear) = $lines[6] =~ /\s+Lix: ([\d\.]+) = school year ([\d\.]+)/;
  my ($SMOG) = $lines[7] =~ /\s+SMOG-Grading: ([\d\.]+)/;
  my ($chars) = $lines[9] =~ /\s+([\d]+) characters/;
  my ($words, $awl, $as) = $lines[10] =~ /\s+(\d+) words, average length ([\d\.]+) characters = ([\d\.]+) syllables/;
  my ($sentences,$asl) = $lines[11] =~ /\s+(\d+) sentences, average length ([\d\.]+) words/;
  my ($ssp,$ss) = $lines[12] =~ /\s+([\d\.]+)\% \((\d+)\) short sentences/;
  my ($lsp,$ls) = $lines[13] =~ /\s+([\d\.]+)\% \((\d+)\) long sentences/;
  my ($paragraphs, $apl) = $lines[14] =~ /\s+(\d+) paragraphs, average length ([\d\.]+) sentences/;
  my ($questionP,$questions) = $lines[15] =~ /\s+(\d+)\% \((\d+)\) questions/;
  my ($psp, $passives) = $lines[16] =~ /\s+(\d+)\% \((\d+)\) passive sentences/;
  my ($longestS,$shortestS) = $lines[17] =~ /\s+longest sent (\d+) wds at sent .* shortest sent (\d+) wds at sent/;
  my ($ToBeVerbs,$AuxilliaryVerbs) = $lines[20] =~ /\s+to be \((\d+)\) auxilliary \((\d+)\)/;
  my ($ConjP, $Conj,$PronounsP,$Pronouns,$PrepP,$Prep) = $lines[22] =~ /\s+conjunctions (\d+)\% \((\d+)\) pronouns (\d+)\% \((\d+)\) prepositions (\d+)\% \((\d+)\)/;
  my ($NomP,$Nom) = $lines[23] =~ /\s+nominalizations (\d+)\% \((\d+)\)/;
  my ($PronounSB,$IPronounSB,$ArticleSB) = $lines[25] =~ /\s+pronoun \((\d+)\) interrogative pronoun \((\d+)\) article \((\d+)\)/;
  my ($SConjSB,$conjSB, $PrepSB) = $lines[26] =~ /\s+subordinating conjunction \((\d+)\) conjunction \((\d+)\) preposition \((\d+)\)/;
  my $rv1 = [ { Name => "Readability Grades",
		Values => [
			   { Label => "Kincaid", Value => $Kincaid },
			   { Label => "ARI", Value => $ARI },
			   { Label => "Coleman-Liau", Value => $Coleman },
			   { Label => "Flesch Index", Value => $Flesch },
			   { Label => "Fog Index", Value => $Fog },
			   { Label => "Lix Index", Value => $Lix },
			   { Label => "Lix School Year", Value => $LixSchoolYear },
			   { Label => "SMOG-Grading", Value => $SMOG }
			  ]
	      },
	      { Name => "Sentence Information",
		Values => [
			   { Label => "Number of Characters", Value=>$chars},
			   { Label => "Number of Words", Value => $words},
			   { Label => "Average Word Length", Value => $awl},
			   { Label => "Average Syllables per Word", Value => $as},
			   { Label => "Number of Sentences", Value => $sentences },
			   { Label => "Average Sentence Length", Value => $asl },
			   { Label => "Short Sentences Percent", Value => $ssp },
			   { Label => "Number of Short Sentences", Value => $ss },
			   { Label => "Long Sentences Percent", Value => $lsp },
			   { Label => "Number of Long Sentences", Value => $ls },
			   { Label => "Number of Paragraphs", Value => $paragraphs},
			   { Label => "Average Paragraph Length (Sentences)", Value => $apl},
			   { Label => "Questions Percent", Value => $questionP },
			   { Label => "Number of Questions", Value => $questions },
			   { Label => "Passive Sentences Percent", Value => $psp },
			   { Label => "Number of Passive Sentences", Value => $passives },
			   { Label => "Length of Longest Sentence", Value => $longestS },
			   { Label => "Length of Shortest Sentence", Value=> $shortestS }
			  ]
	      },
	      { Name => "Word Usage Information",
		Values => [
			   { Label => "To Be Verb Forms", Value => $ToBeVerbs },
			   { Label => "Auxiliary Verb Forms", Value => $AuxilliaryVerbs },
			   { Label => "Conjunctions Percent", Value => $ConjP },
			   { Label => "Number of Conjunctions", Value => $Conj },
			   { Label => "Pronouns Percent", Value => $PronounsP },
			   { Label => "Number of Pronouns", Value => $Pronouns },
			   { Label => "Prepositions Percent", Value => $PrepP },
			   { Label => "Number of Prepositions", Value => $Prep },
			   { Label => "Nominalizations Percent", Value => $NomP },
			   { Label => "Number of Nominalizations", Value => $Nom }
			  ]
	      },
	      { Name => "Sentence Beginnings",
		Values => [
			   { Label => "Pronoun", Value => $PronounSB },
			   { Label => "Interrogative Pronoun", Value => $IPronounSB },
			   { Label => "Article", Value => $ArticleSB },
			   { Label => "Subordinating Conjunction", Value => $SConjSB },
			   { Label => "Preposition", Value => $PrepSB }
			  ]
	      }
	    ];
  my $rv2 = {};
  for my $category (@{$rv1}) {
    my $n = $category->{Name};
    for my $stat (@{$category->{Values}}) {
      my $l = $stat->{Label};
      $rv2->{$n}{$l} = $stat->{Value};
    }
  }
  return wantarray ? ($rv1,$rv2) : $rv1;
}
1;
