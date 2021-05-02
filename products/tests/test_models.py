from django.test import TestCase

from products.models import Category, Product, Favorite


class CategoryModelTest(TestCase):
    """
        Category Model test case
    """

    @classmethod
    def setUpTestData(cls):
        # Setup non modified objects used for all test methods
        Category.objects.create(
            name='Pates',
            json_id='fr:pates',
            url='https://www.openfoodfacts.com/pates'
        )

    def test_name_max_length(self):
        # Test Category name max length
        category = Category.objects.get(id=1)
        max_length = category._meta.get_field('name').max_length
        self.assertEquals(max_length, 200)

    def test_json_id_label(self):
        # Test Category json id field label
        category = Category.objects.get(id=1)
        field_label = category._meta.get_field('json_id').verbose_name
        self.assertEquals(field_label, 'json id')

    def test_jsonid_max_length(self):
        # Test Category json id max length
        category = Category.objects.get(id=1)
        max_length = category._meta.get_field('json_id').max_length
        self.assertEquals(max_length, 200)

    def test_jsonid_is_unique(self):
        # Test Category json id unicity
        category = Category.objects.get(id=1)
        unique = category._meta.get_field('json_id').unique
        self.assertTrue(unique)

    def test_object_name_is_name(self):
        # Test Category object name
        category = Category.objects.get(id=1)
        object_name = category.name
        self.assertEquals(object_name, str(category))


class ProductModelTest(TestCase):
    """
        Product Model test case
    """

    @classmethod
    def setUpTestData(cls):
        # Setup non modified objects used for all test methods
        Product.objects.create(
            name='Saumon',
            brand='Labeyrie',
            description='Saumon fumé savoureux de Norvege',
            score='C',
            barcode='12345678910',
            url_img_small='https://www.off.com/poisson/saumon/img_small',
            url_img='https://www.off.com/poisson/saumon/img',
            url_off='https://www.off.com/poisson/saumon/',
            url_img_nutrition='https://www.off.com/poisson/saumon/img_nutri',
        )

    def test_name_max_length(self):
        # Test Product name max length
        product = Product.objects.get(id=1)
        max_length = product._meta.get_field('name').max_length
        self.assertEquals(max_length, 200)

    def test_brand_max_length(self):
        # Test Product brand max length
        product = Product.objects.get(id=1)
        max_length = product._meta.get_field('brand').max_length
        self.assertEquals(max_length, 200)

    def test_score_max_length(self):
        # Test Product score max length
        product = Product.objects.get(id=1)
        max_length = product._meta.get_field('score').max_length
        self.assertEquals(max_length, 1)

    def test_barcode_max_length(self):
        # Test Product barcode max length
        product = Product.objects.get(id=1)
        max_length = product._meta.get_field('barcode').max_length
        self.assertEquals(max_length, 50)

    def test_barcode_is_unique(self):
        # Test Product barcode unicity
        product = Product.objects.get(id=1)
        unique = product._meta.get_field('barcode').unique
        self.assertTrue(unique)

    def test_object_name_is_name_brand_barcode(self):
        # Test Product object name
        product = Product.objects.get(id=1)
        object_name = f'{product.name}, {product.brand}, {product.barcode}'
        self.assertEquals(object_name, str(product))


class FavoriteModelTest(TestCase):
    """
        Favorite Model test case
    """

    def test_added_date_autonow(self):
        # Test Favorite added date autonow
        added_date = Favorite._meta.get_field('added_date').auto_now_add
        self.assertTrue(added_date)
