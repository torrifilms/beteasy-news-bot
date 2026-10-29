<?php
/**
 * Plugin Name: Beteasy Fan Counter
 * Description: Server-side fan counter with anti-abuse
 * Version: 1.1
 */
if (!defined('ABSPATH')) exit;

add_action('rest_api_init', function() {
    register_rest_route('beteasy/v1', '/fan/(?P<slug>[a-z0-9\-]+)', [
        [
            'methods' => 'GET',
            'callback' => 'beteasy_get_fans',
            'permission_callback' => '__return_true',
        ],
        [
            'methods' => 'POST',
            'callback' => 'beteasy_toggle_fan',
            'permission_callback' => '__return_true',
        ],
    ]);
});

function beteasy_get_fans($request) {
    $slug = sanitize_title($request['slug']);
    $count = (int) get_option('beteasy_fans_' . $slug, 0);
    return new WP_REST_Response(['count' => $count], 200);
}

function beteasy_toggle_fan($request) {
    $slug = sanitize_title($request['slug']);
    $ip = isset($_SERVER['HTTP_X_FORWARDED_FOR']) ? explode(',', $_SERVER['HTTP_X_FORWARDED_FOR'])[0] : ($_SERVER['REMOTE_ADDR'] ?? 'unknown');
    $ip = trim($ip);
    $ua = substr($_SERVER['HTTP_USER_AGENT'] ?? '', 0, 100);
    $fingerprint = md5($slug . $ip . $ua);
    $key = 'beteasy_fan_' . $fingerprint;

    // Strict rate limit: 1 action per fingerprint per 24h
    if (get_transient($key)) {
        $count = (int) get_option('beteasy_fans_' . $slug, 0);
        return new WP_REST_Response(['count' => $count, 'status' => 'limited'], 200);
    }

    $count = (int) get_option('beteasy_fans_' . $slug, 0);
    $body = $request->get_json_params();
    $action = isset($body['action']) ? $body['action'] : 'add';

    if ($action === 'remove') {
        $count = max(0, $count - 1);
    } else {
        $count++;
    }

    update_option('beteasy_fans_' . $slug, $count, false);
    set_transient($key, time(), DAY_IN_SECONDS);

    return new WP_REST_Response(['count' => $count, 'status' => 'ok'], 200);
}

// Allow public access to our endpoint
add_filter('rest_authentication_errors', function($result) {
    if (!empty($result)) return $result;
    $route = isset($_SERVER['REQUEST_URI']) ? $_SERVER['REQUEST_URI'] : '';
    if (strpos($route, '/wp-json/beteasy/v1/fan/') !== false) {
        return true;
    }
    return $result;
});
