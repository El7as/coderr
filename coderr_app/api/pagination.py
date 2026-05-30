from rest_framework.pagination import PageNumberPagination



class OfferPagination(PageNumberPagination):

    """
    Custom pagination class for Offer listings.

    This pagination returns 5 items per page and extends the default
    DRF PageNumberPagination. Additional aggregated fields such as
    min_price, min_delivery_time, and user_details can be added in
    the view or overridden in this class if needed.
    """
        
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 50

