"""Catálogo canónico de atributos tecnológicos y perfiles de búsqueda.

Las reglas de seguridad del ``product_matcher`` siguen decidiendo qué tipo de
artículo es una oferta. Este módulo aporta una capa de datos: define qué
atributos importan en cada categoría, extrae los que aparecen en una consulta
o título y conoce equivalencias comerciales de capacidad (480/500/512 GB,
por ejemplo). No acepta tipos de producto distintos; esa validación permanece
en el matcher principal.
"""

from __future__ import annotations

from dataclasses import dataclass
import re
import unicodedata


# Los códigos se replican en categoria_atributo para que administración, IA y
# scripts de importación compartan el mismo vocabulario.
CATEGORY_ATTRIBUTE_CATALOG: dict[str, dict[str, object]] = {
    "cpu": {"label": "Procesadores", "attributes": ("brand", "model", "socket", "cores", "threads", "generation")},
    "gpu": {"label": "Tarjetas gráficas", "attributes": ("brand", "model", "vram_gb", "chipset_brand", "edition")},
    "ram": {"label": "Memorias RAM", "attributes": ("brand", "capacity_gb", "memory_generation", "speed_mts", "form_factor")},
    "storage": {"label": "SSD", "attributes": ("brand", "capacity_gb", "storage_interface", "form_factor", "protocol")},
    "motherboard": {"label": "Motherboards", "attributes": ("brand", "model", "socket", "chipset", "memory_generation", "form_factor")},
    "laptop": {"label": "Laptops", "attributes": ("brand", "model", "cpu_model", "gpu_model", "ram_gb", "storage_gb", "screen_inches")},
    "computer": {"label": "Computadoras de escritorio", "attributes": ("brand", "model", "cpu_model", "gpu_model", "ram_gb", "storage_gb")},
    "monitor": {"label": "Monitores", "attributes": ("brand", "model", "screen_inches", "resolution", "refresh_hz", "panel_type")},
    "keyboard": {"label": "Teclados", "attributes": ("brand", "model", "connection", "layout", "switch_type")},
    "mouse": {"label": "Mouse", "attributes": ("brand", "model", "connection", "sensor_dpi", "buttons")},
    "audio": {"label": "Audio y audífonos", "attributes": ("brand", "model", "audio_type", "connection", "noise_cancelling")},
    "webcam": {"label": "Webcams", "attributes": ("brand", "model", "resolution", "frame_rate", "connection")},
    "network": {"label": "Redes", "attributes": ("brand", "model", "network_type", "wifi_standard", "ports")},
    "printer": {"label": "Impresoras", "attributes": ("brand", "model", "printer_type", "color", "connection")},
    "tablet": {"label": "Tablets", "attributes": ("brand", "model", "storage_gb", "screen_inches", "connectivity")},
    "phone": {"label": "Celulares", "attributes": ("brand", "model", "storage_gb", "ram_gb", "connectivity")},
    "console": {"label": "Consolas y videojuegos", "attributes": ("brand", "model", "storage_gb", "edition", "platform")},
    "case": {"label": "Gabinetes", "attributes": ("brand", "model", "form_factor", "color", "side_panel")},
    "power_supply": {"label": "Fuentes de poder", "attributes": ("brand", "model", "power_w", "efficiency", "modularity")},
    "cooling": {"label": "Refrigeración", "attributes": ("brand", "model", "cooling_type", "radiator_mm", "socket")},
    "accessory": {"label": "Accesorios tecnológicos", "attributes": ("brand", "model", "accessory_type", "compatibility", "connection")},
}


# Una equivalencia sirve para buscar y presentar alternativas cercanas; no
# cambia la capacidad real que se conserva en producto_tienda_atributo.
CAPACITY_GROUPS_GB: tuple[frozenset[int], ...] = (
    frozenset((64,)),
    frozenset((120, 128)),
    frozenset((240, 250, 256)),
    frozenset((480, 500, 512)),
    frozenset((960, 1000, 1024)),
    frozenset((1920, 2000, 2048)),
    frozenset((3840, 4000, 4096)),
)


