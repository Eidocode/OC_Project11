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

        # Add 40 products in test database
        number_of_products = 40
        for pnum in range(number_of_products):
            product = Product(
                name=f'Product {pnum}',
                brand=f'Brand {pnum}',
                description='Product Description',
                score='B',
                barcode=f'12345678910 {pnum}',
                url_img_small=f'https://www.off.com/cat/prod/img_small{pnum}',
                url_img=f'https://www.off.com/cat/prod/img{pnum}',
                url_off=f'https://www.off.com/cat/prod/off{pnum}',
                url_img_nutrition=f'https://www.off.com/cat/prod/img_nt{pnum}',
            )
            product.save()
            product.categories.add(category.id)

        products = Product.objects.all()
        # some classe variables
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

    def test_categories(self):
        # Test categories in database
        categories = Category.objects.all()
        self.assertEqual(len(categories), 1)

    def test_products(self):
        # Test products in database
        products = Product.objects.all()
        self.assertEqual(len(products), 40)

    def test_logon_user(self):
        # Test that user is registered
        users = User.objects.all()
        self.assertEqual(len(users), 1)
        self.assertRedirects(self.logon_user, '/')

    def test_account(self):
        # Test account page with logged user
        account_page = self.client.get(reverse('user_account'))
        current_user = account_page.wsgi_request.user
        self.assertEqual(account_page.status_code, 200)
        self.assertEqual(current_user.email, 'test.user4@oc.fr')
        self.assertEqual(current_user.username, 'test_user4')
        self.assertEqual(current_user.first_name, 'test4')
        self.assertEqual(current_user.last_name, 'user4')

    def test_search_product(self):
        # Test to search an available product
        search = self.client.get(reverse('search')+'?search=Product')
        self.assertEqual(search.status_code, 200)
        self.assertTrue(search.context['paginate'] is True)

    def test_result_product(self):
        # Test result page with an existing product
        result = self.client.get(reverse(
                    'result',
                    kwargs={'product_id': self.product_id}
                ))

        self.assertEqual(result.status_code, 200)
        self.assertEqual(len(result.context['substitutes']), 6)

    def test_handles_favorites(self):
        # Test to add, check & remove a product from favorites

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
        # Test detail page with an existing product
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
        # Test to logout current logged user
        logout = self.client.get('/logout/')
        self.assertEqual(logout.status_code, 302)
        self.assertRedirects(logout, '/')
