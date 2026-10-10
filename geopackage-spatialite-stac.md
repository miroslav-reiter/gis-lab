# 🗺️ GeoPackage, SpatiaLite a STAC v QGIS a ArcGIS Pro

**Praktický GIS návod na pripojenie existujúcich databáz a online katalógov.**  
**Prostredie:** Microsoft Windows 11 · QGIS · ArcGIS Pro  
**Zameranie:** GeoPackage (.gpkg) · SQLite/SpatiaLite (.sqlite) · STAC API · satelitné údaje

> 🎯 **Cieľ:** Nezakladáme nové databázy ani nevytvárame tabuľky. Stiahneme existujúce geografické databázy, otvoríme ich v QGIS a ArcGIS Pro, porovnáme vrstvy a vyhľadáme satelitné údaje cez verejný STAC katalóg.

## 📑 Obsah

1. [Základné pojmy a rozdiely](#-základné-pojmy-a-rozdiely)
2. [Overené zdroje dát na stiahnutie](#-overené-zdroje-dát-na-stiahnutie)
3. [GeoPackage v QGIS](#-geopackage-v-qgis)
4. [GeoPackage v ArcGIS Pro](#-geopackage-v-arcgis-pro)
5. [SpatiaLite v QGIS](#-spatialite-v-qgis)
6. [SpatiaLite v ArcGIS Pro](#-spatialite-v-arcgis-pro)
7. [Porovnanie GeoPackage a SpatiaLite](#-porovnanie-geopackage-a-spatialite)
8. [STAC a existujúce satelitné údaje](#-stac-a-existujúce-satelitné-údaje)
9. [STAC Browser v QGIS](#-stac-browser-v-qgis)
10. [STAC v ArcGIS Pro](#-stac-v-arcgis-pro)
11. [Praktické cvičenia](#-praktické-cvičenia)
12. [Najčastejšie chyby a riešenia](#-najčastejšie-chyby-a-riešenia)
13. [Návrh 15 slajdov](#-návrh-15-slajdov)
14. [Oficiálna dokumentácia a odkazy](#-oficiálna-dokumentácia-a-odkazy)

## 🧠 Základné pojmy a rozdiely

GIS nepracuje iba s obrázkami máp. Zobrazuje **priestorové objekty** (body, línie, polygóny a rastre) a ich **atribúty** (napr. názvy, kategórie a číselné hodnoty). Tieto údaje môžeme načítavať z existujúcich databázových súborov alebo získavať z online katalógov.

| Technológia | Čo to je | Ako k dátam pristupujeme | Typické využitie |
|---|---|---|---|
| **SQLite** | Vstavaný relačný databázový systém | Otvoríme existujúci databázový súbor | Tabuľky a atribúty bez databázového servera |
| **GeoPackage (GPKG)** | OGC štandard založený na SQLite | Otvoríme súbor `.gpkg` | Vektorové vrstvy, atribúty, prípadne mapové dlaždice |
| **SpatiaLite** | Priestorové rozšírenie SQLite | Otvoríme kompatibilný súbor `.sqlite` | Geometrie, priestorové funkcie, indexy |
| **STAC** | SpatioTemporal Asset Catalog – štandard katalógov | Pripojíme sa ku katalógu / STAC API | Vyhľadávanie snímok a ďalších priestorových údajov podľa miesta a času |

**Nezamieňajme:**

- **GeoPackage ≠ SpatiaLite.** Obe technológie používajú SQLite, ale majú odlišné pravidlá priestorového ukladania a metadát.
- **SQLite ≠ automaticky SpatiaLite.** Obyčajný SQLite súbor nemusí obsahovať geometrie ani požadované priestorové metadáta.
- **STAC ≠ súborová GIS databáza.** STAC opisuje katalóg, položky a odkazy na dátové zdroje; samotný raster môže byť uložený napríklad ako GeoTIFF/COG.
- **GeoPackage súbor ≠ QGIS/ArcGIS projekt.** Projekt si zapamätá cesty, vrstvy a štýly, ale zdrojové dáta ostávajú v osobitnom súbore.

### 📁 Prípony a ich význam

| Prípona | Typický význam | Poznámka |
|---|---|---|
| `.gpkg` | GeoPackage | Odporúčaný prenositeľný GIS formát |
| `.sqlite` | SQLite alebo SpatiaLite | Pre ArcGIS Pro dôležitá správna prípona a kompatibilná schéma |
| `.sqlite3` | SQLite databáza | Nie je automaticky rozpoznaná ako podporovaný priestorový zdroj v každej GIS aplikácii |
| `.db` | Všeobecný databázový súbor | Prípona sama nedokazuje, že ide o SQLite/SpatiaLite |
| `.sqli` | Neštandardné pomenovanie | Na školenie nepoužívame ako formát |
| `.astac` | Konfigurácia STAC pripojenia ArcGIS Pro | Nie je to stiahnutá satelitná snímka |

## 📦 Overené zdroje dát na stiahnutie

V tejto lekcii **nepridávame do repozitára binárne databázy**. Používame existujúce datasety poskytované ich správcami a sťahujeme ich do lokálneho priečinka.

| Zdroj | Súbor / služba | Čo obsahuje | Priamy odkaz |
|---|---|---|---|
| QGIS Training Data | `training_data.gpkg` | Existujúce GIS vrstvy z tréningových dát | [Stiahnuť GPKG](https://raw.githubusercontent.com/qgis/QGIS-Training-Data/master/exercise_data/training_data.gpkg) |
| QGIS Training Data | `landuse.sqlite` | Priestorové údaje o využití územia | [Stiahnuť SQLite](https://raw.githubusercontent.com/qgis/QGIS-Training-Data/master/exercise_data/landuse.sqlite) |
| Natural Earth – komunitná konverzia | `ne_50m_admin_0_countries.gpkg` | Hranice krajín sveta | [Stiahnuť GPKG](https://raw.githubusercontent.com/tohka/ne/master/GeoPackage/ne_50m_admin_0_countries.gpkg) |
| Natural Earth – komunitná konverzia | `ne_50m_admin_0_countries.sqlite` | Rovnaký geografický obsah v SpatiaLite | [Stiahnuť SQLite](https://raw.githubusercontent.com/tohka/ne/master/SpatiaLite/ne_50m_admin_0_countries.sqlite) |
| Element 84 Earth Search | STAC API v1 | Katalóg satelitných a ďalších datasetov | [Otvoriť STAC](https://earth-search.aws.element84.com/v1) |

**Pôvod a dôveryhodnosť:** Prvé dva súbory pochádzajú z oficiálneho repozitára tréningových dát QGIS. Dvojica Natural Earth pochádza z **nezávislého repozitára s konverziami** – nejde o oficiálny distribučný formát vydaný projektom Natural Earth. Earth Search prevádzkuje Element 84. Odkazy smerujú na existujúce súbory a službu, nie na vlastné napodobeniny dát.

### 🪟 Príprava vo Windows 11

1. Otvoríme Prieskumníka súborov pomocou **Win + E**.
2. Vytvoríme priečinok napríklad **C:\\GIS\\data**.
3. Stiahneme požadované `.gpkg` a `.sqlite` súbory cez priame odkazy vyššie. Pri zobrazení binárneho súboru na GitHube môžeme použiť **Download raw file**.
4. Skontrolujeme, že súbory majú správnu príponu a nenesú napr. príponu `.html` po neúmyselnom uložení webovej stránky.
5. Súbory **neprepisujeme ani nemeníme ich prípony naslepo**. Na výučbu používame čítanie a zobrazovanie existujúcich údajov.

## 🗺️ GeoPackage v QGIS

**GeoPackage** je praktický otvorený formát na výmenu dát medzi GIS aplikáciami. V jednom súbore môže obsahovať viac tabuliek a priestorových vrstiev. Na otvorenie `.gpkg` nepotrebujeme samostatný PostgreSQL server.

### Postup pripojenia

1. Spustíme **QGIS**.
2. Zapneme **View → Panels → Browser Panel**, ak nie je zobrazený.
3. V paneli **Browser** nájdeme **GeoPackage**.
4. Pravým kliknutím vyberieme **New Connection…**.
5. Vyberieme stiahnutý `training_data.gpkg`.
6. Rozbalíme databázu a pozrieme dostupné vrstvy.
7. Dvojklikom alebo pretiahnutím pridáme zvolenú vrstvu do **Map Canvas**.
8. V **Layers Panel** otvoríme kontextové menu vrstvy → **Open Attribute Table**.
9. Použijeme **Zoom to Layer**, **Identify Features** a zapínanie viditeľnosti.

**Alternatíva:** Súbor `.gpkg` môžeme tiež načítať pomocou **Layer → Add Layer → Add Vector Layer** alebo ho pretiahnuť z Prieskumníka do QGIS.

### Čo si máme všimnúť

- **Jeden databázový súbor** môže obsahovať **viac samostatných vrstiev**.
- Každá vrstva má vlastnú geometriu, tabuľku atribútov a CRS.
- Zmena zobrazenia alebo posun mapy **nemení obsah databázy**.
- Názvy a počet vrstiev si vždy overíme podľa skutočne stiahnutej verzie súboru.

## 🌐 GeoPackage v ArcGIS Pro

ArcGIS Pro podporuje pripojenie k existujúcim GeoPackage súborom cez **Catalog** a **Folders**.

### Postup pripojenia

1. Spustíme **ArcGIS Pro** a otvoríme mapový projekt.
2. Otvoríme **View → Catalog Pane**.
3. V časti **Folders** pripojíme priečinok **C:\\GIS\\data**.
4. V priečinku vyhľadáme `training_data.gpkg`.
5. Pravým kliknutím použijeme **Add To Project** (alebo pracujeme priamo cez folder connection).
6. Pod **Catalog → Databases** rozbalíme pripojený súbor.
7. Vyberieme podporovanú **feature class** a použijeme **Add To Current Map** alebo ju pretiahneme na mapu.
8. Otvoríme atribútovú tabuľku a porovnáme ju s QGIS.

**Praktický výsledok:** To isté `.gpkg` otvoríme v dvoch programoch **bez vytvorenia novej databázy a bez konverzie**.

> ⚠️ **Kompatibilita:** ArcGIS Pro podporuje GeoPackage a vybrané rozšírenia štandardu, nie nevyhnutne každé možné rozšírenie GeoPackage. Pre neznáme databázy najskôr overíme, ktoré vrstvy ArcGIS Pro skutočne rozpoznal.

## 🧩 SpatiaLite v QGIS

**SpatiaLite** rozširuje SQLite o priestorové typy a operácie. Pre naše cvičenie použijeme už pripravený súbor `landuse.sqlite` z QGIS Training Data.

### Postup pripojenia

1. Otvoríme **QGIS → Browser Panel**.
2. Pravým kliknutím na **SpatiaLite** vyberieme **New Connection…**.
3. Vyhľadáme lokálny súbor `landuse.sqlite`.
4. Rozbalíme pripojenie.
5. Vyberieme existujúcu vrstvu `landuse` a dvojklikom ju pridáme na mapu.
6. Použijeme **Zoom to Layer** a **Open Attribute Table**.
7. Zobrazíme **Layer Properties → Information / Source** a pozrieme CRS a typ geometrie.

Táto úloha zodpovedá príkladu z oficiálneho **QGIS Training Manual**.

### Na čo je dobrý

SpatiaLite je vhodný na lokálnu správu priestorových dát, kde chceme využiť SQL a priestorové funkcie, ale nepotrebujeme samostatný server. Pri školení ho porovnáme s GeoPackage, nie s bežným obrázkom mapy.

## 🏢 SpatiaLite v ArcGIS Pro

ArcGIS Pro podporuje **určité verzie SQLite a SpatiaLite**; nejde o záruku, že bez problémov otvorí ľubovoľnú historickú databázu so súborovou príponou `.sqlite`.

### Postup pripojenia

1. Otvoríme **Catalog Pane**.
2. Pripojíme priečinok obsahujúci `landuse.sqlite`.
3. V časti **Folders** vyhľadáme súbor a pravým kliknutím zvolíme **Add To Project**.
4. V **Databases** skontrolujeme rozpoznané tabuľky a priestorové triedy.
5. Ak je vrstva podporovaná, pridáme ju do mapy pomocou **Add To Current Map**.
6. Ak ArcGIS Pro údaje nečíta, pozrieme **podporované verzie SpatiaLite, geometriu a priestorovú schému**.

> ⚠️ **Dôležité:** `landuse.sqlite` je spoľahlivý tréningový príklad pre QGIS. **Jeho načítanie do aktuálnej verzie ArcGIS Pro treba pred natáčaním osobitne vyskúšať.** ArcGIS Pro 3.6 uvádza podporu SpatiaLite 5.0.1 a GeoPackage 1.1 až 1.4. Obyčajné premenovanie staršieho `.db` na `.sqlite` nedoplní chýbajúce geopriestorové metadáta ani nevyrieši nepodporovanú schému.

## 🔁 Porovnanie GeoPackage a SpatiaLite

### Rovnaké geografické údaje v dvoch formátoch

Použijeme komunitné konverzie **Natural Earth – hranice krajín sveta**:

- [GeoPackage: ne_50m_admin_0_countries.gpkg](https://github.com/tohka/ne/blob/master/GeoPackage/ne_50m_admin_0_countries.gpkg)
- [SpatiaLite: ne_50m_admin_0_countries.sqlite](https://github.com/tohka/ne/blob/master/SpatiaLite/ne_50m_admin_0_countries.sqlite)

**Porovnanie v QGIS:** otvoríme oba súbory, zapneme vždy iba jednu vrstvu, otvoríme tabuľky atribútov a porovnáme počet objektov, geografický rozsah, CRS, výzor mapy aj názvy polí.

**Porovnanie v ArcGIS Pro:** prednostne otvoríme GeoPackage; SpatiaLite zobrazíme, ak ho konkrétna verzia ArcGIS Pro rozpozná. Kompatibilita binárnej SpatiaLite databázy nebola otestovaná v tejto lekcii na reálnej inštalácii ArcGIS Pro.

| Kritérium | GeoPackage | SpatiaLite |
|---|---|---|
| Databázový základ | SQLite | SQLite |
| Primárne zameranie | Štandardizovaný prenos a uloženie GIS dát | Priestorové SQL a geometrické funkcie |
| Bežná prípona | `.gpkg` | `.sqlite` |
| QGIS | Natívna podpora | Natívna podpora |
| ArcGIS Pro | Podporované formáty a verzie GPKG | Len podporované verzie a schémy SpatiaLite |
| Server | Nie je potrebný | Nie je potrebný |

## 🛰️ STAC a existujúce satelitné údaje

**STAC (SpatioTemporal Asset Catalog)** je štandard na opis a vyhľadávanie datasetov podľa **miesta, času a metadát**. Pre tento kurz ho využijeme hlavne na objavenie existujúcich satelitných snímok.

### Ako čítať štruktúru STAC

| Pojem | Význam |
|---|---|
| **Catalog** | Organizovaná zbierka odkazov na kolekcie a položky |
| **Collection** | Logická skupina datasetov, napr. Sentinel-2 |
| **Item** | Jedna scéna / pozorovanie s časom, polohou a metadátami |
| **Asset** | Odkaz na konkrétny dátový súbor, napr. COG alebo iný raster |
| **STAC API** | Rozhranie na filtrovanie a získavanie položiek katalógu |

### Verejné katalógy

| Katalóg | STAC API / zdroj | Poznámka |
|---|---|---|
| **Element 84 Earth Search** | https://earth-search.aws.element84.com/v1 | Hlavný zdroj pre cvičenie |
| **Microsoft Planetary Computer** | https://planetarycomputer.microsoft.com/api/stac/v1 | Niektoré assety vyžadujú podpísané URL alebo autentizáciu |

**Príklady kolekcií Earth Search:** `sentinel-2-l2a`, `sentinel-2-c1-l2a`, `landsat-c2-l2` (dostupnosť konkrétnych položiek a prístupu k assetom sa môže meniť).

Verejný **STAC katalóg neznamená automaticky bezplatné alebo neobmedzené používanie každého assetu**. Vždy overíme licenciu, poskytovateľa, prístupové požiadavky a limity.

## 🔎 STAC Browser v QGIS

Pre jednoduché vyhľadávanie údajov použijeme doplnok [STAC Browser](https://plugins.qgis.org/plugins/stac_browser/). Jeho katalógy zahŕňajú aj **Element 84 Earth Search**.

### Inštalácia a použitie

1. Otvoríme QGIS.
2. Vyberieme **Plugins → Manage and Install Plugins**.
3. Vyhľadáme **STAC Browser** (nie QuickMapServices).
4. Doplnok nainštalujeme a otvoríme jeho panel.
5. Použijeme Earth Search alebo nastavíme dostupný STAC zdroj podľa rozhrania pluginu.
6. Na mape vyberieme **územie Bratislavy** alebo vyhľadáme lokalitu.
7. Nastavíme časové obdobie a vhodný druh datasetu.
8. Prejdeme nájdené položky, dátum získania, oblačnosť a dostupné assety.
9. Vyberieme kompatibilný asset na zobrazenie či stiahnutie, ak to rozhranie doplnku ponúka.

**Ukážkové zadanie:** nájdeme snímku Bratislavy z leta 2025 a porovnáme dve scény s rôznou oblačnosťou.

> Poznámka: Rozhranie a názvy filtrov sa menia podľa verzie pluginu. Nie všetky katalógy majú rovnaké kolekcie ani identické metadáta.

## 🖥️ STAC v ArcGIS Pro

ArcGIS Pro má vlastné **STAC Connection** a panel **Explore STAC**.

### Vytvorenie pripojenia k existujúcemu katalógu

1. Otvoríme **ArcGIS Pro → Insert**.
2. V skupine **Project** zvolíme **Connections → STAC Connection → New STAC Connection**.
3. Zadáme názov pripojenia, napríklad **Earth Search**.
4. Vyberieme vlastný STAC endpoint a zadáme:

~~~text
https://earth-search.aws.element84.com/v1
~~~

5. Potvrdíme pripojenie.
6. Otvoríme **Catalog Pane → STACs**, pravým klikom na spojenie vyberieme **Explore STAC**.
7. V karte **Parameters** nastavíme kolekciu, obdobie a rozsah mapy.
8. Prejdeme na kartu **Results**, pozrieme footprint a metadáta položky.
9. Podporovaný asset / položku pridáme pomocou **Add To Current Map**.

Súbor `.astac` uchováva **nastavenie pripojenia**, nie samotné satelitné dáta.

### 🌍 Rovnaké zadanie pre obe GIS aplikácie

| Parameter | Hodnota pre výučbu |
|---|---|
| Katalóg | Earth Search v1 |
| Kolekcia | `sentinel-2-l2a` |
| Územie | Bratislava a okolie |
| Obdobie | 2025-06-01 až 2025-09-30 |
| Oblačnosť | Pokiaľ je k dispozícii filter, prednostne do 10 % |
| Očakávaný výstup | Položka STAC, metadáta, footprint, kompatibilná snímka |

**Pozor:** Parameter oblačnosti sa často vzťahuje na celú scénu, nie len na Bratislavu. Úspešné nájdenie STAC Item nemusí znamenať úspešné načítanie všetkých jeho assetov bez ďalšieho prístupu do cloudu.

## 🧪 Praktické cvičenia

### 1. Načítanie existujúceho GeoPackage

**Cieľ:** V QGIS a ArcGIS Pro otvoriť rovnaký súbor `training_data.gpkg`.

**Postup:** Stiahneme databázu → pridáme spojenie → zobrazíme dve dostupné vrstvy → otvoríme atribútovú tabuľku → overíme CRS.

**Overenie:** Na oboch mapách vidíme tie isté prvky. **Nič sme nekonvertovali ani nevytvárali novú databázu.**

### 2. Načítanie existujúceho SpatiaLite

**Cieľ:** V QGIS otvoriť `landuse.sqlite` a otestovať jeho čitateľnosť v ArcGIS Pro.

**Postup:** Pripojíme existujúci súbor → zobrazíme vrstvu `landuse` → pozrieme atribúty, rozsah a typ geometrie → pokúsime sa o načítanie v ArcGIS Pro.

**Overenie:** QGIS správne zobrazuje vrstvu; pri ArcGIS Pro zaznamenáme buď úspešné načítanie, alebo konkrétnu nekompatibilitu.

### 3. Rovnaké krajiny sveta v dvoch formátoch

**Cieľ:** Porovnať Natural Earth `.gpkg` a `.sqlite`.

**Postup:** Pridáme oba existujúce súbory → striedavo zapíname vrstvy → otvoríme tabuľky → porovnáme CRS, počty objektov a atribúty.

**Overenie:** Vieme vysvetliť, prečo rovnaké geografické údaje môžu existovať v rozličných formátoch.

### 4. Vyhľadávanie satelitných snímok v STAC

**Cieľ:** V QGIS a ArcGIS Pro vyhľadať snímky rovnakého územia z toho istého obdobia.

**Postup:** Pripojíme Earth Search → nastavíme Bratislavu → kolekciu Sentinel-2 → leto 2025 → vyberieme položku a preskúmame metadáta.

**Overenie:** Poznáme dátum snímky, footprint, dostupné assety a vieme určiť, či sa snímka úspešne načítala.

## 🛠️ Najčastejšie chyby a riešenia

| Problém | Možná príčina | Riešenie |
|---|---|---|
| Súbor `.gpkg` sa nezobrazuje | Chybná cesta, iná prípona, poškodený súbor | Skontrolujeme stiahnutie a použijeme Browser / Catalog |
| V GeoPackage nevidíme očakávanú vrstvu | Iná verzia datasetu alebo nerozbalené pripojenie | Rozbalíme databázu a prezrieme skutočný zoznam vrstiev |
| SQLite sa v ArcGIS Pro nenačíta | Nepodporovaná verzia alebo priestorová schéma | Overíme kompatibilitu SpatiaLite podľa dokumentácie Esri |
| Niekto premenuje `.db` na `.sqlite` | Zmena názvu nevyrieši formát ani obsah | Overíme skutočnú databázovú štruktúru |
| Vrstva je mimo mapy | Iný rozsah alebo nesprávny CRS | Použijeme Zoom to Layer a skontrolujeme CRS |
| Vidíme iba tabuľku | Dáta nemajú podporovanú geometriu | Overíme, či ide o priestorovú tabuľku |
| STAC nevracia výsledky | Nesprávna kolekcia, obdobie alebo územie | Rozšírime čas, rozsah a znížime prísnosť filtrov |
| STAC nájde položku, no raster sa nenačíta | Asset potrebuje token, podpis URL alebo podporovaný ovládač | Skontrolujeme href, autentizáciu a typ assetu |
| GeoPackage je zamknutý | Iný proces súbor upravuje | Pracujeme s kópiou a vyhneme sa súbežným zápisom |

## 🎬 Návrh 15 slajdov

| Slajd | Názov | Obsah a praktická ukážka |
|---:|---|---|
| 1 | GIS Databázy a STAC | Čo budeme pripájať v QGIS a ArcGIS Pro |
| 2 | Čo sú GeoPackage, SQLite a SpatiaLite | Význam a vzťah jednotlivých technológií |
| 3 | GeoPackage vs. SpatiaLite vs. STAC | Súborové databázy vs. online katalógy |
| 4 | Odkiaľ získame GIS dáta | QGIS Training Data, Natural Earth, Earth Search |
| 5 | GeoPackage – existujúca databáza | Stiahnutie a obsah `training_data.gpkg` |
| 6 | GeoPackage v QGIS | Browser, New Connection, atribúty |
| 7 | GeoPackage v ArcGIS Pro | Catalog, Add To Project, zobrazenie vrstvy |
| 8 | SQLite a SpatiaLite | Geometrie a rozdiel oproti obyčajnému SQLite |
| 9 | SpatiaLite v QGIS | `landuse.sqlite`, otvorenie vrstvy `landuse` |
| 10 | SpatiaLite v ArcGIS Pro | Catalog, podporované verzie, kompatibilita |
| 11 | Rovnaké údaje v dvoch formátoch | Natural Earth GPKG vs. SpatiaLite |
| 12 | Čo je STAC | Catalog, Collection, Item, Asset, API |
| 13 | STAC Browser v QGIS | Earth Search a vyhľadanie snímok |
| 14 | Explore STAC v ArcGIS Pro | Pripojenie, filtre, metadáta, assety |
| 15 | Zhrnutie a chyby | Kedy použiť GPKG, SpatiaLite a STAC |

### ⏱️ Orientačné časovanie videa

| Čas | Obsah |
|---|---|
| 00:00–07:00 | Pojmy a rozdiely |
| 07:00–12:00 | Existujúce dátové zdroje |
| 12:00–24:00 | GeoPackage v oboch aplikáciách |
| 24:00–35:00 | SpatiaLite v oboch aplikáciách |
| 35:00–40:00 | Natural Earth – porovnanie |
| 40:00–50:00 | STAC Browser v QGIS |
| 50:00–58:00 | STAC v ArcGIS Pro |
| 58:00–60:00 | Chyby a záver |

## 🔗 Oficiálna dokumentácia a odkazy

**Údaje a ich pôvod**

- [QGIS Training Data – repozitár](https://github.com/qgis/QGIS-Training-Data)
- [QGIS Training Data – priečinok exercise_data](https://github.com/qgis/QGIS-Training-Data/tree/master/exercise_data)
- [Natural Earth – oficiálny web](https://www.naturalearthdata.com/downloads/)
- [Natural Earth – komunitné konverzie GPKG / SpatiaLite](https://github.com/tohka/ne)

**QGIS a ArcGIS Pro**

- [QGIS – Browser Panel](https://docs.qgis.org/testing/en/docs/user_manual/introduction/browser.html)
- [QGIS – tréningová lekcia: pridanie vrstiev](https://docs.qgis.org/testing/en/docs/training_manual/basic_map/preparation.html)
- [ArcGIS Pro – SQLite a GeoPackage](https://pro.arcgis.com/en/pro-app/3.6/help/data/databases/work-with-sqlite-databases-in-arcgis-pro.htm)
- [ArcGIS Pro – požiadavky na SQLite a SpatiaLite](https://pro.arcgis.com/en/pro-app/3.6/help/data/databases/database-requirements-sqlite.htm)
- [ArcGIS Pro – vytvorenie STAC pripojenia](https://doc.esri.com/en/arcgis-pro/latest/help/data/imagery/create-a-stac-connection.html)
- [ArcGIS Pro – Explore STAC](https://doc.esri.com/en/arcgis-pro/latest/help/data/imagery/explore-stac.html)

**STAC**

- [STAC Browser – QGIS Plugins](https://plugins.qgis.org/plugins/stac_browser/)
- [Element 84 Earth Search – ukážky](https://element84.com/earth-search/examples/)
- [Element 84 Earth Search – dokumentácia a kolekcie](https://github.com/Element84/earth-search)
- [STAC Specification](https://stacspec.org/)

> 📌 **Zásada laboratória:** Otvárame a skúmame **existujúce zdrojové dáta**. Lokálne projektové súbory QGIS/ArcGIS môžeme uložiť, ale do originálnych GPKG/SQLite súborov pri cvičení nezapisujeme. Pri komunite prevzatých dátach vždy overíme pôvod, licenciu a kompatibilitu aplikácie.