@dataclass(frozen=True)
class SearchProfile:
    """Interpretación estructurada de la consulta de un usuario."""

    category: str | None
    attributes: dict[str, object]
    capacity_alternatives_gb: frozenset[int]


def canonical(text: str) -> str:
    text = unicodedata.normalize("NFKD", str(text or "")).encode("ascii", "ignore").decode().lower()
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9.]+", " ", text)).strip()


def capacity_values_gb(text: str) -> set[int]:
    """Extrae GB y TB comerciales; 1 TB se representa como 1000 GB."""
    values: set[int] = set()
    for amount, unit in re.findall(r"\b(\d+(?:[.,]\d+)?)\s*(gb|tb)\b", canonical(text)):
        value = float(amount.replace(",", "."))
        values.add(round(value * 1000) if unit == "tb" else round(value))
    return values


def capacity_equivalents(capacity_gb: int) -> frozenset[int]:
    for group in CAPACITY_GROUPS_GB:
        if capacity_gb in group:
            return group
    return frozenset((capacity_gb,))


def _first_match(text: str, patterns: dict[str, str]) -> str | None:
    normalized = canonical(text)
    for value, expression in patterns.items():
        if re.search(expression, normalized):
            return value
    return None


BRAND_PATTERNS = {
    "amd": r"\bamd\b", "intel": r"\bintel\b", "nvidia": r"\bnvidia\b", "asus": r"\basus\b",
    "msi": r"\bmsi\b", "gigabyte": r"\bgigabyte\b", "zotac": r"\bzotac\b", "pny": r"\bpny\b",
    "sapphire": r"\bsapphire\b", "kingston": r"\bkingston\b", "crucial": r"\bcrucial\b",
    "samsung": r"\bsamsung\b", "western digital": r"\b(?:western digital|wd)\b", "seagate": r"\bseagate\b",
    "corsair": r"\bcorsair\b", "g skill": r"\bg\s*skill\b", "logitech": r"\blogitech\b",
    "razer": r"\brazer\b", "steelseries": r"\bsteelseries\b", "hyperx": r"\bhyperx\b",
    "benq": r"\bbenq\b", "lg": r"\blg\b", "acer": r"\bacer\b", "dell": r"\bdell\b",
    "hp": r"\bhp\b", "lenovo": r"\blenovo\b", "apple": r"\bapple\b", "sony": r"\bsony\b",
    "canon": r"\bcanon\b", "epson": r"\bepson\b", "brother": r"\bbrother\b", "tp link": r"\btp\s*link\b",
    "huawei": r"\bhuawei\b", "xiaomi": r"\bxiaomi\b", "google": r"\bgoogle\b", "nintendo": r"\bnintendo\b",
    "playstation": r"\b(?:playstation|ps[45])\b", "xbox": r"\bxbox\b",
}

RESOLUTION_PATTERNS = {
    "fhd": r"\b(?:full\s*hd|fhd|1080p|1920\s*x\s*1080)\b",
    "qhd": r"\b(?:qhd|2k|1440p|2560\s*x\s*1440)\b",
    "uhd_4k": r"\b(?:uhd|4k|2160p|3840\s*x\s*2160)\b",
    "5k": r"\b(?:5k|5120\s*x\s*2880)\b",
    "hd": r"\b(?:hd|720p|1280\s*x\s*720)\b",
}

ATTRIBUTE_UNITS = {
    "capacity_gb": "GB", "storage_gb": "GB", "ram_gb": "GB", "vram_gb": "GB",
    "speed_mts": "MT/s", "power_w": "W", "sensor_dpi": "DPI", "refresh_hz": "Hz",
    "frame_rate": "FPS", "screen_inches": "pulgadas", "radiator_mm": "mm",
}


def _context_capacity(text: str, pattern: str) -> int | None:
    """Capacidad junto a un componente, en cualquiera de los dos órdenes."""
    normalized = canonical(text)
    before = re.search(rf"\b(\d+(?:[.,]\d+)?)\s*(gb|tb)\b\s+{pattern}\b", normalized)
    after = re.search(rf"{pattern}\b(?:\s+\w+){{0,3}}\s+(\d+(?:[.,]\d+)?)\s*(gb|tb)\b", normalized)
    found = before or after
    if not found:
        return None
    value = float(found.group(1).replace(",", "."))
    return round(value * 1000) if found.group(2) == "tb" else round(value)


