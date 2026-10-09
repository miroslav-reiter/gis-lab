"""
QGIS 4.2.3 - GIS map catalog SK + CZ + USA + World (XYZ / WMS / WMTS / WFS / REST)
=====================================================

Autor a aktualizácie: Miroslav Reiter
E-mail: riaditel@itacademy.sk
Online kurz: GIS (Geografické Informačné Systémy), QGIS, ArcGIS
Repozitár: https://github.com/miroslav-reiter/gis-lab
Dátum aktualizácie: 2026-10-09

Pôvodná inšpirácia pre import XYZ: Klas Karlsson (GPL-3.0, 2021).

Spustenie v QGIS pre Windows:
Plugins -> Python Console -> Show Editor -> Open Script -> Run Script

Mapove sluzby:
- Svet: OpenStreetMap, Esri, CARTO, Google (legacy XYZ)
- Volitelne s API klucom: Mapy.com, Bing Enterprise, Azure Maps, Stadia, OWM
- Slovensko: ZBGIS, ortofotomapa, kataster, hranice, reliéf (WMS/WMTS)
- USA: USGS The National Map (topografia, ortofoto, relief, vodstvo)
- Slovenske tematicke mapy: historia, geologia, lesy, pody, zivotne prostredie, povodia a Bratislava
- Vektory: WFS UGKK SR (hranice a geograficke nazvy)
- Cesko: CUZK kataster (WMS/WMTS), INSPIRE/RUIAN (WMS/WFS), ortofoto, ZTM, CGS, AOPK

QGIS 4.x nastavenia:
- XYZ: connections/xyz/items/<name>/...
- WMS/WMTS: connections/ows/items/wms/connections/items/<name>/...
- WFS: connections/ows/items/wfs/connections/items/<name>/...
- ArcGIS REST: connections/arcgisfeatureserver/items/<name>/...

Upozornenia:
- Google mt1.google.com: neoficialne/neudrziavane XYZ URL.
- Bing Maps Basic: ukoncene. Bing Enterprise kluc je volitelny.
- Pri verejnom pouziti treba dodrzat licencie, pripisanie autorstva a podmienky
  poskytovatelov, vratane Mapy.com, USGS, Esri, OSM a slovenskeho UGKK.
- API kluce neukladat do verejneho GitHub repozitara.
- Ceska katastralna WMS zobrazuje mapu, vektorove parcely su cez WFS.
- Stahovacie odkazy VFK/SHP nie su automaticky importovane ako vrstvy.
- Pri CZ WFS pouzite priestorovy filter; velke dataset-y mozu mat limity.
- Tento skript registruje pripojenia, nevytvara automaticky vrstvy v projekte.
"""

import json
import urllib.parse
import urllib.request

from qgis.PyQt.QtCore import QSettings
from qgis.core import QgsSettings
from qgis.utils import iface


# =============================================================================
# CONFIGURATION
# =============================================================================

# Google - legacy/undocumented XYZ endpoints.
# They currently work in QGIS but are not the official Google Maps Platform API.
ENABLE_GOOGLE_LEGACY = True

# Mapy.com / Seznam.cz REST API key:
# https://developer.mapy.com/
MAPY_API_KEY = ""

# Optional language for Mapy.com. Useful values: "sk", "cs", "en"
MAPY_LANGUAGE = "sk"

# Bing Maps Enterprise key.
# Basic/free Bing Maps accounts are retired.
# Existing Enterprise customers can use Bing Maps until Microsoft retirement.
BING_MAPS_KEY = ""

# Azure Maps subscription key - recommended Microsoft replacement for Bing Maps.
AZURE_MAPS_KEY = ""

# Stadia Maps API key for Stamen styles.
STADIA_API_KEY = ""

# OpenWeatherMap API key.
OPENWEATHER_API_KEY = ""

# Regionalne mapove sluzby - bez API kluca
ENABLE_SLOVAK_WMS = True
ENABLE_SLOVAK_WMTS = True
ENABLE_USGS_USA = True

# Dalsie slovenske sluzby (registruju sa ako WMS, ArcGIS REST alebo WFS)
ENABLE_SK_HISTORICAL = True
ENABLE_SK_GEOLOGY = True
ENABLE_SK_FORESTRY = True
ENABLE_SK_SOIL = True
ENABLE_SK_ENVIRONMENT = True
ENABLE_SK_ATLAS = True
ENABLE_SK_HYDROLOGY = True
ENABLE_SK_CITY_MAPS = True
ENABLE_SK_WFS = True


# Cesko - CUZK, CGS, AOPK (bez bezneho API kluca)
ENABLE_CZ_CADASTRE = True
ENABLE_CZ_ORTHOPHOTO = True
ENABLE_CZ_TOPOGRAPHY = True
ENABLE_CZ_ADMIN_INSPIRE = True
ENABLE_CZ_WFS = True
ENABLE_CZ_GEOLOGY = True
ENABLE_CZ_NATURE = True
SHOW_CZ_DOWNLOAD_LINKS = True


# =============================================================================
# QGIS XYZ CONNECTION HELPERS
# =============================================================================

def add_xyz(
    name,
    url,
    zmin=0,
    zmax=19,
    authcfg="",
    username="",
    password="",
    tile_pixel_ratio=1.0,
    headers=None,
):
    """Create or overwrite one XYZ connection in the QGIS 4 settings tree."""

    settings = QSettings()
    base = f"connections/xyz/items/{name}"

    settings.setValue(f"{base}/url", url)
    settings.setValue(f"{base}/zmin", int(zmin))
    settings.setValue(f"{base}/zmax", int(zmax))
    settings.setValue(f"{base}/authcfg", authcfg)
    settings.setValue(f"{base}/username", username)
    settings.setValue(f"{base}/password", password)
    settings.setValue(f"{base}/tile-pixel-ratio", float(tile_pixel_ratio))

    if headers:
        settings.setValue(f"{base}/http-header", headers)

    print(f"ADDED: {name}")


def add_sources(sources):
    """Add a list of (name, url, zmin, zmax) XYZ sources."""
    for name, url, zmin, zmax in sources:
        add_xyz(name, url, zmin, zmax)


# =============================================================================
# 1. OPENSTREETMAP
# =============================================================================

OSM_SOURCES = [
    (
        "OpenStreetMap Standard",
        "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
        0,
        19,
    ),
]

add_sources(OSM_SOURCES)


# =============================================================================
# 2. ESRI / ARCGIS ONLINE
# =============================================================================

