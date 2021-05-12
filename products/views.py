from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from random import randrange
from unidecode import unidecode

from .models import Product, Category, Favorite
from .forms import SearchForm


def index(request):
    """
    Used for index page
    """
    form = None
    if request.GET.get(0) is None:
        # Initialize the search form if GET request is empty
        form = SearchForm()
    else:
        # Sends request to search function
        search(request)

    return render(request, 'products/index.html', {'form': form})


def mentions(request):
    """
    Used for mentions page
    """
    return render(request, 'products/mentions.html')


def result(request, product_id):
    """
    Used for result page
    """
    substitutes = []
    current_user = request.user  # Gets current user

    # Gets a product designated by product_id or returns 404
    product = get_object_or_404(Product, pk=product_id)
    # Gets product-related categor(y)(ies)
    category = Category.objects.filter(products__id=product.id)

    all_prods = []
    for catg in category:
        # Get products related to the categor(y)(ies)
        prods = Product.objects.filter(categories__id=catg.id)
        for prod in prods:
            if prod.score <= product.score:
                # Adds products with same or higher score to all_prods list
                all_prods.append(prod)

    nb_prod = 6
    if len(all_prods) < nb_prod:
        nb_prod = len(all_prods)

    for i in range(nb_prod):
        # Randomly selects products(substitutes) whose number is defined
        # by nb_prod. These substitutes are displayed in the page
        this_index = randrange(0, len(all_prods))
        substitutes.append(all_prods.pop(this_index))
        i += 1

    # Gets current user favorites
    qs_fav = Favorite.objects.filter(users__id=current_user.id)
    fav_prods_id = [fav.products.id for fav in qs_fav]
    context = {
        'product': product,
        'substitutes': substitutes,
        'fav_prods_id': fav_prods_id
    }

    return render(request, 'products/result.html', context)


def detail(request, product_id):
    """
    Used for detail page
    """
    # Gets a product designated by product_id or returns 404
    product = get_object_or_404(Product, pk=product_id)

    context = {
        'product': product
    }

    return render(request, 'products/detail.html', context)


def add_fav(request, product_id):
    """
    Used to add products to favorites
    """
    current_user = request.user  # Gets the current user

    # Gets a product designated by product_id or returns 404
    product = get_object_or_404(Product, pk=product_id)

    new_fav = Favorite(
        products=product,
        users=current_user
    )
    # Save the product in Favorite model
    new_fav.save()

    print(product.name + " a été ajouté aux favoris")
    return redirect(request.META['HTTP_REFERER'])


def get_search_result(result_products):
    # Boolean used if query match (True) or not (False)
    this_result = True

    products = result_products
    if not products.exists():
        print('recherche category')
        this_result = False
        # Returns all products from database
        products = Product.objects.all().order_by('id')

    return {
        'products': products,
        'result': this_result
    }


def search(request):
    """
    Used during the search
    """
    # Returns the query in lower case and without accents
    query = unidecode(request.GET.get('search')).lower()

    form = SearchForm(request.GET)
    search_filter = request.GET['search_filter']

    if form.is_valid():
        result_products = None

        if search_filter == 'product':
            # Returns products based on query
            result_products = Product.objects.filter(
                    name__unaccent__icontains=query).order_by('-id')
        elif search_filter == 'category':
            result_products = Product.objects.filter(
                    categories__name__unaccent__icontains=query).order_by('-id')
        elif search_filter == 'brand':
            result_products = Product.objects.filter(
                    brand__unaccent__icontains=query).order_by('-id')
        elif search_filter == 'barcode':
            result_products = Product.objects.filter(
                    barcode__icontains=query).order_by('-id')
        elif search_filter == 'score':
            result_products = Product.objects.filter(
                    score__contains=query).order_by('-id')

        search_result = get_search_result(result_products)
        products = search_result['products']

        # Init pagination with 6 products
        paginator = Paginator(products, 6)
        page = request.GET.get('page')

        try:
            products = paginator.page(page)
        except PageNotAnInteger:
            products = paginator.page(1)
        except EmptyPage:
            products = paginator.page(paginator.num_pages)

        if search_result['result']:
            title = "Résultats de la recherche : {}".format(query)
        else:
            title = "Aucun résultat pour la recherche : {}".format(query)

        context = {
            'is_result': search_result['result'],
            'products': products,
            'title': title,
            'paginate': True,
            'form': form
        }

        return render(request, 'products/search.html', context)

    else:
        print('le formulaire n est pas valide')
        return render(request, 'products/index.html', {'form': form})
