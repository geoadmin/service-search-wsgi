# pylint: disable=line-too-long


class MockSocket:
    # pylint: disable=unused-argument

    def __init__(self, status, data):
        self.status = status
        self.data = data
        self.n_call = 0

    def recv(self, *args, **kwargs):
        self.n_call = self.n_call + 1
        if self.n_call == 1:
            return self.status
        return self.data

    @staticmethod
    def send(*args, **kwargs):
        return -1

    def close(self):
        pass


MOCK_BUILD_EXCERPTS_SOCK = MockSocket(
    b'\x00\x00\x01\x04\x00\x00\x00u',
    b'\x00\x00\x004this is my <i>test</i> <i>text</i> to be highlighted\x00\x00\x009this is another <i>test</i> <i>text</i> to be highlighted'
)
MOCK_BUILD_EXCERPTS_NO_OPTS_SOCK = MockSocket(
    b'\x00\x00\x01\x04\x00\x00\x00u',
    b'\x00\x00\x004this is my <b>test</b> <b>text</b> to be highlighted\x00\x00\x009this is another <b>test</b> <b>text</b> to be highlighted'
)

MOCK_SEARCH_QUERY_SOCK = MockSocket(
    b'\x00\x00\x01\x1f\x00\x00)\x98',
    b'\x00\x00\x00\x03\x00\x00\x1b=index address,district,gg25,haltestellen,kantone,parcel,swissnames3d,zipcode: query word(s) mismatch: *bern*;\nindex address_metaphone,district_metaphone,gg25_metaphone,haltestellen_metaphone,kantone_metaphone,swissnames3d_metaphone: query word(s) mismatch: *bern*, bern;\nindex ch_astra_ivs_nat,ch_astra_ivs_nat_verlaeufe,ch_astra_ivs_reg_loc,ch_astra_mountainbikeland,ch_astra_mountainbikeland_sperrungen_umleitungen,ch_astra_nationalstrassenachsen,ch_astra_schwerverunfallte_kanton_alkohol,ch_astra_schwerverunfallte_kanton_geschwindigkeit,ch_astra_schwerverunfallte_kanton_jahresvergleich,ch_astra_schwerverunfallte_kanton_pro_einwohner,ch_astra_skatingland,ch_astra_skatingland_sperrungen_umleitungen,ch_astra_strassenverkehrszaehlung_messstellen_regional_lokal,ch_astra_strassenverkehrszaehlung_messstellen_uebergeordnet,ch_astra_strassenverkehrszaehlung_uebergeordnet,ch_astra_unfaelle_personenschaeden_alle,ch_astra_unfaelle_personenschaeden_fahrraeder,ch_astra_unfaelle_personenschaeden_fussgaenger,ch_astra_unfaelle_personenschaeden_getoetete,ch_astra_unfaelle_personenschaeden_motorraeder,ch_astra_veloland,ch_astra_veloland_sperrungen_umleitungen,ch_astra_wanderland,ch_astra_wanderland_sperrungen_umleitungen,ch_babs_kulturgueter,ch_bakom_notruf,ch_bakom_notruf_112_festnetz,ch_bakom_notruf_112_mobilnetz,ch_bakom_notruf_112_satellit,ch_bakom_notruf_117_festnetz,ch_bakom_notruf_117_mobilnetz,ch_bakom_notruf_118_festnetz,ch_bakom_notruf_118_mobilnetz,ch_bakom_notruf_143_festnetz,ch_bakom_notruf_143_mobilnetz,ch_bakom_notruf_144_festnetz,ch_bakom_notruf_144_mobilnetz,ch_bakom_notruf_145_festnetz,ch_bakom_notruf_145_mobilnetz,ch_bakom_notruf_147_festnetz,ch_bakom_notruf_147_mobilnetz,ch_bakom_radio_fernsehsender,ch_bakom_versorgungsgebiet_tv,ch_bakom_versorgungsgebiet_ukw,ch_bav_anlagen_schienengueterverkehr,ch_bav_haltestellen_oev,ch_bav_kataster_belasteter_standorte_oev,ch_bav_sachplan_infrastruktur_schiene_anhorung_1,ch_bav_sachplan_infrastruktur_schiene_anhorung_2,ch_bav_sachplan_infrastruktur_schiene_ausgangslage,ch_bav_sachplan_infrastruktur_schiene_kraft_1,ch_bav_sachplan_infrastruktur_schiene_kraft_2,ch_bav_sachplan_infrastruktur_schifffahrt_anhoerung_1,ch_bav_sachplan_infrastruktur_schifffahrt_anhoerung_2,ch_bav_sachplan_infrastruktur_schifffahrt_ausgangslage,ch_bav_sachplan_infrastruktur_schifffahrt_kraft_1,ch_bav_sachplan_infrastruktur_schifffahrt_kraft_2,ch_bav_schienennetz,ch_bav_seilbahnen_bundeskonzession,ch_bazl_kataster_belasteter_standorte_zivilflugplaetze,ch_bazl_luftfahrthindernis,ch_bfe_abgeltung_wasserkraftnutzung,ch_bfe_biogasanlagen,ch_bfe_biomasse_nicht_verholzt,ch_bfe_biomasse_verholzt,ch_bfe_energieforschung,ch_bfe_energiestaedte,ch_bfe_energiestaedte_2000watt_areale,ch_bfe_erneuerbarheizen,ch_bfe_erneuerbarheizen_mehrfamilienhaeuser,ch_bfe_fernwaerme_angebot,ch_bfe_kehrichtverbrennungsanlagen,ch_bfe_kernkraftwerke,ch_bfe_kleinwasserkraftpotentiale,ch_bfe_komo_projekte,ch_bfe_sachplan_geologie_tiefenlager_1,ch_bfe_sachplan_geologie_tiefenlager_2,ch_bfe_sachplan_geologie_tiefenlager_3,ch_bfe_sachplan_uebertragungsleitungen_anhorung_1,ch_bfe_sachplan_uebertragungsleitungen_anhorung_2,ch_bfe_sachplan_uebertragungsleitungen_anhorung_3,ch_bfe_sachplan_uebertragungsleitungen_anhorung_4,ch_bfe_sachplan_uebertragungsleitungen_kraft_1,ch_bfe_sachplan_uebertragungsleitungen_kraft_2,ch_bfe_sachplan_uebertragungsleitungen_kraft_3,ch_bfe_sachplan_uebertragungsleitungen_kraft_4,ch_bfe_statistik_wasserkraftanlagen,ch_bfe_stauanlagen_bundesaufsicht,ch_bfe_thermische_netze,ch_bfe_waermepotential_gewaesser,ch_bfe_windenergieanlagen,ch_swisstopo_amtliches_gebaeudeadressverzeichnis,ch_swisstopo_amtliches_strassenverzeichnis,ch_swisstopo_burgenkarte200_papier_metadata,ch_swisstopo_geologie_bohrungen_tiefer_500,ch_swisstopo_geologie_felslabore,ch_swisstopo_geologie_generalkarte_ggk200_metadata,ch_swisstopo_geologie_geoevents_anfrage,ch_swisstopo_geologie_geoevents_demnaechst,ch_swisstopo_geologie_geologischer_atlas,ch_swisstopo_geologie_geologischer_atlas_metadata,ch_swisstopo_geologie_geologischer_atlas_papier_metadata,ch_swisstopo_geologie_geologischer_atlas_vector_metadata,ch_swisstopo_geologie_geosites,ch_swisstopo_geologie_geotechnik_ziegeleien_1907,ch_swisstopo_geologie_geothermische_potenzialstudien_regional,ch_swisstopo_geologie_geowege,ch_swisstopo_geologie_gisgeol_flaechen_1000to21000km2,ch_swisstopo_geologie_gisgeol_flaechen_100to1000km2,ch_swisstopo_geologie_gisgeol_flaechen_10to100km2,ch_swisstopo_geologie_gisgeol_flaechen_10x10km,ch_swisstopo_geologie_gisgeol_flaechen_1x1km,ch_swisstopo_geologie_gisgeol_flaechen_gt21000km2,ch_swisstopo_geologie_gisgeol_flaechen_lt10km2,ch_swisstopo_geologie_gisgeol_linien,ch_swisstopo_geologie_gisgeol_punkte,ch_swisstopo_geologie_gletscherausdehnung,ch_swisstopo_geologie_gravimetrischer_atlas_messpunkte,ch_swisstopo_geologie_gravimetrischer_atlas_papier_metadata,ch_swisstopo_geologie_rohstoffe_gebrochene_gesteine_abbau,ch_swisstopo_geologie_rohstoffe_gips_abbau_verarbeitung,ch_swisstopo_geologie_rohstoffe_industrieminerale,ch_swisstopo_geologie_rohstoffe_kohlen_bitumen_erdgas,ch_swisstopo_geologie_rohstoffe_naturwerksteine_abbau,ch_swisstopo_geologie_rohstoffe_salz_abbau_verarbeitung,ch_swisstopo_geologie_rohstoffe_vererzungen,ch_swisstopo_geologie_rohstoffe_zement_abbau_verarbeitung,ch_swisstopo_geologie_rohstoffe_ziegel_abbau,ch_swisstopo_geologie_rohstoffe_ziegel_verarbeitung,ch_swisstopo_geologie_spezialkarten_schweiz_metadata,ch_swisstopo_geologie_spezialkarten_schweiz_papier_metadata,ch_swisstopo_geologie_spezialkarten_schweiz_vector_metadata,ch_swisstopo_geologie_tiefengeothermie_projekte,ch_swisstopo_hebungsraten,ch_swisstopo_landeskarte100_papier_metadata,ch_swisstopo_landeskarte200_papier_metadata,ch_swisstopo_landeskarte25_papier_metadata,ch_swisstopo_landeskarte50_papier_metadata,ch_swisstopo_landesschwerenetz,ch_swisstopo_lhk100_papierkarte_metadata,ch_swisstopo_lotabweichungen,ch_swisstopo_luftfahrtkarten_icao_papier_metadata,ch_swisstopo_schneeschuhwandern,ch_swisstopo_skitourenkarte_50_metadata,ch_swisstopo_swiss_map_vector25_metadata,ch_swisstopo_swissboundaries3d_bezirk_flaeche_fill,ch_swisstopo_swissboundaries3d_gemeinde_flaeche_fill,ch_swisstopo_swissboundaries3d_kanton_flaeche_fill,ch_swisstopo_transformation_bezugsrahmen_hoehe,ch_swisstopo_vd_geometa_periodische_nachfuehrung,ch_swisstopo_vd_ortschaftenverzeichnis_plz,ch_swisstopo_vec200_names_namedlocation,ch_swisstopo_vec25_gewaessernetz_referenz,ch_swisstopo_verschiebungsvektoren_tsp1,ch_swisstopo_verschiebungsvektoren_tsp2,ch_swisstopo_wanderkarte25_zus_papier_metadata,ch_swisstopo_wanderkarte33_papier_metadata,ch_swisstopo_wanderkarte50_papier_metadata,ch_vbs_armee_kriegsdenkmaeler,ch_vbs_armeelogistikcenter,ch_vbs_bundestankstellen_bebeco,ch_vbs_kataster_belasteter_standorte_militaer,ch_vbs_logistikraeume_armeelogistikcenter,ch_vbs_retablierungsstellen,ch_vbs_schiessanzeigen,ch_vbs_waldschadenkarte: query word(s) mismatch: PRN\x00\x00\x00\x02\x00\x00\x00\x06detail\x00\x00\x00\x0egeom_quadindex\x00\x00\x00\x03\x00\x00\x00\x05label\x00\x00\x00\x07\x00\x00\x00\x06origin\x00\x00\x00\x07\x00\x00\x00\x06detail\x00\x00\x00\x07\x00\x00\x00\x14\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x0f\x8d\x00\x00\x07\\\x00\x00\x00\x85W\xc3\xa4rmeversorgung der \xc3\x9cberbauung Weltpoststrasse Bern, mit Eisspeicher-W\xc3\xa4rmepumpe System unter Nutzung von Solar- und Abwasserw\xc3\xa4rme\x00\x00\x00\x07feature\x00\x00\x02\x17waermeversorgung der ueberbauung weltpoststrasse bern, mit eisspeicher-waermepumpe system unter nutzung von solar- und abwasserwaerme waermeversorgung der ueberbauung weltpoststrasse bern, mit eisspeicher-waermepumpe system unter nutzung von solar- und abwasserwaerme waermeversorgung der ueberbauung weltpoststrasse bern, mit eisspeicher-waermepumpe system unter nutzung von solar- und abwasserwaerme waermeversorgung der ueberbauung weltpoststrasse bern, mit eisspeicher-waermepumpe system unter nutzung von solar- und abwasserwaerme\x00\x00\x00\x00\x00\x00\x0c[\x00\x00\x06\xbf\x00\x00\x00\x13Bern Weyermannshaus\x00\x00\x00\x07feature\x00\x00\x00!85070102 bern weyermannshaus bnwm\x00\x00\x00\x00\x00\x00,~\x00\x00\x06\xbe\x00\x00\x00\x13Urban Geotrail Bern\x00\x00\x00\x07feature\x00\x00\x00\x15urban geotrail bern  \x00\x00\x00\x00\x00\x00\x00\xd1\x00\x00\x06\xbd\x00\x00\x00"Bern Energiezentrale Forsthaus EWB\x00\x00\x00\x07feature\x00\x00\x00"bern energiezentrale forsthaus ewb\x00\x00\x00\x00\x00\x00\x12\xc3\x00\x00\x06\xbd\x00\x00\x00\x1aL\xc3\xa4be im Burgereziel, Bern\x00\x00\x00\x07feature\x00\x00\x00\x1alaebe im burgereziel, bern\x00\x00\x00\x00\x00\x00\x89\x1c\x00\x00\x06\xac\x00\x00\x00\x12ARA REGION BERN AG\x00\x00\x00\x07feature\x00\x00\x01\x0835100 ara region bern ag herrenschwanden aare 37 mechanisch-biologische reinigung mit weitergehender p-elimination, nitrifikation und denitrifikation 115200 2500 4000 21000 38500 26950 85 10 85 10 85 2 ja 55 15 10 95 0 10 be i 350000 190446 2005 8.298 ch0000370000\x00\x00\x00\x00\x00\x03\x1a$\x00\x00\x06\xac\x00\x00\x00\x05Matte\x00\x00\x00\x07feature\x00\x00\x00\x18203300 matte bern, matte\x00\x00\x00\x00\x00\x00\x01\t\x00\x00\x06\xab\x00\x00\x00\x0eBERN FORSTHAUS\x00\x00\x00\x07feature\x00\x00\x00\x16bern forsthaus befodig\x00\x00\x00\x00\x00\x00\x04\x8e\x00\x00\x06\xa8\x00\x00\x00\x041166\x00\x00\x00\x07feature\x00\x00\x00\x0ebern 1166 2016\x00\x00\x00\x00\x00\x00\x01\x19\x00\x00\x06\xa3\x00\x00\x00\x10BERN (NULLPUNKT)\x00\x00\x00\x07feature\x00\x00\x00cbern _nullpunkt_ ch 1938 klass -0.76 -0.07 4 2.27 station mit klassischer messung _laenge / breite_\x00\x00\x00\x00\x00\x00\x01#\x00\x00\x06\xa2\x00\x00\x005Geologische Forschung und Anwendungen f\xc3\xbcr den Alltag\x00\x00\x00\x07feature\x00\x00\x00\xcbgeologische forschung und anwendungen fuer den alltag vulkane und ihr nutzen - welches gestein eignet sich fuer die lagerung von radioaktiven abfaellen und warum? - wie entstehen geologische karten? bern\x00\x00\x00\x00\x00\x00\x04\xea\x00\x00\x06\xa2\x00\x00\x00\x07BE S 20\x00\x00\x00\x07feature\x00\x00\x00\x12be s 20 stadt bern\x00\x00\x00\x00\x00\x05J2\x00\x00\x06\x9c\x00\x00\x00&Sperrung: Taatobel Nordseite (Berneck)\x00\x00\x00\x07feature\x00\x00\x00\xbasperrung: taatobel nordseite _berneck_ chemin impraticable: taatobel cote nord _berneck_ sentiero impraticabile: taatobel lato nord,berneck path impassable: taatobel north side _berneck_\x00\x00\x00\x00\x00\x05J\xc7\x00\x00\x06\x9b\x00\x00\x00@Umleitung Route 6, Sufers, Fahrtrichtung Spl\xc3\xbcgen-San Bernardino\x00\x00\x00\x07feature\x00\x00\x01*umleitung route 6, sufers, fahrtrichtung spluegen-san bernardino deviation de l\'itineraire no 6, sufers, en direction de spluegen\xe2\x80\x93san bernardino deviazione del percorso no 6, sufers, in direzione di spluegen\xe2\x80\x93san bernardino diversion of route 6, sufers, in direction of spluegen\xe2\x80\x93san bernardino\x00\x00\x00\x00\x00\x00\x00.\x00\x00\x06\x99\x00\x00\x00\x04Bern\x00\x00\x00\x07feature\x00\x00\x00\x89bern ausbau bahnhof schmalspur amenagement de la gare voie etroite ampliamento della stazione ferroviaria scartamento ridotto 71-w-06-001\x00\x00\x00\x00\x00\x00\t\x8b\x00\x00\x06\x98\x00\x00\x00"Bern Energiezentrale Forsthaus EWB\x00\x00\x00\x07feature\x00\x00\x00"bern energiezentrale forsthaus ewb\x00\x00\x00\x00\x00\x00\n\x1a\x00\x00\x06\x98\x00\x00\x00\x12Ara Region Bern Ag\x00\x00\x00\x07feature\x00\x00\x00\x12ara region bern ag\x00\x00\x00\x00\x00\x00\x18\xa9\x00\x00\x06\x94\x00\x00\x00\x1aAlpines Museum der Schweiz\x00\x00\x00\x07feature\x00\x00\x00 alpines museum der schweiz  bern\x00\x00\x00\x00\x00\x00\x07C\x00\x00\x06\x93\x00\x00\x00\x12Bern, Sch\xc3\xb6nausteg\x00\x00\x00\x07feature\x00\x00\x00\x1c1859 bern, schoenausteg aare\x00\x00\x00\x00\x00\x00\x00\x82\x00\x00\x06\x91\x00\x00\x008Doppelspurausbau Bern Frischingweg \xe2\x80\x93 Bern Weissenb\xc3\xbchl\x00\x00\x00\x07feature\x00\x00\x01\tdoppelspurausbau bern frischingweg \xe2\x80\x93 bern weissenbuehl doppelspurausbau bern frischingweg \xe2\x80\x93 bern weissenbuehl doppelspurausbau bern frischingweg \xe2\x80\x93 bern weissenbuehl sachplan verkehr, teil infrastruktur schiene _gesamtbericht_###ob 4.1 region bern 71-m-02-0057\x00\x00\x03\xe8\x00\x02\xfb\xb8\x00\x00\x00\x7f\x00\x00\x00\x03\x00\x00\x00\x06*bern*\x00\x01JW\x00\x01\xde\xa4\x00\x00\x00\x04bern\x00\x01\xb7.\x00\x02\x96\xad\x00\x00\x00\x03PRN\x00\x00\xd7\xc7\x00\x01c\r'
)

