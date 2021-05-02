import requests

from django.core.management.base import BaseCommand

from random import randrange

from products.models import Category


URL = 'https://fr.openfoodfacts.org/'  # + /categorie/[name_cat].json

MIN_PRODUCTS_TO_FILTER = 100  # Minimum number of products in a category


class Command(BaseCommand):
    """
    Class used to add a new parameter fill_db_categories to manage.py

    ...

    Methods
    -------
    add_arguments(parser)
        Adds int argument for command line

    handle()
        Contains the method called when executed the command line
        (set_categories_to_db) with the specified int argument

    _get_categories(min_nb_prod)
        Method used to get OpenFoodFacts categories from and returns those
        filtered by min_nb_prod

    _get_random_categories(nb_cat)
        Returns some random categories contained in _get_categories defined by
        int nb_cat

    _compare_with_db(nb_cat)
        Compares the data in the database with data received from openfoodfacts
        to avoid adding duplicates. Returns a clean list of categories

    _set_categories_to_db(nb_cat)
        Used to set new categories to database

    """

    help = 'Adds categories and products in pur_beurre database'

    def add_arguments(self, parser):
        """Adds int argument for command line"""

        parser.add_argument(
            'nb_catg',
            type=int,
            nargs='?',
            default=2,
            help='Indicates the number of categories to be created',
        )

    def handle(self, *args, **options):
        """Contains the method called when executed the command line
        (set_categories_to_db) with the specified int argument"""

        nb_cats = options['nb_catg']  # Gets nb_catg argument
        self.stdout.write("Processing for %s categories..." % nb_cats)
        self._set_categories_to_db(nb_cats)  # set_categories_to_db method

    def _get_categories(self, min_nb_prod):
        """Method used to get OpenFoodFacts categories from and returns those
        filtered by min_nb_prod"""

        self.stdout.write(
            "Getting categories containing at least %s products" % min_nb_prod)
        list_cat = []
        list_cat_filtered = []

        # Getting all categories from openfoodfacts
        json_cat = requests.get(
            URL + 'categories.json',
            headers={
                'content-type': 'application/json',
                'User-Agent': 'python-requests - PurbeurreApp'
                }
        ).json()
        list_cat = json_cat.get('tags')

        for category in list_cat:
            # Filter categories by 'id' starting with fr and containing at
            # least min_nb_prod products
            if (category['products'] >= min_nb_prod and
                    category['id'].startswith('fr')):
                json_category = requests.get(
                    category['url'] + '.json',
                    headers={
                        'content-type': 'application/json',
                        'User-Agent': 'python-requests - PurbeurreApp',
                        }
                    ).json()
                nb_products = int(json_category.get('count'))
                if nb_products is not None:
                    if nb_products >= min_nb_prod:
                        list_cat_filtered.append(category)

        print("Categories >= {} product(s) : {}".format(
            min_nb_prod,
            str(len(list_cat_filtered))
        ))

        return list_cat_filtered

    def _get_random_categories(self, nb_cat):
        """Returns some random categories contained in _get_categories defined by
        int nb_cat"""

        # Gets Openfoodfacts categories
        lst = self._get_categories(MIN_PRODUCTS_TO_FILTER)

        if nb_cat > len(lst):
            # Checks if nb_cat > lst length
            nb_cat = len(lst)
            print('Number of categories is less than the parameter...')

        self.stdout.write("Getting %s random categories..." % nb_cat)

        categories = []
        for i in range(nb_cat):
            # Random selection of categories
            index = randrange(0, len(lst))
            categories.append(lst.pop(index))

        return categories

    def _compare_with_db(self, nb_cat):
        """Compares the data in the database with data received from openfoodfacts
        to avoid adding duplicates. Returns a clean list of categories"""

        categories_in_db = Category.objects.all()  # Gets categories from db
        json_ids_in_db = []
        for category in categories_in_db:
            # Gets json_id from each category
            json_ids_in_db.append(category.json_id)

        new_categories = self._get_random_categories(nb_cat)
        self.stdout.write(
            "Compares selection with existing data stored in the database...")

        categories_list = []
        for category in new_categories:
            # Checks if new category id exists in db
            if category['id'] not in json_ids_in_db:
                categories_list.append(category)
            else:
                print("{} with json_id : {} already in database...".format(
                    category['name'],
                    category['id'])
                )

        return categories_list

    def _set_categories_to_db(self, nb_cat):
        """Used to set new categories to database"""
        categories = self._compare_with_db(nb_cat)  # Gets new categories
        self.stdout.write(
            "Adding %s categories in the database..." % len(categories))

        # Adds new categories in db
        for category in categories:
            new_category = Category(
                name=category['name'],
                json_id=category['id'],
                url=category['url']
            )
            print('Added new category : {} to database'.format(
                category['name'])
            )
            new_category.save()  # Save category to db
