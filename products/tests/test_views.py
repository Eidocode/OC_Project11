from django.core import management
from django.db import connections
from django.test import TestCase
from django.urls import reverse

from products.forms import SearchForm
from products.models import Category, Product


class IndexPageTestCase(TestCase):
    """
    Index Page test case
    """

    def test_index_url_exists_at_location(self):
        """
        Test index page location returns 200
        """
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_index_url_by_name(self):
        """
        Test index page name returns 200
        """
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

    def test_index_url_uses_correct_template(self):
        """
        Test index uses a correct template
        """
        response = self.client.get(reverse('index'))
        self.assertTemplateUsed(response, 'products/index.html')


class IndexPageSearchBarTestCase(TestCase):
    """
        Index Page Search Bar test case
    """

    def test_index_search_form_one_char(self):
        """
        Test that submit one char on search form returns an error
        """
        form = SearchForm(data={
            'search_filter': 'product',
            'search': 'd'
        })
        self.assertFalse(form.is_valid())
        self.assertEquals(
            form.errors['search'][0],
            'Saisir, au minimum, deux caractères pour valider la recherche')

    def test_index_search_form_special_char(self):
        """
        Test that submit a special char on search form returns an error
        """
        form = SearchForm(data={
            'search_filter': 'category',
            'search': 'recherche@'
        })
        self.assertFalse(form.is_valid())
        self.assertEquals(
            form.errors['search'][0],
            'Les caractères spéciaux ne sont pas autorisés')

    def test_index_search_form_with_a_quote(self):
        """
        Test that submit a quote is not considered like a special char
        """
        form = SearchForm(data={
            'search_filter': 'product',
            'search': "C'est une recherche"
        })
        self.assertTrue(form.is_valid())

    def test_index_search_form_number(self):
        """
        Test that submit a number returns an error
        """
        form = SearchForm(data={
            'search_filter': 'brand',
            'search': 'recherche1',
        })
        self.assertFalse(form.is_valid())
        self.assertEquals(
            form.errors['search'][0],
            'Les chiffres ne sont pas autorisés')

    def test_index_search_form_barcode_less_5_chars(self):
        """
        Test submitting a barcode of less than 5 characters returns an error
        """
        form = SearchForm(data={
            'search_filter': 'barcode',
            'search': '1234',
        })
        self.assertFalse(form.is_valid())
        self.assertEquals(
            form.errors['search'][0],
            "Saisir, au minimum, cinq caractères pour valider "
            "la recherche d'un code-barres")

    def test_index_search_form_barcode_more_13_chars(self):
        """
        Test submitting a barcode longer than 13 characters returns an error
        """
        form = SearchForm(data={
            'search_filter': 'barcode',
            'search': '12345678901234',
        })
        self.assertFalse(form.is_valid())
        self.assertEquals(
            form.errors['search'][0],
            "Les codes-barres utilisent la norme EAN et ne peuvent contenir, "
            "au maximum, que 13 caractères numériques")

    def test_index_search_form_barcode_with_letters(self):
        """
        Test that submitting a barcode containing letters returns an error
        """
        form = SearchForm(data={
            'search_filter': 'barcode',
            'search': '1234567K',
        })
        self.assertFalse(form.is_valid())
        self.assertEquals(
            form.errors['search'][0],
            "Seuls les chiffres sont autorisés dans un code-barres")

    def test_index_search_form_nutriscore_with_many_chars(self):
        """
        Test submitting a nutriscore containing more than one character
        returns an error
        """
        form = SearchForm(data={
            'search_filter': 'score',
            'search': 'AB',
        })
        self.assertFalse(form.is_valid())
        self.assertEquals(
            form.errors['search'][0],
            "Un nutriscore n'est composé que d'une seule lettre")

    def test_index_search_form_nutriscore_with_nonexistent_letter(self):
        """
        Test submitting a nutriscore containing a non-existent letter
        returns an error
        """
        form = SearchForm(data={
            'search_filter': 'score',
            'search': 'F',
        })
        score_letters = ('A', 'B', 'C', 'D', 'E')
        self.assertFalse(form.is_valid())
        self.assertEquals(
            form.errors['search'][0],
            f"Seuls les caractères suivants sont autorisés dans un "
            f"nutriscore : {score_letters}")


