# -*- coding: utf-8 -*-
"""
QGIS 4.2.3 - Remove basemap connections imported by GIS-LAB scripts
====================================================================
Autor: Miroslav Reiter
E-mail: riaditel@itacademy.sk
Online kurz: GIS (Geografické Informačné Systémy), QGIS, ArcGIS
Repozitar: https://github.com/miroslav-reiter/gis-lab

Funkcia:
- Odstrani iba pomenovane spojenia zoznamu GIS-LAB, nie ostatne spojenia.
- Pred zmazanim vyzaduje potvrdenie a vytvori JSON zalohu.
- Ak sa spojenie s rovnakym nazvom zmenilo na iny server, ponecha ho.
- Odstrani XYZ, WMS/WMTS, WFS a ArcGIS REST spojenia z QGIS Browsera.
- Volitelne moze odstranit aj pripojenia zo stareho skriptu z roku 2021.
- Neodstranuje mapove vrstvy uz vlozene do projektov QGIS (.qgz/.qgs).
- Zaloha moze obsahovat API kluce a hesla: NEPUBLIKOVAT na GitHube.

Spustenie: QGIS -> Plugins -> Python Console -> Show Editor -> Open Script.
"""

import base64
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

from qgis.PyQt.QtCore import QSettings
from qgis.PyQt.QtWidgets import QMessageBox
from qgis.core import QgsSettings
from qgis.utils import iface

# -----------------------------------------------------------------------------
# NASTAVENIA ODINSTALACIE
# -----------------------------------------------------------------------------

# Po spusteni sa zobrazi potvrdzovacie okno a pri kladnej odpovedi sa maze.
REQUIRE_CONFIRMATION = True

# Odsuhlasene nazvy sa odstrania len pri zhode s povodnym poskytovatelom.
PROTECT_CHANGED_URLS = True

# Ak bol pouzity aj povodny skript z roku 2021, odstranit jeho stare zaznamy.
REMOVE_LEGACY_2021 = True

# Umiestnenie zaloh: napr. C:\\Users\\<pouzivatel>\\qgis_basemap_backups
BACKUP_DIR = Path.home() / 'qgis_basemap_backups'

# -----------------------------------------------------------------------------
# PRESNY ZOZNAM PRIPOJENI POUZIVANYCH IMPORTNYMI SKRIPTMI GIS-LAB
# Tato tabulka bola vygenerovana zo suborov bez spustania externych HTTP volani.
# Hodnota je povodna domena mapovej sluzby (nie API kluc).
# -----------------------------------------------------------------------------

