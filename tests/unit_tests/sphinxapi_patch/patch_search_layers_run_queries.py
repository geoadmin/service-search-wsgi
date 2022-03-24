# pylint: disable=line-too-long
results = [{
    'error': '',
    'warning': 'Fields specified in field_weights option not found: [@title @detail @layer]',
    'status': 3,
    'fields': ['title', 'detail', 'layer', 'topics', 'staging', 'id'],
    'attrs': [['label', 7], ['origin', 7], ['title', 7], ['detail', 7], ['layer', 7], ['lang', 7],
              ['topics', 7], ['staging', 7]],
    'matches': [
        {
            'id': 1275,
            'weight': 91,
            'attrs': {
                'label': '<b>Sperrungen Wanderwege</b>',
                'origin': 'layer',
                'title': 'sperrungen wanderwege',
                'detail':
                    'sperrungen / umleitungen wanderwege und wanderland | der datensatz enthaelt wegsperrungen und -umleitungen auf dem wanderwegnetz und den wanderland-routen der schweiz und des fuerstentums liechtenstein, die den schweizer wanderwegen und ihren kantonalen wanderweg-fachorganisationen gemeldet wurden. der datensatz ergaenzt den geobasisdatensatz "wanderwege" _swisstlm3d wanderwege_ und "wanderland" _langsamverkehr – wanderland schweiz_ und wird durch das bundesamt fuer strassen astra, das bundesamt fuer landestopografie swisstopo, die schweizer wanderwege, schweizmobil und die kantone publiziert.link zu disclaimer: https://www.schweizer-wanderwege.ch/de/hinweis-zur-unvollstaendigkeit-der-daten | swisstopo | bundesamt fuer landestopografie swisstopo | bundesamt fuer strassen, kanton',
                'layer': 'ch.astra.wanderland-sperrungen_umleitungen',
                'lang': 'de',
                'topics': 'api,astra,ech,inspire,wms-bgdi',
                'staging': 'prod'
            }
        },
        {
            'id': 851,
            'weight': 60,
            'attrs': {
                'label': '<b>Wanderland</b>',
                'origin': 'layer',
                'title': 'wanderland',
                'detail':
                    'langsamverkehr - wanderland schweiz | "wanderland schweiz" von schweizmobil umfasst die nationalen, regionalen und lokalen wander- und berg-wanderrouten sowie die hindernisfreien wege der schweiz und des fuerstentums liechtenstein. dieser da-tensatz wird gemaess geoinformationsverordnung als teil des geobasisdatensatz "fuss- und wanderwegnet-ze" publiziert. er wird in zusammenarbeit mit dem bundesamt fuer strassen astra, den schweizer wander-wegen, schweizmobil und den kantonen erarbeitet. | swisstopo | bundesamt fuer landestopografie swisstopo | bundesamt fuer strassen, kanton',
                'layer': 'ch.astra.wanderland',
                'lang': 'de',
                'topics': 'api,astra,ech,inspire,kgs,schule,wms-bgdi',
                'staging': 'prod'
            }
        },
        {
            'id': 991,
            'weight': 56,
            'attrs': {
                'label': '<b>Einteilung Wanderkarte 50 Papier</b>',
                'origin': 'layer',
                'title': 'einteilung wanderkarte 50 papier',
                'detail':
                    'papierkarte wanderkarten serie "t" 1:50\'000 | offizielle karte der schweizer wanderwege: das gesamte wanderwegnetz der schweiz auf 59 einzelblaettern.die karten zeigen die signalisierten wander-, bergwander- und alpinwanderwege und nuetzliche informationen wie oev-haltestellen, sehenswerte orte, aussichtstuerme, abgelegene gasthoefe und parkplaetze. zudem sind die wanderrouten von schweizmobil markiert. | swisstopo | bundesamt fuer landestopografie swisstopo | bundesamt fuer landestopografie swisstopo',
                'layer': 'ch.swisstopo.wanderkarte50_papier.metadata',
                'lang': 'de',
                'topics': 'ech,inspire,swisstopo,wms-bgdi',
                'staging': 'prod'
            }
        },
        {
            'id': 279,
            'weight': 54,
            'attrs': {
                'label': '<b>Wanderwege</b>',
                'origin': 'layer',
                'title': 'wanderwege',
                'detail':
                    'swisstlm3d wanderwege | swisstlm3d wanderwege enthaelt die signalisierten wanderrouten der schweiz und des fuerstentums liechtenstein. der datensatz wird in zusammenarbeit mit dem bundesamt fuer strassen astra, schweizmobil, schweizer wanderwege und den kantonen publiziert. swisstlm3d wanderwege bildet einen teil des datensatzes swisstlm3d. | swisstlm3d | swisstopo | bundesamt fuer landestopografie swisstopo | bundesamt fuer landestopografie swisstopo',
                'layer': 'ch.swisstopo.swisstlm3d-wanderwege',
                'lang': 'de',
                'topics':
                    'api,astra,blw,ech,emapis,inspire,kgs,schule,swissmaponline,swisstopo,wms-bgdi,wms-swisstopowms',
                'staging': 'prod'
            }
        },
        {
            'id': 1380,
            'weight': 54,
            'attrs': {
                'label': '<b>Amphibienwanderungen mit Konflikten</b>',
                'origin': 'layer',
                'title': 'amphibienwanderungen mit konflikten',
                'detail':
                    'amphibienwanderungen mit verkehrskonflikten | seit mitte der 1950er jahre nahmen amphibienmortalitaeten auf strassen drastisch zu. jaehrlich ueberqueren in der schweiz hunderttausende amphibien strassen auf ihren wanderungen zwischen landhabitaten und laichgewaessern und erleiden ohne schutzmassnahmen dabei oft den strassentod. dies ist nicht nur ein sicherheitsproblem fuer den verkehr, sondern verursacht auch massive populationsrueckgaenge bei amphibien. die wanderungen innerhalb von populationen finden auf mehr oder weniger immer denselben wanderrouten statt. sie sind saisonal bedingt und erlauben eine temporaere nutzung verschiedener, raeumlich getrennter habitatstypen. fuer den fortbestand der populationen sind diese wanderbewegungen unerlaesslich. info fauna karch fuehrt eine datenbank zu den konfliktstellen der amphibienwanderungen mit der verkehrsinfrastruktur. zurzeit sind knapp 2000 konfliktstellenstandorte bekannt, die in der fachsprache «amphibien-zugstellen» genannt werden. je nach groesse der amphibienpopulation, der verkehrsdichte und den moeglichkeiten vor ort werden hierin enthaltene schutzmassnahmen umgesetzt, wie z.b. die installation von kleintiertunneln und leiteinrichtungen, temporaere amphibienzaeune, temporaere strassensperrungen oder temporaere patrouillen. die bekannten konfliktstellenstandorte der amphibienwanderungen in der schweiz sind in diesem geodatensatz enthalten und visualisierbar. | swisstopo | bundesamt fuer landestopografie swisstopo | bundesamt fuer umwelt bafu',
                'layer': 'ch.bafu.amphibienwanderung-verkehrskonflikte',
                'lang': 'de',
                'topics': 'api,bafu,ech,inspire,wms-bgdi',
                'staging': 'prod'
            }
        },
        {
            'id': 891,
            'weight': 48,
            'attrs': {
                'label': "<b>Einteilung Wanderkarte 1:33'333 Papier</b>",
                'origin': 'layer',
                'title': "einteilung wanderkarte 1:33'333 papier",
                'detail':
                    "papierkarte: wanderkarten 1:33'333 | die wasser- und reissfeste karte, die sie nie im stich laesst! diese wanderkarten decken bekannte und beliebte wanderregionen der schweiz ab. sie sind aeusserst handlich, beidseitig bedruckt und passen mit einer abmessung von 11 x 17,5cm in jede jackentasche. dank der vergroesserung des massstabes auf 1:33 333 und der deutlichen darstellung der wanderwege, sind die karten noch besser lesbar. jede karte beinhaltet drei wandervorschlaege mit unterschiedlichen anforderungen. | swisstopo | bundesamt fuer landestopografie swisstopo | bundesamt fuer landestopografie swisstopo | shop",
                'layer': 'ch.swisstopo.wanderkarte33_papier.metadata',
                'lang': 'de',
                'topics': 'ech,inspire,swisstopo,wms-bgdi',
                'staging': 'prod'
            }
        },
        {
            'id': 195,
            'weight': 42,
            'attrs': {
                'label': '<b>Amphibien Wanderobjekte</b>',
                'origin': 'layer',
                'title': 'amphibien wanderobjekte',
                'detail':
                    'bundesinventar der amphibienlaichgebiete von nationaler bedeutung - wanderobjekte | in der schweiz leben heute 19 amphibienarten – fast alle befinden sich auf der roten liste der gefaehrdeten tierarten. die flaeche der feuchtgebiete als lebensraum der amphibien schrumpfte in den letzten 100 jahren auf weniger als einen zehntel zusammen. die noch erhaltenen lebensraeume sollten deshalb gesichert werden. als laichgewaesser bevorzugen die meisten arten stehende kleingewaesser wie tuempel und weiher. neben kleineren tuempeln bis zu grossen feuchtgebietskomplexen bilden kies- und lehmgruben einen wichtigen anteil _rund ein fuenftel der gesamtobjekte_ des inventars. im laufe der nutzung haben sie sich zu schuetzenswerten naturnahen standorten entwickelt.die ortsfesten objekte sind in zwei verschiedene bereiche eingeteilt: der bereich a ist dem naturschutz unterstellt. der bereich b umfasst den engeren bereich der landlebensraeume und die pufferzonen. es sind meist land- und forstwirtschaftlich genutzte flaechen. die wanderobjekte beinhalten genutzte gruben, innerhalb deren die dynamische voraussetzung fuer eine erhaltung der vorkommenden amphibienbestaende erhalten werden soll. als viertes bundesinventar gemaess art. 18a nhg setzte der bundesrat 2001 das bundesinventar der amphibienlaichgebiete mit 701 objekten in kraft, welches in den jahren 2003, 2007 und 2017 revidiert wurde. aktuell sind 929 objekte _835 ortsfeste und 94 wanderobjekte_ in kraft. weiter sind im anhang 3 30 objekte aufgefuehrt deren perimeter noch nicht definitiv bereinigt sind. deren schutz richtet sich bis zum entscheid ihrer aufnahme in anhang 1 oder 2 nach artikel 29 absatz 1 buchstabe a der natur- und heimatschutzverordnung _nhv_ und nach artikel 10 der amphibienlaichgebiete-verordnung _algv_. der rechtverbindliche massstab fuer die lage des schutzobjektes ist derjenige im objektblatt. die festlegung des genauen grenzverlaufs erfolgt durch die kantone. | bundesinventar der amphibienlaichgebiete von nationaler bedeutung - wanderobjekte | swisstopo | bundesamt fuer landestopografie swisstopo | bundesamt fuer umwelt bafu',
                'layer': 'ch.bafu.bundesinventare-amphibien_wanderobjekte',
                'lang': 'de',
                'topics': 'api,bafu,blw,ech,emapis,energie,inspire,sachplan,swissmaponline,wms-bgdi',
                'staging': 'prod'
            }
        },
        {
            'id': 1351,
            'weight': 32,
            'attrs': {
                'label': '<b>Bilddokumentation Landschaftswandel</b>',
                'origin': 'layer',
                'title': 'bilddokumentation landschaftswandel',
                'detail':
                    'landschaftswandel in der schweiz | die arealstatistik der schweiz erzeugt nicht nur statistische daten, sondern sie dokumentiert auch landschaftsveraenderungen. waehrend den arbeiten an den arealstatistik 2004/09 und 2013/18 wurden bilddokumentationen hergestellt, georeferenziert und nach einer eigenen nomenklatur erfasst. diese illustrieren den landschaftswandel in der schweiz ueber 33 jahre mit vier bzw. ueber 24 jahre mit drei luftbildausschnitten. das bundesamt fuer statistik macht nun gut 1500 bildvergleiche auf dem geoportal des bundes einer breiten oeffentlichkeit zugaenglich. die arealstatistik der schweiz liefert mit den erhebungen 1979/85, 1992/97, 2004/09 und 2013/18 resultate zum zustand und zu den veraenderungen von siedlungsflaechen, wald, gehoelzen, aeckern, wiesen, weiden, gewaessern, gletschern und von vielen weiteren nutzungen. sie vermittelt das wandelnde bild des mosaiks der flaechenverhaeltnisse der bodenbedeckung und -nutzung ueber die ganze schweiz, auch in ihrer regionalen und lokalen geografischen differenzierung. | arealstatistik nach nomenklatur 2004 | swisstopo | bundesamt fuer landestopografie swisstopo | bundesamt fuer statistik',
                'layer': 'ch.bfs.landschaftswandel',
                'lang': 'de',
                'topics': 'api,bfs,ech,inspire,wms-bgdi',
                'staging': 'prod'
            }
        },
        {
            'id': 876,
            'weight': 30,
            'attrs': {
                'label': '<b>Einteilung Wanderkarte 25 Papier</b>',
                'origin': 'layer',
                'title': 'einteilung wanderkarte 25 papier',
                'detail':
                    "papierkarte: wanderkarte weg der schweiz 1:25'000 | zur 700-jahr-feier der eidgenossenschaft wurde der «weg der schweiz» rund um den urnersee erstellt. die offizielle wanderkarte im massstab 1:25'000 ist reich an details und aeusserst praezise. sie zeigt den routenverlauf des weges mit angabe der kantonsabschnitte, verpflegungs- und unterkunftsmoeglichkeiten, aussichtspunkten etc. | swisstopo | bundesamt fuer landestopografie swisstopo | bundesamt fuer landestopografie swisstopo | shop",
                'layer': 'ch.swisstopo.wanderkarte25-zus_papier.metadata',
                'lang': 'de',
                'topics': 'ech,inspire,swisstopo,wms-bgdi',
                'staging': 'prod'
            }
        },
        {
            'id': 1267,
            'weight': 27,
            'attrs': {
                'label': '<b>Schneeschuhwandern</b>',
                'origin': 'layer',
                'title': 'schneeschuhwandern',
                'detail':
                    'langsamverkehr - schneeschuhwandern | der datensatz «schneeschuhwandern» umfasst die best-of-auswahl von schweizmobil aus den signalisierten schneeschuhtrails der schweiz und des fuerstentums liechtenstein. diese auswahl wird mit den kantonen und dem fuerstentum liechtenstein koordiniert. | swisstopo | bundesamt fuer landestopografie swisstopo | bundesamt fuer landestopografie swisstopo',
                'layer': 'ch.swisstopo.schneeschuhwandern',
                'lang': 'de',
                'topics': 'api,ech,inspire,schneesport,schule,wms-bgdi',
                'staging': 'prod'
            }
        },
        {
            'id': 1217,
            'weight': 22,
            'attrs': {
                'label': '<b>Nicht-verholzte Biomassen</b>',
                'origin': 'layer',
                'title': 'nicht-verholzte biomassen',
                'detail':
                    'nachhaltiges potenzial der nicht-verholzten biomassenressourcen fuer bioenergie in der schweiz auf gemeindeebene | biomasse ist eine erneuerbare energiequelle, die in verschiedene energieformen umgewandelt werden kann: waerme, strom, biogas oder fluessige treibstoffe. biomasse ist meist speicherbar und kann daher verwendet werden, um die schwankende energieproduktion von wind und sonne auszugleichen. nicht-verholzte arten von biomasse wurden mit methodisch vergleichbaren ansaetzen untersucht: hofduenger, nebenprodukte aus dem landwirtschaftliche pflanzenbau, organischer anteil kehricht, gruengut aus haushalt und landschaft, organischen abfaelle aus industrie und gewerbe und klaerschlamm. im rahmen der umsetzung der energiestrategie 2050 sieht die schweizer regierung eine massive erhoehung des anteils der erneuerbaren energien vor. das schweizerische kompetenzzentrum fuer energieforschung _sccer_ biosweet _biomass for swiss energy future_ sucht nach loesungen fuer die technischen, sozialen und politischen herausforderungen des energiewandels im bereich biomasse. die eidgenoessische forschungsanstalt fuer wald, schnee und landschaft wsl hat das potenzial wichtiger biomassenressourcen in der schweiz quantifiziert und lokalisiert, insbesondere im hinblick auf ihre nachhaltige verfuegbarkeit. die ergebnisse dienen als grundlage fuer _i_ die optimierung von umwandlungsprozessen unter beruecksichtigung technologischer entwicklungen und _ii_ die identifizierung vielversprechender biomassenutzungspfade und der besten standorte fuer deren umsetzung. die daten _https://www.envidat.ch/dataset/swiss-biomass-potentials_ und ein detaillierter bericht sind online verfuegbar _https://www.wsl.ch/de/publikationen/biomassepotenziale-der-schweiz-fuer-die-energetische-nutzung-ergebnisse-des-schweizerischen-energiek.html_. diese karte zeigt das nachhaltige potenzial _maximale menge an national produzierter biomasse, die nach abzug oekologischer, wirtschaftlicher, rechtlicher und politischer restriktionen genutzt werden kann_ der nicht verholzten biomassen fuer bioenergie in der schweiz auf gemeindeebene in primaerenergie _maximale menge an energie, die in einer ressource ohne umwandlung verfuegbar ist_ in petajoule. | swisstopo | bundesamt fuer landestopografie swisstopo | bundesamt fuer energie',
                'layer': 'ch.bfe.biomasse-nicht-verholzt',
                'lang': 'de',
                'topics': 'api,ech,energie,inspire,schule,wms-bgdi',
                'staging': 'prod'
            }
        },
        {
            'id': 1218,
            'weight': 22,
            'attrs': {
                'label': '<b>Verholzte Biomassen</b>',
                'origin': 'layer',
                'title': 'verholzte biomassen',
                'detail':
                    'nachhaltiges potenzial der verholzten biomassenressourcen fuer bioenergie in der schweiz auf gemeindeebene | biomasse ist eine erneuerbare energiequelle, die in verschiedene energieformen umgewandelt werden kann: waerme, strom, biogas oder fluessige treibstoffe. biomasse ist meist speicherbar und kann daher verwendet werden, um die schwankende energieproduktion von wind und sonne auszugleichen. verholzte arten von biomassen wurden mit methodisch vergleichbaren ansaetzen untersucht: waldholz, flurholz, restholz und altholz.im rahmen der umsetzung der energiestrategie 2050 sieht die schweizer regierung eine massive erhoehung des anteils der erneuerbaren energien vor. das schweizerische kompetenzzentrum fuer energieforschung _sccer_ biosweet _biomass for swiss energy future_ sucht nach loesungen fuer die technischen, sozialen und politischen herausforderungen des energiewandels im bereich biomasse. die eidgenoessische forschungsanstalt fuer wald, schnee und landschaft wsl hat das potenzial wichtiger biomasse-ressourcen in der schweiz quantifiziert und lokalisiert, insbesondere im hinblick auf ihre nachhaltige verfuegbarkeit. die ergebnisse dienen als grundlage fuer _i_ die optimierung von umwandlungsprozessen unter beruecksichtigung technologischer entwicklungen und _ii_ die identifizierung vielversprechender biomassenutzungspfade und der besten standorte fuer deren umsetzung. die daten _https://www.envidat.ch/dataset/swiss-biomass-potentials_ und ein detaillierter bericht sind online verfuegbar _https://www.wsl.ch/de/publikationen/biomassepotenziale-der-schweiz-fuer-die-energetische-nutzung-ergebnisse-des-schweizerischen-energiek.html_. diese karte zeigt das nachhaltige potenzial _maximale menge an national produzierter biomasse, die nach abzug oekologischer, wirtschaftlicher, rechtlicher und politischer restriktionen genutzt werden kann_ der verholzten biomassen fuer die bioenergie in der schweiz auf gemeindeebene in primaerenergie _maximale menge an energie, die in einer ressource ohne umwandlung verfuegbar ist_ in petajoule. | swisstopo | bundesamt fuer landestopografie swisstopo | bundesamt fuer energie',
                'layer': 'ch.bfe.biomasse-verholzt',
                'lang': 'de',
                'topics': 'api,ech,energie,inspire,schule,wms-bgdi',
                'staging': 'prod'
            }
        },
        {
            'id': 320,
            'weight': 18,
            'attrs': {
                'label': '<b>Amphibien Ortsfeste Objekte</b>',
                'origin': 'layer',
                'title': 'amphibien ortsfeste objekte',
                'detail':
                    'bundesinventar der amphibienlaichgebiete von nationaler bedeutung - ortsfeste objekte | in der schweiz leben heute 19 amphibienarten – fast alle befinden sich auf der roten liste der gefaehrdeten tierarten. die flaeche der feuchtgebiete als lebensraum der amphibien schrumpfte in den letzten 100 jahren auf weniger als einen zehntel zusammen. die noch erhaltenen lebensraeume sollten deshalb gesichert werden. als laichgewaesser bevorzugen die meisten arten stehende kleingewaesser wie tuempel und weiher. neben kleineren tuempeln bis zu grossen feuchtgebietskomplexen bilden kies- und lehmgruben einen wichtigen anteil _rund ein fuenftel der gesamtobjekte_ des inventars. im laufe der nutzung haben sie sich zu schuetzenswerten naturnahen standorten entwickelt.die ortsfesten objekte sind in zwei verschiedene bereiche eingeteilt: der bereich a ist dem naturschutz unterstellt. der bereich b umfasst den engeren bereich der landlebensraeume und die pufferzonen. es sind meist land- und forstwirtschaftlich genutzte flaechen. die wanderobjekte beinhalten genutzte gruben, innerhalb deren die dynamische voraussetzung fuer eine erhaltung der vorkommenden amphibienbestaende erhalten werden soll. als viertes bundesinventar gemaess art. 18a nhg setzte der bundesrat 2001 das bundesinventar der amphibienlaichgebiete mit 701 objekten in kraft, welches in den jahren 2003, 2007 und 2017 revidiert wurde. aktuell sind 929 objekte _835 ortsfeste und 94 wanderobjekte_ in kraft. weiter sind im anhang 3 30 objekte aufgefuehrt deren perimeter noch nicht definitiv bereinigt sind. deren schutz richtet sich bis zum entscheid ihrer aufnahme in anhang 1 oder 2 nach artikel 29 absatz 1 buchstabe a der natur- und heimatschutzverordnung _nhv_ und nach artikel 10 der amphibienlaichgebiete-verordnung _algv_. der rechtverbindliche massstab fuer die lage des schutzobjektes ist derjenige im objektblatt. die festlegung des genauen grenzverlaufs erfolgt durch die kantone. | bundesinventar der amphibienlaichgebiete von nationaler bedeutung - ortsfeste objekte | swisstopo | bundesamt fuer landestopografie swisstopo | bundesamt fuer umwelt bafu',
                'layer': 'ch.bafu.bundesinventare-amphibien',
                'lang': 'de',
                'topics':
                    'api,are,bafu,blw,ech,emapis,energie,inspire,sachplan,schule,swissmaponline,wms-bgdi',
                'staging': 'prod'
            }
        },
        {
            'id': 838,
            'weight': 18,
            'attrs': {
                'label': '<b>Geowege</b>',
                'origin': 'layer',
                'title': 'geowege',
                'detail':
                    'erlebnis geologie: geowege | geotourismus erschliesst erdgeschichtliche und landschaftliche besonderheiten. fachleute und laien koennen auf geologischen wanderwegen _geowege_ erdwissenschaftliche entwicklungen vor ort erleben und begreifen. die plattform geowissenschaften der akademie der naturwissenschaften schweiz _scnat_ und «erlebnis geologie» haben die geologischen wanderwege in der schweiz zusammengestellt. | swisstopo | bundesamt fuer landestopografie swisstopo | bundesamt fuer landestopografie swisstopo, erlebnis geologie',
                'layer': 'ch.swisstopo.geologie-geowege',
                'lang': 'de',
                'topics': 'api,ech,geol,inspire,wms-bgdi',
                'staging': 'prod'
            }
        },
        {
            'id': 169,
            'weight': 16,
            'attrs': {
                'label': '<b>Amphibien Anhang 3</b>',
                'origin': 'layer',
                'title': 'amphibien anhang 3',
                'detail':
                    'bundesinventar der amphibienlaichgebiete von nationaler bedeutung - anhang 3 | in der schweiz leben heute 19 amphibienarten – fast alle befinden sich auf der roten liste der gefaehrdeten tierarten. die flaeche der feuchtgebiete als lebensraum der amphibien schrumpfte in den letzten 100 jahren auf weniger als einen zehntel zusammen. die noch erhaltenen lebensraeume sollten deshalb gesichert werden. als laichgewaesser bevorzugen die meisten arten stehende kleingewaesser wie tuempel und weiher. neben kleineren tuempeln bis zu grossen feuchtgebietskomplexen bilden kies- und lehmgruben einen wichtigen anteil _rund ein fuenftel der gesamtobjekte_ des inventars. im laufe der nutzung haben sie sich zu schuetzenswerten naturnahen standorten entwickelt.die ortsfesten objekte _am_l_ sind in zwei verschiedene bereiche eingeteilt: der bereich a ist dem naturschutz unterstellt. der bereich b umfasst den engeren bereich der landlebensraeume und die pufferzonen. es sind meist land- und forstwirtschaftlich genutzte flaechen. die wanderobjekte _am_g_ beinhalten genutzte gruben, innerhalb deren die dynamische voraussetzung fuer eine erhaltung der vorkommenden amphibienbestaende erhalten werden soll. als viertes bundesinventar gemaess art. 18a nhg setzte der bundesrat 2001 das bundesinventar der amphibienlaichgebiete mit 701 objekten in kraft, welches in den jahren 2003, 2007 und 2017 revidiert wurde. aktuell sind 929 objekte _835 ortsfeste und 94 wanderobjekte_ in kraft. weiter sind im anhang 3 30 objekte aufgefuehrt deren perimeter noch nicht definitiv bereinigt sind. deren schutz richtet sich bis zum entscheid ihrer aufnahme in anhang 1 oder 2 nach artikel 29 absatz 1 buchstabe a der natur- und heimatschutzverordnung _nhv_ und nach artikel 10 der amphibienlaichgebiete-verordnung _algv_. | bundesamt fuer umwelt bafu',
                'layer': 'ch.bafu.bundesinventare-amphibien_anhang4',
                'lang': 'de',
                'topics': 'api,bafu,ech',
                'staging': 'prod'
            }
        },
        {
            'id': 686,
            'weight': 12,
            'attrs': {
                'label': '<b>SP Militär</b>',
                'origin': 'layer',
                'title': 'sp militaer',
                'detail':
                    'sachplan militaer | der sachplan militaer _spm_ ist ein planungs- und koordinationsinstrument des bundes im sinne von art. 13 des raumplanungsgesetzes _rpg; sr 700_. er dient der raeumlichen sicherung und abstimmung der militaerischen infrastrukturen und taetigkeiten mit den zivilen raumanspruechen und legt – uebereinstimmend mit dem aktuellen stationierungskonzept – die ziele und vorgaben fuer die sachplanrelevanten militaerinfrastrukturen behoerdenverbindlich fest. dem sicherheitspolitischen und militaerischen wandel folgend sind die infrastrukturbeduerfnisse und raumansprueche der armee staendigen veraenderungen unterworfen. der spm wird dementsprechend regelmaessig ueberprueft und angepasst. der spm umfasst verschiedene objektkategorien: waffenplaetze, schiessplaetze, uebungsplaetze, militaerflugplaetze, armeelogistikstandorte, rekrutierungszentren, uebersetzstellen und besondere anlagen. kleinere oder dem anlageschutzgesetz _sr 510.518_ unterstellte militaerinfrastrukturen werden im spm nicht abgebildet. | waffenplaetze | swisstopo | bundesamt fuer landestopografie swisstopo | verteidigung, bevoelkerungsschutz und sport',
                'layer': 'ch.vbs.sachplan-infrastruktur-militaer_kraft',
                'lang': 'de',
                'topics': 'api,dev,ech,inspire,sachplan,wms-bgdi',
                'staging': 'prod'
            }
        },
        {
            'id': 948,
            'weight': 12,
            'attrs': {
                'label': '<b>Fische</b>',
                'origin': 'layer',
                'title': 'fische',
                'detail':
                    'beurteilung des biologischen gewaesserzustandes: fische | im rahmen der nationalen beobachtung oberflaechengewaesserqualitaet _nawa_ wird an rund 100 messstellen die gewaesserqualitaet durch bund und kantone gemeinsam erfasst. die bewertung des biologischen gewaesserzustandes aufgrund von fisch-untersuchungen erfolgt nach dem modul fische des modul-stufen-konzepts _www.modul-stufen-konzept.ch_. fische kommen in fast allen baechen und fluessen vor. durch ihre komplexen und ausgepraegten lebensraumansprueche sind sie gute indikatoren fuer den morphologischen und hydrologischen gewaesserzustand. die mobilitaet und das wanderverhalten vieler fischarten lassen auch rueckschluesse auf die durchgaengigkeit und vernetzung der gewaesser zu. | swisstopo | bundesamt fuer landestopografie swisstopo | bundesamt fuer umwelt bafu',
                'layer': 'ch.bafu.gewaesserschutz-biologischer_zustand_fische',
                'lang': 'de',
                'topics': 'api,bafu,ech,gewiss,inspire,schule,wms-bgdi',
                'staging': 'prod'
            }
        },
        {
            'id': 952,
            'weight': 12,
            'attrs': {
                'label': '<b>Kieselalgen (Diatomeen)</b>',
                'origin': 'layer',
                'title': 'kieselalgen _diatomeen_',
                'detail':
                    'beurteilung des biologischen gewaesserzustandes: kieselalgen _diatomeen_ | im rahmen der nationalen beobachtung oberflaechengewaesserqualitaet _nawa_ wird an rund 100 messstellen die gewaesserqualitaet durch bund und kantone gemeinsam erfasst. die bewertung des biologischen gewaesserzustandes aufgrund von fisch-untersuchungen erfolgt nach dem modul fische des modul-stufen-konzepts _www.modul-stufen-konzept.ch_. fische kommen in fast allen baechen und fluessen vor. durch ihre komplexen und ausgepraegten lebensraumansprueche sind sie gute indikatoren fuer den morphologischen und hydrologischen gewaesserzustand. die mobilitaet und das wanderverhalten vieler fischarten lassen auch rueckschluesse auf die durchgaengigkeit und vernetzung der gewaesser zu. | swisstopo | bundesamt fuer landestopografie swisstopo | bundesamt fuer umwelt bafu',
                'layer': 'ch.bafu.gewaesserschutz-biologischer_zustand_diatomeen',
                'lang': 'de',
                'topics': 'api,bafu,ech,gewiss,inspire,schule,wms-bgdi',
                'staging': 'prod'
            }
        },
        {
            'id': 992,
            'weight': 12,
            'attrs': {
                'label': '<b>Einteilung Landeskarte 50 Papier</b>',
                'origin': 'layer',
                'title': 'einteilung landeskarte 50 papier',
                'detail':
                    "papierkarte: landeskarte 1:50'000 | die genaue und informative topographische karte der schweiz fuer wanderer, alpinisten, velofahrer, planer, reisende und entdecker. ausgewaehlte gebiete auf zusammensetzungen. die zusammensetzungen praesentieren auf einem blatt attraktive gebiete, welche sonst nur getrennt auf mehreren einzelblaettern erhaeltlich waeren. | swisstopo | bundesamt fuer landestopografie swisstopo | bundesamt fuer landestopografie swisstopo",
                'layer': 'ch.swisstopo.landeskarte50_papier.metadata',
                'lang': 'de',
                'topics': 'ech,inspire,swisstopo,wms-bgdi',
                'staging': 'prod'
            }
        },
        {
            'id': 993,
            'weight': 12,
            'attrs': {
                'label': '<b>Einteilung Landeskarte 25 Papier</b>',
                'origin': 'layer',
                'title': 'einteilung landeskarte 25 papier',
                'detail':
                    "papierkarte: landeskarte 1:25'000 | die genauste und informativste topographische karte der schweiz fuer wanderer, alpinisten, planer, individualisten und entdecker. ausgewaehlte gebiete auf zusammensetzungen. die zusammensetzungen praesentieren auf einem blatt attraktive gebiete, welche sonst nur getrennt auf mehreren einzelblaettern erhaeltlich waeren. die kartenblaetter der gedruckten papierausgabe sind gefalzt und ungefalzt erhaeltlich. | swisstopo | bundesamt fuer landestopografie swisstopo | bundesamt fuer landestopografie swisstopo",
                'layer': 'ch.swisstopo.landeskarte25_papier.metadata',
                'lang': 'de',
                'topics': 'ech,inspire,swisstopo,wms-bgdi',
                'staging': 'prod'
            }
        },
        {
            'id': 33,
            'weight': 10,
            'attrs': {
                'label': '<b>Wildruhezonen</b>',
                'origin': 'layer',
                'title': 'wildruhezonen',
                'detail':
                    'wildruhezonen | wildtiere brauchen rueckzugsgebiete in welchen sie nicht gestoert werden. die ausscheidung von wildruhezonen dient der vermeidung uebermaessiger stoerung gemaess art. 7 abs 4 des jsg als antwort auf die zunehmende freizeitnutzung. es gibt heute rechtsverbindliche wildruhezonen und schutzgebiete, die ueber den rechtssetzungsprozess ausgeschieden sind _kantonales jagdrecht, kommunale zonenplanung, etc._, wie auch empfohlene gebiete. innerhalb von rechtsverbindlichen wildruhezonen und wildtierschutzgebieten duerfen nur die in der karte eingezeichneten erlaubten routen und wege begangen werden. nicht eingezeichnet sind praeparierte _langlauf-_loipen, winterwanderwege und im winter geraeumte oder befahrbare strassen. diese duerfen von schneesportlern selbstverstaendlich begangen werden. in empfohlenen wildruhezonen sind die erlaubten routen und wege als empfehlungen zu verstehen. der stand der arbeiten in den kantonen ist zur zeit sehr unterschiedlich, weshalb der datensatz luecken aufweist. die karte wird mindestens jaehrlich _zu winterbeginn_ aktualisiert. bitte beachten sie die allgemeinen hinweise und aenderungen _z.b. perimeteranpassungen_ unten, welche in der karte noch nicht beruecksichtigt werden konnten. die kampagne "respektiere deine grenzen" setzt sich fuer den schutz der wildtiere und die bekanntmachung der wildruhezonen in der bevoelkerung ein. | swisstopo | bundesamt fuer landestopografie swisstopo | kantone [bundesamt fuer umwelt bafu]',
                'layer': 'ch.bafu.wrz-wildruhezonen_portal',
                'lang': 'de',
                'topics': 'api,ech,inspire,schneesport,schule,wildruhezonen,wms-bgdi',
                'staging': 'prod'
            }
        },
        {
            'id': 97,
            'weight': 10,
            'attrs': {
                'label': '<b>Siegfriedkarte Erstausgabe</b>',
                'origin': 'layer',
                'title': 'siegfriedkarte erstausgabe',
                'detail':
                    "topographischer atlas der schweiz _siegfriedkarte_ | in den jahren 1870 bis 1926 wurde - anfaenglich unter der leitung von oberst hermann siegfried - der topographische atlas der schweiz veroeffentlicht. es handelt sich um das erste detaillierte gesamtwerk fuer die schweiz in den massstaeben 1:25'000 fuer das mittelland, den jura und das suedtessin sowie 1:50'000 fuer die alpen. mit der periodischen fortfuehrung bis 1949 wurden insgesamt ueber 4'000 nachgefuehrte blaetter publiziert. fuer die ersterstellung wurden zwei verschiedene techniken angewandt: kupferstich fuer die 462 kartenblaetter im massstab 1:25'000 und steingravur fuer die 142 blaetter 1:50'000. saemtliche ausgaben sind eingescannt worden und stehen nun digital fuer untersuchungen zur landschaftsentwicklung und weitere anwendungen verfuegung. | topographischer atlas der schweiz _siegfriedkarte_ | swisstopo | bundesamt fuer landestopografie swisstopo | bundesamt fuer landestopografie swisstopo",
                'layer': 'ch.swisstopo.hiks-siegfried',
                'lang': 'de',
                'topics':
                    'api,ech,inspire,ivs,kgs,schule,swissmaponline,swisstopo,wms-bgdi,wms-swisstopowms',
                'staging': 'prod'
            }
        },
        {
            'id': 170,
            'weight': 10,
            'attrs': {
                'label': '<b>Zeitreise - Kartenwerke</b>',
                'origin': 'layer',
                'title': 'zeitreise - kartenwerke',
                'detail':
                    'zeitreise - topografische kartenwerke | das bundesamt fuer landestopografie swisstopo hat seit seiner gruendung durch guillaume-henri dufour im jahre 1838 drei amtliche landeskartenwerke produziert: die topographische karte der schweiz 1:100’000 _dufourkarte_, den topographischen atlas der schweiz 1:25’000 / 1:50’000 _siegfriedkarte_ und die landeskarte der schweiz in verschiedenen massstaeben. die gesamtheit dieser bestaende bildet ein kulturgut von nationaler bedeutung, das als «topographisches landschaftsgedaechtnis der schweiz» bezeichnet werden kann. mit der «zeitreise» laesst sich der landschaftswandel anhand dieser kartenwerke auf interaktive weise erfahren. | bundesamt fuer landestopografie swisstopo',
                'layer': 'ch.swisstopo.zeitreihen',
                'lang': 'de',
                'topics': 'api,dev,ech,energie,geol,inspire,isos,kgs,schule,swisstopo',
                'staging': 'prod'
            }
        },
        {
            'id': 199,
            'weight': 10,
            'attrs': {
                'label': '<b>Wildtierschutzgebiete</b>',
                'origin': 'layer',
                'title': 'wildtierschutzgebiete',
                'detail':
                    'wildtierschutzgebiete | wildtierschutzgebiete haben den schutz ausgewaehlter saeugetiere und voegel sowie ihrer lebensraeume zum ziel. die hier beruecksichtigten 42 eidgenoessischen jagdbanngebiete stuetzen sich auf art. 11 des jagdgesetzes. schneesportarten duerfen nur auf markierten routen ausgeuebt werden. damit gelten fuer schneesportler die gleichen zutrittsbeschraenkungen wie fuer rechtsverbindliche wildruhezonen mit routengebot. innerhalb von rechtsverbindlichen wildruhezonen und wildtierschutzgebieten duerfen nur die in der karte eingezeichneten erlaubten routen und wege begangen werden. nicht eingezeichnet sind praeparierte _langlauf-_loipen, winterwanderwege und im winter geraeumte oder befahrbare strassen. diese duerfen von schneesportlern selbstverstaendlich begangen werden. skilifte oder luftseilbahnen sind in wildtierschutzgebieten _eidg. jagdbanngebieten_ eingetragen. sie geben an, wo sich infrastrukturen befinden, die von schneesportlern zusammen mit den dazugehoerigen skipisten benutzt werden duerfen. skipisten sind nicht eingezeichnet. die kampagne "respektiere deine grenzen" setzt sich fuer den schutz der wildtiere und die bekanntmachung der wildtierschutzgebiete in der bevoelkerung ein. | swisstopo | bundesamt fuer landestopografie swisstopo | bundesamt fuer umwelt bafu',
                'layer': 'ch.bafu.wrz-jagdbanngebiete_select',
                'lang': 'de',
                'topics': 'api,ech,inspire,schneesport,schule,swissmaponline,wildruhezonen,wms-bgdi',
                'staging': 'prod'
            }
        },
        {
            'id': 294,
            'weight': 10,
            'attrs': {
                'label': '<b>Entstehung der Gesteine 500</b>',
                'origin': 'layer',
                'title': 'entstehung der gesteine 500',
                'detail':
                    "lithologisch-petrografische karte der schweiz – genese 1:500000 | die geotechnische karte 1:500'000 _gk500_ der fachgruppe georessourcen schweiz zeigt den untergrund nach lithologisch-petrografischen kriterien. die legende ist im hinblick auf die technische nutzung des untergrundes konzipiert _gewinnung von mineralischen rohstoffen, bauvorhaben_. in dieser darstellung sind die gesteine nach ihrer entstehung _genese_ unterteilt, z.b. ablagerungen von fluessen und gletschern, erstarrung von magmen oder umwandlung kristalliner gesteine durch druck- und temperatureinwirkung. | lithologisch-petrografische karte der schweiz 1:500000 | swisstopo | bundesamt fuer landestopografie swisstopo | bundesamt fuer landestopografie swisstopo, fachgruppe georessourcen schweiz",
                'layer': 'ch.swisstopo.geologie-geotechnik-gk500-genese',
                'lang': 'de',
                'topics': 'api,ech,geol,inspire,schule,swissmaponline,wms-bgdi',
                'staging': 'prod'
            }
        },
        {
            'id': 703,
            'weight': 10,
            'attrs': {
                'label': '<b>Windenergieanlagen</b>',
                'origin': 'layer',
                'title': 'windenergieanlagen',
                'detail':
                    'windenergieanlagen | windenergieanlagen nutzen die kinetische energie der anstroemenden luft zur rotation der fluegel. die auf diese weise erzeugte mechanische energie wird von einem generator in elektrische energie umgewandelt.die erste windenergieanlage der schweiz wurde 1986 beim soolhof _langenbruck, bl_ mit einer leistung von 28 kw in betrieb genommen. 2013 gibt es insgesamt 34 windenergieanlagen, die rund 85 gigawattstunden _gwh_ windstrom produzieren. der groesste windpark befindet sich auf dem mont crosin im berner jura bei st. imier: hier stehen 16 windturbinen mit einer gesamtleistung von 23,6 mw. weitere grossanlagen stehen u.a. im rhonetal _vs_, bei entlebuch _lu_ und auf dem guetsch ob andermatt _ur_. in der schweiz kann sich die windenergie noch stark entwickeln. so sollen windenergieanlagen bis zum jahr 2020 rund 600 gwh und bis 2050 etwa 4‘000 gwh strom pro jahr produzieren. geeignete standorte befinden sich auf den jurahoehen, aber auch in den alpen und voralpen und im westlichen mittelland. die geofachdaten «windenergieanlagen» dokumentieren den aktuellen bestand der windenergieanlagen der schweiz. saemtliche informationen basieren auf den auskuenften der anlagenbetreibenden. die angaben dienen als informationsmaterial fuer die oeffentlichkeit und stellen keine amtliche auskunft oder rechtsverbindliche aussage dar. | swisstopo | bundesamt fuer landestopografie swisstopo | bundesamt fuer energie',
                'layer': 'ch.bfe.windenergieanlagen',
                'lang': 'de',
                'topics': 'api,dev,ech,energie,inspire,kgs,schule,wms-bgdi',
                'staging': 'prod'
            }
        },
        {
            'id': 825,
            'weight': 10,
            'attrs': {
                'label': '<b>SWISSIMAGE Zeitreise</b>',
                'origin': 'layer',
                'title': 'swissimage zeitreise',
                'detail':
                    'swissimage: das digitale orthophotomosaik der schweiz | das orthophotomosaik swissimage ist eine zusammensetzung von gescannten analogen und digitalen, schwarz-weiss und farbigen luftbildern. ein orthofoto ist ein luftbild bei dem neigungseinfluesse der kamera und des gelaendes korrigiert wurden. standardmaessig wird der aktuelle stand vom produkt swissimage angezeigt. mit der anzeige von daten-zeitstaende – genannt «zeitreise» - laesst sich der landschaftswandel von 1970 bis heute anhand dieser bilder auf interaktive weise erfahren. | swissimage | bundesamt fuer landestopografie swisstopo',
                'layer': 'ch.swisstopo.swissimage-product',
                'lang': 'de',
                'topics': 'api,ech,inspire,luftbilder,schule,swisstopo',
                'staging': 'prod'
            }
        },
        {
            'id': 912,
            'weight': 10,
            'attrs': {
                'label': '<b>Diffuse Phosphoreinträge</b>',
                'origin': 'layer',
                'title': 'diffuse phosphoreintraege',
                'detail':
                    'diffuse phosphoreintraege in die gewaesser, modellierte werte | phosphoreintraege in gewaesser stellen eine unerwuenschte belastung dar. hohe eintraege an geloestem phosphor haben in den vergangenen jahrzehnten zu einer ueberduengung der mittellandseen gefuehrt. insgesamt gelangen pro jahr rund 900 t geloester phosphor aus diffusen quellen in die gewaesser der schweiz. hohe eintraege erfolgen vor allem von intensiv genutzten graslandflaechen in hanglagen.die geloesten phosphoreintraege in die gewaesser wurden mit dem stoffflussmodell modiffus ueber alle diffusen eintragsquellen _ackerland, dauergruenland, wald, gletscher, siedlungsgruenflaechen etc._ und eintragspfade _bodenerosion, auswaschung, abschwemmung, drainage, atmosphaerische deposition etc._ berechnet. die karte zeigt die aufsummierten verluste pro landnutzungskategorie im hektarraster, basierend auf der arealstatistik 2004/09. es wurden mittlere klimatische bedingungen zugrunde gelegt, das bezugsjahr ist 2010. diese modellierten werte sind nicht gleichzusetzen mit gemessenen werten in gewaessern, da sie die umwandlungs- und ablagerungsprozesse sowohl in der landschaft als auch im gewaesser selbst nicht beruecksichtigen. die resultate sind fuer hydrologische oder administrative einheiten ab 50 km2 groesse interpretierbar, nicht aber fuer einzelne pixel. | swisstopo | bundesamt fuer landestopografie swisstopo | bundesamt fuer umwelt bafu',
                'layer': 'ch.bafu.gewaesserschutz-diffuse_eintraege_phosphor',
                'lang': 'de',
                'topics': 'api,bafu,ech,gewiss,inspire,schule,wms-bgdi',
                'staging': 'prod'
            }
        },
        {
            'id': 913,
            'weight': 10,
            'attrs': {
                'label': '<b>Diffuse Stickstoffeinträge</b>',
                'origin': 'layer',
                'title': 'diffuse stickstoffeintraege',
                'detail':
                    'diffuse stickstoffeintraege in die gewaesser, modellierte werte | stickstoffeintraege in gewaesser stellen eine unerwuenschte belastung dar. im rahmen des uebereinkommens ueber den schutz der meeresumwelt des nordostatlantiks _ospar_ hat sich die schweiz verpflichtet, die ueber den rhein aus der schweiz gelangende stickstofffracht gegenueber 1985 um 50% zu reduzieren. dieses ziel ist noch nicht erreicht. insgesamt gelangen pro jahr rund 51‘000 t stickstoff aus diffusen quellen in die gewaesser der schweiz. hohe eintraege erfolgen von intensiv genutzten ackerflaechen, insbesondere von drainierten flaechen.die stickstoffeintraege in die gewaesser wurden mit dem stoffflussmodell modiffus ueber alle diffusen eintragsquellen _ackerland, dauergruenland, wald, gletscher, siedlungsgruenflaechen etc._ und eintragspfade _bodenerosion, auswaschung, abschwemmung, drainage, atmosphaerische deposition etc._ berechnet. die karte zeigt die aufsummierten verluste pro landnutzungskategorie im hektarraster, basierend auf der arealstatistik 2004/09. es wurden mittlere klimatische bedingungen zugrunde gelegt, das bezugsjahr ist 2010. diese modellierten werte sind nicht gleichzusetzen mit gemessenen werten in gewaessern, da sie die umwandlungs- und ablagerungsprozesse sowohl in der landschaft als auch im gewaesser selbst nicht beruecksichtigen. die resultate sind fuer hydrologische oder administrative einheiten ab 50 km2 groesse interpretierbar, nicht aber fuer einzelne pixel. | swisstopo | bundesamt fuer landestopografie swisstopo | bundesamt fuer umwelt bafu',
                'layer': 'ch.bafu.gewaesserschutz-diffuse_eintraege_stickstoff',
                'lang': 'de',
                'topics': 'api,bafu,ech,gewiss,inspire,schule,wms-bgdi',
                'staging': 'prod'
            }
        },
        {
            'id': 962,
            'weight': 10,
            'attrs': {
                'label': '<b>Markierversuche</b>',
                'origin': 'layer',
                'title': 'markierversuche',
                'detail':
                    'markierversuche im grundwasser | markierversuche sind ein gaengiges mittel der angewandten hydrogeologie zur verfolgung des wasserflusses im untergrund. der layer zeigt die eingabestellen aller seit 1984 bei infotracer gemeldeten und archivierten markierversuche. infotracer ist das instrument des bafu zur koordination zwischen denjenigen stellen, die markierversuche durchfuehren _in der regel geologie- und ingenieurbueros sowie forschungsinstitute_ und den kantonalen fachstellen. die im layer dargestellten informationen liefern einerseits einen generellen ueberblick der bisher durchgefuehrten markierversuche und ermoeglichen andererseits die ueberpruefung des bereichs geplanter versuche. markierstoffe werden direkt ins grundwasser, in die ungesaettigte zone oder ein oberflaechengewaesser, welche mit dem grundwasser in verbindung stehen kann, eingegeben. insbesondere um unnoetige eingaben von markierstoffen sowie ueberschneidungen unterschiedlicher eingaben zu vermeiden, erfasst infotracer auch die metadaten der markierversuche _datum, eingabemilieu, verwendeter markierstoff, verantwortliche stelle_, verfuegt jedoch ueber keine angaben zu deren ergebnissen. | bundesamt fuer umwelt bafu',
                'layer': 'ch.bafu.hydrogeologie-markierversuche',
                'lang': 'de',
                'topics': 'api,bafu,ech,geol,gewiss,inspire',
                'staging': 'prod'
            }
        }
    ],
    'total': 32,
    'total_found': 32,
    'time': '0.000',
    'words': [{
        'word': '*wand*', 'docs': 33, 'hits': 105
    }, {
        'word': 'wand', 'docs': 0, 'hits': 0
    }, {
        'word': 'wand*', 'docs': 17, 'hits': 68
    }, {
        'word': '*inspire*', 'docs': 766, 'hits': 766
    }, {
        'word': 'inspire', 'docs': 766, 'hits': 766
    }, {
        'word': '*ech*', 'docs': 825, 'hits': 1787
    }, {
        'word': 'ech', 'docs': 814, 'hits': 814
    }, {
        'word': '*prod*', 'docs': 830, 'hits': 941
    }, {
        'word': 'prod', 'docs': 823, 'hits': 823
    }]
}]
