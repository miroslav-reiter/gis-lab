# 🗺️ GIS Lab – Geografické Informačné Systémy (QGIS, ArcGIS, PostGIS)

Testovací a vzdelávací repozitár na praktické precvičovanie **GIS (Geographic Information Systems – geografických informačných systémov)** v prostredí **QGIS, ArcGIS, PostgreSQL/PostGIS, GDAL/OGR a Python (PyQGIS)**.

Repozitár slúži ako študijná základňa pre online kurzy GIS: od mapových vrstiev, priestorových súradníc a súborových formátov až po **analýzu priestorových dát, automatizáciu, databázy a pripojenie online máp**. Praktické príklady sú orientované najmä na **Microsoft Windows** a používateľov QGIS.

**Zameranie:** GIS · QGIS · ArcGIS · PyQGIS · PostGIS · PostgreSQL · GDAL · OGR · GeoPackage · GeoJSON · GeoTIFF · OpenStreetMap · XYZ Tiles · WMS · WMTS · Mapy.com · Google Maps · Azure Maps

> 📌 **Stav repozitára:** Tento dokument predstavuje učebný prehľad a návody. Štruktúra priečinkov a názvy dátových súborov uvedené nižšie sú **návrhom**; neznamená to, že všetky už boli nahrané do repozitára.

## 📑 Obsah

