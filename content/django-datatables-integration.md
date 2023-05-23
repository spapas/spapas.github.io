Title: Simple Django - DataTables integration
Date: 2023-05-23 13:20
Tags: python, django, jquery, datatables
Category: django
Slug: simple-django-datatables-integration
Author: Serafeim Papastefanos
Summary: Integration of jquery DataTables with Django 

In this small post I'll show a simple and quick way to integrate 
the [jquery DataTables library](https://datatables.net/) with Django.

The DataTables library has a lot of features however in this article we'll only
take advantage of the basic features that should be enough for most use cases:

* Ajax loading of data
* Ajax pagination
* Ajax search/filtering

If you want to use more features you can try a django package like
[django-ajax-datatable](https://github.com/morlandi/django-ajax-datatable) that 
supports most of the DataTables features; however because of the DataTables complexity you'll see that it will need a lot of work even for a simple integration.

The following model will be used for our example:

```python
class Item(models.Model):
    code = models.CharField(max_length=16, unique=True, )
    name = models.CharField(max_length=512, )
    name_en = models.CharField(max_length=512, )
```

We'll create a Django class based view that will return a template with an empty `<table>` element that we'll then fill with Ajax. The same view will check if it receives datatables requests and return the correct data in the format datatables expects:

```python
from django.db.models import Q
from django.http import JsonResponse
from django.views.generic import ListView

class ItemListView(ListView):
    model = models.Item
    template_name = "item_datatable.html"

    def render_to_response(self, context, **response_kwargs):
        if self.request.GET.get("datatables"):
            draw = int(self.request.GET.get("draw", "1"))
            length = int(self.request.GET.get("length", "10"))
            start = int(self.request.GET.get("start", "0"))
            sv = self.request.GET.get("search[value]", None)
            qs = self.get_queryset().order_by("code")
            if sv:
                qs = qs.filter(
                    Q(name__icontains=sv)
                    | Q(code__icontains=sv)
                    | Q(name_en__icontains=sv)
                )
            filtered_count = qs.count()
            qs = qs[start : start + length]

            return JsonResponse(
                {
                    "recordsTotal": self.get_queryset().count(),
                    "recordsFiltered": filtered_count,
                    "draw": draw,
                    "data": list(qs.values()),
                },
                safe=False,
            )
        return super().render_to_response(context, **response_kwargs)
```

The above is a simple `ListView` for our `Item` model. It overrides the `render_to_response` method to return the Ajax json data if the request is a datatables request. To do that, it first checks to see if there's a `datatables` parameter in the `request.GET`. If this isn't a datatables request it will return the normal template response.

However, if it is a datatables request it will pick the 
`draw`, 
`length`, `start` and `search[value]` parameters from the `request.GET` (with default values if they aren't there) and use them to prepare the response. Notice that:

* for the filter we need to do an `OR (|)` because of how the datatables default fildering works (one single filter field for all columns)
* we can select any of the fields we want to filter with by adding them to the `OR` expression
* we'll choose the correct page using qs[start:start+length], the length will be changed if the user uses the page-size field of the datatables
* we need to count the filtered results *before* taking the slice or else Django will throw an error
* the `draw` parameter should be converted to integer and passed back to the response (it is used in case there are multiple pending datatable ajax requests).

Finally, we return a `JsonResponse` with the correct data. The `safe=False` is needed because we are returning a list of dictionaries and not a single dictionary. Notice the `recordsTotal` and `recordsFiltered` keys; these are needed by datatables to know how many records there are in total and how many records are returned after filtering.

The `item_datatable.html` template for this view is the following: 

```html
{% extends "site_base.html" %}
{% load static %}

{% block extra_style %}
    <link rel="stylesheet" type="text/css" href="{% static 'datatables.min.css' %}"/>
{% endblock %}

{% block page_content %}

<div class="row">
    <div class="col-md-12">
        <table id='table' class='table'></table>
    </div>
</div>

{% endblock %}

{% block extra_script %}
<script type="text/javascript" src="{% static 'jquery.min.js' %}"></script>
<script type="text/javascript" src="{% static 'datatables.min.js' %}"></script>

<script>
$(function() {
  
  $('#table').DataTable( {
        "ordering": false,
        ajax: '{{ request.path }}?datatables=1',
        serverSide: true,
        columns: [
            { data: 'code', title: 'Κωδικός' },
            { data: 'name', title: 'Περιγραφή' },
            { data: 'name_en', title: 'Περιγραφή (αγγλικά)' },
        ],
        language: {
          "sDecimal":           ",",
          "sEmptyTable":        "Δεν υπάρχουν δεδομένα στον πίνακα",
          "sInfo":              "Εμφανίζονται _START_ έως _END_ από _TOTAL_ εγγραφές",
          "sInfoEmpty":         "Εμφανίζονται 0 έως 0 από 0 εγγραφές",
          "sInfoFiltered":      "(φιλτραρισμένες από _MAX_ συνολικά εγγραφές)",
          "sInfoPostFix":       "",
          "sInfoThousands":     ".",
          "sLengthMenu":        "Δείξε _MENU_ εγγραφές",
          "sLoadingRecords":    "Φόρτωση...",
          "sProcessing":        "Επεξεργασία...",
          "sSearch":            "Αναζήτηση:",
          "sSearchPlaceholder": "Αναζήτηση",
          "sThousands":         ".",
          "sUrl":               "",
          "sZeroRecords":       "Δεν βρέθηκαν εγγραφές που να ταιριάζουν",
          "oPaginate": {
              "sFirst":    "Πρώτη",
              "sPrevious": "Προηγούμενη",
              "sNext":     "Επόμενη",
              "sLast":     "Τελευταία"
          },
          "oAria": {
              "sSortAscending":  ": ενεργοποιήστε για αύξουσα ταξινόμηση της στήλης",
              "sSortDescending": ": ενεργοποιήστε για φθίνουσα ταξινόμηση της στήλης"
          }
      }
    } );
})
</script>
{% endblock %}
```

(Please ignore the `language` setting this is needed to translate the datatables messages to greek.)

The important part is that we add the jquery and datatable dependencies (remeber that datatables also has a css) and then add an empty table (`<table class='table'></table>`). Finally, after the page is loaded the table is initialized as datatable using
`$('table.table').DataTable(options)`.

The options we pass to enable the ajax functionality are:

```js
{
    ordering: false,
    ajax: '{{ request.path }}?datatables=1',
    serverSide: true,
    columns: [
        { data: 'code', title: 'Κωδικός' },
        { data: 'name', title: 'Περιγραφή' },
        { data: 'name_en', title: 'Περιγραφή (αγγλικά)' },
    ]
}
```

I didn't need ordering so I haven't implemented it here however it would be possible to implement it by picking the order-related parameters from the request similar to the filtering and using them as `order_by` parameters to the queryset, see the `order[i][column]` and `order[i][dir]` [here](https://datatables.net/manual/server-side).

For the response, we use the current request url passing it the `datatables=1` parameter as discussed before. We define the datatable columns using the `columns` attr; the `data` key is the name of the field in the json data returned by the server and the `title` is the title of the column. These columns must exist in the json data returned by the server.

Finally, we need to add the view to our urls.py:

```python
    path(
        "item_datatable/",
        ItemListListView.as_view(),
        name="item_datatable",
    ),
```

The above is enough to have a working datatable with ajax loading and filtering in your Django list views.