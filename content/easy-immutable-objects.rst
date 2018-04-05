Easy immutable objects in Javascript
####################################

:date: 2018-04-05 12:20
:tags: javascript, react, redux, hyperapp, immutable, es6
:category: javascript
:slug: easy-immutable-objects
:author: Serafeim Papastefanos
:summary: How to avoid mutations in your objects and a poor man's lens!
:status: draft

With the rise of Redux_ and other similar Javascript frameworks (e.g Hyperapp_) that
try to be a little more *functional* (functional as in functional programming), a 
new problem was introduced to Javascript programmers (at least to those that weren't
familair with functional programming): How to keep their application's
state "immutable". 

Immutable means that the state should be an object that does not change (mutates) - instead
of changing it, Redux needs the state object to be `created from the beginning`_.

So when something happens in your application you need to discard 
the existing state object and create a new one from scratch by modifying and copying the previous state values.
This is easy
in most toy-apps that are used when introducing the concept, for example if your state is ``{counter: 0}``
then you could just define the reducer for the ``ADD`` action (i.e when the user clicks the ``+`` button) like this:

.. code-block:: javascript

    let reducer = (state={counter: 0}, action) => {
      switch (action.type) {
        case 'ADD': return { 'counter': state.counter+1 }
        default: return state
      }
    }

Unfortunately, your application will definitely have a much more complex state than this!

In the following, I'll do a quick introduction on how to keep your state objects immutable
using modern Javascript techniques, I'll present how complex it is to modify non-trivial 
immutable objects and finally I'll give you a quick recipe for modifying your non-trivial
immutable objects. If you want to play with the concepts I'll introduce you can do it at a
`playground I've created on repl.it`_.

Please keep in mind that this article has been written for ES6 - take a look at my
`browserify with ES6`_ article to see how you can also use it in your projects with
Browserify.

Also, if you'd like to see a non-toy React + Redux application or you'd like a gentle
introduction to the concepts I talked about (state, reducers, actions etc)
you can follow along my `React Redux tutorial`_. This is a rather old article 
(considering how quickly the Javascript framework state change) but the basic concepts
introduced there are true today.


Immutable objects
-----------------

Let's start our descent into avoiding mutations by supposing that you had 
something a little more complex than the initial example, for example your state was like this:

.. code-block:: javascript

    let state = {
        'counter': 0,
        'name': 'John',
        'age': 36
    }

If you continued the same example then your ``ADD`` reducer would need to return something like this 

.. code-block:: javascript

    return {
        'counter': state.counter+1,
        'name': state.name,
        'age': state.age
    }
    
This gets difficult and error prone very soon - and what happens if you later need to add another attribute to your state? 

The correct way to implement this would be to enumerate all properties of state except 'counter', copy them to a new
object, and then assign counter+1 to the new object's counter attribute. You could implement this by hand however,
thankfully, there's the `Object.assign`_ method! This method will copy all attributes from a list of objects 
to an object which will return as a result and is defined like this:

.. code-block:: javascript

    Object.assign(target, ...sources)
    
The ``target`` parameter is the object that will retrieve all attributes from ``sources`` (which is a variadic argument - you can
have as many sources as you want - even 0; in this case the target will be returned). For a quick example, running:

.. code-block:: javascript

    let o = {'a': 1}
    let oo = Object.assign(o, {'b': 2, 'c': 1}, {'c': 3})
    console.log(oo, o===oo)
    
will return ``{ a: 1, b: 2, c: 3 } true`` i.e the attributes 'b' and 'c' were copied to ``o`` and it was assigned to ``oo`` -- notice
that o and oo are the same object (thus ``o`` is modified now). Also, notice that the the attributes of objects to the right
have priority over the attributes of the objects to the left (``'c': 1`` was overriden by ``'c': 3``).

As you should have guessed by now, you should never pass the
state as the ``target`` but instead you should create a new object, thus the ``ADD`` reducer should return the following:

