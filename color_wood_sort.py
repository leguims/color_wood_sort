"Module pour créer, résoudre et qualifier les soltuions des plateaux de 'ColorWoordSort'"
from itertools import permutations
import datetime
import json
import copy
from pathlib import Path
from multiprocessing import Pool, cpu_count

import cProfile
import pstats

REPERTOIRE_SORTIE_RACINE = 'Analyses'

# TODO : reprendre l'enregistrement à partir du fichier. => Pas d'amélioration, essayer de comprendre.

class Plateau:
    "Classe qui implémente un plateau. Son contenu et ses différentes représentations."
    def __init__(self, nb_colonnes, nb_lignes, nb_colonnes_vides=1):
        self._nb_colonnes = nb_colonnes
        self._nb_lignes = nb_lignes
        self._nb_colonnes_vides = nb_colonnes_vides
        self._est_valide = None
        self._dico_validite_index_vide = {}
        # plateau_ligne : ['A', 'A', 'B', 'B', ' ', ' ']
        self._plateau_ligne = None
        # plateau_ligne_texte : ['AABB  ']
        self._plateau_ligne_texte = None
        # plateau_rectangle : [['A', 'A'], ['B', 'B]', [' ', ' ']]
        self._plateau_rectangle = None
        # plateau_rectangle_texte : ['AA', 'BB', '  ']
        self._plateau_rectangle_texte = None
        self._str_format = ""
        self._nb_familles = nb_colonnes - nb_colonnes_vides
        self._liste_familles = []
        self.__creer_les_familles()

    def clear(self):
        "Efface le plateau pour en écrire un nouveau"
        self._est_valide = None
        self._plateau_ligne = None
        self._plateau_ligne_texte = None
        self._plateau_ligne_texte_universel = None
        self._plateau_rectangle = None
        self._plateau_rectangle_texte = None
        self._str_format = ""

    def __str__(self):
        if not self._str_format:
            for ligne in self.plateau_rectangle:
                self._str_format += f"{ligne}\n"
        return self._str_format

    def __eq__(self, autre):
        if not isinstance(autre, Plateau):
            # Ne sont pas comparables
            return NotImplemented
        # Comparer la taille
        if self._nb_colonnes == autre._nb_colonnes \
            or self._nb_lignes == autre._nb_lignes \
            or self._nb_colonnes_vides == autre._nb_colonnes_vides :
            return False
        # Comparer le contenu
        return self._plateau_ligne == autre._plateau_ligne

    @property
    def nb_colonnes(self):
        "Nombre de colonnes du plateau"
        return self._nb_colonnes

    @property
    def nb_lignes(self):
        "Nombre de lignes du plateau"
        return self._nb_lignes

    @property
    def nb_colonnes_vides(self):
        "Nombre de colonnes vides du plateau"
        return self._nb_colonnes_vides

    @property
    def plateau_ligne(self):
        "Représentation en 1 ligne du plateau (liste)"
        return self._plateau_ligne

    @plateau_ligne.setter
    def plateau_ligne(self, plateau_ligne):
        # Pas de verification sur la validite,
        # pour pouvoir traiter les plateaux invalides
        # a ignorer.
        self.clear()
        self._plateau_ligne = tuple(plateau_ligne)

    @property
    def plateau_ligne_texte(self):
        "Représentation en 1 ligne du plateau (texte)"
        if not self._plateau_ligne_texte:
            self.__creer_plateau_ligne_texte()
        return self._plateau_ligne_texte

    @plateau_ligne_texte.setter
    def plateau_ligne_texte(self, plateau_ligne_texte):
        # Pas de verification sur la validite,
        # pour pouvoir traiter les plateaux invalides
        # a ignorer.
        self.plateau_ligne = [c for c in plateau_ligne_texte] # via setter
        self._plateau_ligne_texte = plateau_ligne_texte

    @property
    def plateau_ligne_texte_universel(self):
        "Représentation en 1 ligne du plateau (texte)"
        if not self._plateau_ligne_texte_universel:
            self.__creer_plateau_ligne_texte_universel()
        return self._plateau_ligne_texte_universel

    @plateau_ligne_texte_universel.setter
    def plateau_ligne_texte_universel(self, plateau_ligne_texte_universel):
        # Pas de verification sur la validite,
        # pour pouvoir traiter les plateaux invalides
        # a ignorer.
        self._plateau_ligne_texte = plateau_ligne_texte_universel.replace('.', '')
        self.plateau_ligne = [c for c in self._plateau_ligne_texte] # via setter

    @property
    def plateau_rectangle(self):
        "Représentation en rectangle (colonnes et lignes) du plateau (liste)"
        if not self._plateau_rectangle:
            self.__creer_plateau_rectangle()
        return self._plateau_rectangle

    @property
    def plateau_rectangle_texte(self):
        "Représentation en rectangle (colonnes et lignes) du plateau (texte)"
        if not self._plateau_rectangle_texte:
            self.__creer_plateau_rectangle_texte()
        return self._plateau_rectangle_texte

    @plateau_rectangle_texte.setter
    def plateau_rectangle_texte(self, plateau_rectangle_texte):
        # Rectangle_texte => plateau_ligne_texte
        plateau_ligne_texte = ''.join(plateau_rectangle_texte)
        # plateau_ligne_texte => plateau_ligne
        self.plateau_ligne = [c for c in plateau_ligne_texte]

    @property
    def pour_permutations(self):
        "Format du plateau utilisé pour les permutations"
        return self.plateau_ligne

    def afficher(self):
        "Afficher le plateau"
        print(self)

    def __creer_plateau_ligne_texte(self):
        """['A', 'A', 'B', 'B', ' ', ' '] => ['AABB  ']"""
        if self._plateau_ligne:
            self._plateau_ligne_texte = ''.join(self._plateau_ligne)

    def __creer_plateau_ligne_texte_universel(self):
        """['A', 'A', 'B', 'B', ' ', ' '] => ['AA.BB.  ']"""
        if not self._plateau_rectangle_texte:
            self.__creer_plateau_rectangle_texte()
        if self._plateau_rectangle_texte:
            self._plateau_ligne_texte_universel = '.'.join(self._plateau_rectangle_texte)

    def __creer_plateau_rectangle(self):
        """"['A', 'A', 'B', 'B', ' ', ' '] => [['A', 'A'], ['B', 'B'], [' ', ' ']]"""
        if self._plateau_ligne:
            self._plateau_rectangle = []
            for colonne in range(self._nb_colonnes):
                self._plateau_rectangle.append(
                    self._plateau_ligne[colonne*self._nb_lignes : (colonne + 1)*self._nb_lignes])

    def __creer_plateau_rectangle_texte(self):
        """"['A', 'A', 'B', 'B', ' ', ' '] => ['AA', 'BB', '  ']"""
        if self._plateau_ligne:
            self._plateau_rectangle_texte = []
            for colonne in range(self._nb_colonnes):
                self._plateau_rectangle_texte.append(''.join(
                    self._plateau_ligne[colonne*self._nb_lignes : (colonne + 1)*self._nb_lignes]))

    @property
    def nb_familles(self):
        "Nombre de familles de couleurs dans le plateau"
        return self._nb_familles

    def __creer_les_familles(self):
        "Créer une liste des familles"
        if not self._liste_familles:
            self._liste_familles = [chr(ord('A')+F) for F in range(self._nb_familles) ]
        return self._liste_familles

    def creer_plateau_initial(self):
        """"Cree un plateau en ligne initial = ['A', 'A', 'B', 'B', ' ', ' ']"""
        if not self._plateau_ligne:
            self.plateau_ligne = tuple(
                [self._liste_familles[famille] for famille in range(self._nb_familles)
                                                 for membre in range(self._nb_lignes)]
                +[' ' for vide in range(self._nb_colonnes_vides)
                         for membre in range(self._nb_lignes)] )

    @property
    def est_valide(self):
        """"Verifie si le plateau en parametre est valide et interessant"""
        if self._plateau_ligne and self._est_valide is None:
            # Pour chaque colonne, les cases vides sont sur les dernieres cases
            case_vide = ' '

            # Construction de la position des cases vides
            count = self._plateau_ligne.count(case_vide)
            index_vide = []
            index_courant = -1
            for _ in range(count):
                index_courant = self._plateau_ligne.index(case_vide, index_courant+1)
                index_vide.append(index_courant)
            index_vide = tuple(index_vide) # l'index_vide devient invariable
            
            # Est-ce que cet index est valide ?
            if index_vide in self._dico_validite_index_vide:
                return self._dico_validite_index_vide.get(index_vide)
            
            # Index inconnu, identifier sa validité
            for colonne in range(self._nb_colonnes):
                case_vide_presente = False
                for ligne in range(self._nb_lignes):
                    if not case_vide_presente:
                        # Chercher la premiere case vide de la colonne
                        if (colonne * self._nb_lignes + ligne) in index_vide:
                            case_vide_presente = True
                    else:
                        # Toutes les autres case de la lignes doivent etre vides
                        if (colonne * self._nb_lignes + ligne) not in index_vide:
                            self._est_valide = False
                            self._dico_validite_index_vide[index_vide] = self._est_valide
                            return self._est_valide
            self._est_valide = True
            self._dico_validite_index_vide[index_vide] = self._est_valide

            # Est-ce que le plateau est interessant ?
            # Une colonne achevée est sans interet.
            if self.une_colonne_est_pleine_et_monocouleur():
                self._est_valide = False
                return self._est_valide
        return self._est_valide

    def la_colonne_est_vide(self, colonne):
        if colonne >= self.nb_colonnes:
            raise IndexError(f"Le numéro de colonne est hors du plateau ({colonne}>={self.nb_colonnes}).")
        return self.plateau_rectangle_texte[colonne].isspace()

    def la_colonne_est_pleine(self, colonne):
        if colonne >= self.nb_colonnes:
            raise IndexError(f"Le numéro de colonne est hors du plateau ({colonne}>={self.nb_colonnes}).")
        return self.plateau_rectangle_texte[colonne].count(' ') == 0

    def la_colonne_est_pleine_et_monocouleur(self, colonne):
        est_pleine = self.la_colonne_est_pleine(colonne)
        colonne_texte = self.plateau_rectangle_texte[colonne]
        premiere_case = colonne_texte[0]
        return est_pleine and colonne_texte.count(premiere_case) == self.nb_lignes

    def une_colonne_est_pleine_et_monocouleur(self):
        for colonne in range(self.nb_colonnes):
            if self.la_colonne_est_pleine_et_monocouleur(colonne):
                return True
        return False

    def la_couleur_au_sommet_de_la_colonne(self, colonne):
        if colonne >= self.nb_colonnes:
            raise IndexError(f"Le numéro de colonne est hors du plateau ({colonne}>={self.nb_colonnes}).")
        colonne_texte = self.plateau_rectangle_texte[colonne]
        derniere_case_non_vide = colonne_texte.strip()[-1]
        return derniere_case_non_vide

    def _compter_les_couleurs_identiques_au_sommet(self, colonne_texte, couleur):
        nb = 0
        colonne_inversee = list(colonne_texte.rstrip())
        colonne_inversee.reverse()
        for case in colonne_inversee:
            if case == couleur:
                nb += 1
            else:
                break
        return nb

    def nombre_de_case_vide_de_la_colonne(self, colonne):
        if colonne >= self.nb_colonnes:
            raise IndexError(f"Le numéro de colonne est hors du plateau ({colonne}>={self.nb_colonnes}).")
        colonne_texte = self.plateau_rectangle_texte[colonne]
        return len(colonne_texte) - len(colonne_texte.rstrip())

    def nombre_de_cases_monocouleur_au_sommet_de_la_colonne(self, colonne):
        couleur = self.la_couleur_au_sommet_de_la_colonne(colonne)
        colonne_texte = self.plateau_rectangle_texte[colonne]
        return self._compter_les_couleurs_identiques_au_sommet(colonne_texte, couleur)

    def deplacer_blocs(self, colonne_depart, colonne_arrivee, nombre_blocs = 1):
        if nombre_blocs != self.nombre_de_cases_monocouleur_au_sommet_de_la_colonne(colonne_depart):
            raise ValueError("Le nombre de bloc à déplacer est différent à celui du plateau")
        self.annuler_le_deplacer_blocs(colonne_arrivee, colonne_depart, nombre_blocs)

    def annuler_le_deplacer_blocs(self, colonne_depart_a_annuler, colonne_arrivee_a_annuler, nombre_blocs = 1):
        if nombre_blocs > self.nombre_de_cases_monocouleur_au_sommet_de_la_colonne(colonne_arrivee_a_annuler):
            raise ValueError("Le nombre de bloc à déplacer est supérieur à celui du plateau")
        if nombre_blocs > self.nombre_de_case_vide_de_la_colonne(colonne_depart_a_annuler):
            raise ValueError("Le nombre de bloc à déplacer est plus grand que ce que la colonne peut recevoir")
        couleur = self.la_couleur_au_sommet_de_la_colonne(colonne_arrivee_a_annuler)
        case_vide = ' '
        plateau = self.plateau_rectangle_texte
        # Inverser la colonne pour remplacer les couleur du haut, puis rétablir l'ordre
        # colonne de depart : 'ABAA' => 'AABA' => '  BA' => 'AB  '
        plateau[colonne_arrivee_a_annuler] = plateau[colonne_arrivee_a_annuler][::-1].replace(couleur, case_vide, nombre_blocs)[::-1]
        # colonne d'arrivee : 'C   ' => 'CAA '
        plateau[colonne_depart_a_annuler] = plateau[colonne_depart_a_annuler].replace(case_vide, couleur, nombre_blocs)
        self.plateau_rectangle_texte = plateau

    def a_gagne(self):
        """"Verifie si le plateau actuel est gagnant"""
        return False

