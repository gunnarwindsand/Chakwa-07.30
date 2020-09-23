"""

Dataforberedelse - hendelseslogger

Prosessutvinning er basert på hendelseslogger. 

Vi kan beskrive hendelseslogger som en sekvens av sekvenser av hendelser. 
I de fleste tilfeller, når prosessen støttes av et IT-system, produserer den en slags logg over handlinger fullført av brukerne. 
For eksempel kan loggen inneholde alle handlingene en bruker utførte i appen.

For å kunne utføre prosessoppdaging må datasettet inneholde følgende tre typer informasjon:
* Saks-ID - en unik identifikator for en enhet som går gjennom prosessen. Et vanlig eksempel kan være brukerens unike ID, selv om mange muligheter er gyldige (det avhenger av brukssaken).
* Hendelse - et trinn i prosessen, enhver aktivitet som er en del av prosessen vi analyserer.
* Tidsstempel - brukes til evaluering av ytelse og bestemmelse av rekkefølgen på hendelser, kan være tidspunktet da brukeren skrev inn / ut av den gitte hendelsen (eller begge faktisk).

I tillegg kan vi inkludere mer detaljert informasjon som ressurser, land, brukersegment, etc. Ved å utnytte tilleggsinformasjon er vi i stand til å utføre en mye mer detaljert analyse.
"""


import pandas as pd
from pm4py.objects.conversion.log import converter as log_converter
from pm4py.objects.log.importer.xes import importer as xes_importer

# process mining 
from pm4py.algo.discovery.alpha import algorithm as alpha_miner
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.algo.discovery.heuristics import algorithm as heuristics_miner
from pm4py.algo.discovery.dfg import algorithm as dfg_discovery

# viz
from pm4py.visualization.petrinet import visualizer as pn_visualizer
from pm4py.visualization.process_tree import visualizer as pt_visualizer
from pm4py.visualization.heuristics_net import visualizer as hn_visualizer
from pm4py.visualization.dfg import visualizer as dfg_visualization

# misc 
from pm4py.objects.conversion.process_tree import converter as pt_converter


"""
Vær ekstra oppmerksom på navnekonvensjonen som er presentert i tabellen. Det er noe repetisjon i kolonnene,
slik at du tydelig kan se hvordan de ble omdøpt til å fungere godt med algoritmene i pm4py.
Standardnavnet som indikerer saks-ID er  case:concept:name, concept:name er eventen, og til slutt time:timestamp er tilhørende timestamp. 
I tilfelle kolonnene ikke er navngitt på denne måten, kan vi alltid gi dem nytt navn ved hjelp av omdøpningsmetoden til en pd.DataFrame.
"""

df = pd.read_csv("running-example.csv")
df["time:timestamp"]= pd.to_datetime(df["time:timestamp"])
log = log_converter.apply(df)


########## Alpha miner 
"""
Alpha Miner er en av de mest kjente algoritmer for prosessoppdagelse.
Kort sagt, algoritmen skanner sporene (sekvenser i hendelsesloggen) for å bestille relasjoner og bygger fotavtrykkmatrisen.
Deretter konverterer den matrisen til et ** Petri-nett (en type graf) **. 


Å kjøre Alpha Miner resulterer i følgende:
* en Petri-nettmodell der alle overgangene er synlige, unike og tilsvarer de klassifiserte hendelsene.
* den første merkingen - den beskriver statusen til Petri net-modellen når kjøringen starter. 
* den endelige merkingen - den beskriver statusen til Petri-nettmodellen når utførelsen avsluttes.

Prosessmodeller uttrykt ved bruk av Petri-nett deler en veldefinert semantikk: utførelsen av prosessen starter fra hendelsene som inngår i den første merkingen og avsluttes ved hendelsene som inngår i den endelige merkingen.


Noen av egenskapene til algoritmen:

* den kan ikke håndtere loops med lengde en eller to,
* usynlige og dupliserte oppgaver kan ikke oppdages,
* den oppdagede modellen er kanskje ikke en god fit,
* den takler ikke støy bra.

"""

