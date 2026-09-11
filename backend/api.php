<?php
declare(strict_types=1);
require_once __DIR__.'/config/config.php';
header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');
function response(mixed $data = [], ?string $message = null, int $status=200): never { http_response_code($status); echo json_encode(['success'=>$status<400,'data'=>$data,'message'=>$message],JSON_UNESCAPED_UNICODE); exit; }
function live_ingest(string $query): void {
 $python=dirname(__DIR__).'/scrapers/.venv/bin/python'; $script=dirname(__DIR__).'/scrapers/live_ingest.py';
 if(!is_executable($python)){$python='python3';}
 $command=escapeshellarg($python).' '.escapeshellarg($script).' '.escapeshellarg($query);
 $descriptors=[1=>['pipe','w'],2=>['pipe','w']]; $process=proc_open($command,$descriptors,$pipes);
 if(!is_resource($process)){error_log('No se pudo iniciar live_ingest');return;}
 stream_set_timeout($pipes[1],45); stream_set_timeout($pipes[2],45); $output=stream_get_contents($pipes[1]); $error=stream_get_contents($pipes[2]);
 fclose($pipes[1]); fclose($pipes[2]); $code=proc_close($process); if($code!==0){error_log('live_ingest fallo: '.trim($error));} else if($output===''){error_log('live_ingest no devolvio datos');}
}
try {
 $path=trim(parse_url($_SERVER['REQUEST_URI']??'',PHP_URL_PATH) ?? '','/');
 $parts=array_values(array_filter(explode('/',$path),fn($part)=>$part!==''));
 $api_index=array_search('api',$parts,true);
 $route=$api_index===false?array_slice($parts,-3):array_slice($parts,$api_index+1);
 $resource=$route[0]??'';
 $id=isset($route[1])&&ctype_digit($route[1])?(int)$route[1]:null;
 $subresource=$route[2]??null;
 $pdo=db();
 if ($resource==='categorias') response($pdo->query("SELECT idcategoria,nombre FROM categoria WHERE estado=1 ORDER BY nombre")->fetchAll());
 if ($resource==='tiendas') response($pdo->query("SELECT idtienda,nombre,url,logo FROM tienda WHERE estado=1 ORDER BY nombre")->fetchAll());
 if ($resource==='productos' && $id===null) { $q=trim((string)($_GET['q']??'')); $sort=$_GET['sort']??'price'; $order=$sort==='price_desc'?'precio_minimo DESC':($sort==='name'?'p.nombre ASC':'precio_minimo IS NULL,precio_minimo ASC'); if($q!==''){live_ingest($q);} $sql="SELECT p.*,m.nombre marca,c.nombre categoria,MIN(pr.precio) precio_minimo,COUNT(DISTINCT pt.idtienda) tiendas FROM producto p LEFT JOIN marca m ON m.idmarca=p.idmarca LEFT JOIN categoria c ON c.idcategoria=p.idcategoria LEFT JOIN producto_tienda pt ON pt.idproducto=p.idproducto AND pt.estado=1 LEFT JOIN precio pr ON pr.idproducto_tienda=pt.idproducto_tienda AND pr.idprecio=(SELECT p2.idprecio FROM precio p2 WHERE p2.idproducto_tienda=pt.idproducto_tienda ORDER BY p2.fecha DESC,p2.idprecio DESC LIMIT 1) WHERE p.estado=1 "; $params=[]; if($q!==''){ $sql.=" AND (p.nombre LIKE :q OR p.modelo LIKE :q OR m.nombre LIKE :q) "; $params['q']="%$q%"; } $sql.=" GROUP BY p.idproducto ORDER BY $order"; $st=$pdo->prepare($sql);$st->execute($params);response($st->fetchAll()); }
 if ($resource==='productos' && $id!==null && $subresource===null) { $st=$pdo->prepare("SELECT p.*,m.nombre marca,c.nombre categoria FROM producto p LEFT JOIN marca m ON m.idmarca=p.idmarca LEFT JOIN categoria c ON c.idcategoria=p.idcategoria WHERE p.idproducto=? AND p.estado=1");$st->execute([$id]);$p=$st->fetch();if(!$p)response([], 'Producto no encontrado',404); $s=$pdo->prepare("SELECT pt.*,t.nombre tienda,t.url tienda_url,(SELECT pr.precio FROM precio pr WHERE pr.idproducto_tienda=pt.idproducto_tienda ORDER BY pr.fecha DESC,pr.idprecio DESC LIMIT 1) precio,(SELECT pr.fecha FROM precio pr WHERE pr.idproducto_tienda=pt.idproducto_tienda ORDER BY pr.fecha DESC,pr.idprecio DESC LIMIT 1) actualizado FROM producto_tienda pt LEFT JOIN tienda t ON t.idtienda=pt.idtienda WHERE pt.idproducto=? AND pt.estado=1 ORDER BY precio ASC");$s->execute([$id]);$p['tiendas']=$s->fetchAll();$s=$pdo->prepare("SELECT atributo,valor FROM producto_especificacion WHERE idproducto=? ORDER BY atributo");$s->execute([$id]);$p['especificaciones']=$s->fetchAll();response($p); }
 if ($resource==='productos' && $id!==null && $subresource==='precios') { $st=$pdo->prepare("SELECT t.nombre tienda,pt.url,pr.precio,pr.moneda,pr.disponible,pr.fecha FROM precio pr LEFT JOIN producto_tienda pt ON pt.idproducto_tienda=pr.idproducto_tienda LEFT JOIN tienda t ON t.idtienda=pt.idtienda WHERE pt.idproducto=? ORDER BY pr.precio ASC,pr.fecha DESC");$st->execute([$id]);response($st->fetchAll()); }
 if ($resource==='productos' && $id!==null && $subresource==='historial') { $st=$pdo->prepare("SELECT DATE(pr.fecha) fecha,MIN(pr.precio) precio FROM precio pr LEFT JOIN producto_tienda pt ON pt.idproducto_tienda=pr.idproducto_tienda WHERE pt.idproducto=? GROUP BY DATE(pr.fecha) ORDER BY fecha");$st->execute([$id]);response($st->fetchAll()); }
 response([], 'Ruta no encontrada',404);
} catch (Throwable $e) { error_log($e->getMessage()); response([], 'Error interno del servidor',500); }
