"Module pour créer, résoudre et qualifier les soltuions des plateaux de 'ColorWoordSort'"
from itertools import permutations #, product, combinations#, combinations_with_replacement
import datetime
import json
import copy
from pathlib import Path

# TODO : reprendre l'enregistrement à partir du fichier. => Pas d'amélioration, essayer de comprendre.

class Plateau():
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
        """"Verifie si le plateau en parametre est valide"""
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

    def la_couleur_au_sommet_de_la_colonne(self, colonne):
        if colonne >= self.nb_colonnes:
            raise IndexError(f"Le numéro de colonne est hors du plateau ({colonne}>={self.nb_colonnes}).")
        colonne_texte = self.plateau_rectangle_texte[colonne]
        derniere_case_non_vide = colonne_texte.strip()[-1]
        return derniere_case_non_vide

    def nombre_de_case_vide_de_la_colonne(self, colonne):
        if colonne >= self.nb_colonnes:
            raise IndexError(f"Le numéro de colonne est hors du plateau ({colonne}>={self.nb_colonnes}).")
        colonne_texte = self.plateau_rectangle_texte[colonne]
        return colonne_texte.count(' ')

    def nombre_de_cases_monocouleur_au_sommet_de_la_colonne(self, colonne):
        couleur = self.la_couleur_au_sommet_de_la_colonne(colonne)
        colonne_texte = self.plateau_rectangle_texte[colonne]
        return colonne_texte.count(couleur)

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

