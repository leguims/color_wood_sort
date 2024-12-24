"Module pour créer, résoudre et qualifier les soltuions des plateaux de 'ColorWoordSort'"
from itertools import permutations #, product, combinations#, combinations_with_replacement
import cProfile
import pstats
import time

import color_wood_sort as cws

# TODO : reprendre l'enregistrement à partir du fichier. => Pas d'amélioration, essayer de comprendre.

COLONNES = range(2, 5) # range(2, 5) #11
LIGNES = [2] # [2,3] #4
PERIODE_SCRUTATION_SECONDES = 10 # 10*60
COLONNES_VIDES_MAX = 1
MEMOIRE_MAX = 500_000_000
PROFILER_LE_CODE = False

if PROFILER_LE_CODE:
    # Profilage du code
    profil = cProfile.Profile()
    profil.enable()

while(True):
    for lignes in LIGNES:
        for colonnes in COLONNES:
            print(f"*** Generatrice {colonnes}x{lignes}: DEBUT")
            plateau = cws.Plateau(colonnes, lignes, COLONNES_VIDES_MAX)
            plateau.creer_plateau_initial()
            plateau.afficher()
            lot_de_plateaux = cws.LotDePlateaux(nb_plateaux_max = MEMOIRE_MAX)
            if not lot_de_plateaux.est_deja_termine(colonnes, lignes, COLONNES_VIDES_MAX):
                # lot_de_plateaux.fixer_taille_memoire_max(5)
                plateau_courant = cws.Plateau(colonnes, lignes, COLONNES_VIDES_MAX)
                for permutation_courante in permutations(plateau.pour_permutations):
                    # Verifier que ce plateau est nouveau
                    plateau_courant.plateau_ligne = permutation_courante
                    if not lot_de_plateaux.est_ignore(plateau_courant):
                        if lot_de_plateaux.nb_plateaux_valides % 400 == 0:
                            print(f"nb_plateaux_valides={lot_de_plateaux.nb_plateaux_valides}")
                    plateau_courant.clear()

                lot_de_plateaux.arret_des_enregistrements()
                # lot_de_plateaux.exporter_fichier_json()
                if (lot_de_plateaux.duree) < 10:
                    print(f"*** Generatrice {colonnes}x{lignes}: FIN en {
                        int((lot_de_plateaux.duree)*1000)} millisecondes")
                else:
                    print(f"*** Generatrice {colonnes}x{lignes}: FIN en {
                        int(lot_de_plateaux.duree)} secondes")
                print(f"nb_plateaux_valides={lot_de_plateaux.nb_plateaux_valides}")
                print(f"nb_plateaux_ignores={lot_de_plateaux.nb_plateaux_ignores}")
            else:
                print("Ce lot de plateaux est déjà terminé")
    time.sleep(PERIODE_SCRUTATION_SECONDES)


if PROFILER_LE_CODE:
    # Fin du profilage
    profil.disable()

    # Affichage des statistiques de profilage
    stats = pstats.Stats(profil).sort_stats('cumulative')
    stats.print_stats()

    # Exporter les statistiques dans un fichier texte
    with open('profiling_results.txt', 'w') as fichier:
        stats = pstats.Stats(profil, stream=fichier)
        #stats.sort_stats(pstats.SortKey.CUMULATIVE).print_stats(10)
        stats.sort_stats(pstats.SortKey.CUMULATIVE).print_stats()