ESRI_SOURCES = [
    (
        "Esri Satellite",
        "https://server.arcgisonline.com/ArcGIS/rest/services/"
        "World_Imagery/MapServer/tile/{z}/{y}/{x}",
        0,
        19,
    ),
    (
        "Esri Standard",
        "https://server.arcgisonline.com/ArcGIS/rest/services/"
        "World_Street_Map/MapServer/tile/{z}/{y}/{x}",
        0,
        19,
    ),
    (
        "Esri Topo World",
        "https://server.arcgisonline.com/ArcGIS/rest/services/"
        "World_Topo_Map/MapServer/tile/{z}/{y}/{x}",
        0,
        19,
    ),
    (
        "Esri Terrain",
        "https://server.arcgisonline.com/ArcGIS/rest/services/"
        "World_Terrain_Base/MapServer/tile/{z}/{y}/{x}",
        0,
        13,
    ),
    (
        "Esri Ocean",
        "https://services.arcgisonline.com/ArcGIS/rest/services/"
        "Ocean/World_Ocean_Base/MapServer/tile/{z}/{y}/{x}",
        0,
        10,
    ),
    (
        "Esri Gray Light",
        "https://server.arcgisonline.com/ArcGIS/rest/services/"
        "Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}",
        0,
        16,
    ),
    (
        "Esri Gray Dark",
        "https://server.arcgisonline.com/ArcGIS/rest/services/"
        "Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}",
        0,
        16,
    ),
    (
        "Esri Boundaries and Places",
        "https://server.arcgisonline.com/ArcGIS/rest/services/"
        "Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}",
        0,
        20,
    ),
    (
        "Esri Transportation",
        "https://server.arcgisonline.com/ArcGIS/rest/services/"
        "Reference/World_Transportation/MapServer/tile/{z}/{y}/{x}",
        0,
        20,
    ),
]

add_sources(ESRI_SOURCES)


# =============================================================================
# 3. CARTODB / CARTO
# =============================================================================

CARTO_SOURCES = [
    (
        "CartoDB Positron",
        "https://basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png",
        0,
        20,
    ),
    (
        "CartoDB Dark Matter",
        "https://basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png",
        0,
        20,
    ),
]

add_sources(CARTO_SOURCES)


# =============================================================================
# 4. GOOGLE MAPS - LEGACY / UNDOCUMENTED XYZ ENDPOINTS
# =============================================================================

if ENABLE_GOOGLE_LEGACY:
    GOOGLE_SOURCES = [
        (
            "Google Maps",
            "https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}",
            0,
            21,
        ),
        (
            "Google Satellite",
            "https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}",
            0,
            21,
        ),
        (
            "Google Satellite Hybrid",
            "https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}",
            0,
            21,
        ),
        (
            "Google Terrain",
            "https://mt1.google.com/vt/lyrs=t&x={x}&y={y}&z={z}",
            0,
            21,
        ),
        (
            "Google Terrain Hybrid",
            "https://mt1.google.com/vt/lyrs=p&x={x}&y={y}&z={z}",
            0,
            21,
        ),
    ]

    add_sources(GOOGLE_SOURCES)
else:
    print("SKIPPED: Google legacy XYZ sources are disabled.")


# =============================================================================
# 5. MAPY.COM / SEZNAM.CZ
# =============================================================================
#
# Official format:
# https://api.mapy.com/v1/maptiles/{mapset}/256/{z}/{x}/{y}?apikey=...
#
# Available mapsets:
# basic, outdoor, aerial, names-overlay, winter
#
# IMPORTANT:
# Mapy.com requires correct attribution including its logo and copyright.
# The names-overlay layer is transparent and is intended to be placed above
# an aerial layer.
# =============================================================================

if MAPY_API_KEY:
    key = urllib.parse.quote(MAPY_API_KEY, safe="")
    lang = urllib.parse.quote(MAPY_LANGUAGE, safe="")

    MAPY_SOURCES = [
        (
            "Mapy.com Basic",
            f"https://api.mapy.com/v1/maptiles/basic/256/"
            f"{{z}}/{{x}}/{{y}}?apikey={key}&lang={lang}",
            0,
            19,
        ),
        (
            "Mapy.com Outdoor",
            f"https://api.mapy.com/v1/maptiles/outdoor/256/"
            f"{{z}}/{{x}}/{{y}}?apikey={key}&lang={lang}",
            0,
            19,
        ),
        (
            "Mapy.com Aerial",
            f"https://api.mapy.com/v1/maptiles/aerial/256/"
            f"{{z}}/{{x}}/{{y}}?apikey={key}&lang={lang}",
            0,
            19,
        ),
        (
            "Mapy.com Names Overlay",
            f"https://api.mapy.com/v1/maptiles/names-overlay/256/"
            f"{{z}}/{{x}}/{{y}}?apikey={key}&lang={lang}",
            0,
            19,
        ),
        (
            "Mapy.com Winter",
            f"https://api.mapy.com/v1/maptiles/winter/256/"
            f"{{z}}/{{x}}/{{y}}?apikey={key}&lang={lang}",
            0,
            19,
        ),
    ]

    add_sources(MAPY_SOURCES)
else:
    print("SKIPPED: Mapy.com - MAPY_API_KEY is empty.")


# =============================================================================
# 6. BING MAPS - SUPPORTED METHOD VIA IMAGERY METADATA
# =============================================================================
#
# Microsoft states that hard-coded Bing tile URLs must not be used.
# The current tile URL should be obtained from the Bing Imagery Metadata API.
#
# Basic/free Bing Maps accounts are retired. This section is useful only if
# you still have an eligible Bing Maps Enterprise key.
# =============================================================================

def get_bing_xyz_template(imagery_set, bing_key):
    """
    Request the current Bing tile URL and convert its placeholders to QGIS form.

    Bing metadata usually returns placeholders such as:
        {subdomain}
        {quadkey}
        {culture}

    QGIS uses {q} for Bing quadkeys.
    """

    endpoint = (
        "https://dev.virtualearth.net/REST/v1/Imagery/Metadata/"
        f"{imagery_set}"
        "?output=json"
        "&uriScheme=https"
        "&include=ImageryProviders"
        f"&key={urllib.parse.quote(bing_key, safe='')}"
    )

    request = urllib.request.Request(
        endpoint,
        headers={"User-Agent": "QGIS-Basemap-Importer/4.x"},
    )

    with urllib.request.urlopen(request, timeout=15) as response:
        payload = json.loads(response.read().decode("utf-8"))

    resource_sets = payload.get("resourceSets", [])
    if not resource_sets:
        raise RuntimeError("Bing metadata returned no resourceSets.")

    resources = resource_sets[0].get("resources", [])
    if not resources:
        raise RuntimeError("Bing metadata returned no resources.")

    resource = resources[0]
    image_url = resource.get("imageUrl")

    if not image_url:
        raise RuntimeError("Bing metadata returned no imageUrl.")

    subdomains = resource.get("imageUrlSubdomains", [])
    subdomain = subdomains[0] if subdomains else "t0"

    qgis_url = image_url
    qgis_url = qgis_url.replace("{subdomain}", subdomain)
    qgis_url = qgis_url.replace("{quadkey}", "{q}")
    qgis_url = qgis_url.replace("{culture}", "sk-SK")

    zoom_min = int(resource.get("zoomMin", 1))
    zoom_max = int(resource.get("zoomMax", 20))

    return qgis_url, zoom_min, zoom_max


