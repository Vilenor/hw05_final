from django.core.paginator import Paginator


def paginator(request, posts, amount_of_page):
    paginator = Paginator(posts, amount_of_page)
    page_number = request.GET.get('page')
    return (paginator.get_page(page_number))
