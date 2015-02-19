# pyLang
A simple script to test the langage of a text file or a .srt file

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
 
   find ./ -name "*.srt" -exec pyLang.py {} \; > lang_ST.txt
   
 ou bien :
 
   find "/chemin absolu/"  -name "*.srt" -exec pyLang.py {} \; > lang_ST.txt
   
 On peut aussi rajouter | grep "ENG" pour récupérer les sous-titres en anglais :
 
   find ./ -name "*.srt" -exec pyLang.py  {} \; | grep "ENG" > lang_ST.txt
 
 Distribué sous licence WTFPL.
 
 Source des fréquences théoriques : stefantrost.de

Abunux - abunux at gmail point com 
24/02/2010
