#!/usr/local/bin/perl
use strict;
use warnings;

print "Checking Modules\n";

my @modules = qw( Apache::DBI HTML::Parser HTML::Scrubber DBI DBD::mysql 
		  Data::Dumper Template 
		  Date::Calc IO::File CGI MIME::Lite IO::Handle 
		  URI Time::HiRes Benchmark Calendar::Simple Net::DNS 
		  LWP::UserAgent HTTP::Request::Common Digest::MD5 
		  File::Basename Class::Accessor Class::Fields 
		  HTML::TokeParser::Simple);
for my $module (@modules) {
  eval "require $module";
  my $ok = '';
  if ($@) { 
    $ok =  "NOT OK\n";
  } else {
    $ok = "Ok\n";
  }
  printf ("%-23s  %-s",($module, $ok));
}