class LotDePlateaux:
    """Classe qui gère les lots de plateaux pour parcourir l'immensité des plateaux existants.
Le chanmps nb_plateaux_max désigne la mémoire allouée pour optimiser la recherche."""
    def __init__(self, dim_plateau, nb_plateaux_max = 1_000_000):
        # Plateau de base
        self._nb_colonnes = dim_plateau[0]
        self._nb_lignes = dim_plateau[1]
        self._nb_colonnes_vides = dim_plateau[2]
        self._plateau_courant = Plateau(self._nb_colonnes, self._nb_lignes, self._nb_colonnes_vides)

        # Gestion du lot de plateau
        self._ignorer_ensemble_des_plateaux_valides_connus = set()
        self._ensemble_des_plateaux_valides = set()
        self._ensemble_des_plateaux_a_ignorer = set()
        self._ensemble_des_plateaux_iteres = set()
        self._ensemble_des_permutations_de_nombres = None
        self._dico_compteur_des_plateaux_a_ignorer = {}
        self._nb_plateaux_max = nb_plateaux_max
        self._debut_recherche_des_plateaux_valides = datetime.datetime.now().timestamp()
        self._fin_recherche_des_plateaux_valides = None
        self._export_json = None
        self._ensemble_des_difficultes_de_plateaux = {}
        self._debut_recherche_des_solutions = None
        self._fin_recherche_des_solutions = None
        self._a_change = False
        self._difficulte = None
    
    def __len__(self):
        return self.nb_plateaux_valides

    def to_dict(self):
        dict_lot_de_plateaux = {}
        
        # Ajouter les informations de colonnes et lignes si disponibles
        if self._nb_colonnes is not None:
            dict_lot_de_plateaux['colonnes'] = self._nb_colonnes
            dict_lot_de_plateaux['lignes'] = self._nb_lignes
            dict_lot_de_plateaux['colonnes vides'] = self._nb_colonnes_vides

        # Ajouter les timestamps de début et de fin
        dict_lot_de_plateaux['debut'] = self.debut
        dict_lot_de_plateaux['fin'] = self.fin

        # Formater la durée de manière lisible
        dict_lot_de_plateaux['duree'] = self.formater_duree(self.duree)
        
        # Indiquer si la recherche est terminée
        dict_lot_de_plateaux['recherche terminee'] = self._fin_recherche_des_plateaux_valides is not None

        # Ajouter le nombre de plateaux et la liste des plateaux valides
        dict_lot_de_plateaux['nombre plateaux'] = len(self.plateaux_valides)
        liste_plateaux_universelle = []
        plateau = Plateau(self._nb_colonnes, self._nb_lignes, self._nb_colonnes_vides)
        for plateau_txt in self.plateaux_valides:
            plateau.clear()
            plateau.plateau_ligne_texte = plateau_txt
            liste_plateaux_universelle.append(plateau.plateau_ligne_texte_universel)
        dict_lot_de_plateaux['liste plateaux'] = liste_plateaux_universelle

        # Ajouter les timestamps de début et de fin des solutions
        dict_lot_de_plateaux['debut solutions'] = self._debut_recherche_des_solutions
        dict_lot_de_plateaux['fin solutions'] = self._fin_recherche_des_solutions

        # Ajouter la duree de recherche des solutions
        if self._debut_recherche_des_solutions is not None \
            and self._debut_recherche_des_solutions is not None:
            duree_solution = self._fin_recherche_des_solutions - self._debut_recherche_des_solutions
            dict_lot_de_plateaux['duree solutions'] = self.formater_duree(duree_solution)
        
        # La difficulté est un entier, mais est enregistrée comme une chaine de caracteres dans le JSON. Surement car c'est une clé.
        liste_difficultes_universelles = {}
        plateau = Plateau(self._nb_colonnes, self._nb_lignes, self._nb_colonnes_vides)
        for difficulte, dico_nb_coups in self._ensemble_des_difficultes_de_plateaux.items():
            liste_difficultes_universelles[difficulte] = {}
            for nb_coups, liste_plateaux in dico_nb_coups.items():
                liste_difficultes_universelles[difficulte][nb_coups] = []
                for plateau_txt in liste_plateaux:
                    plateau.clear()
                    plateau.plateau_ligne_texte = plateau_txt
                    liste_difficultes_universelles[difficulte][nb_coups].append(plateau.plateau_ligne_texte_universel)
        dict_lot_de_plateaux['liste difficulte des plateaux']= liste_difficultes_universelles

        return dict_lot_de_plateaux

    def formater_duree(self, duree):
        """Formater la durée en une chaîne de caractères lisible."""
        if duree < 0.001:
            return f"{int(duree * 1_000_000)} microsecondes"
        elif duree < 1:
            return f"{int(duree * 1_000)} millisecondes"
        elif duree < 60:
            return f"{int(duree)} secondes"
        else:
            minutes, secondes = divmod(duree, 60)
            heures, minutes = divmod(minutes, 60)
            jours, heures = divmod(heures, 24)
            if jours > 0:
                return f"{int(jours)} jours {int(heures)} heures"
            elif heures > 0:
                return f"{int(heures)} heures {int(minutes)} minutes"
            else:
                return f"{int(minutes)} minutes {int(secondes)} secondes"

    def arret_des_enregistrements(self):
        "Méthode qui finalise la recherche de plateaux"
        self._ensemble_des_plateaux_a_ignorer.clear()
        self._dico_compteur_des_plateaux_a_ignorer.clear()
        self._fin_recherche_des_plateaux_valides = datetime.datetime.now().timestamp()
        self.exporter_fichier_json()

    def est_ignore(self, permutation_plateau):
        "Retourne 'True' si le plateau est deja connu"
        # Ignorer toutes les permutations jusqu'à ce que toute les solutions connues soient trouvées
        if len(self._ignorer_ensemble_des_plateaux_valides_connus) > 0 :
            self._ignorer_ensemble_des_plateaux_valides_connus.discard(permutation_plateau)
            if len(self._ignorer_ensemble_des_plateaux_valides_connus) == 0:
                print(f"[{self._nb_colonnes}x{self._nb_lignes}] Fin de parcours des plateaux déjà connus.")
            return True
        
        # Ignorer les permutations en doublon
        if permutation_plateau in self._ensemble_des_plateaux_iteres:
            return True
        else:
            if len(self._ensemble_des_plateaux_iteres) > self._nb_plateaux_max:
                self._ensemble_des_plateaux_iteres.clear()
            self._ensemble_des_plateaux_iteres.add(permutation_plateau)
        
        if permutation_plateau not in self._ensemble_des_plateaux_valides \
            and permutation_plateau not in self._ensemble_des_plateaux_a_ignorer:
            self._plateau_courant.clear()
            self._plateau_courant.plateau_ligne_texte = permutation_plateau
            # plateau.afficher()
            # Verifier que la plateau est valide
            if self._plateau_courant.est_valide:
                # Enregistrer la permutation courante qui est un nouveau plateau valide
                self.__ajouter_le_plateau(self._plateau_courant)
                return False
            else:
                # Nouveau Plateau invalide, on l'ignore
                self.__ignorer_le_plateau_et_ses_permutations(self._plateau_courant)
                return True
        self.__compter_plateau_a_ignorer(self._plateau_courant)
        return True

    def mettre_a_jour_les_plateaux_valides(self):
        "Vérifie la liste des plateau valide car les regles ont changé. Utile pour les recherches déjà terminées."
        liste_nouveaux_plateaux_invalides = []
        for plateau in self.plateaux_valides:
            if plateau not in liste_nouveaux_plateaux_invalides:
                plateau_courant = Plateau(self._nb_colonnes, self._nb_lignes, self._nb_colonnes_vides)
                plateau_courant.plateau_ligne_texte = plateau
                if not plateau_courant.est_valide:
                    print(f"'{plateau_courant.plateau_ligne_texte_universel}' : invalide à supprimer")
                    liste_nouveaux_plateaux_invalides.append(plateau)

                # Vérifier de nouvelles formes de doublons (permutations) dans les plateaux valides
                # Construire les permutations de colonnes et jetons, rationnaliser et parcourir
                liste_permutations = self.__construire_les_permutations_de_colonnes(plateau_courant) \
                                    + self.__construire_les_permutations_de_jetons(plateau_courant)
                # TODO : CORRIGER CA : for plateau_a_ignorer in set(tuple(liste_permutations)):
                for plateau_a_ignorer in liste_permutations:
                    # Tester si la permutation de colonne/jeton était déjà dans les plateaux valides
                    if plateau_a_ignorer.plateau_ligne_texte in self._ensemble_des_plateaux_valides:
                        print(f"'{plateau_a_ignorer.plateau_ligne_texte_universel}' : en doublon avec {plateau_courant.plateau_ligne_texte_universel}")
                        liste_nouveaux_plateaux_invalides.append(plateau_a_ignorer.plateau_ligne_texte)

        if liste_nouveaux_plateaux_invalides:
            for plateau in liste_nouveaux_plateaux_invalides:
                self.plateaux_valides.remove(plateau)
            self._export_json.forcer_export(self)

    @property
    def plateaux_valides(self):
        "Ensemble des plateaux valides"
        return self._ensemble_des_plateaux_valides

    @property
    def nb_plateaux_valides(self):
        "Nombre de plateaux valides"
        return len(self._ensemble_des_plateaux_valides)

    @property
    def nb_plateaux_ignores(self):
        "Nombre de plateaux ignorés"
        return len(self._ensemble_des_plateaux_a_ignorer)

    @property
    def debut(self):
        "Heure de début de la recherche"
        return self._debut_recherche_des_plateaux_valides

    @property
    def fin(self):
        "Heure de fin (ou courante) de la recherche"
        if self._fin_recherche_des_plateaux_valides:
            return self._fin_recherche_des_plateaux_valides
        return datetime.datetime.now().timestamp()

    @property
    def duree(self):
        "Durée de la recherche"
        return self.fin - self.debut

    def __ajouter_le_plateau(self, plateau: Plateau):
        "Memorise un plateau deja traite"
        # Avec les réductions de memoires, un nouveau plateau pourrait-etre une ancienne
        # permutation effacée. Il faut vérifier les permutations avant d'ajouter définitivement
        # le plateau.
        nouveau_plateau = True
        # Construire les permutations de colonnes et jetons, rationnaliser et parcourir
        liste_permutations = self.__construire_les_permutations_de_colonnes(plateau) \
                            + self.__construire_les_permutations_de_jetons(plateau)
        for plateau_a_ignorer in set(liste_permutations):
            # Tester si la permutation de colonne/jeton était déjà dans les plateaux valides
            if plateau_a_ignorer.plateau_ligne_texte in self._ensemble_des_plateaux_valides:
                nouveau_plateau = False
            # Ignorer toutes les permutations
            self.__ignorer_le_plateau(plateau_a_ignorer)

        if not nouveau_plateau:
            # Ignorer le "Faux" nouveau plateau
            self.__ignorer_le_plateau(plateau)
        else:
            self._ensemble_des_plateaux_valides.add(plateau.plateau_ligne_texte)
            self._a_change = True
            # _a_change | exporter() || _a_change
            # ===================================
            #   False   |   False    ||  False
            #   False   |   True     ||  False
            #   True    |   False    ||  True
            #   False   |   True     ||  False
            self._a_change = self._a_change and not self._export_json.exporter(self)

    def __construire_les_permutations_de_colonnes(self, plateau: Plateau):
        """Méthode qui construit les permutations de colonnes d'un plateau.
Le plateau lui-même n'est pas dans les permutations."""
        liste_permutations_de_colonnes = []
        # 'set()' est utilisé pour éliminer les permutations identiques
        for permutation_courante in set(permutations(plateau.plateau_rectangle_texte)):
            plateau_a_ignorer = Plateau(self._nb_colonnes, self._nb_lignes, self._nb_colonnes_vides)
            plateau_a_ignorer.plateau_rectangle_texte = permutation_courante

            # Ignorer toutes les permutations
            if plateau_a_ignorer.plateau_ligne_texte != plateau.plateau_ligne_texte:
                liste_permutations_de_colonnes.append(plateau_a_ignorer)
        return liste_permutations_de_colonnes

    def __construire_les_permutations_de_jetons(self, plateau: Plateau):
        """Méthode qui construit les permutations de jetons d'un plateau.
Par exemple, ces deux plateaux sont équivalents pour un humain : 'ABC.CBA' ==(A devient B)== 'BAC.CAB'
Le plateau lui-même n'est pas dans les permutations."""
        # Liste des permutations 'nombre'
        if self._ensemble_des_permutations_de_nombres is None:
            self._ensemble_des_permutations_de_nombres = set(permutations(range(self._plateau_courant.nb_familles)))

        case_vide = ' '
        liste_permutations_de_jetons = []
        for permutation_nombre_courante in self._ensemble_des_permutations_de_nombres:
            # Pour chaque permutation, transposer le plateau
            permutation_jeton_courante = []
            for jeton in plateau.plateau_ligne:
                if jeton != case_vide:
                    # Pour chaque jeton (sauf case vide), appliquer sa transposition
                    indice_jeton = ord(jeton) - ord(self._plateau_courant._liste_familles[0])
                    nouvel_indice_jeton = permutation_nombre_courante[indice_jeton]
                    nouveau_jeton = self._plateau_courant._liste_familles[nouvel_indice_jeton]
                else:
                    nouveau_jeton = case_vide
                # Création de la transposition jeton après jeton
                permutation_jeton_courante.append(nouveau_jeton)
            # Le plateau transposé est le plateau à ingorer
            plateau_a_ignorer = Plateau(self._nb_colonnes, self._nb_lignes, self._nb_colonnes_vides)
            plateau_a_ignorer.plateau_ligne = permutation_jeton_courante
            if plateau_a_ignorer.plateau_ligne_texte != plateau.plateau_ligne_texte:
                liste_permutations_de_jetons.append(plateau_a_ignorer)
        return liste_permutations_de_jetons

    def __compter_plateau_a_ignorer(self, plateau_a_ignorer: Plateau):
        "Compte un plateau a ignorer"
        if plateau_a_ignorer.plateau_ligne_texte not in self._dico_compteur_des_plateaux_a_ignorer:
            self._dico_compteur_des_plateaux_a_ignorer[plateau_a_ignorer.plateau_ligne_texte] = 1
        else:
            self._dico_compteur_des_plateaux_a_ignorer[plateau_a_ignorer.plateau_ligne_texte] += 1

    def __ignorer_le_plateau_et_ses_permutations(self, plateau_a_ignorer: Plateau):
        # 'set()' est utilisé pour éliminer les permutations identiques
        for permutation_courante in set(permutations(plateau_a_ignorer.plateau_rectangle_texte)):
            plateau = Plateau(self._nb_colonnes, self._nb_lignes, self._nb_colonnes_vides)
            plateau.plateau_rectangle_texte = permutation_courante
            self.__ignorer_le_plateau(plateau)

    def __ignorer_le_plateau(self, plateau_a_ignorer: Plateau):
        "Ignore un plateau et met a jour les ensembles et compteurs"
        # Ignorer le plateau
        self._ensemble_des_plateaux_a_ignorer.add(plateau_a_ignorer.plateau_ligne_texte)
        # Compter l'occurence
        self.__compter_plateau_a_ignorer(plateau_a_ignorer)
        # Optimiser la memoire
        self.__reduire_memoire()

    def __reduire_memoire(self):
        "Optimisation memoire quand la memoire maximum est atteinte"
        # Trier par valeur croissantes
        if len(self._ensemble_des_plateaux_a_ignorer) > self._nb_plateaux_max:
            print('*' * 80 + ' Réduction mémoire.')
            dico_trie_par_valeur_croissantes = dict(sorted(
                self._dico_compteur_des_plateaux_a_ignorer.items(), key=lambda item: item[1]))
            # for key, value in dico_trie_par_valeur_croissantes.items():
            #     print(f"[reduire_memoire] ({key}, {value})")

            # Vider les memoires et compteurs
            self._dico_compteur_des_plateaux_a_ignorer.clear()
            self._ensemble_des_plateaux_a_ignorer.clear()
            # print(len(self._dico_compteur_des_plateaux_a_ignorer))
            # print(len(self._ensemble_des_plateaux_a_ignorer))

            for _ in range(int(self._nb_plateaux_max/10)):
                if len(dico_trie_par_valeur_croissantes) == 0:
                    break
                # Reconduire les 10% les plus sollicites
                key, _ = dico_trie_par_valeur_croissantes.popitem()
                # print(f"[reduire_memoire] Conservation de ({key}, {_})")
                self._ensemble_des_plateaux_a_ignorer.add(key)
                self._dico_compteur_des_plateaux_a_ignorer[key] = 1
            dico_trie_par_valeur_croissantes.clear()
            # print(len(dico_trie_par_valeur_croissantes))

    def fixer_taille_memoire_max(self, nb_plateaux_max):
        "Fixe le nombre maximum de plateau a memoriser"
        if nb_plateaux_max > 0:
            self._nb_plateaux_max = nb_plateaux_max
        self.__reduire_memoire()

    def __init_export_json(self):
        nom = f"Plateaux_{self._nb_colonnes}x{self._nb_lignes}"
        self._export_json = ExportJSON(delai=60, longueur=100, nom_plateau=nom, nom_export=nom)

    def exporter_fichier_json(self):
        """Enregistre un fichier JSON avec les plateaux valides"""
        # Enregistrement des donnees dans un fichier JSON
        if self.nb_plateaux_valides > 0 and self._a_change:
            self._a_change = self._a_change and not self._export_json.forcer_export(self)

    def __importer_fichier_json(self):
        """Lit l'enregistrement JSON s'il existe"""
        data_json = self._export_json.importer()
        if "colonnes" in data_json:
            self._nb_colonnes = data_json["colonnes"]
        if "lignes" in data_json:
            self._nb_lignes = data_json["lignes"]
        if "colonnes vides" in data_json:
            self._nb_colonnes_vides = data_json["colonnes vides"]
        if "debut" in data_json:
            self._debut_recherche_des_plateaux_valides = data_json["debut"]
        if "recherche terminee" in data_json and not data_json["recherche terminee"]:
            self._fin_recherche_des_plateaux_valides = None
        elif "fin" in data_json:
            self._fin_recherche_des_plateaux_valides = data_json["fin"]

        # Rejouer les plateaux déjà trouvés
        if 'nombre plateaux' in data_json \
            and data_json['nombre plateaux'] > 0:
            # Récupération des plateaux valides que la recherche soit terminée ou non
            # pas d'optilmisation identifiée pour accelerer la poursuite de la recherche
            plateau = Plateau(self._nb_colonnes, self._nb_lignes, self._nb_colonnes_vides)
            for plateau_valide in data_json['liste plateaux']:
                # 'self.est_ignore()' n'est pas utilisé, car il va modifier le fichier
                #  d'export quand des plateaux valides sont ajoutés. Dans notre cas, il
                #  faut ajouter les plateaux depuis l'export en considérant qu'il sont fiables.
                plateau.clear()
                plateau.plateau_ligne_texte_universel = plateau_valide
                self._ensemble_des_plateaux_valides.add(plateau.plateau_ligne_texte)

        # Solutions
        if "debut solutions" in data_json:
            self._debut_recherche_des_solutions = data_json["debut solutions"]
        if "fin solutions" in data_json:
            self._fin_recherche_des_solutions = data_json["fin solutions"]
        if 'liste difficulte des plateaux' in data_json and data_json['liste difficulte des plateaux']:
            # Convertir 'difficulte' et 'nb_coups' en entiers
            plateau = Plateau(self._nb_colonnes, self._nb_lignes, self._nb_colonnes_vides)
            for difficulte_str, dico_nb_coups in data_json['liste difficulte des plateaux'].items():
                if difficulte_str == 'null':
                    difficulte = None
                else:
                    difficulte = int(difficulte_str)
                for nb_coups_str, liste_plateaux in dico_nb_coups.items():
                    if nb_coups_str == 'null':
                        nb_coups = None
                    else:
                        nb_coups = int(nb_coups_str)
                    if difficulte not in self._ensemble_des_difficultes_de_plateaux:
                        self._ensemble_des_difficultes_de_plateaux[difficulte] = {}
                    if nb_coups not in self._ensemble_des_difficultes_de_plateaux.get(difficulte):
                        self._ensemble_des_difficultes_de_plateaux[difficulte][nb_coups] = []
                    for plateau_txt in liste_plateaux:
                        plateau.clear()
                        plateau.plateau_ligne_texte_universel = plateau_txt
                        self._ensemble_des_difficultes_de_plateaux[difficulte][nb_coups].append(plateau.plateau_ligne_texte)

    def est_deja_termine(self):
        self.__init_export_json()
        self.__importer_fichier_json()

        recherche_terminee = self._fin_recherche_des_plateaux_valides is not None
        self._ignorer_ensemble_des_plateaux_valides_connus = copy.deepcopy(self._ensemble_des_plateaux_valides)
        return recherche_terminee
    
    def est_deja_connu_difficulte_plateau(self, plateau: Plateau):
        "Méthode qui vérifie si le plateau est déjà résolu"
        est_connu = False
        for difficulte in self._ensemble_des_difficultes_de_plateaux.keys():
            if plateau.plateau_ligne_texte in self._ensemble_des_difficultes_de_plateaux[difficulte]:
                est_connu = True
                break
        return est_connu

    def definir_difficulte_plateau(self, plateau: Plateau, difficulte, nb_coups):
        "Méthode qui enregistre les difficultés des plateaux et la profondeur de leur solution"
        if self._debut_recherche_des_solutions is None:
            self._debut_recherche_des_solutions = datetime.datetime.now().timestamp()
        if difficulte not in self._ensemble_des_difficultes_de_plateaux:
            self._ensemble_des_difficultes_de_plateaux[difficulte] = {}
        if nb_coups not in self._ensemble_des_difficultes_de_plateaux[difficulte]:
            self._ensemble_des_difficultes_de_plateaux[difficulte][nb_coups] = []
        if plateau.plateau_ligne_texte not in self._ensemble_des_difficultes_de_plateaux[difficulte][nb_coups]:
            self._ensemble_des_difficultes_de_plateaux[difficulte][nb_coups].append(plateau.plateau_ligne_texte)
            self._a_change = True
            self._fin_recherche_des_solutions = datetime.datetime.now().timestamp()

    def effacer_difficulte_plateau(self):
        "Méthode qui enregistre les difficultés des plateaux et la profondeur de leur solution"
        self._ensemble_des_difficultes_de_plateaux.clear()
        self._a_change = True

    def arret_des_enregistrements_de_difficultes_plateaux(self):
        "Méthode qui finalise l'arret des enregistrements des difficultés de plateaux"
        # Classement des difficultés
        cles_difficulte = list(self._ensemble_des_difficultes_de_plateaux.keys())
        if None in cles_difficulte:
            cles_difficulte.remove(None) # None est inclassable avec 'list().sort()'
        cles_difficulte_classees = copy.deepcopy(cles_difficulte)
        cles_difficulte_classees.sort()
        if cles_difficulte != cles_difficulte_classees:
            # Ordonner l'ensemble par difficulté croissante
            dico_difficulte_classe = {k: self._ensemble_des_difficultes_de_plateaux.get(k) for k in cles_difficulte_classees}
            if None in self._ensemble_des_difficultes_de_plateaux:
                dico_difficulte_classe[None] = self._ensemble_des_difficultes_de_plateaux.get(None)
            self._ensemble_des_difficultes_de_plateaux = copy.deepcopy(dico_difficulte_classe)
        
        # Classement du nombre de coups
        for difficulte, dico_nb_coups in self._ensemble_des_difficultes_de_plateaux.items():
            cles_nb_coups = list(dico_nb_coups.keys())
            if None in cles_nb_coups:
                cles_nb_coups.remove(None) # None est inclassable avec 'list().sort()'
            cles_nb_coups_classees = copy.deepcopy(cles_nb_coups)
            cles_nb_coups_classees.sort()
            if cles_nb_coups != cles_nb_coups_classees:
                # Ordonner l'ensemble par nombre de coups croissant
                dico_nb_coups_classe = {k: dico_nb_coups.get(k) for k in cles_nb_coups_classees}
                if None in self._ensemble_des_difficultes_de_plateaux.get(difficulte):
                    dico_nb_coups_classe[None] = self._ensemble_des_difficultes_de_plateaux.get(difficulte).get(None)
                self._ensemble_des_difficultes_de_plateaux[difficulte] = copy.deepcopy(dico_nb_coups_classe)
        self.exporter_fichier_json()

    @property
    def difficulte_plateaux(self):
        "Ensemble des difficultés de plateaux résolus"
        return self._ensemble_des_difficultes_de_plateaux

    @property
    def nb_plateaux_solutionnes(self):
        "Nombre de plateaux valides"
        return sum([len(liste_plateaux) for difficulte, dico_nb_coups in self._ensemble_des_difficultes_de_plateaux.items() for nb_coups, liste_plateaux in dico_nb_coups.items()])

