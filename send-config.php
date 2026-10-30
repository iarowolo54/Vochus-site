<?php
// Vochus website form handler: the addresses live here so they are easy to change.
// This file is blocked from direct web access by .htaccess.
return [
    'to'        => 'info@vochuseasysave.com',
    'from_name' => 'Vochus Website',
    'from'      => 'no-reply@vochuseasysave.com',   // must be a mailbox (or a sender the domain is allowed to use)
    'site'      => 'https://vochuseasysave.com',
    'timezone'  => 'Africa/Lagos',
    'rate_limit' => ['max' => 5, 'window' => 3600],  // submissions per IP per window (seconds)
    'min_seconds' => 3,                             // submissions faster than this (with JS timing present) are treated as bots
];
