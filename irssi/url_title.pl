#!/usr/bin/env perl

use strict;
use warnings;

use LWP::UserAgent;

use Irssi;
use vars qw($VERSION %IRSSI);

$VERSION='0.1';

%IRSSI = (
    authors => 'sbz',
    contact => 'sbz@6dev.net',
    name => 'url_title.pl',
    description => 'Print url title on active window when someone paste a link',
    licence => 'BSD',
    url => 'https://raw.github.com/sbz/misc/master/irssi/url_title.pl'
);


sub title($) {
    my ($url) = @_;
    my $ua = LWP::UserAgent->new;
    my $response = $ua->get($url);
    return if $response->is_error;
    my ($title) = ($response->as_string =~m#<title>(.*)</title>#og);
    return unless $title;
    return $title;
}

sub event_message_public ($$$$) {
    my ($server, $text, $nick, $address, $target) = @_;
    Irssi::active_win->print(title($text)." on $target by $nick ($address)") if $text =~m#^http(s?)://.*#og;
}

Irssi::signal_add('message public', "event_message_public");
