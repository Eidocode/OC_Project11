import requests

from django.core.management.base import BaseCommand
from random import randrange
from math import ceil

from products.models import Category, Product


PRODUCTS_PER_PAGE = 20  # Products per page of a category in openfoodfacts


class Command(BaseCommand):
    """
    Class used to add a new parameter fill_db_products to manage.py

    ...

    Methods
    -------
    add_arguments(parser)
        Adds int argument for command line

    handle()
        Contains the method called when executed the command line
        (_get_random_products) with the specified int argument

    _get_categories_url()
        Gets from database all categories url

    _get_categories_jsonid()
        Gets from database categories id & jsonid

    _get_products_from_url(url)
        Gets all products from category openfoodfacts url

    _get_random_products(nb_prod)
        Returns some random products defined by int nb_prod

    _test_product_keys(product)
        Tests each key in product to define viability

    _get_products_db_barcode()
        Gets all products barcodes in database
    """

    help = 'Adds categories and products in pur_beurre database'

    def add_arguments(self, parser):
        """Adds int argument for command line"""

        parser.add_argument(
            'nb_prod',
            type=int,
            nargs='?',
            default=5,
            help='Indicates the number of products by category to be created'
        )

    def handle(self, *args, **options):
        """Contains the method called when executed the command line
        (set_categories_to_db) with the specified int argument"""

        nb_prod = options['nb_prod']  # Gets nb_prod argument
        self.stdout.write(
            "Processing for %s products by category..." % nb_prod
        )
        self._get_random_products(nb_prod)  # _get_random_products method

    def _get_categories_url(self):
        """Gets from database all categories url"""

        categories_in_db = Category.objects.all()  # Gets categories from db
        categories_url = []
        for category in categories_in_db:
            # Gets category url
            categories_url.append(category.url)

        return categories_url

    def _get_categories_jsonid(self):
        """Gets from database categories id & jsonid"""

        categories_in_db = Category.objects.all()  # Gets categories from db
        categories_jsonid = []
        for category in categories_in_db:
            data = {
                'id': category.id,
                'json_id': category.json_id,
            }
            categories_jsonid.append(data)

        return categories_jsonid

    def _get_products_from_url(self, url):
        """Gets all products from category openfoodfacts url"""

        # Attempt to connect to the specified url
        try:
            url_json = requests.get(
                url + '.json',
                headers={
                    'content-type': 'application/json',
                    'User-Agent': 'python-requests - PurbeurreApp',
                    }
                )
            print('Connecting to {}...'.format(url))
        except requests.exceptions.ConnectionError:
            print('Unable to connect to {}, skip the category...'.format(url))
            return
        except requests.exceptions.ConnectionError:
            print('An error has occured with {}...'.format(url))
            return

        self.stdout.write("Getting products from " + url)
        json_data = url_json.json()

        nb_products = int(json_data.get('count'))  # Nb products in category

        # Nb pages defined by PRODUCTS_PER_PAGE
        nb_pages = ceil(nb_products / PRODUCTS_PER_PAGE)

        lst_all_prods = []
        i = 1
        # Gets products from all pages
        for i in range(nb_pages):
            page_url = "{}/{}.json".format(url, str(i))
            json_url_products = requests.get(
                page_url,
                headers={
                    'content-type': 'application/json',
                    'User-Agent': 'python-requests - PurbeurreApp',
                    }
                ).json()
            lst_products = json_url_products.get('products')

            for product in lst_products:
                lst_all_prods.append(product)

        return lst_all_prods

    def _get_random_products(self, nb_prod):
        """Returns some random products defined by int nb_prod"""

        # Gets Categories jsonid, url & products barcodes
        categories_db_jsonid = self._get_categories_jsonid()
        products_db_barcode = self._get_products_db_barcode()
        categories_url = self._get_categories_url()

        list_rnd_products = []
        count = 0
        for url in categories_url:
            # Gets products from categories url
            products_in_category = self._get_products_from_url(url)

            if products_in_category is None:
                continue

            print('==== {} ===='.format(url))
            print('')

            if nb_prod > len(products_in_category):
                nb_prod = len(products_in_category)
                print(
                    "{} products available in this category...".format(nb_prod)
                )

            rnd_prod_catg = []
            for i in range(nb_prod):
                # Gets some products randomly
                index = randrange(0, len(products_in_category))
                rnd_prod_catg.append(products_in_category.pop(index))
                i += 1

            list_rnd_products.append(rnd_prod_catg)

            for product in rnd_prod_catg:
                # Test products data
                data = self._test_product_keys(product)
                if data is not None:
                    prod = Product(
                        name=data['name'],
                        brand=data['brand'],
                        description=data['description'],
                        score=data['score'],
                        barcode=data['barcode'],
                        url_img_small=data['url_img_small'],
                        url_img=data['url_img'],
                        url_off=data['url_off'],
                        url_img_nutrition=data['url_img_nutrition'],
                    )

                    # Checks if product barcode exists in db
                    if data['barcode'] not in products_db_barcode:
                        prod.save()
                    else:
                        print(
                            '{} with barcode : {} already in database'.format(
                                data['name'],
                                data['barcode'])
                            )
                        continue

                    for catg in categories_db_jsonid:
                        # Linking (if any) in database between new products
                        # and existing categories
                        if catg['json_id'] in product['categories_tags']:
                            prod.categories.add(catg['id'])
                            print('Links {} with category id {}'.format(
                                data['name'],
                                catg['id'])
                            )

                    count += 1
            print('')

        print(str(count) + ' viables products.')

        return list_rnd_products

    def _test_product_keys(self, product):
        """Tests each key in product to define viability"""

        data = None
        try:
            data = {
                'name': product['product_name'],
                'brand': product['brands'],
                'description': product['ingredients_text'],
                'score': product['nutriscore_grade'],
                'barcode': product['code'],
                'categories': product['categories_tags'],
                'url_img': product['image_url'],
                'url_img_small': product['image_small_url'],
                'url_off': product['url'],
                'url_img_nutrition': product['image_nutrition_url']
            }
        except KeyError:
            print('This product is not viable')

        return data

    def _get_products_db_barcode(self):
        """Gets all products barcodes in database"""

        products = Product.objects.all()  # Gets all products from database
        products_barcode = []

        for product in products:
            # Gets product barcode
            products_barcode.append(product.barcode)

        return products_barcode
