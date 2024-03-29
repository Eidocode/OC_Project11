from django.test import TestCase

from products.forms import SearchForm


class SearchFormTest(TestCase):
    """
        SearchForm test case
    """

    def test_search_form_field_label(self):
        """
        Test label
        """
        form = SearchForm()
        self.assertTrue(form.fields['search'].label is None)

    def test_search_form_max_length(self):
        """
        Test form field max length
        """
        form = SearchForm()
        max_length = form.fields['search'].max_length
        self.assertEquals(max_length, 30)

    def test_search_form_is_required(self):
        """
        Test form required restriction
        """
        form = SearchForm()
        required = form.fields['search'].required
        self.assertTrue(required)

    def test_search_form_widget_attrs_class(self):
        """
        Test form class attributes
        """
        form = SearchForm()
        attr = form.fields['search'].widget.attrs['class']
        self.assertEquals(attr, 'form-control form-control-lg bg-light')

    def test_search_form_widget_attrs_placeholder(self):
        """
        Test form Placeholder value
        """
        form = SearchForm()
        attr = form.fields['search'].widget.attrs['placeholder']
        self.assertEquals(attr, 'Rechercher un élément...')

    def test_search_filter_form_widget_attrs_class(self):
        """
        Test form class attributes (search_filter)
        """
        form = SearchForm()
        attr = form.fields['search_filter'].widget.attrs['class']
        self.assertEquals(attr, 'btn btn-light rounded-left')

    def test_search_filter_form_filter_choices(self):
        """
        Test form choices attributes (search_filter)
        """
        form = SearchForm()
        attr = form.fields['search_filter'].widget.choices
        filter_choices = [
            ('product', 'Produit'),
            ('category', 'Catégorie'),
            ('brand', 'Marque'),
            ('barcode', 'Code-Barres'),
            ('score', 'Nutriscore')
        ]
        for i, item in enumerate(attr):
            self.assertEquals(item, filter_choices[i])
