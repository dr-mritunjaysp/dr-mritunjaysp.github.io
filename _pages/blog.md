---
layout: default
permalink: /blog/
title: Blog
nav: true
nav_order: 1
---

<div class="post">
  <div class="projects travel-blog-grid">
    <div class="header-bar">
      <h1>Travel Blog</h1>
      <h2>Stories, notes, and snapshots from memorable journeys.</h2>
    </div>

    {% assign travel_posts = site.posts | where_exp: "post", "post.categories contains 'travel'" | sort: "date" | reverse %}

    <div class="row row-cols-1 row-cols-md-3">
      {% for post in travel_posts %}
        {% include travel_post_card.liquid %}
      {% endfor %}
    </div>
  </div>
</div>
