<?php
$base_url = "https://boletikapp.com/a12/devices/";

// =======================
// Validate received MODEL
// =======================
$model = $_REQUEST['model'] ?? null;

if (!$model) {
    die("Missing parameter: model");
}

// Build final URL
$epub_url = $base_url . $model . '/asset.epub';

// =======================
// Original SQLite path
// =======================
$original = __DIR__ . "/original.BLDatabaseManager.sqlite";

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
$q1 = $db->exec("
    UPDATE ZBLDOWNLOADINFO 
    SET ZTHUMBNAILIMAGEURL = '$epub_url'
");

$q2 = $db->exec("
    UPDATE ZBLDOWNLOADINFO 
    SET ZURL = '$epub_url'
");

// OPTIONAL error check
if (!$q1 || !$q2) {
    die("SQL update failed.");
}

$db->close();

// =======================
// 3. Download modified SQLite
// =======================
header("Content-Type: application/octet-stream");
header("Content-Disposition: attachment; filename=BLDatabaseManager.sqlite");
header("Content-Length: " . filesize($tmp));

readfile($tmp);

// Delete temporary file
unlink($tmp);

exit;
?>
