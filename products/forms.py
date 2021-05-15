from django import forms

import re


class SearchForm(forms.Form):
    """
    Class used for the search form

    ...

    Methods
    -------
    clean()
        Returns the search submitted by the user after performing the tests.

    check_product_search()
        Check product search constraints

    check_barcode_search()
        Check barcode search constraints

    check_nutriscore_search()
        Check nutriscore search constraints
    """

    search = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'id': 'id_search',
            'class': 'form-control form-control-lg bg-light',
            'placeholder': 'Rechercher un élément...'
        }),
        required=True
    )

    FILTER_CHOICES = [
        ('product', 'Produit'),
        ('category', 'Catégorie'),
        ('brand', 'Marque'),
        ('barcode', 'Code Barre'),
        ('score', 'Nutriscore')
    ]
    search_filter = forms.CharField(
        widget=forms.Select(
            choices=FILTER_CHOICES,
            attrs={
                'class': 'btn btn-light rounded-left',
            }),
    )

    def check_product_search(self, search, search_filter, filter_value):
        # Check product search constraints

        if search_filter == filter_value:
            # Returns an error if the search length is < 2
            if len(search) < 2:
                self._errors['search'] = self.error_class([
                    'Saisir, au minimum, deux caractères pour valider '
                    'la recherche'
                ])
            # Returns an error if the search contains a number
            if bool(re.search(r"\d", search)):
                self._errors['search'] = self.error_class([
                    'Les chiffres ne sont pas autorisés'
                ])

    def check_barcode_search(self, search, search_filter):
        # Check barcode search constraints

        if search_filter == 'barcode':
            if len(search) < 5:
                self._errors['search'] = self.error_class([
                    "Saisir, au minimum, cinq caractères pour valider "
                    "la recherche d'un code barre"
                ])
            if len(search) > 13:
                self._errors['search'] = self.error_class([
                    "Les codes barres utilisent la norme EAN et ne peuvent "
                    "contenir, au maximum, que 13 caractères "
                    "numériques"
                ])
            if bool(re.search(r"\D", search)):
                self._errors['search'] = self.error_class([
                    "Seuls les chiffres sont autorisés dans un code barre"
                ])

    def check_nutriscore_search(self, search, search_filter):
        # Check nutriscore search constraints

        if search_filter == 'score':
            if len(search) > 1:
                self._errors['search'] = self.error_class([
                    "Un nutriscore n'est composé que d'une seule lettre"
                ])
            elif not bool(re.search(r"\d", search)):
                score_letters = ('A', 'B', 'C', 'D', 'E')
                if str(search).upper() not in score_letters:
                    self._errors['search'] = self.error_class([
                        f"Seuls les caractères suivants sont autorisés dans "
                        f"un nutriscore : {score_letters}"
                    ])

    def clean(self):
        super(SearchForm, self).clean()
        search = self.cleaned_data.get('search')  # Gets search input
        search_filter = self.cleaned_data.get('search_filter')

        # Check all constraints
        self.check_product_search(search, search_filter, 'product')
        self.check_product_search(search, search_filter, 'category')
        self.check_product_search(search, search_filter, 'brand')
        self.check_barcode_search(search, search_filter)
        self.check_nutriscore_search(search, search_filter)

        # Returns an error if the search contains a special char (except quote)
        if bool(re.search(r"([^\w ^'])", search)):
            self._errors['search'] = self.error_class([
                'Les caractères spéciaux ne sont pas autorisés'
            ])

        return search
