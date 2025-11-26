<?php
header('Content-Type: application/json');

$model = $_REQUEST['model'] ?? null;

if ($model === null || $model==='') {
    http_response_code(400); // Bad Request
    echo json_encode([
        "status" => "error",
        "message" => "Missing parameter: model"
    ]);
    exit;
}

$path = __DIR__ . "/devices/" . $model;

if (is_dir($path)) {
    http_response_code(200); // OK
    echo json_encode([
        "status" => "ok",
        "model_name" => $model
    ]);
    exit;
} else {
    http_response_code(404); // Not Found
    echo json_encode([
        "status" => "not_found",
        "model_name" => "Unknown"
    ]);
    exit;
}