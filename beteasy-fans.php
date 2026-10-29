<?php
/**
 * Plugin Name: Beteasy Fan Counter
 * Description: AJAX endpoint for team fan counts
 * Version: 1.0
 */

if (!defined('ABSPATH')) exit;

// Register REST endpoint
add_action('rest_api_init', function() {
    register_rest_route('beteasy/v1', '/fan/(?P<slug>[a-z0-9\-]+)', [
        'methods' => 'GET',
        'callback' => 'beteasy_get_fans',
        'permission_callback' => '__return_true',
    ]);
    register_rest_route('beteasy/v1', '/fan/(?P<slug>[a-z0-9\-]+)', [
        'methods' => 'POST',
        'callback' => 'beteasy_toggle_fan',
        'permission_callback' => '__return_true',
    ]);
});

function beteasy_get_fans($request) {
    $slug = sanitize_title($request['slug']);
    $count = (int) get_option('beteasy_fans_' . $slug, 0);
    return ['count' => $count];
}

function beteasy_toggle_fan($request) {
    $slug = sanitize_title($request['slug']);
    $ip = $_SERVER['REMOTE_ADDR'] ?? 'unknown';
    $key = 'beteasy_fan_ip_' . md5($slug . $ip);
    
    // Rate limit: 1 toggle per IP per team per day
    if (get_transient($key)) {
        $count = (int) get_option('beteasy_fans_' . $slug, 0);
        return ['count' => $count, 'status' => 'already'];
    }
    
    $count = (int) get_option('beteasy_fans_' . $slug, 0);
    $action = $request->get_param('action') ?: 'add';
    
    if ($action === 'remove' && $count > 0) {
        $count--;
    } else {
        $count++;
    }
    
    update_option('beteasy_fans_' . $slug, $count);
    set_transient($key, 1, DAY_IN_SECONDS);
    
    return ['count' => $count, 'status' => 'ok'];
}