- [Čo je GIS](#-čo-je-gis)
- [Ako GIS funguje](#-ako-gis-funguje)
- [QGIS vs. ArcGIS vs. PostGIS](#-qgis-vs-arcgis-vs-postgis)
- [Vektorové a rastrové dáta](#-vektorové-a-rastrové-dáta)
- [Súradnicové referenčné systémy a EPSG](#-súradnicové-referenčné-systémy-a-epsg)
- [Inštalácia a nástroje pre Windows](#-inštalácia-a-nástroje-pre-windows)
- [Navrhovaná štruktúra repozitára](#-navrhovaná-štruktúra-repozitára)
- [Online mapové podklady a XYZ Tiles](#-online-mapové-podklady-a-xyz-tiles)
- [Python a automatizácia v QGIS](#-python-a-automatizácia-v-qgis)
- [GDAL a OGR – praktické príkazy](#-gdal-a-ogr--praktické-príkazy)
- [PostgreSQL a PostGIS](#-postgresql-a-postgis)
- [Praktické cvičenia](#-praktické-cvičenia)
- [GIS cheat sheet](#-gis-cheat-sheet)
- [Typické chyby a riešenia](#-typické-chyby-a-riešenia)
- [Bezpečnosť, licencie a atribúcia](#-bezpečnosť-licencie-a-atribúcia)
- [Užitočné odkazy a zdroje](#-užitočné-odkazy-a-zdroje)

## 🌍 Čo je GIS

**GIS (Geographic Information System)** je systém na **zber, ukladanie, správu, analýzu a vizualizáciu údajov, ktoré majú priestorovú polohu**. Kombinuje mapu, databázu, geometriu objektov, súradnicové systémy a nástroje na priestorové operácie.

Na mape preto nevidíme iba obrázok územia. Pracujeme aj s údajmi o cestách, budovách, parcelách, obyvateľstve, výške terénu alebo dostupnosti služieb.

### 🧠 Základné pojmy

| Pojem | Význam | Praktický príklad |
|---|---|---|
| GIS | Systém na prácu s priestorovými dátami | QGIS, ArcGIS |
| Vrstva (Layer) | Súbor priestorových objektov alebo rastrových údajov | Cesty, obce, ortofotomapa |
| Prvok (Feature) | Jednotlivý objekt vo vektorovej vrstve | Jedna budova |
| Geometria (Geometry) | Priestorový tvar objektu | Bod, línia, polygón |
| Atribút (Attribute) | Opisný údaj objektu | Názov obce, počet obyvateľov |
| CRS | Súradnicový referenčný systém | EPSG:4326 |
| SRID | Identifikátor referenčného systému v databáze | `4326` v PostGIS |
| Geoprocessing | Priestorové operácie nad údajmi | Buffer, Clip, Intersection |
| Georeferencovanie | Priradenie súradníc obrázku alebo skenu | Digitalizovaná historická mapa |
| Geokódovanie | Prevod adresy na súradnice | Adresa → bod na mape |

### ⚙️ Ako GIS funguje

Typický GIS workflow:

1. **Získame dáta** – GPS, open data, databáza, GeoJSON, GeoPackage alebo mapová služba.
2. **Určíme ich polohu a CRS** – skontrolujeme súradnice a správny referenčný systém.
3. **Načítame vrstvy** – zobrazíme vektorové a rastrové údaje.
4. **Spracujeme a analyzujeme dáta** – priestorové filtre, buffery, vzdialenosti, prieniky.
5. **Vizualizujeme výsledky** – štýly, popisy, tematické mapy, mapové rozloženie.
6. **Exportujeme výstup** – GeoPackage, GeoJSON, PDF, obrázok alebo databázovú tabuľku.

## 🧩 QGIS vs. ArcGIS vs. PostGIS

| Technológia | Typ | Hlavné využitie | Licencovanie |
|---|---|---|---|
| **QGIS** | Desktop GIS | Mapy, analýzy, geoprocessing, PyQGIS | Open source |
| **ArcGIS Pro** | Desktop GIS | Mapová tvorba, analytické nástroje, ArcPy | Komerčné licencie Esri |
| **ArcGIS Online** | Cloud GIS | Webové mapy, zdieľanie vrstiev a aplikácií | Podľa účtu a plánu Esri |
| **PostgreSQL + PostGIS** | Priestorová databáza | Ukladanie, indexovanie a SQL analýza geometrií | Open source |
| **pgAdmin** | Administrácia PostgreSQL | Databázy, SQL editor, správa tabuliek | Open source |
| **GDAL/OGR** | Knižnice a CLI nástroje | Konverzie, raster/vector processing | Open source |

**Dôležité:** QGIS a ArcGIS sú primárne GIS aplikácie. **PostGIS je rozšírenie databázy PostgreSQL**, nie samostatný mapový editor. **pgAdmin je administračné rozhranie PostgreSQL** a samo osebe nenahrádza PostGIS.

### 🔁 Typický GIS workflow

```text
Zdrojové údaje (GeoJSON / SHP / GPKG / GeoTIFF / API)
                          |
                          v
                 QGIS / ArcGIS Pro
                          |
          +---------------+----------------+
          |                                |
          v                                v
  GDAL/OGR / Python                PostgreSQL + PostGIS
  konverzia a spracovanie          SQL a priestorové indexy
          |                                |
          +---------------+----------------+
                          |
                          v
             Mapa / PDF / GeoPackage
```

## 🧱 Vektorové a rastrové dáta

### 📍 Vektorové dáta

Vektorové dáta reprezentujú objekty pomocou súradníc a geometrie:

- **Bod (Point)** – zastávka, škola, meteorologická stanica.
- **Línia (LineString)** – cesta, rieka, trasa.
- **Polygón (Polygon)** – parcela, okres, jazero.

Výhodou je možnosť pracovať s jednotlivými objektmi a ich atribútmi.

### 🛰️ Rastrové dáta

Raster je mriežka buniek (pixelov) s hodnotami alebo farbami. Používame ho pre satelitné a letecké snímky, digitálne modely reliéfu, teplotné mapy alebo klasifikované povrchy.

| Formát | Typ | Charakteristika |
|---|---|---|
| `*.gpkg` | Vektor / prípadne raster | GeoPackage, vhodný na prenos a ukladanie viacerých vrstiev |
| `*.shp` | Vektor | Shapefile, starší viac-súborový formát |
| `*.geojson` | Vektor | JSON s geometriami, vhodný na výmenu dát |
| `*.kml` / `*.kmz` | Vektor / kontajner | Geografické vrstvy známe z Google Earth |
| `*.tif` / `*.tiff` | Raster | GeoTIFF, typicky snímky alebo výškové modely |
| `*.vrt` | Virtuálny dataset | Odkazy na iné rastrové či vektorové zdroje |
| `*.qgz` | Projekt QGIS | Konfigurácia projektu, vrstiev a štýlov, nie kompletný dataset |
| `*.aprx` | Projekt ArcGIS Pro | Projekt ArcGIS Pro, nie automaticky všetky zdrojové dáta |

### ⚠️ Shapefile nie je jediný súbor

Pri prenose Shapefile musíme zachovať súvisiace súbory. Bežná zostava:

```text
obce.shp   # geometria
obce.shx   # index geometrie
obce.dbf   # atribúty
obce.prj   # informácia o CRS
obce.cpg   # kódovanie textu, ak je prítomné
```

Na nové projekty často uprednostňujeme **GeoPackage (`.gpkg`)**.

## 🧭 Súradnicové referenčné systémy a EPSG

**CRS (Coordinate Reference System)** definuje, ako súradnice súvisia s polohou na Zemi. Priestorové vrstvy nemusia používať rovnaký CRS, ale pri kombinovaní a meraní musíme správne pracovať s ich transformáciami.

| CRS | Označenie | Typické využitie |
|---|---|---|
| `EPSG:4326` | WGS 84 | Zemepisná dĺžka a šírka v stupňoch, GPS |
| `EPSG:3857` | WGS 84 / Pseudo-Mercator | Bežné webové mapy a XYZ dlaždice |
| `EPSG:5514` | S-JTSK / Krovak East North | Priestorové dáta v SR/ČR, vhodný projektovaný CRS pre regionálnu analýzu |
| `EPSG:32633` | WGS 84 / UTM zone 33N | Vybrané lokality v zóne UTM 33N |

### 📌 Rozdiel medzi nastavením CRS a transformáciou

- **Assign/Set CRS**: označíme, aké súradnice dáta už majú; ich číselné hodnoty sa nemenia.
- **Reproject/Transform**: hodnoty súradníc sa skutočne prepočítajú do iného CRS.

Ak body ležia mimo očakávaného miesta, najskôr skontrolujeme, či sme **nesprávne nepriradili CRS**. Samotné prepnutie CRS projektu chybný zdrojový CRS neopraví.

### ⚠️ Meranie vzdialeností

Hodnoty geometrie v `EPSG:4326` sú v **stupňoch**, nie v metroch. Ak potrebujeme metrické vzdialenosti a plochy, použijeme vhodný projektovaný CRS alebo v PostGIS dátový typ `geography`.

## 🪟 Inštalácia a nástroje pre Windows

### 1. QGIS

Oficiálne stiahnutie: https://qgis.org/download/

Po inštalácii overíme funkčnosť:

1. Spustíme **QGIS**.
2. Otvoríme panel **Browser** a položku **XYZ Tiles**.
3. Vytvoríme testovací projekt.
4. Overíme, že je možné načítať mapovú vrstvu.

Pre prácu so skriptmi používame **Python Console integrovanú priamo v QGIS**. Samostatný systémový Python spravidla neobsahuje knižnice `qgis` ani zodpovedajúce prostredie QGIS.

### 2. ArcGIS Pro

Oficiálna stránka: https://www.esri.com/en-us/arcgis/products/arcgis-pro/overview

ArcGIS Pro je proprietárna aplikácia Esri pre Windows. Používanie môže vyžadovať vhodné predplatné alebo licenciu. Automatizáciu v rámci ekosystému ArcGIS riešime spravidla cez **ArcPy**.

### 3. PostgreSQL, PostGIS a pgAdmin

- PostgreSQL: https://www.postgresql.org/download/windows/
- PostGIS: https://postgis.net/
- pgAdmin: https://www.pgadmin.org/

PostGIS nainštalujeme pre konkrétnu inštanciu PostgreSQL a následne ho **aktivujeme v každej databáze, v ktorej ho chceme používať**.

### 4. GDAL/OGR

GDAL je dostupný aj v prostredí QGIS. Na Windows môžeme používať **OSGeo4W Shell** dodaný s príslušnou inštaláciou alebo samostatnú kompatibilnú inštaláciu GDAL.

```powershell
gdalinfo --version
ogrinfo --version
ogr2ogr --version
```

> Príkazy musíme spúšťať v prostredí, v ktorom sú nástroje GDAL dostupné cez `PATH`.

## 📁 Navrhovaná štruktúra repozitára

Nasledujúca štruktúra je **odporúčaný návrh pre ďalšie rozšírenie**, nie výpis súčasného obsahu GitHub repozitára.

```text
gis-lab/
├── README.md
├── scripts/
│   ├── qgis_basemaps_qgis_4_2_3_complete.py
│   └── pyqgis_examples.py
├── data/
│   ├── sample.geojson
│   └── sample.gpkg
├── sql/
│   └── postgis_examples.sql
├── notebooks/
├── maps/
├── images/
└── docs/
```

**Odporúčania:** malé testovacie datasety možno verzovať v Gite; veľké rastre, databázové výpisy, osobné údaje a tajné API kľúče do verejného repozitára nepatria. Pri veľkých dátach zvážime Git LFS alebo odkazy na ich pôvodný zdroj.

## 🗺️ Online mapové podklady a XYZ Tiles

**XYZ Tiles** sú mapové dlaždice poskytované serverom podľa úrovne priblíženia (`z`) a pozície dlaždice (`x`, `y`). QGIS ich spojí do mapového podkladu.

```text
https://server.example.com/{z}/{x}/{y}.png
```

Kde:
- `{z}` = zoom level, úroveň priblíženia;
- `{x}` = stĺpec dlaždice;
- `{y}` = riadok dlaždice;
- `{q}` = **quadkey**, alternatívne kódovanie dlaždice typické pre Bing Maps.

### 🌐 Prehľad poskytovateľov

| Poskytovateľ | Príklady vrstiev | API kľúč | Poznámka |
|---|---|---|---|
| OpenStreetMap | Standard | Nie pre verejný tile endpoint | Nutné dodržať tile usage policy |
| Esri | Satellite, Standard, Topo, Terrain | Závisí od služby a podmienok | Dostupnosť a práva na použitie sa líšia |
| CARTO | Positron, Dark Matter | Podľa používania/služby | Nutná atribúcia dát a mapového štýlu |
| Google | Maps, Satellite, Hybrid, Terrain | Neoficiálne XYZ URL bez kľúča | Nedokumentované endpointy, nie oficiálne Google Maps Platform API |
| Mapy.com / Seznam | Basic, Outdoor, Aerial, Winter, Names Overlay | Áno | Logo a copyright sú povinné |
| Bing Maps | Aerial, Road | Áno, oprávnený Enterprise účet | Basic bol vyradený, Enterprise končí v roku 2028 |
| Azure Maps | Road, Imagery, Hybrid | Áno | Oficiálna náhrada Microsoftu za Bing |
| Stadia Maps | Stamen Terrain, Toner, Watercolor | Typicky áno | Nástupca pôvodných Stamen tile serverov |
| OpenWeatherMap | Temperature, Clouds, Wind | Áno | Dostupnosť závisí od API a tarify |

**Rozlišujeme dostupnosť servera, licenciu a podporované API.** To, že sa dlaždica technicky načíta do QGIS, ešte neznamená, že ju môžeme ľubovoľne publikovať alebo hromadne sťahovať.

### 🧪 Ručné pridanie OpenStreetMap do QGIS

V paneli **Browser → XYZ Tiles** klikneme pravým tlačidlom na **New Connection** a vyplníme:

| Nastavenie | Hodnota |
|---|---|
| Name | `OpenStreetMap Standard` |
| URL | `https://tile.openstreetmap.org/{z}/{x}/{y}.png` |
| Minimum zoom | `0` |
| Maximum zoom | `19` |

Následne otvoríme vytvorené pripojenie alebo ho potiahneme na mapové plátno.

### 🌍 Google Maps – neoficiálne XYZ príklady

Tieto URL sa často používajú na testovanie, **nejde však o dokumentované verejné Google Maps XYZ API**. Ich funkčnosť sa môže zmeniť a použitie podlieha pravidlám spoločnosti Google.

```text
Google Maps:
https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}

Google Satellite:
https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}

Google Satellite Hybrid:
https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}

Google Terrain:
https://mt1.google.com/vt/lyrs=t&x={x}&y={y}&z={z}
```

Pre oficiálnu integráciu používame **Google Maps Platform – Map Tiles API**, ktoré vyžaduje projekt, fakturačné nastavenie, API kľúč a pri príslušných 2D dlaždiciach aj časovo obmedzený session token.

### 🧭 Mapy.com / Seznam – oficiálne API

Príklad formátu mapovej URL:

```text
https://api.mapy.com/v1/maptiles/basic/256/{z}/{x}/{y}?apikey=VAS_API_KLUC
```

| Mapset | Využitie |
|---|---|
| `basic` | Základná mapa |
| `outdoor` | Turistické a outdoorové mapy |
| `aerial` | Letecké snímky |
| `names-overlay` | Priehľadné popisy a hranice nad leteckou mapou |
| `winter` | Zimná mapa |

**Mapy.com Aerial** a **Mapy.com Names Overlay** môžeme vložiť ako dve vrstvy s overlay vrstvou **nad leteckou mapou**. Nezabúdame, že ručné XYZ pripojenie v QGIS automaticky nerieši všetky požiadavky na logo a autorskú atribúciu Mapy.com.

API kľúč získame na https://developer.mapy.com/.

### 🪟 Bing Maps a Azure Maps

Historické Bing Maps používali aj **quadkey `{q}`**. Pri novom projekte však uprednostňujeme **Azure Maps**. Bing Maps Basic je vyradený a dostupnosť Bing Maps Enterprise je časovo obmedzená do **30. júna 2028**.

Pri Bing Enterprise skript získava aktuálnu URL pomocou **Imagery Metadata API** namiesto pevne zapísanej starej URL. Azure Maps používa vlastné API a predplatiteľský kľúč. Azure Maps navyše vyžaduje zobrazenie atribúcie získanej cez príslušné API.

### ⚙️ XYZ vs. WMS vs. WMTS vs. WFS

| Služba | Čo poskytuje | Typické využitie |
|---|---|---|
| `XYZ` | Dlaždice určené súradnicami `z/x/y` | Podkladové webové mapy |
| `WMS` | Serverom vykreslený mapový obraz | Zobrazenie tematických vrstiev |
| `WMTS` | Predpripravené mapové dlaždice podľa štandardu OGC | Výkonné mapové podklady |
| `WFS` | Geografické objekty a ich atribúty | Práca s vektorovými údajmi |
| `OGC API – Features` | Webové API pre geopriestorové objekty | Moderné sprístupnenie priestorových dát |

**Pozor:** XYZ, WMS a WMTS zvyčajne neposkytujú vektorové geometrie na priamu editáciu. Ak potrebujeme analyzovať jednotlivé objekty, použijeme vektorový zdroj alebo príslušné dátové API.

## 🐍 Python a automatizácia v QGIS

QGIS poskytuje **PyQGIS** – Python API na načítanie vrstiev, prácu s geometriou, analýzu dát a automatizáciu GIS úloh.

### ▶️ Spustenie importného skriptu pre QGIS 4.2.3

Skript pripravovaný k tomuto GIS laboratóriu má názov:

```text
qgis_basemaps_qgis_4_2_3_complete.py
```

**Poznámka:** Súbor skriptu treba do repozitára nahrať samostatne; jeho prítomnosť tu nepredpokladáme.

V QGIS pre Windows otvoríme:

```text
Plugins → Python Console → Show Editor
        → Open Script → Run Script
```

Alternatívne môžeme v Python Console spustiť súbor z absolútnej cesty:

```python
from pathlib import Path

script = Path(r"C:\GIS\qgis_basemaps_qgis_4_2_3_complete.py")
exec(compile(script.read_text(encoding="utf-8"), str(script), "exec"))
```

Cestu upravíme podľa skutočného umiestnenia súboru.

### 🔑 Konfigurácia pripojení

V skripte nastavujeme služby a prípadné vlastné kľúče:

```python
ENABLE_GOOGLE_LEGACY = True

MAPY_API_KEY = ""
MAPY_LANGUAGE = "sk"

BING_MAPS_KEY = ""
AZURE_MAPS_KEY = ""
STADIA_API_KEY = ""
OPENWEATHER_API_KEY = ""
```

Prázdne kľúče znamenajú, že príslušné služby skript preskočí. Pri niektorých poskytovateľoch môžeme naraziť aj na neplatný kľúč, vyčerpanú kvótu, zmenený endpoint alebo licenčné obmedzenie.

> 🔒 **Do verejného GitHub repozitára nikdy necommitujeme osobné API kľúče.** Ak pracujeme s verejným repozitárom, používame lokálnu konfiguráciu, ktorú Git ignoruje, alebo vhodnú správu tajomstiev. Pozor aj na uloženie API kľúča v URL pripojenia, exportoch nastavení, logoch a súboroch projektu.

### ⚙️ Ako skript registruje XYZ zdroje

V QGIS 4.x môžeme pracovať s nastaveniami pripojení cez `QSettings`:

```python
from qgis.PyQt.QtCore import QSettings
from qgis.utils import iface

name = "OpenStreetMap Standard"
url = "https://tile.openstreetmap.org/{z}/{x}/{y}.png"

settings = QSettings()
base = f"connections/xyz/items/{name}"

settings.setValue(f"{base}/url", url)
settings.setValue(f"{base}/zmin", 0)
settings.setValue(f"{base}/zmax", 19)
settings.sync()

iface.reloadConnections()
```

Tento príklad spúšťame **v integrovanej Python Console v QGIS**; nie ako samostatný Python program bez inicializácie QGIS.

### 🧪 Pridanie rasterovej XYZ vrstvy pomocou PyQGIS

```python
from qgis.core import QgsProject, QgsRasterLayer

uri = (
    "type=xyz&url=https://tile.openstreetmap.org/{z}/{x}/{y}.png"
    "&zmin=0&zmax=19"
)

layer = QgsRasterLayer(uri, "OSM – test", "wms")

if layer.isValid():
    QgsProject.instance().addMapLayer(layer)
    print("Vrstva bola pridaná.")
else:
    print("Načítanie XYZ vrstvy zlyhalo.")
```

Názov poskytovateľa `wms` je pri tomto spôsobe načítania XYZ vrstvy v QGIS historicky používaný **GDAL/QGIS provider identifikátor**, nie tvrdenie, že zdroj je skutočná WMS služba.

## 🛠️ GDAL a OGR – praktické príkazy

**GDAL** používame na spracovanie rastrov a priestorových formátov. Nástroje **OGR** z tej istej knižnice slúžia najmä na prácu s vektorovými údajmi.

### 🧪 Kontrola inštalácie

```powershell
gdalinfo --version
ogrinfo --version
```

### 📋 Informácie o rastri

```powershell
gdalinfo "data\vyska_terenu.tif"
```

### 📋 Informácie o vektorovom datasete

```powershell
ogrinfo -al -so "data\obce.gpkg"
```

### 🔁 Konverzia GeoJSON na GeoPackage

```powershell
ogr2ogr -f GPKG "data\obce.gpkg" "data\obce.geojson"
```

### 🌍 Reprojekcia vektorových údajov

```powershell
ogr2ogr -f GPKG -t_srs EPSG:5514 "data\obce_5514.gpkg" "data\obce.gpkg"
```

### 🖼️ Reprojekcia rastra

```powershell
gdalwarp -t_srs EPSG:3857 "data\vstup.tif" "data\vystup_3857.tif"
```

**Poznámka:** Názvy súborov v príkladoch sú ukážkové. Pred spustením musíme vytvoriť príslušné súbory alebo nahradiť cesty vlastnými dátami.

## 🗄️ PostgreSQL a PostGIS

**PostGIS** pridáva databáze PostgreSQL priestorové typy, funkcie a indexy. Umožňuje realizovať GIS analýzy pomocou **SQL dopytov** bez nutnosti držať všetky dáta priamo v QGIS projekte.

### ⚙️ Aktivácia PostGIS v pgAdmin

1. V pgAdmin sa pripojíme k PostgreSQL serveru.
2. Vyberieme konkrétnu databázu.
3. Otvoríme **Query Tool**.
4. Spustíme:

```sql
CREATE EXTENSION IF NOT EXISTS postgis;

SELECT PostGIS_Full_Version();
```

Na vytvorenie rozšírenia potrebujeme zodpovedajúce oprávnenia a PostGIS musí byť nainštalovaný na serveri.

### 🧠 `geometry` vs. `geography`

| Dátový typ | Súradnice a meranie | Typické využitie |
|---|---|---|
| `geometry` | Pracuje v jednotkách použitého SRID/CRS | GIS operácie, priestorové indexy, lokálne analýzy |
| `geography` | Zemepisné súradnice, vzdialenosť spravidla v metroch | Metrické vzdialenosti na zemskom povrchu |

### 📍 Praktický príklad – body a vzdialenosť

```sql
-- Testovacia tabuľka bodov vo WGS 84.
CREATE TABLE IF NOT EXISTS public.poi_demo (
    id BIGSERIAL PRIMARY KEY,
    nazov TEXT NOT NULL,
    geom geometry(Point, 4326)
);

-- V PostgreSQL/PostGIS uvádzame pri ST_MakePoint najprv
-- zemepisnú dĺžku (longitude), potom šírku (latitude).
INSERT INTO public.poi_demo (nazov, geom)
VALUES (
    'Bratislava – demo',
    ST_SetSRID(ST_MakePoint(17.1077, 48.1486), 4326)
);

-- Body do 1000 metrov od zadaného referenčného bodu.
SELECT id, nazov
FROM public.poi_demo
WHERE ST_DWithin(
    geom::geography,
    ST_SetSRID(ST_MakePoint(17.1080, 48.1490), 4326)::geography,
    1000
);
```

Pri pretypovaní na `geography` udávame vzdialenosť pre `ST_DWithin` **v metroch**. Pri `geometry` závisí jednotka od použitého CRS.

### 🔧 Priestorové indexovanie

```sql
CREATE INDEX IF NOT EXISTS poi_demo_geom_gix
ON public.poi_demo
USING GIST (geom);
```

Tento index podporuje operácie nad stĺpcom `geom` typu `geometry`. Ak optimalizujeme opakované dopyty s výrazom `geom::geography`, môžeme vytvoriť **samostatný výrazový GiST index**:

```sql
CREATE INDEX IF NOT EXISTS poi_demo_geog_gix
ON public.poi_demo
USING GIST ((geom::geography));
```

### 🧠 PostGIS cheat sheet

| Funkcia | Úloha |
|---|---|
| `ST_GeomFromText()` | Vytvorí geometriu z WKT |
| `ST_SetSRID()` | Nastaví SRID bez transformácie súradníc |
| `ST_Transform()` | Prepočíta geometriu do iného CRS |
| `ST_Intersects()` | Overí priestorový prienik objektov |
| `ST_Contains()` | Testuje obsahovanie geometrie |
| `ST_Within()` | Testuje, či je geometria vnútri druhej |
| `ST_DWithin()` | Testuje, či je vzdialenosť v stanovenom limite |
| `ST_Distance()` | Vypočíta vzdialenosť |
| `ST_Area()` | Vypočíta plochu |
| `ST_Buffer()` | Vytvorí obalovú zónu |
| `ST_AsGeoJSON()` | Exportuje geometriu do GeoJSON reprezentácie |

## 🎯 Praktické cvičenia

| Č. | Zadanie | Nástroje | Očakávaný výsledok |
|---:|---|---|---|
| 1 | Pridáme OpenStreetMap ako XYZ podklad | QGIS | Funkčná online podkladová mapa |
| 2 | Porovnáme satelitné a topografické mapy | QGIS, Esri | Dve mapové vrstvy s odlišným účelom |
| 3 | Importujeme GeoJSON a skontrolujeme atribúty | QGIS | Vektorová vrstva a atribútová tabuľka |
| 4 | Zmeníme štýl bodov podľa kategórie | QGIS | Tematická mapa |
| 5 | Pretransformujeme vrstvu z EPSG:4326 do EPSG:5514 | QGIS / GDAL | Dáta v novom CRS |
| 6 | Vytvoríme buffer okolo vybraných objektov | QGIS Processing | Nová polygonová vrstva |
| 7 | Vyrežeme dáta podľa hranice územia | QGIS Clip | Výstup obmedzený na vybrané územie |
| 8 | Exportujeme výsledok do GeoPackage | QGIS / OGR | Súbor `.gpkg` |
| 9 | Aktivujeme PostGIS a vytvoríme tabuľku bodov | pgAdmin, PostgreSQL | Funkčná priestorová tabuľka |
| 10 | Vyhľadáme body do vzdialenosti 1 km | PostGIS | Výsledok SQL dopytu |
| 11 | Spustíme PyQGIS skript na registráciu XYZ | QGIS Python Console | Nové položky v Browseri |
| 12 | Pripravíme mapové rozloženie s legendou a mierkou | QGIS Layout | Výstupná mapa vo formáte PDF |

### 🧪 Cvičenie – porovnanie mapových vrstiev

1. Načítame **OpenStreetMap Standard**.
2. Pridáme **Esri Satellite**.
3. Presunieme satelitnú vrstvu pod tematické vektorové dáta.
4. Porovnáme identické územie pri rôznych úrovniach zoomu.
5. Skontrolujeme, kto je poskytovateľ a aké má podmienky používania.
6. Uložíme projekt ako `.qgz`.

**Výsledok:** pochopíme rozdiel medzi podkladovou mapou, rastrovou službou, vektorovou analytickou vrstvou a samotným projektom QGIS.

## 📚 GIS cheat sheet

### 🗺️ Práca s mapovými vrstvami

| Operácia | Účel | Príklad |
|---|---|---|
| Add Vector Layer | Načítanie vektorovej vrstvy | GeoJSON, GPKG |
| Add Raster Layer | Načítanie rastrov | GeoTIFF |
| XYZ Tiles | Pripojenie online podkladu | OpenStreetMap |
| Layer Properties | Nastavenie vrstvy | Symbology, Labels, CRS |
| Attribute Table | Zobrazenie záznamov | Parcely a ich výmera |
| Select by Expression | Filtrovanie objektov výrazom | `pocet_obyvatelov > 10000` |
| Buffer | Vytvorenie zóny okolo geometrie | Okolie cesty |
| Clip | Orezanie vrstvy polygónom | Údaje len pre okres |
| Intersection | Prienik dvoch vrstiev | Parcely v záplavovej oblasti |
| Reproject Layer | Transformácia CRS | EPSG:4326 → EPSG:5514 |
| Print Layout | Príprava mapy na publikovanie | PDF s legendou |

### 🧮 Praktické rozdiely GIS funkcií

| Funkcia | Stručne | Dôležitá poznámka |
|---|---|---|
| `Intersects` | Objekty sa priestorovo pretínajú | Zahŕňa aj dotyk hraníc |
| `Contains` | A obsahuje B | Hranice majú špecifickú topologickú sémantiku |
| `Within` | A je vnútri B | Inverzná relácia k Contains |
| `Buffer` | Vytvorí zónu v určitej vzdialenosti | Skontrolujeme jednotky CRS |
| `Distance` | Vypočíta vzdialenosť | Jednotky závisia od typu dát/CRS |
| `Transform` | Prevedie súradnice do iného CRS | Na rozdiel od `SetSRID` mení hodnoty súradníc |

## ⚠️ Typické chyby a riešenia

| Problém | Pravdepodobná príčina | Riešenie |
|---|---|---|
| XYZ vrstva sa nezobrazuje | Neplatná URL, výpadok, sieťové obmedzenie | Skontrolujeme URL, internet a QGIS Log Messages |
| Po spustení skriptu nevidíme nové mapy | Panel Browser sa neobnovil | Obnovíme `XYZ Tiles` alebo zavoláme `iface.reloadConnections()` |
| `ModuleNotFoundError: No module named 'qgis'` | Skript beží v bežnom Pythone bez QGIS | Spustíme ho v integrovanej Python Console |
| HTTP `401 Unauthorized` | Chýbajúci alebo nesprávny API kľúč | Skontrolujeme API účet a autentifikáciu |
| HTTP `403 Forbidden` | Oprávnenia, limity alebo zmluvné podmienky | Overíme tarif, prístup a licenciu |
| HTTP `429 Too Many Requests` | Príliš veľa požiadaviek | Obmedzíme počet volaní a rešpektujeme limity |
| Google/Bing podklad prestal fungovať | Zmena nedokumentovaného alebo starého endpointu | Prejdeme na podporované API alebo iný podklad |
| Mapy.com Names Overlay vyzerá prázdne | Priehľadná vrstva bez vhodného podkladu | Položíme ju nad leteckú mapu |
| Objekty ležia na nesprávnom mieste | Nesprávne CRS alebo poradie súradníc | Overíme pôvodný CRS, transformáciu a osy |
| Vzdialenosť je v „stupňoch“ | Výpočet v EPSG:4326 cez `geometry` | Použijeme `geography` alebo vhodný projektovaný CRS |
| V Shapefile chýbajú atribúty | Preniesli sme iba `.shp` | Doplníme `.dbf`, `.shx` a ostatné súčasti |
| QGIS hlási neplatný zdroj projektu | Projekt odkazuje na súbor z inej cesty | Opravíme zdroj dát a použijeme prenositeľné relatívne cesty |

## 🔒 Bezpečnosť, licencie a atribúcia

Pri spracovaní GIS dát používame aj služby tretích strán. Musíme preto rozlišovať medzi **právom zobraziť mapu, právom dáta spracovať a právom výsledky distribuovať**.

- **API kľúče:** nikdy ich nevkladáme do verejného repozitára ani do snímok obrazovky. Pripravíme `.gitignore` pre lokálne konfiguračné súbory.
- **Google Maps:** neoficiálne `mt1.google.com` XYZ endpointy nie sú náhradou oficiálneho, licencovaného Google Maps Platform API.
- **Bing Maps:** legacy integrácie nahrádzame Azure Maps; pri Bing Enterprise sledujeme dátum ukončenia.
- **Mapy.com:** zobrazíme požadované logo a autorské údaje. Samotná existencia XYZ vrstvy túto povinnosť nesplní.
- **Azure Maps:** pri použití dlaždíc zobrazíme atribúciu požadovanú API.
- **OpenStreetMap:** uvedieme `© OpenStreetMap contributors`, použijeme korektnú identifikáciu klienta, rešpektujeme caching a **nepoužívame verejný tile server na hromadné offline sťahovanie**.
- **Esri a ďalšie mapové služby:** preveríme aktuálne podmienky konkrétneho podkladu vrátane atribúcie a povoleného použitia.
- **Osobné údaje:** pred publikovaním anonymizujeme citlivé priestorové dáta, adresy a identifikátory.
- **Súbory:** cudzie QGIS projekty, skripty a pluginy kontrolujeme pred spustením; neznámy kód nespúšťame bez kontroly.

Príklad lokálneho `.gitignore` pre budúce rozšírenie:

```gitignore
.env
.env.*
!.env.example
secrets/
*_local_config.py
__pycache__/
*.py[cod]
```

**Pozor:** `.gitignore` nezruší únik kľúča, ktorý sme už commitli. V takom prípade kľúč okamžite **zneplatníme/rotujeme** a až potom odstránime z histórie alebo aktuálnej verzie súborov.

## 🧳 Prenositeľnosť GIS projektov

Projekt `.qgz` zvyčajne ukladá **odkazy na dáta**, nie všetky zdrojové dáta. Pri prenose projektu medzi počítačmi preto použijeme relatívne cesty, rozumnú priečinkovú štruktúru a podľa možností jednotný formát GeoPackage.

Pred zdieľaním si overíme, či projekt funguje aj po presunutí do iného priečinka. Online vrstvy navyše vyžadujú sieťový prístup a môžu mať licenčné alebo autentifikačné obmedzenia.

## 📚 Užitočné odkazy a zdroje

### 📖 GIS, QGIS a ArcGIS

- QGIS – oficiálna stránka: https://qgis.org/
- QGIS 4.2 – dokumentácia: https://docs.qgis.org/4.2/en/docs/
- QGIS – Browser a mapové služby: https://docs.qgis.org/4.2/en/docs/user_manual/introduction/browser.html
- QGIS – PyQGIS Developer Cookbook: https://docs.qgis.org/4.2/en/docs/pyqgis_developer_cookbook/
- Esri ArcGIS Pro – dokumentácia: https://pro.arcgis.com/en/pro-app/latest/
- Esri ArcPy – dokumentácia: https://pro.arcgis.com/en/pro-app/latest/arcpy/main/arcgis-pro-arcpy-reference.htm
- EPSG Geodetic Parameter Dataset: https://epsg.org/

### 🗃️ Dáta, databázy a GIS knižnice

- PostGIS – dokumentácia: https://postgis.net/documentation/
- PostGIS – `ST_DWithin`: https://postgis.net/docs/ST_DWithin.html
- PostgreSQL – dokumentácia: https://www.postgresql.org/docs/
- pgAdmin – dokumentácia: https://www.pgadmin.org/docs/
- GDAL – dokumentácia: https://gdal.org/
- GeoPackage – OGC štandard: https://www.geopackage.org/
- OpenStreetMap – mapové dáta: https://www.openstreetmap.org/
- OpenStreetMap – Tile Usage Policy: https://operations.osmfoundation.org/policies/tiles/

### 🌐 Mapové servery a API

- Google Maps Platform – Map Tiles API: https://developers.google.com/maps/documentation/tile/
- Google Maps Platform – Map Tiles API Policies: https://developers.google.com/maps/documentation/tile/policies
- Mapy.com – API: https://developer.mapy.com/
- Mapy.com – Map Tiles API: https://developer.mapy.com/rest-api-mapy-cz/function/map-tiles/
- Mapy.com – atribúcia: https://developer.mapy.com/rest-api-mapy-cz/atribution/
- Bing Maps – priamy prístup k dlaždiciam: https://learn.microsoft.com/en-us/bingmaps/rest-services/directly-accessing-the-bing-maps-tiles
- Azure Maps – Get Map Tile: https://learn.microsoft.com/en-us/rest/api/maps/render/get-map-tile?view=rest-maps-1.0
- Azure Maps – Get Map Attribution: https://learn.microsoft.com/en-us/rest/api/maps/render/get-map-attribution?view=rest-maps-2026-01-01
- Stadia Maps – dokumentácia: https://docs.stadiamaps.com/
- OpenWeatherMap – dokumentácia API: https://openweathermap.org/api

## 🎓 O repozitári

**GIS Lab** je testovací vzdelávací repozitár pre praktické ukážky a precvičovanie GIS v rámci online kurzov. Zameriavame sa na zrozumiteľné vysvetlenie nástrojov a reprodukovateľné postupy od jednoduchého mapového podkladu až po priestorové databázy a automatizáciu.

**Autor:** Miroslav Reiter  
**GitHub:** https://github.com/miroslav-reiter/gis-lab