def add_bing_maps(bing_key):
    """Add supported Bing Maps connections using live Bing metadata."""

    bing_sets = [
        ("Bing Aerial", "Aerial"),
        ("Bing Road", "RoadOnDemand"),
        ("Bing Aerial With Labels", "AerialWithLabelsOnDemand"),
        ("Bing Canvas Light", "CanvasLight"),
        ("Bing Canvas Dark", "CanvasDark"),
    ]

    for connection_name, imagery_set in bing_sets:
        try:
            url, zmin, zmax = get_bing_xyz_template(imagery_set, bing_key)
            add_xyz(connection_name, url, zmin, zmax)
        except Exception as exc:
            print(
                f"FAILED: {connection_name} ({imagery_set}) - "
                f"{type(exc).__name__}: {exc}"
            )


if BING_MAPS_KEY:
    add_bing_maps(BING_MAPS_KEY)
else:
    print("SKIPPED: Bing Maps - BING_MAPS_KEY is empty.")


# =============================================================================
# 7. AZURE MAPS - CURRENT MICROSOFT REPLACEMENT FOR BING MAPS
# =============================================================================
#
# Azure Maps raster tiles use standard z/x/y coordinates.
# A subscription key is required.
#
# Microsoft also requires map attribution to be retrieved/displayed according
# to Azure Maps terms. This script only creates XYZ connections.
# =============================================================================

if AZURE_MAPS_KEY:
    azure_key = urllib.parse.quote(AZURE_MAPS_KEY, safe="")

    def azure_tile_url(tileset_id):
        return (
            "https://atlas.microsoft.com/map/tile"
            "?api-version=2024-04-01"
            f"&tilesetId={tileset_id}"
            "&zoom={z}"
            "&x={x}"
            "&y={y}"
            "&tileSize=256"
            f"&subscription-key={azure_key}"
        )

    AZURE_SOURCES = [
        (
            "Azure Maps Road",
            azure_tile_url("microsoft.base.road"),
            0,
            22,
        ),
        (
            "Azure Maps Dark Grey",
            azure_tile_url("microsoft.base.darkgrey"),
            0,
            22,
        ),
        (
            "Azure Maps Imagery",
            azure_tile_url("microsoft.imagery"),
            1,
            19,
        ),
        (
            "Azure Maps Hybrid Road",
            azure_tile_url("microsoft.base.hybrid.road"),
            0,
            22,
        ),
        (
            "Azure Maps Labels Road",
            azure_tile_url("microsoft.base.labels.road"),
            0,
            22,
        ),
    ]

    add_sources(AZURE_SOURCES)
else:
    print("SKIPPED: Azure Maps - AZURE_MAPS_KEY is empty.")


# =============================================================================
# 8. STAMEN STYLES VIA STADIA MAPS
# =============================================================================

if STADIA_API_KEY:
    stadia_key = urllib.parse.quote(STADIA_API_KEY, safe="")

    STADIA_SOURCES = [
        (
            "Stamen Terrain (Stadia)",
            "https://tiles.stadiamaps.com/tiles/stamen_terrain/"
            f"{{z}}/{{x}}/{{y}}.png?api_key={stadia_key}",
            0,
            18,
        ),
        (
            "Stamen Toner (Stadia)",
            "https://tiles.stadiamaps.com/tiles/stamen_toner/"
            f"{{z}}/{{x}}/{{y}}.png?api_key={stadia_key}",
            0,
            20,
        ),
        (
            "Stamen Toner Lite (Stadia)",
            "https://tiles.stadiamaps.com/tiles/stamen_toner_lite/"
            f"{{z}}/{{x}}/{{y}}.png?api_key={stadia_key}",
            0,
            20,
        ),
        (
            "Stamen Watercolor (Stadia)",
            "https://tiles.stadiamaps.com/tiles/stamen_watercolor/"
            f"{{z}}/{{x}}/{{y}}.jpg?api_key={stadia_key}",
            0,
            18,
        ),
    ]

    add_sources(STADIA_SOURCES)
else:
    print("SKIPPED: Stadia/Stamen - STADIA_API_KEY is empty.")


# =============================================================================
# 9. OPENWEATHERMAP
# =============================================================================

if OPENWEATHER_API_KEY:
    weather_key = urllib.parse.quote(OPENWEATHER_API_KEY, safe="")

    WEATHER_SOURCES = [
        (
            "OpenWeatherMap Temperature",
            "https://tile.openweathermap.org/map/temp_new/"
            f"{{z}}/{{x}}/{{y}}.png?appid={weather_key}",
            0,
            19,
        ),
        (
            "OpenWeatherMap Clouds",
            "https://tile.openweathermap.org/map/clouds_new/"
            f"{{z}}/{{x}}/{{y}}.png?appid={weather_key}",
            0,
            19,
        ),
        (
            "OpenWeatherMap Wind",
            "https://tile.openweathermap.org/map/wind_new/"
            f"{{z}}/{{x}}/{{y}}.png?appid={weather_key}",
            0,
            19,
        ),
    ]

    add_sources(WEATHER_SOURCES)
else:
    print("SKIPPED: OpenWeatherMap - OPENWEATHER_API_KEY is empty.")


# =============================================================================
# 10. SLOVENSKO - OFICIALNE WMS / WMTS (UGKK SR, GKÚ)
# =============================================================================
# Overene katalogove odkazy (2026-02):
# https://www.skgeodesy.sk/geoportal/sluzby/mapove-sluzby/
# WMS a WMTS nepatria medzi XYZ Tiles: zobrazia sa v sekcii WMS/WMTS.
# V QGIS je WMS a WMTS ulozene v spolocnom OWS strome so sluzbou 'wms'.
# WMS servery ponukaju viac vrstiev; po pripojeni vyberte konkretnu vrstvu.
# Licencia uvedenych sluzieb: CC BY 4.0 (pozrite aktualne podmienky).
# =============================================================================