CANDIDATES = {'xyz': {'Azure Maps Dark Grey': 'atlas.microsoft.com',
         'Azure Maps Hybrid Road': 'atlas.microsoft.com',
         'Azure Maps Imagery': 'atlas.microsoft.com',
         'Azure Maps Labels Road': 'atlas.microsoft.com',
         'Azure Maps Road': 'atlas.microsoft.com',
         'Bing Aerial': '.virtualearth.net',
         'Bing Aerial With Labels': '.virtualearth.net',
         'Bing Canvas Dark': '.virtualearth.net',
         'Bing Canvas Light': '.virtualearth.net',
         'Bing Road': '.virtualearth.net',
         'CartoDB Dark Matter': 'basemaps.cartocdn.com',
         'CartoDB Positron': 'basemaps.cartocdn.com',
         'Esri Boundaries and Places': 'server.arcgisonline.com',
         'Esri Gray Dark': 'server.arcgisonline.com',
         'Esri Gray Light': 'server.arcgisonline.com',
         'Esri Ocean': 'services.arcgisonline.com',
         'Esri Satellite': 'server.arcgisonline.com',
         'Esri Standard': 'server.arcgisonline.com',
         'Esri Terrain': 'server.arcgisonline.com',
         'Esri Topo World': 'server.arcgisonline.com',
         'Esri Transportation': 'server.arcgisonline.com',
         'Google Maps': 'mt1.google.com',
         'Google Satellite': 'mt1.google.com',
         'Google Satellite Hybrid': 'mt1.google.com',
         'Google Terrain': 'mt1.google.com',
         'Google Terrain Hybrid': 'mt1.google.com',
         'Mapy.com Aerial': 'api.mapy.com',
         'Mapy.com Basic': 'api.mapy.com',
         'Mapy.com Names Overlay': 'api.mapy.com',
         'Mapy.com Outdoor': 'api.mapy.com',
         'Mapy.com Winter': 'api.mapy.com',
         'OpenStreetMap Standard': 'tile.openstreetmap.org',
         'OpenWeatherMap Clouds': 'tile.openweathermap.org',
         'OpenWeatherMap Temperature': 'tile.openweathermap.org',
         'OpenWeatherMap Wind': 'tile.openweathermap.org',
         'Stamen Terrain (Stadia)': 'tiles.stadiamaps.com',
         'Stamen Toner (Stadia)': 'tiles.stadiamaps.com',
         'Stamen Toner Lite (Stadia)': 'tiles.stadiamaps.com',
         'Stamen Watercolor (Stadia)': 'tiles.stadiamaps.com',
         'USA USGS - Aerial Imagery': 'basemap.nationalmap.gov',
         'USA USGS - Aerial Imagery + Topography': 'basemap.nationalmap.gov',
         'USA USGS - Hydrography': 'basemap.nationalmap.gov',
         'USA USGS - Shaded Relief': 'basemap.nationalmap.gov',
         'USA USGS - Topographic Map': 'basemap.nationalmap.gov'},
 'wms': {'CZ AOPK - Chranena uzemi, pametne stromy (WMS)': 'gis.nature.cz',
         'CZ CUZK - Spravni jednotky (WMS)': 'services.cuzk.gov.cz',
         'CZ CUZK - Stav digitalizace katastru (WMS)': 'services.cuzk.gov.cz',
         'CZ INSPIRE - Adresy (WMS)': 'services.cuzk.gov.cz',
         'CZ INSPIRE - Budovy (WMS)': 'services.cuzk.gov.cz',
         'CZ INSPIRE - Spravni jednotky (WMS)': 'services.cuzk.gov.cz',
         'CZ Katastr - Katastralni mapa (WMS)': 'services.cuzk.gov.cz',
         'CZ Katastr - Katastralni mapa JTSK (WMTS)': 'services.cuzk.gov.cz',
         'CZ Katastr - Katastralni mapa Web Mercator (WMTS)': 'services.cuzk.gov.cz',
         'CZ Katastr - Parcely INSPIRE CP (WMS)': 'services.cuzk.gov.cz',
         'CZ Ortofoto - Aktualni (WMS)': 'ags.cuzk.gov.cz',
         'CZ Ortofoto - Aktualni (WMTS)': 'ags.cuzk.gov.cz',
         'CZ Ortofoto - Archivni po rocich (WMS)': 'geoportal.cuzk.gov.cz',
         'CZ Ortofoto - CIR infracervene (WMS)': 'geoportal.cuzk.gov.cz',
         'CZ RUIAN - Ucelove uzemni prvky (WMS)': 'services.cuzk.gov.cz',
         'CZ Topo - Data50 (WMS)': 'ags.cuzk.gov.cz',
         'CZ Topo - Prehledova mapa (WMTS)': 'ags.cuzk.gov.cz',
         'CZ Topo - Zakladni topograficke mapy ZTM (WMTS)': 'ags.cuzk.gov.cz',
         'CZ Topo - ZTM 1-10000 (WMTS)': 'ags.cuzk.gov.cz',
         'CZ Topo - ZTM 1-100000 (WMTS)': 'ags.cuzk.gov.cz',
         'CZ Topo - ZTM 1-25000 (WMTS)': 'ags.cuzk.gov.cz',
         'CZ Topo - ZTM 1-5000 (WMTS)': 'ags.cuzk.gov.cz',
         'CZ Topo - ZTM 1-50000 (WMTS)': 'ags.cuzk.gov.cz',
         'SK ESKN - Kataster nad ortofotom (WMS)': 'kataster.skgeodesy.sk',
         'SK ESKN - Kataster nad ortofotom Web Mercator (WMTS)': 'kataster.skgeodesy.sk',
         'SK ESKN - Kataster Web Mercator (WMTS)': 'kataster.skgeodesy.sk',
         'SK ESKN - Katastrálna mapa (WMS)': 'kataster.skgeodesy.sk',
         'SK ESKN - Mapa určeného operátu (WMS)': 'kataster.skgeodesy.sk',
         'SK GKU - Administratívna mapa SR raster (WMS)': 'zbgisws.skgeodesy.sk',
         'SK GKU - Historická mapa III. vojenského mapovania (WMS)': 'zbgisws.skgeodesy.sk',
         'SK GKU - Klady mapových listov (WMS)': 'zbgisws.skgeodesy.sk',
         'SK GKU - Topografické mapy RETM raster (WMS)': 'zbgisws.skgeodesy.sk',
         'SK GKU - Základné mapy SR raster (WMS)': 'zbgisws.skgeodesy.sk',
         'SK ZBGIS - Administratívne hranice (WMS)': 'zbgisws.skgeodesy.sk',
         'SK ZBGIS - Digitálny model reliéfu DMR 5.0 (WMS)': 'zbgisws.skgeodesy.sk',
         'SK ZBGIS - Geografické názvy (WMS)': 'zbgisws.skgeodesy.sk',
         'SK ZBGIS - Ortofotomozaika S-JTSK (WMTS)': 'zbgisws.skgeodesy.sk',
         'SK ZBGIS - Ortofotomozaika SR (WMS)': 'zbgisws.skgeodesy.sk',
         'SK ZBGIS - Vodstvo (WMS)': 'zbgisws.skgeodesy.sk',
         'SK ZBGIS - Výškopis (WMS)': 'zbgisws.skgeodesy.sk',
         'SK ZBGIS - Základná mapa (WMS)': 'zbgisws.skgeodesy.sk',
         'SK ZBGIS - Základná mapa S-JTSK (WMTS)': 'zbgisws.skgeodesy.sk'},
 'wfs': {'CZ AOPK - Chranena uzemi, opendata (WFS)': 'gis.nature.cz',
         'CZ WFS - Adresy INSPIRE AD': 'services.cuzk.gov.cz',
         'CZ WFS - Budovy INSPIRE BU': 'services.cuzk.gov.cz',
         'CZ WFS - Katastralni mapa rozsirena CPX': 'services.cuzk.gov.cz',
         'CZ WFS - Katastralni parcely INSPIRE CP': 'services.cuzk.gov.cz',
         'CZ WFS - Spravni jednotky INSPIRE AU': 'services.cuzk.gov.cz',
         'CZ WFS - Zaznamy podrobneho mereni zmen ZPMZ': 'services.cuzk.gov.cz',
         'SK WFS - Administratívne hranice (ÚGKK)': 'zbgisws.skgeodesy.sk',
         'SK WFS - Geografické názvoslovie (ÚGKK)': 'zbgisws.skgeodesy.sk'},
 'arcgis': {'CZ AOPK - Chranena uzemi a opendata (ArcGIS REST)': 'gis.nature.cz',
            'CZ AOPK - Uzemi ochrany prirody': 'gis.nature.cz',
            'CZ CGS - Geologicka mapa 1-25000 odkryta': 'mapy.geology.cz',
            'CZ CGS - Geologicka mapa 1-25000 zakryta': 'mapy.geology.cz',
            'CZ CGS - Geologicka mapa 1-50000': 'mapy.geology.cz',
            'CZ CGS - Geologicka mapa 1-500000': 'mapy.geology.cz',
            'CZ CGS - Historicke geologicke mapy 1-144000': 'mapy.geology.cz',
            'CZ CGS - Historicke geologicke mapy 1-28800': 'mapy.geology.cz',
            'CZ CGS - Hydrogeologicka mapa 1-50000': 'mapy.geology.cz',
            'CZ CGS - Nerostne suroviny SurIS': 'mapy.geology.cz',
            'CZ CGS - Pudy - pudni typy 1-50000': 'mapy.geology.cz',
            'CZ CGS - Sesuvy Geofond': 'mapy.geology.cz',
            'CZ CGS - Vrtna prozkoumanost': 'mapy.geology.cz',
            'CZ Topo - Prehledova mapa ArcGIS REST': 'ags.cuzk.gov.cz',
            'CZ Topo - ZTM ArcGIS REST': 'ags.cuzk.gov.cz',
            'SK Atlas krajiny - Rastrové podklady': 'arc.sazp.sk',
            'SK Atlas krajiny - Tematické mapy prírody': 'arc.sazp.sk',
            'SK Atlas krajiny - Vektorové mapové podklady': 'arc.sazp.sk',
            'SK Bratislava - Cyklotrasy': 'geoportal.bratislava.sk',
            'SK Bratislava - Funkčné plochy': 'geoportal.bratislava.sk',
            'SK Bratislava - Linky MHD': 'geoportal.bratislava.sk',
            'SK Bratislava - Územný plán - Funkčné využitie': 'geoportal.bratislava.sk',
            'SK Geológia - Geologická mapa SR 1-200 000': 'ags.geology.sk',
            'SK Geológia - Geologická mapa SR 1-50 000': 'ags.geology.sk',
            'SK Geológia - Radónové riziko': 'ags.geology.sk',
            'SK Lesy - Druhové zloženie lesa': 'gis.nlcsk.org',
            'SK Lesy - Hranice lesných porastov (JPRL)': 'gis.nlcsk.org',
            'SK Lesy - Lesné cesty a komunikácie': 'gis.nlcsk.org',
            'SK Lesy - Lesné pôdne jednotky': 'gis.nlcsk.org',
            'SK Pôda - Bonitované pôdno-ekologické jednotky BPEJ': 'portal.vupop.sk',
            'SK SHMÚ - Hlavné povodia 1-50 000': 'arcgis.shmu.sk',
            'SK SHMÚ - Podrobné povodia 1-50 000': 'arcgis.shmu.sk',
            'SK Životné prostredie - Biocentrá a biokoridory RÚSES': 'arc.sazp.sk',
            'SK Životné prostredie - Environmentálne záťaže': 'arc.sazp.sk'},
 'legacy2021': {'Bing VirtualEarth': 'ecn.t3.tiles.virtualearth.net',
                'CartoDb Dark Matter': 'basemaps.cartocdn.com',
                'CartoDb Positron': 'basemaps.cartocdn.com',
                'Esri Boundaries Places': 'server.arcgisonline.com',
                'Esri Gray (dark)': 'services.arcgisonline.com',
                'Esri Gray (light)': 'services.arcgisonline.com',
                'Esri National Geographic': 'services.arcgisonline.com',
                'Esri Ocean': 'services.arcgisonline.com',
                'Esri Satellite': 'server.arcgisonline.com',
                'Esri Standard': 'server.arcgisonline.com',
                'Esri Terrain': 'server.arcgisonline.com',
                'Esri Topo World': 'services.arcgisonline.com',
                'Esri Transportation': 'server.arcgisonline.com',
                'Google Maps': 'mt1.google.com',
                'Google Satellite': 'mt1.google.com',
                'Google Satellite Hybrid': 'mt1.google.com',
                'Google Terrain': 'mt1.google.com',
                'Google Terrain Hybrid': 'mt1.google.com',
                'Open Weather Map Clouds': 'tile.openweathermap.org',
                'Open Weather Map Temperature': 'tile.openweathermap.org',
                'Open Weather Map Wind Speed': 'tile.openweathermap.org',
                'OpenStreetMap H.O.T.': 'tile.openstreetmap.fr',
                'OpenStreetMap Monochrome': 'tiles.wmflabs.org',
                'OpenStreetMap Standard': 'tile.openstreetmap.org',
                'Stamen Terrain': 'tile.stamen.com',
                'Stamen Toner': 'tile.stamen.com',
                'Stamen Toner Light': 'tile.stamen.com',
                'Stamen Watercolor': 'tile.stamen.com',
                'Strava All': 'heatmap-external-b.strava.com',
                'Strava Run': 'heatmap-external-b.strava.com',
                'Wikimedia Hike Bike Map': 'tiles.wmflabs.org',
                'Wikimedia Map': 'maps.wikimedia.org'}}