MOCK_QUERY_SOCK_1 = MockSocket(
    b'\x00\x00\x01\x1f\x00\x00\x027',
    b'\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x06detail\x00\x00\x00\x0egeom_quadindex\x00\x00\x00\x10\x00\x00\x00\nfeature_id\x00\x00\x00\x07\x00\x00\x00\x06detail\x00\x00\x00\x07\x00\x00\x00\x05label\x00\x00\x00\x07\x00\x00\x00\x06origin\x00\x00\x00\x07\x00\x00\x00\x0egeom_quadindex\x00\x00\x00\x07\x00\x00\x00\rgeom_st_box2d\x00\x00\x00\x07\x00\x00\x00\x12geom_st_box2d_lv95\x00\x00\x00\x07\x00\x00\x00\x04rank\x00\x00\x00\x01\x00\x00\x00\x01x\x00\x00\x00\x05\x00\x00\x00\x01y\x00\x00\x00\x05\x00\x00\x00\x06x_lv95\x00\x00\x00\x05\x00\x00\x00\x06y_lv95\x00\x00\x00\x05\x00\x00\x00\x03lat\x00\x00\x00\x05\x00\x00\x00\x03lon\x00\x00\x00\x05\x00\x00\x00\tzoomlevel\x00\x00\x00\x01\x00\x00\x00\x03num\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\xc6\x00\x01\x89N\x00\x00\x00\x03351\x00\x00\x00\x07bern be\x00\x00\x00\x10<b>Bern (BE)</b>\x00\x00\x00\x04gg25\x00\x00\x00\x03021\x00\x00\x00FBOX(589007.981000169 196443.17110866,604334.389999973 204343.59986848)\x00\x00\x00HBOX(2589007.98100017 1196443.17110866,2604334.38999997 1204343.59986848)\x00\x00\x00\x02HC\xb0\xb2I\x12&\x9dI\x92\x88\x16J\x1e\x9b\xa7B;\xd1x@\xedv@\xff\xff\xff\xff\x00\x00\x00\x01\x00\x00\x00\x04\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x04bern\x00\x00\xf7\xaf\x00\x01[E'
)

