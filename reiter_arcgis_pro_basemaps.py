#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
GIS-LAB: ArcGIS Pro map catalog / optional map layer importer

Author: Miroslav Reiter
Email: riaditel@itacademy.sk
Course: GIS (Geografické Informačné Systémy), QGIS, ArcGIS
Repository: https://github.com/miroslav-reiter/gis-lab
Updated: 2026-10-12

Adapted from the user-supplied QGIS 4.2.3 catalog, originally inspired by
Klas Karlsson's QGIS basemap script (2021; GPL-3.0). Derivative: GPL-3.0.

IMPORTANT DIFFERENCE FROM QGIS:
- ArcGIS Pro does not expose a QGIS-like XYZ/WMS/WMTS/WFS registry in QSettings.
- ArcPy can add supported XYZ, WMS and ArcGIS REST layers to an .aprx map.
- WMTS and WFS must be connected in the ArcGIS Pro Catalog user interface.
- ArcGIS REST site connections (.ags) can optionally be created by ArcPy.
- Exported CSV/JSON files are catalogs, NOT native ArcGIS server connections.
- The URLs are copied from the source file; availability has NOT been tested
  for every service and may change. Connection failures are logged.
- Never publish real API keys, CSV logs with keys, or credential files.

RUN INSIDE ARCGIS PRO (recommended):
1. Save or create an ArcGIS Pro project.
2. View -> Python Window (or Analysis -> Python -> Python Window).
3. Run: exec(compile(open(r"C:\PATH\reiter_arcgis_pro_basemaps.py", encoding="utf-8").read(),
                  r"C:\PATH\reiter_arcgis_pro_basemaps.py", "exec"))
4. A project folder GIS-LAB-ArcGIS-Catalog is created with CSV/JSON, README
   and a separate log. Selected sample layers are added if enabled.
5. Save the ArcGIS Pro project if AUTO_SAVE_PROJECT is disabled.

