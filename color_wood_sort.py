from itertools import permutations #, product, combinations#, combinations_with_replacement
import datetime
import json


COLONNES = range(2, 5) #11
LIGNES = [2] #4
COLONNES_VIDES_MAX = 1


class Plateau():
    def __init__(self, nb_colonnes, nb_lignes, nb_colonnes_vides=1):
        self._nb_colonnes = nb_colonnes
        self._nb_lignes = nb_lignes
        self._nb_colonnes_vides = nb_colonnes_vides
        self._est_valide = None
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
    
    def __str__(self):
        if not self._str_format:
            for ligne in self.plateau_rectangle:
                self._str_format += f"{ligne}\n"
        return self._str_format

    @property
    def plateau_ligne(self):
        return self._plateau_ligne

    @plateau_ligne.setter
    def plateau_ligne(self, plateau_ligne):
        # Pas de verification sur la validite,
        # pour pouvoir traiter les plateaux invalides
        # a ignorer.
        self._plateau_ligne = tuple(plateau_ligne)

    @property
    def plateau_ligne_texte(self):
        if not self._plateau_ligne_texte:
            self.__creer_plateau_ligne_texte()
        return self._plateau_ligne_texte

    @property
    def plateau_rectangle(self):
        if not self._plateau_rectangle:
            self.__creer_plateau_rectangle()
        return self._plateau_rectangle

    @property
    def plateau_rectangle_texte(self):
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
        return self.plateau_ligne

    def afficher(self):
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
                self._plateau_rectangle.append(self._plateau_ligne[colonne*self._nb_lignes : (colonne + 1)*self._nb_lignes])

    def __creer_plateau_rectangle_texte(self):
        """"['A', 'A', 'B', 'B', ' ', ' '] => ['AA', 'BB', '  ']"""
        if self._plateau_ligne:
            self._plateau_rectangle_texte = []
            for colonne in range(self._nb_colonnes):
                self._plateau_rectangle_texte.append(''.join(self._plateau_ligne[colonne*self._nb_lignes : (colonne + 1)*self._nb_lignes]))

    @property
    def nb_familles(self):
        return self._nb_familles

    def creer_les_familles(self):
        if not self._liste_familles:
            self._liste_familles = [chr(ord('A')+F) for F in range(self._nb_familles) ]
        return self._liste_familles

    def creer_plateau_initial(self):
        """"Cree un plateau en ligne initial = ['A', 'A', 'B', 'B', ' ', ' ']"""
        if not self._plateau_ligne:
            liste_familles = self.creer_les_familles()
            self.plateau_ligne = tuple(
                [self._liste_familles[famille] for famille in range(self._nb_familles) for membre in range(self._nb_lignes)]
                +[' ' for vide in range(self._nb_colonnes_vides) for membre in range(self._nb_lignes)] )

    @property
    def est_valide(self):
        """"Verifie si le plateau en parametre est valide"""
        if self._plateau_ligne and self._est_valide is None:
            # Pour chaque colonne, les cases vides sont sur les dernieres cases
            case_vide = ' '
            for colonne in range(self._nb_colonnes):
                case_vide_presente = False
                for ligne in range(self._nb_lignes):
                    if not case_vide_presente:
                        # Chercher la premiere case vide de la colonne
                        if self.plateau_ligne[colonne * self._nb_lignes + ligne] == case_vide:
                            case_vide_presente = True
                    else:
                        # Toutes les autres case de la lignes doivent etre vides
                        if self.plateau_ligne[colonne * self._nb_lignes + ligne] != case_vide:
                            self._est_valide = False
                            return self._est_valide
            self._est_valide = True
        return self._est_valide

    def a_gagne(self):
        """"Verifie si le plateau actuel est gagnant"""
        return False

