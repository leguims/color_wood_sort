"Parcourt les plateaux résolus et les rassemble dans le fichier 'Solutions_classees.json' par difficulté avec une écriture universelle"
import datetime
import time
import copy

import color_wood_sort as cws

# Filtrer les plateaux à 2 lignes ou 2 colonnes qui sont trop triviaux et repetitifs.
COLONNES = range(3, 8) # [2] # range(2, 12)
LIGNES = range(3, 8) # [2] # range(2, 5)
PERIODE_SCRUTATION_SECONDES = 30*60
COLONNES_VIDES_MAX = 1
PROFILER_LE_CODE = False


def classer_les_solutions(colonnes, lignes, nb_coups_min = 3):
    message = f"\n\r*** Classer les Solutions {colonnes}x{lignes}:"
    # plateau.afficher()
    lot_de_plateaux = cws.LotDePlateaux((colonnes, lignes, COLONNES_VIDES_MAX))
    if lot_de_plateaux.est_deja_termine(): # or True: # True = Classe toutes les solutions à l'heure actuel.
        message += " - Ce lot de plateaux est terminé"

        solutions_classees_json = cws.ExportJSON(delai=60, longueur=100, nom_plateau='', nom_export='Solutions_classees', repertoire='Solutions')
        solutions_classees = solutions_classees_json.importer()
        plateau = cws.Plateau(colonnes, lignes, COLONNES_VIDES_MAX)

        liste_plateaux_avec_solutions = lot_de_plateaux.to_dict().get('liste difficulte des plateaux')
        if "liste difficulte des plateaux" not in solutions_classees:
            solutions_classees["liste difficulte des plateaux"] = {}
        dict_difficulte = solutions_classees["liste difficulte des plateaux"]
        # Filtrer les plateaux sans solutions ou trop triviaux
        for difficulte, dico_nb_coups in liste_plateaux_avec_solutions.items():
            for nb_coups, liste_plateaux in dico_nb_coups.items():
                message += f"\n\r - Difficulté : {difficulte} en {nb_coups} coups : {len(liste_plateaux)} plateau{pluriel(liste_plateaux, 'x')}"
                if difficulte is not None and nb_coups is not None and int(nb_coups) >= nb_coups_min :
                    if difficulte not in dict_difficulte:
                        dict_difficulte[str(difficulte)] = {}
                    if nb_coups not in dict_difficulte[str(difficulte)]:
                        dict_difficulte[str(difficulte)][str(nb_coups)] = []
                    for plateau_ligne_texte_universel in liste_plateaux:
                        plateau.clear()
                        plateau.plateau_ligne_texte_universel = plateau_ligne_texte_universel
                        dict_difficulte[str(difficulte)][str(nb_coups)].append(plateau.plateau_ligne_texte_universel)
        ordonner_difficulte_nombre_coups(solutions_classees["liste difficulte des plateaux"])
        solutions_classees_json.forcer_export(solutions_classees)
    else:
        message += " - Ce lot de plateaux n'est pas encore terminé, pas de classement de solutions."
    return message

# Copie de 'LotDePlateaux.arret_des_enregistrements_de_difficultes_plateaux()'
def ordonner_difficulte_nombre_coups(ensemble_des_difficultes_de_plateaux):
    "Méthode qui classe les difficultés et nombres de coups des solutions"
    # Classement des difficultés
    cles_difficulte = list(ensemble_des_difficultes_de_plateaux.keys())
    if None in cles_difficulte:
        cles_difficulte.remove(None) # None est inclassable avec 'list().sort()'
    cles_difficulte.sort()
    dico_difficulte_classe = {k: ensemble_des_difficultes_de_plateaux[k] for k in cles_difficulte}
    if None in ensemble_des_difficultes_de_plateaux:
        dico_difficulte_classe[None] = ensemble_des_difficultes_de_plateaux[None]
    ensemble_des_difficultes_de_plateaux.clear()
    ensemble_des_difficultes_de_plateaux.update(dico_difficulte_classe)
    
    # Classement du nombre de coups
    for difficulte, dico_nb_coups in ensemble_des_difficultes_de_plateaux.items():
        cles_nb_coups = list(dico_nb_coups.keys())
        if None in cles_nb_coups:
            cles_nb_coups.remove(None) # None est inclassable avec 'list().sort()'
        cles_nb_coups.sort()
        dico_nb_coups_classe = {k: dico_nb_coups[k] for k in cles_nb_coups}
        if None in dico_nb_coups:
            dico_nb_coups_classe[None] = dico_nb_coups[None]
        dico_nb_coups.clear()
        dico_nb_coups.update(dico_nb_coups_classe)

def afficher_synthese():
    message = f"\n\r*** Synthèse des Solutions:"
    solutions_classees_json = cws.ExportJSON(delai=60, longueur=100, nom_plateau='', nom_export='Solutions_classees', repertoire='Solutions')
    solutions_classees = solutions_classees_json.importer()

    somme_plateaux = 0
    for difficulte, dico_nb_coups in solutions_classees.get('liste difficulte des plateaux').items():
        for nb_coups, liste_plateaux in dico_nb_coups.items():
            print(f" - Difficulté : {difficulte} en {nb_coups} coups : {len(liste_plateaux)} plateau{pluriel(liste_plateaux, 'x')}")
            if difficulte != 'None':
                somme_plateaux += len(liste_plateaux)
    print(f" - Total : {somme_plateaux} plateau{pluriel(liste_plateaux, 'x')} valide{pluriel(liste_plateaux, 's')}")

def pluriel(LIGNES, lettre='s'):
    return lettre if len(LIGNES) > 1 else ""

def chercher_en_boucle():
    messages = ""
    while(True):
        derniers_messages = messages
        messages = delta = ""
        for lignes in LIGNES:
            for colonnes in COLONNES:
                message = classer_les_solutions(colonnes, lignes)
                messages += message
                if message not in derniers_messages:
                    delta += message
        if delta:
            print(delta)
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        print(f"{current_time} - Attente entre 2 itérations de {PERIODE_SCRUTATION_SECONDES}s...")
        time.sleep(PERIODE_SCRUTATION_SECONDES)

def chercher():
    profil = cws.ProfilerLeCode('chercher_des_solutions', PROFILER_LE_CODE)
    profil.start()

    # Effacer l'existant
    solutions_classees_json = cws.ExportJSON(0, 0, '', nom_export='Solutions_classees', repertoire='Solutions')
    solutions_classees_json.effacer()
    
    messages = ""
    for lignes in LIGNES:
        for colonnes in COLONNES:
            message = classer_les_solutions(colonnes, lignes)
            messages += message
    profil.stop()
    print(messages)

    afficher_synthese()

if __name__ == "__main__":
    # chercher_en_boucle()
    chercher()