ArcGIS Pro documentation:
https://doc.esri.com/en/arcgis-pro/latest/arcpy/mapping/map-class.html
https://doc.esri.com/en/arcgis-pro/latest/help/data/services/add-wmts-services.html
https://doc.esri.com/en/arcgis-pro/latest/help/data/services/add-wfs-services.html
"""

import csv
import json
import os
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen

# ---------------------------------------------------------------------------
# CONFIGURATION - change these options before running the script.
# ---------------------------------------------------------------------------
# Create a catalog (CSV/JSON) containing ALL public services.
EXPORT_CATALOG = True

# Add only named sample layers to a dedicated ArcGIS Pro 2D map.
# Set to False to create only the catalog without altering map contents.
AUTO_ADD_SELECTED_LAYERS = True
MAP_NAME = "GIS-LAB - Basemap Samples"
SELECTED_LAYER_NAMES = [
    "OpenStreetMap Standard",
    "Esri Satellite",
    "USA USGS - Topographic Map",
]

# If True, create additional .ags ArcGIS Server SITE connections in the
# catalog folder. One .ags per server root. Network access may be slow.
CREATE_AGS_SITE_CONNECTIONS = False

# Link the output directory under Project -> Folders in the Catalog pane.
ADD_CATALOG_FOLDER_TO_PROJECT = True
AUTO_SAVE_PROJECT = False  # Safer: save with Ctrl+S once you verify results.

# These are retrieved from environment variables. Do NOT paste credentials
# into this file if you publish it on GitHub. Values are never exported.
API_KEYS = {
    name: os.environ.get(name, "").strip()
    for name in (
        "MAPY_API_KEY", "BING_MAPS_KEY", "AZURE_MAPS_KEY",
        "STADIA_API_KEY", "OPENWEATHER_API_KEY",
    )
}

# Google mt1.google.com XYZ endpoints are undocumented (legacy) and may
# violate provider terms in some uses. Listed for reference, but not loaded
# unless the user explicitly selects them below.
ENABLE_LEGACY_GOOGLE_LOADING = False

# Override output folder if needed, e.g. r"D:\GIS-LAB\ArcGIS-Catalog".
OUTPUT_DIRECTORY = ""

# ---------------------------------------------------------------------------
# MAP SOURCE CATALOG EXTRACTED FROM THE PROVIDED QGIS SCRIPT
# ---------------------------------------------------------------------------
BASE_SERVICES = [
  {
    "name": "OpenStreetMap Standard",
    "kind": "XYZ",
    "url": "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
    "region": "WORLD",
    "auth": ""
  },
  {
    "name": "Esri Satellite",
    "kind": "XYZ",
    "url": "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    "region": "WORLD",
    "auth": ""
  },
  {
    "name": "Esri Standard",
    "kind": "XYZ",
    "url": "https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}",
    "region": "WORLD",
    "auth": ""
  },
  {
    "name": "Esri Topo World",
    "kind": "XYZ",
    "url": "https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}",
    "region": "WORLD",
    "auth": ""
  },
  {
    "name": "Esri Terrain",
    "kind": "XYZ",
    "url": "https://server.arcgisonline.com/ArcGIS/rest/services/World_Terrain_Base/MapServer/tile/{z}/{y}/{x}",
    "region": "WORLD",
    "auth": ""
  },
  {
    "name": "Esri Ocean",
    "kind": "XYZ",
    "url": "https://services.arcgisonline.com/ArcGIS/rest/services/Ocean/World_Ocean_Base/MapServer/tile/{z}/{y}/{x}",
    "region": "WORLD",
    "auth": ""
  },
  {
    "name": "Esri Gray Light",
    "kind": "XYZ",
    "url": "https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}",
    "region": "WORLD",
    "auth": ""
  },
  {
    "name": "Esri Gray Dark",
    "kind": "XYZ",
    "url": "https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}",
    "region": "WORLD",
    "auth": ""
  },
  {
    "name": "Esri Boundaries and Places",
    "kind": "XYZ",
    "url": "https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}",
    "region": "WORLD",
    "auth": ""
  },
  {
    "name": "Esri Transportation",
    "kind": "XYZ",
    "url": "https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Transportation/MapServer/tile/{z}/{y}/{x}",
    "region": "WORLD",
    "auth": ""
  },
  {
    "name": "CartoDB Positron",
    "kind": "XYZ",
    "url": "https://basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png",
    "region": "WORLD",
    "auth": ""
  },
  {
    "name": "CartoDB Dark Matter",
    "kind": "XYZ",
    "url": "https://basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png",
    "region": "WORLD",
    "auth": ""
  },
  {
    "name": "Google Maps",
    "kind": "XYZ",
    "url": "https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}",
    "region": "WORLD",
    "auth": ""
  },
  {
    "name": "Google Satellite",
    "kind": "XYZ",
    "url": "https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}",
    "region": "WORLD",
    "auth": ""
  },
  {
    "name": "Google Satellite Hybrid",
    "kind": "XYZ",
    "url": "https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}",
    "region": "WORLD",
    "auth": ""
  },
  {
    "name": "Google Terrain",
    "kind": "XYZ",
    "url": "https://mt1.google.com/vt/lyrs=t&x={x}&y={y}&z={z}",
    "region": "WORLD",
    "auth": ""
  },
  {
    "name": "Google Terrain Hybrid",
    "kind": "XYZ",
    "url": "https://mt1.google.com/vt/lyrs=p&x={x}&y={y}&z={z}",
    "region": "WORLD",
    "auth": ""
  },
  {
    "name": "USA USGS - Topographic Map",
    "kind": "XYZ",
    "url": "https://basemap.nationalmap.gov/arcgis/rest/services/USGSTopo/MapServer/tile/{z}/{y}/{x}",
    "region": "USA",
    "auth": ""
  },
  {
    "name": "USA USGS - Aerial Imagery",
    "kind": "XYZ",
    "url": "https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/tile/{z}/{y}/{x}",
    "region": "USA",
    "auth": ""
  },
  {
    "name": "USA USGS - Aerial Imagery + Topography",
    "kind": "XYZ",
    "url": "https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryTopo/MapServer/tile/{z}/{y}/{x}",
    "region": "USA",
    "auth": ""
  },
  {
    "name": "USA USGS - Shaded Relief",
    "kind": "XYZ",
    "url": "https://basemap.nationalmap.gov/arcgis/rest/services/USGSShadedReliefOnly/MapServer/tile/{z}/{y}/{x}",
    "region": "USA",
    "auth": ""
  },
  {
    "name": "USA USGS - Hydrography",
    "kind": "XYZ",
    "url": "https://basemap.nationalmap.gov/arcgis/rest/services/USGSHydroCached/MapServer/tile/{z}/{y}/{x}",
    "region": "USA",
    "auth": ""
  },
  {
    "name": "SK ZBGIS - Z\u00e1kladn\u00e1 mapa (WMS)",
    "kind": "WMS",
    "url": "https://zbgisws.skgeodesy.sk/zbgis_wms_featureinfo/service.svc/get",
    "region": "SK",
    "auth": ""
  },
  {
    "name": "SK ZBGIS - Ortofotomozaika SR (WMS)",
    "kind": "WMS",
    "url": "https://zbgisws.skgeodesy.sk/zbgis_ortofoto_wms/service.svc/get",
    "region": "SK",
    "auth": ""
  },
  {
    "name": "SK ZBGIS - Administrat\u00edvne hranice (WMS)",
    "kind": "WMS",
    "url": "https://zbgisws.skgeodesy.sk/zbgis_administrativne_hranice_wms_featureinfo/service.svc/get",
    "region": "SK",
    "auth": ""
  },
  {
    "name": "SK ZBGIS - V\u00fd\u0161kopis (WMS)",
    "kind": "WMS",
    "url": "https://zbgisws.skgeodesy.sk/zbgis_vyskopis_wms_featureinfo/service.svc/get",
    "region": "SK",
    "auth": ""
  },
  {
    "name": "SK ZBGIS - Vodstvo (WMS)",
    "kind": "WMS",
    "url": "https://zbgisws.skgeodesy.sk/zbgis_vodstvo_wms_featureinfo/service.svc/get",
    "region": "SK",
    "auth": ""
  },
  {
    "name": "SK ZBGIS - Geografick\u00e9 n\u00e1zvy (WMS)",
    "kind": "WMS",
    "url": "https://zbgisws.skgeodesy.sk/zbgis_geograficke_nazvoslovie_wms/service.svc/get",
    "region": "SK",
    "auth": ""
  },
  {
    "name": "SK ZBGIS - Digit\u00e1lny model reli\u00e9fu DMR 5.0 (WMS)",
    "kind": "WMS",
    "url": "https://zbgisws.skgeodesy.sk/zbgis_dmr_wms/service.svc/get",
    "region": "SK",
    "auth": ""
  },
  {
    "name": "SK ESKN - Katastr\u00e1lna mapa (WMS)",
    "kind": "WMS",
    "url": "https://kataster.skgeodesy.sk/eskn/services/NR/kn_wms_norm/MapServer/WmsServer",
    "region": "SK",
    "auth": ""
  },
  {
    "name": "SK ESKN - Kataster nad ortofotom (WMS)",
    "kind": "WMS",
    "url": "https://kataster.skgeodesy.sk/eskn/services/NR/kn_wms_orto/MapServer/WmsServer",
    "region": "SK",
    "auth": ""
  },
  {
    "name": "SK ESKN - Mapa ur\u010den\u00e9ho oper\u00e1tu (WMS)",
    "kind": "WMS",
    "url": "https://kataster.skgeodesy.sk/eskn/services/NR/uo_wms_norm/MapServer/WmsServer",
    "region": "SK",
    "auth": ""
  },
  {
    "name": "SK ZBGIS - Z\u00e1kladn\u00e1 mapa S-JTSK (WMTS)",
    "kind": "WMTS",
    "url": "https://zbgisws.skgeodesy.sk/zbgis_wmts_sjtsk/service.svc/get?",
    "region": "SK",
    "auth": ""
  },
  {
    "name": "SK ZBGIS - Ortofotomozaika S-JTSK (WMTS)",
    "kind": "WMTS",
    "url": "https://zbgisws.skgeodesy.sk/zbgis_ortofoto_wmts_sjtsk/service.svc/get?",
    "region": "SK",
    "auth": ""
  },
  {
    "name": "SK ESKN - Kataster Web Mercator (WMTS)",
    "kind": "WMTS",
    "url": "https://kataster.skgeodesy.sk/eskn/rest/services/NR/kn_wmts_norm_wm/MapServer/WMTS",
    "region": "SK",
    "auth": ""
  },
  {
    "name": "SK ESKN - Kataster nad ortofotom Web Mercator (WMTS)",
    "kind": "WMTS",
    "url": "https://kataster.skgeodesy.sk/eskn/rest/services/NR/kn_wmts_orto_wm/MapServer/WMTS",
    "region": "SK",
    "auth": ""
  },
  {
    "name": "SK GKU - Historick\u00e1 mapa III. vojensk\u00e9ho mapovania (WMS)",
    "kind": "WMS",
    "url": "https://zbgisws.skgeodesy.sk/hm_III_vm/service.svc/get",
    "region": "SK",
    "auth": ""
  },
  {
    "name": "SK GKU - Z\u00e1kladn\u00e9 mapy SR raster (WMS)",
    "kind": "WMS",
    "url": "https://zbgisws.skgeodesy.sk/zmsr_wms/service.svc/get",
    "region": "SK",
    "auth": ""
  },
  {
    "name": "SK GKU - Topografick\u00e9 mapy RETM raster (WMS)",
    "kind": "WMS",
    "url": "https://zbgisws.skgeodesy.sk/retm_wms/service.svc/get",
    "region": "SK",
    "auth": ""
  },
  {
    "name": "SK GKU - Klady mapov\u00fdch listov (WMS)",
    "kind": "WMS",
    "url": "https://zbgisws.skgeodesy.sk/klady_mapovych_listov_wms/service.svc/get",
    "region": "SK",
    "auth": ""
  },
  {
    "name": "SK GKU - Administrat\u00edvna mapa SR raster (WMS)",
    "kind": "WMS",
    "url": "https://zbgisws.skgeodesy.sk/amsr_wms/service.svc/get",
    "region": "SK",
    "auth": ""
  },
  {
    "name": "SK Geol\u00f3gia - Geologick\u00e1 mapa SR 1-50 000",
    "kind": "ARCGIS_REST",
    "url": "https://ags.geology.sk/arcgis/rest/services/GeologickeMapy/GeologickaMapaSR50_2/MapServer",
    "region": "SK",
    "auth": ""
  },
  {
    "name": "SK Geol\u00f3gia - Geologick\u00e1 mapa SR 1-200 000",
    "kind": "ARCGIS_REST",
    "url": "https://ags.geology.sk/arcgis/rest/services/WebServices/GM200/MapServer",
    "region": "SK",
    "auth": ""
  },
  {
    "name": "SK Geol\u00f3gia - Rad\u00f3nov\u00e9 riziko",
    "kind": "ARCGIS_REST",
    "url": "https://ags.geology.sk/arcgis/rest/services/WebServices/RADON/MapServer",
    "region": "SK",
    "auth": ""
  },
  {
    "name": "SK Lesy - Hranice lesn\u00fdch porastov (JPRL)",
    "kind": "ARCGIS_REST",
    "url": "https://gis.nlcsk.org/arcgis/rest/services/Inspire/JPRL/MapServer",
    "region": "SK",
    "auth": ""
  },
  {
    "name": "SK Lesy - Druhov\u00e9 zlo\u017eenie lesa",
    "kind": "ARCGIS_REST",
    "url": "https://gis.nlcsk.org/arcgis/rest/services/Inspire/DrevinoveZlozenie/MapServer",
    "region": "SK",
    "auth": ""
  },
  {
    "name": "SK Lesy - Lesn\u00e9 cesty a komunik\u00e1cie",
    "kind": "ARCGIS_REST",
    "url": "https://gis.nlcsk.org/arcgis/rest/services/Inspire/LesneCesty/MapServer",
    "region": "SK",
    "auth": ""
  },
  {
    "name": "SK Lesy - Lesn\u00e9 p\u00f4dne jednotky",
    "kind": "ARCGIS_REST",
    "url": "https://gis.nlcsk.org/arcgis/rest/services/Inspire/PodneTypy/MapServer",
    "region": "SK",
    "auth": ""
  },
  {
    "name": "SK P\u00f4da - Bonitovan\u00e9 p\u00f4dno-ekologick\u00e9 jednotky BPEJ",
    "kind": "ARCGIS_REST",
    "url": "https://portal.vupop.sk/arcgis/rest/services/BPEJ/BPEJ_ZBGIS/MapServer",
    "region": "SK",
    "auth": ""
  },
  {
    "name": "SK \u017divotn\u00e9 prostredie - Environment\u00e1lne z\u00e1\u0165a\u017ee",
    "kind": "ARCGIS_REST",
    "url": "https://arc.sazp.sk/arcgis/rest/services/env_zataze/environmentalna_zataz/MapServer",
    "region": "SK",
    "auth": ""
  },
  {
    "name": "SK \u017divotn\u00e9 prostredie - Biocentr\u00e1 a biokoridory R\u00daSES",
    "kind": "ARCGIS_REST",
    "url": "https://arc.sazp.sk/arcgis/rest/services/uses/ruses/MapServer",
    "region": "SK",
    "auth": ""
  },
  {
    "name": "SK Atlas krajiny - Rastrov\u00e9 podklady",
    "kind": "ARCGIS_REST",
    "url": "https://arc.sazp.sk/arcgis/rest/services/atlassr/atlas_podklad_raster/MapServer",
    "region": "SK",
    "auth": ""
  },
  {
    "name": "SK Atlas krajiny - Vektorov\u00e9 mapov\u00e9 podklady",
    "kind": "ARCGIS_REST",
    "url": "https://arc.sazp.sk/arcgis/rest/services/atlassr/atlas_podklad_vektor/MapServer",
    "region": "SK",
    "auth": ""
  },
  {
    "name": "SK Atlas krajiny - Tematick\u00e9 mapy pr\u00edrody",
    "kind": "ARCGIS_REST",
    "url": "https://arc.sazp.sk/arcgis/rest/services/atlassr/atlassr_08/MapServer",
    "region": "SK",
    "auth": ""
  },
  {
    "name": "SK SHM\u00da - Podrobn\u00e9 povodia 1-50 000",
    "kind": "ARCGIS_REST",
    "url": "https://arcgis.shmu.sk/arcgis/rest/services/public/PodrobnePovodia50/MapServer",
    "region": "SK",
    "auth": ""
  },
  {
    "name": "SK SHM\u00da - Hlavn\u00e9 povodia 1-50 000",
    "kind": "ARCGIS_REST",
    "url": "https://arcgis.shmu.sk/arcgis/rest/services/public/HlavnePovodia50/MapServer",
    "region": "SK",
    "auth": ""
  },
  {
    "name": "SK Bratislava - \u00dazemn\u00fd pl\u00e1n - Funk\u010dn\u00e9 vyu\u017eitie",
    "kind": "ARCGIS_REST",
    "url": "https://geoportal.bratislava.sk/hSite/rest/services/up/2_1_Priestorov%C3%A9_usporiadanie_a_funk%C4%8Dn%C3%A9_vyu%C5%BEitie_%C3%BAzemia__komplexn%C3%A9_rie%C5%A1enie/MapServer",
    "region": "SK",
    "auth": ""
  },
  {
    "name": "SK Bratislava - Funk\u010dn\u00e9 plochy",
    "kind": "ARCGIS_REST",
    "url": "https://geoportal.bratislava.sk/hSite/rest/services/up/funkcne_plochy_pop_up_sde/MapServer",
    "region": "SK",
    "auth": ""
  },
  {
    "name": "SK Bratislava - Cyklotrasy",
    "kind": "ARCGIS_REST",
    "url": "https://geoportal.bratislava.sk/hSite/rest/services/doprava/Cyklotrasy/MapServer",
    "region": "SK",
    "auth": ""
  },
  {
    "name": "SK Bratislava - Linky MHD",
    "kind": "ARCGIS_REST",
    "url": "https://geoportal.bratislava.sk/hSite/rest/services/doprava/Linky_MHD/MapServer",
    "region": "SK",
    "auth": ""
  },
  {
    "name": "SK WFS - Administrat\u00edvne hranice (\u00daGKK)",
    "kind": "WFS",
    "url": "https://zbgisws.skgeodesy.sk/zbgis_administrativne_hranice_wfs/service.svc/get",
    "region": "SK",
    "auth": ""
  },
  {
    "name": "SK WFS - Geografick\u00e9 n\u00e1zvoslovie (\u00daGKK)",
    "kind": "WFS",
    "url": "https://zbgisws.skgeodesy.sk/zbgis_geograficke_nazvoslovie_wfs/service.svc/get",
    "region": "SK",
    "auth": ""
  },
  {
    "name": "CZ Katastr - Katastralni mapa (WMS)",
    "kind": "WMS",
    "url": "https://services.cuzk.gov.cz/wms/local-km-wms.asp",
    "region": "CZ",
    "auth": ""
  },
  {
    "name": "CZ Katastr - Katastralni mapa JTSK (WMTS)",
    "kind": "WMTS",
    "url": "https://services.cuzk.gov.cz/wmts/local-km-wmts-jtsk.asp",
    "region": "CZ",
    "auth": ""
  },
  {
    "name": "CZ Katastr - Katastralni mapa Web Mercator (WMTS)",
    "kind": "WMTS",
    "url": "https://services.cuzk.gov.cz/wmts/local-km-wmts-google.asp",
    "region": "CZ",
    "auth": ""
  },
  {
    "name": "CZ Katastr - Parcely INSPIRE CP (WMS)",
    "kind": "WMS",
    "url": "https://services.cuzk.gov.cz/wms/inspire-cp-wms.asp",
    "region": "CZ",
    "auth": ""
  },
  {
    "name": "CZ Ortofoto - Aktualni (WMS)",
    "kind": "WMS",
    "url": "https://ags.cuzk.gov.cz/arcgis1/services/ORTOFOTO/MapServer/WMSServer",
    "region": "CZ",
    "auth": ""
  },
  {
    "name": "CZ Ortofoto - Aktualni (WMTS)",
    "kind": "WMTS",
    "url": "https://ags.cuzk.gov.cz/arcgis1/rest/services/ORTOFOTO/MapServer/WMTS?service=WMTS&request=GetCapabilities",
    "region": "CZ",
    "auth": ""
  },
  {
    "name": "CZ Ortofoto - Archivni po rocich (WMS)",
    "kind": "WMS",
    "url": "https://geoportal.cuzk.gov.cz/WMS_ORTOFOTO_ARCHIV/WMService.aspx",
    "region": "CZ",
    "auth": ""
  },
  {
    "name": "CZ Ortofoto - CIR infracervene (WMS)",
    "kind": "WMS",
    "url": "https://geoportal.cuzk.gov.cz/WMS_ORTOFOTO_CIR/WMService.aspx",
    "region": "CZ",
    "auth": ""
  },
  {
    "name": "CZ Topo - Zakladni topograficke mapy ZTM (WMTS)",
    "kind": "WMTS",
    "url": "https://ags.cuzk.gov.cz/arcgis1/rest/services/ZTM/MapServer/WMTS?service=WMTS&request=GetCapabilities",
    "region": "CZ",
    "auth": ""
  },
  {
    "name": "CZ Topo - Prehledova mapa (WMTS)",
    "kind": "WMTS",
    "url": "https://ags.cuzk.gov.cz/arcgis1/rest/services/PrehledovaMapa/MapServer/WMTS/1.0.0/WMTSCapabilities.xml",
    "region": "CZ",
    "auth": ""
  },
  {
    "name": "CZ Topo - ZTM 1-5000 (WMTS)",
    "kind": "WMTS",
    "url": "https://ags.cuzk.gov.cz/arcgis1/rest/services/ZTM/ZTM5/MapServer/WMTS/1.0.0/WMTSCapabilities.xml",
    "region": "CZ",
    "auth": ""
  },
  {
    "name": "CZ Topo - ZTM 1-10000 (WMTS)",
    "kind": "WMTS",
    "url": "https://ags.cuzk.gov.cz/arcgis1/rest/services/ZTM/ZTM10/MapServer/WMTS/1.0.0/WMTSCapabilities.xml",
    "region": "CZ",
    "auth": ""
  },
  {
    "name": "CZ Topo - ZTM 1-25000 (WMTS)",
    "kind": "WMTS",
    "url": "https://ags.cuzk.gov.cz/arcgis1/rest/services/ZTM/ZTM25/MapServer/WMTS/1.0.0/WMTSCapabilities.xml",
    "region": "CZ",
    "auth": ""
  },
  {
    "name": "CZ Topo - ZTM 1-50000 (WMTS)",
    "kind": "WMTS",
    "url": "https://ags.cuzk.gov.cz/arcgis1/rest/services/ZTM/ZTM50/MapServer/WMTS/1.0.0/WMTSCapabilities.xml",
    "region": "CZ",
    "auth": ""
  },
  {
    "name": "CZ Topo - ZTM 1-100000 (WMTS)",
    "kind": "WMTS",
    "url": "https://ags.cuzk.gov.cz/arcgis1/rest/services/ZTM/ZTM100/MapServer/WMTS/1.0.0/WMTSCapabilities.xml",
    "region": "CZ",
    "auth": ""
  },
  {
    "name": "CZ Topo - Data50 (WMS)",
    "kind": "WMS",
    "url": "https://ags.cuzk.gov.cz/arcgis/services/DATA50/MapServer/WmsServer",
    "region": "CZ",
    "auth": ""
  },
  {
    "name": "CZ Topo - ZTM ArcGIS REST",
    "kind": "ARCGIS_REST",
    "url": "https://ags.cuzk.gov.cz/arcgis1/rest/services/ZTM/MapServer",
    "region": "CZ",
    "auth": ""
  },
  {
    "name": "CZ Topo - Prehledova mapa ArcGIS REST",
    "kind": "ARCGIS_REST",
    "url": "https://ags.cuzk.gov.cz/arcgis1/rest/services/PrehledovaMapa/MapServer",
    "region": "CZ",
    "auth": ""
  },
  {
    "name": "CZ CUZK - Spravni jednotky (WMS)",
    "kind": "WMS",
    "url": "https://services.cuzk.gov.cz/wms/local-ux-wms.asp",
    "region": "CZ",
    "auth": ""
  },
  {
    "name": "CZ CUZK - Stav digitalizace katastru (WMS)",
    "kind": "WMS",
    "url": "https://services.cuzk.gov.cz/wms/local-dg-wms.asp",
    "region": "CZ",
    "auth": ""
  },
  {
    "name": "CZ RUIAN - Ucelove uzemni prvky (WMS)",
    "kind": "WMS",
    "url": "https://services.cuzk.gov.cz/wms/local-uup-wms.asp",
    "region": "CZ",
    "auth": ""
  },
  {
    "name": "CZ INSPIRE - Adresy (WMS)",
    "kind": "WMS",
    "url": "https://services.cuzk.gov.cz/wms/inspire-ad-wms.asp",
    "region": "CZ",
    "auth": ""
  },
  {
    "name": "CZ INSPIRE - Spravni jednotky (WMS)",
    "kind": "WMS",
    "url": "https://services.cuzk.gov.cz/wms/inspire-au-wms.asp",
    "region": "CZ",
    "auth": ""
  },
  {
    "name": "CZ INSPIRE - Budovy (WMS)",
    "kind": "WMS",
    "url": "https://services.cuzk.gov.cz/wms/inspire-bu-wms.asp",
    "region": "CZ",
    "auth": ""
  },
  {
    "name": "CZ WFS - Katastralni parcely INSPIRE CP",
    "kind": "WFS",
    "url": "https://services.cuzk.gov.cz/wfs/inspire-cp-wfs.asp",
    "region": "CZ",
    "auth": ""
  },
  {
    "name": "CZ WFS - Katastralni mapa rozsirena CPX",
    "kind": "WFS",
    "url": "https://services.cuzk.gov.cz/wfs/inspire-cpx-wfs.asp",
    "region": "CZ",
    "auth": ""
  },
  {
    "name": "CZ WFS - Budovy INSPIRE BU",
    "kind": "WFS",
    "url": "https://services.cuzk.gov.cz/wfs/inspire-bu-wfs.asp",
    "region": "CZ",
    "auth": ""
  },
  {
    "name": "CZ WFS - Adresy INSPIRE AD",
    "kind": "WFS",
    "url": "https://services.cuzk.gov.cz/wfs/inspire-ad-wfs.asp",
    "region": "CZ",
    "auth": ""
  },
  {
    "name": "CZ WFS - Spravni jednotky INSPIRE AU",
    "kind": "WFS",
    "url": "https://services.cuzk.gov.cz/wfs/inspire-au-wfs.asp",
    "region": "CZ",
    "auth": ""
  },
  {
    "name": "CZ WFS - Zaznamy podrobneho mereni zmen ZPMZ",
    "kind": "WFS",
    "url": "https://services.cuzk.gov.cz/wfs/local-zpmz-wfs.asp",
    "region": "CZ",
    "auth": ""
  },
  {
    "name": "CZ CGS - Geologicka mapa 1-25000 zakryta",
    "kind": "ARCGIS_REST",
    "url": "https://mapy.geology.cz/arcgis/rest/services/Geologie/geologicka_mapa25_zakryta/MapServer",
    "region": "CZ",
    "auth": ""
  },
  {
    "name": "CZ CGS - Geologicka mapa 1-25000 odkryta",
    "kind": "ARCGIS_REST",
    "url": "https://mapy.geology.cz/arcgis/rest/services/Geologie/geologicka_mapa25_odkryta/MapServer",
    "region": "CZ",
    "auth": ""
  },
  {
    "name": "CZ CGS - Geologicka mapa 1-50000",
    "kind": "ARCGIS_REST",
    "url": "https://mapy.geology.cz/arcgis/rest/services/Geologie/geologicka_mapa50/MapServer",
    "region": "CZ",
    "auth": ""
  },
  {
    "name": "CZ CGS - Geologicka mapa 1-500000",
    "kind": "ARCGIS_REST",
    "url": "https://mapy.geology.cz/arcgis/rest/services/Geologie/geologicka_mapa500_CR/MapServer",
    "region": "CZ",
    "auth": ""
  },
  {
    "name": "CZ CGS - Historicke geologicke mapy 1-144000",
    "kind": "ARCGIS_REST",
    "url": "https://mapy.geology.cz/arcgis/rest/services/Geologie/stare_mapy_144000/MapServer",
    "region": "CZ",
    "auth": ""
  },
  {
    "name": "CZ CGS - Historicke geologicke mapy 1-28800",
    "kind": "ARCGIS_REST",
    "url": "https://mapy.geology.cz/arcgis/rest/services/Geologie/stare_mapy_28800/MapServer",
    "region": "CZ",
    "auth": ""
  },
  {
    "name": "CZ CGS - Pudy - pudni typy 1-50000",
    "kind": "ARCGIS_REST",
    "url": "https://mapy.geology.cz/arcgis/rest/services/Pudy/pudni_typy50/MapServer",
    "region": "CZ",
    "auth": ""
  },
  {
    "name": "CZ CGS - Hydrogeologicka mapa 1-50000",
    "kind": "ARCGIS_REST",
    "url": "https://mapy.geology.cz/arcgis/rest/services/HydroGeologie/HG50_mapa/MapServer",
    "region": "CZ",
    "auth": ""
  },
  {
    "name": "CZ CGS - Sesuvy Geofond",
    "kind": "ARCGIS_REST",
    "url": "https://mapy.geology.cz/arcgis/rest/services/Geohazardy/sesuvy_Geofond/MapServer",
    "region": "CZ",
    "auth": ""
  },
  {
    "name": "CZ CGS - Vrtna prozkoumanost",
    "kind": "ARCGIS_REST",
    "url": "https://mapy.geology.cz/arcgis/rest/services/Prozkoumanost/Vrtna_prozkoumanost/MapServer",
    "region": "CZ",
    "auth": ""
  },
  {
    "name": "CZ CGS - Nerostne suroviny SurIS",
    "kind": "ARCGIS_REST",
    "url": "https://mapy.geology.cz/arcgis/rest/services/Suroviny/Surovinovy_informacni_system/MapServer",
    "region": "CZ",
    "auth": ""
  },
  {
    "name": "CZ AOPK - Chranena uzemi a opendata (ArcGIS REST)",
    "kind": "ARCGIS_REST",
    "url": "https://gis.nature.cz/arcgis/rest/services/Aplikace/Opendata/MapServer",
    "region": "CZ",
    "auth": ""
  },
  {
    "name": "CZ AOPK - Uzemi ochrany prirody",
    "kind": "ARCGIS_REST",
    "url": "https://gis.nature.cz/arcgis/rest/services/UzemniOchrana/ChranUzemi/MapServer",
    "region": "CZ",
    "auth": ""
  },
  {
    "name": "CZ AOPK - Chranena uzemi, pametne stromy (WMS)",
    "kind": "WMS",
    "url": "https://gis.nature.cz/arcgis/services/Aplikace/Opendata/MapServer/WMSServer",
    "region": "CZ",
    "auth": ""
  },
  {
    "name": "CZ AOPK - Chranena uzemi, opendata (WFS)",
    "kind": "WFS",
    "url": "https://gis.nature.cz/arcgis/services/Aplikace/Opendata/MapServer/WFSServer",
    "region": "CZ",
    "auth": ""
  }
]

OPTIONAL_SERVICES = [
  {
    "name": "Mapy.com basic",
    "kind": "XYZ",
    "region": "WORLD",
    "auth": "MAPY_API_KEY",
    "url": "https://api.mapy.com/v1/maptiles/basic/256/{z}/{x}/{y}?apikey=${MAPY_API_KEY}"
  },
  {
    "name": "Mapy.com outdoor",
    "kind": "XYZ",
    "region": "WORLD",
    "auth": "MAPY_API_KEY",
    "url": "https://api.mapy.com/v1/maptiles/outdoor/256/{z}/{x}/{y}?apikey=${MAPY_API_KEY}"
  },
  {
    "name": "Mapy.com aerial",
    "kind": "XYZ",
    "region": "WORLD",
    "auth": "MAPY_API_KEY",
    "url": "https://api.mapy.com/v1/maptiles/aerial/256/{z}/{x}/{y}?apikey=${MAPY_API_KEY}"
  },
  {
    "name": "Mapy.com names-overlay",
    "kind": "XYZ",
    "region": "WORLD",
    "auth": "MAPY_API_KEY",
    "url": "https://api.mapy.com/v1/maptiles/names-overlay/256/{z}/{x}/{y}?apikey=${MAPY_API_KEY}"
  },
  {
    "name": "Mapy.com winter",
    "kind": "XYZ",
    "region": "WORLD",
    "auth": "MAPY_API_KEY",
    "url": "https://api.mapy.com/v1/maptiles/winter/256/{z}/{x}/{y}?apikey=${MAPY_API_KEY}"
  },
  {
    "name": "Azure Maps Road",
    "kind": "XYZ",
    "region": "WORLD",
    "auth": "AZURE_MAPS_KEY",
    "url": "https://atlas.microsoft.com/map/tile?api-version=2024-04-01&tilesetId=microsoft.base.road&zoom={z}&x={x}&y={y}&tileSize=256&subscription-key=${AZURE_MAPS_KEY}"
  },
  {
    "name": "Azure Maps Dark Grey",
    "kind": "XYZ",
    "region": "WORLD",
    "auth": "AZURE_MAPS_KEY",
    "url": "https://atlas.microsoft.com/map/tile?api-version=2024-04-01&tilesetId=microsoft.base.darkgrey&zoom={z}&x={x}&y={y}&tileSize=256&subscription-key=${AZURE_MAPS_KEY}"
  },
  {
    "name": "Azure Maps Imagery",
    "kind": "XYZ",
    "region": "WORLD",
    "auth": "AZURE_MAPS_KEY",
    "url": "https://atlas.microsoft.com/map/tile?api-version=2024-04-01&tilesetId=microsoft.imagery&zoom={z}&x={x}&y={y}&tileSize=256&subscription-key=${AZURE_MAPS_KEY}"
  },
  {
    "name": "Azure Maps Hybrid Road",
    "kind": "XYZ",
    "region": "WORLD",
    "auth": "AZURE_MAPS_KEY",
    "url": "https://atlas.microsoft.com/map/tile?api-version=2024-04-01&tilesetId=microsoft.base.hybrid.road&zoom={z}&x={x}&y={y}&tileSize=256&subscription-key=${AZURE_MAPS_KEY}"
  },
  {
    "name": "Azure Maps Labels Road",
    "kind": "XYZ",
    "region": "WORLD",
    "auth": "AZURE_MAPS_KEY",
    "url": "https://atlas.microsoft.com/map/tile?api-version=2024-04-01&tilesetId=microsoft.base.labels.road&zoom={z}&x={x}&y={y}&tileSize=256&subscription-key=${AZURE_MAPS_KEY}"
  },
  {
    "name": "Stamen Terrain (Stadia)",
    "kind": "XYZ",
    "region": "WORLD",
    "auth": "STADIA_API_KEY",
    "url": "https://tiles.stadiamaps.com/tiles/stamen_terrain/{z}/{x}/{y}.png?api_key=${STADIA_API_KEY}"
  },
  {
    "name": "Stamen Toner (Stadia)",
    "kind": "XYZ",
    "region": "WORLD",
    "auth": "STADIA_API_KEY",
    "url": "https://tiles.stadiamaps.com/tiles/stamen_toner/{z}/{x}/{y}.png?api_key=${STADIA_API_KEY}"
  },
  {
    "name": "Stamen Toner Lite (Stadia)",
    "kind": "XYZ",
    "region": "WORLD",
    "auth": "STADIA_API_KEY",
    "url": "https://tiles.stadiamaps.com/tiles/stamen_toner_lite/{z}/{x}/{y}.png?api_key=${STADIA_API_KEY}"
  },
  {
    "name": "Stamen Watercolor (Stadia)",
    "kind": "XYZ",
    "region": "WORLD",
    "auth": "STADIA_API_KEY",
    "url": "https://tiles.stadiamaps.com/tiles/stamen_watercolor/{z}/{x}/{y}.jpg?api_key=${STADIA_API_KEY}"
  },
  {
    "name": "OpenWeatherMap Temperature",
    "kind": "XYZ",
    "region": "WORLD",
    "auth": "OPENWEATHER_API_KEY",
    "url": "https://tile.openweathermap.org/map/temp_new/{z}/{x}/{y}.png?appid=${OPENWEATHER_API_KEY}"
  },
  {
    "name": "OpenWeatherMap Clouds",
    "kind": "XYZ",
    "region": "WORLD",
    "auth": "OPENWEATHER_API_KEY",
    "url": "https://tile.openweathermap.org/map/clouds_new/{z}/{x}/{y}.png?appid=${OPENWEATHER_API_KEY}"
  },
  {
    "name": "OpenWeatherMap Wind",
    "kind": "XYZ",
    "region": "WORLD",
    "auth": "OPENWEATHER_API_KEY",
    "url": "https://tile.openweathermap.org/map/wind_new/{z}/{x}/{y}.png?appid=${OPENWEATHER_API_KEY}"
  },
  {
    "name": "Bing Aerial",
    "kind": "BING_DYNAMIC",
    "region": "WORLD",
    "auth": "BING_MAPS_KEY",
    "url": "BING_METADATA:Aerial"
  },
  {
    "name": "Bing Road",
    "kind": "BING_DYNAMIC",
    "region": "WORLD",
    "auth": "BING_MAPS_KEY",
    "url": "BING_METADATA:RoadOnDemand"
  },
  {
    "name": "Bing Aerial With Labels",
    "kind": "BING_DYNAMIC",
    "region": "WORLD",
    "auth": "BING_MAPS_KEY",
    "url": "BING_METADATA:AerialWithLabelsOnDemand"
  },
  {
    "name": "Bing Canvas Light",
    "kind": "BING_DYNAMIC",
    "region": "WORLD",
    "auth": "BING_MAPS_KEY",
    "url": "BING_METADATA:CanvasLight"
  },
  {
    "name": "Bing Canvas Dark",
    "kind": "BING_DYNAMIC",
    "region": "WORLD",
    "auth": "BING_MAPS_KEY",
    "url": "BING_METADATA:CanvasDark"
  }
]


# ---------------------------------------------------------------------------
# Helpers: catalog files, stable service names, and ArcGIS Pro integration
# ---------------------------------------------------------------------------

def all_services():
    return BASE_SERVICES + OPTIONAL_SERVICES


def is_available(item):
    return not item["auth"] or bool(API_KEYS.get(item["auth"], ""))


def public_url(item):
    # Always keep ${NAME} placeholders - never disclose actual API keys.
    return item["url"]


def runtime_url(item):
    """Build a URL in memory; NEVER print or persist a URL containing a key."""
    url = item["url"]
    keyname = item["auth"]
    if keyname:
        key = API_KEYS.get(keyname, "")
        if not key:
            raise ValueError("Missing API key: " + keyname)
        if item["kind"] == "BING_DYNAMIC":
            url = get_bing_template(url.split(":", 1)[1], key)
        else:
            url = url.replace("${" + keyname + "}", quote(key, safe=""))
    if item["kind"] == "XYZ":
        # Esri support documentation gives {level}/{col}/{row} for XYZ URLs.
        # Pure text substitution also works for x/y/z query parameters.
        url = (url.replace("{z}", "{level}")
                  .replace("{x}", "{col}")
                  .replace("{y}", "{row}"))
    return url


def get_bing_template(imagery_set, key):
    """Bing Enterprise metadata (official, requires eligible key)."""
    endpoint = (
        "https://dev.virtualearth.net/REST/v1/Imagery/Metadata/"
        + quote(imagery_set, safe="")
        + "?output=json&uriScheme=https&key=" + quote(key, safe="")
    )
    req = Request(endpoint, headers={"User-Agent": "GIS-LAB-ArcGISPro/1.0"})
    with urlopen(req, timeout=12) as response:
        payload = json.load(response)
    entries = payload.get("resourceSets", [{}])[0].get("resources", [])
    if not entries:
        raise RuntimeError("Bing metadata has no image URL")
    res = entries[0]
    subs = res.get("imageUrlSubdomains") or ["t0"]
    return (res["imageUrl"]
            .replace("{subdomain}", subs[0])
            .replace("{quadkey}", "{quadkey}")
            .replace("{culture}", "sk-SK"))
    # CAUTION: ArcGIS Pro XYZ custom URL quadkey support is not guaranteed.


def get_export_dir(aprx=None):
    if OUTPUT_DIRECTORY:
        directory = Path(OUTPUT_DIRECTORY)
    elif aprx is not None and getattr(aprx, "homeFolder", None):
        directory = Path(aprx.homeFolder) / "GIS-LAB-ArcGIS-Catalog"
    else:
        directory = Path.home() / "Documents" / "GIS-LAB-ArcGIS-Catalog"
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def export_catalog(directory):
    """Export source-only (safe) URLs, excluding all real credential values."""
    services = all_services()
    columns = ["region", "name", "kind", "url", "api_key_variable", "requires_key"]
    with (directory / "arcgis_basemaps_catalog.csv").open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns, delimiter=";")
        writer.writeheader()
        for item in services:
            writer.writerow({
                "region": item["region"],
                "name": item["name"],
                "kind": item["kind"],
                "url": public_url(item),
                "api_key_variable": item["auth"],
                "requires_key": "yes" if item["auth"] else "no",
            })
    with (directory / "arcgis_basemaps_catalog.json").open("w", encoding="utf-8") as f:
        json.dump(services, f, indent=2, ensure_ascii=False)
    with (directory / "README.txt").open("w", encoding="utf-8") as f:
        f.write(
            "GIS-LAB - ArcGIS Pro map catalog\n"
            "Author: Miroslav Reiter | riaditel@itacademy.sk\n\n"
            "SERVICES / WAYS TO CONNECT:\n"
            "XYZ: Map > Add Data > Data From Path, if provider supports it.\n"
            "ArcGIS REST MapServer: Map > Add Data > Data From Path.\n"
            "WMS: Map > Add Data > Data From Path, choose WMS.\n"
            "WFS: Insert > Connections > Server > New WFS Server.\n"
            "WMTS: Insert > Connections > Server > New WMTS Server.\n"
            "Select the individual layer after connecting to WFS/WMTS.\n\n"
            "CSV and JSON are reference catalogs, NOT native server connections.\n"
            "Custom keys are placeholders, not actual credentials.\n"
            "Google legacy and Bing Enterprise are restricted/legacy sources.\n"
            "Service availability and licensing must be checked with providers.\n"
        )
    return len(services)


def site_root(url):
    """Extract ArcGIS REST service site's root to create site-level .ags."""
    token = "/rest/services/"
    before, separator, _ = url.partition(token)
    return before if separator else None


