import time

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from django.contrib.auth.models import User
from django.urls import reverse

from products.models import Category, Product, Favorite


class TestAppIntegration(StaticLiveServerTestCase):
    """
        integration tests of purbeurre app
    """

    def setUp(self):
        time.sleep(1)
        # Initialize driver for chrome
        self.driver = webdriver.Chrome()
        self.driver.maximize_window()

        # Logon new user
        self.logon_user = self.client.post(
                    reverse('signup'),
                    data={
                        'username': 'test_user5',
                        'first_name': 'test5',
                        'last_name': 'user5',
                        'email': 'test.user5@oc.fr',
                        'password1': 'Apass_0404',
                        'password2': 'Apass_0404',
                    })

    def tearDown(self):
        time.sleep(1)
        self.driver.quit()

    def test_homepage(self):
        # Opens homepage & checks the title
        self.driver.get(self.live_server_url)
        self.assertTrue(self.driver.title == "Pur Beurre App'")

    def test_logon_new_user(self):
        # Tests logon user from signup page

        # New user information
        user = {
            'username': "toto",
            'fname': "Toto",
            'lname': "Tutu",
            'email': "Toto.Tutu@oc.fr",
            'password': "motdepasse123",
        }

        self.driver.get(self.live_server_url+'/users/signup/')

        # username
        username_field = self.driver.find_element_by_id("id_username")
        username_field.send_keys(user['username'])

        # First name
        fname_field = self.driver.find_element_by_id("id_first_name")
        fname_field.send_keys(user['fname'])

        # last name
        lname_field = self.driver.find_element_by_id("id_last_name")
        lname_field.send_keys(user['lname'])

        # email
        email_field = self.driver.find_element_by_id("id_email")
        email_field.send_keys(user['email'])

        # password
        pass1_field = self.driver.find_element_by_id("id_password1")
        pass1_field.send_keys(user['password'])

        # confirm password
        pass2_field = self.driver.find_element_by_id("id_password2")
        pass2_field.send_keys(user['password'])

        # submit information
        time.sleep(1)
        submit = self.driver.find_element_by_id('logon_btn')
        submit.send_keys(Keys.RETURN)

        # Checks objects in User table
        users = User.objects.all()
        self.assertEqual(len(users), 2)  # must returns 2
        # Logon successful redirection
        self.assertEqual(self.driver.current_url, self.live_server_url+'/')

    def login(self):
        # Method for login user

        self.driver.get(self.live_server_url + '/login/')

        # username
        username_field = self.driver.find_element_by_id("id_username")
        username_field.send_keys("test_user5")

        # password
        username_field = self.driver.find_element_by_id("id_password")
        username_field.send_keys("Apass_0404")

        # submit login information
        time.sleep(1)
        submit = self.driver.find_element_by_id('login_btn')
        submit.send_keys(Keys.RETURN)

    def test_login_user(self):
        # Tests login user from signin page

        # Uses login method
        self.login()
        # Checks login successful redirection
        self.assertEqual(self.driver.current_url, self.live_server_url+'/')

        # Checks that search button is enabled (only when a user is logged in)
        time.sleep(1)
        btn = self.driver.find_element_by_id("send_btn")
        self.assertTrue(btn.is_enabled())

    def test_user_account_page(self):
        # Test user account page

        self.login()  # Login user
        # account page
        self.driver.get(self.live_server_url + '/users/account/')
        time.sleep(1)
        self.assertEqual(self.driver.current_url,
                         self.live_server_url + '/users/account/')

    def test_change_user_password_button(self):
        # Test change password button

        self.login()  # Login user
        # account page
        self.driver.get(self.live_server_url + '/users/account/')
        # change password button
        self.driver.find_element_by_id("reset_btn").send_keys(Keys.RETURN)
        time.sleep(1)
        self.assertEqual(self.driver.current_url,
                         self.live_server_url + '/users/password/')

    def test_failure_change_user_password(self):
        # Test case failure for change password

        self.login()  # Login user
        # password page
        self.driver.get(self.live_server_url + '/users/password/')

        # Passwords
        ids = {
            'id_old_password': 'a_password',
            'id_new_password1': 'new_Apass_0404',
            'id_new_password2': 'new_Apass_0404',
        }
        for key, value in ids.items():
            # Adding passwords to fields
            field = self.driver.find_element_by_id(key)
            field.send_keys(value)
        # Save button
        save_pwd_button = self.driver.find_element_by_id("rst_pwd_btn")
        save_pwd_button.send_keys(Keys.RETURN)
        time.sleep(1)
        self.assertEqual(self.driver.current_url,
                         self.live_server_url + '/users/password/')

    def test_success_change_user_password(self):
        # Test case success for change password

        self.login()  # Login user
        # account page
        self.driver.get(self.live_server_url + '/users/account/')
        # change password button
        self.driver.find_element_by_id("reset_btn").send_keys(Keys.RETURN)
        time.sleep(1)
        self.assertEqual(self.driver.current_url,
                         self.live_server_url + '/users/password/')

        # Passwords
        ids = {
            'id_old_password': 'Apass_0404',
            'id_new_password1': 'new_Apass_0404',
            'id_new_password2': 'new_Apass_0404',
        }
        for key, value in ids.items():
            # Adding passwords to fields
            field = self.driver.find_element_by_id(key)
            field.send_keys(value)
        # Save button
        save_pwd_button = self.driver.find_element_by_id("rst_pwd_btn")
        save_pwd_button.send_keys(Keys.RETURN)
        time.sleep(1)
        self.assertEqual(self.driver.current_url,
                         self.live_server_url + '/users/account/')

    @staticmethod
    def add_to_db():
        # Method used to add new items to database

        # Adds 1 category in test database
        category = Category(
            name='Category2',
            json_id='fr:category2',
            url='https://www.openfoodfacts.com/category2',
        )
        category.save()

        # Add a product in test database
        number_of_products = 1
        for pnum in range(number_of_products):
            num = 100 + pnum
            product = Product(
                name=f'Product {num}',
                brand=f'Brand {num}',
                description='Product Description',
                score='B',
                barcode=f'12345678910 {num}',
                url_img_small=f'https://www.off.com/cat/prod/img_small{num}',
                url_img=f'https://www.off.com/cat/prod/img{num}',
                url_off=f'https://www.off.com/cat/prod/off{num}',
                url_img_nutrition=f'https://www.off.com/cat/prod/img_nt{num}',
            )
            product.save()
            product.categories.add(category.id)

    def test_search_product_and_favorites(self):
        # Tests search product, search page, result page and favorites

        # Login a user & add elements to database
        self.login()
        self.add_to_db()

        # search a product
        search_field = self.driver.find_element_by_id('id_search')
        search_field.send_keys("Product")
        time.sleep(1)
        submit = self.driver.find_element_by_id('send_btn')
        submit.send_keys(Keys.RETURN)  # Submit research
        # Checks products in db & result page
        products = Product.objects.all()
        self.assertEqual(len(products), 1)
        search_link = '/products/search/?search_filter=product&search=Product'
        self.assertEqual(
            self.driver.current_url,
            self.live_server_url + search_link
        )

        # Test product result page
        p_url = '/products/' + str(products[0].id) + '/'
        time.sleep(1)
        self.driver.get(self.live_server_url + p_url)
        # Click on first save button (favorite)
        save = self.driver.find_element_by_id("save1")
        save.send_keys(Keys.RETURN)

        # Test favorites result page
        self.driver.find_element_by_xpath('//*[@title="Mes aliments"]').click()
        time.sleep(1)
        self.assertEqual(
            self.driver.current_url,
            self.live_server_url+'/users/favorites/'
        )
        # Checks favorites in database (must return 1)
        favorites = Favorite.objects.all()
        self.assertEqual(len(favorites), 1)
        # Click on first remove button (favorite)
        del_elem = self.driver.find_element_by_id("delete1")
        del_elem.send_keys(Keys.RETURN)
        # Checks favorites in database (must return 2)
        favorites = Favorite.objects.all()
        self.assertEqual(len(favorites), 0)

    def test_filter_search_category(self):
        # Tests search category

        # Login a user & add elements to database
        self.login()
        self.add_to_db()
        # search a product
        self.driver.find_element_by_xpath(
            "//select[@name='search_filter']"
            "/option[text()='Catégorie']").click()
        search_field = self.driver.find_element_by_id('id_search')
        search_field.send_keys("Category")
        time.sleep(1)
        submit = self.driver.find_element_by_id('send_btn')
        submit.send_keys(Keys.RETURN)  # Submit research
        # Check result page
        search_link = '/products/search/?search_filter=category&search=Category'
        self.assertEqual(
            self.driver.current_url,
            self.live_server_url + search_link
        )

    def test_filter_search_brand(self):
        # Tests search brand

        # Login a user & add elements to database
        self.login()
        self.add_to_db()
        # search a brand
        self.driver.find_element_by_xpath("//select[@name='search_filter']"
                                          "/option[text()='Marque']").click()
        search_field = self.driver.find_element_by_id('id_search')
        search_field.send_keys("Brand")
        time.sleep(1)
        submit = self.driver.find_element_by_id('send_btn')
        submit.send_keys(Keys.RETURN)  # Submit research
        # Check result page
        search_link = '/products/search/?search_filter=brand&search=Brand'
        self.assertEqual(
            self.driver.current_url,
            self.live_server_url + search_link
        )

    def test_category_search_with_special_char(self):
        # Tests search category with a special char. Must fail
        # Same for all other research

        # Login a user & add elements to database
        self.login()
        self.add_to_db()
        # search a category
        self.driver.find_element_by_xpath(
            "//select[@name='search_filter']"
            "/option[text()='Catégorie']").click()
        search_field = self.driver.find_element_by_id('id_search')
        search_field.send_keys("Category@")
        time.sleep(1)
        submit = self.driver.find_element_by_id('send_btn')
        submit.send_keys(Keys.RETURN)  # Submit research
        # Check error message
        result = self.driver.find_element_by_id("form_error").text
        self.assertEqual(
            result,
            "Les caractères spéciaux ne sont pas autorisés"
        )

    def test_brand_search_with_one_char(self):
        # Tests search brand with only one char. Must fail
        # Same for product and category research

        # Login a user & add elements to database
        self.login()
        self.add_to_db()
        # search a category
        self.driver.find_element_by_xpath("//select[@name='search_filter']"
                                          "/option[text()='Marque']").click()
        search_field = self.driver.find_element_by_id('id_search')
        search_field.send_keys("M")
        time.sleep(1)
        submit = self.driver.find_element_by_id('send_btn')
        submit.send_keys(Keys.RETURN)  # Submit research
        # Check error message
        result = self.driver.find_element_by_id("form_error").text
        self.assertEqual(
            result,
            "Saisir, au minimum, deux caractères pour valider la recherche"
        )

    def test_barcode_search_with_letters(self):
        # Tests search barcode with letters. Must fail

        # Login a user & add elements to database
        self.login()
        self.add_to_db()
        # search a category
        self.driver.find_element_by_xpath("//select[@name='search_filter']"
                                          "/option"
                                          "[text()='Code-Barres']").click()
        search_field = self.driver.find_element_by_id('id_search')
        search_field.send_keys("12453JDS")
        time.sleep(1)
        submit = self.driver.find_element_by_id('send_btn')
        submit.send_keys(Keys.RETURN)  # Submit research
        # Check error message
        result = self.driver.find_element_by_id("form_error").text
        self.assertEqual(
            result,
            "Seuls les chiffres sont autorisés dans un code-barres"
        )

    def test_nutriscore_search_with_two_letters(self):
        # Tests search nutriscore with two letters. Must fail

        # Login a user & add elements to database
        self.login()
        self.add_to_db()
        # search a category
        self.driver.find_element_by_xpath("//select[@name='search_filter']"
                                          "/option"
                                          "[text()='Nutriscore']").click()
        search_field = self.driver.find_element_by_id('id_search')
        search_field.send_keys("AB")
        time.sleep(1)
        submit = self.driver.find_element_by_id('send_btn')
        submit.send_keys(Keys.RETURN)  # Submit research
        # Check error message
        result = self.driver.find_element_by_id("form_error").text
        self.assertEqual(
            result,
            "Un nutriscore n'est composé que d'une seule lettre"
        )

    def test_filter_search_barcode(self):
        # Tests search barcode

        # Login a user & add elements to database
        self.login()
        self.add_to_db()
        # search a brand
        self.driver.find_element_by_xpath("//select[@name='search_filter']"
                                          "/option"
                                          "[text()='Code-Barres']").click()
        search_field = self.driver.find_element_by_id('id_search')
        search_field.send_keys("12345678910")
        time.sleep(1)
        submit = self.driver.find_element_by_id('send_btn')
        submit.send_keys(Keys.RETURN)  # Submit research
        # Check result page
        search_link = "/products/search/?search_filter=" \
                      "barcode&search=12345678910"
        self.assertEqual(
            self.driver.current_url,
            self.live_server_url + search_link
        )

    def test_filter_search_nutriscore(self):
        # Tests search nutriscore

        # Login a user & add elements to database
        self.login()
        self.add_to_db()
        # search a nutriscore
        self.driver.find_element_by_xpath("//select[@name='search_filter']"
                                          "/option"
                                          "[text()='Nutriscore']").click()
        search_field = self.driver.find_element_by_id('id_search')
        search_field.send_keys("B")
        time.sleep(1)
        submit = self.driver.find_element_by_id('send_btn')
        submit.send_keys(Keys.RETURN)  # Submit research
        # Check result page
        search_link = '/products/search/?search_filter=score&search=B'
        self.assertEqual(
            self.driver.current_url,
            self.live_server_url + search_link
        )

    def test_logout_user(self):
        # Tests logout user

        # Login user
        self.login()

        # identifies disconnect icon
        self.driver.find_element_by_xpath('//*[@title="Déconnexion"]').click()
        time.sleep(1)

        # Checks that search button is disabled (only when no user's logged in)
        btn = self.driver.find_element_by_id("send_btn")
        self.assertFalse(btn.is_enabled())
