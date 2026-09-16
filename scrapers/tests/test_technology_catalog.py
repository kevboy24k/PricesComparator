import unittest

from core.product_matcher import product_type
from core.technology_catalog import (
    CATEGORY_ATTRIBUTE_CATALOG,
    attributes_match,
    build_search_profile,
    query_variants,
)
from live_ingest import relevant


class TechnologyCatalogTests(unittest.TestCase):
    def test_every_supported_category_has_a_profile_and_extractable_example(self):
        cases = {
            'cpu': ('Procesador AMD AM5 6 nucleos', 'Procesador AMD Ryzen AM5 6 nucleos', {'brand': 'amd', 'socket': 'am5', 'cores': 6}),
            'gpu': ('Tarjeta grafica MSI RTX 5070 12GB Ventus', 'Tarjeta grafica MSI RTX 5070 12GB Ventus', {'brand': 'msi', 'vram_gb': 12, 'edition': 'ventus'}),
            'ram': ('Memoria RAM DDR5 16GB 5600MHz DIMM', 'Memoria Kingston DDR5 16GB 5600MHz DIMM', {'capacity_gb': 16, 'memory_generation': 'ddr5', 'speed_mts': 5600}),
            'storage': ('SSD SATA 500GB 2.5', 'SSD Crucial SATA 512GB 2.5', {'storage_interface': 'sata', 'form_factor': '2.5'}),
            'motherboard': ('Motherboard ASUS B650 DDR5 AM5 ATX', 'Motherboard ASUS B650 DDR5 AM5 ATX', {'brand': 'asus', 'chipset': 'b650', 'memory_generation': 'ddr5'}),
            'laptop': ('Laptop Lenovo 16GB RAM 1TB SSD 15 pulgadas', 'Laptop Lenovo 16GB RAM 1TB SSD 15 pulgadas', {'brand': 'lenovo', 'ram_gb': 16, 'storage_gb': 1000}),
            'computer': ('PC HP 32GB RAM 1TB SSD', 'PC HP 32GB RAM 1TB SSD', {'brand': 'hp', 'ram_gb': 32, 'storage_gb': 1000}),
            'monitor': ('Monitor LG 27 pulgadas QHD 165Hz IPS', 'Monitor LG 27 pulgadas 2560x1440 165Hz IPS', {'brand': 'lg', 'resolution': 'qhd', 'refresh_hz': 165}),
            'keyboard': ('Teclado Logitech Bluetooth ANSI Red', 'Teclado Logitech Bluetooth ANSI Red', {'brand': 'logitech', 'connection': 'bluetooth', 'layout': 'ansi'}),
            'mouse': ('Mouse Logitech inalambrico 16000 DPI 6 botones', 'Mouse Logitech wireless 16000 DPI 6 botones', {'brand': 'logitech', 'connection': 'wireless', 'sensor_dpi': 16000}),
            'audio': ('Audifonos HyperX Bluetooth cancelacion de ruido', 'Audifonos HyperX Bluetooth ANC', {'brand': 'hyperx', 'connection': 'bluetooth', 'noise_cancelling': True}),
            'webcam': ('Webcam Logitech Full HD 30 FPS USB', 'Webcam Logitech 1080p 30 FPS USB', {'brand': 'logitech', 'resolution': 'fhd', 'frame_rate': 30}),
            'network': ('Router TP Link WiFi 6 4 puertos', 'Router TP Link WiFi 6 4 puertos', {'brand': 'tp link', 'network_type': 'router', 'wifi_standard': 'wifi6'}),
            'printer': ('Impresora Epson laser a color USB', 'Impresora Epson laser color USB', {'brand': 'epson', 'printer_type': 'laser', 'color': True}),
            'tablet': ('Tablet Apple 128GB 11 pulgadas', 'Tablet Apple 128GB 11 pulgadas', {'brand': 'apple', 'storage_gb': 128, 'screen_inches': 11.0}),
            'phone': ('Celular Samsung 256GB 8GB RAM', 'Celular Samsung 256GB 8GB RAM', {'brand': 'samsung', 'storage_gb': 256, 'ram_gb': 8}),
            'console': ('PS5 1TB', 'Consola PlayStation 5 1TB', {'platform': 'playstation', 'storage_gb': 1000}),
            'case': ('Gabinete Corsair ATX negro vidrio', 'Gabinete Corsair ATX black tempered glass', {'brand': 'corsair', 'form_factor': 'atx', 'color': 'black'}),
            'power_supply': ('Fuente de poder Corsair 750W 80 Plus Gold semi modular', 'Fuente Corsair 750W 80 Plus Gold semi modular', {'brand': 'corsair', 'power_w': 750, 'efficiency': '80_plus_gold'}),
            'cooling': ('Refrigeracion liquida Corsair 360mm AM5', 'Liquid cooling Corsair 360mm AM5', {'brand': 'corsair', 'cooling_type': 'liquid', 'radiator_mm': 360}),
            'accessory': ('Adaptador USB Logitech', 'Adaptador USB Logitech', {'brand': 'logitech', 'accessory_type': 'adapter', 'connection': 'usb'}),
        }
        self.assertEqual(set(cases), set(CATEGORY_ATTRIBUTE_CATALOG))
        for category, (query, offer, expected) in cases.items():
            with self.subTest(category=category):
                self.assertEqual(product_type({'name': query}), category)
                profile = build_search_profile(query, category)
                for key, value in expected.items():
                    self.assertEqual(profile.attributes.get(key), value)
                self.assertTrue(attributes_match(profile, offer))

    def test_monitor_aliases_and_strict_attributes_filter_results(self):
        query = 'Monitor 27 pulgadas Full HD 144 Hz IPS'
        profile = build_search_profile(query, product_type({'name': query}))
        self.assertIn('Monitor 27 1920x1080 144 Hz', query_variants('Monitor 27 Full HD 144 Hz', profile))
        self.assertTrue(relevant({'name': 'Monitor LG 27 pulgadas FHD IPS 144Hz'}, query, profile))
        self.assertFalse(relevant({'name': 'Monitor LG 27 pulgadas QHD IPS 144Hz'}, query, profile))
        self.assertFalse(relevant({'name': 'Monitor LG 32 pulgadas FHD IPS 144Hz'}, query, profile))
        self.assertFalse(relevant({'name': 'Laptop LG 27 pulgadas FHD IPS 144Hz'}, query, profile))


if __name__ == '__main__':
    unittest.main()
