
# Améliorez un projet existant en Python

*Projet N°11 - Parcours développeur d'application Python*

### Sujet du projet

Basez-vous sur l’un des projets que vous avez déjà réalisés dans ce parcours de formation ou dans votre carrière. Choisissez une fonctionnalité à ajouter. Elle doit être assez importante pour justifier des tests fonctionnels. Votre mentor jouera le rôle du client. Jouez le jeu et communiquez avec lui de la même manière que vous le feriez avec un client : soignez votre présentation, l’endroit où se déroule votre session de mentorat et l’orthographe dans vos e-mails !

Quant aux tests, cassez-en un puis réparez-le en le "**refactorant**". Je suis sûre que vous avez un test caché quelque part qui mérite une nouvelle jeunesse !


## Structure du projet

Dans notre cas, nous avons sélectionné le **projet N°8** pour le développement de deux nouvelles fonctionnalités. La structure est donc sensiblement la même, pour de plus amples informations à ce sujet, merci de consulter le **Readme.md** du **projet N°8** ⇒ [**Créez une plateforme pour amateurs de Nutella**](https://github.com/Eidocode/OC_Project8#cr%C3%A9ez-une-plateforme-pour-amateurs-de-nutella)

La première fonctionnalité consiste à permettre à un utilisateur de modifier son mot de passe quand il le souhaite, et la seconde, ajoute de nouvelles possibilités de recherche de produit.


### Fonctionnalité "Change_password" :

Comme expliqué précédemment, cette fonctionnalité permet à un utilisateur de modifier son mot de passe lorsqu'il le souhaite. Les modifications apportées au projet pour intégrer cette fonctionnalité, se situent principalement dans l'application "**Users**" du projet. Un **template** a été ajouté, contenant le nouveau formulaire, ainsi qu'un élément "**Password**" dans la page "**Gestion de compte**" contenant un bouton "**Modifier**" pointant vers le **template** associé.
La méthode "**change_password()**", dans le fichier "**views.py**" contient la logique utilisée par cette fonctionnalité.


### Fonctionnalité "Search_filter" :

Cette deuxième fonctionnalité permet à un utilisateur d'effectuer des recherches plus uniquement sur le nom du produit, mais également par catégorie, marque, code-barres et nutriscore. Ici, les modifications apportées se situent au niveau de l'application "**Products**" de l'application. 
Le formulaire utilisé par la barre de recherche a été modifié pour ajouter sur la partie gauche un menu déroulant permettant à l'utilisateur de sélectionner le "**type**" de recherche qu'il souhaite effectuer. Cela se situe au niveau du fichier "**forms.py**" ou d'autres restrictions ont été ajoutées pour chacun des types énoncés précédemment. 
Bien entendu, le fichier "**views.py**" a également été modifié puisque la "*méthode*" de recherche utilisée précédemment n'est plus d'actualité. Celle-ci, nommée "**search()**" contient les différentes "*conditions*" de recherche. A noter qu'une partie de la précédente version de la fonctionnalité se situe maintenant dans une autre méthode nommée "**get_search_result()**"


### Bugfix :

Le sujet du projet nécessitait également que le client décèle un *Bug* sur le serveur de production qu'il fallait donc corriger rapidement. Dans notre cas, il s'avère que la recherche d'un produit contenant un accent pouvait poser problème. En effet, si la base de données contient un nom de produit accentué (Pâtes par exemple) le résultat sera différent selon que la recherche soit saisie avec ou sans accent. 
Afin de corriger cela sans trop impacter l'application déjà en production, nous avons trouvé la possibilité d'utiliser une extension **PostgreSQL** nommée "**Unaccent**" et permettant de retourner le résultat d'une requête avec et sans accent.
Donc si on saisi "*Pâtes*" comme recherche, elle retournera les éléments contenant "*Pâtes*" et "*pate*" par exemple.

Pour cela, des modifications mineures ont été apportées sur l'application et également la base de données. 

Côté application, la modification se situe au niveau des "**queryset**". En effet, l'ajout de "**unaccent**" dans le filtre d'une "**queryset**" suffit, cela donnera donc :

    result = Product.objects.filter(name__unaccent__icontains=query)

Il est également nécessaire d'ajouter l'élément suivant dans les settings de l'application :

    INSTALLED_APPS = [
         ...
         'django.contrib.postgres',
         ...
    ]

Côté base de données **PostgreSQL**, il faut également effectuer certaines modifications :
 - Sur la console **PSQL** du serveur hébergeant la base de données : 
	
		CREATE EXTENSION unaccent;
	
	puis on donne les droits *superuser* à l'utilisateur chargé d'interagir avec la base :

		ALTER ROLE <username> SUPERUSER;

 - On créé ensuite une *migration* vide du côté de **Django** : 

		manage.py makemigrations myapp --empty

 - On ouvre ensuite le fichier créé par la migration pour y ajouter la prise en charge de l'extension "**Unaccent**" :

		from django.contrib.postgres.operations import UnaccentExtension
		from django.db import migrations

	    class Migration(migrations.Migration):
    
        dependencies = [
            ('products', '0001_initial'),
        ]
    
        operations = [
            UnaccentExtension()
        ]

 - Il suffit maintenant d'appliquer la migration par l'intermédiaire de la commande :

		manage.py migrate

 - Il ne reste alors plus qu'à rétablir les droits sur l'utilisateur de la base :

		ALTER ROLE <username> NOSUPERUSER;


## Tests unitaires & fonctionnels :

Les précédents tests ont été modifiés pour fonctionner avec les nouvelles fonctionnalités, et bien évidemment, des nouveaux ont été ajoutés pour couvrir la quasi totalité de l'application. La couverture actuelle des tests concerne **98%** de l'application. Les tests unitaires sont visibles dans le répertoires "**tests**" de l'application "**Products**" et se nomment : "**test_forms.py**", "**test_models.py**" et "**test_views.py**".
Des tests fonctionnels sont également disponibles dans à la racine de l'application "**Users**" : "**test_user_experience.py**" et un test intégrant **Sélénium** nommé "**s_test_app_integration.py**".
A noter qu'il est nécessaire de renommer le test **Sélénium** en supprimant le préfixe "**s_**" pour l'intégrer au "*coverage*".