class ResoudrePlateau:
    "Classe de résultion d'un plateau par parcours de toutes les possibilités de choix"
    def __init__(self, plateau_initial: Plateau):
        self._plateau_initial = copy.deepcopy(plateau_initial)
        self._liste_des_solutions = []
        # Statistiques des solutions:
        #   - la plus longue
        #   - la plus courte
        #   - la moyenne
        #   - le nombre de solution
        # Les longueurs sont toutes égales (courtes et longues).
        # La longueur de la solution est la grandeur qui quantifie la difficulte du plateau.
        self._statistiques = {}
        self._liste_plateaux_gagnants = None
        self._liste_des_choix_possibles = None
        self._liste_des_choix_courants = None
        nom_plateau = f"Plateaux_{self._plateau_initial.nb_colonnes}x{self._plateau_initial._nb_lignes}"
        nom = f"Plateaux_{self._plateau_initial.nb_colonnes}x{self._plateau_initial._nb_lignes}_Resolution_{plateau_initial.plateau_ligne_texte.replace(' ', '-')}"
        self._export_json_analyses = ExportJSON(delai=60, longueur=100, nom_plateau=nom_plateau, nom_export=nom, repertoire = 'Analyses')
        self._export_json_solutions = ExportJSON(delai=60, longueur=100, nom_plateau=nom_plateau, nom_export=nom, repertoire = 'Solutions')
        self.__importer_fichier_json()

    def __len__(self):
        "La longueur de la solution définit la difficulté"
        # Le nombre de soltuioon n'a pas d'incidence sur la difficulté
        if self.solution_la_plus_courte:
            return self.solution_la_plus_courte
        return 0

    def to_dict(self):
        dict_resoudre_plateau = {}
        dict_resoudre_plateau['plateau'] = self._plateau_initial.plateau_ligne_texte_universel
        dict_resoudre_plateau['nombre de solutions'] = self.nb_solutions
        dict_resoudre_plateau['solution la plus courte'] = self.solution_la_plus_courte
        dict_resoudre_plateau['solution la plus longue'] = self.solution_la_plus_longue
        dict_resoudre_plateau['solution moyenne'] = self.solution_moyenne
        dict_resoudre_plateau['liste des solutions'] = self._liste_des_solutions
        return dict_resoudre_plateau

    def __ensemble_des_choix_possibles(self):
        "Liste tous les choix possible pour un plateau (valide et invalides)"
        if not self._liste_des_choix_possibles:
            # Liste de tous les possibles à construire selon la dimension du plateau
            self._liste_des_choix_possibles = []
            for depart in range(self._plateau_initial.nb_colonnes):
                for arrivee in range(self._plateau_initial.nb_colonnes):
                    if depart != arrivee:
                        self._liste_des_choix_possibles.append(tuple([depart, arrivee]))
        # Nombre de choix = (nb_colonnes * (nb_colonnes-1))
        return self._liste_des_choix_possibles

    def __ensemble_des_plateaux_gagnants(self):
        "Liste tous les plateaux gagnants"
        if self._liste_plateaux_gagnants is None:
            nb_c = self._plateau_initial.nb_colonnes
            nb_l = self._plateau_initial.nb_lignes
            nb_cv = self._plateau_initial.nb_colonnes_vides
            plateau_gagnant = Plateau(nb_c, nb_l, nb_cv)
            plateau_gagnant.creer_plateau_initial()

            self._liste_plateaux_gagnants = []
            # 'set()' est utilisé pour éliminer les permutations identiques
            for permutation_courante in set(permutations(plateau_gagnant.plateau_rectangle_texte)):
                plateau_gagnant_courant = Plateau(nb_c, nb_l, nb_cv)
                plateau_gagnant_courant.plateau_rectangle_texte = permutation_courante
                self._liste_plateaux_gagnants.append(plateau_gagnant_courant.plateau_ligne_texte)
        return self._liste_plateaux_gagnants

    def __ajouter_choix(self, plateau: Plateau, choix):
        "Enregistre un choix et modifie le plateau selon ce choix"
        # Enregistrer le choix
        self._liste_des_choix_courants.append(choix[0:2])
        # Modifier le plateau
        plateau.deplacer_blocs(*choix)

    def __retirer_choix(self, plateau: Plateau, choix):
        "Annule le dernier choix et restaure le plateau precedent"
        # Désenregistrer le choix
        self._liste_des_choix_courants.pop()
        # Modifier le plateau
        plateau.annuler_le_deplacer_blocs(*choix)

    def __est_valide(self, plateau: Plateau, choix):
        "Vérifie la validité du choix"
        c_depart, c_arrivee = choix
        # INVALIDE Si les colonnes de départ et d'arrivée sont identiques
        if c_depart == c_arrivee:
            return False
        # INVALIDE Si la colonne de départ est vide
        if plateau.la_colonne_est_vide(c_depart):
            return False
        # INVALIDE Si la colonne de départ est pleine et monocouleur
        if plateau.la_colonne_est_pleine_et_monocouleur(c_depart):
            return False
        # INVALIDE Si la colonne d'arrivée est pleine
        if plateau.la_colonne_est_pleine(c_arrivee):
            return False
        # INVALIDE Si la colonne d'arrivée n'est pas vide et n'a pas la même couleur au sommet
        if not plateau.la_colonne_est_vide(c_arrivee) and \
            plateau.la_couleur_au_sommet_de_la_colonne(c_depart) != plateau.la_couleur_au_sommet_de_la_colonne(c_arrivee):
            return False
        # INVALIDE Si la colonne d'arrivée n'a pas assez de place
        if plateau.nombre_de_cases_monocouleur_au_sommet_de_la_colonne(c_depart) > plateau.nombre_de_case_vide_de_la_colonne(c_arrivee):
            return False
        return True

    def __solution_complete(self, plateau: Plateau):
        "Evalue si le plateau est terminé (gagné ou bloqué)"
        if plateau.plateau_ligne_texte in self.__ensemble_des_plateaux_gagnants():
            return True
        # TODO : Evaluer si le plateau est "bloqué" => à observer, mais vérification inutile jusque là.
        return False

    def __enregistrer_solution(self, plateau: Plateau):
        "Enregistre le parcours de la solution pour la restituer"
        # Enregistrer la liste des choix courant comme la solution
        self._liste_des_solutions.append(copy.deepcopy(self._liste_des_choix_courants))

        if 'solution la plus longue' not in self._statistiques \
            or len(self._liste_des_choix_courants) > self._statistiques['solution la plus longue']:
            self._statistiques['solution la plus longue'] = len(self._liste_des_choix_courants)
            
        if 'solution la plus courte' not in self._statistiques \
            or len(self._liste_des_choix_courants) < self._statistiques['solution la plus courte']:
            self._statistiques['solution la plus courte'] = len(self._liste_des_choix_courants)

        if 'nombre de solution' not in self._statistiques:
            self._statistiques['nombre de solution'] = 1
        else:
            self._statistiques['nombre de solution'] += 1

        self._export_json_solutions.exporter(self)

    def backtracking(self, plateau: Plateau = None):
        "Parcours de tous les choix afin de débusquer toutes les solutions"
        if plateau is None:
            if len(self._liste_des_solutions) != 0:
                # Le plateau est déjà résolu et enregistré
                return
            plateau = self._plateau_initial
            self._liste_des_choix_courants = []
            self._profondeur_recursion = -1
        
        self._profondeur_recursion += 1
        # print(self._profondeur_recursion)
        if self._profondeur_recursion > 50:
            raise RuntimeError("Appels récursifs infinis !")
        
        if self.__solution_complete(plateau):   # Condition d'arrêt
            self.__enregistrer_solution(plateau)
            self._profondeur_recursion -= 1
            return

        for choix in self.__ensemble_des_choix_possibles():
            if self.__est_valide(plateau, choix):  # Vérifier si le choix est valide
                # Enrichir le choix du nombre de cases à déplacer (pour pouvoir rétablir)
                nb_cases_deplacees = plateau.nombre_de_cases_monocouleur_au_sommet_de_la_colonne(choix[0])
                choix += tuple([nb_cases_deplacees])
                self.__ajouter_choix(plateau, choix)  # Prendre ce choix
                self.backtracking(plateau)  # Appeler récursivement la fonction
                self.__retirer_choix(plateau, choix)  # Annuler le choix (retour en arrière)
        
        if self._profondeur_recursion == 0:
            # fin de toutes les recherches
            self.exporter_fichier_json()
        self._profondeur_recursion -= 1

    def exporter_fichier_json(self):
        """Enregistre un fichier JSON avec les solutions et les statistiques du plateau"""
        self._export_json_solutions.forcer_export(self)

    def __importer_fichier_json(self):
        """Lit l'enregistrement JSON s'il existe"""
        data_json = self._export_json_analyses.importer()
        if 'nombre de solutions' in data_json:
            self._statistiques['nombre de solution'] = data_json['nombre de solutions']
        if 'solution la plus courte' in data_json:
            self._statistiques['solution la plus courte'] = data_json['solution la plus courte']
        if 'solution la plus longue' in data_json:
            self._statistiques['solution la plus longue'] = data_json['solution la plus longue']
        if 'solution moyenne' in data_json:
            self._statistiques['solution moyenne'] = data_json['solution moyenne']
        if 'liste des solutions' in data_json:
            for solution in data_json['liste des solutions']:
                self._liste_des_solutions.append(solution)

    @property
    def nb_solutions(self):
        if 'nombre de solution' in self._statistiques:
            return self._statistiques['nombre de solution']
        return 0

    @property
    def solution_la_plus_courte(self):
        if 'solution la plus courte' in self._statistiques:
            return self._statistiques['solution la plus courte']
        return None

    @property
    def solution_la_plus_longue(self):
        if 'solution la plus longue' in self._statistiques:
            return self._statistiques['solution la plus longue']
        return None
    #TODO : Sur quelques plateaux, la solution la plus courte était différente en longueru de la plus longue.
    #       C'était sur un plateau 4x3 je crois. Voir s'il faut en tenir compte avec de grands ecarts.

    @property
    def solution_moyenne(self):
        # TODO : ResoudrePlateau().solution_moyenne => ABANDONNE, nettoyer le code de la 'moyenne' !
        if 'solution moyenne' in self._statistiques:
            return self._statistiques['solution moyenne']
        return None

    @property
    def difficulte(self):
        """Retourne la difficulté de la solution
La difficulté est le nombre de coups pour résoudre le plateau rapporté à la taille du plateau."""
        if self.solution_la_plus_courte is None:
            return None
        surface_plateau_max = 12 * 12
        surface_plateau = self._plateau_initial.nb_colonnes * self._plateau_initial.nb_lignes
        inverse_ratio_surface = surface_plateau_max / surface_plateau
        self._difficulte = int( self.solution_la_plus_courte * inverse_ratio_surface )
        return self._difficulte

