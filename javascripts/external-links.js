// Open external links in a new tab. Runs on every page load AND on every
// instant-navigation swap (Material's `navigation.instant` replaces content
// via fetch, so a plain DOMContentLoaded listener would only fire once).
function markExternalLinks() {
  var host = window.location.hostname;
  document.querySelectorAll('a[href^="http"]').forEach(function (link) {
    if (link.hostname && link.hostname !== host) {
      link.setAttribute('target', '_blank');
      link.setAttribute('rel', 'noopener noreferrer');
    }
  });
}

if (window.document$) {
  // Material's instant-navigation observable — fires on first load and on
  // every subsequent client-side page swap.
  document$.subscribe(markExternalLinks);
} else {
  document.addEventListener('DOMContentLoaded', markExternalLinks);
}
