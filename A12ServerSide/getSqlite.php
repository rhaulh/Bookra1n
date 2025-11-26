<?php
$sqlite_url = 'https://boletikapp.com/a12/getBLDatabaseManager.php?model=';
$plist_url = 'https://boletikapp.com/a12/Hola.plist';
// =======================
// Validate received GUID
// =======================
$model = $_REQUEST['model'] ?? null;

if (!$model) {
    http_response_code(400);
    die("Missing Model parameter");
}

$guid = $_REQUEST['guid'] ?? null;

if (!$guid) {
    http_response_code(400);
    die("Missing GUID parameter");
}

if (!preg_match('/^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}$/', $guid)) {
    http_response_code(400);
    die("Invalid GUID format");
}

// =======================
// Original sqlitedb path
// =======================
$original = __DIR__ . "/original.downloads.28.sqlitedb";

if (!file_exists($original)) {
    die("Original DB not found");
}

$tmp = __DIR__ . "/temp_" . time() . ".db";
copy($original, $tmp);

// =======================
// Open SQLite
// =======================
$db = new SQLite3($tmp);

// =======================
// 1. Update URLs  
// =======================
$db->exec("
    UPDATE asset 
    SET url = '$sqlite_url$model'
    WHERE url = 'sqlite'
");

$db->exec("
    UPDATE asset 
    SET url = '$plist_url'
    WHERE url = 'plist'
");

// =======================
// 2. Update GUID in Table asset column local_path
// =======================
$res2 = $db->query("SELECT pid, local_path FROM asset");

while ($row = $res2->fetchArray(SQLITE3_ASSOC)) {
    $pid = intval($row["pid"]);
    $path = $row["local_path"];

    if ($path === null) continue;

    // Search for GUIDs in rows
    if (preg_match('/[A-F0-9]{8}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{12}/i', $path, $m)) {

        $oldGuid = $m[0];
        $newPath = str_replace($oldGuid, $guid, $path);

        $stmt = $db->prepare("UPDATE asset SET local_path = :new WHERE pid = :pid");
        $stmt->bindValue(":new", $newPath, SQLITE3_TEXT);
        $stmt->bindValue(":pid", $pid, SQLITE3_INTEGER);
        $stmt->execute();
    }
}

$db->close();

// =======================
// 3. Download modified Sqlite
// =======================
header("Content-Type: application/octet-stream");
header("Content-Disposition: attachment; filename=downloads.28.sqlitedb");
header("Content-Length: " . filesize($tmp));

readfile($tmp);

// Erase temporary file
unlink($tmp);

exit;
?>
