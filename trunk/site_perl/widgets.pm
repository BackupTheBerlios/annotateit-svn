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
#!/usr/local/bin/perl -w
use strict;
package widgets;
use DBI;
use HTML::Scrubber;


sub dbConnect {
  my ($config) = @_;
  unless (defined $config) {
    my ($a, $b, $c) = caller();
    die "Config is not defined: $a: $b: $c\n";
  }
  my $user = $config->param("database.user") || die "[database] user=\"\" is not defined in configuration file";
  my $password = $config->param("database.password") || die "[database] password=\"\" is not defined in configuration file";
  my $database = $config->param("database.name") || die "[database] name=\"\" is not defined in configuration file";
  my $host = $config->param("database.host");
  unless (defined $host and $host) {
    $host = "localhost";
    warn "[database] host=\"\" is not defined in configuration file.  Defaulting to \"localhost\"";
  }

  my $dsn = "DBI:mysql:database=$database;host=$host";
  my $dbh = DBI->connect($dsn,$user,$password,{RaiseError => 1, ShowErrorStatement => 1});
  return $dbh;

}

sub scrub {
  my @values = @_;
  my @returns = ();
  my @allowedTags = qw[ br hr b i p];
  if (defined $values[0] and $values[0] eq 'keeplinks') {
    push @allowedTags, 'a';
    shift @values;
  }
  
  my @ruleSet = (
 		 script => 0,
 		 img => {
 			 src => qr{^(?!http://)}i,
 			 alt => 1,
 			 '*' => 0 },
 		);
  my @defaultRules = (
 		      0 =>
 		      { '*' => 1,
 			'href' => qr{^(?!(?:java)?script)}i,
 			'src' => qr{^(?!(?:java)?script)}i,
 			'cite' => '(?i-xsm:^(?!(?:java)?script))',
 			'language' => 0,
 			'name' => 1,
 			'onblur' => 0,
 			'onchange' => 0,
 			'onclick' => 0,
 			'ondblclick' => 0,
 			'onerror' => 0,
 			'onfocus' => 0,
 			'onkeydown' => 0,
 			'onkeypress' => 0,
 			'onkeyup' => 0,
 			'onload' => 0,
 			'onmousedown' => 0,
 			'onmousemove' => 0,
 			'onmouseout' => 0,
 			'onmouseover' => 0,
 			'onmouseup' => 0,
 			'onreset' => 0,
 			'onselect' => 0,
 			'onsubmit' => 0,
 			'onunload' => 0,
 			'src' => 0,
 			'type' => 0
 		      }
 		     );
  my $scrubber = HTML::Scrubber->new( allow => \@allowedTags);
  
  $scrubber->rules( @ruleSet );
  $scrubber->default( @defaultRules);
  $scrubber->comment(1);
  for my $value (@values) {
    push @returns, $scrubber->scrub($value);
  }
  if (wantarray) {
    return @returns;
  } else {
    return $returns[0];
  }


}

1;