class ExportJSON:
    def __init__(self, delai, longueur, nom_plateau, nom_export, repertoire = REPERTOIRE_SORTIE_RACINE):
        self._delai_enregistrement = delai
        self._longueur_enregistrement = longueur
        self._chemin_enregistrement = Path(repertoire) / nom_plateau / (nom_export+'.json')

        self._timestamp_dernier_enregistrement = datetime.datetime.now().timestamp()
        self._longueur_dernier_enregistrement = 0

    def exporter(self, contenu):
        """Enregistre un fichier JSON selon des critères de nombres et de temps.
Retourne True si l'export a été réalisé"""
        if (len(contenu) - self._longueur_dernier_enregistrement >= self._longueur_enregistrement):
            return self.forcer_export(contenu)

        if (datetime.datetime.now().timestamp() - self._timestamp_dernier_enregistrement >= self._delai_enregistrement) \
            and (len(contenu) > self._longueur_dernier_enregistrement):
            return self.forcer_export(contenu)
        
        return False

    def forcer_export(self, contenu):
        """Enregistre un fichier JSON en ignorant les critères.
Retourne True si l'export a été réalisé"""
        # Enregistrement des donnees dans un fichier JSON
        if not self._chemin_enregistrement.parent.exists():
            self._chemin_enregistrement.parent.mkdir(parents=True, exist_ok=True)
        if type(contenu) == dict:
            with open(self._chemin_enregistrement, "w", encoding='utf-8') as fichier:
                json.dump(contenu, fichier, ensure_ascii=False, indent=4)
        else:
            # Enregistrement d'une classe
            with open(self._chemin_enregistrement, "w", encoding='utf-8') as fichier:
                json.dump(contenu.to_dict(), fichier, ensure_ascii=False, indent=4)
        self._longueur_dernier_enregistrement = len(contenu)
        self._timestamp_dernier_enregistrement = datetime.datetime.now().timestamp()
        return True

    def effacer(self):
        """Effacer le contenu du fichier existant"""
        return self.forcer_export(dict())

    def importer(self):
        """Lit dans un fichier JSON les informations totales ou de la dernière itération réalisée."""
        try:
            with open(self._chemin_enregistrement, "r", encoding='utf-8') as fichier:
                dico_json = json.load(fichier)
            return dico_json
        except FileNotFoundError:
            return {}