def _screen_inches(text: str) -> float | None:
    raw = str(text or "").lower()
    explicit = re.search(r"\b(\d{2}(?:[.,]\d)?)\s*(?:inch(?:es)?|in\.?|pulgadas?|[\"″])", raw)
    if explicit:
        return float(explicit.group(1).replace(",", "."))
    normalized = canonical(text)
    implied = re.search(r"\b(?:monitor|pantalla|laptop|notebook|tablet)\s+(?:de\s+)?(\d{2}(?:\.\d)?)\b", normalized)
    return float(implied.group(1)) if implied else None


def _set_common_attributes(attributes: dict[str, object], normalized: str) -> None:
    brand = _first_match(normalized, BRAND_PATTERNS)
    if brand:
        attributes["brand"] = brand


def extract_attributes(text: str, category: str | None) -> dict[str, object]:
    """Obtiene solo atributos explícitos; nunca inventa una especificación."""
    normalized = canonical(text)
    attributes: dict[str, object] = {}
    _set_common_attributes(attributes, normalized)
    capacities = capacity_values_gb(normalized)
    if capacities and category in ("storage", "ram"):
        attributes["capacity_gb"] = min(capacities)

    if category == "storage":
        interface = _first_match(normalized, {
            "nvme": r"\bnvme\b", "sata": r"\bsata(?:\s*(?:iii|3))?\b",
            "sas": r"\bsas\b", "usb": r"\busb\b",
        })
        if interface:
            attributes["storage_interface"] = interface
        form_factor = _first_match(normalized, {"m2": r"\bm\s*2\b|\bm2\b", "2.5": r"\b2[.,]?5\b"})
        if form_factor:
            attributes["form_factor"] = form_factor
        protocol = _first_match(normalized, {"pcie4": r"\b(?:pcie|pci e)\s*4", "pcie5": r"\b(?:pcie|pci e)\s*5"})
        if protocol:
            attributes["protocol"] = protocol
    elif category == "ram":
        generation = _first_match(normalized, {"ddr3": r"\bddr3\b", "ddr4": r"\bddr4\b", "ddr5": r"\bddr5\b"})
        if generation:
            attributes["memory_generation"] = generation
        form_factor = _first_match(normalized, {"sodimm": r"\bso dimm\b|\bsodimm\b", "dimm": r"\bdimm\b"})
        if form_factor:
            attributes["form_factor"] = form_factor
        speed = re.search(r"\b(\d{3,5})\s*(?:mt s|mhz)\b", normalized)
        if speed:
            attributes["speed_mts"] = int(speed.group(1))
    elif category == "gpu":
        vram = re.search(r"\b(\d{1,2})\s*gb\b", normalized)
        if vram:
            attributes["vram_gb"] = int(vram.group(1))
        chipset_brand = _first_match(normalized, {"nvidia": r"\b(?:nvidia|geforce)\b", "amd": r"\b(?:amd|radeon)\b", "intel": r"\bintel\s+arc\b"})
        if chipset_brand:
            attributes["chipset_brand"] = chipset_brand
        edition = _first_match(normalized, {
            "ventus": r"\bventus\b", "tuf": r"\btuf\b", "strix": r"\bstrix\b", "suprim": r"\bsuprim\b",
            "aorus": r"\baorus\b", "eagle": r"\beagle\b", "gaming_x": r"\bgaming\s*x\b",
            "gaming_trio": r"\bgaming\s*trio\b", "dual": r"\bdual\b", "prime": r"\bprime\b",
        })
        if edition:
            attributes["edition"] = edition
    elif category == "cpu":
        socket = _first_match(normalized, {"am4": r"\bam4\b", "am5": r"\bam5\b", "lga1700": r"\blga\s*1700\b", "lga1851": r"\blga\s*1851\b"})
        if socket:
            attributes["socket"] = socket
        cores = re.search(r"\b(\d{1,2})\s*(?:cores?|nucleos?)\b", normalized)
        threads = re.search(r"\b(\d{1,2})\s*(?:threads?|hilos?)\b", normalized)
        if cores:
            attributes["cores"] = int(cores.group(1))
        if threads:
            attributes["threads"] = int(threads.group(1))
    elif category == "motherboard":
        socket = _first_match(normalized, {"am4": r"\bam4\b", "am5": r"\bam5\b", "lga1700": r"\blga\s*1700\b", "lga1851": r"\blga\s*1851\b"})
        if socket:
            attributes["socket"] = socket
        chipset = re.search(r"\b(?:[abxz]|h)\d{3,4}[a-z]?\b", normalized)
        if chipset:
            attributes["chipset"] = chipset.group(0)
        generation = _first_match(normalized, {"ddr4": r"\bddr4\b", "ddr5": r"\bddr5\b"})
        if generation:
            attributes["memory_generation"] = generation
        form_factor = _first_match(normalized, {"microatx": r"\bmicro\s*atx\b|\bmatx\b", "mini_itx": r"\bmini\s*itx\b", "atx": r"\b(?:e?atx|atx)\b"})
        if form_factor:
            attributes["form_factor"] = form_factor
    elif category in ("laptop", "computer"):
        ram = _context_capacity(normalized, r"(?:ram|ddr[345]|memoria)")
        storage = _context_capacity(normalized, r"(?:ssd|hdd|nvme|almacenamiento)")
        if ram is not None:
            attributes["ram_gb"] = ram
        if storage is not None:
            attributes["storage_gb"] = storage
        inches = _screen_inches(text)
        if category == "laptop" and inches is not None:
            attributes["screen_inches"] = inches
    elif category == "power_supply":
        watts = re.search(r"\b(\d{3,4})\s*w(?:atts?)?\b", normalized)
        if watts:
            attributes["power_w"] = int(watts.group(1))
        efficiency = _first_match(normalized, {"80_plus_bronze": r"80\s*plus\s*bronze", "80_plus_gold": r"80\s*plus\s*gold", "80_plus_platinum": r"80\s*plus\s*platinum"})
        if efficiency:
            attributes["efficiency"] = efficiency
        modularity = _first_match(normalized, {"fully_modular": r"\b(?:full|totalmente)\s*modular\b", "semi_modular": r"\bsemi\s*modular\b", "non_modular": r"\bno\s*modular\b"})
        if modularity:
            attributes["modularity"] = modularity
    elif category == "monitor":
        inches = _screen_inches(text)
        if inches is not None:
            attributes["screen_inches"] = inches
        resolution = _first_match(normalized, RESOLUTION_PATTERNS)
        if resolution:
            attributes["resolution"] = resolution
        refresh = re.search(r"\b(\d{2,3})\s*hz\b", normalized)
        if refresh:
            attributes["refresh_hz"] = int(refresh.group(1))
        panel = _first_match(normalized, {"ips": r"\bips\b", "va": r"\bva\b", "tn": r"\btn\b", "oled": r"\b(?:oled|amoled)\b", "mini_led": r"\bmini\s*led\b"})
        if panel:
            attributes["panel_type"] = panel
    elif category in ("keyboard", "mouse", "audio", "webcam", "printer", "accessory"):
        connection = _first_match(normalized, {"bluetooth": r"\bbluetooth\b", "wireless": r"\b(?:inalambric[oa]|wireless|2\.4\s*ghz)\b", "usb": r"\busb(?:\s*[ac])?\b", "wired": r"\b(?:cableado|wired)\b"})
        if connection:
            attributes["connection"] = connection
        if category == "keyboard":
            layout = _first_match(normalized, {"es": r"\b(?:espanol|latam|spanish)\b", "ansi": r"\bansi\b", "iso": r"\biso\b"})
            switch = _first_match(normalized, {"red": r"\b(?:switch\s*)?red\b", "blue": r"\b(?:switch\s*)?blue\b", "brown": r"\b(?:switch\s*)?brown\b", "membrane": r"\bmembrane\b"})
            if layout:
                attributes["layout"] = layout
            if switch:
                attributes["switch_type"] = switch
        elif category == "mouse":
            dpi = re.search(r"\b(\d{3,5})\s*dpi\b", normalized)
            buttons = re.search(r"\b(\d{1,2})\s*(?:botones|buttons)\b", normalized)
            if dpi:
                attributes["sensor_dpi"] = int(dpi.group(1))
            if buttons:
                attributes["buttons"] = int(buttons.group(1))
        elif category == "audio":
            audio_type = _first_match(normalized, {"headset": r"\bheadset\b", "headphones": r"\b(?:audifonos?|headphones?)\b", "earbuds": r"\bearbuds?\b", "speaker": r"\b(?:bocinas?|altavoces?|speaker)\b"})
            if audio_type:
                attributes["audio_type"] = audio_type
            if re.search(r"\b(?:anc|cancelacion de ruido|noise cancelling)\b", normalized):
                attributes["noise_cancelling"] = True
        elif category == "webcam":
            resolution = _first_match(normalized, RESOLUTION_PATTERNS)
            fps = re.search(r"\b(\d{2,3})\s*(?:fps|frames?)\b", normalized)
            if resolution:
                attributes["resolution"] = resolution
            if fps:
                attributes["frame_rate"] = int(fps.group(1))
        elif category == "printer":
            printer_type = _first_match(normalized, {"laser": r"\blaser\b", "inkjet": r"\b(?:inkjet|inyeccion de tinta|tinta)\b", "thermal": r"\btermica\b"})
            if printer_type:
                attributes["printer_type"] = printer_type
            if re.search(r"\b(?:color|a color)\b", normalized):
                attributes["color"] = True
            elif re.search(r"\b(?:monocromatica|blanco y negro)\b", normalized):
                attributes["color"] = False
        elif category == "accessory":
            accessory_type = _first_match(normalized, {"cable": r"\bcable\b", "adapter": r"\b(?:adaptador|adapter)\b", "stand": r"\b(?:soporte|stand)\b", "case": r"\b(?:funda|carcasa)\b", "charger": r"\bcargador\b"})
            if accessory_type:
                attributes["accessory_type"] = accessory_type
    elif category == "network":
        network_type = _first_match(normalized, {"router": r"\brouter\b", "switch": r"\bswitch\b", "access_point": r"\b(?:access point|punto de acceso)\b", "mesh": r"\bmesh\b"})
        wifi = _first_match(normalized, {"wifi7": r"\b(?:wifi|wi fi)\s*7\b", "wifi6e": r"\b(?:wifi|wi fi)\s*6e\b", "wifi6": r"\b(?:wifi|wi fi)\s*6\b", "wifi5": r"\b(?:wifi|wi fi)\s*5\b"})
        ports = re.search(r"\b(\d{1,2})\s*(?:puertos?|ports?)\b", normalized)
        if network_type:
            attributes["network_type"] = network_type
        if wifi:
            attributes["wifi_standard"] = wifi
        if ports:
            attributes["ports"] = int(ports.group(1))
    elif category in ("tablet", "phone", "console"):
        if capacities:
            # En un teléfono puede aparecer "256GB 8GB RAM"; la capacidad
            # de almacenamiento es la mayor si no hay una etiqueta explícita.
            attributes["storage_gb"] = max(capacities)
        ram = _context_capacity(normalized, r"(?:ram|memoria)")
        if category == "phone" and ram is not None:
            attributes["ram_gb"] = ram
        inches = _screen_inches(text)
        if category == "tablet" and inches is not None:
            attributes["screen_inches"] = inches
        if category == "console":
            platform = _first_match(normalized, {"playstation": r"\b(?:playstation|ps[45])\b", "xbox": r"\bxbox\b", "nintendo_switch": r"\bnintendo\s*switch\b"})
            if platform:
                attributes["platform"] = platform
    elif category == "case":
        form_factor = _first_match(normalized, {"microatx": r"\bmicro\s*atx\b|\bmatx\b", "mini_itx": r"\bmini\s*itx\b", "atx": r"\b(?:e?atx|atx)\b"})
        panel = _first_match(normalized, {"glass": r"\b(?:vidrio|glass|tempered)\b", "mesh": r"\bmalla\b|\bmesh\b"})
        color = _first_match(normalized, {"black": r"\bnegro\b|\bblack\b", "white": r"\bblanco\b|\bwhite\b"})
        if form_factor:
            attributes["form_factor"] = form_factor
        if panel:
            attributes["side_panel"] = panel
        if color:
            attributes["color"] = color
    elif category == "cooling":
        cooling_type = _first_match(normalized, {"liquid": r"\b(?:liquid|liquida|aio|water cooling)\b", "air": r"\b(?:air cooling|por aire|disipador)\b"})
        radiator = re.search(r"\b(\d{2,3})\s*mm\b", normalized)
        socket = _first_match(normalized, {"am4": r"\bam4\b", "am5": r"\bam5\b", "lga1700": r"\blga\s*1700\b", "lga1851": r"\blga\s*1851\b"})
        if cooling_type:
            attributes["cooling_type"] = cooling_type
        if radiator:
            attributes["radiator_mm"] = int(radiator.group(1))
        if socket:
            attributes["socket"] = socket
    return attributes


