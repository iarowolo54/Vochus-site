<?php
/**
 * Vochus website form handler (Contact + Agent application).
 * Plain PHP, no libraries. Both forms POST here with a hidden field form=contact|agent.
 *
 *   - POST only; fields are whitelisted per form, trimmed and length-limited; CR/LF rejected in header values.
 *   - Spam: honeypot ("website"), JS timing ("t", under 3s = bot), 5 submissions per IP per hour (flat file in a
 *     non-public directory: ../vochus-data when writable, otherwise the system temp dir).
 *   - Sends with mail() from no-reply@vochuseasysave.com, Reply-To the visitor, envelope sender set with -f.
 *   - Responds with JSON when the request accepts application/json, otherwise a 303 redirect
 *     (thanks.html?f=... on success, back to the page with ?error=1#form on failure).
 *   - VOCHUS_MAIL_DRYRUN=1 (environment) writes the composed email to the data dir instead of sending. Off by default.
 *
 * If mail() deliverability turns out poor on the host, swap send_mail() for SMTP (PHPMailer or the host's SMTP
 * relay); nothing else in this file needs to change. See _docs/DEPLOY.md.
 */
declare(strict_types=1);

$config = require __DIR__ . '/send-config.php';

$wantsJson = isset($_SERVER['HTTP_ACCEPT']) && stripos($_SERVER['HTTP_ACCEPT'], 'application/json') !== false;

$forms = [
    'contact' => [
        'page'   => 'contact.html',
        'fields' => [
            'name'    => ['label' => 'Full name',     'max' => 100,  'required' => true],
            'email'   => ['label' => 'Email address', 'max' => 254,  'required' => true, 'type' => 'email'],
            'subject' => ['label' => 'Subject',       'max' => 60,   'required' => true],
            'message' => ['label' => 'Message',       'max' => 3000, 'required' => true],
        ],
    ],
    'agent' => [
        'page'   => 'agent.html',
        'fields' => [
            'first'   => ['label' => 'First name',    'max' => 100,  'required' => true],
            'last'    => ['label' => 'Last name',     'max' => 100,  'required' => true],
            'phone'   => ['label' => 'Phone number',  'max' => 30,   'required' => true, 'type' => 'phone'],
            'email'   => ['label' => 'Email address', 'max' => 254,  'required' => true, 'type' => 'email'],
            'message' => ['label' => 'Message',       'max' => 3000, 'required' => true],
        ],
    ],
];

function respond(bool $ok, int $status, array $extra, string $redirect, bool $wantsJson): never
{
    if ($wantsJson) {
        http_response_code($status);
        header('Content-Type: application/json; charset=utf-8');
        header('Cache-Control: no-store');
        echo json_encode(['ok' => $ok] + $extra, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
    } else {
        http_response_code(303);
        header('Location: ' . $redirect);
    }
    exit;
}

function clean(string $v, int $max): string
{
    $v = trim(str_replace("\0", '', $v));
    if (function_exists('mb_substr')) {
        $v = mb_substr($v, 0, $max, 'UTF-8');
    } else {
        $v = substr($v, 0, $max);
    }
    return $v;
}

function data_dir(): string
{
    $candidates = [dirname(__DIR__) . '/vochus-data', sys_get_temp_dir() . '/vochus-data'];
    foreach ($candidates as $dir) {
        if (!is_dir($dir)) { @mkdir($dir, 0700, true); }
        if (is_dir($dir) && is_writable($dir)) { return $dir; }
    }
    return sys_get_temp_dir();
}

/** Returns true when this IP is still within its allowance; records the attempt. */
function rate_ok(string $ip, int $max, int $window): bool
{
    $file = data_dir() . '/rate.json';
    $fh = @fopen($file, 'c+');
    if (!$fh) { return true; }   // never block real people because the host's disk is odd
    flock($fh, LOCK_EX);
    $raw = stream_get_contents($fh);
    $data = $raw ? (json_decode($raw, true) ?: []) : [];
    $now = time();
    $key = hash('sha256', $ip);
    $hits = array_values(array_filter($data[$key] ?? [], fn($t) => $t > $now - $window));
    $ok = count($hits) < $max;
    if ($ok) { $hits[] = $now; }
    $data[$key] = $hits;
    foreach ($data as $k => $list) {   // drop stale entries
        $list = array_filter($list, fn($t) => $t > $now - $window);
        if (!$list) { unset($data[$k]); } else { $data[$k] = array_values($list); }
    }
    ftruncate($fh, 0); rewind($fh);
    fwrite($fh, json_encode($data));
    flock($fh, LOCK_UN); fclose($fh);
    return $ok;
}

function send_mail(array $config, string $subject, string $body, string $replyTo): bool
{
    $from = sprintf('%s <%s>', $config['from_name'], $config['from']);
    $headers = [
        'From: ' . $from,
        'Reply-To: ' . $replyTo,
        'MIME-Version: 1.0',
        'Content-Type: text/plain; charset=UTF-8',
        'Content-Transfer-Encoding: 8bit',
        'X-Mailer: Vochus website form',
    ];
    $encodedSubject = '=?UTF-8?B?' . base64_encode($subject) . '?=';
    if (getenv('VOCHUS_MAIL_DRYRUN') === '1') {
        $out = "To: {$config['to']}\nSubject: {$subject}\n" . implode("\n", $headers) . "\n\n" . $body;
        return (bool) file_put_contents(data_dir() . '/mail-' . date('Ymd-His') . '-' . bin2hex(random_bytes(3)) . '.txt', $out);
    }
    return mail($config['to'], $encodedSubject, $body, implode("\r\n", $headers), '-f' . $config['from']);
}

// ---- request gate ----
if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') {
    http_response_code(405);
    header('Allow: POST');
    header('Content-Type: text/plain; charset=utf-8');
    echo "Method not allowed\n";
    exit;
}

