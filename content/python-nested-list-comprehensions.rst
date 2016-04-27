Understanding nested list comprehension syntax in Python 
########################################################

:date: 2016-04-27 11:20
:tags: python, debug, 404, error, python
:category: python
:slug: python-nested-list-comprehensions
:author: Serafeim Papastefanos
:summary: Write nested list comprehensions with ease

List comprehensions are one of the really nice and powerful features of Python. It
is actually a smart way to introduce new users to functional programming concepts
(after all a list comprehension is just a combination of map and filter) and compact statements.

However, one thing that always troubled me when using list comprehensions is their
non intuitive syntax when nesting was needed. For example, let's say that we just
want to flatten a list of lists using a nested list comprehension:

.. code-block:: python

    non_flat = [ [1,2,3], [4,5,6], [7,8] ]
    
To write that, somebody would think: For a simple list 
comprehension I need to 
write ``[ x for x in non_flat ]`` to get all its items - however I want to retrieve each element of the ``x`` list so I'll write something like this: 

.. code-block:: python

    >>> [y for y in x for x in non_flat]
    [7, 7, 7, 8, 8, 8]
    
Well duh! At this time I'd need research google for a working list comprehension syntax and adjust it to my needs (or give up and write it as a double for loop).

Here's the correct nested list comprehension people wondering:

.. code-block:: python
    
    >>> [y for x in non_flat for y in x]
    [1, 2, 3, 4, 5, 6, 7, 8]

What if I wanted to add a third level of nesting or an if? Well I'd just bite the bullet and use for loops!

However, if you take a look at the document describing list comprehensions in python (`PEP 202`) you'll see
the following phrase:

    It is proposed to allow conditional construction of list literals
    using for and if clauses. **They would nest in the same way for
    loops and if statements nest now.**
    
This statement explains everything! *Just think in for-loops syntax*. So, If I used for loops for the previous flattening, I'd do something like:

.. code-block:: python

    for x in non_flat:
        for y in x:
            y
            
which, if `y` is moved to the front and joined in one line would be the correct nested list comprehension!

So that's the way... What If I wanted to include only lists with more than 2 elements in the flattening
(so `[7,8]` should not be included)? I'll write it with for loops first:

.. code-block:: python

    for x in non_flat:
        if len(x) > 2
            for y in x:
                y

so by convering this to list comprehension we get:

.. code-block:: python

    >>> [ y for x in non_flat if len(x) > 2 for y in x ]
    [1, 2, 3, 4, 5, 6]
    
Success!

One final, more complex example: Let's say that we have a list
of lists of words and we want to get a list of all the letters of these words
along with the index of the list they belong to 
but only for words with more than two characters. Using the same
for-loop syntax for the nested list comprehensions we'll get:

.. code-block:: python

    >>> strings = [ ['foo', 'bar'], ['baz', 'taz'], ['w', 'koko'] ]
    >>> [ (letter, idx) for idx, lst in enumerate(strings) for word in lst if len(word)>2 for letter in word]
    [('f', 0), ('o', 0), ('o', 0), ('b', 0), ('a', 0), ('r', 0), ('b', 1), ('a', 1), ('z', 1), ('t', 1), ('a', 1), ('z', 1), ('k', 2), ('o', 2), ('k', 2), ('o', 2)]
            

            

.. _`PEP 202`: https://www.python.org/dev/peps/pep-0202/
