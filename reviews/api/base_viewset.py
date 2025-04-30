from rest_framework import filters, mixins, pagination, viewsets

from api.permissions import IsAdminOrReadOnly


class BaseReadOnlyViewSet(
    mixins.CreateModelMixin, mixins.ListModelMixin,
    mixins.DestroyModelMixin, viewsets.GenericViewSet
):
    """
    Базовый ViewSet с доступом только для чтения,
    поддерживающий создание, получение списка и удаление объектов.
    """
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = pagination.LimitOffsetPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
