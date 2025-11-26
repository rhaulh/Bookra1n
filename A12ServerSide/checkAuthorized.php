<?php
header('Content-Type: application/json');

$serial = $_REQUEST['serial'] ?? null;

if ($serial === null || $serial === '') {
    http_response_code(400);
    echo json_encode([
        "status" => "error",
        "message" => "Missing parameter: serial"
    ]);
    exit;
}

try {

    // =======================
    // Open SQLite
    // =======================
    $dbPath = __DIR__ . "/activator.sqlite";
    if (!file_exists($dbPath)) {
        throw new Exception("Database file not found");
    }

    $db = new SQLite3($dbPath);

    // =======================
    // Lookup serial
    // =======================
    $stmt = $db->prepare("SELECT serial, status, stored_guid FROM registered_serials WHERE serial = :serial LIMIT 1");
    $stmt->bindValue(":serial", $serial, SQLITE3_TEXT);
    $result = $stmt->execute();
    $row = $result->fetchArray(SQLITE3_ASSOC);

    if (!$row) {
        http_response_code(401);
        echo json_encode([
            "status" => "Not Authorized",
            "message" => "Serial not found"
        ]);
        exit;
    }

    $db->close();

    // =======================
    // Response
    // =======================
    http_response_code(200);
    echo json_encode([
        "status" => "Authorized",
        "stored_guid" => $storedGuid,
        "serial" => $serial
    ]);
    exit;

} catch (Exception $e) {

    http_response_code(500);
    echo json_encode([
        "status" => "Error",
        "message" => $e->getMessage()
    ]);
    exit;
}
