'''
Media outlet bias scores provided by
    Richard Fletcher, Alessio Cornia, and Rasmus Kleis Nielsen. 2020. 
    How Polarized Are Online and Offline News Audiences? A Comparative Analysis of Twelve Countries. 
    The International Journal of Press/Politics (2020)
Manually extracted from the paper.
'''


outlet_all = [
    '''Channel 7/Yahoo! News : 7news.com.au
Channel 9/MSN News : 9news.com.au
ABC News : abc.net.au
Channel TEN News : 10daily.com.au
News.com.au: news.com.au 
Sydney Morning Herald : smh.com.au
Herald Sun : heraldsun.com.au
Daily Telegraph: dailytelegraph.com.au
The Age: theage.com.au
The Australian: theaustralian.com.au
Sky News: skynews.com.au
Courier Mail : couriermail.com.au
HuffPost : huffpost
Australian Financial Review : afr
Guardian Australia : theguardian
BuzzFeed News : buzzfeednews
The Advertiser : adelaidenow.com.au
The Conversation : theconversation
Vice News : vice
Crikey : crikey.com.au
Junkee : junkee
''',
    '''ARD Tagesschau : tagesschau.de
ZDF Heute : zdf.de
RTL Aktuell : rtl.de
N24 : welt.de
n-tv : n-tv.de
Der Spiegel : spiegel.de
Bild : bild.de
Sat.1 Nachrichten : sat1.de
Focus : focus.de
t-online : t-online.de
Web.de : web.de
Stern : stern.de
Gmx.de : gmx.net
Die Welt : welt.de
Süddeutsche Zeitung : sueddeutsche.de
Die ZEIT : zeit.de
FAZ : faz.net
Huffington Post : huffpost
Yahoo! News : news.yahoo
Handelsblatt : handelsblatt
MSN News : msn
''',
    '''Antena 3 News : antena3
RTVE News : rtve.es
LaSexta News : lasexta
El Pais : elpais
Telecinco News : telecinco.es
Cuatro News : cuatro
El Mundo : elmundo.es
20 Minutos : 20minutos.es
Marca : marca
Cadena SER News : cadenaser
ABC : abc.es
El Periódico : elperiodico
ElConfidencial.com : elconfidencial
Eldiario.es : eldiario.es
La Vanguardia : lavanguardia
COPE News : cope.es
Yahoo! News : news.yahoo
Onda Cero News : ondacero.es
La Razon : larazon.es
El HuffPost : huffingtonpost.es
Público.es : publico.es
As : eldiario.es
MSN News : msn
OKDiario.com : okdiario
Europa Press : europapress.es
Expansión : expansion
Euronews : es.euronews
ElEspañol.com : elespanol
Cinco Dias : cincodias.elpais
''',
    '''BFMTV News : bfmtv
TF1 News : tf1.fr
France Télévisions News : france.tv
20 Minutes : 20minutes.fr
Le Monde : lemonde.fr
Le Figaro : lefigaro.fr
Itélé News : cnews.fr
LCI News : lci.fr
Le Point  : lepoint.fr
L’Express : lexpress.fr
Le HuffPost  : huffpost
L’Obs  : nouvelobs
Libération : liberation.fr
France 24 News  : france24
Yahoo! News : fr.news.yahoo
L’internaute.com : linternaute
Les Echos : lesechos.fr
Direct Matin : cnews.fr
Médiapart : mediapart.fr
MSN News : msn
Courrier International  : courrierinternational
Aufeminin.com : aufeminin
Marianne : marianne.net
Rue89 : nouvelobs
BuzzFeed News : buzzfeednews
L’Opinion : lopinion.fr
La Croix : la-croix
Atlantico : atlantico.fr
''',
    '''RTÉ News : rte.ie
Irish Independent : independent.ie
Sky News : sky.news
BBC News : bbc
Irish Times : irishtimes
Journal.ie : thejournal
Newstalk : newstalk
BreakingNews.ie : breakingnews.ie
Irish Examiner : irishexaminer
Irish Daily Mail : dailymail.co.uk
Yahoo! News : news.yahoo
The Sunday Times : thetimes.co.uk
Irish Mirror : mirror.co.uk
Her.ie/joe.ie : joe.ie
HuffPost : huffpost
Irish Daily Sun : thesun.ie
UTV Ireland News : itv
MSN News : msn
Evening Herald : independent.ie
Sunday World : sundayworld
BuzzFeed News : buzzfeednews
Irish Daily Star : dailystar.co.uk
dailyedge.ie/The42/Fora.ie : the42.ie
Vice News : vice''',
    '''Rai News : rainews.it
Mediaset (inc. TgCom24) : mediaset.www.tgcom24.it
SkyTg24 : sky.tg24.it
Tg La7 News : la7.it
La Repubblica : repubblica.it
Il Corriere della Sera : corriere.it
ANSA: ansa.it
Il Fatto Quotidiano: ilfattoquotidiano.it
Il Sole 24 Ore : ilsole24ore
La Stampa : lastampa.it
Yahoo! News : yahoo.it.notizie
Notizie.Libero.it : liberoquotidiano.it
L’HuffPost : huffpost
Il Giornale : ilgiornale.it
MSN News : msn
Il Messangero : ilmessaggero.it
L'Espresso : repubblica.espresso.it
Quotidiano.net : ilfattoquotidiano.it
Fanpage : fanpage.it
Tiscali.it News : tiscali.notizie.it
Il Post.it : ilpost.it
Dagospia.com : dagospia
Linkiesta.it : linkiesta.it
Lettera43.it : lettera43.it
Blogo.it : blogo.it''',
    '''NOS : nos.nl
RTL : rtlnieuws.nl
Nu : nu.nl
De Telegraaf : telegraaf.nl
Algemeen Dagblad : ad.nl
SBS : sbs.com.au
Metro : metro.co.uk
de Volkskrant : volkskrant.nl
NRC Handelsblad (inc. Next) : nrc.nl
MSN News : msn
Geen Stijl : geenstijl.nl
Trouw : trouw.nl
Netherlands Dagblad : nd.nl
Het Financieele Dagblad : fd.nl
Yahoo! News : news.yahoo
De Correspondent : decorrespondent.nl''',
    '''TVN News : tvn24.pl
Onet.pl News : onet.wiadomosci.pl
WP.pl News : wp.wiadomosci.pl
RMF FM : rmf24.pl
Polsat News : polsatnews.pl
TVP News : tvp.info
Radio Zet : radiozet.wiadomosci.pl
Gazeta Wyborcza : wyborcza.pl
Interia.pl News : interia.fakty.pl
Fakt : interia.fakty.pl
Gazeta.pl : gazeta.next.pl
Newsweek Polska : newsweek
Dziennik Gazeta Prawna : dziennik.wiadomosci.pl
Nasze Miasto : naszemiasto.nowytomysl.pl
Super Express : se.pl
Polskie Radio : polskieradio24.pl
Polityka : polityka.pl
Wprost : wprost.pl
Rzeczpospolita : rp.pl
Money.pl : money.pl
Przeglad Sportowy : przegladsportowy.pl
Sport.pl : dziennik.sport.pl
Bankier.pl : bankier.pl
Nasz Dziennik : dziennik.wiadomosci.pl
Niezalenza.pl : niezalezna.pl
Dziennik.pl : dziennik.wiadomosci.pl
Natemat.pl : natemat.pl
MSN News : msn
Gosc Niedzielny : gosc.pl
Wpolityce.pl : wpolityce.pl
Yahoo! News : news.yahoo''',
    '''BBC News : bbc
ITV News : itv
Sky News : news.sky
Daily Mail/MailOnline : dailymail.co.uk
The Guardian : theguardian
Huffington Post : huffingtonpost.co.uk
Metro : metro.co.uk
The Mirror : mirror.co.uk
The Sun : thesun.co.uk
The Telegraph : telegraph.co.uk
BuzzFeed News : buzzfeednews
The Times : thetimes.co.uk
Independent/i100 : independent.co.uk
MSN News : msn
Yahoo! News : uk.news.yahoo
The Lad Bible : ladbible
The Express : express.co.uk
The Canary Financial Time : thecanary.co''',
    '''Fox News : foxnews
CNN : cnn
NBC News : nbcnews
ABC News : abcnews.go
CBS News : cbsnews
Huffington Post : huffpost
Yahoo! News : news.yahoo
New York Times : nytimes
Washington Post : washingtonpost
NPR : npr.org
USA TODAY : usatoday
BuzzFeed News : buzzfeednews
MSN News : msn
Wall Street Journal : wsj
LA Times : latimes
Breitbart News : breitbart
Occupy Democrats : occupydemocrats
Vox : vox
AOL News : aol
Al Jazeera : aljazeera
Vice News : vice
Infowars : infowars
Upworthy : upworthy
Mashable : mashable
'''

]