def add_wms_wmts(name, url):
    """Zaregistruje WMS/WMTS pripojenie v QGIS 4.x Browser paneli."""
    settings = QgsSettings()
    base = f"connections/ows/items/wms/connections/items/{name}"
    settings.setValue(f"{base}/url", url)
    print(f"ADDED WMS/WMTS: {name}")


if ENABLE_SLOVAK_WMS:
    SLOVAK_WMS_SOURCES = [
        (
            "SK ZBGIS - Základná mapa (WMS)",
            "https://zbgisws.skgeodesy.sk/zbgis_wms_featureinfo/service.svc/get",
        ),
        (
            "SK ZBGIS - Ortofotomozaika SR (WMS)",
            "https://zbgisws.skgeodesy.sk/zbgis_ortofoto_wms/service.svc/get",
        ),
        (
            "SK ZBGIS - Administratívne hranice (WMS)",
            "https://zbgisws.skgeodesy.sk/zbgis_administrativne_hranice_wms_featureinfo/service.svc/get",
        ),
        (
            "SK ZBGIS - Výškopis (WMS)",
            "https://zbgisws.skgeodesy.sk/zbgis_vyskopis_wms_featureinfo/service.svc/get",
        ),
        (
            "SK ZBGIS - Vodstvo (WMS)",
            "https://zbgisws.skgeodesy.sk/zbgis_vodstvo_wms_featureinfo/service.svc/get",
        ),
        (
            "SK ZBGIS - Geografické názvy (WMS)",
            "https://zbgisws.skgeodesy.sk/zbgis_geograficke_nazvoslovie_wms/service.svc/get",
        ),
        (
            "SK ZBGIS - Digitálny model reliéfu DMR 5.0 (WMS)",
            "https://zbgisws.skgeodesy.sk/zbgis_dmr_wms/service.svc/get",
        ),
        (
            "SK ESKN - Katastrálna mapa (WMS)",
            "https://kataster.skgeodesy.sk/eskn/services/NR/kn_wms_norm/MapServer/WmsServer",
        ),
        (
            "SK ESKN - Kataster nad ortofotom (WMS)",
            "https://kataster.skgeodesy.sk/eskn/services/NR/kn_wms_orto/MapServer/WmsServer",
        ),
        (
            "SK ESKN - Mapa určeného operátu (WMS)",
            "https://kataster.skgeodesy.sk/eskn/services/NR/uo_wms_norm/MapServer/WmsServer",
        ),
    ]
    for connection_name, service_url in SLOVAK_WMS_SOURCES:
        add_wms_wmts(connection_name, service_url)
else:
    print("SKIPPED: Slovenske WMS sluzby su vypnute.")


if ENABLE_SLOVAK_WMTS:
    SLOVAK_WMTS_SOURCES = [
        (
            "SK ZBGIS - Základná mapa S-JTSK (WMTS)",
            "https://zbgisws.skgeodesy.sk/zbgis_wmts_sjtsk/service.svc/get?",
        ),
        (
            "SK ZBGIS - Ortofotomozaika S-JTSK (WMTS)",
            "https://zbgisws.skgeodesy.sk/zbgis_ortofoto_wmts_sjtsk/service.svc/get?",
        ),
        (
            "SK ESKN - Kataster Web Mercator (WMTS)",
            "https://kataster.skgeodesy.sk/eskn/rest/services/NR/kn_wmts_norm_wm/MapServer/WMTS",
        ),
        (
            "SK ESKN - Kataster nad ortofotom Web Mercator (WMTS)",
            "https://kataster.skgeodesy.sk/eskn/rest/services/NR/kn_wmts_orto_wm/MapServer/WMTS",
        ),
    ]
    for connection_name, service_url in SLOVAK_WMTS_SOURCES:
        add_wms_wmts(connection_name, service_url)
else:
    print("SKIPPED: Slovenske WMTS sluzby su vypnute.")


# =============================================================================
# 11. USA - USGS THE NATIONAL MAP (XYZ / ARCGIS TILE CACHE)
# =============================================================================
# Zdroj: https://basemap.nationalmap.gov/arcgis/rest/services/
# USA pokrytie sa meni podla produktu. Z je obmedzene na 16 zodpovedajuci
# mierke 1:9028 u mnohych mapovych sluzieb (v rozhrani servera su aj dalsie LOD).
# Ziadny API kluc nie je potrebny pre uvedene verejne USGS sluzby.
# =============================================================================

if ENABLE_USGS_USA:
    USGS_SOURCES = [
        (
            "USA USGS - Topographic Map",
            "https://basemap.nationalmap.gov/arcgis/rest/services/"
            "USGSTopo/MapServer/tile/{z}/{y}/{x}",
            0, 16,
        ),
        (
            "USA USGS - Aerial Imagery",
            "https://basemap.nationalmap.gov/arcgis/rest/services/"
            "USGSImageryOnly/MapServer/tile/{z}/{y}/{x}",
            0, 16,
        ),
        (
            "USA USGS - Aerial Imagery + Topography",
            "https://basemap.nationalmap.gov/arcgis/rest/services/"
            "USGSImageryTopo/MapServer/tile/{z}/{y}/{x}",
            0, 16,
        ),
        (
            "USA USGS - Shaded Relief",
            "https://basemap.nationalmap.gov/arcgis/rest/services/"
            "USGSShadedReliefOnly/MapServer/tile/{z}/{y}/{x}",
            0, 16,
        ),
        (
            "USA USGS - Hydrography",
            "https://basemap.nationalmap.gov/arcgis/rest/services/"
            "USGSHydroCached/MapServer/tile/{z}/{y}/{x}",
            0, 16,
        ),
    ]
    add_sources(USGS_SOURCES)
else:
    print("SKIPPED: USGS USA mapove zdroje su vypnute.")



# =============================================================================
# 12. SLOVENSKO - HISTORICKE A KARTOGRAFICKE MAPY (GKU)
# =============================================================================
# Oficalny zoznam GKÚ (aktualizovany 2026-07-23):
# https://www.gku.sk/gku/produkty-sluzby/zbgis/wms.html
# Služby su WMS - nemusia obsahovat vektorove atributy.
# =============================================================================

