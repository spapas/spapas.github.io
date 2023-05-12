Title: HTML form disable after submit
Date: 2023-05-12 15:20
Tags: html, javascript
Category: html
Slug: disable-your-forms
Author: Serafeim Papastefanos
Summary: A simple way to improve the functionality of your HTML forms by disabling the submit button after submitting.


One of the most common problems I get in my apps is double submissions of forms. A lot of users
can't understand the difference between single and double click and end up double clicking
the form submit button. Also, if the form takes too long to submit they might thing that they didn't
press the button correctly and click it again.

This, depending on how your app is built could result in either working perfectly, or showing errors
to users or (which is the worst) duplicate entries in your database.

There is a *very simple* fix for that: Disable the submit button after the first click. Here's how to
do it with jQuery:

```javascript

$(document).ready(function () {
    $('form').submit(function () {
        let submit = $(this).find(':input[type=submit]')
        submit.prop('disabled', true);
        if(submit.val()) {
            submit.val(submit.val() + ' ⌛' )
        } else {
            submit.html(submit.html() + ' ⌛')
        }
    })
});

```


and with vanilla.js if you don't use jquery

```javascript

document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('form').forEach(function (form) {
        form.addEventListener('submit', function (event) {
            let submit = this.querySelector('input[type="submit"], button[type="submit"]');
            submit.disabled = true;
            if(submit.value) {
                submit.value = submit.value + ' ⌛';
            } else {
                submit.innerHTML = submit.innerHTML + ' ⌛';
            }
        });
    });
});

```

The above will find all forms and add an event listener to the submit event. When the form is submitted
it will find the submit button and disable it. Finally, it adds a unicode hourglass character (⌛) to the 
displayed button text so the user gets a quick feedback that the form is being submitted.

The above snippets  should work correctly no matter if you use 
an `<input type="submit">` or a `<button type="submit">` element (that's why we use `:input` in jquery to capture both types of elements or we do the double check on the `querySelector`, also notice that it checks if the element has a `val()/value` and sets 
sets `val()/value` or `html()/innerHTML` accordingly).

I use the above snippet on every project I work on and it has saved me a lot of headaches. Please be advised that if you do funny JS things with your form this snippet may not work and break its functionality, but in this case you are probably handling the form disabling yourself.