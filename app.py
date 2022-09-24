import streamlit as st
import numpy as np
import pandas as pd

"""\
# Installation solaire

"""

surface_par_kwc = 5

f"""\
## Les seuils d'installation

[Diverses
aides](https://www.butagaz.fr/espace-energies/environnement/energie-solaire/tout-savoir-sur-les-aides-a-l-installation-de-panneaux-solaires)
existent pour installer des panneaux solaires, mais la plus importante est *l'obligation d'achat*
(**OA**).  Sous certaines conditions, EDF doit proposer un contrat de rachat d'électricité, à un
prix fixe sur 20 ans.  Cela permet d'assurer l'amortissement de l'investissement solaire. Les
installations ont des durées de vie supérieures à ce seuil, mais on considère souvent toute
production au delà de 20 ans comme un effet d'aubaine, et les calculs d'amortissement sont faits
sur 20 ans.

Les seuils d'aides reposent sur un chiffre clé: le nombre de kWc, ou 'kilowatts crête', installés.
Jusqu'à récemment limité à 100 kWc, le [nouvel arrêté
tarifaire](https://solaire.butagaz.fr/faq/arrete-tarifaire-solaire-100-500-kWc-du-06-octobre-2021)
du 6 Octobre 2021 ouvre la possiblité de monter jusqu'à 500 kWc. A noter toutefois que [certaines
démarches
supplémentaires](https://www.ecologie.gouv.fr/sites/default/files/Guide_EI_Installations-photovolt-au-sol_DEF_19-04-11.pdf)
sont nécessaires lorsqu'on dépasse 250 kWc installés.

Un kWc installé correspond à une surface approximative de panneaux de {surface_par_kwc} m2
([exemple](https://climatebiz.com/1kw-solar-panel/)).

L'arrêté tarifaire en vigueur donne les tarifs de rachat d'électricité actuels:
"""

st.image('img/tarifs_oa.png')


def cout_rachat(kwh, kwc):
    """
    Cout du rachat (en €) d'un nombre de kWh annuels selon la taille
    d'installation en kWc
    """
    if kwc <= 3:
        return kwh * 0.2022
    if kwc <= 9:
        return kwh * 0.1718
    if kwc <= 36:
        return kwh * 0.1231
    if kwc <= 100:
        return kwh * 0.1070
    if kwc <= 500:
        if kwh / kwc < 1100:
            return 0.1107 * kwh
        else:
            return 1100 * kwc * 0.1107 + (kwh - 1100 * kwc) * 0.04
    raise ValueError("Pas de rachat au delà de 500 kWc installés")

"""
---

## Paramétrage projet

L'outil [PVGIS](https://re.jrc.ec.europa.eu/pvg_tools/en/) de l'Europe permet d'évaluer la
production annuelle d'un kWc en un lieu donné. Exemples:

- Jonquières-Saint-Vincent: 1539 kWh / kWc / an
- Toulouse: 1320 kWh / kWc / an

"""

production_par_kwc = st.slider(
    "kWh produits annuellement par kWc installé.",
    min_value=1000, max_value=1800, value=1529)

"""
**Chiffre d'affaires (€/an) d'une installation par kWc installés**
"""

puiss = np.arange(1, 501)
installations = pd.DataFrame(
    {"Puissance installée (kWc)": puiss,
     "Chiffre d'affaires (€/an)": [cout_rachat(p*production_par_kwc, p) for p in puiss]})
st.line_chart(installations, x="Puissance installée (kWc)")

"### Coûts"

cout_kWc = st.slider("Coût d'installation par kWc, HT. Aujourd'hui autour de 800€.",
                     min_value=400, max_value=1000, value=800)

cout_raccordement = st.slider(
    "Coût total du raccordement au réseau. Dépend de la puissance d'installation",
    min_value=0, max_value=30000, value=10000, step=100)

cout_entretien = st.slider(
    "Coût d'entretien annuel par kWc. Aujourd'hui autour de 20€.",
    min_value=0, max_value=50, value=20)

puissance_installee = st.slider("Puissance installée en kWc:", min_value=1, max_value=500,
                                value=100)

surface = puissance_installee * surface_par_kwc
cout_install = cout_kWc * puissance_installee + cout_raccordement
cout_entretien = cout_entretien * puissance_installee
production_kwh = production_par_kwc * puissance_installee
chiffre_affaires = cout_rachat(production_kwh, puissance_installee)
amortissement = cout_install / (chiffre_affaires - cout_entretien)

# f"""\
# Le coût total d'installation serait de {cout_install} €.
# Son coût d'entrein annuel serait lui de {cout_entretien} €/an.
# Les économies réalisées seraient de {production_kwh} kWh par an,
# soit {chiffre_affaires} € / an. Le système s'amortirait
# donc en {amortissement:.1f} années.
# """

col1, col2, col3, col4 = st.columns(4)
col1.metric("Coût total", f"{cout_install} €")
col2.metric("Entretien annuel", f"{cout_entretien} €")
col3.metric("Chiffre d'affaires annuel", f"{chiffre_affaires} €")
col4.metric("Amortissement", f"{amortissement:.1f} ans")

annees = np.arange(21)