def build_search_profile(query: str, category: str | None) -> SearchProfile:
    attributes = extract_attributes(query, category)
    requested_capacity = attributes.get("capacity_gb")
    alternatives = capacity_equivalents(int(requested_capacity)) if requested_capacity else frozenset()
    return SearchProfile(category=category, attributes=attributes, capacity_alternatives_gb=alternatives)


def query_variants(query: str, profile: SearchProfile) -> list[str]:
    """Genera búsquedas equivalentes sin ampliar atributos incompatibles."""
    requested = profile.attributes.get("capacity_gb")
    variants = [query]
    # Las capacidades de módulos RAM y SSD comparten grupos comerciales. En
    # móviles, laptops y consolas se mantiene el valor exacto solicitado.
    if requested and profile.category in ("ram", "storage") and len(profile.capacity_alternatives_gb) > 1:
        match = re.search(r"\b\d+(?:[.,]\d+)?\s*(?:gb|tb)\b", query, flags=re.IGNORECASE)
        if match:
            for capacity in sorted(profile.capacity_alternatives_gb):
                candidate = query[:match.start()] + f"{capacity} GB" + query[match.end():]
                if candidate not in variants:
                    variants.append(candidate)
    # Equivalencias de resolución que las tiendas suelen indexar de modo distinto.
    resolution_variants = {
        "hd": ("HD", "720p", "1280x720"),
        "fhd": ("Full HD", "FHD", "1080p", "1920x1080"),
        "qhd": ("QHD", "2K", "1440p", "2560x1440"),
        "uhd_4k": ("4K", "UHD", "2160p", "3840x2160"),
        "5k": ("5K", "5120x2880"),
    }
    resolution = profile.attributes.get("resolution")
    if resolution in resolution_variants:
        expression = RESOLUTION_PATTERNS[str(resolution)]
        for replacement in resolution_variants[str(resolution)]:
            candidate = re.sub(expression, replacement, query, flags=re.IGNORECASE)
            if candidate not in variants:
                variants.append(candidate)
    return variants[:8]


