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
package Match;
use strict;

sub checkPhrase {
  my ($args) = @_;
  my $selectedtext = $args->{selectedtext};
#  warn "\n\n$selectedtext\n";
  my $context = $args->{context};
  my $content = $args->{content};
  my $contextRE = $context;
  $content = &cleanContent($content);
  for my $re ($selectedtext,$contextRE) {
#    warn "\n$re\n";
    $re =~ s/[^[:alnum:]\s]/./sg;
    # $re =~ s/([\w\.]+)([^\w\.]+)/$1\\b$2/sg;
    $re =~ s/\s+/(?:(?:\\{\\{[^\\}]+\\}\\})*|(?:\\s+)|(?:<[^>]*>+)+)+/sg;
    $re =~ s/\\b\./\./g;
    $re =~ s/\.\\b/\./g;
  }
  our $numMatches = &checkPhraseMatch($content,$selectedtext);
#  warn $content;
#  warn "$selectedtext\n\n";
#  warn "$contextRE\n\n\n\n";
#  warn "Phrase Matches: $numMatches\n";

  if ($numMatches == 0) {
    # phrase isn't in the document requested
    warn "Not in document: $selectedtext\n";
      return {Ok => 0,
	      error => "That complete word or phrase with complete words isn't in the document."};
  } elsif ($numMatches == 1) {
#    warn "Exactly one match: $selectedtext\n";
    # phrase is in the document exactly 1 time
    return { Ok => 1,
	     selectedtextRE => $selectedtext,
	     contextRE => $contextRE };
  } else {
#    warn "More than one match: $selectedtext\n";
    our $contextMatches = &checkPhraseMatch($content,$contextRE);
#    warn "Context RE: $contextRE\n";
#    warn "Context Matches: $contextMatches\n";
    if ($contextMatches == 0) {
      # there's no context match.
#      warn "The context doesn't match: $contextRE\n";
      return {error => "That context (complete word or phrase with complete words) doesn't exist in the document.",
	      phraseTooNarrow => 1,
	      Ok => 0};
    } elsif ($contextMatches == 1) {
#      warn "There is exactly one context match: $contextRE\n";
      # there's exactly one context match
      unless ($context =~ /$selectedtext/s) {
	return {error => "The context doesn't contain the specified selected text (complete word or phrase with complete words).",
		phraseTooNarrow => 1,
		Ok => 0
	       };
      }
      # and it contains the selected text
      my ($contentMatch) = $content =~ /($contextRE)/s;
      unless ($contentMatch =~ /$selectedtext/s) {
	return {error => "Although the supplied context contains the supplied selected text, there seems to be a problem with getting the selected text to match in the matched content.",
		phraseTooNarrow => 1,
		Ok => 0};
	# exit;
      }
      return { Ok => 1,
	       selectedtextRE => $selectedtext,
	       contextRE => $contextRE};
    } else {
      # there's more than one context that matches.
#      warn "There is more than one context match: $contextRE\n";
      my @cMatches = $content =~ /$contextRE/sg;
      my $matches = 0;
      for my $contextM (@cMatches) {
	my $m = "";
	($m) = $contextM =~ /($selectedtext)/s;
	if ($m) {
	  $matches++;
	}
      }
      if ($matches == 1) {
#	warn "There is exactly one match inside multiple contexts: $contextRE\n";
	return { Ok => 1 };
      } else {
	return {error => "The context is not unique and the phrase appears more than once, even having been contextualized.  Lengthen the context a little bit.  Either start earlier, or end later, or both.",
		phraseTooNarrow => 1,
		Ok => 0};
      }
    }
  }
}

sub checkPhraseMatch {
  my ($content,$phrase) = @_;
  my @matches = ();
  @matches = $content =~ /$phrase/sg;
  return $#matches + 1;
}
sub cleanContent {
  my ($content) = @_;
  my %replacement = ( "8217" => "'",
		      "039" => "'",
		      "8220" => '"',
		      "8221" => '"',
		      "8230" => "...",
		      "quot" => '"',
		      "amp" => '&',
		      "nbsp" => " ",
		      "middot" => " o ",
		      "copy" => "(C)",
		      "apos" => "'",
		      "raquo" => "_");
  my (@match) = $content =~ /\&\#?([\d]+?|[\w]+)\;/g;
  my %matches = ();
  for my $m (@match) {
    $matches{$m}++;
  }
  for my $m (keys %matches) {
    warn "Undefined character entity: $m" unless exists $replacement{$m};
  }
  $content =~ s/\&\#?([\d]+?|[\w]+?)\;/$replacement{$1}/gx;
  return $content;

}
1;

