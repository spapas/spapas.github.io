Splitting a query into individual fields in Django
##################################################

:date: 2016-09-12 16:20
:tags: django, python, query, q, filter
:category: django
:slug: django-split-query
:author: Serafeim Papastefanos
:summary: How to split a query containing spaces into individual model fields

As you should have already seen in `previous articles <{filename}/django-dynamic-table.rst>`_, I really like using django-filter_ since it covers (nearly) all my queryset filtering needs.
With django-filter, you define a bunch of fields and it will automatically create inputs for each one of these fields so that you can filter by each one of these fields individually or a
combination of them.

However, one thing that django-filter (and django in generally) lacks is the ability to *filter multiple fields using a single input*. This functionality may be familiar to some readers from
the datatable_ jquery plugin. If you take a look at the example in the datatable homepage, you'll see a single "Search" field. What is really great is that you can enter multiple values (seperated
by spaces) into that field and it will filter the individual table values by each one of them. For example, if you enter "2011 Engineer" you'll see all engineering positions that started
on 2011. If you append "Singapore" (so you'll have "2011 Engineer Singapore") you'll also get only the corresponding results!

This functionality is really useful and is very important to have if you use single-input fields to query your data. One such example is if you use autocompletes, for example with
django-autocomplete-light: You'll have a single input however you may need to filter on more than one field to find out your selection.

In the following ost I'll show you how to implement this functionality using Django and django-filters (actually django-filters will be used to provide the form) - to see it
in action you may use the https://github.com/spapas/django_table_filtering repository (check out the `/filter_ex/` view).

I won't go into detail on how the code is structured (it's really simple) and I'll go directly to the filter I am using. Instead of using a filter you can of course directly query on
your view. What you actually need is:

    - a queryset with the instances you want to search
    - a text value with the query (that may contain spaces)
    - a list of the names of the fields you want to search

In my case, I am using a `Book` model that has the following fields: `id, title, author, category`. I have created a filter with a single field named `ex` that will filter on
all these fields. So you should be able to enter "King It" and find "It by Stephen King". Let's see how the filter is implemented:

.. code::

    import itertools

    class BookFilterEx(django_filters.FilterSet):
        ex = django_filters.MethodFilter()
        search_fields = ['title', 'author', 'category', 'id', ]

        def filter_ex(self, qs, value):
            if value:
                q_parts = value.split()

                # Permutation code copied from http://stackoverflow.com/a/12935562/119071

                list1=self.search_fields
                list2=q_parts
                perms = [zip(x,list2) for x in itertools.permutations(list1,len(list2))]

                q_totals = Q()
                for perm in perms:
                    q_part = Q()
                    for p in perm:
                        q_part = q_part & Q(**{p[0]+'__icontains': p[1]})
                    q_totals = q_totals | q_part

                qs = qs.filter(q_totals)
            return qs

        class Meta:
            model = books.models.Book
            fields = ['ex']

The meat of this code is in the ``filter_ex`` method, let's analyze it line by line:
First of all, we split the value to its corresponding parts using the whitespace to sperate into individual tokens. For example if the user has entered
``King It``, ``q_parts`` be equal to ``['King', 'It']``. As you can see the `search_fields` attribute contains the names of the
fields we want to search. The first thing I like to do is to generate all possible combinations between ``q_parts``
and ``search_fields``, I've copied the list combination code from http://stackoverflow.com/a/12935562/119071 and it is the line
``perms = [zip(x,list2) for x in itertools.permutations(list1,len(list2))]``.

The ``itertools.permutations(list1,len(list2))`` will generate all permutations of list1
that have length equal to the length of list2. I.e if list2 is ``['King', 'It']`` (len=2) then it will generate all combinations
of search_fields with length=2, i.e it will generate the following list of tuples:

.. code::

    [
        ('title', 'author'), ('title', 'category'), ('title', 'id'), ('author', 'title'),
        ('author', 'category'), ('author', 'id'), ('category', 'title'), ('category', 'author'),
        ('category', 'id'), ('id', 'title'), ('id', 'author'), ('id', 'category')
    ]

Now, the ``zip`` will combine the elements of each one of these tuples with the elements of ``list2``, so, in our example
(``list2=['King', 'It']``) ``perms`` will be the following array:

.. code::

    [
        [('title', 'King'), ('author', 'It')],
        [('title', 'King'), ('category', 'It')],
        [('title', 'King'), ('id', 'It')],
        [('author', 'King'), ('title', 'It')],
        [('author', 'King'), ('category', 'It')],
        [('author', 'King'), ('id', 'It')],
        [('category', 'King'), ('title', 'It')],
        [('category', 'King'), ('author', 'It')],
        [('category', 'King'), ('id', 'It')],
        [('id', 'King'), ('title', 'It')],
        [('id', 'King'), ('author', 'It')],
        [('id', 'King'), ('category', 'It')]
    ]

Notice that ``itertools.permutations(list1,len(list2))`` will return an empty list if ``len(list2) > len(list1)`` - this is actually what
we want since that means that the user entered more query parts than the available fields, i.e we can't match each one of the
possible values after we split the input with a search field so we should return nothing.