def create_site_connections(arcpy, items, directory, log):
    roots = sorted({site_root(i["url"]) for i in items if i["kind"] == "ARCGIS_REST"} - {None})
    out = directory / "ags_site_connections"
    out.mkdir(exist_ok=True)
    used = set()
    for root in roots:
        # Use the hostname and last path component; ensure unique filenames.
        hostname = root.split("//", 1)[-1].replace("/", "_").replace(":", "_")
        safe = "".join(ch if ch.isascii() and (ch.isalnum() or ch in "-_.") else "_" for ch in hostname)
        name = safe + ".ags"
        if name in used:
            continue
        used.add(name)
        outfile = out / name
        if outfile.exists():
            log.append("SKIP AGS existing: " + name)
            continue
        try:
            arcpy.CreateAGSServerConnection(str(outfile), root)
            log.append("OK AGS: " + name)
        except Exception as exc:
            log.append("FAIL AGS: " + name + " / " + type(exc).__name__)
    return len(roots)


def attach_catalog_folder(aprx, directory, log):
    if not hasattr(aprx, "updateFolderConnections"):
        log.append("SKIP: This ArcGIS Pro version does not support updateFolderConnections")
        return
    connections = list(aprx.folderConnections)
    normalized = os.path.normcase(os.path.normpath(str(directory)))
    if any(os.path.normcase(os.path.normpath(c["connectionString"])) == normalized for c in connections):
        log.append("SKIP: Catalog folder already linked")
        return
    connections.append({"connectionString": str(directory), "alias": "GIS-LAB Basemaps", "isHomeFolder": False})
    aprx.updateFolderConnections(connections, validate=True)
    log.append("OK: Catalog folder linked under Project > Folders")