if ENABLE_SK_HISTORICAL:
    SK_HISTORICAL_WMS = [
        ("SK GKU - Historická mapa III. vojenského mapovania (WMS)",
         "https://zbgisws.skgeodesy.sk/hm_III_vm/service.svc/get"),
        ("SK GKU - Základné mapy SR raster (WMS)",
         "https://zbgisws.skgeodesy.sk/zmsr_wms/service.svc/get"),
        ("SK GKU - Topografické mapy RETM raster (WMS)",
         "https://zbgisws.skgeodesy.sk/retm_wms/service.svc/get"),
        ("SK GKU - Klady mapových listov (WMS)",
         "https://zbgisws.skgeodesy.sk/klady_mapovych_listov_wms/service.svc/get"),
        ("SK GKU - Administratívna mapa SR raster (WMS)",
         "https://zbgisws.skgeodesy.sk/amsr_wms/service.svc/get"),
    ]
    for connection_name, service_url in SK_HISTORICAL_WMS:
        add_wms_wmts(connection_name, service_url)
else:
    print("SKIPPED: SK historical/topographic maps are disabled.")


# =============================================================================
# 13. SLOVENSKO - ARCGIS REST MAP SERVER
# =============================================================================
# ArcGIS MapServer + FeatureServer use the same QGIS settings list
# 'arcgisfeatureserver' in QGIS 4.2 (QgsArcGisConnectionSettings).
# The corresponding connection is visible in ArcGIS Map Server in Browser.
# This script registers service URLs; it does not load all layers at once.
# References:
# https://api.qgis.org/api/4.2/qgsowsconnection_8h_source.html
# =============================================================================

def add_arcgis_mapserver(name, url):
    """Register one ArcGIS REST service in the QGIS 4.x Browser panel."""
    url = url.rstrip("/")
    if not url.startswith("https://") or not url.endswith("/MapServer"):
        raise ValueError(f"ArcGIS MapServer URL invalid: {url}")
    settings = QgsSettings()
    base = f"connections/arcgisfeatureserver/items/{name}"
    settings.setValue(f"{base}/url", url)
    print(f"ADDED ArcGIS REST: {name}")


def add_arcgis_sources(sources):
    for name, url in sources:
        add_arcgis_mapserver(name, url)


# =============================================================================
# 14. GEOLOGIA (SGUDS)
# https://ags.geology.sk/arcgis/rest/services/
# =============================================================================

if ENABLE_SK_GEOLOGY:
    SK_GEOLOGY_REST = [
        ("SK Geológia - Geologická mapa SR 1-50 000",
         "https://ags.geology.sk/arcgis/rest/services/GeologickeMapy/GeologickaMapaSR50_2/MapServer"),
        ("SK Geológia - Geologická mapa SR 1-200 000",
         "https://ags.geology.sk/arcgis/rest/services/WebServices/GM200/MapServer"),
        ("SK Geológia - Radónové riziko",
         "https://ags.geology.sk/arcgis/rest/services/WebServices/RADON/MapServer"),
    ]
    add_arcgis_sources(SK_GEOLOGY_REST)
else:
    print("SKIPPED: SK geology maps are disabled.")


# =============================================================================
# 15. LESNICTVO (NLC ZVOLEN)
# https://gis.nlcsk.org/arcgis/rest/services/Inspire
# =============================================================================

if ENABLE_SK_FORESTRY:
    SK_FORESTRY_REST = [
        ("SK Lesy - Hranice lesných porastov (JPRL)",
         "https://gis.nlcsk.org/arcgis/rest/services/Inspire/JPRL/MapServer"),
        ("SK Lesy - Druhové zloženie lesa",
         "https://gis.nlcsk.org/arcgis/rest/services/Inspire/DrevinoveZlozenie/MapServer"),
        ("SK Lesy - Lesné cesty a komunikácie",
         "https://gis.nlcsk.org/arcgis/rest/services/Inspire/LesneCesty/MapServer"),
        ("SK Lesy - Lesné pôdne jednotky",
         "https://gis.nlcsk.org/arcgis/rest/services/Inspire/PodneTypy/MapServer"),
    ]
    add_arcgis_sources(SK_FORESTRY_REST)
else:
    print("SKIPPED: SK forestry maps are disabled.")


# =============================================================================
# 16. PODA - NPPC VUPOP
# https://portal.vupop.sk/arcgis/rest/services/BPEJ/
# =============================================================================

if ENABLE_SK_SOIL:
    SK_SOIL_REST = [
        ("SK Pôda - Bonitované pôdno-ekologické jednotky BPEJ",
         "https://portal.vupop.sk/arcgis/rest/services/BPEJ/BPEJ_ZBGIS/MapServer"),
    ]
    add_arcgis_sources(SK_SOIL_REST)
else:
    print("SKIPPED: SK soil maps are disabled.")


# =============================================================================
# 17. ZIVOTNE PROSTREDIE (SAZP)
# https://arc.sazp.sk/arcgis/rest/services/
# NOTE: Environmental burden layers may have special use restrictions.
# =============================================================================

if ENABLE_SK_ENVIRONMENT:
    SK_ENVIRONMENT_REST = [
        ("SK Životné prostredie - Environmentálne záťaže",
         "https://arc.sazp.sk/arcgis/rest/services/env_zataze/environmentalna_zataz/MapServer"),
        ("SK Životné prostredie - Biocentrá a biokoridory RÚSES",
         "https://arc.sazp.sk/arcgis/rest/services/uses/ruses/MapServer"),
    ]
    add_arcgis_sources(SK_ENVIRONMENT_REST)
else:
    print("SKIPPED: SK environment maps are disabled.")

if ENABLE_SK_ATLAS:
    SK_ATLAS_REST = [
        ("SK Atlas krajiny - Rastrové podklady",
         "https://arc.sazp.sk/arcgis/rest/services/atlassr/atlas_podklad_raster/MapServer"),
        ("SK Atlas krajiny - Vektorové mapové podklady",
         "https://arc.sazp.sk/arcgis/rest/services/atlassr/atlas_podklad_vektor/MapServer"),
        ("SK Atlas krajiny - Tematické mapy prírody",
         "https://arc.sazp.sk/arcgis/rest/services/atlassr/atlassr_08/MapServer"),
    ]
    add_arcgis_sources(SK_ATLAS_REST)
else:
    print("SKIPPED: SK Atlas krajiny maps are disabled.")


# =============================================================================
# 18. VODSTVO A POVODIA (SHMU)
# https://arcgis.shmu.sk/arcgis/rest/services/public/
# =============================================================================

