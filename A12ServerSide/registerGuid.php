<?php
header('Content-Type: application/json');

// =======================
// Obtener parámetros
// =======================
$serial = $_POST['serial'] ?? '';
$guid   = $_POST['guid'] ?? '';

if ($serial === '' || $guid === '') {
    echo json_encode([
        "success" => false,
        "message" => "Faltan parámetros: serial y guid son requeridos."
    ]);
    exit;
}

// =======================
// Abrir SQLite
// =======================
$db_path = __DIR__ . "/activator.sqlite";

if (!file_exists($db_path)) {
    echo json_encode([
        "success" => false,
        "message" => "La base de datos no existe."
    ]);
    exit;
}

$db = new SQLite3($db_path, SQLITE3_OPEN_READWRITE);

// =======================
// 1. Verificar si el serial existe
// =======================
$stmt = $db->prepare("SELECT status FROM registered_serials WHERE serial = :serial LIMIT 1");
$stmt->bindValue(":serial", $serial, SQLITE3_TEXT);
$result = $stmt->execute();
$row = $result->fetchArray(SQLITE3_ASSOC);

if (!$row) {
    echo json_encode([
        "success" => false,
        "message" => "El serial no existe."
    ]);
    exit;
}

// =======================
// 2. Validar que status NO esté vacío
// =======================
if (trim($row['status']) === '') {
    echo json_encode([
        "success" => false,
        "message" => "El serial existe pero su status está vacío. No se puede registrar GUID."
    ]);
    exit;
}

// =======================
// 3. Registrar GUID
// =======================
$update = $db->prepare("
    UPDATE registered_serials
    SET stored_guid = :guid
    WHERE serial = :serial
");

$update->bindValue(":guid", $guid, SQLITE3_TEXT);
$update->bindValue(":serial", $serial, SQLITE3_TEXT);
$update->execute();

// =======================
// Respuesta final
// =======================
echo json_encode([
    "success" => true,
    "message" => "GUID registrado correctamente.",
    "serial"  => $serial,
    "guid"    => $guid
]);

$db->close();
