'use strict';

document.addEventListener('DOMContentLoaded',() => {
  const forms = document.querySelectorAll('.form_to_change'),
        way = document.getElementById('way');


  forms.forEach((item,i) => {
    item.addEventListener('change',() => {
      way.submit();
    });
  });
});