class SearchPageTestCase(TestCase):
    """
        Search page test case
    """

    def test_search_url_exists_at_location(self):
        """
        Test that search page returns 200
        """
        response = self.client.get(
            '/products/search/?search_filter=product&search=test')
        self.assertEqual(response.status_code, 200)

    def test_search_url_by_name(self):
        """
        Test that a valid research returns 200
        """
        response = self.client.get(
            reverse('search')+'?search_filter=product&search=test')
        self.assertEqual(response.status_code, 200)

    def test_bad_search_url_returns_404(self):
        """
        Test that a bad research returns 404
        """
        response = self.client.get(reverse('search')+'search=test')
        self.assertEqual(response.status_code, 404)

    def test_search_url_uses_correct_template(self):
        """
        Test that search page returns a correct template
        """
        response = self.client.get(
            reverse('search')+'?search_filter=product&search=test')
        self.assertTemplateUsed(response, 'products/search.html')

    def test_pagination_is_true(self):
        """
        Test pagination
        """
        response = self.client.get(
            reverse('search')+'?search_filter=product&search=test')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('paginate' in response.context)
        self.assertTrue(response.context['paginate'] is True)


class ResultPageTestCase(TestCase):
    """
        Result page test case
    """

    @classmethod
    def setUpTestData(cls):
        # Setup objects used for test methods
        number_of_products = 20
        category = Category(
            name='Category',
            json_id='fr:category',
            url='https://www.openfoodfacts.com/category',
        )
        category.save()

        for pnum in range(number_of_products):
            prod = Product(
                name=f'Product {pnum}',
                brand=f'Brand {pnum}',
                description='Product Description',
                score='B',
                barcode=f'12345678910 {pnum}',
                url_img_small=f'https://www.off.com/cat/prod/img_small{pnum}',
                url_img=f'https://www.off.com/cat/prod/img{pnum}',
                url_off=f'https://www.off.com/cat/prod/{pnum}',
                url_img_nutrition=f'https://www.off.com/cat/prod/img_nt{pnum}',
            )
            prod.save()
            # Adds relations products --> category
            prod.categories.add(category.id)

    @classmethod
    def tearDownClass(cls):
        # Call super to close connections and remove data from the database
        super().tearDownClass()
        # Delete the test database
        management.call_command('flush', verbosity=0, interactive=False)
        # Disconnect from the test database
        connections['default'].close()

    def test_result_url_exists_at_location(self):
        """
        Test that result page returns 200
        """
        response = self.client.get('/products/5/')
        self.assertEqual(response.status_code, 200)

    def test_result_url_by_name(self):
        """
        Test that result page name returns 200
        """
        args = {'product_id': 5}
        response = self.client.get(reverse('result', kwargs=args))
        self.assertEqual(response.status_code, 200)

    def test_bad_search_url_returns_404(self):
        """
        Test that search url page returns 404 when a product id doesn't exist
        """
        args = {'product_id': 100}
        response = self.client.get(reverse('result', kwargs=args))
        self.assertEqual(response.status_code, 404)

    def test_search_url_uses_correct_template(self):
        """
        Test that search page uses correct template
        """
        args = {'product_id': 5}
        response = self.client.get(reverse('result', kwargs=args))
        self.assertTemplateUsed(response, 'products/result.html')

    def test_search_url_proposes_6_substitutes(self):
        """
        Test that search page offers 6 substitutes to the initial search
        """
        args = {'product_id': 5}
        response = self.client.get(reverse('result', kwargs=args))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('substitutes' in response.context)
        self.assertTrue(len(response.context['substitutes']) == 6)

    def test_detail_url_exists_at_location(self):
        """
        Test that detail page url returns 200
        """
        response = self.client.get('/products/5/detail/')
        self.assertEqual(response.status_code, 200)

    def test_detail_url_by_name(self):
        """
        Test that detail page name returns 200
        """
        args = {'product_id': 5}
        response = self.client.get(reverse('detail', kwargs=args))
        self.assertEqual(response.status_code, 200)

    def test_bad_detail_url_returns_404(self):
        """
        Test that detail page returns 404 if a product id doesn't exists
        """
        args = {'product_id': 100}
        response = self.client.get(reverse('detail', kwargs=args))
        self.assertEqual(response.status_code, 404)

    def test_detail_url_uses_correct_template(self):
        """
        Test that detail page uses correct template
        """
        args = {'product_id': 5}
        response = self.client.get(reverse('detail', kwargs=args))
        self.assertTemplateUsed(response, 'products/detail.html')

    def test_detail_url_returns_good_product(self):
        """
        Test that detail page provides good informations if product id exists
        """
        args = {'product_id': 4}
        response = self.client.get(reverse('detail', kwargs=args))
        product = response.context['product']
        self.assertEqual(product.name, 'Product 3')
        self.assertEqual(product.brand, 'Brand 3')
        self.assertEqual(product.score, 'B')
        self.assertEqual(product.description, 'Product Description')
        self.assertEqual(
            product.url_img_nutrition,
            'https://www.off.com/cat/prod/img_nt3')
        self.assertEqual(product.barcode, '12345678910 3')
        self.assertEqual(
            product.url_off,
            'https://www.off.com/cat/prod/3')