class LotDePlateau():
    def __init__(self):
        self.ensemble_des_plateaux_valides = set()
        self.ensemble_des_plateaux_a_ignorer = set()
        self.dico_compteur_des_plateaux_a_ignorer = dict()
        self.nb_plateaux_max = 1_000_000

    def arret_des_enregistrements(self):
        self.ensemble_des_plateaux_a_ignorer.clear()
        self.dico_compteur_des_plateaux_a_ignorer.clear()

    def est_connu(self, plateau: Plateau):
        "Retourne 'True' si le plateau est deja connu"
        if plateau.plateau_ligne_texte not in self.ensemble_des_plateaux_valides and plateau.plateau_ligne_texte not in self.ensemble_des_plateaux_a_ignorer:
            # plateau.afficher()
            # Verifier que la plateau est valide
            if plateau.est_valide:
                # Enregistrer la permutation courante qui est un plateau valide
                self.__ajouter_le_plateau(plateau)
            else:
                # Plateau invalide, on l'ignore
                self.__ignorer_le_plateau(plateau)
            return False
        else:
            self.__compter_plateau_a_ignorer(plateau)
            return True

    @property
    def plateaux_valides(self):
        return self.ensemble_des_plateaux_valides

    @property
    def nb_plateaux_valides(self):
        return len(self.ensemble_des_plateaux_valides)

    @property
    def nb_plateaux_ignores(self):
        return len(self.ensemble_des_plateaux_a_ignorer)

    def __ajouter_le_plateau(self, plateau: Plateau):
        "Memorise un plateau deja traite"
        self.ensemble_des_plateaux_valides.add(plateau.plateau_ligne_texte)
        self.__ignorer_les_permutations(plateau)

    def __ignorer_les_permutations(self, plateau: Plateau):
        "Ajoute toutes les permutations d'un plateau dans l'ensemble a ignorer"
        for permutation_courante in permutations(plateau.plateau_rectangle_texte):
            plateau_a_ignorer = Plateau(colonnes, lignes, COLONNES_VIDES_MAX)
            plateau_a_ignorer.plateau_rectangle_texte = permutation_courante
            if plateau_a_ignorer.plateau_ligne_texte != plateau.plateau_ligne_texte:
                self.__ignorer_le_plateau(plateau_a_ignorer)

    def __compter_plateau_a_ignorer(self, plateau_a_ignorer: Plateau):
        "Compte un plateau a ignorer"
        if plateau_a_ignorer.plateau_ligne_texte not in self.dico_compteur_des_plateaux_a_ignorer:
            self.dico_compteur_des_plateaux_a_ignorer[plateau_a_ignorer.plateau_ligne_texte] = 1
        else:
            self.dico_compteur_des_plateaux_a_ignorer[plateau_a_ignorer.plateau_ligne_texte] += 1

    def __ignorer_le_plateau(self, plateau_a_ignorer: Plateau):
        "Ignore un plateau et met a jour les ensembles et compteurs"
        # Ignorer le plateau
        self.ensemble_des_plateaux_a_ignorer.add(plateau_a_ignorer.plateau_ligne_texte)
        # Compter l'occurence
        self.__compter_plateau_a_ignorer(plateau_a_ignorer)
        # Optimiser la memoire
        self.__reduire_memoire()

    def __reduire_memoire(self):
        "Optimisation memoire quand la memoire maximum est atteinte"
        # Trier par valeur croissantes
        if len(self.ensemble_des_plateaux_a_ignorer) > self.nb_plateaux_max:
            dico_trie_par_valeur_croissantes = dict(sorted(self.dico_compteur_des_plateaux_a_ignorer.items(), key=lambda item: item[1]))

            # Vider les memoires et compteurs
            self.dico_compteur_des_plateaux_a_ignorer.clear()
            self.ensemble_des_plateaux_a_ignorer.clear()

            for i in range(int(self.nb_plateaux_max/10)):
                if len(dico_trie_par_valeur_croissantes) == 0:
                    break
                # Reconduire les 10% les plus sollicites
                key, value = dico_trie_par_valeur_croissantes.popitem()
                self.ensemble_des_plateaux_a_ignorer.add(key)
                self.dico_compteur_des_plateaux_a_ignorer[key] = 1
            dico_trie_par_valeur_croissantes.clear()

    def fixer_taille_memoire_max(self, nb_plateaux_max):
        "Fixe le nombre maximum de plateau a memoriser"
        self.__reduire_memoire()

def afficher_heure():
    "Fonction pour obtenir et afficher l'heure actuelle"
    # Obtention de l'heure actuelle
    heure_actuelle = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print("L'heure actuelle est :", heure_actuelle)

def lire_heure():
    return datetime.datetime.now().timestamp()

def enregistrer_la_liste_de_plateaux_ligne(plateaux_ligne_texte, nb_colonnes, nb_lignes, debut=None, fin=None):
    """"plateaux_ligne = [['A', 'A', 'B', 'B', ' ', ' ', 'B', 'A', 'B', 'A', ' ', ' ']]
     enregistrement plateaux_lignes_string = ['AABB  ', 'BABA  ']"""
    infos_plateau = {}
    infos_plateau['COLONNES']= nb_colonnes
    infos_plateau['LIGNES']= nb_lignes
    if debut:
        infos_plateau['debut']= debut
    if fin:
        infos_plateau['fin']= fin
    if debut and fin:
        infos_plateau['duree']= int(fin - debut)
    infos_plateau['nombre_plateaux']= len(plateaux_ligne_texte)
    infos_plateau['liste_plateaux']= list(plateaux_ligne_texte)

    # Enregistrement des donnees dans un fichier JSON
    with open(f"Plateaux_{nb_colonnes}x{nb_lignes}.json", "w", encoding='utf-8') as fichier:
        #json.dump(infos_plateau, fichier, ensure_ascii=False, indent=4)
        json.dump(infos_plateau, fichier, ensure_ascii=False)



for lignes in LIGNES:
    for colonnes in COLONNES:
        print(f"*** Generatrice {colonnes}x{lignes}: DEBUT")
        debut = lire_heure()
        afficher_heure()
        plateau = Plateau(colonnes, lignes, COLONNES_VIDES_MAX)
        plateau.creer_plateau_initial()
        plateau.afficher()
        lot_de_plateaux = LotDePlateau()
        ensemble_des_plateaux_a_ignorer = set()
        for permutation_courante in permutations(plateau.pour_permutations):
            # Verifier que ce plateau est nouveau
            plateau_courant = Plateau(colonnes, lignes, COLONNES_VIDES_MAX)
            plateau_courant.plateau_ligne = permutation_courante
            if not lot_de_plateaux.est_connu(plateau_courant):
                if lot_de_plateaux.nb_plateaux_valides % 400 == 0:
                    print(f"nb_plateaux_valides={lot_de_plateaux.nb_plateaux_valides}")

        print(f"nb_plateaux_valides={lot_de_plateaux.nb_plateaux_valides}")
        print(f"nb_plateaux_ignores={lot_de_plateaux.nb_plateaux_ignores}")
        lot_de_plateaux.arret_des_enregistrements()
        fin = lire_heure()
        enregistrer_la_liste_de_plateaux_ligne(lot_de_plateaux.plateaux_valides, colonnes, lignes, debut, fin)
        if (fin - debut) < 10:
            print(f"*** Generatrice {colonnes}x{lignes}: FIN en {int((fin - debut)*1000)} millisecondes")
        else:
            print(f"*** Generatrice {colonnes}x{lignes}: FIN en {int(fin - debut)} secondes")
