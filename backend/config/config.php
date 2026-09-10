<?php
declare(strict_types=1);
function env_value(string $key, string $default = ''): string { static $env = null; if ($env === null) { $env = []; $file = dirname(__DIR__, 2).'/.env'; if (is_file($file)) foreach (file($file, FILE_IGNORE_NEW_LINES|FILE_SKIP_EMPTY_LINES) as $line) if (str_contains($line,'=') && !str_starts_with(trim($line),'#')) { [$k,$v] = explode('=', $line, 2); $env[trim($k)] = trim($v, " \t\""); } } return $env[$key] ?? getenv($key) ?: $default; }
function db(): PDO { static $pdo; if (!$pdo) { $dsn='mysql:host='.env_value('DB_HOST','127.0.0.1').';port='.env_value('DB_PORT','3306').';dbname='.env_value('DB_NAME','compara_tech_gt').';charset=utf8mb4'; $pdo=new PDO($dsn,env_value('DB_USER','root'),env_value('DB_PASSWORD',''),[PDO::ATTR_ERRMODE=>PDO::ERRMODE_EXCEPTION,PDO::ATTR_DEFAULT_FETCH_MODE=>PDO::FETCH_ASSOC]); } return $pdo; }