def attributes_match(profile: SearchProfile, text: str) -> bool:
    """Verifica los atributos solicitados contra una oferta del mismo tipo."""
    if not profile.category:
        return True
    offered = extract_attributes(text, profile.category)
    requested = profile.attributes
    if profile.capacity_alternatives_gb:
        offered_capacity = offered.get("capacity_gb")
        if offered_capacity not in profile.capacity_alternatives_gb:
            return False
    for key, requested_value in requested.items():
        if key == "capacity_gb":
            continue
        offered_value = offered.get(key)
        if offered_value is None:
            return False
        if key == "screen_inches":
            if abs(float(offered_value) - float(requested_value)) > 0.5:
                return False
        elif isinstance(requested_value, (int, float, bool)):
            if offered_value != requested_value:
                return False
        elif offered_value != requested_value:
            return False
    return True


def offer_attribute_rows(text: str, category: str | None) -> list[tuple[str, str | None, float | None, str | None]]:
    """Filas normalizadas para producto_tienda_atributo."""
    rows: list[tuple[str, str | None, float | None, str | None]] = []
    for key, value in extract_attributes(text, category).items():
        if isinstance(value, (int, float)):
            unit = ATTRIBUTE_UNITS.get(key)
            rows.append((key, None, float(value), unit))
        else:
            rows.append((key, str(value), None, None))
    return rows