class LotDePlateaux():
    """Classe qui gère les lots de plateaux pour parcourir l'immensité des plateaux existants.
Le chanmps nb_plateaux_max désigne la mémoire allouée pour optimiser la recherche."""
    def __init__(self, nb_plateaux_max = 1_000_000):
        self._ensemble_des_plateaux_valides = set()
        self._ensemble_des_plateaux_a_ignorer = set()
        self._dico_compteur_des_plateaux_a_ignorer = {}
        self._nb_plateaux_max = nb_plateaux_max
        self._debut_recherche_des_plateaux_valides = datetime.datetime.now().timestamp()
        self._fin_recherche_des_plateaux_valides = None
        self._export_json = None
        self._nb_colonnes = None
        self._nb_lignes = None
        self._nb_colonnes_vides = None
        self._ensemble_des_difficultes_de_plateaux = {}
        self._debut_recherche_des_solutions = None
        self._fin_recherche_des_solutions = None
        self._a_change = False
    
    def __len__(self):
        return self.nb_plateaux_valides

    def to_dict(self):
        dict_lot_de_plateaux = {}
        if self._nb_colonnes is not None:
            dict_lot_de_plateaux['colonnes']= self._nb_colonnes
            dict_lot_de_plateaux['lignes']= self._nb_lignes
            dict_lot_de_plateaux['colonnes vides']= self._nb_colonnes_vides

        dict_lot_de_plateaux['debut']= self.debut
        dict_lot_de_plateaux['fin']= self.fin
        if self.duree < 0.001:
            dict_lot_de_plateaux['duree']= f"{int(self.duree*1_000_000)} microsecondes"
        elif self.duree < 1:
            dict_lot_de_plateaux['duree']= f"{int(self.duree*1_000)} millisecondes"
        elif self.duree < 60:
            dict_lot_de_plateaux['duree']= f"{int(self.duree)} secondes"
        else:
            dict_lot_de_plateaux['duree']= f"{int(self.duree / 60)} minutes {int(self.duree % 60)} secondes"
        
        dict_lot_de_plateaux['recherche terminee'] = self._fin_recherche_des_plateaux_valides is not None

        dict_lot_de_plateaux['nombre plateaux']= len(self.plateaux_valides)
        dict_lot_de_plateaux['liste plateaux']= list(self.plateaux_valides)

        # Solutions
        dict_lot_de_plateaux['debut solutions']= self._debut_recherche_des_solutions
        dict_lot_de_plateaux['fin solutions']= self._fin_recherche_des_solutions
        if self._debut_recherche_des_solutions is not None \
            and self._debut_recherche_des_solutions is not None:
            duree_solution = self._fin_recherche_des_solutions - self._debut_recherche_des_solutions
            if duree_solution < 0.001:
                dict_lot_de_plateaux['duree solutions']= f"{int(duree_solution*1_000_000)} microsecondes"
            elif duree_solution < 1:
                dict_lot_de_plateaux['duree solutions']= f"{int(duree_solution*1_000)} millisecondes"
            elif duree_solution < 60:
                dict_lot_de_plateaux['duree solutions']= f"{int(duree_solution)} secondes"
            else:
                dict_lot_de_plateaux['duree solutions']= f"{int(duree_solution / 60)} minutes {int(duree_solution % 60)} secondes"
        # La difficulté est un entier, mais est enregistrée comme une chaine de caracteres dans le JSON. Surement car c'est une clé.
        dict_lot_de_plateaux['liste difficulte des plateaux']= self._ensemble_des_difficultes_de_plateaux
        return dict_lot_de_plateaux

    def arret_des_enregistrements(self):
        "Méthode qui finalise la recherche de plateaux"
        self._ensemble_des_plateaux_a_ignorer.clear()
        self._dico_compteur_des_plateaux_a_ignorer.clear()
        self._fin_recherche_des_plateaux_valides = datetime.datetime.now().timestamp()
        self.exporter_fichier_json()

    def est_ignore(self, plateau: Plateau):
        "Retourne 'True' si le plateau est deja connu"
        if plateau.plateau_ligne_texte not in self._ensemble_des_plateaux_valides \
            and plateau.plateau_ligne_texte not in self._ensemble_des_plateaux_a_ignorer:
            # plateau.afficher()
            # Verifier que la plateau est valide
            if plateau.est_valide:
                # Enregistrer la permutation courante qui est un nouveau plateau valide
                self.__ajouter_le_plateau(plateau)
                return False
            else:
                # Nouveau Plateau invalide, on l'ignore
                self.__ignorer_le_plateau(plateau)
                return True
        self.__compter_plateau_a_ignorer(plateau)
        return True

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
        for permutation_courante in permutations(plateau.plateau_rectangle_texte):
            plateau_a_ignorer = Plateau(self._nb_colonnes, self._nb_lignes, self._nb_colonnes_vides)
            plateau_a_ignorer.plateau_rectangle_texte = permutation_courante

            # Tester si la permutation était déjà dans les plateaux valides
            if plateau_a_ignorer.plateau_ligne_texte in self._ensemble_des_plateaux_valides:
                nouveau_plateau = False

            # Si nouveau plateau : on enregistre seulement les permutations dans 'IGNORER'
            # Sinon : on enregistre tout dans 'IGNORER'
            if not nouveau_plateau \
                or plateau_a_ignorer.plateau_ligne_texte != plateau.plateau_ligne_texte:
                self.__ignorer_le_plateau(plateau_a_ignorer)

        if nouveau_plateau:
            self._ensemble_des_plateaux_valides.add(plateau.plateau_ligne_texte)
            self._a_change = True
            # _a_change | exporter() || _a_change
            # ===================================
            #   False   |   False    ||  False
            #   False   |   True     ||  False
            #   True    |   False    ||  True
            #   False   |   True     ||  False
            self._a_change = self._a_change and not self._export_json.exporter(self)

    def __compter_plateau_a_ignorer(self, plateau_a_ignorer: Plateau):
        "Compte un plateau a ignorer"
        if plateau_a_ignorer.plateau_ligne_texte not in self._dico_compteur_des_plateaux_a_ignorer:
            self._dico_compteur_des_plateaux_a_ignorer[plateau_a_ignorer.plateau_ligne_texte] = 1
        else:
            self._dico_compteur_des_plateaux_a_ignorer[plateau_a_ignorer.plateau_ligne_texte] += 1

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

        recherche_terminee = 'recherche terminee' in data_json and data_json['recherche terminee'] is True
        # Rejouer les plateaux déjà trouvés
        if 'nombre plateaux' in data_json \
            and data_json['nombre plateaux'] > 0:
            if recherche_terminee is False:
                # Récupération des plateaux valides et des ignorés
                for plateau_valide in data_json['liste plateaux']:
                    # 'self.est_ignore()' n'est pas utilisé, car il va modifier le fichier
                    #  d'export quand des plateaux valides sont ajoutés. Dans noter cas, il
                    #  faut ajouter les plateaux depuis l'export en considérant qu'il sont fiables.
                    self._ensemble_des_plateaux_valides.add(plateau_valide)
            elif recherche_terminee is True:
                # Récupération des plateaux valides uniquement
                plateau_courant = Plateau(self._nb_colonnes, self._nb_lignes, self._nb_colonnes_vides)
                for plateau_valide in data_json['liste plateaux']:
                    self._ensemble_des_plateaux_valides.add(plateau_valide)

        # Solutions
        if "debut solutions" in data_json:
            self._debut_recherche_des_solutions = data_json["debut solutions"]
        if "fin solutions" in data_json:
            self._fin_recherche_des_solutions = data_json["fin solutions"]
        if 'liste difficulte des plateaux' in data_json:
            for difficulte, liste_plateaux in data_json['liste difficulte des plateaux'].items():
                if difficulte not in self._ensemble_des_difficultes_de_plateaux:
                    self._ensemble_des_difficultes_de_plateaux[difficulte] = []
                for plateau in liste_plateaux:
                    self._ensemble_des_difficultes_de_plateaux[difficulte].append(plateau)

    def est_deja_termine(self, nb_colonnes, nb_lignes, nb_colonnes_vides):
        self.__init_export_json(nb_colonnes, nb_lignes, nb_colonnes_vides)
        self.__importer_fichier_json()

        recherche_terminee = self._fin_recherche_des_plateaux_valides is not None
        return recherche_terminee
    
    def __init_export_json(self, nb_colonnes, nb_lignes, nb_colonnes_vides):
        self._nb_colonnes = nb_colonnes
        self._nb_lignes = nb_lignes
        self._nb_colonnes_vides = nb_colonnes_vides
        nom = f"Plateaux_{self._nb_colonnes}x{self._nb_lignes}"
        self._export_json = ExportJSON(delai=60, longueur=100, nom_plateau=nom, nom_export=nom)

    def definir_difficulte_plateau(self, plateau: Plateau, difficulte):
        "Méthode qui enregistre l'enregistrement des difficultés des plateaux"
        if self._debut_recherche_des_solutions is None:
            self._debut_recherche_des_solutions = datetime.datetime.now().timestamp()
        if str(difficulte) not in self._ensemble_des_difficultes_de_plateaux:
            self._ensemble_des_difficultes_de_plateaux[str(difficulte)] = []
        if plateau.plateau_ligne_texte not in self._ensemble_des_difficultes_de_plateaux[str(difficulte)]:
            self._ensemble_des_difficultes_de_plateaux[str(difficulte)].append(plateau.plateau_ligne_texte)
            self._a_change = True
            self._fin_recherche_des_solutions = datetime.datetime.now().timestamp()

    def arret_des_enregistrements_de_difficultes_plateaux(self):
        "Méthode qui finalise l'arret des enregistrements des difficultés de plateaux"
        cles_dico = list(self._ensemble_des_difficultes_de_plateaux.keys())
        if None in cles_dico:
            cles_dico.remove(None) # None est inclassable avec 'list().sort()'
        cles_dico_classees = copy.deepcopy(cles_dico)
        cles_dico_classees.sort()
        if cles_dico != cles_dico_classees:
            # Ordonner l'ensemble par difficulté croissante
            dico_classe = {k: self._ensemble_des_difficultes_de_plateaux.get(k) for k in cles_dico_classees}
            if None in self._ensemble_des_difficultes_de_plateaux:
                dico_classe[None] = self._ensemble_des_difficultes_de_plateaux.get(None)
            self._ensemble_des_difficultes_de_plateaux = copy.deepcopy(dico_classe)
        self.exporter_fichier_json()

    @property
    def difficulte_plateaux(self):
        "Ensemble des difficultés de plateaux résolus"
        return self._ensemble_des_difficultes_de_plateaux

    @property
    def nb_plateaux_solutionnes(self):
        "Nombre de plateaux valides"
        return sum([len(plateaux) for difficulte, plateaux in self._ensemble_des_difficultes_de_plateaux.items()])