BASE_PATHS = {'arcgis': 'connections/arcgisfeatureserver/items/',
 'legacy2021': 'qgis/connections-xyz/',
 'wfs': 'connections/ows/items/wfs/connections/items/',
 'wms': 'connections/ows/items/wms/connections/items/',
 'xyz': 'connections/xyz/items/'}


def _settings(kind):
    return QSettings() if kind in ('xyz', 'legacy2021') else QgsSettings()


def _to_json_safe(value):
    """Backup-friendly representation of QSettings values."""
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, (bytes, bytearray)):
        return {'__bytes_base64__': base64.b64encode(bytes(value)).decode('ascii')}
    if isinstance(value, (list, tuple)):
        return [_to_json_safe(v) for v in value]
    if isinstance(value, dict):
        return {str(k): _to_json_safe(v) for k, v in value.items()}
    try:
        return {'__bytes_base64__': base64.b64encode(bytes(value)).decode('ascii')}
    except Exception:
        return str(value)


def _get_snapshot(settings, key):
    """Read all values for one connection without altering the settings."""
    settings.beginGroup(key)
    try:
        values = {item: _to_json_safe(settings.value(item))
                  for item in settings.allKeys()}
    finally:
        settings.endGroup()
    return values


def _hostname_ok(url, expected):
    """Match domain or suffix for dynamic Bing metadata subdomains."""
    actual = (urlsplit(str(url)).hostname or '').casefold()
    target = expected.casefold()
    if target.startswith('.'):
        return actual.endswith(target)
    return actual == target