MOCK_QUERY_SOCK_2 = MockSocket(
    b'\x00\x00\x01\x1f\x00\x00\x05\xe0',
    b'\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x06detail\x00\x00\x00\x0egeom_quadindex\x00\x00\x00\x12\x00\x00\x00\nfeature_id\x00\x00\x00\x07\x00\x00\x00\x06detail\x00\x00\x00\x07\x00\x00\x00\x05label\x00\x00\x00\x07\x00\x00\x00\x06origin\x00\x00\x00\x07\x00\x00\x00\x0egeom_quadindex\x00\x00\x00\x07\x00\x00\x00\rgeom_st_box2d\x00\x00\x00\x07\x00\x00\x00\x12geom_st_box2d_lv95\x00\x00\x00\x07\x00\x00\x00\x04rank\x00\x00\x00\x01\x00\x00\x00\x01x\x00\x00\x00\x05\x00\x00\x00\x01y\x00\x00\x00\x05\x00\x00\x00\x06x_lv95\x00\x00\x00\x05\x00\x00\x00\x06y_lv95\x00\x00\x00\x05\x00\x00\x00\x03lat\x00\x00\x00\x05\x00\x00\x00\x03lon\x00\x00\x00\x05\x00\x00\x00\tzoomlevel\x00\x00\x00\x01\x00\x00\x00\x03num\x00\x00\x00\x01\x00\x00\x00\x08@groupby\x00\x00\x00\x01\x00\x00\x00\x06@count\x00\x00\x00\x01\x00\x00\x00\x04\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x01[\x00\x01\x88\xfc\x00\x00\x00\x10ch14uvag00040743\x00\x00\x00*bern, universitaet 8571357 haltestelle bus\x00\x00\x001<i>haltestellen_bus</i> <b>Bern, Universit\xc3\xa4t</b>\x00\x00\x00\tgazetteer\x00\x00\x00\x15021211313131220000303\x00\x00\x00HBOX(599768.000000008 199978.000214348,599768.000000008 199978.000214348)\x00\x00\x00HBOX(2599768.00000001 1199978.00021435,2599768.00000001 1199978.00021435)\x00\x00\x00\x08HCJ\x80I\x12m\x80I\x92{PJ\x1e\xad`B;\xcd\xb5@\xed\xf0P\xff\xff\xff\xff\x00\x00\x00\x01\x00\x00\x00\x08\x00\x00\x00\n\x00\x00\x00\x00\x00\x00\x00\xc6\x00\x01\x89N\x00\x00\x00\x03351\x00\x00\x00\x07bern be\x00\x00\x00\x10<b>Bern (BE)</b>\x00\x00\x00\x04gg25\x00\x00\x00\x03021\x00\x00\x00FBOX(589007.981000169 196443.17110866,604334.389999973 204343.59986848)\x00\x00\x00HBOX(2589007.98100017 1196443.17110866,2604334.38999997 1204343.59986848)\x00\x00\x00\x02HC\xb0\xb2I\x12&\x9dI\x92\x88\x16J\x1e\x9b\xa7B;\xd1x@\xedv@\xff\xff\xff\xff\x00\x00\x00\x01\x00\x00\x00\x02\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x02\x00\x01\x89t\x00\x00\x00\x012\x00\x00\x00\x07bern be\x00\x00\x00\x0b<b>Bern</b>\x00\x00\x00\x07kantone\x00\x00\x00\x010\x00\x00\x00HBOX(556240.840994776 130584.965007186,677745.364988658 243834.789996064)\x00\x00\x00HBOX(2556240.84099478 1130584.96500719,2677745.36498866 1243834.78999606)\x00\x00\x00\x04H5\x91PI\x15\xcf\x1dI\x90\xc4*J\x1f\x85\xc7B;L\x1f@\xf3\xbfF\xff\xff\xff\xff\x00\x00\x00\x01\x00\x00\x00\x04\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\xf6\x00\x01\x89v\x00\x00\x00\x03246\x00\x00\x00\x0fBern-Mittelland\x00\x00\x00\x16<b>Bern-Mittelland</b>\x00\x00\x00\x08district\x00\x00\x00\x03021\x00\x00\x00HBOX(575209.931000573 168848.668974539,622384.234999242 219079.768430131)\x00\x00\x00HBOX(2575209.93100057 1168848.66897454,2622384.23499924 1219079.76843013)\x00\x00\x00\x03H=m\xcbI\x13\x8c\xb6I\x91\xbf\xb9J\x1e\xf5.B;\x96f@\xef\xde\\\xff\xff\xff\xff\x00\x00\x00\x01\x00\x00\x00\x03\x00\x00\x00\x01\x00\x00\x00\x04\x00\x00\x00\x04\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x04bern\x00\x00\xf7\xaf\x00\x01[E'
)

