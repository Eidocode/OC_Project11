from django.core import management
from django.db import connections
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from products.models import Category, Product, Favorite


class TestUserExperience(TestCase):
    """
        Test User Experience test case
    """

    @classmethod
    def setUpClass(cls):
        # Setup objects used for test methods
        super(TestUserExperience, cls).setUpClass()
        # Adds 1 category in test database
        category = Category(
            name='Category1',
            json_id='fr:category1',
            url='https://www.openfoodfacts.com/category1',
        )
        category.save()

        prod_with_accent = Product(
                name='Pâtes',
                brand='Marqué',
                description='Product Description',
                score='B',
                barcode='12345678',
                url_img_small='https://www.off.com/cat/prod/img_small',
                url_img='https://www.off.com/cat/prod/img',
                url_off='https://www.off.com/cat/prod/off',
                url_img_nutrition='https://www.off.com/cat/prod/img_nt',
            )
        prod_with_accent.save()
        prod_with_accent.categories.add(category.id)
        # Add 40 products in test database
        number_of_products = 40
        for pnum in range(number_of_products):
            product = Product(
                name=f'Product {pnum}',
                brand=f'Brand {pnum}',
                description='Product Description',
                score='B',
                barcode=f'12345678910{pnum}',
                url_img_small=f'https://www.off.com/cat/prod/img_small{pnum}',
                url_img=f'https://www.off.com/cat/prod/img{pnum}',
                url_off=f'https://www.off.com/cat/prod/off{pnum}',
                url_img_nutrition=f'https://www.off.com/cat/prod/img_nt{pnum}',
            )
            product.save()
            product.categories.add(category.id)
        products = Product.objects.all()
        # some class variables
        cls.product_id = products[1].id
        cls.substitute_id = products[20].id
        cls.favorite_id = None

    def setUp(self):
        # Logon new user
        self.logon_user = self.client.post(
                    reverse('signup'),
                    data={
                        'username': 'test_user4',
                        'first_name': 'test4',
                        'last_name': 'user4',
                        'email': 'test.user4@oc.fr',
                        'password1': 'Apass_0404',
                        'password2': 'Apass_0404',
                    })

    @classmethod
    def tearDownClass(cls):
        # Call super to close connections and remove data from the database
        super().tearDownClass()
        # Delete the test database
        management.call_command('flush', verbosity=0, interactive=False)
        # Disconnect from the test database
        connections['default'].close()

    def test_categories(self):
        """
        Test categories in database
        """
        categories = Category.objects.all()
        self.assertEqual(len(categories), 1)

    def test_products(self):
        """
        Test products in database
        """
        products = Product.objects.all()
        self.assertEqual(len(products), 41)

    def test_logon_user(self):
        """
        Test that user is registered
        """
        users = User.objects.all()
        self.assertEqual(len(users), 1)
        self.assertRedirects(self.logon_user, '/')

    def test_account(self):
        """
        Test account page with logged user
        """
        account_page = self.client.get(reverse('user_account'))
        current_user = account_page.wsgi_request.user
        self.assertEqual(account_page.status_code, 200)
        self.assertEqual(current_user.email, 'test.user4@oc.fr')
        self.assertEqual(current_user.username, 'test_user4')
        self.assertEqual(current_user.first_name, 'test4')
        self.assertEqual(current_user.last_name, 'user4')

    def test_change_password_page(self):
        """
        Test change password page
        """
        password_page = self.client.get(reverse('change_password'))
        self.assertEqual(password_page.status_code, 200)

    def test_change_password_failure(self):
        """
        Test change password (failure) with current user
        """
        data = {
            'old_password': 'Apass_0101',
            'new_password1': 'Newpass_0505',
            'new_password2': 'Newpass_0505',
        }
        change_password = self.client.post(
            reverse('change_password'),
            data
        )
        self.assertEqual(change_password.status_code, 200)

    def test_change_password_success(self):
        """
        Test change password (success) with current user
        """
        data = {
            'old_password': 'Apass_0404',
            'new_password1': 'Newpass_0505',
            'new_password2': 'Newpass_0505',
        }
        change_password = self.client.post(
            reverse('change_password'),
            data
        )
        self.assertRedirects(change_password, reverse('user_account'))

    def test_search_product(self):
        """
        Test to search an available product
        """
        search = self.client.get(
            reverse('search')+'?search_filter=product&search=Product')
        self.assertEqual(search.status_code, 200)
        self.assertTrue(search.context['paginate'] is True)
        self.assertEqual(len(search.context['products']), 6)

    def test_search_product_with_accented_name(self):
        """
        Product search test with or without accent
        """
        first_search = self.client.get(
            reverse('search')+'?search_filter=product&search=Pâte')
        second_search = self.client.get(
            reverse('search')+'?search_filter=product&search=Pate')
        self.assertEqual(first_search.status_code, 200)
        self.assertTrue(first_search.context['paginate'] is True)
        self.assertEqual(len(first_search.context['products']), 1)
        self.assertEqual(first_search.status_code, second_search.status_code)
        self.assertEqual(second_search.status_code, 200)
        self.assertEqual(
            len(first_search.context['products']),
            len(second_search.context['products'])
        )

    def test_result_product(self):
        """
        Test result page with an existing product
        """
        result = self.client.get(reverse(
                    'result',
                    kwargs={'product_id': self.product_id}
                ))
        self.assertEqual(result.status_code, 200)
        self.assertEqual(len(result.context['substitutes']), 6)

    def test_search_category(self):
        """
        Test search by category
        """
        search = self.client.get(
            reverse('search')+'?search_filter=category&search=Category')
        self.assertEqual(search.status_code, 200)
        self.assertTrue(search.context['paginate'] is True)
        self.assertEqual(len(search.context['products']), 6)

    def test_search_brand(self):
        """
        Test search by brand
        """
        search = self.client.get(
            reverse('search')+'?search_filter=brand&search=Brand')
        self.assertEqual(search.status_code, 200)
        self.assertTrue(search.context['paginate'] is True)
        self.assertEqual(len(search.context['products']), 6)

    def test_search_barcode(self):
        """
        Test search by barcode
        """
        search = self.client.get(
            reverse('search')+'?search_filter=barcode&search=1234567891012')
        self.assertEqual(search.status_code, 200)
        self.assertTrue(search.context['paginate'] is True)
        self.assertEqual(len(search.context['products']), 1)

    def test_search_nutriscore(self):
        """
        Test search by nutriscore
        """
        search = self.client.get(
            reverse('search')+'?search_filter=score&search=B')
        self.assertEqual(search.status_code, 200)
        self.assertTrue(search.context['paginate'] is True)
        self.assertEqual(len(search.context['products']), 6)

    def test_handles_favorites(self):
        """
        Test to add, check & remove a product from favorites
        """
        # Add a product to favorites
        self.client.get(reverse(
            'add_fav',
            kwargs={'product_id': self.substitute_id}),
            HTTP_REFERER=reverse(
                'result',
                kwargs={'product_id': self.product_id}))
        self.assertEqual(len(Favorite.objects.all()), 1)
        # Get a product from favorites
        favorite_page = self.client.get(reverse('favorites'))
        favorites = favorite_page.context['favorites']
        self.assertEqual(len(favorites), 1)
        for fav in favorites:
            self.favorite_id = fav.id
            self.assertEqual(fav.products.id, self.substitute_id)
        # Remove a product from favorites
        del_favorite = self.client.get(reverse(
                            'del_fav',
                            kwargs={'favorite_id': self.favorite_id}),
                            HTTP_REFERER=reverse('favorites'))
        self.assertEqual(del_favorite.status_code, 302)
        self.assertRedirects(del_favorite, '/users/favorites/')
        favorites = Favorite.objects.all()
        self.assertEqual(len(favorites), 0)

    def test_product_detail(self):
        """
        Test detail page with an existing product
        """
        detail_page = self.client.get(reverse(
                        'detail',
                        kwargs={'product_id': self.product_id}))
        self.assertEqual(detail_page.status_code, 200)

        product = Product.objects.get(pk=self.product_id)
        self.assertEqual(
            detail_page.context['product'].name,
            product.name
        )
        self.assertEqual(
            detail_page.context['product'].score,
            product.score
        )
        self.assertEqual(
            detail_page.context['product'].barcode,
            product.barcode
        )
        self.assertEqual(
            detail_page.context['product'].description,
            product.description
        )
        self.assertEqual(
            detail_page.context['product'].url_off,
            product.url_off
        )
        self.assertEqual(
            detail_page.context['product'].url_img_nutrition,
            product.url_img_nutrition
        )

    def test_logout_user(self):
        """
        Test to logout the current logged user
        """
        logout = self.client.get('/logout/')
        self.assertEqual(logout.status_code, 302)
        self.assertRedirects(logout, '/')