def gather_candidates():
    found = []
    skipped = []
    for kind, candidates in CANDIDATES.items():
        if kind == 'legacy2021' and not REMOVE_LEGACY_2021:
            continue
        settings = _settings(kind)
        for name, expected_host in candidates.items():
            group = BASE_PATHS[kind] + name
            if not settings.contains(group + '/url'):
                continue
            url = settings.value(group + '/url', '')
            if PROTECT_CHANGED_URLS and not _hostname_ok(url, expected_host):
                skipped.append((kind, name, expected_host))
                continue
            snapshot = _get_snapshot(settings, group)
            if snapshot:
                found.append({
                    'type': kind,
                    'name': name,
                    'group': group,
                    'values': snapshot,
                })
    return found, skipped


def save_backup(found):
    """Backup is mandatory; any failure aborts removal."""
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S_%fZ')
    backup_path = BACKUP_DIR / ('gis_lab_connections_before_remove_' + stamp + '.json')
    content = {
        'format': 'GIS-LAB QGIS connections backup v1',
        'created_utc': datetime.now(timezone.utc).isoformat(),
        'important': 'May contain API keys or passwords. Keep this backup private.',
        'connections': found,
    }
    # Exclusive create: never replace an older backup.
    with backup_path.open('x', encoding='utf-8') as handle:
        json.dump(content, handle, ensure_ascii=False, indent=2)
    return backup_path


