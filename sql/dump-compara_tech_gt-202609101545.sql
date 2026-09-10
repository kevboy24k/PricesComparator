-- MySQL dump 10.13  Distrib 9.6.0, for macos15.7 (arm64)
--
-- Host: localhost    Database: compara_tech_gt
-- ------------------------------------------------------
-- Server version	8.4.3

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `categoria`
--

DROP TABLE IF EXISTS `categoria`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `categoria` (
  `idcategoria` int unsigned NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `estado` tinyint(1) NOT NULL DEFAULT '1',
  PRIMARY KEY (`idcategoria`),
  UNIQUE KEY `nombre` (`nombre`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `categoria`
--

LOCK TABLES `categoria` WRITE;
/*!40000 ALTER TABLE `categoria` DISABLE KEYS */;
INSERT INTO `categoria` VALUES (1,'Procesadores',1),(2,'Tarjetas gráficas',1),(3,'Memorias RAM',1),(4,'SSD',1),(5,'Motherboards',1),(6,'Monitores',1),(7,'Laptops',1);
/*!40000 ALTER TABLE `categoria` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `marca`
--

DROP TABLE IF EXISTS `marca`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `marca` (
  `idmarca` int unsigned NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `estado` tinyint(1) NOT NULL DEFAULT '1',
  PRIMARY KEY (`idmarca`),
  UNIQUE KEY `nombre` (`nombre`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `marca`
--

LOCK TABLES `marca` WRITE;
/*!40000 ALTER TABLE `marca` DISABLE KEYS */;
INSERT INTO `marca` VALUES (1,'AMD',1),(2,'NVIDIA',1),(3,'Kingston',1),(4,'Samsung',1);
/*!40000 ALTER TABLE `marca` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `precio`
--

DROP TABLE IF EXISTS `precio`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `precio` (
  `idprecio` bigint unsigned NOT NULL AUTO_INCREMENT,
  `idproducto_tienda` int unsigned NOT NULL,
  `precio` decimal(12,2) NOT NULL,
  `precio_anterior` decimal(12,2) DEFAULT NULL,
  `moneda` char(3) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'GTQ',
  `disponible` tinyint(1) NOT NULL DEFAULT '0',
  `fecha` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`idprecio`),
  KEY `idx_precio_historial` (`idproducto_tienda`,`fecha`),
  KEY `idx_precio_actual` (`idproducto_tienda`,`fecha` DESC),
  CONSTRAINT `precio_ibfk_1` FOREIGN KEY (`idproducto_tienda`) REFERENCES `producto_tienda` (`idproducto_tienda`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `precio`
--

LOCK TABLES `precio` WRITE;
/*!40000 ALTER TABLE `precio` DISABLE KEYS */;
INSERT INTO `precio` VALUES (1,1,1649.00,NULL,'GTQ',1,'2026-08-11 14:51:02'),(2,1,1599.00,NULL,'GTQ',1,'2026-08-21 14:51:02'),(3,1,1649.00,NULL,'GTQ',1,'2026-09-10 14:51:02'),(4,2,1699.00,NULL,'GTQ',1,'2026-08-11 14:51:02'),(5,2,1749.00,NULL,'GTQ',1,'2026-08-27 14:51:02'),(6,2,1699.00,NULL,'GTQ',1,'2026-09-10 14:51:02'),(7,3,1899.00,NULL,'GTQ',1,'2026-08-11 14:51:02'),(8,3,1790.00,NULL,'GTQ',1,'2026-08-31 14:51:02'),(9,3,1790.00,NULL,'GTQ',1,'2026-09-10 14:51:02'),(10,1,2039.00,1649.00,'GTQ',1,'2026-09-10 09:21:31'),(11,1,2039.00,1649.00,'GTQ',1,'2026-09-10 09:29:05'),(12,1,1953.00,NULL,'GTQ',1,'2026-09-10 09:30:19');
/*!40000 ALTER TABLE `precio` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `producto`
--

DROP TABLE IF EXISTS `producto`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `producto` (
  `idproducto` int unsigned NOT NULL AUTO_INCREMENT,
  `idcategoria` int unsigned NOT NULL,
  `idmarca` int unsigned DEFAULT NULL,
  `nombre` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `modelo` varchar(150) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `sku_global` varchar(150) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `imagen` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `descripcion` text COLLATE utf8mb4_unicode_ci,
  `estado` tinyint(1) NOT NULL DEFAULT '1',
  `creado_en` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `actualizado_en` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`idproducto`),
  UNIQUE KEY `sku_global` (`sku_global`),
  KEY `idcategoria` (`idcategoria`),
  KEY `idmarca` (`idmarca`),
  KEY `idx_producto_busqueda` (`nombre`,`modelo`),
  CONSTRAINT `producto_ibfk_1` FOREIGN KEY (`idcategoria`) REFERENCES `categoria` (`idcategoria`),
  CONSTRAINT `producto_ibfk_2` FOREIGN KEY (`idmarca`) REFERENCES `marca` (`idmarca`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `producto`
--

LOCK TABLES `producto` WRITE;
/*!40000 ALTER TABLE `producto` DISABLE KEYS */;
INSERT INTO `producto` VALUES (1,1,1,'AMD Ryzen 5 7600','7600','AMD-RYZEN-5-7600','https://placehold.co/480x360/e8f0ff/21457a?text=Ryzen+5+7600','Procesador AMD de 6 núcleos para socket AM5.',1,'2026-09-10 14:51:02','2026-09-10 14:51:02');
/*!40000 ALTER TABLE `producto` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `producto_especificacion`
--

DROP TABLE IF EXISTS `producto_especificacion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `producto_especificacion` (
  `idproducto_especificacion` int unsigned NOT NULL AUTO_INCREMENT,
  `idproducto` int unsigned NOT NULL,
  `atributo` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `valor` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`idproducto_especificacion`),
  UNIQUE KEY `uk_especificacion` (`idproducto`,`atributo`),
  CONSTRAINT `producto_especificacion_ibfk_1` FOREIGN KEY (`idproducto`) REFERENCES `producto` (`idproducto`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `producto_especificacion`
--

LOCK TABLES `producto_especificacion` WRITE;
/*!40000 ALTER TABLE `producto_especificacion` DISABLE KEYS */;
INSERT INTO `producto_especificacion` VALUES (1,1,'Núcleos','6'),(2,1,'Hilos','12'),(3,1,'Socket','AM5'),(4,1,'Frecuencia','3.8 GHz');
/*!40000 ALTER TABLE `producto_especificacion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `producto_match_pendiente`
--

DROP TABLE IF EXISTS `producto_match_pendiente`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `producto_match_pendiente` (
  `idmatch` bigint unsigned NOT NULL AUTO_INCREMENT,
  `idtienda` int unsigned DEFAULT NULL,
  `idproducto_tienda` int unsigned DEFAULT NULL,
  `nombre_detectado` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `nombre_tienda` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `sku_tienda` varchar(150) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `url` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `imagen` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `precio` decimal(12,2) DEFAULT NULL,
  `moneda` char(3) COLLATE utf8mb4_unicode_ci DEFAULT 'GTQ',
  `disponible` tinyint(1) DEFAULT '0',
  `puntuacion` decimal(5,2) NOT NULL,
  `estado` enum('pendiente','aprobado','rechazado') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'pendiente',
  `creado_en` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`idmatch`),
  KEY `idproducto_tienda` (`idproducto_tienda`),
  KEY `fk_match_tienda` (`idtienda`),
  CONSTRAINT `fk_match_tienda` FOREIGN KEY (`idtienda`) REFERENCES `tienda` (`idtienda`) ON DELETE SET NULL,
  CONSTRAINT `producto_match_pendiente_ibfk_1` FOREIGN KEY (`idproducto_tienda`) REFERENCES `producto_tienda` (`idproducto_tienda`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=40 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `producto_match_pendiente`
--

LOCK TABLES `producto_match_pendiente` WRITE;
/*!40000 ALTER TABLE `producto_match_pendiente` DISABLE KEYS */;
INSERT INTO `producto_match_pendiente` VALUES (1,1,1,'Procesador Ryzen 5 7600X 4.7GHz 6 Núcleos AM5','Procesador Ryzen 5 7600X 4.7GHz 6 Núcleos AM5',NULL,'https://www.kemik.gt/amd-procesador-ryzen-5-7600x-4_7ghz-6-nucleos-am5','https://static.kemikcdn.com/2025/11/23989-RZ-7600XBX1200x12001.-300x300.jpg',1953.00,'GTQ',1,0.00,'aprobado','2026-09-10 09:21:31'),(2,1,NULL,'B840M EAGLE WIFI6 Motherboard AMD AM5 Ryzen™ 7000 Series a 9000 Series, 2xDDR5 MicroATX','B840M EAGLE WIFI6 Motherboard AMD AM5 Ryzen™ 7000 Series a 9000 Series, 2xDDR5 MicroATX',NULL,'https://www.kemik.gt/gigabyte-b840m-eagle-wifi6-motherboard-amd-am5-ryzen-7000-series-a-9000-series-2xddr5-microatx','https://static.kemikcdn.com/2026/03/24292-B840MEAGLEWIFI61200x12001.-300x300.jpg',1257.00,'GTQ',1,0.00,'pendiente','2026-09-10 09:21:31'),(3,1,NULL,'PRIME B840-PLUS WIFI Motherboard AM5 Ryzen 9000 Series 4xDDR5 ATX','PRIME B840-PLUS WIFI Motherboard AM5 Ryzen 9000 Series 4xDDR5 ATX',NULL,'https://www.kemik.gt/asus-prime-b840-plus-wifi-motherboard-am5-ryzen-9000-series-4xddr5-atx','https://static.kemikcdn.com/2025/02/PRIMEB840-PLUSWIFI-ASUS-1200x1200-01.-300x300.jpg',1606.00,'GTQ',1,0.00,'pendiente','2026-09-10 09:21:31'),(4,1,NULL,'PRIME A620AM-K Motherboard Gaming AMD AM5 2xDDR5 MicroATX','PRIME A620AM-K Motherboard Gaming AMD AM5 2xDDR5 MicroATX',NULL,'https://www.kemik.gt/asus-prime-a620am-k-motherboard-gaming-amd-am5-2xddr5-microatx','https://static.kemikcdn.com/2026/08/CP82201200x12001A.-300x300.jpg',799.00,'GTQ',1,0.00,'pendiente','2026-09-10 09:21:31'),(5,1,NULL,'OmniBook 5 NGAI 16 Ryzen 5 AI 340 + 16GB RAM + 512GB SSD, Win 11 Home, Plata - En Español','OmniBook 5 NGAI 16 Ryzen 5 AI 340 + 16GB RAM + 512GB SSD, Win 11 Home, Plata - En Español',NULL,'https://www.kemik.gt/hp-omnibook-5-ngai-16-ryzen-5-ai-340-16gb-ram-512gb-ssd-win-11-home-plata-en-espanol','https://static.kemikcdn.com/2025/07/BM7W1LA-1200x1200-1.-300x300.jpg',6105.00,'GTQ',1,0.00,'pendiente','2026-09-10 09:21:31'),(6,1,NULL,'Motherboard ASUS ROG Strix B850-A Gaming WiFi ATX AM5 con PCIe 5.0 y Wi-Fi 7 para Procesadores AMD Ryzen - Blanco/Plata','Motherboard ASUS ROG Strix B850-A Gaming WiFi ATX AM5 con PCIe 5.0 y Wi-Fi 7 para Procesadores AMD Ryzen - Blanco/Plata',NULL,'https://www.kemik.gt/asus-rog-strix-b850-a-gaming-wifi-amd-am5-b850-atx-placa-base-1422-etapas-de-potencia-ddr5-aemp-lan-2_5g-wifi-7-con-antena-q-4x-m_2-pcie-5_0-usb-20gbps-tipo-c-ai-networking-ii-asus-ai','https://static.kemikcdn.com/2025/02/81ZJGsaELhL.-300x300.jpg',2444.00,'GTQ',1,0.00,'pendiente','2026-09-10 09:21:31'),(7,1,NULL,'Mini PC Beelink SER8 Ryzen 7 8745HS 32GB RAM + 1TB SSD, Sin SO - Gris','Mini PC Beelink SER8 Ryzen 7 8745HS 32GB RAM + 1TB SSD, Sin SO - Gris',NULL,'https://www.kemik.gt/beelink-ser8-mini-pc-amd-ryzen-7-8745hs-hasta-4_9-ghz-32-gb-ddr5-1-tb-pcie4_0-ssd-amd-radeon-780m-mini-computadora-de-escritorio-4k-triple-pantalla-hdmi-2_1dpusb4_wifi-6_bt5_2_2_5g-lan-r7-8745hs-32gb1tb','https://static.kemikcdn.com/2025/02/61VPjLRVCwL.-300x300.jpg',7659.00,'GTQ',1,0.00,'pendiente','2026-09-10 09:21:31'),(8,1,NULL,'PRO B850-S WiFi6E Motherboard AMD AM5 DDR5 ATX','PRO B850-S WiFi6E Motherboard AMD AM5 DDR5 ATX',NULL,'https://www.kemik.gt/msi-pro-b850-s-wifi6e-motherboard-amd-am5-ddr5-atx','https://static.kemikcdn.com/2026/03/CP8195-1200x1200-7.-300x300.jpg',2113.00,'GTQ',1,0.00,'pendiente','2026-09-10 09:21:31'),(9,1,NULL,'B850M Gaming Plus WiFi6E Motherboard AMD AM5 DDR5 Micro-ATX - Blanco','B850M Gaming Plus WiFi6E Motherboard AMD AM5 DDR5 Micro-ATX - Blanco',NULL,'https://www.kemik.gt/msi-b850m-gaming-plus-wifi6e-motherboard-amd-am5-ddr5-micro-atx-blanco','https://static.kemikcdn.com/2026/03/CP8194-1200x1200-7.-300x300.jpg',2000.00,'GTQ',1,0.00,'pendiente','2026-09-10 09:21:31'),(10,1,NULL,'PRO B850M-B GEN4 Motherboard AMD AM5 DDR5 Micro-ATX','PRO B850M-B GEN4 Motherboard AMD AM5 DDR5 Micro-ATX',NULL,'https://www.kemik.gt/msi-pro-b850m-b-gen4-motherboard-amd-am5-ddr5-micro-atx','https://static.kemikcdn.com/2026/03/CP8196-1200x1200-5.-300x300.jpg',1154.00,'GTQ',1,0.00,'pendiente','2026-09-10 09:21:31'),(11,1,NULL,'B840 Gaming Plus WiFi Motherboard AMD AM5 4xDDR5, ATX','B840 Gaming Plus WiFi Motherboard AMD AM5 4xDDR5, ATX',NULL,'https://www.kemik.gt/msi-b840-gaming-plus-wifi-motherboard-atx-supports-amd-ryzen-9000_8000-_-7000-processors-am5-ddr5-memory-boost-8000-mt_s-oc-pcie-4_0-x16-m_2-gen4-wi-fi-7-2_5g-lan','https://static.kemikcdn.com/2026/08/CP82071200x12001.-300x300.jpg',1872.00,'GTQ',1,0.00,'pendiente','2026-09-10 09:21:31'),(12,1,NULL,'Procesador de Escritorio Desbloqueado Ryzen 9 7900X, 12 Núcleos y 24 Hilos, AM5','Procesador de Escritorio Desbloqueado Ryzen 9 7900X, 12 Núcleos y 24 Hilos, AM5',NULL,'https://www.kemik.gt/amd-procesador-de-escritorio-desbloqueado-ryzen-9-7900x-de-12-nucleos-24-hilos-solo-cpu-ryzen-9-7900x','https://static.kemikcdn.com/2026/01/51OEiWrUtqL.-1085x700.-310x200.jpg',3646.00,'GTQ',1,0.00,'pendiente','2026-09-10 09:21:31'),(13,1,NULL,'Procesador de Escritorio Desbloqueado Ryzen 7 7700X, 8 Núcleos y 16 Hilos, AM5','Procesador de Escritorio Desbloqueado Ryzen 7 7700X, 8 Núcleos y 16 Hilos, AM5',NULL,'https://www.kemik.gt/amd-procesador-de-escritorio-desbloqueado-ryzen-7-7700x-de-8-nucleos-y-16-hilos-solo-cpu-ryzen-7-7700x','https://static.kemikcdn.com/2023/11/51hfER1cZVL._AC_SL1500_.-259x300.jpg',2744.00,'GTQ',1,0.00,'pendiente','2026-09-10 09:21:31'),(14,1,NULL,'AK-B650M EG Motherboard AMD AM5, 2xDDR5 MicroATX','AK-B650M EG Motherboard AMD AM5, 2xDDR5 MicroATX',NULL,'https://www.kemik.gt/arktek-ak-b650m-eg-motherboard-amd-am5-2xddr5-microatx','https://static.kemikcdn.com/2026/05/CP81811200x12001.-300x300.jpg',714.00,'GTQ',1,0.00,'pendiente','2026-09-10 09:21:31'),(15,1,NULL,'B650M H Motherboard Gaming AMD AM5, 2xDDR5 MicroATX','B650M H Motherboard Gaming AMD AM5, 2xDDR5 MicroATX',NULL,'https://www.kemik.gt/gigabyte-b650m-h-motherboard-gaming-amd-am5-2xddr5-microatx','https://static.kemikcdn.com/2026/01/115691200x12001.-300x300.jpg',802.00,'GTQ',1,0.00,'pendiente','2026-09-10 09:21:31'),(16,1,NULL,'Ryzen 5 9600 Procesador 6 Núcleos 12 Hilos hasta 5.2GHz, Socket AM5 con Gráficos Integrados - Disipador Incluido','Ryzen 5 9600 Procesador 6 Núcleos 12 Hilos hasta 5.2GHz, Socket AM5 con Gráficos Integrados - Disipador Incluido',NULL,'https://www.kemik.gt/amd-ryzen-5-9600-procesador-6-nucleos-12-hilos-hasta-5_2ghz-socket-am5-con-graficos-integrados-disipador-incluido','https://static.kemikcdn.com/2026/05/CP6024-1200x1200-1.-300x300.jpg',2434.00,'GTQ',1,0.00,'pendiente','2026-09-10 09:21:31'),(17,1,NULL,'Laptop HP 15-fc0353la Ryzen 5-7530U 8GB RAM + 512GB SSD 15.6\", Win 11 Home Español, Negro','Laptop HP 15-fc0353la Ryzen 5-7530U 8GB RAM + 512GB SSD 15.6\", Win 11 Home Español, Negro',NULL,'https://www.kemik.gt/laptop-hp-15-fc0353la-ryzen-5-7530u-8gb-ram-512gb-ssd-15_6pulgadas-win-11-home-espanol-negro','https://static.kemikcdn.com/2026/07/D6ZM8LAABM-HP-1200X1200-1.-300x300.jpg',4863.00,'GTQ',1,0.00,'pendiente','2026-09-10 09:21:31'),(18,1,NULL,'Procesador Ryzen 5 5600GT 3.6GHz 6 Núcleos AM4','Procesador Ryzen 5 5600GT 3.6GHz 6 Núcleos AM4',NULL,'https://www.kemik.gt/amd-procesador-ryzen-5-5600gt-3_6ghz-6-nucleos-am4','https://static.kemikcdn.com/2024/10/100-100001488BOX-AMD-1200x1200-01.-300x300.jpg',1689.00,'GTQ',1,0.00,'pendiente','2026-09-10 09:21:31'),(19,1,NULL,'Laptop Asus Vivobook Go 15 Ryzen 5 7520U 16GB RAM + 512GB SSD, 15.6\" Windows 11 Home en Español - Negro','Laptop Asus Vivobook Go 15 Ryzen 5 7520U 16GB RAM + 512GB SSD, 15.6\" Windows 11 Home en Español - Negro',NULL,'https://www.kemik.gt/laptop-asus-vivobook-go-15-ryzen-5-7520u-16gb-ram-512gb-ssd-15_6pulgadas-windows-11-home-negro','https://static.kemikcdn.com/2025/12/90NB0ZR2M03X-1200x1200-1.-300x300.jpg',5599.00,'GTQ',1,0.00,'pendiente','2026-09-10 09:21:31'),(20,1,NULL,'All-in-one Ryzen 5 7520U + 8GB RAM + 512GB SSD 23.8\" Win 11 Home, Blanco en Español','All-in-one Ryzen 5 7520U + 8GB RAM + 512GB SSD 23.8\" Win 11 Home, Blanco en Español',NULL,'https://www.kemik.gt/hp-all-in-one-ryzen-5-7520u-8gb-ram-512gb-ssd-win-11-home-blanco-en-espanol','https://static.kemikcdn.com/2025/07/BA1V5LA-1200x1200-1.-300x300.jpg',7544.00,'GTQ',1,0.00,'pendiente','2026-09-10 09:21:31'),(21,1,NULL,'Desktop NSX Ryzen 5 5500 16GB RAM + 512GB SSD + RTX 3050 6GB, Win11 Home - Negro','Desktop NSX Ryzen 5 5500 16GB RAM + 512GB SSD + RTX 3050 6GB, Win11 Home - Negro',NULL,'https://www.kemik.gt/desktop-nsx-ryzen-5-5500-8gb-ram-500gb-ssd-rtx-3050-6gb-win11-home-negro','https://static.kemikcdn.com/2025/05/R555008G500GRTX3050-NSX-1200x1200-01.-300x300.jpg',9139.00,'GTQ',1,0.00,'pendiente','2026-09-10 09:21:31'),(22,1,NULL,'Desktop NSX Ryzen 5 5600GT 16GB RAM + 512GB SSD, FreeDOS - Negro','Desktop NSX Ryzen 5 5600GT 16GB RAM + 512GB SSD, FreeDOS - Negro',NULL,'https://www.kemik.gt/desktop-nsx-ryzen-5-5600g-16gb-ram-512gb-ssd-freedos-negro','https://static.kemikcdn.com/2025/05/R55600G16G512G-NSX-1200x1200-01.-300x300.jpg',6320.00,'GTQ',1,0.00,'pendiente','2026-09-10 09:21:31'),(23,1,NULL,'Procesador Ryzen 5 8600G 4.3GHz 6 Núcleos AM5','Procesador Ryzen 5 8600G 4.3GHz 6 Núcleos AM5',NULL,'https://www.kemik.gt/amd-procesador-ryzen-5-8600g-4_3ghz-6-nucleos-am5','https://static.kemikcdn.com/2024/12/100-100001237BOX-AMD-1200x1200-01.-300x300.jpg',1739.00,'GTQ',1,0.00,'pendiente','2026-09-10 09:21:31'),(24,1,NULL,'Procesador Ryzen 5 8500G 3.5GHz 6 Núcleos AM5','Procesador Ryzen 5 8500G 3.5GHz 6 Núcleos AM5',NULL,'https://www.kemik.gt/amd-procesador-ryzen-5-8500g-3_5ghz-6-nucleos-am5','https://static.kemikcdn.com/2024/10/100-100000931BOX-AMD-1200x1200-01.-300x300.jpg',1454.00,'GTQ',1,0.00,'pendiente','2026-09-10 09:21:31'),(25,1,NULL,'Laptop Dell DC15255 AMD Ryzen 5 7520U 8GB RAM + 512GB SSD, 15.6\" FHD a 120Hz, Win11 Home en Español Plateado','Laptop Dell DC15255 AMD Ryzen 5 7520U 8GB RAM + 512GB SSD, 15.6\" FHD a 120Hz, Win11 Home en Español Plateado',NULL,'https://www.kemik.gt/laptop-dell-dc15255-amd-ryzen-5-7520u-8gb-ram-512gb-ssd-15_6pulgadas-fhd-a-120hz-win11-home-en-espanol-plateado','https://static.kemikcdn.com/2026/04/24784-JMF3D1200x12001.-300x300.jpg',6255.00,'GTQ',1,0.00,'pendiente','2026-09-10 09:21:31'),(26,1,NULL,'Procesador Ryzen 5 9600X 3.9GHz 6 Núcleos AM5','Procesador Ryzen 5 9600X 3.9GHz 6 Núcleos AM5',NULL,'https://www.kemik.gt/amd-procesador-ryzen-5-9600x-3_9ghz-6-nucleos-am5','https://static.kemikcdn.com/2025/11/23974-RZ9600XWOF1200x12001.-300x300.jpg',2343.00,'GTQ',1,0.00,'pendiente','2026-09-10 09:21:31'),(27,1,NULL,'Laptop HP Ryzen 5-7520U 8GB RAM + 1TB SSD 15.6\" Touch, Win 11 Home en Español - Plateado','Laptop HP Ryzen 5-7520U 8GB RAM + 1TB SSD 15.6\" Touch, Win 11 Home en Español - Plateado',NULL,'https://www.kemik.gt/laptop-hp-ryzen-5-7520u-8gb-ram-1tb-ssd-15_6pulgadas-touch-win-11-home-en-espanol-plateado','https://static.kemikcdn.com/2026/06/LP2280-HP-1200X1200-1.-300x300.jpg',5476.00,'GTQ',1,0.00,'pendiente','2026-09-10 09:21:31'),(28,1,NULL,'Laptop HP 15-fc0250la Ryzen 5 7520U 8GB RAM + 512GB SSD 15.6\" Win11 Home en Español Azul','Laptop HP 15-fc0250la Ryzen 5 7520U 8GB RAM + 512GB SSD 15.6\" Win11 Home en Español Azul',NULL,'https://www.kemik.gt/laptop-hp-15-fc0250la-ryzen-5-7520u-8gb-ram-512gb-ssd-15_6pulgadas-win11-home-en-espanol-azul','https://static.kemikcdn.com/2025/07/B9TP1LA-HP-1200x1200-01.-300x300.jpg',6162.00,'GTQ',1,0.00,'pendiente','2026-09-10 09:21:31'),(29,1,NULL,'Laptop Dell DC15255 Ryzen 5 7520U 8GB RAM + 512GB SSD 15.6\" Win11 Home en Español - Plateado','Laptop Dell DC15255 Ryzen 5 7520U 8GB RAM + 512GB SSD 15.6\" Win11 Home en Español - Plateado',NULL,'https://www.kemik.gt/laptop-dell-dc15255-ryzen-5-7520u-8gb-ram-512gb-ssd-15_6pulgadas-win11-home-en-espanol-plateado','https://static.kemikcdn.com/2026/02/JMF3D-DELL-1200x1200-01.-300x300.jpg',4726.00,'GTQ',1,0.00,'pendiente','2026-09-10 09:21:31'),(30,1,NULL,'Mini PC Beelink SER5 Ryzen 5 5500 Pro 32GB RAM+ 500GB SSD, Sin SO - Negro','Mini PC Beelink SER5 Ryzen 5 5500 Pro 32GB RAM+ 500GB SSD, Sin SO - Negro',NULL,'https://www.kemik.gt/beelink-mini-pc-ser5-amd-ryzen-7-5800h-pro-8c_16t-hasta-4_4-ghz-mini-computadora-con-16-gb-ddr4-ram_500gb-m_2-2280-ssd-micro-pc-compatible-con-4k-fps-wifi6_bt5_2_usb3_2_hogar_oficina_juego-ser-5-16g500gb-5800h-pro','https://static.kemikcdn.com/2024/07/71g-wpEXPrL.-300x300.jpg',5684.00,'GTQ',1,0.00,'pendiente','2026-09-10 09:21:31'),(31,1,NULL,'Laptop Acer Aspire Lite 15 Ryzen 5 6600H 16GB RAM + 512GB SSD 15.6\" Win11 Home Plateado en Español','Laptop Acer Aspire Lite 15 Ryzen 5 6600H 16GB RAM + 512GB SSD 15.6\" Win11 Home Plateado en Español',NULL,'https://www.kemik.gt/laptop-acer-aspire-lite-15-ryzen-5-6600h-16gb-ram-512gb-ssd-15_6pulgadas-win11-home-plateado-en-espanol','https://static.kemikcdn.com/2025/12/NX.JCFAL.002-ACER-1200x1200-01.-300x300.jpg',4768.00,'GTQ',1,0.00,'pendiente','2026-09-10 09:21:31'),(32,1,NULL,'Desktop All in One 24-cr0251la AMD Ryzen 5 7520U 8GB RAM + 512GB SSD, 23.8\" FHD, Win11 Home Blanco Nácar','Desktop All in One 24-cr0251la AMD Ryzen 5 7520U 8GB RAM + 512GB SSD, 23.8\" FHD, Win11 Home Blanco Nácar',NULL,'https://www.kemik.gt/desktop-all-in-one-24-cr0251la-amd-ryzen-5-7520u-8gb-ram-512gb-ssd-23_8pulgadas-fhd-win11-home-blanco-nacar','https://static.kemikcdn.com/2026/07/PC006HPR841200x12001.-300x300.jpg',5542.00,'GTQ',1,0.00,'pendiente','2026-09-10 09:21:31'),(33,1,NULL,'Laptop MSI Thin A15 AMD Ryzen 5 7535HS 8GB RAM + 512GB SSD + NVIDIA® GeForce RTX™ 4050, 15.6\" FHD a 144Hz, Win11 Home Inglés','Laptop MSI Thin A15 AMD Ryzen 5 7535HS 8GB RAM + 512GB SSD + NVIDIA® GeForce RTX™ 4050, 15.6\" FHD a 144Hz, Win11 Home Inglés',NULL,'https://www.kemik.gt/laptop-msi-thin-a15-amd-ryzen-5-7535hs-8gb-ram-512gb-ssd-nvidia-geforce-rtx-4050-15_6pulgadas-fhd-a-144hz-win11-home-ingles','https://static.kemikcdn.com/2026/07/8241424114761200x12001.-300x300.jpg',8485.00,'GTQ',1,0.00,'pendiente','2026-09-10 09:21:31'),(34,1,NULL,'Laptop Lenovo IdeaPad 1 AMD Ryzen 5 7520U 8GB RAM + 256GB SSD, 15.6\" FHD, Win11 Home Inglés Abyss Blue','Laptop Lenovo IdeaPad 1 AMD Ryzen 5 7520U 8GB RAM + 256GB SSD, 15.6\" FHD, Win11 Home Inglés Abyss Blue',NULL,'https://www.kemik.gt/laptop-lenovo-ideapad-1-amd-ryzen-5-7520u-8gb-ram-256gb-ssd-15_6pulgadas-fhd-win11-home-ingles-abyss-blue','https://static.kemikcdn.com/2026/02/1992713366011200x12001.-300x300.jpg',4197.00,'GTQ',1,0.00,'pendiente','2026-09-10 09:21:31'),(35,1,NULL,'Laptop IdeaPad Slim 3 Ryzen 5 40 16GB RAM + 512GB SSD, 15.6\" FHD, Win11 Home en Español - Azul Claro','Laptop IdeaPad Slim 3 Ryzen 5 40 16GB RAM + 512GB SSD, 15.6\" FHD, Win11 Home en Español - Azul Claro',NULL,'https://www.kemik.gt/lenovo-laptop-ideapad-slim-3-ryzen-5-40-16gb-ram-512gb-ssd-15_6pulgadas-fhd-win11-home-en-espanol-azul-claro','https://static.kemikcdn.com/2026/07/NT089LEN68-1200x1200-9.-300x300.jpg',11645.00,'GTQ',1,0.00,'pendiente','2026-09-10 09:21:31'),(36,1,NULL,'Laptop Lenovo IdeaPad Slim 3 15ABR8 Ryzen 5 5625U 16GB RAM + 512GB SSD, 15.6\" FHD, Windows 11 Home Español - Azul','Laptop Lenovo IdeaPad Slim 3 15ABR8 Ryzen 5 5625U 16GB RAM + 512GB SSD, 15.6\" FHD, Windows 11 Home Español - Azul',NULL,'https://www.kemik.gt/laptop-lenovo-ideapad-slim-3-15abr8-ryzen-5-5625u-16gb-ram-512gb-ssd-15_6pulgadas-fhd-windows-11-home-espanol-azul','https://static.kemikcdn.com/2026/05/NT081LEN10-1200x1200-6.-300x300.jpg',12899.00,'GTQ',1,0.00,'pendiente','2026-09-10 09:21:31'),(37,1,NULL,'Laptop Lenovo ThinkBook 16 G7 ARP Ryzen 5-7535HS 16GB RAM + 512GB SSD, AMD Radeon 660M, Win 11 Pro Español - Negro','Laptop Lenovo ThinkBook 16 G7 ARP Ryzen 5-7535HS 16GB RAM + 512GB SSD, AMD Radeon 660M, Win 11 Pro Español - Negro',NULL,'https://www.kemik.gt/laptop-lenovo-thinkbook-16-g7-arp-ryzen-5-7535hs-16gb-ram-512gb-ssd-amd-radeon-660m-win-11-pro-espanol-negro','https://static.kemikcdn.com/2026/07/NT076LEN57-Lenovo-1200x1200-3.-300x300.jpg',17934.00,'GTQ',1,0.00,'pendiente','2026-09-10 09:21:31'),(38,1,NULL,'Procesador AMD Ryzen 7 5700 (8 Núcleos / 16 Hilos, Hasta 4.6 GHz, Socket AM4, 65W) - Incluye Disipador Wraith Stealth','Procesador AMD Ryzen 7 5700 (8 Núcleos / 16 Hilos, Hasta 4.6 GHz, Socket AM4, 65W) - Incluye Disipador Wraith Stealth',NULL,'https://www.kemik.gt/amd-ryzen-7-5700-8-cores-_-16-thread-65w-tdp-socket-am4-l2l3-cache-20mb-up-to-4_6ghz-boost-clock-wraith-stealth-cooler','https://static.kemikcdn.com/2026/05/510zj43C3iL.-300x300.jpg',1882.00,'GTQ',1,0.00,'pendiente','2026-09-10 09:21:31'),(39,1,NULL,'Motherboard MSI PRO B550M-VC WiFi AM4, PCIe 4.0 y Wi-Fi 6E para Procesadores AMD Ryzen 3000, 4000 y 5000 - Negro','Motherboard MSI PRO B550M-VC WiFi AM4, PCIe 4.0 y Wi-Fi 6E para Procesadores AMD Ryzen 3000, 4000 y 5000 - Negro',NULL,'https://www.kemik.gt/msi-pro-b550m-vc-wifi-proseries-motherboard-amd-ryzen-5000-series-am4-ddr4-pcie-4_0-sata-6gb_s-m_2-usb-3_2-gen-2-hdmi_dp-wi-fi-6e-bluetooth-5_2-matx-9_6pulgadas-x-9_6pulgadas-pro-b550m-vc-wifi','https://static.kemikcdn.com/2026/01/71Mumt38AtL.-400x300.-267x200.jpg',1505.00,'GTQ',1,0.00,'pendiente','2026-09-10 09:21:31');
/*!40000 ALTER TABLE `producto_match_pendiente` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `producto_tienda`
--

DROP TABLE IF EXISTS `producto_tienda`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `producto_tienda` (
  `idproducto_tienda` int unsigned NOT NULL AUTO_INCREMENT,
  `idproducto` int unsigned NOT NULL,
  `idtienda` int unsigned NOT NULL,
  `nombre_tienda` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `sku_tienda` varchar(150) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `url` varchar(500) COLLATE utf8mb4_unicode_ci NOT NULL,
  `imagen` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `disponibilidad` tinyint(1) NOT NULL DEFAULT '0',
  `estado` tinyint(1) NOT NULL DEFAULT '1',
  `creado_en` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `actualizado_en` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`idproducto_tienda`),
  UNIQUE KEY `uk_producto_tienda` (`idproducto`,`idtienda`),
  UNIQUE KEY `uk_sku_tienda` (`idtienda`,`sku_tienda`),
  KEY `idx_pt_disponibilidad` (`disponibilidad`,`estado`),
  CONSTRAINT `producto_tienda_ibfk_1` FOREIGN KEY (`idproducto`) REFERENCES `producto` (`idproducto`) ON DELETE CASCADE,
  CONSTRAINT `producto_tienda_ibfk_2` FOREIGN KEY (`idtienda`) REFERENCES `tienda` (`idtienda`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `producto_tienda`
--

LOCK TABLES `producto_tienda` WRITE;
/*!40000 ALTER TABLE `producto_tienda` DISABLE KEYS */;
INSERT INTO `producto_tienda` VALUES (1,1,1,'Procesador Ryzen 5 7600X 4.7GHz 6 Núcleos AM5','K-R57600','https://www.kemik.gt/amd-procesador-ryzen-5-7600x-4_7ghz-6-nucleos-am5','https://static.kemikcdn.com/2025/11/23989-RZ-7600XBX1200x12001.-300x300.jpg',1,1,'2026-09-10 14:51:02','2026-09-10 09:30:19'),(2,1,2,'Procesador AMD R5-7600 AM5','I-R57600','https://www.intelaf.com','https://placehold.co/480x360/e8f0ff/21457a?text=Ryzen+5+7600',1,1,'2026-09-10 14:51:02','2026-09-10 14:51:02'),(3,1,3,'Ryzen 5 7600 AMD','P-R57600','https://www.pacifiko.com','https://placehold.co/480x360/e8f0ff/21457a?text=Ryzen+5+7600',1,1,'2026-09-10 14:51:02','2026-09-10 14:51:02');
/*!40000 ALTER TABLE `producto_tienda` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `scraper_log`
--

DROP TABLE IF EXISTS `scraper_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `scraper_log` (
  `idscraper_log` bigint unsigned NOT NULL AUTO_INCREMENT,
  `idtienda` int unsigned DEFAULT NULL,
  `fecha_inicio` datetime NOT NULL,
  `fecha_fin` datetime DEFAULT NULL,
  `productos_encontrados` int unsigned NOT NULL DEFAULT '0',
  `productos_actualizados` int unsigned NOT NULL DEFAULT '0',
  `errores` int unsigned NOT NULL DEFAULT '0',
  `estado` enum('ejecutando','completado','error') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'ejecutando',
  `mensaje` text COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY (`idscraper_log`),
  KEY `idtienda` (`idtienda`),
  KEY `idx_scraper_log_fecha` (`fecha_inicio` DESC),
  CONSTRAINT `scraper_log_ibfk_1` FOREIGN KEY (`idtienda`) REFERENCES `tienda` (`idtienda`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `scraper_log`
--

LOCK TABLES `scraper_log` WRITE;
/*!40000 ALTER TABLE `scraper_log` DISABLE KEYS */;
INSERT INTO `scraper_log` VALUES (1,1,'2026-09-10 09:21:31','2026-09-10 09:21:31',40,1,39,'error',NULL),(2,1,'2026-09-10 09:29:05','2026-09-10 09:29:05',40,1,39,'error',NULL);
/*!40000 ALTER TABLE `scraper_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tienda`
--

DROP TABLE IF EXISTS `tienda`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tienda` (
  `idtienda` int unsigned NOT NULL AUTO_INCREMENT,
  `nombre` varchar(120) COLLATE utf8mb4_unicode_ci NOT NULL,
  `url` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `logo` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `estado` tinyint(1) NOT NULL DEFAULT '1',
  PRIMARY KEY (`idtienda`),
  UNIQUE KEY `nombre` (`nombre`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tienda`
--

LOCK TABLES `tienda` WRITE;
/*!40000 ALTER TABLE `tienda` DISABLE KEYS */;
INSERT INTO `tienda` VALUES (1,'Kemik','https://www.kemik.gt','',1),(2,'Intelaf','https://www.intelaf.com','',1),(3,'Pacifiko','https://www.pacifiko.com','',1);
/*!40000 ALTER TABLE `tienda` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping events for database 'compara_tech_gt'
--

--
-- Dumping routines for database 'compara_tech_gt'
--
--
-- WARNING: can't read the INFORMATION_SCHEMA.libraries table. It's most probably an old server 8.4.3.
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-09-10 15:45:04
