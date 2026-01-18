from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class MaterialsPagination(PageNumberPagination):
    """
    Кастомный пагинатор для материалов (курсов и уроков).
    """
    page_size = 10  # Количество элементов на странице по умолчанию
    page_size_query_param = 'page_size'  # Параметр для изменения размера страницы
    max_page_size = 50  # Максимальное количество элементов на странице

    def get_paginated_response(self, data):
        """
        Форматируем ответ с пагинацией.
        """
        current_page_size = self.get_page_size(self.request)

        return Response({
            'pagination': {
                'count': self.page.paginator.count,
                'total_pages': self.page.paginator.num_pages,
                'current_page': self.page.number,
                'page_size': current_page_size,
                'has_next': self.page.has_next(),
                'has_previous': self.page.has_previous(),
            },
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link(),
            },
            'results': data
        })


class SmallPagination(PageNumberPagination):
    """
    Пагинатор для небольших списков.
    """
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 20


class LargePagination(PageNumberPagination):
    """
    Пагинатор для больших списков.
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
