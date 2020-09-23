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
from pm4py.objects.conversion.log import factory as log_conv_factory

#Tilføye en mer kompleks log


from pm4py.objects.log.adapters.pandas import csv_import_adapter as csv_importer
df = csv_importer.import_dataframe_from_path("receipt.csv")
log = log_conv_factory.apply(df)
from pm4py.algo.discovery.inductive import factory as inductive_miner

net, im, fm = inductive_miner.apply(log)

from pm4py.visualization.petrinet import factory as pn_vis_factory
gviz = pn_vis_factory.apply(net, im, fm)
pn_visualizer.save(gviz, "inductive_miner_recipt.png")
pn_vis_factory.view(gviz)
