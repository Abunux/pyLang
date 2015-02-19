#!/usr/bin/python
# -*- coding:Utf-8 -*-

version="1.15"

about="""
        **************
        * lang v"""+version+""" *
        **************

 Script pour déterminer la langue d'un fichier texte.
 Pratique pour faire le ménage dans ses sous-titres.
 Peut servir aussi pour des sites web,...
 Traite l'anglais, le français, l'allemand et l'espagnol,
 l'italien et le portugais.
 C'est très facile d'ajouter d'autres langues.

 Se base sur la fréquence d'apparition théorique de chaque lettre
 dans les différente langues. 

 Astuce pour parcourir les sous-titres d'une arborescence :
 Se mettre à la racine puis :
   find ./ -name "*.srt" -exec lang {} \; > lang_ST.txt
 ou bien :
   find "/chemin absolu/"  -name "*.srt" -exec lang {} \; > lang_ST.txt
 On peut aussi rajouter | grep "ENG" pour récupérer les sous-titres en anglais :
   find ./ -name "*.srt" -exec lang  {} \; | grep "ENG" > lang_ST.txt
 
 Distribué sous licence WTFPL

 Source des fréquences théoriques : stefantrost.de

        Abunux - abunux at gmail point com - 24/02/2010 - 03/03/2010
 """

todo="""
            -----------
             A faire :
            -----------
        
    - Fonctionnalités :
    
- Ajouter d'autres langues (facile) : NL, DAN, NOR, SWE, FIN, POL, TUR
- Voir les langues non latines (Russe, Grec, langues asiatiques,...)

- Interprétation des indicateurs et mise en place de bon / pas bon
-> des tests, des tests et encore des tests sur plein de fichiers
avec plein de langues différentes

- Script bash pour parcourir un dossier et sortir les résultats dans un
fichier ou un graphique gnuplot
- Intégrer ça à nautilus (clic droit sur un sous-titre donne la langue
dans le menu contextuel). Ce serait génial ça...

    - Améliorations :
    
- Accents dans l'aide -h (optparse)
- Déterminer si un fichier est un fichier texte sans utiliser l'extension
- Fonction de renommage un peu lourde

"""


#-------------------------------------------------------------------------------
# Récupération des paramètres en ligne de commande
#-------------------------------------------------------------------------------

import sys
from optparse import OptionParser, OptionGroup

# A ajouter : NL, DAN, NOR, SWE, FIN, POL, TUR
LANG_dispo=['ENG','FR','GER','ESP','ITA','POR']

usage="%prog [OPTIONS] FICHIER"
version="%prog v"+version

parser=OptionParser(usage=usage, version=version)

# Options de sortie
groupe_sorties1=OptionGroup(parser,"Options de sortie ")
groupe_sorties1.add_option("-n","--nom",action="store_true",dest="nom",
    default=True,help="(Par defaut) Donne une sortie 'Fichier : LANG'")
groupe_sorties1.add_option("-m","--mini",action="store_true",dest="mini",
    default=False,help="Donne juste la langue(ENG,FR,...)")
groupe_sorties1.add_option("-r","--rename",action="store_true",dest="rename",
    default=False,help="Renomme le fichier en rajoutant la langue")
groupe_sorties1.add_option("-i","--interact",action="store_true",dest="interact",
    default=False,help="Demande confirmation avant de renommer")

groupe_sorties2=OptionGroup(parser,"Options de sortie d'analyse ",\
    "A terme, inutiles pour le commun des mortels")
groupe_sorties2.add_option("-c","--complet",action="store_true",dest="complet",
    default=False,help="Sortie complete (resume de toutes les valeurs)")
groupe_sorties2.add_option("-t","--table",action="store_true",dest="table",
    default=False,help="Sortie adaptee pour etudier dans un tableur : \
Resultats separes par des virgules")
groupe_sorties2.add_option("-g","--gnuplot",action="store_true",dest="gnuplot",
    default=False,help="Sortie adaptee pour tracer dans gnuplot : Resultats \
separes par des espaces. Pas de nom de fichier")

# Options de langues
groupe_lang=OptionGroup(parser,"Options de langue ")
groupe_lang.add_option("-A","--ALL",action="store_true",dest="all",
    default=False,help="Teste toutes les langues disponibles : "
                  +str(LANG_dispo)+ " (ENG et FR uniquement par defaut)")

parser.add_option_group(groupe_sorties1)
parser.add_option_group(groupe_lang)
parser.add_option_group(groupe_sorties2)