def ensure_map(aprx):
    matches = aprx.listMaps(MAP_NAME)
    if matches:
        return matches[0]
    return aprx.createMap(MAP_NAME, "MAP")


def load_selected_layers(aprx, log):
    sources = {entry["name"]: entry for entry in all_services()}
    names = list(dict.fromkeys(SELECTED_LAYER_NAMES))
    if not names:
        log.append("No layer names selected")
        return
    target = ensure_map(aprx)
    existing = {layer.name for layer in target.listLayers()}
    first_visible = True
    for name in names:
        item = sources.get(name)
        if item is None:
            log.append("SKIP: Unknown catalog item: " + name)
            continue
        kind = item["kind"]
        if kind in ("WFS", "WMTS"):
            log.append("MANUAL " + kind + ": " + name + " -> use Insert > Connections > Server")
            continue
        if kind == "BING_DYNAMIC":
            log.append("MANUAL Bing: quadkey template compatibility is not guaranteed")
            continue
        if not is_available(item):
            log.append("SKIP: API key required: " + name + " / " + item["auth"])
            continue
        if name.startswith("Google ") and not ENABLE_LEGACY_GOOGLE_LOADING:
            log.append("SKIP: Undocumented Google legacy URL disabled: " + name)
            continue
        if name in existing:
            log.append("SKIP: Already in map: " + name)
            continue
        try:
            url = runtime_url(item)
            if kind == "WMS":
                layer = target.addDataFromPath(url, "WMS")
            elif kind == "ARCGIS_REST":
                layer = target.addDataFromPath(url, "ARCGIS_SERVER_WEB")
            else:
                layer = target.addDataFromPath(url)
            if layer is None:
                raise RuntimeError("ArcGIS Pro did not return a layer")
            layer.name = name
            layer.visible = first_visible  # Only the first imported layer is visible.
            first_visible = False
            existing.add(name)
            log.append("OK layer: " + name)
        except Exception as exc:
            # Do not leak embedded API key in exception text or logs.
            log.append("FAIL layer: " + name + " / " + type(exc).__name__)