#Initaite alpha miner

net, initial_marking, final_marking = alpha_miner.apply(log)

# viz
gviz = pn_visualizer.apply(net, initial_marking, final_marking)
pn_visualizer.view(gviz)


""" 

Den grønne sirkelen representerer den første merkingen i data, mens den oransje den siste merkingen. 
Ved å bruke det første tilfellet av datasettet kan vi følge sporet: registrer forespørsel -> undersøker grundig -> sjekk "ticket" -> avgjør -> avvis forespørsel.

For å gi litt mer informasjon på proseskartet, kan vi legge til informasjon om hyppigheten av hendelsene. 

Man trenger ikke kjøre algoritmen på nytt, vi legger bare til en parameter i visualisereren.

"""


# add information about frequency to the illustrasjon  
parameters = {pn_visualizer.Variants.FREQUENCY.value.Parameters.FORMAT: "png"}
gviz = pn_visualizer.apply(net, initial_marking, final_marking, 
                           parameters=parameters, 
                           variant=pn_visualizer.Variants.FREQUENCY, 
                           log=log)

# save the Petri net
pn_visualizer.save(gviz, "alpha_miner_petri_net.png")

pn_visualizer.view(gviz)



""" 
Her observer vi de hyppigste stegene som er tatt i de ulike sekvensene i event-loggen
Det er en forbedret versjon av Alpha Miner kalt Alpha + Miner, som i tillegg kan håndtere loops med henholdvis lengde en og to.
"""

################ Directly-Follows Graph

"""
Den andre typen av prosessmodeller er Directly-Follows Graph. 

I denne type modeller representerer nodene hendelsene fra loggen, mens målrettede kanter forbinder nodene 
hvis det er minst ett spor i loggen der kildehendelsen følges av målhendelsen.

Disse målrettede kantene fungerer fint sammen med noen ekstra metrics, for eksempel:
* frekvens - antall ganger kildehendelsen etterfølges av målhendelsen.
* ytelse - en slags aggregering, for eksempel den gjennomsnittlige tiden som har gått mellom de to hendelsene.

I den mest grunnleggende varianten kan vi opprette en Directly-Follows Graph fra hendelsesloggen ved å kjøre følgende kodelinjer:
"""

dfg = dfg_discovery.apply(log)

gviz = dfg_visualization.apply(dfg, log=log, variant=dfg_visualization.Variants.FREQUENCY)
dfg_visualization.view(gviz)

"""
I denne grafen la vi til frekvensen på toppen av de målrettede kantene. 
Vi kan se at denne grafen er vesentlig forskjellig fra Petri-nettet hentet fra Alpha Miner. 
Det er fordi denne typen graf viser alle sammenhengene og ikke prøver å finne noen regler som hendelsene følger.


Alternativt kan vi dekorere kantene ved å bruke ytelsesberegningen i stedet. 
Ved å bruke PERFORMANCE-varianten viser vi gjennomsnittlig tid som har gått mellom de to nodene.
"""


dfg = dfg_discovery.apply(log, variant=dfg_discovery.Variants.PERFORMANCE)

gviz = dfg_visualization.apply(dfg, log=log, variant=dfg_visualization.Variants.PERFORMANCE)
dfg_visualization.view(gviz)


######### Heurstic miner

"""
Heuristics Miner er en forbedring av Alpha Miner-algoritmen og fungerer på en Directly-Follows Graph. 

Fordelen ved bruk av denne algoritmen er at den gir en måte å håndtere støy på, samt at det å finne vanlige konstruksjoner. 
Utgangen av algoritmen er et Heuristics Net - et objekt som inneholder både aktivitetene og forholdet mellom dem. 
--> https://www.futurelearn.com/courses/process-mining/0/steps/15639

Merk: Heuristics Net kan konverteres til et Petri-nett.


Noen av egenskapene til algoritmen:
* tar frekvens i betraktning,
* oppdager korte løkker og hopper over hendelser,
* garanterer ikke at den oppdagede modellen vil være sunn.

"""