scores_all = [
  '''.01
.04
-.08
-.03
-.01
-.10
.05
.01
-.08
-.01
.03
-.05
-.17
-.02
-.17
-.20
-.10
-.22
-.24
-.21
-.17''',
    '''-.07
-.01
.02
.13
.02
-.05
.05
-.01
.08
.02
.01
-.05
-.03
.04
-.11
-.09
.00
.03
.03
.07
.02''',
    '''.05
.09
-.16
-.08
-.01
-.05
.11
-.04
.03
-.09
.19
-.14
.01
-.12
-.05
.25
.03
.11
.18
-.12
-.20
.03
.06
.09
.01
.16
-.02
.10
.11''',
    '''.03
.04
-.15
-.01
-.16
.13
-.06
-.01
.08
.01
-.18
-.18
-.21
-.02
.03
-.03
.01
-.01
-.30
-.01
-.20
-.02
-.25
-.22
-.16
.01
.03
.12''',
    '''.02
.03
.02
.01
-.02
-.02
-.02
-.03
.00
.05
.00
-.03
-.03
-.09
-.09
-.07
-.07
-.03
.00
-.08
-.12
.03
-.09
-.13''',
    '''-.07
.13
.00
-.04
-.17
-.03
-.04
-.14
-.04
-.09
.04
.08
-.17
.22
.02
-.01
-.12
-.01
.00
.05
-.10
-.07
-.08
-.12
-.13''',
    '''-.03
.05
.02
.10
.00
.07
.00
-.17
-.08
-.03
.19
-.11
-.05
.19
.04
-.09''',
    '''-.08
.00
.02
.02
-.05
.20
-.05
-.10
.00
-.06
-.05
-.10
-.02
.03
-.04
.13
-.06
.07
.04
.02
.08
.06
.00
.29
.27
.14
-.01
.02
.23
.22
.04''',
    '''-.03
.09
.09
.15
-.17
-.13
-.04
-.12
.07
.13
-.09
.21
-.19
.10
-.02
-.06
.30
-.35''',
    '''.28
-.17
-.22
-.16
-.11
-.22
.00
-.27
-.23
-.32
-.13
-.19
-.12
-.09
-.25
.34
-.38
-.35
.05
-.30
-.28
.19
-.29
-.18
'''
]


