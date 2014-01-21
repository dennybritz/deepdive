#!/usr/bin/perl

# Scores the performance of a system response for the entity linking
# task in TAC KBP 2009.

# Truth files are of the form:
#   query-id list-of-acceptable-KB-identifiers

# Systems files are of the form:
#   query-id single-identifier

# Query ids are of the form EL1, EL2, EL3, ... ELn. KB identifiers can
# be any string without spaces. There might be more than one correct
# identifier because the KB may have duplicate nodes for some
# entities. This is chiefly because the reference KB derived from
# Wikipedia which has some duplication.  In the truth file's list of
# acceptable responses a prefix of NIL (e.g. NIL4) indicates that the
# particular entity is judged to be missing from the KB.  (However,
# systems will return just "NIL", which is not an exact string match.)

# This script computes accuracies, both averaged over queries about the
# same entity (a macro average), and over all queries (a micro
# average).

# Feedback: Paul McNamee, paul (full stop) mcnamee [a t] jhuapl d.o.t. edu
# Date: 5/15/09
# Usage: kbpenteval.pl truth-file system-output

if ($#ARGV+1 < 2) {
  die "Usage: truth-file system-output\n";
}

my $keyfile = $ARGV[0];
my $testfile = $ARGV[1];

die "Can't read one of the input files.\n" if (! (-e $keyfile && -e $testfile));

# Read in keyfile
my %correct = {};
my $numqueries = 0;
open FH, "<$keyfile";
while (my $line = <FH>) {
  chomp($line);
  next if ($line =~ /^#/);
  if ($line =~ /^EL(\d+)\s+([^\s].*)/s) { # line starts with a qid "EL...." and has at least one link
    $numqueries++;
    my $qid = $1;
    my @links = split /\s+/, $2;
    foreach my $link (@links) {
      push @{ $correct->{$qid} }, $link # correct{$qid} holds a list of acceptable links
    }
  } else {
    die "In $keyfile there is a problem with line:\n  $line\n";
  }
}
close FH;

$microsum = 0.0;

# Read in system output file and evaluate it
open FH, "<$testfile";
while (my $line = <FH>) {
  chomp($line);
  if ($line =~ /^EL(\d+)\s+([^\s]+)\s*$/) { # line starts with a qid and has exactly one link
    my $qid = $1;
    my $link = $2;
    
    # Decide if $link is correct (value is 0 or 1)
    my $corr = 0;
    foreach my $valident (@{ $correct->{$qid}}) {
      my $x = $valident;
      $x =~ s/^NIL.*/NIL/;
      if ($link eq $x) {
        $corr = 1;
        last;
      }
    }

    my $isNILEntity = grep /NIL/, @{ $correct->{$qid} };
    my $canonicalAnswer = @{ $correct->{$qid} }[0]; # first in list is used as a representative

    # Microaveraged accuracy
    $microsum += $corr;
    if ($isNILEntity) {
      $micro_nil_sum += $corr;
      $micro_nil_cnt++;
    } else {
      $micro_oth_sum += $corr;
      $micro_oth_cnt++;
    }

    # Add to macro average statistics
    push @{ $macrotbl{$canonicalAnswer} }, $corr;  # build a list of zeros and ones

  } else {
    die "In $testfile there is a problem with line:\n  $line\n";
  }
}
close FH;

# Print out micro average results
$microsum /= $numqueries;

print "Micro-averages:\n";
print "$numqueries queries: " . sprintf("%.4f\n", $microsum);

if ($micro_oth_cnt > 0) {
  $micro_oth_sum /= $micro_oth_cnt;
  print "$micro_oth_cnt KB: " . sprintf("%.4f\n", $micro_oth_sum);
}

if ($micro_nil_cnt > 0) {
  $micro_nil_sum /= $micro_nil_cnt;
  print "$micro_nil_cnt NIL: " . sprintf("%.4f\n", $micro_nil_sum);
}

# Compute and print out macro average results
print "\nMacro-averages:\n";

$macrosum = 0.0;
foreach my $key (keys %macrotbl) {
  my @list = @ {$macrotbl{$key}};
  my $sum = 0.0;
  foreach my $x (@list) {
    $sum += $x;
  }
  my $len = @list;
  $sum /= $len;
  $macrosum += $sum;
  $macrocnt++;
#  print "    $key: $sum ($len)\n";

  # Breakdown for NIL and non-NIL
  if ($key =~ /NIL/i) {
    $macro_nil_sum += $sum;
    $macro_nil_cnt++;
  } else {
    $macro_oth_sum += $sum;
    $macro_oth_cnt++;
  }

}
$macrosum /= $macrocnt;
print "$macrocnt entities: " . sprintf("%.4f\n", $macrosum);

if ($macro_oth_cnt > 0) {
  $macro_oth_sum /= $macro_oth_cnt;
  print "$macro_oth_cnt KB: " . sprintf("%.4f\n", $macro_oth_sum);
}

if ($macro_nil_cnt > 0) {
  $macro_nil_sum /= $macro_nil_cnt;
  print "$macro_nil_cnt NIL: " . sprintf("%.4f\n", $macro_nil_sum);
}

# blank line