if ENABLE_SK_HYDROLOGY:
    SK_HYDROLOGY_REST = [
        ("SK SHMÚ - Podrobné povodia 1-50 000",
         "https://arcgis.shmu.sk/arcgis/rest/services/public/PodrobnePovodia50/MapServer"),
        ("SK SHMÚ - Hlavné povodia 1-50 000",
         "https://arcgis.shmu.sk/arcgis/rest/services/public/HlavnePovodia50/MapServer"),
    ]
    add_arcgis_sources(SK_HYDROLOGY_REST)
else:
    print("SKIPPED: SK hydrology maps are disabled.")


# =============================================================================
# 19. BRATISLAVA - UZEMNY PLAN A DOPRAVA
# https://geoportal.bratislava.sk/hSite/rest/services/
# UPN: vzdy skontrolujte aktualne schvalene znenie a zmeny a doplnky.
# Cyklotrasy_v_Bratislave zahrna historicku vrstvu do roku 2018,
# preto tu prednostne pouzivame samostatnu sluzbu Cyklotrasy.
# =============================================================================

if ENABLE_SK_CITY_MAPS:
    SK_CITY_REST = [
        ("SK Bratislava - Územný plán - Funkčné využitie",
         "https://geoportal.bratislava.sk/hSite/rest/services/up/"
         "2_1_Priestorov%C3%A9_usporiadanie_a_funk%C4%8Dn%C3%A9_vyu%C5%BEitie_"
         "%C3%BAzemia__komplexn%C3%A9_rie%C5%A1enie/MapServer"),
        ("SK Bratislava - Funkčné plochy",
         "https://geoportal.bratislava.sk/hSite/rest/services/up/funkcne_plochy_pop_up_sde/MapServer"),
        ("SK Bratislava - Cyklotrasy",
         "https://geoportal.bratislava.sk/hSite/rest/services/doprava/Cyklotrasy/MapServer"),
        ("SK Bratislava - Linky MHD",
         "https://geoportal.bratislava.sk/hSite/rest/services/doprava/Linky_MHD/MapServer"),
    ]
    add_arcgis_sources(SK_CITY_REST)
else:
    print("SKIPPED: SK city maps are disabled.")


# =============================================================================
# 20. WFS - UGKK SR (VEKTOROVE OBJEKTY)
# https://www.gku.sk/gku/produkty-sluzby/zbgis/wms.html
# QGIS Browser -> WFS / OGC API Features -> select an individual feature type.
# WFS can be slow for large geographic extents, use spatial filters.
# =============================================================================

def add_wfs(name, url):
    """Register an OGC WFS connection in QGIS 4.x."""
    settings = QgsSettings()
    base = f"connections/ows/items/wfs/connections/items/{name}"
    settings.setValue(f"{base}/url", url)
    settings.setValue(f"{base}/version", "auto")
    print(f"ADDED WFS: {name}")


if ENABLE_SK_WFS:
    SK_WFS_SOURCES = [
        ("SK WFS - Administratívne hranice (ÚGKK)",
         "https://zbgisws.skgeodesy.sk/zbgis_administrativne_hranice_wfs/service.svc/get"),
        ("SK WFS - Geografické názvoslovie (ÚGKK)",
         "https://zbgisws.skgeodesy.sk/zbgis_geograficke_nazvoslovie_wfs/service.svc/get"),
    ]
    for connection_name, service_url in SK_WFS_SOURCES:
        add_wfs(connection_name, service_url)
else:
    print("SKIPPED: SK WFS connections are disabled.")

# =============================================================================
# 21. CESKO - CUZK KATASTER NEMOVITOSTI (WMS/WMTS)
# =============================================================================
# Official service catalogue (checked 2026-10-09):
# https://wms.cuzk.gov.cz/
# This adds view services, NOT a local copy of cadastral records.
# The WMS cadastral map also contains selectable layers about ownership type,
# mismatches, etc. Actual cadastral parcel geometry: see WFS below.
# WMTS JTSK: EPSG:5514; WMTS Google: EPSG:3857.
# =============================================================================

if ENABLE_CZ_CADASTRE:
    CZ_CADASTRE_WMS_WMTS = [
        ("CZ Katastr - Katastralni mapa (WMS)",
         "https://services.cuzk.gov.cz/wms/local-km-wms.asp"),
        ("CZ Katastr - Katastralni mapa JTSK (WMTS)",
         "https://services.cuzk.gov.cz/wmts/local-km-wmts-jtsk.asp"),
        ("CZ Katastr - Katastralni mapa Web Mercator (WMTS)",
         "https://services.cuzk.gov.cz/wmts/local-km-wmts-google.asp"),
        ("CZ Katastr - Parcely INSPIRE CP (WMS)",
         "https://services.cuzk.gov.cz/wms/inspire-cp-wms.asp"),
    ]
    for n, u in CZ_CADASTRE_WMS_WMTS:
        add_wms_wmts(n, u)
else:
    print("SKIPPED: CZ cadastre WMS/WMTS are disabled.")


# =============================================================================
# 22. CESKO - CUZK ORTOFOTO A ARCHIV (WMS/WMTS)
# =============================================================================
# Official metadata:
# https://geoportal.gov.cz/php/micka/record/basic/CZ-CUZK-WMTS-ORTOFOTO-P
# https://geoportal.gov.cz/php/micka/record/basic/CZ-CUZK-WMS-ORTOARCHIV
# https://geoportal.gov.cz/php/micka/record/basic/CZ-CUZK-WMS-ORTOCIR
# WMS archived ortho contains separate annual layers.
# =============================================================================

if ENABLE_CZ_ORTHOPHOTO:
    CZ_ORTHO = [
        ("CZ Ortofoto - Aktualni (WMS)",
         "https://ags.cuzk.gov.cz/arcgis1/services/ORTOFOTO/MapServer/WMSServer"),
        ("CZ Ortofoto - Aktualni (WMTS)",
         "https://ags.cuzk.gov.cz/arcgis1/rest/services/ORTOFOTO/MapServer/WMTS?service=WMTS&request=GetCapabilities"),
        ("CZ Ortofoto - Archivni po rocich (WMS)",
         "https://geoportal.cuzk.gov.cz/WMS_ORTOFOTO_ARCHIV/WMService.aspx"),
        ("CZ Ortofoto - CIR infracervene (WMS)",
         "https://geoportal.cuzk.gov.cz/WMS_ORTOFOTO_CIR/WMService.aspx"),
    ]
    for n, u in CZ_ORTHO:
        add_wms_wmts(n, u)