def main():
    found, skipped = gather_candidates()
    tally = Counter(entry['type'] for entry in found)
    print('\n=== GIS-LAB: KONTROLA MAPOVYCH PRIPOJENI ===')
    print('Naslo sa na odstranenie:', len(found))
    for kind in ('xyz', 'wms', 'arcgis', 'wfs', 'legacy2021'):
        print('  %s: %s' % (kind, tally[kind]))
    if skipped:
        print('\nPRESKOCENE: rovnaky nazov, ale ina domena (%s):' % len(skipped))
        for kind, name, _ in skipped:
            print(' - %s / %s' % (kind, name))

    if not found:
        print('Nenasli sa ziadne vhodne pripojenia. Nic sa nemeni.')
        return

    if REQUIRE_CONFIRMATION:
        text = (
            'Odstranit %s mapovych pripojeni GIS-LAB?\\n\\n'
            'XYZ: %s | WMS/WMTS: %s | ArcGIS REST: %s | WFS: %s | Stare 2021: %s\\n\\n'
            'Najprv sa automaticky ulozi zaloha nastaveni do lokalneho priecinka.\\n'
            'Ostatne mapove a databazove pripojenia zostanu zachovane.\\n'
            'Vrstvy uz nacitane v projekte sa neodstrania.'
        ) % (len(found), tally['xyz'], tally['wms'], tally['arcgis'],
               tally['wfs'], tally['legacy2021'])
        result = QMessageBox.question(
            iface.mainWindow(), 'GIS-LAB - odstranit mapove spojenia', text,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if result != QMessageBox.StandardButton.Yes:
            print('Zrusene pouzivatelom - nic nebolo odstranene.')
            return

    try:
        backup_path = save_backup(found)
    except Exception as exc:
        print('CHYBA: Nepodarilo sa vytvorit zalohu, mazanie sa NEVYKONALO:', exc)
        return

    removed = Counter()
    errors = []
    for entry in found:
        try:
            settings = _settings(entry['type'])
            settings.remove(entry['group'])
            settings.sync()
            # Verify, including cases where QGIS settings backend rejects a write.
            if settings.contains(entry['group'] + '/url'):
                raise RuntimeError('Nastavenie URL zostalo v profile aj po odstraneni.')
            removed[entry['type']] += 1
            print('REMOVED: %s / %s' % (entry['type'], entry['name']))
        except Exception as exc:
            errors.append((entry['name'], str(exc)))
            print('ERROR:', entry['name'], exc)

    QSettings().sync()
    QgsSettings().sync()
    iface.reloadConnections()
    print('\n=== VYSLEDOK ===')
    print('Odstranene:', sum(removed.values()))
    print('Chyby:', len(errors))
    print('Zaloha:', backup_path)
    print('Projektove vrstvy .qgs/.qgz sa nemenia.')
    print('Zaloha moze obsahovat API kluce; nezverejnujte ju.')
    if errors:
        print('Pripojenia s chybou skontrolujte v QGIS Browseri.')
    else:
        print('Hotovo. Ak Browser stale zobrazuje stare polozky, obnovte ho.')


# QGIS Python Console Editor nemusi pouzivat __name__ == '__main__'.
# Preto volame main() aj pri spusteni cez tlacidlo Run Script.
main()