.. code-block:: javascript

    return Object.assign({}, state, {'counter': state.counter+1)
    
This means that it will create a new object which will copy all current attributes of state and increase the existing 
``counter`` attribute. 

I'd like to also add here that instead of using the ``Object.assign`` method you could use the `spread syntax`_
to more or less do the same. The spread syntax on an object takes this object's attributes and outputs them as key-value
dictionary pairs (for them to be used to initialize other objects). Thus, you can use the spread syntax to create an new object that has the same attributes
of another object like this:

.. code-block:: javascript
    
    let newState = {...state}
    // which is similar to 
    newState = Object.assign({}, state)
    
Of course you usually need to override some attributes, which can be passed directly to the newly created object,
for example for the ``ADD`` reducer:

.. code-block:: javascript

    return {...state, 'counter': state.counter+1 }

Like ``Object.assign``, you can have as many sources as you want in your spread syntax thus nothing stops you from using ``...`` multiple times to copy the attributes of multiple objects
for example you could define ``ADD`` like this: 

.. code-block:: javascript

    return {...state, ...{'counter': state.counter+1 } }
    
The order is similar to Object.assign, i.e the attributes that follow will override the previous ones. 

One final comment is that both ``Object.assign`` and copying objects with the spread syntax will do a "shallow"
copy i.e it will copy only the outer object, not the objects its keys refer to. An example of this behavior is that
if you run the following:

.. code-block:: javascript

    let a = {'val': 3 }
    let x = {a }
    let y = {...x}
    console.log(x, y)
    x['val2'] = 4
    y['val2'] = 5
    a['val'] = 33
    console.log(x, y)

you'll get:

.. code-block:: javascript

    { a: { val: 3 } } { a: { val: 3 } }
    { a: { val: 33 }, val2: 4 } { a: { val: 33 }, val2: 5 }   
    
i.e ``x`` and ``y`` got a different ``val2`` attribute since they not the same object, however both ``x`` and ``y``
have a reference to the *same* ``a`` thus when it's ``val`` attribute was changed this change appears to both ``x`` and ``y``!

    
What the above means is that if you have a state object containing
other objects (or arrays) you will also need to copy these children 
objects to keep your state immutable. We'll see examples on this later.

Immutable arrays
----------------    
    
One thing we haven't talked about yet is what happens if there's an array in the state, for example your state is 
``let state=[]`` and you have and ``APPEND`` reducer that puts something in the end of that array. The naive (and wrong)
way to do it is to call ``push`` directly to the state - this will mutate your state and is not be allowed! 

You need to copy the array elements and the tool for this job is Array.slice_. This methods takes two optional arguments (``begin`` 
and ``end``) that define the range of elements that will be copied; if you call it without arguments then it will copy
the whole array. Using slice, your ``APPEND`` reducer can be like this:

.. code-block:: javascript

    let newState = state.slice()
    newState.push('new element')
    return newState

Also, you could use the `Array.concat` method which will return a new array by copying all the elements of its
arguments

.. code-block:: javascript
    
    return state.concat(['new element'])
    
This will append ``new element`` to a new object that will have the elements of state (it won't modify the 
existing state) and is easier if you have this exact requirement. The advantage of slice is that you can 
use it to add/remove/modify elements from any place in the original array. For example, here's how you can
add an element after the first element of an array:

.. code-block:: javascript

    let x = ['a', 'b', 'c' ]
    let y = x.slice(0,1).concat(['second' ], x.slice(1,3))

Now ``y`` will be equal to ``[ 'a', 'second', 'b', 'c' ]``. So the above will get the first (0-th) element from the ``x``
array and concat it with another element (``second``) and the remaining elements of ``x``. Remember that ``x`` is not
modifyied since ``concat`` will create a new array.

In a similar fashion to objects, instead of using concat it is much easier to use the spread syntax. The spread syntax for
an array will output its elements one after the other for them to be used by other arrays. Thus, continuing from the
previous example, ``[...x]`` will return a new array with the elements of ``x`` (so it is similar to ``x.slice()`` or ``x.concat()``),
thus to re-generate the previous example you'll do something like 

.. code-block:: javascript

    let y = y=[...x.slice(0,1), 'second', ...x.slice(1,3)]

All three of concat, slice or the spread syntax will do a shallow copy (similar to how Object.assign works) so the same
conclusions from the previous section are true here: If you have arrays inside other arrays (or objects) you'll need to copy the inner
arrays recursively.
    
More complex cases
------------------

We'll now take a look at some more complex cases and see how quickly it gets difficult because of the shallow copying. 
Let's suppose that our state is the following:

.. code-block:: javascript

    const state = {
      'user': {
        'first_name': 'John',
        'last_name': 'Doe',
        'address': {
          'city': 'Athens',
          'country': 'Greece',
          'zip': '12345'
        }
      }
    }
    
and we want to assign a ``group`` attribute to the state. This can be easily done with ``assign``:

.. code-block:: javascript

    let groups = [{
        'name': 'group1'
    }]

    state = Object.assign({}, state, {
      'groups': groups
    })
    
or spread:

.. code-block:: javascript

    state = { 
      ...state, 'groups': groups
    }

Notice that instead of ``'groups': groups`` I could have used the `shorthand syntax`_ and written only ``groups`` and it would still work 
(i.e ``state = {...state, groups}`` is the same). In all cases, the resulting state will be:     

.. code-block:: javascript

    {
      'user': {
        'first_name': 'John',
        'last_name': 'Doe',
        'address': {
          'city': 'Athens',
          'country': 'Greece',
          'zip': '12345'
        }
      },
      'groups': [{
        'name': 'group1'
      }]
    }

From now on I'll only use the spread syntax which is more compact.  
    
Let's try to change the user's name. This is not as easy as the first example because we need to:

* Create a new copy of the ``user`` object with the new first name
* Create a new copy of the ``state`` object with the new user object created above

This can be done in two steps like this:

.. code-block:: javascript

    let user ={...state['user'], 'first_name': 'Jack'}
    state = {...state, user}

or in one step like this:

.. code-block:: javascript

    state = {...state, 'user':{
      ...state['user'], 'first_name': 'Jack'}
    }

The single step assignment is the combination of the two step described above. It is a little more complex
but it saves typing and is prefered because it allows the reducer function to have a single expression. Now
let's try to modify the user's zip code. We'll do it in three steps first:

.. code-block:: javascript

    let address ={...state['user']['address'], 'zip': '54321'}
    user ={...state['user'], address}
    state = {...state, user}
    
And now in one:

.. code-block:: javascript
   
    state = {...state, 'user': {
      ...state['user'], 'address': {
        ...state['user']['address'], 'zip': 54321
      }
    }}
    
Now, as can be seen in the above examples, modifying (without mutating) a compex state object 
is not very easy - it needs much thinking and is too error prone! This will be even more
apparent when we also get the array modifications into the equation, for example by adding another
two groups: 

.. code-block:: javascript
   
    state = {
      ...state, groups: [
        ...state['groups'].slice(), 
        {name: 'group2', id: 2},
        {name: 'group3', id: 3}
      ]
    }

The above copies the existing state and assigns to it a new ``groups`` object by copying
the existing groups and appending two more groups to that array! The state now will be:

.. code-block:: javascript

    { 
      user: { 
        first_name: 'Jack',
        last_name: 'Doe',
        address: { city: 'Athens', country: 'Greece', zip: 54321 } 
      },
      groups: [ 
        { name: 'group1' },
        { name: 'group2', id: 2 },
        { name: 'group3', id: 3 } 
      ] 
    }

As a final examply, how can we add the missing ``id`` attribute to the first group? 
Following the above techniques:

.. code-block:: javascript

    state = {
      ...state, groups: [
        {...state['groups'][0], 'id': 1},
        ...state['groups'].slice(1)
      ]
    }    

One more time what the above does? 

* Creates a new object and copies all existing properties of state to it
* Creates a new array which assigns it to the new state's ``groups`` attribute
* For the first element of that array it copies all attributes of the first element of state['groups'] and assings it an ``id=1`` attribute
* For the remaining elements of that array it copies all elements of state['groups] after the first one

Now think what would happen if we had an even more complex state with 3 or 4 nested levels!

Immutability's little helpers
-----------------------------

As you've seen from the previous examples, using immutable objects is not as easy as seems from
the toy examples. Actually, drilling down into complex immutable 
objects and returning new ones that have
some values changed  is a well-known problem in the functional world and has already a solution 
called "lenses". This is a funny name but it more or less means that you use a magnifying lens to look at
exactly the value you want and modify or retrieve it. The problem with lenses is that although they solve
the problem I mention is that if you want to use them you'll need to dive deep into functional
programming and also you'll need to include an extra library to your project (even if you only
want this specific capability). 

For completeness, here's the `the docs on lens`_ from Ramda_ which is a well known Javascript functional library.
This needs you to understand what is ``prop``, what is ``assoc`` and then how to use the lens with ``view``,
``set`` and ``over``. For me, these are way too much things to remember for such a specific thing. Also, notice
that the minified version of Ramda is around 45 kb which is not small. Yes, if I wanted
to fully use Ramda or a similar library I'd be delighted to use all these techniques and include it as a 
dependency - however most people prefer to stick with more familiar (and more procedural) concepts.

The helpers I'm going to present here are more or less a poor man's lens, i.e you will be able to use the basic
functionality of a lens but...

* without the peculiar syntax and 
* without the need to learn more functional concepts than what you'll want and 
* without the need to include any more external dependencies

Pretty good deal, no? 

In any case, a lens has two parts, a get and a set. The get will be used to drill down and retrieve a value from a 
complex object while the set will be used to drill down and assign a value to a complex object. The set does not 
modify the object but returns a new one. The get lens is not really needed since you can easily drill down to an
object using the good old index syntax but I'll include it here for completenes.

We'll start with the get which seems easier. For this, I'll just create a function that will take an object and 
a path inside that object as parameter and retrieve the value at that path. The path could be either a string of the form
'a.0.c.d' or an array ['a', '0', 'c', 'd'] - for numerical indeces we'll consider an array at that point.

Thus, for the object ``{'a': [{'b': {'c': {'d': 32} }}]}`` when the lens getter is called with either
``'a.0.b.c'`` or ['a', 0, 'b', 'c'] as the path, it should return ``{'d': 32}``.

To implement the get helper I will use a functional concept, ``reduce``. I've already explained this concept
in my `previous react-redux tutorial`_ so I urge you to read that article for more info. Using reduce we
can apply one by one accumulatively the members of the path to the initial object and the result will be 
the value of that path. Here's the implementation of ``pget`` (from property get):

.. code-block:: javascript

    const objgetter = (accumulator, currentValue) => accumulator[currentValue];
    const pget = (obj, path) =>  (
        (typeof path === 'string' || path instanceof String)?path.split('.'):path
    ).reduce(objgetter, obj)
    
I have defined an objgetter reducer function that gets an accumulated object and the current
value of the path and just returns the ``currentValue`` index of that accumulated object. Finally,
for the get lens (named ``pget``) I just check to see if the path is a string or an array (if it's
a string I split it on dots) and then I "reduce" the path using the objgetter defined above and
starting by the original object as the initial value. To understand how it is working, let's try calling it
for an object:

.. code-block:: javascript

    const s1 = {'a': [{'b': {'c': {'d': 32} }}]}
    console.log(pget(s1, ['a', 0, 'b', 'c']))

The above ``pget`` will call ``reduce`` on the passed array using the defined ``objgetter`` above
as the reducer function and ``s1`` as the original object. So, the reducer function will be called with
the following values each time:

==========================  ============
accumulator                 currentvalue
==========================  ============
``s1``                      ``'a'``
``s1['a']``                 ``0``
``s1['a'][0]``              ``'b'``
``s1['a'][0]['b']``         ``'c'``
``s1['a'][0]['b']['c']``        
==========================  ============

Thus the result will be exactly what we wanted ``{'d' :32}``. An interesting thing is that it's working
fine without the need to differentiate between arrays and objects because of how index access ``[]`` works.

Continuing for the set lens (which will be more difficult), I'll first represent a simple version that
works only with objects and an array path but displays the main idea of how this will work: It uses \
recursion i.e it will call itself to gradually build the new object. Here's how it is implemented:

.. code-block:: javascript

    const pset0 = (obj, path, val) => {
      let idx = path[0]
      
      if(path.length==1) {
        return {
          ...obj, [idx]: val
        }
      } else {
        let remaining = path.slice(1)
        return {
          ...obj,
          [idx]: pset0(...[obj[idx]], remaining, val)
        }
      }
    }

As already explained, I have assumed that the path is an array of indeces and that the ``obj`` is a complex object 
(no arrays in it please); the function returns a new object with the old object's value at the path be replaced 
with ``val``. This function checks to see if the path has only one element, if yes it will assign the value to that
attribute of the object it retrieve. If not, it will call itself recursively by skipping the current index and assign the return value to the
current index of the curent object. Let's see how it works for the following call:

.. code-block:: javascript

    const s2 = {a0: 0, a: {b0: 0, b: {c0: 0, c: 3}}}
    console.log(pset0(s2, ['a', 'b', 'c'], 4))

====== ============================= ======    
# Call Call parameters               Return 
====== ============================= ======
1      pset0(s2, ['a', 'b', 'c'], 4) {...s2, ['b']: pset0(s2['a'], ['b', 'c'], 4) }
2      pset0(s2['a'], ['b', 'c'], 4) {...s2['a'], ['c']: pset0(s2['a']['b'], ['c'], 4) }
3      pset0(s2['a']['b'], ['c'], 4) {...s2['a']['b'], ['c']: 4}
====== ============================= ======

Thus, the first time it will be called it will return a new object with the attributes of ``s2``
but overriding its ``'b'`` index with the return of the second call. The second call will return
a new object with the attributes of ``s2['a']`` but override it's ``'c'`` index with the return
of the third call. Finally, the 3rd call will return an object with the attributes of ``s2['a']['b']``
and setting the ``'c'`` index to ``4``. The result will be as expected equal to:

.. code-block:: javascript

    {a0: 0, a: {b0: 0, b: {c0: 0, c: 4 }}}

Now that we've understood the logic we can extend the above function with the following extras:

* support for arrays in the object using numerical indeces
* support for array (``['a', 'b']``) or string path (``'a.b'``) parameter
* support for a direct value to set on the path or a function that will be applied on that value

Here's the resulting set lens:

.. code-block:: javascript

    const pset = (obj, path, val) => {
      let parts = (typeof path === 'string' || path instanceof String)?path.split('.'):path
      const cset = (obj, cidx, val) => {
        let newval = val
        if (typeof val === "function") {
          newval = val(obj[cidx])
        } 
        if(Array.isArray(obj)) {
          return [
            ...obj.slice(0, cidx*1),
            newval,
            ...obj.slice(cidx*1+1)
            ]
        } else {
          return {
            ...obj, [cidx]: newval
          }
        }
      }
      
      let pidx = parts[0]
      if(parts.length==1) {
        return cset(obj, pidx, val) 
      } else {
        let remaining = parts.slice(1)
        return cset(obj, pidx, pset(obj[pidx], remaining, val)) 
      }
    }

It may seem a little complex but I think it's easy to be understood: The parts in the beginning
will just check to see if the path is an array or a string and split the string to its parts.
The ``cset`` function that follows is a local function that is used to make the copy of the object
or array and set the new value. Here's how it is working: It will first check to see if the ``val``
parameter is a function or a not. If it is a function it will apply this function to the object's index
to get the ``newvalue`` else it will just use ``val`` as the ``newvalue``. After that it checks if the
object it got is an array or not. If it is an array it will do the slice trick we saw before to copy
the elements of the array except the ``newval`` which will put it at the index (notice that the index
at that point must be numerical but that's up to you to assert). If the current ``obj`` is not an array
then it must be an object thus it uses the spread syntax to copy the object's attributes and reassign
the current index to ``newval``.

The last part of ``pset`` is similar to the ``pset0`` it just uses ``cset`` to do the new object/array
generation instead of doing it in place like ``pset0`` - as already explained, ``pset`` is called recursively
until only one element remains on the path in which case the ``newval`` will be assigned to the current index of 
the current ``obj``.

Let's try to use ``pset`` for the following rather complex state:

.. code-block:: javascript

    let state2 = {
      'users': {
        'results': [
          {'name': 'Sera', 'groups': ['g1', 'g2', 'g3']},
          {'name': 'John', 'groups': ['g1', 'g2', 'g3']},
          {'name': 'Joe', 'groups': []}
        ],
        'pagination': {
          'total': 100,
          'perpage': 5,
          'number': 0
        }
      },
      'groups': {
        'results': [
        ]
        ,
        'total': 0
      }
    }

Let's call it three times one after the other to change various attributes: 

.. code-block:: javascript
    
    let new_state2 = pset(
        pset(
            pset(
                pset(state2, "users.results.2.groups.0", 'aa'), 
            "users.results.0.name", x=>x.toUpperCase()), 
        "users.total", x=>x+1), 
    'users.results.1.name', 'Jack')

And here's the result:
    
.. code-block:: javascript

    {
        "users": {
            "results": [{
                "name": "SERA",
                "groups": ["g1", "g2", "g3"]
            }, {
                "name": "Jack",
                "groups": ["g1", "g2", "g3"]
            }, {
                "name": "Joe",
                "groups": ["aa"]
            }],
            "pagination": {
                "total": 101,
                "perpage": 5,
                "number": 0
            }
        },
        "groups": {
            "results": [],
            "total": 0
        }
    }
    
This should be self explanatory.

I've published the above immutable little helpers as an npm package: https://www.npmjs.com/package/poor-man-lens (yes I
decided to use the poor man lens name instead of the immutable little helpers) - they are too simple and could be easily
copied and pasted to your project but I've seen even smaller npm packages and I wanted to try to see if it is easy to
publish a package to npm (answer: it is very easy - easier than python's pip). Also there's a github repository for
these utils in case somebody wants to contribute anything or look at the source: https://github.com/spapas/poor-man-lens.

Notice that this package has been written in ES5 (and actually has a polyfil for Object.assign) thus you should probably
be able to use it anywhere you want, even directly from the browser by directly including the ``pml.js`` file.

Conclusion
----------

Using the above techniques you should be able to easily keep your state objects immutable. For simple cases you
can stick to the spread syntax or Object.assign / Array.slice but for more complex cases you may want to consider
either copying directly the pset and pget utils I explained above or just using the `poor-man-lens npm package`. 


.. _`Redux`: https://redux.js.org
.. _`Hyperapp`: https://hyperapp.js.org
.. _`created from the beginning`: https://redux.js.org/basics/reducers
.. _`React Redux tutorial`: https://spapas.github.io/2016/03/02/react-redux-tutorial/
.. _`Object.assign`: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Object/assign
.. _`spread syntax`: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Spread_syntax
.. _`Array.slice`: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/slice
.. _`Array.concat`: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/concat
.. _`playground I've created on repl.it`: https://repl.it/@spapas/JS-Drill-Down-objectarray-immutable
.. _`shorthand syntax`: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Object_initializer#Syntax
.. _`the docs on lens`: http://ramdajs.com/docs/#lens
.. _Ramda: http://ramdajs.com
.. _`previous react-redux tutorial`: https://spapas.github.io/2016/03/02/react-redux-tutorial/#interlude-so-what-s-a-reducer
.. _`browserify with ES6`: https://spapas.github.io/2015/11/16/using-browserify-es6/
.. _`poor-man-lens npm package`: https://www.npmjs.com/package/poor-man-lens