else:
    print("SKIPPED: CZ orthophoto are disabled.")


# =============================================================================
# 23. CESKO - CUZK TOPOGRAFICKE MAPY (WMTS / WMS / ArcGIS REST)
# =============================================================================
# https://geoportal.gov.cz/php/micka/record/basic/CZ-CUZK-WMTS-ZTM
# https://geoportal.gov.cz/php/micka/record/basic/CZ-CUZK-WMTS-PM
# https://geoportal.gov.cz/php/micka/record/basic/CZ-CUZK-WMS-DATA50-P
# ZTM means Zakladni topograficke mapy CR; Data50 is a WMS rendering,
# not a downloadable vector layer.
# =============================================================================

if ENABLE_CZ_TOPOGRAPHY:
    CZ_TOPO_WMTS_WMS = [
        ("CZ Topo - Zakladni topograficke mapy ZTM (WMTS)",
         "https://ags.cuzk.gov.cz/arcgis1/rest/services/ZTM/MapServer/WMTS?service=WMTS&request=GetCapabilities"),
        ("CZ Topo - Prehledova mapa (WMTS)",
         "https://ags.cuzk.gov.cz/arcgis1/rest/services/PrehledovaMapa/MapServer/WMTS/1.0.0/WMTSCapabilities.xml"),
        ("CZ Topo - ZTM 1-5000 (WMTS)",
         "https://ags.cuzk.gov.cz/arcgis1/rest/services/ZTM/ZTM5/MapServer/WMTS/1.0.0/WMTSCapabilities.xml"),
        ("CZ Topo - ZTM 1-10000 (WMTS)",
         "https://ags.cuzk.gov.cz/arcgis1/rest/services/ZTM/ZTM10/MapServer/WMTS/1.0.0/WMTSCapabilities.xml"),
        ("CZ Topo - ZTM 1-25000 (WMTS)",
         "https://ags.cuzk.gov.cz/arcgis1/rest/services/ZTM/ZTM25/MapServer/WMTS/1.0.0/WMTSCapabilities.xml"),
        ("CZ Topo - ZTM 1-50000 (WMTS)",
         "https://ags.cuzk.gov.cz/arcgis1/rest/services/ZTM/ZTM50/MapServer/WMTS/1.0.0/WMTSCapabilities.xml"),
        ("CZ Topo - ZTM 1-100000 (WMTS)",
         "https://ags.cuzk.gov.cz/arcgis1/rest/services/ZTM/ZTM100/MapServer/WMTS/1.0.0/WMTSCapabilities.xml"),
        ("CZ Topo - Data50 (WMS)",
         "https://ags.cuzk.gov.cz/arcgis/services/DATA50/MapServer/WmsServer"),
    ]
    for n, u in CZ_TOPO_WMTS_WMS:
        add_wms_wmts(n, u)
    CZ_TOPO_REST = [
        ("CZ Topo - ZTM ArcGIS REST",
         "https://ags.cuzk.gov.cz/arcgis1/rest/services/ZTM/MapServer"),
        ("CZ Topo - Prehledova mapa ArcGIS REST",
         "https://ags.cuzk.gov.cz/arcgis1/rest/services/PrehledovaMapa/MapServer"),
    ]
    add_arcgis_sources(CZ_TOPO_REST)
else:
    print("SKIPPED: CZ topographic maps are disabled.")


# =============================================================================
# 24. CESKO - CUZK SPRAVNE JEDNOTKY, RUIAN, INSPIRE (WMS)
# =============================================================================
# https://wms.cuzk.gov.cz/
# RUIAN records and INSPIRE features are not identical. RUIAN SHP downloads
# are shown below, WMS is view-only.
# =============================================================================

if ENABLE_CZ_ADMIN_INSPIRE:
    CZ_ADMIN_WMS = [
        ("CZ CUZK - Spravni jednotky (WMS)",
         "https://services.cuzk.gov.cz/wms/local-ux-wms.asp"),
        ("CZ CUZK - Stav digitalizace katastru (WMS)",
         "https://services.cuzk.gov.cz/wms/local-dg-wms.asp"),
        ("CZ RUIAN - Ucelove uzemni prvky (WMS)",
         "https://services.cuzk.gov.cz/wms/local-uup-wms.asp"),
        ("CZ INSPIRE - Adresy (WMS)",
         "https://services.cuzk.gov.cz/wms/inspire-ad-wms.asp"),
        ("CZ INSPIRE - Spravni jednotky (WMS)",
         "https://services.cuzk.gov.cz/wms/inspire-au-wms.asp"),
        ("CZ INSPIRE - Budovy (WMS)",
         "https://services.cuzk.gov.cz/wms/inspire-bu-wms.asp"),
    ]
    for n, u in CZ_ADMIN_WMS:
        add_wms_wmts(n, u)
else:
    print("SKIPPED: CZ admin/INSPIRE WMS are disabled.")


# =============================================================================
# 25. CESKO - CUZK KATASTRALNE VEKTORY, INSPIRE A RUIAN (WFS)
# =============================================================================
# https://wms.cuzk.gov.cz/
# WFS downloads spatial features, not ownership/legal deeds.
# CP  = INSPIRE cadastral parcels
# CPX = national extended cadastral map geometry (more detailed drawing)
# AD  = INSPIRE addresses; AU = admin units; BU = buildings
# ZPMZ = polygons and reference points for detailed change surveys
# WARNING: Query small areas; servers can impose feature/response limits.
# =============================================================================

if ENABLE_CZ_WFS:
    CZ_WFS_SOURCES = [
        ("CZ WFS - Katastralni parcely INSPIRE CP",
         "https://services.cuzk.gov.cz/wfs/inspire-cp-wfs.asp"),
        ("CZ WFS - Katastralni mapa rozsirena CPX",
         "https://services.cuzk.gov.cz/wfs/inspire-cpx-wfs.asp"),
        ("CZ WFS - Budovy INSPIRE BU",
         "https://services.cuzk.gov.cz/wfs/inspire-bu-wfs.asp"),
        ("CZ WFS - Adresy INSPIRE AD",
         "https://services.cuzk.gov.cz/wfs/inspire-ad-wfs.asp"),
        ("CZ WFS - Spravni jednotky INSPIRE AU",
         "https://services.cuzk.gov.cz/wfs/inspire-au-wfs.asp"),
        ("CZ WFS - Zaznamy podrobneho mereni zmen ZPMZ",
         "https://services.cuzk.gov.cz/wfs/local-zpmz-wfs.asp"),
    ]
    for n, u in CZ_WFS_SOURCES:
        add_wfs(n, u)