#Divers
parser.add_option("-a","--about",action="store_true",dest="about",
    default=False,help="A propos")
parser.add_option("-d","--todo",action="store_true",dest="todo",
    default=False,help="A faire")
parser.add_option("-s","--source",action="store_true",dest="source",
    default=False,help="Afficher le code source du script")

global opts
(opts,args)=parser.parse_args()

# Options diverses
if opts.source:
    source_file=open(sys.argv[0],"r")    
    print source_file.read()
    sys.exit(0)
elif opts.about:
    print about
    sys.exit(0)
elif opts.todo:
    print todo
    sys.exit(0)

# Génération de la liste de langues à tester
global LANG; LANG=[]
if opts.all:
    LANG=LANG_dispo
else:
    # Par défaut juste anglais et français pour être plus rapide
    LANG=['ENG','FR']

# Génération du nom du fichier à tester
global nom_fichier
nom_fichier="".join(args)
if nom_fichier=="":
    sys.stderr.write("Erreur : Aucun fichier passé en paramètre. \n")
    parser.print_help()
    sys.exit(2)

#-------------------------------------------------------------------------------
# Test et ouverture du fichier passé en paramètre
#-------------------------------------------------------------------------------

import os.path
global prog; prog=os.path.basename(sys.argv[0])

# Test que le fichier existe
if not os.path.isfile(nom_fichier):
    sys.stderr.write("Erreur : %s n'existe pas.\n" % nom_fichier)
    sys.exit(2)
    
# Test que le fichier est un fichier texte
ext=os.path.splitext(nom_fichier)[1]
connu=(".srt",".txt",".htm",".html")
if ext not in connu :
    sys.stderr.write("Erreur : %s n'est pas reconnu. \
Extensions possibles : %s\n" % (nom_fichier,connu))
    sys.exit(2)

# Ouverture du fichier
try:
    fichier=open(nom_fichier,"r")
except:
    sys.stderr.write("Erreur : Erreur d'ouverture de %s.\n" % nom_fichier)
    sys.exit(2)

# Plus qu'à récupérer le contenu et fermer
texte_brut=fichier.read()
fichier.close()

#-------------------------------------------------------------------------------
# Prétraitement du texte
#-------------------------------------------------------------------------------

def suppr_tag(texte,delimitateurs=[('<script','</script>'),('{','}'),('<','>')]):
    # Supprime les parties de texte comprises entre les delimitateurs (compris)
    # Ca peut être n'importe quelle chaine de caractères
    # Exemple ici avec les balises html <script...>...</script>      
    # Mettre ('<','>') en dernier au cas où il y ait des "inférieur","supérieur"
    # On peut adapter suivant l'utilisation (par ex LaTeX ou autre)        
    for (debut,fin) in delimitateurs:        
        i0=len(texte)        
        while i0!=-1 :        
            i0=texte.rfind(debut,0,i0)    
            i1=texte.find(fin,i0)       
            if i1!=-1:
                texte=texte[:i0]+texte[i1+len(fin):]
            else:
                i0=max(-1,i0-1)        
    return texte

def suppr_HTML(texte):
    # Remplace les caractères spéciaux du HTML
    remplacement_HTML={'&nbsp;':' '} # A compléter...    
    for lettre in remplacement_HTML:
        texte=texte.replace(lettre,remplacement_HTML[lettre])
    return texte

def suppr_speciaux(texte):
    # Supprime les caractères spéciaux (ponctuation, chiffres, symboles,...)
    texte=texte.translate(None,\
                '@§^&|$€¤£µ².;,`\'\"?!¿¡#:%*+-_/><~0123456789=()[]{}\\')
                #' \n@§^&|$€¤£µ².;,`\'\"?!¿¡#:%*+-_/><~0123456789=()[]{}\\')
    return texte

def nettoyage(texte):
    # Nettoyage du texte avant traitement
    texte=suppr_tag(texte)    
    texte=suppr_HTML(texte)
    texte=suppr_speciaux(texte)
    return texte

def substitution(texte):
    texte=texte.lower()
    # Mettre toutes les lettres spéciales en minuscule    
    remplacement=\
    {'À':'à','Á':'á','Â':'â','Ä':'ä','Ã':'ã','Å':'å',
     'È':'è','É':'é','Ê':'ê','Ë':'ë',
     'Ì':'ì','Í':'í','Î':'î','Ï':'ï',
     'Ò':'ò','Ó':'ó','Ô':'ô','Ö':'ö','Õ':'õ','Ø':'ø',
     'Ù':'ù','Ú':'ú','Û':'û','Ü':'ü',
     'Ç':'ç','Œ':'œ','Æ':'æ','Ñ':'ñ'}    
    for lettre in remplacement:
        texte=texte.replace(lettre,remplacement[lettre])
    return texte