MOCK_QUERY_SOCK_3 = MockSocket(
    b'\x00\x00\x01\x1f\x00\x00\x15T',
    b'\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x06detail\x00\x00\x00\x0egeom_quadindex\x00\x00\x00\x10\x00\x00\x00\nfeature_id\x00\x00\x00\x07\x00\x00\x00\x06detail\x00\x00\x00\x07\x00\x00\x00\x05label\x00\x00\x00\x07\x00\x00\x00\x06origin\x00\x00\x00\x07\x00\x00\x00\x0egeom_quadindex\x00\x00\x00\x07\x00\x00\x00\rgeom_st_box2d\x00\x00\x00\x07\x00\x00\x00\x12geom_st_box2d_lv95\x00\x00\x00\x07\x00\x00\x00\x04rank\x00\x00\x00\x01\x00\x00\x00\x01x\x00\x00\x00\x05\x00\x00\x00\x01y\x00\x00\x00\x05\x00\x00\x00\x06x_lv95\x00\x00\x00\x05\x00\x00\x00\x06y_lv95\x00\x00\x00\x05\x00\x00\x00\x03lat\x00\x00\x00\x05\x00\x00\x00\x03lon\x00\x00\x00\x05\x00\x00\x00\tzoomlevel\x00\x00\x00\x01\x00\x00\x00\x03num\x00\x00\x00\x01\x00\x00\x00\x10\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\xc6\x00\x01\x89N\x00\x00\x00\x03351\x00\x00\x00\x07bern be\x00\x00\x00\x10<b>Bern (BE)</b>\x00\x00\x00\x04gg25\x00\x00\x00\x03021\x00\x00\x00FBOX(589007.981000169 196443.17110866,604334.389999973 204343.59986848)\x00\x00\x00HBOX(2589007.98100017 1196443.17110866,2604334.38999997 1204343.59986848)\x00\x00\x00\x02HC\xb0\xb2I\x12&\x9dI\x92\x88\x16J\x1e\x9b\xa7B;\xd1x@\xedv@\xff\xff\xff\xff\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\xc9\x00\x01\x89N\x00\x00\x00\x03353\x00\x00\x00\x16bremgarten bei bern be\x00\x00\x00\x1f<b>Bremgarten bei Bern (BE)</b>\x00\x00\x00\x04gg25\x00\x00\x00\x03021\x00\x00\x00GBOX(598815.283999986 201901.089942302,600792.60400001 204121.301875178)\x00\x00\x00HBOX(2598815.28399999 1201901.08994231,2600792.60400001 1204121.30187518)\x00\x00\x00\x02HFA\x86I\x12f\xceI\x92\xda1J\x1e\xab\xb3B;\xe9\xac@\xed\xe4\xc3\xff\xff\xff\xff\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\xcc\x00\x01\x89N\x00\x00\x00\x03356\x00\x00\x00\x10muri bei bern be\x00\x00\x00\x19<b>Muri bei Bern (BE)</b>\x00\x00\x00\x04gg25\x00\x00\x00\x070213002\x00\x00\x00HBOX(602320.709999972 196070.738119948,606561.147999936 199977.171246593)\x00\x00\x00HBOX(2602320.70999997 1196070.73811995,2606561.14799994 1199977.17124659)\x00\x00\x00\x02HAe\xdfI\x13\x9e\x95I\x92>\xbcJ\x1e\xf9\xa5B;\xbb\xd6@\xef\xfdn\xff\xff\xff\xff\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\xd0\x00\x01\x89N\x00\x00\x00\x03360\x00\x00\x00\x12wohlen bei bern be\x00\x00\x00\x1b<b>Wohlen bei Bern (BE)</b>\x00\x00\x00\x04gg25\x00\x00\x00\x06021211\x00\x00\x00GBOX(587831.182999835 200975.086970439,598245.08499997 205985.374819303)\x00\x00\x00GBOX(2587831.18299984 1200975.08697044,2598245.08499997 1205985.3748193)\x00\x00\x00\x02HF\xb0kI\x10\xcc^I\x92\xe8\rJ\x1eE\x17B;\xed\xb8@\xeb!\xaa\xff\xff\xff\xff\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\xf6\x00\x01\x89v\x00\x00\x00\x03246\x00\x00\x00\x0fBern-Mittelland\x00\x00\x00\x16<b>Bern-Mittelland</b>\x00\x00\x00\x08district\x00\x00\x00\x03021\x00\x00\x00HBOX(575209.931000573 168848.668974539,622384.234999242 219079.768430131)\x00\x00\x00HBOX(2575209.93100057 1168848.66897454,2622384.23499924 1219079.76843013)\x00\x00\x00\x03H=m\xcbI\x13\x8c\xb6I\x91\xbf\xb9J\x1e\xf5.B;\x96f@\xef\xde\\\xff\xff\xff\xff\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x02\x00\x01\x89t\x00\x00\x00\x012\x00\x00\x00\x07bern be\x00\x00\x00\x0b<b>Bern</b>\x00\x00\x00\x07kantone\x00\x00\x00\x010\x00\x00\x00HBOX(556240.840994776 130584.965007186,677745.364988658 243834.789996064)\x00\x00\x00HBOX(2556240.84099478 1130584.96500719,2677745.36498866 1243834.78999606)\x00\x00\x00\x04H5\x91PI\x15\xcf\x1dI\x90\xc4*J\x1f\x85\xc7B;L\x1f@\xf3\xbfF\xff\xff\xff\xff\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x01[\x00\x01\x88\xfc\x00\x00\x00\x10ch14uvag00040743\x00\x00\x00*bern, universitaet 8571357 haltestelle bus\x00\x00\x001<i>haltestellen_bus</i> <b>Bern, Universit\xc3\xa4t</b>\x00\x00\x00\tgazetteer\x00\x00\x00\x15021211313131220000303\x00\x00\x00HBOX(599768.000000008 199978.000214348,599768.000000008 199978.000214348)\x00\x00\x00HBOX(2599768.00000001 1199978.00021435,2599768.00000001 1199978.00021435)\x00\x00\x00\x08HCJ\x80I\x12m\x80I\x92{PJ\x1e\xad`B;\xcd\xb5@\xed\xf0P\xff\xff\xff\xff\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x03\xc4\x00\x01\x88\xfc\x00\x00\x00\x10ch14uvag00040650\x00\x00\x00/bern, gaebelbach 8590045 haltestelle bus / tram\x00\x00\x006<i>haltestellen_bus / tram</i> <b>Bern, G\xc3\xa4belbach</b>\x00\x00\x00\tgazetteer\x00\x00\x00\x15021211303300003212201\x00\x00\x00HBOX(595350.000000008 199638.000011062,595350.000000008 199638.000011062)\x00\x00\x00HBOX(2595350.00000001 1199638.00001106,2595350.00000001 1199638.00001106)\x00\x00\x00\x08HB\xf5\x80I\x11Y`I\x92p\xb0J\x1ehXB;\xca\x8f@\xec\x14\xeb\xff\xff\xff\xff\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x04\xd4\x00\x01\x88\xfc\x00\x00\x00\x10ch14uvag00222333\x00\x00\x001bern muensterplattform 8500258 haltestelle aufzug\x00\x00\x008<i>haltestellen_aufzug</i> <b>Bern M\xc3\xbcnsterplattform</b>\x00\x00\x00\tgazetteer\x00\x00\x00\x15021300202300320022122\x00\x00\x00FBOX(601056.999999997 199499.00001524,601056.999999997 199499.00001524)\x00\x00\x006BOX(2601057 1199499.00001524,2601057 1199499.00001524)\x00\x00\x00\x08HB\xd2\xc0I\x12\xbe\x10I\x92lXJ\x1e\xc1\x84B;\xc9K@\xee{\x03\xff\xff\xff\xff\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x05A\x00\x01\x88\xfc\x00\x00\x00\x10ch14uvag00040645\x00\x00\x00*bern, faehrstrasse 8590074 haltestelle bus\x00\x00\x001<i>haltestellen_bus</i> <b>Bern, F\xc3\xa4hrstrasse</b>\x00\x00\x00\tgazetteer\x00\x00\x00\x15021300022222113110100\x00\x00\x00HBOX(600229.000000003 202704.999917964,600229.000000003 202704.999917964)\x00\x00\x006BOX(2600229 1202704.99991797,2600229 1202704.99991797)\x00\x00\x00\x08HE\xf4@I\x12\x8aPI\x92\xd0\x88J\x1e\xb4\x94B;\xe6\xd3@\xee!\xed\xff\xff\xff\xff\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x05\x81\x00\x01\x88\xfc\x00\x00\x00\x10ch14uvag00040679\x00\x00\x00*bern, laeuferplatz 8590120 haltestelle bus\x00\x00\x001<i>haltestellen_bus</i> <b>Bern, L\xc3\xa4uferplatz</b>\x00\x00\x00\tgazetteer\x00\x00\x00\x15021300202132201121020\x00\x00\x00HBOX(601453.999999999 199796.000006205,601453.999999999 199796.000006205)\x00\x00\x006BOX(2601454 1199796.00000621,2601454 1199796.00000621)\x00\x00\x00\x08HC\x1d\x00I\x12\xd6\xe0I\x92u\xa0J\x1e\xc7\xb8B;\xcc\x07@\xee\xa5\xbd\xff\xff\xff\xff\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x06u\x00\x01\x88\xfc\x00\x00\x00\x10ch14uvag00040746\x00\x00\x002bern, viktoriaplatz 8590021 haltestelle bus / tram\x00\x00\x009<i>haltestellen_bus / tram</i> <b>Bern, Viktoriaplatz</b>\x00\x00\x00\tgazetteer\x00\x00\x00\x15021300202100220310003\x00\x00\x00HBOX(600960.000000002 200433.999986817,600960.000000002 200433.999986817)\x00\x00\x006BOX(2600960 1200433.99998682,2600960 1200433.99998682)\x00\x00\x00\x08HC\xbc\x80I\x12\xb8\x00I\x92\x89\x90J\x1e\xc0\x00B;\xd1\xe8@\xeep\x97\xff\xff\xff\xff\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x06z\x00\x01\x88\xfc\x00\x00\x00\x10ch14uvag00040627\x00\x00\x00-bern, bruennenstrasse 8590108 haltestelle bus\x00\x00\x004<i>haltestellen_bus</i> <b>Bern, Br\xc3\xbcnnenstrasse</b>\x00\x00\x00\tgazetteer\x00\x00\x00\x15021211303331023312222\x00\x00\x00HBOX(596067.000000018 199109.000027153,596067.000000018 199109.000027153)\x00\x00\x00HBOX(2596067.00000002 1199109.00002715,2596067.00000002 1199109.00002715)\x00\x00\x00\x08HBq@I\x11\x860I\x92`(J\x1es\x8cB;\xc5\xb0@\xecb\x1b\xff\xff\xff\xff\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x06\xd6\x00\x01\x88\xfc\x00\x00\x00\x10ch14uvag00091169\x00\x00\x00Bbern, wallgasse _vzw_ 8519403 verzweigung, abzweigung, spaltweiche\x00\x00\x001<i>haltestellen_</i> <b>Bern, Wallgasse (Vzw)</b>\x00\x00\x00\tgazetteer\x00\x00\x00\x15021300202200223001232\x00\x00\x004BOX(600034 199479.000015843,600034 199479.000015843)\x00\x00\x006BOX(2600034 1199479.00001585,2600034 1199479.00001585)\x00\x00\x00\x08HB\xcd\xc0I\x12~ I\x92k\xb8J\x1e\xb1\x88B;\xc9\x1c@\xee\x0c\xf0\xff\xff\xff\xff\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x06\xd8\x00\x01\x88\xfc\x00\x00\x00\x10ch14uvag00040694\x00\x00\x00.bern, morgartenstrasse 8588999 haltestelle bus\x00\x00\x005<i>haltestellen_bus</i> <b>Bern, Morgartenstrasse</b>\x00\x00\x00\tgazetteer\x00\x00\x00\x15021300200310130331020\x00\x00\x00HBOX(601608.000000012 201480.999955041,601608.000000012 201480.999955041)\x00\x00\x00HBOX(2601608.00000001 1201480.99995504,2601608.00000001 1201480.99995504)\x00\x00\x00\x08HD\xc2@I\x12\xe0\x80I\x92\xaaHJ\x1e\xca B;\xdb\x8c@\xee\xb6[\xff\xff\xff\xff\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x07&\x00\x01\x88\xfc\x00\x00\x00\x10ch14uvag00040709\x00\x00\x00-bern, riedbachstrasse 8591756 haltestelle bus\x00\x00\x004<i>haltestellen_bus</i> <b>Bern, Riedbachstrasse</b>\x00\x00\x00\tgazetteer\x00\x00\x00\x15021211303310201100021\x00\x00\x00HBOX(595826.000000009 199569.000013151,595826.000000009 199569.000013151)\x00\x00\x00HBOX(2595826.00000001 1199569.00001315,2595826.00000001 1199569.00001315)\x00\x00\x00\x08HB\xe4@I\x11w I\x92n\x88J\x1eo\xc8B;\xc9\xed@\xecH$\xff\xff\xff\xff\x00\x00\x00\x01\x00\x00\x00\x10\x00\x00\x00\x10\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x04bern\x00\x00\xf7\xaf\x00\x01[E'
)

