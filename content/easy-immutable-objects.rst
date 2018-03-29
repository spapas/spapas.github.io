Easy immutable objects in Javascript
####################################

:date: 2018-03-28 11:20
:tags: javascript, react, redux, hyperapp, immutable, es6
:category: javascript
:slug: easy-immutable-objects
:author: Serafeim Papastefanos
:summary: How to install and use both Python 2.x and 3.x on Windows
:status: draft

With the rise of Redux_ and other similar frameworks (e.g Hyperapp_) that
try to be a little more *functional* (functional as in functional programming), a 
new problem was introduced to Javascript programmers (at least to those that weren't
familair with functional programming): How to keep their application's
state "immutable". 

Immutable means that the state should be an object that does not change (mutates) - instead
of changing it, Redux needs the state object to be `created from the beginning`_. So when
something happens in your application you need to discard 
the existing state object and create a new one from scratch by modifying and copying the previous state values.
This is easy
in most toy-apps that are used when introducing the concept for example if your state is ``{counter: 0}``
then you could just define the reducer for the ``ADD`` action (i.e when the user clicks the ``+`` button) like this:

.. code-block:: javascript

    let reducer = (state={counter: 0}, action) => {
      switch (action.type) {
        case 'ADD': return { 'counter': state.counter+1 }
        default: return state
      }
    }
    

Notice that if you'd like to see a non-toy React + Redux application or you'd like a gentle
introduction to the concepts I talked about (state, reducers, actions etc)
you can follow along my `React Redux tutorial`_.

In the following, I'll do a quick introduction on how to keep your state objects immutable
using modern Javascript techniques, I'll present how complex it is to modify non-trivial 
immutable objects and finally I'll give you a quick recipe for modifying your non-trivial
immutable objects. If you want to play with the concepts I'll introduce you can do it at a
`playground I've created on repl.it`_

Immutable objects
-----------------

The example I gave in the introduction was easy and nice however usually you won't have such 
a small state! Let's suppose that you had something a little more complex, for example your state was like this:

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

Thankfully, there's the `Object.assign`_ method! This method will copy all attributes from a list of objects 
to an object which will return as a result and is defined like this:

.. code-block:: javascript

    Object.assign(target, ...sources)
    
The ``target`` parameter is the object that will retrieve all attributes from ``sourcess`` (which is a variadic argument you can
have as many sources as you want - even 0; in this case the target will be returned). For a quick example, running

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

One final comment is that nothing stops you from using ``...`` multiple times to copy the attributes of multiple objects
for example you could define ``ADD`` like this: 

.. code-block:: javascript

    return {...state, ...{'counter': state.counter+1 } }

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


More complex cases
------------------

We'll now take a look at some more complex cases and see how quickly it gets difficult. Let's suppose that our state is the following:

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
but it saves typing and is prefered because it allows the reducer function to have a single expression. This 
will be made more clear with the third example, trying to modify the user's zip code. Let's do it in three
steps first:

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
this is not very easy - it needs much thinking and is too error prone! This will be even more
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

The state now will be 

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

How can we add the missing 'id' attribute to the first group? "Easy" (depending on what your defintion of easy is):

.. code-block:: javascript

    state = {
      ...state, groups: [
        {...state['groups'][0], 'id': 1},
        ...state['groups'].slice(1)
      ]
    }    

One more time what the above does? 

* Creates a new object and copies all existing properties of state to it
* Creates a new array which assigns it to the new state's groups
* For the first element of that array it copies all attributes of the first element of state['groups'] and assings it an ``id=1`` attribute
* For the remaining elements of that array it copies all elements of state['groups] after the first one


    
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