#-----------------------------------------------------------------------------
# Gestion des langues
#-----------------------------------------------------------------------------

# Fréquences théoriques d'apparition des caractères
# Source :
#   http://www.sttmedia.com/characterfrequencies
#   (stefantrost.de)
#
# Idée :
#   On stocke les fréquences théoriques pour chaque langue dans un dictionnaire
# de dictionnaires ayant pour clefs chaque lettre de l'alphabet :
# freq_theo['LANG']
#   On crée les alphabets de chaque langue sous forme d'un dictionnaire
# d'ensembles : alpha['LANG']
# alpha['total'] regroupe toutes les lettres de toutes les langues étudiées

   
# Fréquences théoriques d'apparition de chaques lettres
# -----------------------------------------------------

global freq_theo; freq_theo={}

##freq_theo['LAN']={'a':,'b':,'c':,'d':,'e':,'f':,
##                  'g':,'h':,'i':,'j':,'k':,'l':,
##                  'm':,'n':,'o':,'p':,'q':,'r':,
##                  's':,'t':,'u':,'v':,'w':,'x':,
##                  'y':,'z':,'à':,'á':,'â':,'ä':,
##                  'ã':,'å':,'è':,'é':,'ê':,'ë':,
##                  'ì',:'í':,'î':,'ï':,'ò':,'ó':,
##                  'ô':,'ö':,'õ':,'ø':,'ù':,'ú':,
##                  'û':,'ü':,'ç':,'œ':,'æ':,'ñ':}

freq_theo['ENG']={'a':8.34,'b':1.54,'c':2.73,'d':4.14,'e':12.60,'f':2.03,
                  'g':1.92,'h':6.11,'i':6.71,'j':0.23,'k':0.87,'l':4.24,
                  'm':2.53,'n':6.80,'o':7.70,'p':1.66,'q':0.09,'r':5.68,
                  's':6.11,'t':9.37,'u':2.85,'v':1.06,'w':2.34,'x':0.20,
                  'y':2.04,'z':0.06}

freq_theo['FR']={'a':8.13,'b':0.93,'c':3.15,'d':3.55,'e':15.1,'f':0.96,
                 'g':0.97,'h':1.08,'i':6.94,'j':0.71,'k':0.16,'l':5.68,
                 'm':3.23,'n':6.42,'o':5.27,'p':3.03,'q':0.89,'r':6.43,
                 's':7.91,'t':7.11,'u':6.05,'v':1.83,'w':0.04,'x':0.42,
                 'y':0.19,'z':0.21,'œ':0.01,'à':0.54,'â':0.03,'ç':0,
                 'è':0.35,'é':2.13,'ê':0.24,'ë':0.01,'î':0.03,'ï':0,
                 'ô':0.07,'ù':0.02,'û':0.05,'ü':0.02}

freq_theo['GER']={'a':5.58,'b':1.96,'c':3.16,'d':4.98,'e':16.93,'f':1.49,
                  'g':3.02,'h':4.98,'i':8.02,'j':0.24,'k':1.32,'l':3.60,
                  'm':2.55,'n':10.53,'o':2.24,'p':0.67,'q':0.02,'r':6.89,
                  's':6.42,'t':5.79,'u':3.83,'v':0.84,'w':1.78,'x':0.05,
                  'y':0.05,'z':1.21,'ä':0.54,'ö':0.30,'ü':0.65,'ß':0.37}

freq_theo['ESP']={'a':11.72,'b':1.49,'c':3.87,'d':4.67,'e':13.72,'f':0.69,
                  'g':1.00,'h':1.18,'i':5.25,'j':0.52,'k':0.11,'l':5.24,
                  'm':3.08,'n':6.83,'o':8.44,'p':2.89,'q':1.11,'r':6.41,
                  's':7.20,'t':4.60,'u':4.55,'v':1.05,'w':0.04,'x':0.14,
                  'y':1.09,'z':0.47,'á':0.44,'é':0.36,'í':0.70,'ñ':0.17,
                  'ó':0.76,'ú':0.12,'ü':0.02}

