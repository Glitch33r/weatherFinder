from dal import autocomplete
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.views.generic.edit import FormView

from portal.forms import CityFindForm
from portal.models import City, Weather
from portal.weather import WeatherFinder


class CityAutocomplete(autocomplete.Select2QuerySetView):
    create_field = 'name'

    def has_add_permission(self, request):
        return True

    def get_queryset(self):
        qs = City.objects.all()
        if self.q:
            qs = qs.filter(name__istartswith=self.q)
        return qs


class IndexView(FormView):
    template_name = 'index.html'
    form_class = CityFindForm


def helper_for_pagination(request, p: Paginator):
    page = request.GET.get('page')

    try:
        data = p.page(page)
    except PageNotAnInteger:
        data = p.page(1)
    except EmptyPage:
        data = p.page(p.num_pages)
    return data


def submit_find_weather(request):
    if request.is_ajax():
        city = request.POST['name']
        finder = WeatherFinder('3d01e07938359060ded56bac02e4224a', city, City, Weather)
        result = finder.get_weather()
        if result:
            return JsonResponse({'status': True, 'msg': 'Founded!'})
        else:
            return JsonResponse({'status': False, 'msg': 'City not found! Try again!'})
    else:
        return JsonResponse({'status': False, 'msg': 'Bad request'})


def result_view(request):
    SEARCH_QUERY = """
        SELECT w.*
        FROM portal_weather AS w
                 INNER JOIN portal_city AS c ON w.city_id= c.id
        WHERE c.name LIKE '%{}%'
        ORDER BY w.city_id ASC, w.date ASC
    """
    FILTER_DATE_QUERY = """
        SELECT w.*
        FROM portal_weather AS w
                 INNER JOIN portal_city AS c ON w.city_id= c.id
        {}
        ORDER BY w.city_id ASC, w.date ASC
    """

    MAX_DATE_QUERY = """
        SELECT id, MAX(date) as max_date
        FROM portal_weather
    """
    MIN_DATE_QUERY = """
        SELECT id, MIN(date) as min_date
        FROM portal_weather
    """

    object_list = Weather.objects.all()
    data = helper_for_pagination(request, Paginator(object_list, 10))

    if request.is_ajax():
        if request.GET.get('search'):
            text_to_search = request.GET.get('search')

            return JsonResponse(
                {
                    'type': 'search',
                    'response': render_to_string('element.html', {
                        'object_list': Weather.objects.raw(SEARCH_QUERY.format(text_to_search))
                    })
                }
            )
        elif request.GET.get('type'):
            import json

            filter_data = request.GET.dict()
            filter_data = json.loads(filter_data["data"])
            city_name = filter_data[0]['value']
            date_from = filter_data[1]['value'] if filter_data[1]['value'] != '' else Weather.objects.raw(MIN_DATE_QUERY, translations={'max_date': 'date'})[0].date
            date_to = filter_data[2]['value'] if filter_data[2]['value'] != '' else Weather.objects.raw(MAX_DATE_QUERY, translations={'max_date': 'date'})[0].date

            part = "WHERE w.date BETWEEN '{}' AND '{}'".format(date_from, date_to)
            if city_name != '':
                part += "AND c.name LIKE '%{}%'".format(city_name)

            return JsonResponse(
                {
                    'response': render_to_string('element.html', {
                        'object_list': Weather.objects.raw(FILTER_DATE_QUERY.format(part))
                    })
                }
            )
        else:
            data = helper_for_pagination(request, Paginator(object_list, 10))
            return JsonResponse(
                {
                    'type': 'default',
                    'response': render_to_string('element.html', {'object_list': data})
                }
            )

    return render(request, 'result_list.html', {'object_list': data})