class ResoudrePlateau():
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
        self._export_json = ExportJSON(delai=60, longueur=100, nom_plateau=nom_plateau, nom_export=nom)
        self.__importer_fichier_json()
        # TODO : Ajouter un debut/fin => Abandonné. La résolution d'un plateau est trop courte.

    def __len__(self):
        "La longueur de la solution définit la difficulté"
        # Le nombre de soltuioon n'a pas d'incidence sur la difficulté
        if self.solution_la_plus_courte:
            return self.solution_la_plus_courte
        return 0

    def to_dict(self):
        dict_resoudre_plateau = {}
        dict_resoudre_plateau['plateau'] = self._plateau_initial.plateau_ligne_texte
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
            for permutation_courante in permutations(plateau_gagnant.plateau_rectangle_texte):
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

        self._export_json.exporter(self)

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
        self._export_json.forcer_export(self)

    def __importer_fichier_json(self):
        """Lit l'enregistrement JSON s'il existe"""
        data_json = self._export_json.importer()
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

class ExportJSON():
    def __init__(self, delai, longueur, nom_plateau, nom_export):
        self._delai_enregistrement = delai
        self._longueur_enregistrement = longueur
        self._chemin_enregistrement = Path('Analyses') / nom_plateau / (nom_export+'.json')

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
        with open(self._chemin_enregistrement, "w", encoding='utf-8') as fichier:
            json.dump(contenu.to_dict(), fichier, ensure_ascii=False)
        self._longueur_dernier_enregistrement = len(contenu)
        self._timestamp_dernier_enregistrement = datetime.datetime.now().timestamp()
        return True

    def importer(self):
        """Lit dans un fichier JSON les informations totales ou de la dernière itération réalisée."""
        try:
            with open(self._chemin_enregistrement, "r", encoding='utf-8') as fichier:
                dico_json = json.load(fichier)
            return dico_json
        except FileNotFoundError:
            return {}