else:
    print("SKIPPED: CZ cadastral/INSPIRE WFS are disabled.")


# =============================================================================
# 26. CESKO - GEOLOGIE, HISTORICKE GEOLOGICKE MAPY, PUDY (CGS)
# =============================================================================
# Official catalog:
# https://cgs.gov.cz/mapy-a-data/data
# https://cgs.gov.cz/mapy-a-data/webove-sluzby
# =============================================================================

if ENABLE_CZ_GEOLOGY:
    CZ_GEOLOGY_REST = [
        ("CZ CGS - Geologicka mapa 1-25000 zakryta",
         "https://mapy.geology.cz/arcgis/rest/services/Geologie/geologicka_mapa25_zakryta/MapServer"),
        ("CZ CGS - Geologicka mapa 1-25000 odkryta",
         "https://mapy.geology.cz/arcgis/rest/services/Geologie/geologicka_mapa25_odkryta/MapServer"),
        ("CZ CGS - Geologicka mapa 1-50000",
         "https://mapy.geology.cz/arcgis/rest/services/Geologie/geologicka_mapa50/MapServer"),
        ("CZ CGS - Geologicka mapa 1-500000",
         "https://mapy.geology.cz/arcgis/rest/services/Geologie/geologicka_mapa500_CR/MapServer"),
        ("CZ CGS - Historicke geologicke mapy 1-144000",
         "https://mapy.geology.cz/arcgis/rest/services/Geologie/stare_mapy_144000/MapServer"),
        ("CZ CGS - Historicke geologicke mapy 1-28800",
         "https://mapy.geology.cz/arcgis/rest/services/Geologie/stare_mapy_28800/MapServer"),
        ("CZ CGS - Pudy - pudni typy 1-50000",
         "https://mapy.geology.cz/arcgis/rest/services/Pudy/pudni_typy50/MapServer"),
        ("CZ CGS - Hydrogeologicka mapa 1-50000",
         "https://mapy.geology.cz/arcgis/rest/services/HydroGeologie/HG50_mapa/MapServer"),
        ("CZ CGS - Sesuvy Geofond",
         "https://mapy.geology.cz/arcgis/rest/services/Geohazardy/sesuvy_Geofond/MapServer"),
        ("CZ CGS - Vrtna prozkoumanost",
         "https://mapy.geology.cz/arcgis/rest/services/Prozkoumanost/Vrtna_prozkoumanost/MapServer"),
        ("CZ CGS - Nerostne suroviny SurIS",
         "https://mapy.geology.cz/arcgis/rest/services/Suroviny/Surovinovy_informacni_system/MapServer"),
    ]
    add_arcgis_sources(CZ_GEOLOGY_REST)
else:
    print("SKIPPED: CZ geology maps are disabled.")


# =============================================================================
# 27. CESKO - OCHRANA PRIRODY (AOPK CR)
# =============================================================================
# Official open data / WMS / WFS:
# https://data.nature.cz/ds/3
# https://gis.nature.cz/arcgis/rest/services/Aplikace/Opendata/MapServer
# Source attribution: (c) AOPK CR; CC BY 4.0.
# =============================================================================

if ENABLE_CZ_NATURE:
    add_arcgis_sources([
        ("CZ AOPK - Chranena uzemi a opendata (ArcGIS REST)",
         "https://gis.nature.cz/arcgis/rest/services/Aplikace/Opendata/MapServer"),
        ("CZ AOPK - Uzemi ochrany prirody",
         "https://gis.nature.cz/arcgis/rest/services/UzemniOchrana/ChranUzemi/MapServer"),
    ])
    add_wms_wmts(
        "CZ AOPK - Chranena uzemi, pametne stromy (WMS)",
        "https://gis.nature.cz/arcgis/services/Aplikace/Opendata/MapServer/WMSServer",
    )
    add_wfs(
        "CZ AOPK - Chranena uzemi, opendata (WFS)",
        "https://gis.nature.cz/arcgis/services/Aplikace/Opendata/MapServer/WFSServer",
    )
else:
    print("SKIPPED: CZ nature maps are disabled.")


# =============================================================================
# 28. CESKO - ACTUAL DATA DOWNLOAD LINKS (VFK / SHP)
# =============================================================================
# NOTE: these are download directories, NOT WMS/WFS/XYZ live layers.
# WFS above registers available feature services inside the QGIS Browser.
# Use the official CUZK data downloads to obtain bulk datasets.
# =============================================================================

CZ_DOWNLOAD_LINKS = {
    "CZ Katastr - VFK/ISKN state (monthly)":
        "https://services.cuzk.gov.cz/vfk/stavy/aktualni/",
    "CZ Katastr - VFK/ISKN changes (monthly)":
        "https://services.cuzk.gov.cz/vfk/zmeny/aktualni/",
    "CZ Katastr - parcel geometry SHP by cadastral unit":
        "https://services.cuzk.gov.cz/shp/ku/",
    "CZ RUIAN - SHP by municipality":
        "https://services.cuzk.gov.cz/shp/obec/",
    "CZ RUIAN - SHP country/region/district/municipality":
        "https://services.cuzk.gov.cz/shp/stat/",
}

if SHOW_CZ_DOWNLOAD_LINKS:
    print("\nCZ OFFICIAL FILE DOWNLOADS (not registered as QGIS layers):")
    for label, download_url in CZ_DOWNLOAD_LINKS.items():
        print(f"  {label}: {download_url}")


# =============================================================================
# FINISH
# =============================================================================

QSettings().sync()
QgsSettings().sync()
iface.reloadConnections()

print("")
print("==============================================================")
print("QGIS XYZ / WMS / WMTS / ARCGIS REST / WFS IMPORT FINISHED")
print("==============================================================")
print("If the Browser panel does not refresh immediately:")
print("  Browser -> XYZ Tiles -> Refresh")
print("  Browser -> WMS/WMTS -> Refresh (Slovakia)")
print("  Browser -> ArcGIS Map Server -> Refresh (Slovak thematic maps)")
print("  Browser -> WFS / OGC API Features -> Refresh (SK and CZ vectors)\n  Browser -> WMS/WMTS -> Refresh (Czech cadastre and maps)\n  Browser -> ArcGIS Map Server -> Refresh (CZ topography / CGS / AOPK)")
print("")
print("For Mapy.com, Bing, Azure Maps, Stadia and OpenWeatherMap")
print("fill in the corresponding API key at the top of this script.")
print("==============================================================")
