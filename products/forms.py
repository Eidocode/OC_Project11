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
    """

    search = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'id': 'id_search',
            'class': 'form-control form-control-lg bg-light',
            'placeholder': 'Rechercher un produit...'
        }),
        required=True
    )

    def clean(self):
        super(SearchForm, self).clean()
        search = self.cleaned_data.get('search')  # Gets search input

        # Returns an error if the search length is < 2
        if len(search) < 2:
            self._errors['search'] = self.error_class([
                'Saisir, au minimum, deux caractères pour valider la recherche'
            ])

        # Returns an error if the search contains a special char (except quote)
        if bool(re.search(r"([^\w ^'])", search)):
            self._errors['search'] = self.error_class([
                'Les caractères spéciaux ne sont pas autorisés'
            ])

        # Returns an error if the search contains a number
        if bool(re.search(r"\d", search)):
            self._errors['search'] = self.error_class([
                'Les chiffres ne sont pas autorisés'
            ])

        return search