def main():
    try:
        import arcpy
        aprx = arcpy.mp.ArcGISProject("CURRENT")
    except (ImportError, RuntimeError, OSError) as exc:
        print("ArcGIS Pro is required for project import:", type(exc).__name__)
        print("Run from the ArcGIS Pro Python Window with a project open.")
        # Still export the catalog for offline inspection.
        aprx = None
        arcpy = None

    directory = get_export_dir(aprx)
    log = []
    if EXPORT_CATALOG:
        count = export_catalog(directory)
        log.append("OK catalog: " + str(count) + " sources")
    if aprx is not None:
        if ADD_CATALOG_FOLDER_TO_PROJECT:
            try:
                attach_catalog_folder(aprx, directory, log)
            except Exception as exc:
                log.append("FAIL folder connection: " + type(exc).__name__)
        if CREATE_AGS_SITE_CONNECTIONS:
            n = create_site_connections(arcpy, all_services(), directory, log)
            log.append("AGS site roots considered: " + str(n))
        if AUTO_ADD_SELECTED_LAYERS:
            load_selected_layers(aprx, log)
        if AUTO_SAVE_PROJECT:
            try:
                aprx.save()
                log.append("OK: Project saved")
            except Exception as exc:
                log.append("FAIL save: " + type(exc).__name__)
        else:
            log.append("NOTE: Save the project yourself using Ctrl+S")

    (directory / "import_log.txt").write_text("\n".join(log) + "\n", encoding="utf-8")
    print("\nGIS-LAB ArcGIS Pro import\n" + "\n".join(log))
    print("Output: " + str(directory))
    print("To add WFS/WMTS: use the Catalog pane and copy the endpoint from CSV.")


if __name__ == "__main__":
    main()
