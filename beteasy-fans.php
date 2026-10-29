<?php
/**
 * Plugin Name: Beteasy Fan Counter
 * Description: Fan counter via admin-ajax (bypasses REST restriction)
 * Version: 1.2
 */
if (!defined('ABSPATH')) exit;

// AJAX handlers (work for logged-in and guests)
add_action('wp_ajax_beteasy_fan', 'beteasy_fan_handler');
add_action('wp_ajax_nopriv_beteasy_fan', 'beteasy_fan_handler');

function beteasy_fan_handler() {
    $slug = sanitize_title($_POST['slug'] ?? '');
    $action = sanitize_text_field($_POST['do'] ?? 'get');
    
    if (!$slug) {
        wp_send_json_error('no slug');
    }
    
    $ip = isset($_SERVER['HTTP_X_FORWARDED_FOR']) ? trim(explode(',', $_SERVER['HTTP_X_FORWARDED_FOR'])[0]) : ($_SERVER['REMOTE_ADDR'] ?? 'unknown');
    $ua = substr($_SERVER['HTTP_USER_AGENT'] ?? '', 0, 80);
    $key = 'bfan_' . md5($slug . $ip . $ua);
    
    if ($action === 'get') {
        $count = (int) get_option('beteasy_fans_' . $slug, 0);
        wp_send_json_success(['count' => $count]);
    }
    
    if (get_transient($key)) {
        $count = (int) get_option('beteasy_fans_' . $slug, 0);
        wp_send_json_success(['count' => $count, 'status' => 'limited']);
    }
    
    $count = (int) get_option('beteasy_fans_' . $slug, 0);
    if ($action === 'remove') {
        $count = max(0, $count - 1);
    } else {
        $count++;
    }
    update_option('beteasy_fans_' . $slug, $count, false);
    set_transient($key, 1, DAY_IN_SECONDS);
    
    wp_send_json_success(['count' => $count, 'status' => 'ok']);
}
