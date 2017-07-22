#READ ME

----------


----------

##Les fichiers python


----------


###scrap.py

Contient les programmes de scap pour fairlay, forbet, et le comparateur de côte. Ils sont décomposés en quatre rubriques, une pour chaque site, et la dernière contenant l'API finale. On y trouve la fonction de scrap définitive de chaque site, ainsi que sa version de test, qui est identique à la différence près que les changements dans la base de données ne sont pas sauvegardés.

 - ajourfc(*jour*) : Regarde les matchs de la base **matchavenir** survenant avant *jour* jours, et rentre dans la base **coteSites** les côtes des différents sites de paris trouvés sur le comparateur

 - scrapmatch(*jour*) : met à jour les bases **matchavenir**, **cotefair**, et **volumefair** avec les matchs de Fairlay se déroulant dans moins de *jour* jours.
 
 - rez(*minu*) : commence par déplacer les matchs déjà passés de la table **matchavenir** à la table **matchhier**. Pour tous les matchs de **matchhier**, cherche sur forbet les résulats, et les inscrit dans la table **result**. Pour matcher les résultats avec les matchs de la base **matchavenir**, dont les noms d'équipes et les date sont indiqués par Fairlay, on regarde si au moins un des noms concorde, et si la date est proche à *minu* minutes près (il y a souvent des petites différences, parfois même des erreurs d'une heure...). Quand c'est le cas, on rajoute à **result** le résultat, avec les noms et la date de Fairlay.
 
 - reztest(*minu*) : Pour éviter des matchs qui ne seraient pas matchés si les noms des deux équipes étaient légèrement différents sur Fairlay et sur Forbet, reztest affiche pour tous les matchs de matchhier non matchés l'ensemble des matchs qui s'étaient déroulés à la même date à *minu* minutes près. L'affichage est du type : 
```
 cur.execute('INSERT INTO nomfp(nomf, nomp) VALUES(?,?)', ['Inter Baku Sporting Club', 'Inter Baku'])
```

Lorsque les équipes concordent, on utilise TT.py.


----------
### TT.py

Lorsque l'on a trouvé des équipes qui concordent avec des noms différents sur Fairlay et Forbet, on les ajoute à la table **nomfp**. Elle contient des couples de noms et fait la correspondance entre les dénominations utilisées par les deux sites. Pour cela, on utilise instruction précédente, que l'on y copie colle et éxécute après avoir décommenté la ligne : 
 ```
 #conn.commit()
```

----------


### Projet X.py

Un fichier qui sert simplement à appeler les fonctions de scrap.py.


----------


###rentabilité.py

Tests de rentabilité d'algorithmes avec les 250 matchs de la base de donnée. Étrangement, on perd de l'argent quand on parie avec une espérance positive, et on en gagne lorsque l'on prend des paris à priori perdants. 


----------


### Création bases.py

Les informations relatives aux bases de données, et les codes pour les créer. 

### fairscrap.py

Un brouillon :)
