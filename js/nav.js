'use strict';

(function () {
  var path = window.location.pathname;
  var links = document.querySelectorAll('.nav-links a');

  links.forEach(function (link) {
    link.classList.remove('active');
    var href = link.getAttribute('href');
    if (path.endsWith(href) || (href === 'index.html' && (path === '/' || path.endsWith('/')))) {
      link.classList.add('active');
    }
    // Post pages: highlight "canon"
    if (path.indexOf('/canon/') !== -1 && href === 'canon.html') {
      link.classList.add('active');
    }
  });
})();
