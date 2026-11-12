/* Free Stack site script: theme, search, copy, highlighting, TOC, mobile nav. */
(function () {
  'use strict';
  var root = document.documentElement;

  /* ---------- Theme ---------- */
  function setTheme(t) {
    root.setAttribute('data-theme', t);
    try { localStorage.setItem('fs-theme', t); } catch (e) {}
    document.querySelectorAll('[data-theme-label]').forEach(function (el) {
      el.textContent = t === 'dark' ? 'Light mode' : 'Dark mode';
    });
  }
  document.querySelectorAll('[data-theme-toggle]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      setTheme(root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark');
    });
  });
  setTheme(root.getAttribute('data-theme') || 'light');

  /* ---------- Mobile nav ---------- */
  var body = document.body;
  document.querySelectorAll('[data-nav-open]').forEach(function (b) {
    b.addEventListener('click', function () { body.classList.add('nav-open'); });
  });
  document.querySelectorAll('[data-nav-close]').forEach(function (b) {
    b.addEventListener('click', function () { body.classList.remove('nav-open'); });
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') body.classList.remove('nav-open');
  });

  /* ---------- Syntax highlighting (small, dependency free) ---------- */
  var KEYWORDS = {
    js: 'import export from const let var function async await return if else for of in new class extends try catch throw default true false null undefined typeof',
    ts: 'import export from const let var function async await return if else for of in new class extends try catch throw default true false null undefined typeof type interface as',
    py: 'import from def async await return if elif else for in while with as class try except finally raise True False None and or not lambda pass',
    sql: 'create table alter add enable row level security policy on for to using with check select insert update delete from where and or not null primary key references default unique index as public auth publication returns language begin end function trigger execute grant revoke',
    yaml: 'true false null',
    sh: 'export cd echo sudo',
    json: 'true false null'
  };
  function esc(s) { return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;'); }
  function highlight(code, lang) {
    var kw = KEYWORDS[lang];
    if (!kw) return esc(code);
    var kwSet = {};
    kw.split(' ').forEach(function (k) { kwSet[k] = 1; });
    var ci = lang === 'sql';
    var comment = lang === 'py' || lang === 'yaml' || lang === 'sh' ? '#' : lang === 'sql' ? '--' : '//';
    var out = '', i = 0, n = code.length;
    while (i < n) {
      var c = code[i];
      // comments (for '#', only at line start or after whitespace)
      if (code.startsWith(comment, i) && (comment !== '#' || i === 0 || /\s/.test(code[i - 1]))) {
        var end = code.indexOf('\n', i); if (end < 0) end = n;
        out += '<span class="tk-c">' + esc(code.slice(i, end)) + '</span>'; i = end; continue;
      }
      if (c === '"' || c === "'" || c === '`') {
        var j = i + 1;
        while (j < n && code[j] !== c && code[j] !== '\n') { if (code[j] === '\\') j++; j++; }
        out += '<span class="tk-s">' + esc(code.slice(i, j + 1)) + '</span>'; i = j + 1; continue;
      }
      if (/[A-Za-z_]/.test(c)) {
        var k = i; while (k < n && /[A-Za-z0-9_]/.test(code[k])) k++;
        var w = code.slice(i, k);
        out += kwSet[ci ? w.toLowerCase() : w] ? '<span class="tk-k">' + w + '</span>' : w;
        i = k; continue;
      }
      if (/[0-9]/.test(c) && (i === 0 || !/[A-Za-z_]/.test(code[i - 1]))) {
        var m = i; while (m < n && /[0-9._]/.test(code[m])) m++;
        out += '<span class="tk-n">' + code.slice(i, m) + '</span>'; i = m; continue;
      }
      out += esc(c); i++;
    }
    return out;
  }
  document.querySelectorAll('pre[data-lang]').forEach(function (pre) {
    var lang = pre.getAttribute('data-lang');
    pre.innerHTML = highlight(pre.textContent, lang);
  });

  /* ---------- Copy buttons ---------- */
  document.querySelectorAll('.copy').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var pre = btn.closest('.codeblock').querySelector('pre');
      var text = pre.textContent;
      var done = function () {
        btn.textContent = 'Copied';
        setTimeout(function () { btn.textContent = 'Copy'; }, 1600);
      };
      if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(text).then(done, function () {});
      } else {
        var ta = document.createElement('textarea');
        ta.value = text; ta.style.position = 'fixed'; ta.style.opacity = '0';
        document.body.appendChild(ta); ta.select();
        try { document.execCommand('copy'); done(); } catch (e) {}
        ta.remove();
      }
    });
  });

  /* ---------- On this page: highlight current section ---------- */
  var tocLinks = Array.prototype.slice.call(document.querySelectorAll('.toc a'));
  if (tocLinks.length && 'IntersectionObserver' in window) {
    var map = {};
    tocLinks.forEach(function (a) { map[a.getAttribute('href').slice(1)] = a; });
    var visible = {};
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { visible[e.target.id] = e.isIntersecting; });
      var heads = document.querySelectorAll('.prose h2[id]');
      var current = null;
      for (var i = 0; i < heads.length; i++) {
        if (heads[i].getBoundingClientRect().top < window.innerHeight * 0.35) current = heads[i].id;
      }
      if (!current && heads.length) current = heads[0].id;
      tocLinks.forEach(function (a) { a.classList.remove('active'); });
      if (current && map[current]) map[current].classList.add('active');
    }, { rootMargin: '0px 0px -60% 0px', threshold: [0, 1] });
    document.querySelectorAll('.prose h2[id]').forEach(function (h) { io.observe(h); });
    window.addEventListener('scroll', function () {
      if (window.innerHeight + window.scrollY >= document.body.scrollHeight - 4) {
        tocLinks.forEach(function (a) { a.classList.remove('active'); });
        tocLinks[tocLinks.length - 1].classList.add('active');
      }
    }, { passive: true });
  }

  /* ---------- Search ---------- */
  var input = document.querySelector('.search input');
  var box = document.querySelector('.results');
  var index = window.FS_SEARCH || [];
  var sel = -1;
  function render(q) {
    q = q.trim().toLowerCase();
    if (!q) { box.classList.remove('open'); box.innerHTML = ''; return; }
    var words = q.split(/\s+/);
    var hits = index.filter(function (it) {
      var hay = (it.t + ' ' + it.g + ' ' + (it.k || '')).toLowerCase();
      return words.every(function (w) { return hay.indexOf(w) !== -1; });
    }).slice(0, 8);
    sel = hits.length ? 0 : -1;
    box.innerHTML = hits.length
      ? hits.map(function (h, i) {
          return '<a href="' + h.u + '"' + (i === 0 ? ' class="active"' : '') + '>' + esc(h.t) + '<span>' + esc(h.g) + '</span></a>';
        }).join('')
      : '<p>No matches. Try a product name or a word like "keys" or "webhook".</p>';
    box.classList.add('open');
  }
  if (input && box) {
    input.addEventListener('input', function () { render(input.value); });
    input.addEventListener('keydown', function (e) {
      var items = box.querySelectorAll('a');
      if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
        if (!items.length) return;
        e.preventDefault();
        sel = (sel + (e.key === 'ArrowDown' ? 1 : -1) + items.length) % items.length;
        items.forEach(function (a, i) { a.classList.toggle('active', i === sel); });
      } else if (e.key === 'Enter' && sel >= 0 && items[sel]) {
        window.location.href = items[sel].getAttribute('href');
      } else if (e.key === 'Escape') {
        input.value = ''; render(''); input.blur();
      }
    });
    document.addEventListener('click', function (e) {
      if (!e.target.closest('.search')) box.classList.remove('open');
    });
    document.addEventListener('keydown', function (e) {
      var typing = /INPUT|TEXTAREA/.test(document.activeElement.tagName);
      if ((e.key === 'k' && (e.metaKey || e.ctrlKey)) || (e.key === '/' && !typing)) {
        e.preventDefault();
        body.classList.add('nav-open');
        input.focus();
      }
    });
  }

  /* ---------- Home: "What are you building?" ---------- */
  document.querySelectorAll('.ask-opts button').forEach(function (b) {
    b.addEventListener('click', function () {
      var open = b.getAttribute('aria-pressed') === 'true';
      document.querySelectorAll('.ask-opts button').forEach(function (x) { x.setAttribute('aria-pressed', 'false'); });
      document.querySelectorAll('.recipe').forEach(function (r) { r.classList.remove('open'); });
      if (!open) {
        b.setAttribute('aria-pressed', 'true');
        var r = document.getElementById(b.getAttribute('aria-controls'));
        if (r) r.classList.add('open');
      }
    });
  });
})();