MOCK_UPDATE_ATTRIBUTES_SOCK = MockSocket(b'\x00\x00\x01\x00\x00\x00\x00\x04', b'\x00\x00\x00\x01')

MOCK_QUERY_BUILD_KEYWORDS_SOCK = MockSocket(
    b'\x00\x00\x01\x00\x00\x00\x00H',
    b'\x00\x00\x00\x02\x00\x00\x00\x0fseftigenstrasse\x00\x00\x00\x0fseftigenstrasse\x00\x00\x01v\x00\x00\x01v\x00\x00\x00\x03264\x00\x00\x00\x03264\x00\x00\x00\xd7\x00\x00\x00\xd7'
)

MOCK_QUERY_OVERRIDES_SOCK = MockSocket(
    b'\x00\x00\x01\x1f\x00\x00\x01k',
    b'\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x06detail\x00\x00\x00\x0egeom_quadindex\x00\x00\x00\x13\x00\x00\x00\nfeature_id\x00\x00\x00\x07\x00\x00\x00\x06detail\x00\x00\x00\x07\x00\x00\x00\x06origin\x00\x00\x00\x07\x00\x00\x00\x0egeom_quadindex\x00\x00\x00\x07\x00\x00\x00\rgeom_st_box2d\x00\x00\x00\x07\x00\x00\x00\x12geom_st_box2d_lv95\x00\x00\x00\x07\x00\x00\x00\x04rank\x00\x00\x00\x01\x00\x00\x00\x01x\x00\x00\x00\x05\x00\x00\x00\x01y\x00\x00\x00\x05\x00\x00\x00\x06y_lv95\x00\x00\x00\x05\x00\x00\x00\x06x_lv95\x00\x00\x00\x05\x00\x00\x00\x03lat\x00\x00\x00\x05\x00\x00\x00\x03lon\x00\x00\x00\x05\x00\x00\x00\x03num\x00\x00\x00\x01\x00\x00\x00\tzoomlevel\x00\x00\x00\x01\x00\x00\x00\x05label\x00\x00\x00\x07\x00\x00\x00\x08@groupby\x00\x00\x00\x06\x00\x00\x00\x06@count\x00\x00\x00\x01\x00\x00\x00\t@distinct\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x04bern\x00\x00\xf7\xaf\x00\x01[E'
)