freq_theo['ITA']={'a':10.85,'b':1.05,'c':4.30,'d':3.39,'e':11.49,'f':1.01,
                  'g':1.65,'h':1.43,'i':10.18,'j':0,'k':0,'l':5.70,
                  'm':2.87,'n':7.02,'o':9.97,'p':2.96,'q':0.45,'r':6.19,
                  's':5.48,'t':6.97,'u':3.16,'v':1.75,'w':0,'x':0,
                  'y':0,'z':0.85,'à':0.15,'è':0.42,'é':0.06,'ì':0.09,
                  'ò':0.11,'ù':0.12}

freq_theo['POR']={'a':12.21,'b':1.01,'c':3.35,'d':4.21,'e':13.19,'f':1.07,
                  'g':1.08,'h':1.22,'i':5.49,'j':0.30,'k':0.13,'l':3.00,
                  'm':5.07,'n':5.02,'o':10.22,'p':3.01,'q':1.10,'r':6.73,
                  's':7.35,'t':5.07,'u':4.46,'v':1.72,'w':0.05,'x':0.28,
                  'y':0.04,'z':0.45,'à':0.04,'á':0.41,'ã':0.83,'ç':0.40,
                  'é':0.52,'ê':0.36,'ì':0.18,'ò':0.17,'ô':0.01,'õ':0.04,
                  'ú':0.11}


# On crée l'alphabet total avec les lettres de chaques langues
# alpha['ENG']=set(['a',....]), alpha['FR']=set(['a',..,'é',...]) ....
# alpha['total']=Alphabet total regroupant toutes les lettres
# J'utilise des ensembles pour le fun
global alpha;alpha={};
alpha['total']=set([])
for L in LANG:
    alpha[L]=set(freq_theo[L].keys())
    alpha['total']=alpha['total'].union(alpha[L])

# On complète par 0 les fréquences des lettres qui n'appartiennent
# pas à l'alphabet de la langue
# A voir : Mettre un poids négatif sur ces lettre ?
for L in LANG:
    for l in alpha['total']:
        if l not in alpha[L]:
            freq_theo[L][l]=0


#-----------------------------------------------------------------------------
# Calcul du résultat et d'indicateurs
#-----------------------------------------------------------------------------

from math import sqrt

# Traitement du texte contenu dans le fichier
# -------------------------------------------
texte_clean=nettoyage(texte_brut)
texte=substitution(texte_clean)
if texte=='':
    sys.stderr.write("Erreur : Fichier %s vide.\n" % nom_fichier)
    sys.exit(2)


# Calcul de la distance du texte avec les langues connues
# -------------------------------------------------------
# C'est la distance euclidienne dans R^(nbre de lettres dans l'alphabet total)
# d=sqrt(Somme_lettres((fréq réelle-freq théorique)²))

def compte(texte,alphabet=alpha['total']):
    # Fréquences des lettres de texte
    # Résultat dans un dictionnaire :
    # freq{'a'},...
    # total=Nombre total de lettres comptées
    nb_lettres={}
    total=0
    freq={}
    for l in alphabet:
        nb_lettres[l]=0 
    i=0
    while i<len(texte):
        # Si la lettre de rang i est dans 'abc...yz'
        if texte[i] in alphabet:        
            nb_lettres[texte[i]]+=1
            i+=1
            total+=1            
        # Les caractères spéciaux comptent pour 2 caractères
        # Zarbi... mais ça marche
        elif i+1<len(texte) and texte[i]+texte[i+1] in alphabet :
            nb_lettres[texte[i]+texte[i+1]]+=1
            i+=2
            total+=1            
        else:
            i+=1        
    if total==0 :
        sys.stderr.write("Erreur : Aucun caractère alphabétique.\n")
        sys.exit(2)        
    for l in alphabet:
        freq[l]=float(nb_lettres[l])*100/total
    return freq,total

def dist(dict1,dict2,alphabet=alpha['total']):
    # Calcul la distance euclidienne entre 2 vecteurs (dictionnaires)
    d=0
    for l in alphabet:
        d+=(dict1[l]-dict2[l])**2
    return sqrt(d)

def calcul_distances(X):
    # Retourne un vecteur R=[d(X,ENG),d(X,FR),...]
    R=[]
    for L in LANG:
        R.append(0)        
    for L in LANG:
            R[LANG.index(L)]=dist(freq_theo[L],X)
    return R

freq,total=compte(texte)
R=calcul_distances(freq)
m=min(R)
langue=LANG[R.index(m)]    


