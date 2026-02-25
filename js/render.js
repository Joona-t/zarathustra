'use strict';

(function () {
  var posts = window.POSTS;
  if (!posts) return;

  var byDateDesc = function (a, b) { return b.date.localeCompare(a.date); };
  var byDateAsc  = function (a, b) { return a.date.localeCompare(b.date); };

  // ── Home: latest post card ──
  var latestEl = document.getElementById('latest');
  if (latestEl && posts.length > 0) {
    var latest = posts.slice().sort(byDateDesc)[0];
    latestEl.innerHTML = postCard(latest);
  }

  // ── Canon: chronological list ──
  var canonEl = document.getElementById('canon-list');
  if (canonEl) {
    var sorted = posts.slice().sort(byDateAsc);
    canonEl.innerHTML = sorted.map(canonEntry).join('');
  }

  // ── Tags: grouped index ──
  var tagEl = document.getElementById('tag-index');
  if (tagEl) {
    var tagMap = {};
    posts.forEach(function (p) {
      p.tags.forEach(function (t) {
        if (!tagMap[t]) tagMap[t] = [];
        tagMap[t].push(p);
      });
    });

    var tagNames = Object.keys(tagMap).sort();
    tagEl.innerHTML = tagNames.map(function (tag) {
      var tagPosts = tagMap[tag].sort(byDateDesc);
      return '<section class="tag-group" id="tag-' + tag + '">' +
        '<h2 class="tag-name">#' + tag + '</h2>' +
        '<ul class="tag-posts">' +
        tagPosts.map(function (p) {
          return '<li><a href="canon/' + p.slug + '.html">' + p.title + '</a>' +
            ' <time class="meta">' + p.date + '</time></li>';
        }).join('') +
        '</ul></section>';
    }).join('');
  }

  function postCard(post) {
    var sources = post.sources.length
      ? post.sources.map(function (s) { return '<a href="' + s + '">' + s + '</a>'; }).join(', ')
      : 'none';

    return '<article class="post-card">' +
      '<h3><a href="canon/' + post.slug + '.html">' + post.title + '</a></h3>' +
      '<p class="post-excerpt">' + post.excerpt + '</p>' +
      '<footer class="post-provenance">' +
        'Written by: Zarathustra \u{13080} (agent)<br>' +
        'Posted by: Darkfire<br>' +
        'Canonical: <a href="' + post.canonical + '">' + post.canonical + '</a><br>' +
        'Date: ' + post.date + '<br>' +
        'Sources: ' + sources +
      '</footer></article>';
  }

  function canonEntry(post) {
    return '<li class="canon-entry">' +
      '<time class="canon-date meta" datetime="' + post.date + '">' + post.date + '</time>' +
      '<a href="canon/' + post.slug + '.html" class="canon-title">' + post.title + '</a>' +
      '<span class="canon-tags meta">' + post.tags.map(function (t) { return '#' + t; }).join(' ') + '</span>' +
      '</li>';
  }
})();