Now, what I want is to create a single query that will combine the tuples in each of these combinations by AND (i.e
``title==King AND author==It`` ) and then combine all these subqueries using OR (i.e
`` (title==King AND author==It) OR (title==King AND category==It) OR (title==King AND id==It) OR ...``.

This could of course be implemented with a raw sql query however we could use some interesting django tricks for this. 
I've already done something similar to `a previous article <{filename}/django-dynamic-table.rst>`_ so I won't go
into much detail explaining the code that creates the ``q_totals`` ``Q`` object. What it does is that it create a big django ``Q`` object that combines using AND (``&``)
all individual ``q_part`` objects. Each ``q_part`` object combines using OR (``|``) the individual combinations of field name
and value -- I've used `__icontains`` to create the query. So the result will be something like this:

.. code::

    q_totals =
        Q(title__icontains='King') & Q(author__icontains='It')
        |
        Q(title__icontains='King') & Q(category__icontains='It')
        |
        Q(title__icontains='King') & Q(id__icontains='It')
        |
        Q(author__icontains='King') & Q(title__icontains='It')
        ...

Filtering by this ``q_totals`` will return the correct values!

One extra complication we should be aware of is what happens if the user needs to also search for books with multiple words
in their titles. For example, if the user enters "Under the Dome King" or "It Stephen King" or even "The Stand Stephen King"
we won't get any results :(

To fix this, we need to get all possible combinations of sequential substrings, i.e for "Under the Dome King", after we
split it to ['Under', 'the', 'Dome', 'King'] we'll need the following combinations:

.. code::

    [
        ['Under', 'the', 'Dome', 'King'],
        ['Under', 'the', 'Dome King'],
        ['Under', 'the Dome', 'King'],
        ['Under', 'the Dome King'],
        ['Under the', 'Dome', 'King'],
        ['Under the', 'Dome King'],
        ['Under the Dome', 'King'],
        ['Under the Dome King']
    ]

A possible solution for that problem can be found on this SO answer: http://stackoverflow.com/a/27263616/119071.

Now, to extend our solution to include this, we'd need to actually search for each one of the above possiblities
and combine again the results with OR, something like this:

.. code::

    def filter_ex(self, qs, value):
        if value:
            q_parts = value.split()

            # Use a global q_totals
            q_totals = Q()

            # This part will get us all possible segmantiation of the query parts and put it in the possibilities list
            combinatorics = itertools.product([True, False], repeat=len(q_parts) - 1)
            possibilities = []
            for combination in combinatorics:
                i = 0
                one_such_combination = [q_parts[i]]
                for slab in combination:
                    i += 1
                    if not slab: # there is a join
                        one_such_combination[-1] += ' ' + q_parts[i]
                    else:
                        one_such_combination += [q_parts[i]]
                possibilities.append(one_such_combination)

            # Now, for all possiblities we'll append all the Q objects using OR
            for p in possibilities:
                list1=self.search_fields
                list2=p
                perms = [zip(x,list2) for x in itertools.permutations(list1,len(list2))]

                for perm in perms:
                    q_part = Q()
                    for p in perm:
                        q_part = q_part & Q(**{p[0]+'__icontains': p[1]})
                    q_totals = q_totals | q_part

            qs = qs.filter(q_totals)
        return qs

The previous filtering code works fine with querise like "The Stand" or "Under the Dome Stephen King"!

One thing that you must be careful is that this code will create *very complicated and big* queries. For example,
searching for "Under the Dome Stephen King" will result to `q_totals` getting this monster value:

.. code::

    (OR: 
    (AND: ), 
    (AND: ('title__icontains', u'Under'), ('author__icontains', u'the'), ('category__icontains', u'Dome'), ('id__icontains', u'Stephen King')), 
    (AND: ('title__icontains', u'Under'), ('author__icontains', u'the'), ('id__icontains', u'Dome'), ('category__icontains', u'Stephen King')), 
    (AND: ('title__icontains', u'Under'), ('category__icontains', u'the'), ('author__icontains', u'Dome'), ('id__icontains', u'Stephen King')),
    (AND: ('title__icontains', u'Under'), ('category__icontains', u'the'), ('id__icontains', u'Dome'), ('author__icontains', u'Stephen King')), 
    (AND: ('title__icontains', u'Under'), ('id__icontains', u'the'), ('author__icontains', u'Dome'), ('category__icontains', u'Stephen King')), 
    (AND: ('title__icontains', u'Under'), ('id__icontains', u'the'), ('category__icontains', u'Dome'), ('author__icontains', u'Stephen King')),
    (AND: ('author__icontains', u'Under'), ('title__icontains', u'the'), ('category__icontains', u'Dome'), ('id__icontains', u'Stephen King')), 
    (AND: ('author__icontains', u'Under'), ('title__icontains', u'the'), ('id__icontains', u'Dome'), ('category__icontains', u'Stephen King')), 
    (AND: ('author__icontains', u'Under'), ('category__icontains', u'the'), ('title__icontains', u'Dome'), ('id__icontains', u'Stephen King')),
    (AND: ('author__icontains', u'Under'), ('category__icontains', u'the'), ('id__icontains', u'Dome'), ('title__icontains', u'Stephen King')), 
    (AND: ('author__icontains', u'Under'), ('id__icontains', u'the'), ('title__icontains', u'Dome'), ('category__icontains', u'Stephen King')), 
    (AND: ('author__icontains', u'Under'), ('id__icontains', u'the'), ('category__icontains', u'Dome'), ('title__icontains', u'Stephen King')),
    (AND: ('category__icontains', u'Under'), ('title__icontains', u'the'), ('author__icontains', u'Dome'), ('id__icontains', u'Stephen King')), 
    (AND: ('category__icontains', u'Under'), ('title__icontains', u'the'), ('id__icontains', u'Dome'), ('author__icontains', u'Stephen King')), 
    (AND: ('category__icontains', u'Under'), ('author__icontains', u'the'), ('title__icontains', u'Dome'), ('id__icontains', u'Stephen King')),
    (AND: ('category__icontains', u'Under'), ('author__icontains', u'the'), ('id__icontains', u'Dome'), ('title__icontains', u'Stephen King')), 
    (AND: ('category__icontains', u'Under'), ('id__icontains', u'the'), ('title__icontains', u'Dome'), ('author__icontains', u'Stephen King')), 
    (AND: ('category__icontains', u'Under'), ('id__icontains', u'the'), ('author__icontains', u'Dome'), ('title__icontains', u'Stephen King')),
    (AND: ('id__icontains', u'Under'), ('title__icontains', u'the'), ('author__icontains', u'Dome'), ('category__icontains', u'Stephen King')), 
    (AND: ('id__icontains', u'Under'), ('title__icontains', u'the'), ('category__icontains', u'Dome'), ('author__icontains', u'Stephen King')), 
    (AND: ('id__icontains', u'Under'), ('author__icontains', u'the'), ('title__icontains', u'Dome'), ('category__icontains', u'Stephen King')),
    (AND: ('id__icontains', u'Under'), ('author__icontains', u'the'), ('category__icontains', u'Dome'), ('title__icontains', u'Stephen King')), 
    (AND: ('id__icontains', u'Under'), ('category__icontains', u'the'), ('title__icontains', u'Dome'), ('author__icontains', u'Stephen King')), 
    (AND: ('id__icontains', u'Under'), ('category__icontains', u'the'), ('author__icontains', u'Dome'), ('title__icontains', u'Stephen King')),
    (AND: ('title__icontains', u'Under'), ('author__icontains', u'the'), ('category__icontains', u'Dome Stephen'), ('id__icontains', u'King')), 
    (AND: ('title__icontains', u'Under'), ('author__icontains', u'the'), ('id__icontains', u'Dome Stephen'), ('category__icontains', u'King')), 
    (AND: ('title__icontains', u'Under'), ('category__icontains', u'the'), ('author__icontains', u'Dome Stephen'), ('id__icontains', u'King')),
    (AND: ('title__icontains', u'Under'), ('category__icontains', u'the'), ('id__icontains', u'Dome Stephen'), ('author__icontains', u'King')), 
    (AND: ('title__icontains', u'Under'), ('id__icontains', u'the'), ('author__icontains', u'Dome Stephen'), ('category__icontains', u'King')), 
    (AND: ('title__icontains', u'Under'), ('id__icontains', u'the'), ('category__icontains', u'Dome Stephen'), ('author__icontains', u'King')),
    (AND: ('author__icontains', u'Under'), ('title__icontains', u'the'), ('category__icontains', u'Dome Stephen'), ('id__icontains', u'King')), 
    (AND: ('author__icontains', u'Under'), ('title__icontains', u'the'), ('id__icontains', u'Dome Stephen'), ('category__icontains', u'King')), 
    (AND: ('author__icontains', u'Under'), ('category__icontains', u'the'), ('title__icontains', u'Dome Stephen'), ('id__icontains', u'King')),
    (AND: ('author__icontains', u'Under'), ('category__icontains', u'the'), ('id__icontains', u'Dome Stephen'), ('title__icontains', u'King')), 
    (AND: ('author__icontains', u'Under'), ('id__icontains', u'the'), 'title__icontains', u'Dome Stephen'), ('category__icontains', u'King')), 
    (AND: ('author__icontains', u'Under'), ('id__icontains', u'the'), ('category__icontains', u'Dome Stephen'), ('title__icontains', u'King')),
    (AND: ('category__icontains', u'Under'), ('title__icontains', u'the'), ('author__icontains', u'Dome Stephen'),('id__icontains', u'King')), 
    (AND: ('category__icontains', u'Under'), ('title__icontains', u'the'), ('id__icontains', u'Dome Stephen'), ('author__icontains', u'King')),
    (AND: ('category__icontains', u'Under'), ('author__icontains', u'the'), ('title__icontains', u'Dome Stephen'), ('id__icontains', u'King')),
    (AND: ('category__icontains', u'Under'), ('author__icontains', u'the'), ('id__icontains', u'Dome Stephen'), ('title__icontains', u'King')),
    (AND: ('category__icontains', u'Under'), ('id__icontains', u'the'), ('title__icontains', u'Dome Stephen'), ('author__icontains', u'King')),
    (AND: ('category__icontains', u'Under'), ('id__icontains', u'the'), ('author__icontains', u'Dome Stephen'), ('title__icontains', u'King')),
    (AND: ('id__icontains', u'Under'), ('title__icontains', u'the'), ('author__icontains', u'Dome Stephen'), ('category__icontains', u'King')),
    (AND: ('id__icontains', u'Under'), ('title__icontains', u'the'), ('category__icontains', u'Dome Stephen'), ('author__icontains', u'King')),
    (AND: ('id__icontains', u'Under'), ('author__icontains', u'the'), ('title__icontains', u'Dome Stephen'), ('category__icontains', u'King')),
    (AND: ('id__icontains', u'Under'), ('author__icontains', u'the'), ('category__icontains', u'Dome Stephen'), ('title__icontains', u'King')),
    (AND: ('id__icontains', u'Under'), ('category__icontains', u'the'), ('title__icontains', u'Dome Stephen'), ('author__icontains', u'King')),
    (AND: ('id__icontains', u'Under'), ('category__icontains', u'the'), ('author__icontains', u'Dome Stephen'), ('title__icontains', u'King')),
    (AND: ('title__icontains', u'Under'), ('author__icontains', u'the'), ('category__icontains', u'Dome Stephen King')),
    (AND: ('title__icontains', u'Under'), ('author__icontains', u'the'), ('id__icontains', u'Dome Stephen King')),
    (AND: ('title__icontains', u'Under'), ('category__icontains', u'the'), ('author__icontains', u'Dome Stephen King')),
    (AND: ('title__icontains', u'Under'), ('category__icontains', u'the'), ('id__icontains', u'Dome Stephen King')),
    (AND: ('title__icontains', u'Under'), ('id__icontains', u'the'), ('author__icontains', u'Dome Stephen King')),
    (AND: ('title__icontains', u'Under'), ('id__icontains', u'the'), ('category__icontains', u'Dome Stephen King')),
    (AND: ('author__icontains', u'Under'), ('title__icontains', u'the'), ('category__icontains', u'Dome Stephen King')),
    (AND: ('author__icontains', u'Under'), ('title__icontains', u'the'), ('id__icontains', u'Dome Stephen King')),
    (AND: ('author__icontains', u'Under'), ('category__icontains', u'the'), ('title__icontains', u'Dome Stephen King')),
    (AND: ('author__icontains', u'Under'), ('category__icontains', u'the'), ('id__icontains', u'Dome Stephen King')),
    (AND: ('author__icontains', u'Under'), ('id__icontains', u'the'), ('title__icontains', u'Dome Stephen King')),
    (AND: ('author__icontains', u'Under'), ('id__icontains', u'the'), ('category__icontains', u'Dome Stephen King')),
    (AND: ('category__icontains', u'Under'), ('title__icontains', u'the'), ('author__icontains', u'Dome Stephen King')),
    (AND: ('category__icontains', u'Under'), ('title__icontains', u'the'), ('id__icontains', u'Dome Stephen King')),
    (AND: ('category__icontains', u'Under'), ('author__icontains', u'the'), ('title__icontains', u'Dome Stephen King')),
    (AND: ('category__icontains', u'Under'), ('author__icontains', u'the'), ('id__icontains', u'Dome Stephen King')),
    (AND: ('category__icontains', u'Under'), ('id__icontains', u'the'), ('title__icontains', u'Dome Stephen King')),
    (AND: ('category__icontains', u'Under'), ('id__icontains', u'the'), ('author__icontains', u'Dome Stephen King')),
    (AND: ('id__icontains', u'Under'), ('title__icontains', u'the'), ('author__icontains', u'Dome Stephen King')),
    (AND: ('id__icontains', u'Under'), ('title__icontains', u'the'), ('category__icontains', u'Dome Stephen King')),
    (AND: ('id__icontains', u'Under'), ('author__icontains', u'the'), ('title__icontains', u'Dome Stephen King')),
    (AND: ('id__icontains', u'Under'), ('author__icontains', u'the'), ('category__icontains', u'Dome Stephen King')),
    (AND: ('id__icontains', u'Under'), ('category__icontains', u'the'), ('title__icontains', u'Dome Stephen King')),
    (AND: ('id__icontains', u'Under'), ('category__icontains', u'the'), ('author__icontains', u'Dome Stephen King')),
    (AND: ('title__icontains', u'Under'), ('author__icontains', u'the Dome'), ('category__icontains', u'Stephen'), ('id__icontains', u'King')),
    (AND: ('title__icontains', u'Under'), ('author__icontains', u'the Dome'), ('id__icontains', u'Stephen'), ('category__icontains', u'King')),
    (AND: ('title__icontains', u'Under'), ('category__icontains', u'the Dome'), ('author__icontains', u'Stephen'), ('id__icontains', u'King')),
    (AND: ('title__icontains', u'Under'), ('category__icontains', u'the Dome'), ('id__icontains', u'Stephen'), ('author__icontains', u'King')), 
    (AND: ('title__icontains', u'Under'), ('id__icontains', u'the Dome'), ('author__icontains', u'Stephen'), ('category__icontains', u'King')), 
    (AND: ('title__icontains', u'Under'), ('id__icontains', u'the Dome'), ('category__icontains', u'Stephen'), ('author__icontains', u'King')), 
    (AND: ('author__icontains', u'Under'), ('title__icontains', u'the Dome'), ('category__icontains', u'Stephen'), ('id__icontains', u'King')), 
    (AND: ('author__icontains', u'Under'), ('title__icontains', u'the Dome'), ('id__icontains', u'Stephen'), ('category__icontains', u'King')), 
    (AND: ('author__icontains', u'Under'), ('category__icontains', u'the Dome'), ('title__icontains', u'Stephen'), ('id__icontains', u'King')), 
    (AND: ('author__icontains', u'Under'), ('category__icontains', u'the Dome'), ('id__icontains', u'Stephen'), ('title__icontains', u'King')), 
    (AND: ('author__icontains', u'Under'), ('id__icontains', u'the Dome'), ('title__icontains', u'Stephen'), ('category__icontains', u'King')), 
    (AND: ('author__icontains', u'Under'), ('id__icontains', u'the Dome'), ('category__icontains', u'Stephen'), ('title__icontains', u'King')), 
    (AND: ('category__icontains', u'Under'), ('title__icontains', u'the Dome'), ('author__icontains', u'Stephen'), ('id__icontains', u'King')), 
    (AND: ('category__icontains', u'Under'), ('title__icontains', u'the Dome'), ('id__icontains', u'Stephen'), ('author__icontains', u'King')), 
    (AND: ('category__icontains', u'Under'), ('author__icontains', u'the Dome'), ('title__icontains', u'Stephen'), ('id__icontains', u'King')), 
    (AND: ('category__icontains', u'Under'), ('author__icontains', u'the Dome'), ('id__icontains', u'Stephen'), ('title__icontains', u'King')), 
    (AND: ('category__icontains', u'Under'), ('id__icontains', u'the Dome'), ('title__icontains', u'Stephen'), ('author__icontains', u'King')), 
    (AND: ('category__icontains', u'Under'), ('id__icontains', u'the Dome'), ('author__icontains', u'Stephen'), ('title__icontains', u'King')), 
    (AND: ('id__icontains', u'Under'), ('title__icontains', u'the Dome'), ('author__icontains', u'Stephen'), ('category__icontains', u'King')), 
    (AND: ('id__icontains', u'Under'), ('title__icontains', u'the Dome'), ('category__icontains', u'Stephen'), ('author__icontains', u'King')), 
    (AND: ('id__icontains', u'Under'), ('author__icontains', u'the Dome'), ('title__icontains', u'Stephen'), ('category__icontains', u'King')), 
    (AND: ('id__icontains', u'Under'), ('author__icontains', u'the Dome'), ('category__icontains', u'Stephen'), ('title__icontains', u'King')), 
    (AND: ('id__icontains', u'Under'), ('category__icontains', u'the Dome'), ('title__icontains', u'Stephen'), ('author__icontains', u'King')), 
    (AND: ('id__icontains', u'Under'), ('category__icontains', u'the Dome'), ('author__icontains', u'Stephen'), ('title__icontains', u'King')), 
    (AND: ('title__icontains', u'Under'), ('author__icontains', u'the Dome'), ('category__icontains', u'Stephen King')),
    (AND: ('title__icontains', u'Under'), ('author__icontains', u'the Dome'), ('id__icontains', u'Stephen King')), 
    (AND: ('title__icontains', u'Under'), ('category__icontains', u'the Dome'), ('author__icontains', u'Stephen King')), 
    (AND: ('title__icontains', u'Under'), ('category__icontains', u'the Dome'), ('id__icontains', u'Stephen King')), 
    (AND: ('title__icontains', u'Under'), ('id__icontains', u'the Dome'), ('author__icontains', u'Stephen King')), 
    (AND: ('title__icontains', u'Under'), ('id__icontains', u'the Dome'), ('category__icontains', u'Stephen King')), 
    (AND: ('author__icontains', u'Under'), ('title__icontains', u'the Dome'), ('category__icontains', u'Stephen King')), 
    (AND: ('author__icontains', u'Under'), ('title__icontains', u'the Dome'), ('id__icontains', u'Stephen King')), 
    (AND: ('author__icontains', u'Under'), ('category__icontains', u'the Dome'), ('title__icontains', u'Stephen King')), 
    (AND: ('author__icontains', u'Under'), ('category__icontains', u'the Dome'), ('id__icontains', u'Stephen King')), 
    (AND: ('author__icontains', u'Under'), ('id__icontains', u'the Dome'), ('title__icontains', u'Stephen King')), 
    (AND: ('author__icontains', u'Under'), ('id__icontains', u'the Dome'), ('category__icontains', u'Stephen King')), 
    (AND: ('category__icontains', u'Under'), ('title__icontains', u'the Dome'), ('author__icontains', u'Stephen King')), 
    (AND: ('category__icontains', u'Under'), ('title__icontains', u'the Dome'), ('id__icontains', u'Stephen King')), 
    (AND: ('category__icontains', u'Under'), ('author__icontains', u'the Dome'), ('title__icontains', u'Stephen King')), 
    (AND: ('category__icontains', u'Under'), ('author__icontains', u'the Dome'), ('id__icontains', u'Stephen King')), 
    (AND: ('category__icontains', u'Under'), ('id__icontains', u'the Dome'), ('title__icontains', u'Stephen King')), 
    (AND: ('category__icontains', u'Under'), ('id__icontains', u'the Dome'), ('author__icontains', u'Stephen King')), 
    (AND: ('id__icontains', u'Under'), ('title__icontains', u'the Dome'), ('author__icontains', u'Stephen King')), 
    (AND: ('id__icontains', u'Under'), ('title__icontains', u'the Dome'), ('category__icontains', u'Stephen King')), 
    (AND: ('id__icontains', u'Under'), ('author__icontains', u'the Dome'), ('title__icontains', u'Stephen King')), 
    (AND: ('id__icontains', u'Under'), ('author__icontains', u'the Dome'), ('category__icontains', u'Stephen King')), 
    (AND: ('id__icontains', u'Under'), ('category__icontains', u'the Dome'), ('title__icontains', u'Stephen King')), 
    (AND: ('id__icontains', u'Under'), ('category__icontains', u'the Dome'), ('author__icontains', u'Stephen King')), 
    (AND: ('title__icontains', u'Under'), ('author__icontains', u'the Dome Stephen'), ('category__icontains', u'King')), 
    (AND: ('title__icontains', u'Under'), ('author__icontains', u'the Dome Stephen'), ('id__icontains', u'King')), 
    (AND: ('title__icontains', u'Under'), ('category__icontains', u'the Dome Stephen'), ('author__icontains', u'King')),
    (AND: ('title__icontains', u'Under'), ('category__icontains', u'the Dome Stephen'), ('id__icontains', u'King')), 
    (AND: ('title__icontains', u'Under'), ('id__icontains', u'the Dome Stephen'), ('author__icontains', u'King')), 
    (AND: ('title__icontains', u'Under'), ('id__icontains', u'the Dome Stephen'), ('category__icontains', u'King')), 
    (AND: ('author__icontains', u'Under'), ('title__icontains', u'the Dome Stephen'), ('category__icontains', u'King')), 
    (AND: ('author__icontains', u'Under'), ('title__icontains', u'the Dome Stephen'), ('id__icontains', u'King')), 
    (AND: ('author__icontains', u'Under'), ('category__icontains', u'the Dome Stephen'), ('title__icontains', u'King')), 
    (AND: ('author__icontains', u'Under'), ('category__icontains', u'the Dome Stephen'), ('id__icontains', u'King')), 
    (AND: ('author__icontains', u'Under'), ('id__icontains', u'the Dome Stephen'), ('title__icontains', u'King')), 
    (AND: ('author__icontains', u'Under'), ('id__icontains', u'the Dome Stephen'), ('category__icontains', u'King')), 
    (AND: ('category__icontains', u'Under'), ('title__icontains', u'the Dome Stephen'), ('author__icontains', u'King')), 
    (AND: ('category__icontains', u'Under'), ('title__icontains', u'the Dome Stephen'), ('id__icontains', u'King')), 
    (AND: ('category__icontains', u'Under'), ('author__icontains', u'the Dome Stephen'), ('title__icontains', u'King')), 
    (AND: ('category__icontains', u'Under'), ('author__icontains', u'the Dome Stephen'), ('id__icontains', u'King')), 
    (AND: ('category__icontains', u'Under'), ('id__icontains', u'the Dome Stephen'), ('title__icontains', u'King')), 
    (AND: ('category__icontains', u'Under'), ('id__icontains', u'the Dome Stephen'), ('author__icontains', u'King')), 
    (AND: ('id__icontains', u'Under'), ('title__icontains', u'the Dome Stephen'), ('author__icontains', u'King')), 
    (AND: ('id__icontains', u'Under'), ('title__icontains', u'the Dome Stephen'), ('category__icontains', u'King')), 
    (AND: ('id__icontains', u'Under'), ('author__icontains', u'the Dome Stephen'), ('title__icontains', u'King')), 
    (AND: ('id__icontains', u'Under'), ('author__icontains', u'the Dome Stephen'), ('category__icontains', u'King')), 
    (AND: ('id__icontains', u'Under'), ('category__icontains', u'the Dome Stephen'), ('title__icontains', u'King')), 
    (AND: ('id__icontains', u'Under'), ('category__icontains', u'the Dome Stephen'), ('author__icontains', u'King')), 
    (AND: ('title__icontains', u'Under'), ('author__icontains', u'the Dome Stephen King')), 
    (AND: ('title__icontains', u'Under'), ('category__icontains', u'the Dome Stephen King')), 
    (AND: ('title__icontains', u'Under'), ('id__icontains', u'the Dome Stephen King')), 
    (AND: ('author__icontains', u'Under'), ('title__icontains', u'the Dome Stephen King')), 
    (AND: ('author__icontains', u'Under'), ('category__icontains', u'the Dome Stephen King')), 
    (AND: ('author__icontains', u'Under'), ('id__icontains', u'the Dome Stephen King')), 
    (AND: ('category__icontains', u'Under'), ('title__icontains', u'the Dome Stephen King')), 
    (AND: ('category__icontains', u'Under'), ('author__icontains', u'the Dome Stephen King')), 
    (AND: ('category__icontains', u'Under'), ('id__icontains', u'the Dome Stephen King')), 
    (AND: ('id__icontains', u'Under'), ('title__icontains', u'the Dome Stephen King')),
    (AND: ('id__icontains', u'Under'), ('author__icontains', u'the Dome Stephen King')), 
    (AND: ('id__icontains', u'Under'), ('category__icontains', u'the Dome Stephen King')), 
    (AND: ('title__icontains', u'Under the'), ('author__icontains', u'Dome'), ('category__icontains', u'Stephen'), ('id__icontains', u'King')), 
    (AND: ('title__icontains', u'Under the'), ('author__icontains', u'Dome'), ('id__icontains', u'Stephen'), ('category__icontains', u'King')), 
    (AND: ('title__icontains', u'Under the'), ('category__icontains', u'Dome'), ('author__icontains', u'Stephen'), ('id__icontains', u'King')), 
    (AND: ('title__icontains', u'Under the'), ('category__icontains', u'Dome'), ('id__icontains', u'Stephen'), ('author__icontains', u'King')), 
    (AND: ('title__icontains', u'Under the'), ('id__icontains', u'Dome'), ('author__icontains', u'Stephen'), ('category__icontains', u'King')), 
    (AND: ('title__icontains', u'Under the'), ('id__icontains', u'Dome'), ('category__icontains', u'Stephen'), ('author__icontains', u'King')), 
    (AND: ('author__icontains', u'Under the'), ('title__icontains', u'Dome'), ('category__icontains', u'Stephen'), ('id__icontains', u'King')), 
    (AND: ('author__icontains', u'Under the'), ('title__icontains', u'Dome'), ('id__icontains', u'Stephen'), ('category__icontains', u'King')), 
    (AND: ('author__icontains', u'Under the'), ('category__icontains', u'Dome'), ('title__icontains', u'Stephen'), ('id__icontains', u'King')), 
    (AND: ('author__icontains', u'Under the'), ('category__icontains', u'Dome'), ('id__icontains', u'Stephen'), ('title__icontains', u'King')), 
    (AND: ('author__icontains', u'Under the'), ('id__icontains', u'Dome'), ('title__icontains', u'Stephen'), ('category__icontains', u'King')), 
    (AND: ('author__icontains', u'Under the'), ('id__icontains', u'Dome'), ('category__icontains', u'Stephen'), ('title__icontains', u'King')), 
    (AND: ('category__icontains', u'Under the'), ('title__icontains', u'Dome'), ('author__icontains', u'Stephen'), ('id__icontains', u'King')), 
    (AND: ('category__icontains', u'Under the'), ('title__icontains', u'Dome'), ('id__icontains', u'Stephen'), ('author__icontains', u'King')), 
    (AND: ('category__icontains', u'Under the'), ('author__icontains', u'Dome'), ('title__icontains', u'Stephen'), ('id__icontains', u'King')), 
    (AND: ('category__icontains', u'Under the'), ('author__icontains', u'Dome'), ('id__icontains', u'Stephen'), ('title__icontains', u'King')), 
    (AND: ('category__icontains', u'Under the'), ('id__icontains', u'Dome'), ('title__icontains', u'Stephen'), ('author__icontains', u'King')), 
    (AND: ('category__icontains', u'Under the'), ('id__icontains', u'Dome'), ('author__icontains', u'Stephen'), ('title__icontains', u'King')), 
    (AND: ('id__icontains', u'Under the'), ('title__icontains', u'Dome'), ('author__icontains', u'Stephen'), ('category__icontains', u'King')), 
    (AND: ('id__icontains', u'Under the'), ('title__icontains', u'Dome'), ('category__icontains', u'Stephen'), ('author__icontains', u'King')), 
    (AND: ('id__icontains', u'Under the'), ('author__icontains', u'Dome'), ('title__icontains', u'Stephen'), ('category__icontains', u'King')), 
    (AND: ('id__icontains', u'Under the'), ('author__icontains', u'Dome'), ('category__icontains', u'Stephen'), ('title__icontains', u'King')), 
    (AND: ('id__icontains', u'Under the'), ('category__icontains', u'Dome'), ('title__icontains', u'Stephen'), ('author__icontains', u'King')), 
    (AND: ('id__icontains', u'Under the'), ('category__icontains', u'Dome'), ('author__icontains', u'Stephen'), ('title__icontains', u'King')), 
    (AND: ('title__icontains', u'Under the'), ('author__icontains', u'Dome'), ('category__icontains', u'Stephen King')), 
    (AND: ('title__icontains', u'Under the'), ('author__icontains', u'Dome'), ('id__icontains', u'Stephen King')),
    (AND: ('title__icontains', u'Under the'), ('category__icontains', u'Dome'), ('author__icontains', u'Stephen King')),
    (AND: ('title__icontains', u'Under the'), ('category__icontains', u'Dome'), ('id__icontains', u'Stephen King')), 
    (AND: ('title__icontains', u'Under the'), ('id__icontains', u'Dome'), ('author__icontains', u'Stephen King')), 
    (AND: ('title__icontains', u'Under the'), ('id__icontains', u'Dome'), ('category__icontains', u'Stephen King')),
    (AND: ('author__icontains', u'Under the'), ('title__icontains', u'Dome'), ('category__icontains', u'Stephen King')), 
    (AND: ('author__icontains', u'Under the'), ('title__icontains', u'Dome'), ('id__icontains', u'Stephen King')), 
    (AND: ('author__icontains', u'Under the'), ('category__icontains', u'Dome'), ('title__icontains', u'Stephen King')), 
    (AND: ('author__icontains', u'Under the'), ('category__icontains', u'Dome'), ('id__icontains', u'Stephen King')), 
    (AND: ('author__icontains', u'Under the'), ('id__icontains', u'Dome'), ('title__icontains', u'Stephen King')), 
    (AND: ('author__icontains', u'Under the'), ('id__icontains', u'Dome'), ('category__icontains', u'Stephen King')), 
    (AND: ('category__icontains', u'Under the'), ('title__icontains', u'Dome'), ('author__icontains', u'Stephen King')), 
    (AND: ('category__icontains', u'Under the'), ('title__icontains', u'Dome'), ('id__icontains', u'Stephen King')),
    (AND: ('category__icontains', u'Under the'), ('author__icontains', u'Dome'), ('title__icontains', u'Stephen King')), 
    (AND: ('category__icontains', u'Under the'), ('author__icontains', u'Dome'), ('id__icontains', u'Stephen King')), 
    (AND: ('category__icontains', u'Under the'), ('id__icontains', u'Dome'), ('title__icontains', u'Stephen King')), 
    (AND: ('category__icontains', u'Under the'), ('id__icontains', u'Dome'), ('author__icontains', u'Stephen King')),
    (AND: ('id__icontains', u'Under the'), ('title__icontains', u'Dome'), ('author__icontains', u'Stephen King')),
    (AND: ('id__icontains', u'Under the'), ('title__icontains', u'Dome'), ('category__icontains', u'Stephen King')),
    (AND: ('id__icontains', u'Under the'), ('author__icontains', u'Dome'), ('title__icontains', u'Stephen King')), 
    (AND: ('id__icontains', u'Under the'), ('author__icontains', u'Dome'), ('category__icontains', u'Stephen King')),
    (AND: ('id__icontains', u'Under the'), ('category__icontains', u'Dome'), ('title__icontains', u'Stephen King')),
    (AND: ('id__icontains', u'Under the'), ('category__icontains', u'Dome'), ('author__icontains', u'Stephen King')), 
    (AND: ('title__icontains', u'Under the'), ('author__icontains', u'Dome Stephen'), ('category__icontains', u'King')),
    (AND: ('title__icontains', u'Under the'), ('author__icontains', u'Dome Stephen'), ('id__icontains', u'King')), 
    (AND: ('title__icontains', u'Under the'), ('category__icontains', u'Dome Stephen'), ('author__icontains', u'King')),
    (AND: ('title__icontains', u'Under the'), ('category__icontains', u'Dome Stephen'), ('id__icontains', u'King')),
    (AND: ('title__icontains', u'Under the'), ('id__icontains', u'Dome Stephen'), ('author__icontains', u'King')),
    (AND: ('title__icontains', u'Under the'), ('id__icontains', u'Dome Stephen'), ('category__icontains', u'King')), 
    (AND: ('author__icontains', u'Under the'), ('title__icontains', u'Dome Stephen'), ('category__icontains', u'King')),
    (AND: ('author__icontains', u'Under the'), ('title__icontains', u'Dome Stephen'), ('id__icontains', u'King')),
    (AND: ('author__icontains', u'Under the'), ('category__icontains', u'Dome Stephen'), ('title__icontains', u'King')),
    (AND: ('author__icontains', u'Under the'), ('category__icontains', u'Dome Stephen'), ('id__icontains', u'King')),
    (AND: ('author__icontains', u'Under the'), ('id__icontains', u'Dome Stephen'), ('title__icontains', u'King')),
    (AND: ('author__icontains', u'Under the'), ('id__icontains', u'Dome Stephen'), ('category__icontains', u'King')),
    (AND: ('category__icontains', u'Under the'), ('title__icontains', u'Dome Stephen'), ('author__icontains', u'King')),
    (AND: ('category__icontains', u'Under the'), ('title__icontains', u'Dome Stephen'), ('id__icontains', u'King')),
    (AND: ('category__icontains', u'Under the'), ('author__icontains', u'Dome Stephen'), ('title__icontains', u'King')),
    (AND: ('category__icontains', u'Under the'), ('author__icontains', u'Dome Stephen'), ('id__icontains', u'King')), 
    (AND: ('category__icontains', u'Under the'), ('id__icontains', u'Dome Stephen'), ('title__icontains', u'King')), 
    (AND: ('category__icontains', u'Under the'), ('id__icontains', u'Dome Stephen'), ('author__icontains', u'King')),
    (AND: ('id__icontains', u'Under the'), ('title__icontains', u'Dome Stephen'), ('author__icontains', u'King')), 
    (AND: ('id__icontains', u'Under the'), ('title__icontains', u'Dome Stephen'), ('category__icontains', u'King')),
    (AND: ('id__icontains', u'Under the'), ('author__icontains', u'Dome Stephen'), ('title__icontains', u'King')), 
    (AND: ('id__icontains', u'Under the'), ('author__icontains', u'Dome Stephen'), ('category__icontains', u'King')),
    (AND: ('id__icontains', u'Under the'), ('category__icontains', u'Dome Stephen'), ('title__icontains', u'King')), 
    (AND: ('id__icontains', u'Under the'), ('category__icontains', u'Dome Stephen'), ('author__icontains', u'King')),
    (AND: ('title__icontains', u'Under the'), ('author__icontains', u'Dome Stephen King')),
    (AND: ('title__icontains', u'Under the'), ('category__icontains', u'Dome Stephen King')),
    (AND: ('title__icontains', u'Under the'), ('id__icontains', u'Dome Stephen King')), 
    (AND: ('author__icontains', u'Under the'), ('title__icontains', u'Dome Stephen King')),
    (AND: ('author__icontains', u'Under the'), ('category__icontains', u'Dome Stephen King')),
    (AND: ('author__icontains', u'Under the'), ('id__icontains', u'Dome Stephen King')),
    (AND: ('category__icontains', u'Under the'), ('title__icontains', u'Dome Stephen King')), 
    (AND: ('category__icontains', u'Under the'), ('author__icontains', u'Dome Stephen King')), 
    (AND: ('category__icontains', u'Under the'), ('id__icontains', u'Dome Stephen King')), 
    (AND: ('id__icontains', u'Under the'), ('title__icontains', u'Dome Stephen King')), 
    (AND: ('id__icontains', u'Under the'), ('author__icontains', u'Dome Stephen King')),
    (AND: ('id__icontains', u'Under the'), ('category__icontains', u'Dome Stephen King')), 
    (AND: ('title__icontains', u'Under the Dome'), ('author__icontains', u'Stephen'), ('category__icontains', u'King')), 
    (AND: ('title__icontains', u'Under the Dome'), ('author__icontains', u'Stephen'), ('id__icontains', u'King')), 
    (AND: ('title__icontains', u'Under the Dome'), ('category__icontains', u'Stephen'), ('author__icontains', u'King')),
    (AND: ('title__icontains', u'Under the Dome'), ('category__icontains', u'Stephen'), ('id__icontains', u'King')),
    (AND: ('title__icontains', u'Under the Dome'), ('id__icontains', u'Stephen'), ('author__icontains', u'King')),
    (AND: ('title__icontains', u'Under the Dome'), ('id__icontains', u'Stephen'), ('category__icontains', u'King')),
    (AND: ('author__icontains', u'Under the Dome'), ('title__icontains', u'Stephen'), ('category__icontains', u'King')),
    (AND: ('author__icontains', u'Under the Dome'), ('title__icontains', u'Stephen'), ('id__icontains', u'King')),
    (AND: ('author__icontains', u'Under the Dome'), ('category__icontains', u'Stephen'), ('title__icontains', u'King')),
    (AND: ('author__icontains', u'Under the Dome'), ('category__icontains', u'Stephen'), ('id__icontains', u'King')), 
    (AND: ('author__icontains', u'Under the Dome'), ('id__icontains', u'Stephen'), ('title__icontains', u'King')), 
    (AND: ('author__icontains', u'Under the Dome'), ('id__icontains', u'Stephen'), ('category__icontains', u'King')), 
    (AND: ('category__icontains', u'Under the Dome'), ('title__icontains', u'Stephen'), ('author__icontains', u'King')), 
    (AND: ('category__icontains', u'Under the Dome'), ('title__icontains', u'Stephen'), ('id__icontains', u'King')), 
    (AND: ('category__icontains', u'Under the Dome'), ('author__icontains', u'Stephen'), ('title__icontains', u'King')), 
    (AND: ('category__icontains', u'Under the Dome'), ('author__icontains', u'Stephen'), ('id__icontains', u'King')), 
    (AND: ('category__icontains', u'Under the Dome'), ('id__icontains', u'Stephen'), ('title__icontains', u'King')), 
    (AND: ('category__icontains', u'Under the Dome'), ('id__icontains', u'Stephen'), ('author__icontains', u'King')), 
    (AND: ('id__icontains', u'Under the Dome'), ('title__icontains', u'Stephen'), ('author__icontains', u'King')), 
    (AND: ('id__icontains', u'Under the Dome'), ('title__icontains', u'Stephen'), ('category__icontains', u'King')), 
    (AND: ('id__icontains', u'Under the Dome'), ('author__icontains', u'Stephen'), ('title__icontains', u'King')), 
    (AND: ('id__icontains', u'Under the Dome'), ('author__icontains', u'Stephen'), ('category__icontains', u'King')), 
    (AND: ('id__icontains', u'Under the Dome'), ('category__icontains', u'Stephen'), ('title__icontains', u'King')), 
    (AND: ('id__icontains', u'Under the Dome'), ('category__icontains', u'Stephen'), ('author__icontains', u'King')),
    (AND: ('title__icontains', u'Under the Dome'), ('author__icontains', u'Stephen King')),
    (AND: ('title__icontains', u'Under the Dome'), ('category__icontains', u'Stephen King')), 
    (AND: ('title__icontains', u'Under the Dome'), ('id__icontains', u'Stephen King')), 
    (AND: ('author__icontains', u'Under the Dome'), ('title__icontains', u'Stephen King')), 
    (AND: ('author__icontains', u'Under the Dome'), ('category__icontains', u'Stephen King')),
    (AND: ('author__icontains', u'Under the Dome'), ('id__icontains', u'Stephen King')),
    (AND: ('category__icontains', u'Under the Dome'), ('title__icontains', u'Stephen King')), 
    (AND: ('category__icontains', u'Under the Dome'), ('author__icontains', u'Stephen King')),
    (AND: ('category__icontains', u'Under the Dome'), ('id__icontains', u'Stephen King')),
    (AND: ('id__icontains', u'Under the Dome'), ('title__icontains', u'Stephen King')),
    (AND: ('id__icontains', u'Under the Dome'), ('author__icontains', u'Stephen King')), 
    (AND: ('id__icontains', u'Under the Dome'), ('category__icontains', u'Stephen King')), 
    (AND: ('title__icontains', u'Under the Dome Stephen'), ('author__icontains', u'King')), 
    (AND: ('title__icontains', u'Under the Dome Stephen'), ('category__icontains', u'King')), 
    (AND: ('title__icontains', u'Under the Dome Stephen'), ('id__icontains', u'King')),
    (AND: ('author__icontains', u'Under the Dome Stephen'), ('title__icontains', u'King')),
    (AND: ('author__icontains', u'Under the Dome Stephen'), ('category__icontains', u'King')), 
    (AND: ('author__icontains', u'Under the Dome Stephen'), ('id__icontains', u'King')),
    (AND: ('category__icontains', u'Under the Dome Stephen'), ('title__icontains', u'King')), 
    (AND: ('category__icontains', u'Under the Dome Stephen'), ('author__icontains', u'King')), 
    (AND: ('category__icontains', u'Under the Dome Stephen'), ('id__icontains', u'King')),
    (AND: ('id__icontains', u'Under the Dome Stephen'), ('title__icontains', u'King')),
    (AND: ('id__icontains', u'Under the Dome Stephen'), ('author__icontains', u'King')), 
    (AND: ('id__icontains', u'Under the Dome Stephen'), ('category__icontains', u'King')), 
    ('title__icontains', u'Under the Dome Stephen King'), 
    ('author__icontains', u'Under the Dome Stephen King'), 
    ('category__icontains', u'Under the Dome Stephen King'), 
    ('id__icontains', u'Under the Dome Stephen King')
    )

This query has around 200 different OR parts!!! So please be careful on the amount of search fields you'll enable to works
with this method or your database will really struggle!
    
.. _django-filter: https://github.com/alex/django-filter
.. _datatable: https://datatables.net/
.. _django-autocomplete-light: https://github.com/yourlabs/django-autocomplete-light