# Calcul des indicateurs de qualité
# ---------------------------------

def somme(a):
    # Calcule la somme des éléments de la liste a
    s=0
    for i in range(len(a)):
        s+=a[i]
    return s

def dist2(a,b):
    # Calcul la distance euclidienne entre 2 vecteurs (listes)
    d=0
    for i in range(len(a)):
	    d+=(a[i]-b[i])**2
    return sqrt(d)

R0=calcul_distances(freq_theo[langue])
C=1-(len(R)*m)/somme(R)
D=dist2(R,R0)
M=(1-C)*D*m

# Stockage des résultats dans un dictionnaire
global result; result={}
result['langue']=langue
result['m']=m
result['total']=total
result['R']=R
result['R0']=R0
result['C']=C
result['D']=D
result['M']=M



#   ------  A voir  ------
# Dit si le résultat est bon en fonction des indicateurs
def est_bon(res):
    #if res['C']>0.5:
    if True:
        return True
    else:
        return False

def pas_bon(res):
    #if res['C']<0.3:
    if False:
        return True
    else:
        return False

##if pas_bon(result):
##    result['langue']='N/A'

#-------------------------------------------------------------------------------
# Sortie des résultats
#-------------------------------------------------------------------------------

# Fonction pour renommer le fichier
def renomme(old_name,new_name):    
    if opts.interact:
        try:
            fichier=open(old_name,"r")
        except:
            sys.stderr.write("Erreur : Erreur d'ouverture de %s.\n"\
                             % old_name)
            sys.exit(2)
        rep=raw_input("Voulez-vous lire les 10 premières lignes [o/N] ? ")
        while rep not in ('N','n',''):
            for i in range(10):
                print unicode(fichier.readline(),'iso-8859-15')
            rep=raw_input("Voulez-vous lire 10 autres lignes [o/N] ? ")
        fichier.close()
        rep=raw_input("Voulez-vous renommer le fichier %s en %s [O/n] ? "\
                      % (old_name,new_name))     
    else:
        rep='o'
    if rep in ('O','o',''):
        try :
            os.rename(old_name,new_name)
            print "%s renommé en %s avec succès." % (old_name,new_name)            
        except:
            sys.stderr.write("Erreur : Echec pour renommer %s en %s.\n" %\
                (nom_fichier,new_nom))
            sys.exit(2)                      
    sys.exit(0)
    return

def recup_indication(nom):
    # On récupère les différentes parties du nom du fichier
    # A la recherche d'un indication de langue
                                            # Ex : Si nom='aaa.fr.srt' :
    corps=os.path.splitext(nom)[0]          #   corps='aaa.fr'
    ext=os.path.splitext(nom)[1]            #   ext='.srt'
    fin=os.path.splitext(corps)[1]          #   fin='.fr'
    indication=fin.lstrip('.')              #   indication='fr'
    
    # Compatibilité avec les sous-titres standards
    indic_remplace={'en':'ENG','fr':'FR','de':'GER','es':'ESP','it':'ITA',
               'pt':'POR','br':'POR'}
    if indication in indic_remplace.keys():
        indication=indic_remplace[indication]
    else:
        indication=indication.upper()  
    return indication

# Renommage du fichier
# --------------------
# (Un peu lourdingue. A retravailler)

if opts.rename:    
    # On vérifie qu'il n'y a pas la bonne langue déjà indiquée
    indication=recup_indication(nom_fichier)
    
    if langue=='N/A': # A implanter (voir au-dessus)
        print "Désolé, je ne connais pas cette langue."
        sys.stderr.write("%s : Langue inconnu" % nom_fichier)
        sys.exit(0)

    # Si il y a déjà une indication de langue
    # (d'autres à rajouter ?)
    if indication.upper() in \
            LANG+['VO','ANG','EN','DE','ESP','ES','FRA','VOSTF',
                  'VOSTFR','VOSTE','IT','PT']:
        # Pas bonne langue. C'est rare donc on prend des précautions.
        if indication != result['langue']:
            print "%s contient une indication de langue qui semble \
être fausse : %s au lieu de %s" % (nom_fichier,indication,langue)
            if est_bon(result):
                print "Je suis assez sûr de moi : %.2f" % result['C']
            elif pas_bon(result):
                print "Je suis sûr de me tromper : %.2f" % result['C']
                print "%s ne peut pas être en %s." %\
                      (nom_fichier,result['langue'])
                sys.exit(0)
            else:
                print "Il est possible que j'ai raison : %.2f" % result['C']
                opts.interact=True # Dans ce cas on demande confirmation
            new_nom=os.path.splitext(os.path.splitext(nom_fichier)[0])[0]+\
                     "."+langue+os.path.splitext(nom_fichier)[1]            
            renomme(nom_fichier,new_nom)            
        # Bonne langue
        else:
            print "%s est correctement nommé, rien à faire." % nom_fichier
            sys.exit(0)
            
    # Pas d'indication de langue
    else:
        if est_bon(result):
            print "Je suis assez sûr de moi : %s est en %s (%.2f)"\
                      % (nom_fichier,result['langue'],result['C'])
        else:
            print "Il semble que %s est en %s mais je ne suis pas sûr (%.2f)"\
                      % (nom_fichier,result['langue'],result['C'])
            opts.interact=True # Dans ce cas on demande confirmation        
        new_nom=os.path.splitext(nom_fichier)[0]+\
                 "."+langue+os.path.splitext(nom_fichier)[1] 
        renomme(nom_fichier,new_nom)
        sys.exit(0)
    sys.exit(0)