$type = isset($_POST['form']) && is_string($_POST['form']) ? $_POST['form'] : '';
if (!isset($forms[$type])) {
    respond(false, 400, ['errors' => ['form' => 'Unknown form.']], 'contact.html?error=1#form', $wantsJson);
}
$spec = $forms[$type];
$backTo = $spec['page'] . '?error=1#form';
$thanks = 'thanks.html?f=' . $type;

// ---- spam checks: honeypot and timing. Bots get a "success" so they learn nothing. ----
$honeypot = isset($_POST['website']) && is_string($_POST['website']) ? trim($_POST['website']) : '';
if ($honeypot !== '') {
    respond(true, 200, [], $thanks, $wantsJson);
}
$t = isset($_POST['t']) && is_string($_POST['t']) ? $_POST['t'] : '';
if ($t !== '' && ctype_digit($t)) {
    $elapsed = (microtime(true) * 1000) - (float) $t;   // t is set by JS as Date.now() in milliseconds
    if ($elapsed < $config['min_seconds'] * 1000) {
        respond(true, 200, [], $thanks, $wantsJson);
    }
}

// ---- rate limit ----
$ip = $_SERVER['REMOTE_ADDR'] ?? '0.0.0.0';
if (!rate_ok($ip, (int) $config['rate_limit']['max'], (int) $config['rate_limit']['window'])) {
    respond(false, 429, ['errors' => ['form' => 'Too many messages from this connection. Please try again later or email us directly.']], $backTo, $wantsJson);
}

// ---- collect and validate the whitelisted fields ----
$values = [];
$errors = [];
foreach ($spec['fields'] as $key => $rule) {
    $raw = isset($_POST[$key]) && is_string($_POST[$key]) ? $_POST[$key] : '';
    $v = clean($raw, $rule['max']);
    if ($key !== 'message' && preg_match('/[\r\n]/', $v)) {   // single-line fields never carry line breaks (header injection)
        $errors[$key] = 'Please remove line breaks.';
        continue;
    }
    if ($rule['required'] && $v === '') {
        $errors[$key] = 'Please fill in this field.';
        continue;
    }
    if ($v !== '' && ($rule['type'] ?? '') === 'email' && !filter_var($v, FILTER_VALIDATE_EMAIL)) {
        $errors[$key] = 'Enter a valid email address.';
        continue;
    }
    if ($v !== '' && ($rule['type'] ?? '') === 'phone' && !preg_match('/^[0-9+\s\-()]{7,30}$/', $v)) {
        $errors[$key] = 'Enter a valid phone number.';
        continue;
    }
    $values[$key] = $v;
}
if ($errors) {
    respond(false, 422, ['errors' => $errors], $backTo, $wantsJson);
}

// ---- compose ----
date_default_timezone_set($config['timezone']);
$name = $type === 'agent' ? trim($values['first'] . ' ' . $values['last']) : $values['name'];
$subject = $type === 'agent'
    ? '[Vochus website] Agent application: ' . $name
    : '[Vochus website] Message: ' . $values['subject'] . ': ' . $name;
$subject = str_replace(["\r", "\n"], ' ', $subject);

$referer = isset($_SERVER['HTTP_REFERER']) && is_string($_SERVER['HTTP_REFERER']) ? $_SERVER['HTTP_REFERER'] : '';
$page = (parse_url($referer, PHP_URL_HOST) === parse_url($config['site'], PHP_URL_HOST)) ? $referer : $config['site'] . '/' . $spec['page'];
$page = str_replace(["\r", "\n"], '', $page);

$lines = [];
foreach ($spec['fields'] as $key => $rule) {
    $lines[] = $rule['label'] . ': ' . ($key === 'message' ? "\n" . $values[$key] . "\n" : $values[$key]);
}
$body = ($type === 'agent' ? "New agent application from the Vochus website\n" : "New message from the Vochus website\n")
    . str_repeat('-', 46) . "\n"
    . implode("\n", $lines) . "\n"
    . str_repeat('-', 46) . "\n"
    . 'Sent: ' . date('D, j M Y H:i') . ' (' . $config['timezone'] . ")\n"
    . 'Page: ' . $page . "\n";

$replyTo = $values['email'];   // validated above; never contains CR/LF
if (!send_mail($config, $subject, $body, $replyTo)) {
    respond(false, 500, ['errors' => ['form' => 'We could not send your message right now. Please email us directly.']], $backTo, $wantsJson);
}
respond(true, 200, [], $thanks, $wantsJson);
