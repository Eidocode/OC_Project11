from django.shortcuts import get_object_or_404, redirect, render
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from unidecode import unidecode

from products.models import Favorite


def favorites(request):
    """
    Used when displaying the current user's favorites
    """
    cur_user = request.user  # Gets the current logged-in user
    fav_products = Favorite.objects.all()  # Gets all "Favorite" model objects

    # Gets the favorites of the current user
    fav_prod_filtered = fav_products.filter(users_id=cur_user).order_by('-id')

    # Adds pagination for up to 6 products per page
    paginator = Paginator(fav_prod_filtered, 6)
    page = request.GET.get('page')

    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    context = {
        'favorites': products,
        'paginate': True,
    }
    return render(request, 'favorites/favorites.html', context)


def remove_from_fav(request, favorite_id):
    """
    Used when the user removes a product from his favorites
    """
    # Gets a favorite designated by favorite_id or returns 404
    favorite = get_object_or_404(Favorite, pk=favorite_id)
    favorite.delete()

    print("{}, {} a été supprimé des favoris".format(
                    favorite.products.name, favorite.products.brand))

    return redirect(request.META['HTTP_REFERER'])


def search_in_fav(request):
    """
    Used for favorites search
    """
    query = request.GET.get('user_search')

    if query:
        # Returns the query in lower case and without accents
        query = unidecode(query).lower()
        result = True

        cur_user = request.user
        # Returns all favorites
        favorites = Favorite.objects.all()

        # Returns current user filtered favorites
        fav_filtered = favorites.filter(
            users_id=cur_user
            ).filter(products__name__icontains=query).order_by('id')

        if not fav_filtered.exists():
            result = False
            fav_filtered = favorites.filter(
                users_id=cur_user).order_by('id')

        # Init pagination with 6 products
        paginator = Paginator(fav_filtered, 6)
        page = request.GET.get('page')

        try:
            fav_filtered = paginator.page(page)
        except PageNotAnInteger:
            fav_filtered = paginator.page(1)
        except EmptyPage:
            fav_filtered = paginator.page(paginator.num_pages)

        if result:
            title = "Résultats de la recherche : {}".format(query)
        else:
            title = "Aucun résultat pour la recherche : {}".format(query)

        context = {
                'is_result': result,
                'fav_filtered': fav_filtered,
                'title': title,
                'paginate': True,
            }

        return render(request, 'favorites/search_in_fav.html', context)
