(function() {
    const links = Array.from(new Set(Array.from(document.querySelectorAll('a')).map(a => a.href)));
    return { links: links };
  })();
  