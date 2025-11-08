from rest_framework import pagination


class HabitPagination(pagination.PageNumberPagination):
    """
    Пагинация для списка привычек.

    page_size (int): количество привычек на странице по умолчанию.
    page_size_query_param (str): имя параметра запроса для ручной установки размера страницы.
    max_page_size (int): максимальное допустимое количество привычек на страницу.
    """

    page_size = 5
    page_size_query_param = "page_size"
    max_page_size = 100
