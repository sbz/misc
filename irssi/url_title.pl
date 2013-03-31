#!/usr/bin/env perl

use strict;
use warnings;

use LWP::UserAgent;

use Irssi;
use vars qw($VERSION %IRSSI $window_name);

$VERSION='0.2';
$window_name = 'url_title'; # use a specific window to write the events

%IRSSI = (
    authors => 'sbz',
    contact => 'sbz@6dev.net',
    name => 'url_title.pl',
    description => 'Print url title in irssi window when someone paste a link',
    licence => 'BSD',
    url => 'https://raw.github.com/sbz/misc/master/irssi/url_title.pl'
);


sub title($) {
    my ($url) = @_;
    $ENV{'PERL_LWP_SSL_VERIFY_HOSTNAME'} = 0;
    my $ua = LWP::UserAgent->new;
    my $response = $ua->get($url);
    return "" if $response->is_error;
    my ($title) = ($response->content =~m#<title>([^<]+)</title>#og);
    return "" unless $title;
    return $title;
}

sub event_message_public ($$$$$) {
    my ($server, $text, $nick, $address, $target) = @_;
#   Irssi::active_win->print(title($text)." on $target by $nick ($address)") if $text =~m#^http(s?)://.*#og;
    if ($text =~m#\b(?P<url>https??://[^\s()<>]+(?:\([\w\d]+\)|([^[:punct:]\s]|/)))#og) {
	my $url = $1;
	my $message = sprintf("%s on %s by %s (%s) %s", title($text), $target, $nick, $address, $url) if defined($url);
	Irssi::window_find_name($window_name)->print($message);
    }
}

Irssi::signal_add('message public', "event_message_public");