class ProfilerLeCode:
    def __init__(self, nom, actif = False):
        self.actif = actif
        self._nom = nom

    def start(self):
        if self.actif:
            # Profilage du code
            self._profil = cProfile.Profile()
            self._profil.enable()

    def stop(self):
        if self.actif:
            # Fin du profilage
            self._profil.disable()

            # Affichage des statistiques de profilage
            self._stats = pstats.Stats(self._profil).sort_stats('cumulative')
            self._stats.print_stats()

            # Exporter les statistiques dans un fichier texte
            with open(f'profiling_results_{self._nom}.txt', 'w') as fichier:
                self._stats = pstats.Stats(self._profil, stream=fichier)
                #stats.sort_stats(pstats.SortKey.CUMULATIVE).print_stats(10)
                self._stats.sort_stats(pstats.SortKey.CUMULATIVE).print_stats()

class CreerLesTaches:
    def __init__(self, nom, nb_colonnes, nb_lignes):
        self._nom = f'{nom}_{nb_colonnes}x{nb_lignes}'
        self._taches = [{'colonnes': c, 'lignes': l, 'complexite': c*l, 'terminee': False, 'en_cours': False} for c in range(2, nb_colonnes) for l in range(2, nb_lignes)]
        self._taches.sort(key=lambda x: x['complexite'])

    def exporter(self):
        with open(f'{self._nom}.json', 'w', encoding='utf-8') as fichier:
            json.dump(self._taches, fichier, ensure_ascii=False, indent=4)

    def importer(self):
        if Path(f'{self._nom}.json').exists():
            with open(f'{self._nom}.json', 'r', encoding='utf-8') as fichier:
                self._taches = json.load(fichier)

    def __mettre_a_jour_tache(self, colonnes, lignes):
        print(f"Fin [{colonnes}x{lignes}]")
        tache_courante_traitee = False
        for tache in self._taches:
            if tache['colonnes'] == colonnes and tache['lignes'] == lignes:
                tache['terminee'] = True
                tache['en_cours'] = False
                tache_courante_traitee = True
                continue
            elif tache_courante_traitee and not tache['terminee'] and not tache['en_cours']:
                # Tâche suivant celle qui vient de s'achever => indiquer son lancement
                tache_courante_traitee = False
                print(f"Lancement [{tache['colonnes']}x{tache['lignes']}]")
                tache['en_cours'] = True
                break
        self.exporter()

    def executer_taches(self, fonction, nb_processus=None):
        if nb_processus:
            cpt_processus = nb_processus
        else:
            cpt_processus = cpu_count()

        with Pool(processes=nb_processus) as pool:
            for tache in self._taches:
                if not tache['terminee'] and not tache['en_cours']:
                    pool.apply_async(fonction, (tache['colonnes'], tache['lignes']), callback=lambda _, c=tache['colonnes'], l=tache['lignes']: self.__mettre_a_jour_tache(c, l))
                    if cpt_processus and cpt_processus > 0:
                        print(f"Lancement [{tache['colonnes']}x{tache['lignes']}]")
                        cpt_processus -= 1
                        tache['en_cours'] = True
                        self.exporter()
            pool.close()
            pool.join()

    @property
    def taches(self):
        return self._taches