class LogonPageTestCase(TestCase):
    """
    Logon page test case
    """

    @classmethod
    def tearDownClass(cls):
        # Call super to close connections and remove data from the database
        super().tearDownClass()
        # Delete the test database
        management.call_command('flush', verbosity=0, interactive=False)
        # Disconnect from the test database
        connections['default'].close()

    def test_logon_url_exists_at_location(self):
        """
        Test that logon page location returns 200
        """
        response = self.client.get('/users/signup/')
        self.assertEqual(response.status_code, 200)

    def test_logon_url_by_name(self):
        """
        Test that logon page name returns 200
        """
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, 200)

    def test_logon_url_uses_correct_template(self):
        """
        Test that logon page uses correct template
        """
        response = self.client.get(reverse('signup'))
        self.assertTemplateUsed(response, 'users/signup.html')

    def test_logon_post_success(self):
        """
        Test that logon page returns 302 and redirects to homepage when a
        good POST request is sent
        """
        response = self.client.post(reverse('signup'),
                                    data={
                                        'username': 'test_user',
                                        'first_name': 'test',
                                        'last_name': 'user',
                                        'email': 'test.user@oc.fr',
                                        'password1': 'Apass_0404',
                                        'password2': 'Apass_0404',
                                        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/')

    def test_logon_post_failure(self):
        """
        Test that logon page returns 200 and false for form.is_valid if a bad
        POST request is sent
        """
        response = self.client.post(reverse('signup'),
                                    data={
                                        'username': 'test_user2',
                                        'first_name': 'test2',
                                        'last_name': 'user2',
                                        'email': 'test2.user2@oc.fr',
                                        'password1': 'Apass_0404',
                                        'password2': 'Apss_0404',
                                        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['form'].is_valid())


class LoginPageTestCase(TestCase):
    """
    Login page test case
    """

    def test_login_url_exists_at_location(self):
        """
        Test that login page location returns 200
        """
        response = self.client.get('/login/')
        self.assertEqual(response.status_code, 200)

    def test_login_url_uses_correct_template(self):
        """
        Test that login page uses a correct template
        """
        response = self.client.get('/login/')
        self.assertTemplateUsed(response, 'registration/login.html')


class AccountPageTestCase(TestCase):
    """
    Account page test case
    """

    def test_account_url_exists_at_location(self):
        """
        Test that account page location returns 200
        """
        response = self.client.get('/users/signup/')
        self.assertEqual(response.status_code, 200)

    def test_account_url_by_name(self):
        """
        Test that account page name returns 200
        """
        response = self.client.get(reverse('user_account'))
        self.assertEqual(response.status_code, 200)

    def test_account_url_uses_correct_template(self):
        """
        Test that account page uses a correct template
        """
        response = self.client.get(reverse('user_account'))
        self.assertTemplateUsed(response, 'users/user_account.html')


class FavoritePageTestCase(TestCase):
    """
    Favorite page test case
    """

    def setUp(self):
        self.client.post(
                reverse('signup'),
                data={
                    'username': 'test_user3',
                    'first_name': 'test3',
                    'last_name': 'user3',
                    'email': 'test.user3@oc.fr',
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

    def test_favorite_url_exists_at_location(self):
        """
        Test that favorite page location returns 200
        """
        response = self.client.get('/users/favorites/')
        self.assertEqual(response.status_code, 200)

    def test_favorite_url_by_name(self):
        """
        Test that favorite page name returns 200
        """
        response = self.client.get(reverse('user_account'))
        self.assertEqual(response.status_code, 200)

    def test_favorite_url_uses_correct_template(self):
        """
        Test that favorite page uses a correct template
        """
        response = self.client.get(reverse('favorites'))
        self.assertTemplateUsed(response, 'favorites/favorites.html')

    def test_favorite_url_pagination_is_true(self):
        """
        Test that favorite page returns true for pagination
        """
        response = self.client.get(reverse('favorites'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('paginate' in response.context)
        self.assertTrue(response.context['paginate'] is True)

    def test_search_in_fav_url_exists_at_location(self):
        """
        Test that search_in_fav page location returns 200
        """
        response = self.client.get('/users/favorites/search/?user_search=test')
        self.assertEqual(response.status_code, 200)

    def test_search_in_fav_url_by_name(self):
        """
        Test that search_in_fav page name returns 200
        """
        response = self.client.get(reverse('search_fav')+'?user_search=test')
        self.assertEqual(response.status_code, 200)

    def test_bad_search_in_fav_url_returns_404(self):
        """
        Test that a bad research returns 404
        """
        response = self.client.get(reverse('search_fav')+'user_search=test')
        self.assertEqual(response.status_code, 404)

    def test_search_in_fav_pagination_is_true(self):
        """
        Test pagination
        """
        response = self.client.get(reverse('search_fav')+'?user_search=test')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('paginate' in response.context)
        self.assertTrue(response.context['paginate'] is True)

    def test_search_in_fav_url_uses_correct_template(self):
        """
        Test that search_in_fav page uses a correct template
        """
        response = self.client.get(reverse('search_fav')+'?user_search=test')
        self.assertTemplateUsed(response, 'favorites/search_in_fav.html')


class MentionPageTestCase(TestCase):
    """
    Mention page test case
    """

    def test_mentions_url_exists_at_location(self):
        """
        Test that mention page location returns 200
        """
        response = self.client.get('/mentions/')
        self.assertEqual(response.status_code, 200)

    def test_mentions_url_by_name(self):
        """
        Test that mention page name returns 200
        """
        response = self.client.get(reverse('mentions'))
        self.assertEqual(response.status_code, 200)

    def test_mentions_url_uses_correct_template(self):
        """
        Test that mention page uses a correct template
        """
        response = self.client.get(reverse('mentions'))
        self.assertTemplateUsed(response, 'products/mentions.html')


class ResetPasswordPageTestCase(TestCase):
    """
    Reset password page test case
    """

    def test_reset_url_exists_at_location(self):
        """
        Test that reset page location returns 200
        """
        response = self.client.get('/users/password/')
        self.assertEqual(response.status_code, 200)

    def test_reset_url_by_name(self):
        """
        Test that reset page name returns 200
        """
        response = self.client.get(reverse('change_password'))
        self.assertEqual(response.status_code, 200)

    def test_mentions_url_uses_correct_template(self):
        """
        Test that reset page uses a correct template
        """
        response = self.client.get(reverse('change_password'))
        self.assertTemplateUsed(response, 'users/change_password.html')