# Gestion des sorties texte
# -------------------------

# Sortie minimale
# ---------------
if opts.mini:
    print result['langue']
    sys.exit(0)
    
# Sortie complète
# ---------------
if opts.complet:    
    sortie=""
    sortie+="    - Nom_fichier : %s \n" % nom_fichier
##    for L in LANG:
##        sortie+="    - d(X,%3s)    : %5.2f (%5.2f)\n" \
##                 % (L,result['R'][LANG.index(L)],result['R0'][LANG.index(L)])        
    sortie+="    - Langue      : %s \n" % result['langue']
    sortie+="\n"
    
    sortie+="                  %s \n" \
             % "  ".join(['%5s' % L for L in LANG])
    sortie+="    - R           :%s \n" \
             % ", ".join(['%5.2f' % x for x in result['R']])
    sortie+="    - R0          :%s \n" \
             % ", ".join(['%5.2f' % x for x in result['R0']])
    
    sortie+="    - Longueur    : %d \n" % result['total']
    sortie+="    - m=min d(X,L): %.3f \n" % result['m']
    sortie+="    - C (0<=C<=1) : %.2f (Doit être proche de 1)\n" \
             % result['C']
    sortie+="    - D=d(R,R0)   : %.2f (Doit être petit) \n" \
             %result['D']
    sortie+="    - M=(1-C)*D*m : %.2f (Doit être petit) \n" \
             % result['M']
    print sortie    
    sys.exit(0)

# Sorties debug
# -------------
# Sortie personnalisée pour étudier les résultats
# Marche nikel avec calc (copier-coller, valeurs séparées par des virgules)
# ou avec gnuplot (valeurs séparées par des espaces), puis dans gnuplot :
#   > plot fichier.txt u a:b  (où a et b sont les colonnes à représenter)
# Rappel :
#   find ./ -name "*.srt" -exec lang -Ad {} \; > fichier.txt
if opts.table or opts.gnuplot:
    indication=recup_indication(nom_fichier)
    if result['langue']==indication:
        bon=1
        OK='BON'
    else:
        bon=0
        OK='PAS_BON'

    sortie=''
        
    if opts.table:
        # Sortie adaptée à Calc
        # ---------------------
        sortie+="%s," % nom_fichier
        sortie+="%s,%s,%d,%s," % (indication,result['langue'],bon,OK)
        for L in LANG:        
             sortie+="%.2f," % R[LANG.index(L)]
        sortie+=",%.3f,%.3f,%.3f,%.3f,%.3f,%d"\
                 % (result['m'],result['C'],1-result['C'],result['D'],
                    result['M'],result['total'])        
        
    elif opts.gnuplot:
        # Sortie adaptée à Gnuplot
        # ------------------------
        sortie+="%s %s %d %s " % (indication,result['langue'],bon,OK)
        for L in LANG:        
             sortie+="%.2f " % R[LANG.index(L)]
        sortie+="%.3f %.3f %.3f %.3f %.3f %d"\
                 % (result['m'],result['C'],1-result['C'],result['D'],
                    result['M'],result['total']) 
    
    print sortie
    sys.exit(0)


# Sortie par défaut (nom)
# -----------------------
if opts.nom:
    print "%s : %s" % (nom_fichier,result['langue'])
    sys.exit(0)
    
sys.exit(0)