# Au CERFACS, 2 types d'installations semblent envisageables (en mettant de côté une installation sur le toît):
# au sol ou en ombrières.
# 
# [div]
#   [Inline][img src:"static/images/solaire_au_sol.jpg" width:300 /][/Inline]
#   [Inline][img src:"static/images/solaire_ombriere.jpg" width:300 /][/Inline]
# [/div]
# 
# Voici deux exemples de sites qui pourraient être sélectionnés: 
# un au sol d'environ 1700 m2, l'autre en ombriere sur 2300 m2.
# 
# ![installation](static/images/installation.png)
# 
# ## Puissance installée
# 
# 
# Le CERFACS consomme continuellement au moins [Dynamic value:puissance_mini /] kW,
# pour une énergie annuelle totale de [Dynamic value:conso_annuelle_mwh /] MWh,  
# soit [Display value:conso_annuelle /] kWh.
# 
# Parmi de nombreux scénarii, on peut en isoler 3 simples et illustratifs:
# 
# * Autoconsommation à 100%: la puissance produite n’excède jamais la puissance consommée, le système est là pour alléger la facture électrique du CERFACS
# * Autoconsommation avec vente du surplus: une puissance supérieure à 200 kWc mais n'exédant pas 500 kWc est installée, et le surplus vendu à EDF.
# * Production équivalente: vise la production annuelle d'énergie équivalente à la consommation actuelle du CERFACS. Ce dernier sort du contexte encadré par l'obligation d'achat EDF, et donc aucune estimation financière ne sera faite. 
# 
# ### Scenario 1: autoconsommation 100%
# 
# [derived name:'surface_scenario1' value:`puissance_mini * surface_par_kwc` /]
# [derived name:'cout_install_scenario1' value:`cout_kWc * puissance_mini + cout_raccordement` /]
# [derived name:'cout_entretien_scenario1' value:`cout_entretien * puissance_mini` /]
# [derived name:'economies_kwh_scenario1' value:`production_par_kwc * puissance_mini` /]
# [derived name:'economies_euros_scenario1' value:`economies_kwh_scenario1 * cout_kWh_edf / 100` /]
# [derived name:'amortissement_scenario1' value:`cout_install_scenario1 / (economies_euros_scenario1 - cout_entretien_scenario1) ` /]
# 
# 
# Pour ne jamais sur-produire, la puissance maximale installable est 
# la puissance minimale consommée au CERFACS, [Dynamic value:puissance_mini /] kW.
# Cela correspond à [Display value:surface_scenario1 /] m2 de panneaux.
# 
# Le coût total d'installation serait de [Display value:cout_install_scenario1 /] €.
# Son coût d'entrein annuel serait lui de [Display value:cout_entretien_scenario1 /] €/an.
# Les économies réalisées seraient de [Display value:economies_kwh_scenario1 /] kWh par an,
# soit [Display value:economies_euros_scenario1 /] € / an. Le système s'amortirait
# donc en [Display value:amortissement_scenario1 /] années.
# 
# 
# ### Scenario 2: vente du surplus
# 
# Ici, la puissance installée est limitée par l'arrêté tarifaire:
# 
# [var name:"puissance_scenario2" value:500 /]
# [Range value:puissance_scenario2 min:200 max:500 step:10 /]
# [Display value:puissance_scenario2/] kWc.
# 
# [derived name:'surface_scenario2' value:`puissance_scenario2 * surface_par_kwc` /]
# [derived name:'cout_install_scenario2' value:`cout_kWc * puissance_scenario2 + cout_raccordement` /]
# [derived name:'cout_entretien_scenario2' value:`cout_entretien * puissance_scenario2` /]
# [derived name:'ventes_kwh_scenario2' value:`production_par_kwc * puissance_scenario2 - economies_kwh_scenario1` /]
# [derived name:'ventes_euros_scenario2' value:`ventes_kwh_scenario2 * 0.1107` /]
# [derived name:'amortissement_scenario2' value:`cout_install_scenario2 / (economies_euros_scenario1 + ventes_euros_scenario2 - cout_entretien_scenario2) ` /]
# 
# Le coût total d'installation serait de [Display value:cout_install_scenario2 /] €. 
# Son coût d'entrein annuel serait lui de [Display value:cout_entretien_scenario2 /] €/an. 
# Les économies réalisées ne changent pas par rapport au scenario 1: 
# [Display value:economies_kwh_scenario1 /] kWh par an, 
# soit [Display value:economies_euros_scenario1 /] € / an. En revanche, s'y ajoutent les ventes
# de surplus à EDF, soit [Display value:ventes_kwh_scenario2 /] kWh / an ou encore [Display value:ventes_euros_scenario2 /] € / an. Le système s'amortirait 
# donc en [Display value:amortissement_scenario2 /] années.
# 
# 
# ### Scenario 3: production équivalente
# 
# [derived name:"puissance_equivalente" value:`conso_annuelle / production_par_kwc` /]
# [derived name:"surface_equivalente" value:`surface_par_kwc * puissance_equivalente` /]
# [derived name:"cout_install_scenario3" value:`cout_kWc * puissance_equivalente + cout_raccordement` /]
# 
# 
# Pour produire [Display value:conso_annuelle_mwh /] MWh/an (la consommation annuelle du CERFACS), 
# il faut [Display value:puissance_equivalente /] kWc installés, soit 
# [Display value:surface_equivalente /] m2 de panneaux. Cela correspond à un investissement 
# initial de [Display value:cout_install_scenario3 /] €.
