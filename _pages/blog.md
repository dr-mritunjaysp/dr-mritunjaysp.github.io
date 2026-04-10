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
      <div class="travel-quote-wrap">
        <p class="travel-kicker">Nature Notes</p>
        <p
          class="travel-typed-quote"
          id="travel-typed-quote"
          data-quotes='[
            "Take only memories, leave only footprints, and keep walking toward wonder.",
            "Every journey writes a quiet poem in the language of mountains, rain, and light.",
            "Travel slows the heart enough to notice how beautiful the world already is.",
            "Roads do not only lead to places; they lead us back to ourselves."
          ]'
        ></p>
      </div>
    </div>

    {% assign travel_posts = site.posts | where_exp: "post", "post.categories contains 'travel'" | sort: "date" | reverse %}

    <div class="row row-cols-1 row-cols-sm-2 row-cols-lg-4 compact-travel-row">
      {% for post in travel_posts %}
        {% include travel_post_card.liquid %}
      {% endfor %}
    </div>
  </div>
</div>

<script>
  document.addEventListener('DOMContentLoaded', () => {
    const quoteEl = document.getElementById('travel-typed-quote');
    if (!quoteEl) return;

    const quotes = JSON.parse(quoteEl.dataset.quotes || '[]');
    if (!quotes.length) return;

    let quoteIndex = 0;
    let charIndex = 0;
    let deleting = false;

    const typeLoop = () => {
      const currentQuote = quotes[quoteIndex];

      if (!deleting) {
        charIndex += 1;
        quoteEl.textContent = currentQuote.slice(0, charIndex);

        if (charIndex >= currentQuote.length) {
          deleting = true;
          window.setTimeout(typeLoop, 1800);
          return;
        }

        window.setTimeout(typeLoop, 42);
        return;
      }

      charIndex -= 1;
      quoteEl.textContent = currentQuote.slice(0, charIndex);

      if (charIndex <= 0) {
        deleting = false;
        quoteIndex = (quoteIndex + 1) % quotes.length;
        window.setTimeout(typeLoop, 260);
        return;
      }

      window.setTimeout(typeLoop, 18);
    };

    quoteEl.textContent = '';
    typeLoop();
  });
</script>
