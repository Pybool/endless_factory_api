from collections import OrderedDict

from rest_framework import pagination
from rest_framework.response import Response
from rest_framework.utils.urls import replace_query_param, remove_query_param
from rest_framework.pagination import LimitOffsetPagination

class CustomPaginatorClass(object):
    
    def __init__(self,paginationclass,request):
        
        self.pagination_class = paginationclass
        self.request = request
        self.use_envelope = True
        
    @property
    def paginator(self):
       
        if not hasattr(self, '_paginator'):
            if self.pagination_class is None:
                self._paginator = None
            else:
                self._paginator = self.pagination_class()
        return self._paginator

    def paginate_queryset(self, queryset):
     
        if self.paginator is None:
            return None
        return self.paginator.paginate_queryset(queryset, self.request, view=self)

    # def get_paginated_response(self, data):
    
    #     assert self.paginator is not None
    #     # self.paginator.last_url = self.get_last_link()
    #     return self.paginator.get_paginated_response(data)
    
    def get_paginated_response(self, data):
        next_url = self.paginator.get_next_link()
        previous_url = self.paginator.get_previous_link()
        first_url = self.get_first_link()
        last_url = self.get_last_link()

        links = []
        for label, url in (
            ('first', first_url),
            ('next', next_url),
            ('previous', previous_url),
            ('last', last_url),
        ):
            if url is not None:
                links.append('<{}>; rel="{}"'.format(url, label))

        headers = {'Link': ', '.join(links)} if links else {}
        headers['x-total-count'] = self.paginator.count

        if self.use_envelope:
            return Response(OrderedDict([
                ('count', self.paginator.count),
                ('first', first_url),
                ('next', next_url),
                ('previous', previous_url),
                ('last', last_url),
                ('results', data)
            ]), headers=headers)
        return Response(data, headers=headers)

    def get_first_link(self):
        if self.paginator.offset <= 0:
            return None
        url = self.paginator.request.build_absolute_uri()
        return remove_query_param(url, self.paginator.offset_query_param)

    def get_last_link(self):
        if self.paginator.offset + self.paginator.limit >= self.paginator.count:
            return None
        url = self.paginator.request.build_absolute_uri()
        url = replace_query_param(url, self.paginator.limit_query_param, self.paginator.limit)
        offset = self.paginator.count - self.paginator.limit
        return replace_query_param(url, self.paginator.offset_query_param, offset)



