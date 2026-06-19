# Démonstrateur d'algorithme génétique

Ce projet a été réalisé lors d’un stage au laboratoire **IETR** de l’**INSA Rennes**, au sein de l’équipe [Vaader](https://www.ietr.fr/equipe-vaader-video-analysis-and-architecture-design-embedded-resources).

Il consiste en une application interactive destinée à **illustrer le fonctionnement d’un algorithme génétique** auprès d’un public large, des enfants aux adultes.

L’application simule des **voitures** cherchant à parcourir le plus de distance possible sur un circuit. Au fil des générations, leur performance s’améliore grâce à l’algorithme génétique.

Les **paramètres des voitures** peuvent aussi être définis à partir de **dés colorés détectés par caméra**, permettant de générer aléatoirement de nouveaux individus à comparer avec ceux de la simulation.

Un **support visuel** (Supports.pdf / Supports.svg) accompagne la démonstration pour aider à expliquer les mouvements et les principes de l’algorithme.

## Guide d’installation

Prérequis : [uv](https://docs.astral.sh/uv/)

```bash
uv sync          # Crée le venv et installe les dépendances
uv run python src/main.py   # Lance l’application
```

## Fonctionnalités

<p align="center">
  <img src="/images/menu.png">
  <em>Capture d'écran de l'application</em>
</p>

Après avoir lancé le programme, vous arrivez directement dans l'application. Le bouton tout en haut à gauche permet
d'ouvrir un menu permettant de modifier les paramètres de la simulation. Ces paramètres sont explicitées plus bas dans 
ce document.

Le bouton 'Garage' permet de voir toutes les voitures des générations précédentes, ainsi que les voitures capturées 
avec les dés. Ces voitures se sauvegardent lorsqu'on ferme l'application (⚠️ Pour que cela fonctionne, il faut 
fermer la simulation avec la croix en haut à droite et non en forçant la fermeture du programme). Dans ce menu, vous 
pouvez sélectionner les voitures pour les faire rouler, ou bien les modifier (modification du nom,
de la couleur, des paramètres ou suppression de la voiture).

Le bouton 'Capter les dés' permet d'utiliser la caméra pour reconnaître la valeur des différents dés. Les dés à utiliser doivent
avoir des points blancs. Ces dés sont les suivants:
- un dé **rouge**
- un dé **noir**
- un dé **vert**
- un dé **orange**
- un dé **jaune**
- un dé **jaune foncé** (avec des points noirs)

Après un clic sur le bouton 'Capter les dés", Une fenêtre s'affiche et on peut y voir les dés ainsi que 
leurs scores en temps réel.

<p align="center">
  <img src="/images/dice.png" alt>
</p>
<p align="center">
  <em>Capture d'écran de la reconnaissance des dés</em>
</p>
  

Il faut attendre un peu que le score se stabilise, et lorsque c'est bon, on peut cliquer n'importe où pour quitter
cette fenêtre. Il y a alors la possibilité de modifier la valeur des dés en cas d'erreurs. 

⚠️ Il est possible que la caméra ne soit pas reconnu. Dans ce cas, il faut modifier le numéro de la caméra dans le menu
paramètres.

D'autres boutons sont présent en haut à droite de l'écran. Ils servent à changer le circuit, changer le nombre
de voitures, lancer la simulation, arrêter la simulation, mettre en pause, recommencer la dernière génération, ou 
passer à la génération suivante. On peut aussi cliquer directement sur les voitures pour afficher leurs paramètres 
ainsi que leurs champs de vision.

Enfin, le bouton coloré à gauche permet de visualiser les emplacements où il y a le plus de crash de voitures. (Plus les cercles
sont rouges foncés, plus il y a de crashs à cet endroit).

### Paramètres de la simulation

Les paramètres pouvant être modifiés sont les suivants :
- **Paramètres généraux** :
  - **FPS** : le nombre d'images par seconde, cela permet d'accélerer ou de ralentir la simulation (sans impact sur le
  résultat final)
  - **Seed** : la graine utilisée pour générer les voitures (si on utilise la même seed sur le même circuit avec les mêmes paramètres, on obtiendra
  toujours le même résultat)
  - **Caméra** : le numéro de la caméra à utiliser pour la reconnaissance des dés
- **Paramètres d'affichage :**
  - **Champs de vision** : afficher les cônes de détections utilisés par les voitures
  - **Explosions** : afficher des explosions lorsqu'une voiture touche un mur
  - **Checkpoints** : afficher les checkpoints du circuit actuel
- **Paramètres des voitures :**
  - **Vitesse maximale** : modifier la vitesse maximale des voitures
  - **Angle de rotation** : modifier l'angle de rotation des voitures
  - **Accélération** : modifier la puissance de l'accélération des voitures
  - **Freinage** : modifier la puissance de freinage des voitures
  - **Coef drift** : modifier le coefficient de drift des voitures (un coeficient élevé fait glisser les
  voitures)
- **Paramètres de l'algorithme génétique :**
  - **Proportion conservée** : modifier la proportion de voitures conservées à l'identique lors de la sélection
  naturelle
  - **Chance croisement** : modifier la chance de croisement des voitures (plus la valeur est élevée, plus les voitures
  ont de chance d'échanger leurs caractéristiques)
  - **Chance mutation** : modifier la chance de mutation des voitures (plus la valeur est élevée, plus les voitures
  ont de chance de muter)
  - **Temps par génération** : modifier le temps de la simulation par génération (en secondes)
- **Paramètres des cônes de vision :**
  - **Largeur** : modifier la largeur du champ de vision des voitures
  - **Longueur** : modifier la longueur du champ de vision des voitures


## Explication du système de contrôle des voitures

Le système de contrôle se base sur le champ de vision des voitures. Les différents véhicules ont tous les mêmes 
caractéristiques de base : taille, accélération, vitesse maximale, force de freinage… La seule différence est le 
champ de vision, représenté par un cône. Un cône peut être représenté avec deux dés : un dé qui détermine la largeur
du cône, et un dé qui détermine la longueur du cône. Les valeurs des dés indiquent la taille du cône.

<p align="center">
  <img src="/images/cones.png" alt>
</p>
<p align="center">
  <em>Exemple de cônes de détection</em>
</p>


Leur champ de vision évolue en fonction de leur vitesse. C’est par 
exemple le cas dans la réalité, avec un champ de vision qui a tendance à se rétrécir au fur et à mesure que la 
vitesse augmente. Nous retrouvons cela avec les voitures de la simulation, qui possèdent 3 champs de vision différents 
en fonction de leur vitesse actuelle. Selon la vitesse, il faut donc utiliser le bon cône de vision. Nous pouvons 
par exemple imaginer 3 champs de visions différents pour 3 zones de vitesses différentes :
- Vitesse lente : Moins de 50 km/h
- Vitesse moyenne : Entre 50 et 100 km/h
- Vitesse rapide : Plus de 100 km/h

C’est le même principe pour les voitures de la simulation, avec des unités de vitesse différentes. Chaque 
cône de vision étant représenté par deux dés, il faut 6 dés au total pour représenter nos voitures. Cela fait 
ainsi 46 656 possibilités de voitures différentes.

La voiture utilise ensuite son cône pour se déplacer. À chaque pas de simulation, la voiture détecte les murs et 
agit en conséquence. Tout d’abord, elle regarde si elle détecte un mur en face d’elle dans le cône de vision. Si
c’est le cas, elle freine, sinon, elle accélère. Elle regarde ensuite s’il y a un mur qui coupe le champ de vision sur les côtés. 
S’il y a un mur à gauche, elle tourne à droite et inversement. S’il y a un mur de chaque côté, la voiture regarde 
quel mur est le plus proche et tourne de telle sorte à s’en éloigner.


## Organisation des fichiers

- **data** : contient des données utiles lors de la simulation ainsi que les résultats de différents tests
    - **checkpoints** : contient les coordonnées des checkpoints pour chaque circuit
    - **tests** : contient les résultats des différents tests (des résultats concernant le nombre de voitures pouvant 
faire le tour de chaque circuit se trouvent dans le dossier 'data/tests/all_cars/analysis')
    - **cars** : contient les voitures sauvegardées
    - **parameters** : contient les paramètres de la simulation pour chaque circuit
  

- **images** : contient les images utilisées dans l'application


- **src** : contient le code source de l'application
    - **data**: contient les fichiers permettant de gérer les données
    - **game**: contient les fichiers permettant de gérer la simulation
    - **menus**: contient les fichiers permettant de gérer les menus
    - **render**: contient les fichiers permettant de gérer l'affichage
    - **other**: contient des fonctions diverses ainsi que les fichiers permettant de gérer la reconnaissance des dés
    - **main.py**: fichier principal de l'application
    - **analyze_data.py**: fichier permettant d'analyser les données de la simulation
    - **Supports.pdf**: fichier de support à la démonstration
    - **Supports.svg**: fichier de support à la démonstration (format SVG)


## Crédits

Démonstrateur Python réalisé par Valentin Cherel sous la supervision de Karol Desnos et Hugo Miomandre, à partir d'une implémentation en C par Enzo Leveque, Loïs Rincé et Tanguy Raufflet, sous la supervision de Karol Desnos.
