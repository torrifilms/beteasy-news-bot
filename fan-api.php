<?php
// Standalone fan counter endpoint
// Place in: /wp-content/themes/easynew/fan-api.php

require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');

header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');

$slug = sanitize_title($_REQUEST['slug'] ?? '');
$do = sanitize_text_field($_REQUEST['do'] ?? 'get');

if (!$slug) {
    echo json_encode(['error' => 'no slug']);
    exit;
}

$ip = $_SERVER['HTTP_X_FORWARDED_FOR'] ?? $_SERVER['REMOTE_ADDR'] ?? 'unknown';
$ip = trim(explode(',', $ip)[0]);
$key = 'bfan_' . md5($slug . $ip);

if ($do === 'get') {
    $count = (int) get_option('beteasy_fans_' . $slug, 0);
    echo json_encode(['count' => $count, 'status' => 'ok']);
    exit;
}

if (get_transient($key)) {
    $count = (int) get_option('beteasy_fans_' . $slug, 0);
    echo json_encode(['count' => $count, 'status' => 'limited']);
    exit;
}

$count = (int) get_option('beteasy_fans_' . $slug, 0);
if ($do === 'remove') {
    $count = max(0, $count - 1);
} else {
    $count++;
}
update_option('beteasy_fans_' . $slug, $count, false);
set_transient($key, 1, DAY_IN_SECONDS);

echo json_encode(['count' => $count, 'status' => 'ok']);
