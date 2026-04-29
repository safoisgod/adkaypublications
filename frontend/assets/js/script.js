/* ============================================================
   A-D KAY PUBLICATIONS — Integrated script.js
   P1 GSAP animations + P2 Backend API logic
   ============================================================ */

'use strict';

/* ─────────────────────────────────────────────────────────────
   1. CONFIGURATION
   ───────────────────────────────────────────────────────────── */
const CONFIG = {
  API_BASE: 'https://adkaypublications.com',
  ENDPOINTS: {
    books:      '/api/books/',
    book:       (slug) => `/api/books/${slug}/`,
    blog:       '/api/blog/posts/',
    post:       (slug) => `/api/blog/posts/${slug}/`,
    authors:    '/api/authors/',
    author:     (slug) => `/api/authors/${slug}/`,
    services:   '/api/services/',
    search:     (q)    => `/api/search/?q=${encodeURIComponent(q)}`,
    contact:    '/api/contact/',
    newsletter: '/api/newsletter/subscribe/',
  },
};

/* ─────────────────────────────────────────────────────────────
   2. API UTILITY
   ───────────────────────────────────────────────────────────── */
const API = {
  async fetch(endpoint, options = {}) {
    const url = CONFIG.API_BASE + endpoint;
    const defaults = { headers: { 'Content-Type': 'application/json' }, ...options };
    const response = await fetch(url, defaults);
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      console.log('API Error full response:', JSON.stringify(errorData, null, 2)); // ADD THIS
      const unwrapped = errorData.data || errorData;
      const msg = unwrapped.detail
        || Object.entries(unwrapped)
            .filter(([k]) => k !== 'status')
            .map(([k, v]) => `${k}: ${[].concat(v).join(', ')}`)
            .join(' | ')
        || `HTTP ${response.status}`;
      throw new Error(msg);
    }
    return response.json();
  },

  getBooks:    ()     => API.fetch(CONFIG.ENDPOINTS.books),
  getBook:     (slug) => API.fetch(CONFIG.ENDPOINTS.book(slug)),
  getPosts:    ()     => API.fetch(CONFIG.ENDPOINTS.blog),
  getPost:     (slug) => API.fetch(CONFIG.ENDPOINTS.post(slug)),
  getAuthors:  ()     => API.fetch(CONFIG.ENDPOINTS.authors),
  getServices: ()     => API.fetch(CONFIG.ENDPOINTS.services),
  getAuthor:   (slug) => API.fetch(CONFIG.ENDPOINTS.author(slug)),
  search:      (q)    => API.fetch(CONFIG.ENDPOINTS.search(q)),
  postContact:    (data) => API.fetch(CONFIG.ENDPOINTS.contact,    { method: 'POST', body: JSON.stringify(data) }),
  postNewsletter: (data) => API.fetch(CONFIG.ENDPOINTS.newsletter, { method: 'POST', body: JSON.stringify(data) }),
  imgUrl: (path) => {
    if (!path) return 'https://placehold.co/400x600/1a2d6b/ffffff?text=No+Cover';
    if (path.startsWith('http')) return path;
    return CONFIG.API_BASE + path;
  },
};

const toArray = (data) => {
  if (Array.isArray(data)) return data;
  if (data?.data  && Array.isArray(data.data))    return data.data;
  if (data?.results && Array.isArray(data.results)) return data.results;
  return [];
};

/* ─────────────────────────────────────────────────────────────
   3. HELPERS
   ───────────────────────────────────────────────────────────── */
const getParam   = (key) => new URLSearchParams(window.location.search).get(key);
const formatDate = (iso) => iso ? new Date(iso).toLocaleDateString('en-US', { year:'numeric', month:'long', day:'numeric' }) : '';
const truncate   = (str = '', max = 160) => str.length > max ? str.slice(0, max).trimEnd() + '…' : str;
const onPage     = (...pages) => pages.some(p =>
  window.location.pathname.includes(p) ||
  (p === 'index' && (window.location.pathname === '/' || window.location.pathname.endsWith('index.html')))
);

/* ─────────────────────────────────────────────────────────────
   4. SKELETON / EMPTY STATE
   ───────────────────────────────────────────────────────────── */
const Skeleton = {
  books: (n = 4) => Array.from({ length: n }, () => `
    <div class="skeleton-card">
      <div class="skeleton skeleton-cover"></div>
      <div class="skeleton skeleton-line w-60" style="margin-top:14px"></div>
      <div class="skeleton skeleton-line w-40"></div>
    </div>`).join(''),
  blog: (n = 3) => Array.from({ length: n }, () => `
    <div class="skeleton-card">
      <div class="skeleton skeleton-blog-thumb"></div>
      <div class="skeleton skeleton-line" style="margin-top:16px"></div>
      <div class="skeleton skeleton-line w-60"></div>
      <div class="skeleton skeleton-line w-40"></div>
    </div>`).join(''),
  team: (n = 4) => Array.from({ length: n }, () => `
    <div class="skeleton-card" style="text-align:center;padding:1rem">
      <div class="skeleton" style="width:160px;height:160px;border-radius:50%;margin:0 auto 1rem"></div>
      <div class="skeleton skeleton-line w-60" style="margin:0 auto 0.5rem"></div>
      <div class="skeleton skeleton-line w-40" style="margin:0 auto"></div>
    </div>`).join(''),
  services: (n = 3) => Array.from({ length: n }, () => `
    <div class="skeleton-card" style="padding:2rem">
      <div class="skeleton" style="width:48px;height:48px;border-radius:50%;margin-bottom:1.5rem"></div>
      <div class="skeleton skeleton-line w-60"></div>
      <div class="skeleton skeleton-line"></div>
      <div class="skeleton skeleton-line w-40"></div>
    </div>`).join(''),
};

const emptyState = (title = 'Nothing here yet', msg = '') => `
  <div class="empty-state">
    <div class="empty-state-icon">◈</div>
    <h3>${title}</h3>
    ${msg ? `<p>${msg}</p>` : ''}
  </div>`;

/* ─────────────────────────────────────────────────────────────
   5. RENDER FUNCTIONS — use P1 class names so existing CSS applies
   ───────────────────────────────────────────────────────────── */

function renderBookCard(book, linkToDetail = true) {
  const coverSrc = API.imgUrl(book.cover_url || book.image || book.cover);
  const author   = book.author_names || book.author || '';
  const genre    = book.genre?.name  || book.genre  || '';
  const detail   = `book-detail.html?slug=${book.slug}`;
  return `
    <div class="book-card" data-genre="${genre.toLowerCase()}"
         ${linkToDetail ? `style="cursor:pointer" onclick="window.location='${detail}'"` : ''}>
      <div class="book-card-img">
        <img src="${coverSrc}" alt="${book.title}" loading="lazy">
        <div class="book-card-overlay">
          <span class="book-title">${book.title}</span>
          <span class="book-author">${author}</span>
        </div>
      </div>
      <div class="book-card-info">
        <p class="book-title">${book.title}</p>
        <p class="book-author">${author}</p>
        ${genre ? `<span class="book-genre">${genre}</span>` : ''}
      </div>
    </div>`;
}

function resolveAuthor(post) {
  if (typeof post.author_name === 'string' && post.author_name) return post.author_name;
  if (post.author && typeof post.author === 'object') {
    return post.author.full_name || post.author.name ||
      `${post.author.first_name || ''} ${post.author.last_name || ''}`.trim() ||
      post.author.username || 'Editorial Team';
  }
  if (typeof post.author === 'string' && post.author) return post.author;
  return 'Editorial Team';
}

function renderBlogCard(post) {
  const imgSrc  = API.imgUrl(post.cover_url || post.image || post.cover);
  const author  = resolveAuthor(post);
  const catName = post.category?.name || (typeof post.category === 'string' ? post.category : '') || '';
  const date    = formatDate(post.published_at || post.date || post.created_at);
  return `
    <div class="blog-card" style="cursor:pointer" onclick="window.location='blog-detail.html?slug=${post.slug}'">
      <div class="blog-img">
        <img src="${imgSrc}" alt="${post.title}" loading="lazy">
      </div>
      <div class="blog-content">
        ${catName ? `<p class="blog-tag">${catName}</p>` : ''}
        <h3 class="blog-title">${post.title}</h3>
        <p class="blog-excerpt">${truncate(post.excerpt || '', 130)}</p>
        <div class="blog-meta">
          ${date ? `<span>${date}</span>` : ''}
          ${post.reading_time ? `<span>·</span><span>${post.reading_time} min read</span>` : ''}
          ${author ? `<span>·</span><span>By ${author}</span>` : ''}
        </div>
      </div>
    </div>`;
}

function renderFeaturedPost(post) {
  const imgSrc  = API.imgUrl(post.cover_url || post.image || post.cover);
  const author  = resolveAuthor(post);
  const catName = post.category?.name || (typeof post.category === 'string' ? post.category : '') || '';
  const date    = formatDate(post.published_at || post.date || post.created_at);
  return `
    <div class="blog-featured fade-up">
      <a href="blog-detail.html?slug=${post.slug}">
        <div class="blog-img">
          <img src="${imgSrc}" alt="${post.title}" loading="lazy">
        </div>
      </a>
      <div class="blog-content">
        <p class="blog-tag">${catName ? catName + ' · ' : ''}Featured</p>
        <h2 class="blog-title">${post.title}</h2>
        <p class="blog-excerpt">${truncate(post.excerpt || '', 200)}</p>
        <div class="blog-meta" style="margin-bottom:1.5rem;">
          ${date ? `<span>${date}</span><span>·</span>` : ''}
          ${post.reading_time ? `<span>${post.reading_time} min read</span><span>·</span>` : ''}
          ${author ? `<span>By ${author}</span>` : ''}
        </div>
        <a href="blog-detail.html?slug=${post.slug}" class="btn btn-outline">
          Read Essay <span class="btn-icon">→</span>
        </a>
      </div>
    </div>`;
}

function renderServiceCard(service, index = 0) {
  const fallbackIcons = ['✦','◈','◎','⬡','◇','⟡'];
  const isSvg  = service.icon && service.icon.trim().startsWith('<');
  const icon   = isSvg ? service.icon : (service.icon || fallbackIcons[index % fallbackIcons.length]);
  const num    = String(index + 1).padStart(2, '0');
  return `
    <div class="service-card">
      <p class="service-number">${num}</p>
      ${isSvg
        ? `<div class="service-icon">${icon}</div>`
        : `<div class="service-icon" style="font-size:2rem;line-height:1">${icon}</div>`}
      <h3 class="service-title">${service.title}</h3>
      <p class="service-desc">${service.short_description || service.description || ''}</p>
    </div>`;
}

function renderServiceDetailCard(service, index = 0) {
  const fallbackIcons = ['✦','◈','◎','⬡','◇','⟡'];
  const isSvg    = service.icon && service.icon.trim().startsWith('<');
  const icon     = isSvg ? service.icon : (service.icon || fallbackIcons[index % fallbackIcons.length]);
  const imgSrc   = service.image_url ? API.imgUrl(service.image_url) : null;
  const features = parseFeatures(service.features_list || service.features);
  const num      = String(index + 1).padStart(2, '0');
  const isEven   = index % 2 === 0;
  return `
    <article class="svc-detail ${isEven ? '' : 'svc-detail--reverse'}" id="svc-${service.slug || index}">
      <div class="svc-detail-visual">
        ${imgSrc
          ? `<div class="svc-detail-image"><img src="${imgSrc}" alt="${service.title}" loading="lazy"></div>`
          : `<div class="svc-detail-icon-large">${isSvg ? icon : `<span style="font-size:4rem">${icon}</span>`}</div>`}
      </div>
      <div class="svc-detail-content">
        <div class="svc-detail-header">
          <div class="svc-number">${num}</div>
          <h2 class="svc-detail-title">${service.title}</h2>
        </div>
        <p class="svc-detail-short">${service.short_description || ''}</p>
        ${service.full_description ? `<div class="svc-detail-full prose-content">${service.full_description}</div>` : ''}
        ${features.length ? `
          <div class="svc-features-grid">
            ${features.map(f => `<div class="svc-feature"><div class="svc-feature-dot"></div><span>${f}</span></div>`).join('')}
          </div>` : ''}
        ${service.cta_text ? `
          <div style="margin-top:2rem">
            <a href="${service.cta_link || 'about.html#contact'}" class="btn btn-primary">${service.cta_text} →</a>
          </div>` : ''}
      </div>
    </article>`;
}

function parseFeatures(raw) {
  if (!raw) return [];
  if (Array.isArray(raw)) return raw.filter(Boolean);
  if (typeof raw === 'string') {
    try { const p = JSON.parse(raw); if (Array.isArray(p)) return p.filter(Boolean); } catch {}
    return raw.split('\n').map(s => s.trim()).filter(Boolean);
  }
  return [];
}

function renderTeamCard(author) {
  const imgSrc   = API.imgUrl(author.photo_url || author.photo);
  const name     = author.full_name || author.name || '';
  const initials = name.split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase();
  AuthorPanel.store(author);
  return `
    <div class="team-card" role="button" tabindex="0" style="cursor:pointer"
         onclick="AuthorPanel.open(${author.id})"
         onkeydown="if(event.key==='Enter')AuthorPanel.open(${author.id})">
      <div class="team-card-img">
        ${author.photo_url || author.photo
          ? `<img src="${imgSrc}" alt="${name}" loading="lazy">`
          : `<div style="width:100%;height:100%;display:flex;align-items:center;justify-content:center;
                         background:var(--blue-pale);font-family:var(--font-display);
                         font-size:2rem;color:var(--blue-mid)">${initials}</div>`}
      </div>
      <div class="team-card-info">
        <p class="member-name">${name}</p>
        ${author.role     ? `<p class="member-role">${author.role}</p>` : ''}
        ${author.short_bio ? `<p class="member-bio">${truncate(author.short_bio, 100)}</p>` : ''}
      </div>
    </div>`;
}

function renderSearchResult(item) {
  const imgSrc = API.imgUrl(item.image || item.cover);

  const type = item.type || 'result';

  const title =
    item.title ||
    item.name ||
    item.full_name ||
    'Untitled';

  const detail =
    type === 'book'
      ? `book-detail.html?slug=${item.slug || item.id}`
      : type === 'post'
      ? `blog-detail.html?slug=${item.slug || item.id}`
      : type === 'author'
      ? `team.html` // or custom author page
      : '#';

  return `
    <div class="search-result-item" onclick="window.location='${detail}'" style="cursor:pointer">
      <div class="search-result-thumb">
        <img src="${imgSrc}" alt="${title}" loading="lazy">
      </div>
      <div>
        <div class="search-result-type">${type}</div>
        <div class="search-result-title">${title}</div>
      </div>
    </div>`;
}

/* ─────────────────────────────────────────────────────────────
   6. AUTHOR PANEL (slide-in drawer with GSAP)
   ───────────────────────────────────────────────────────────── */
const AuthorPanel = {
  isOpen: false,
  currentAuthor: null,
  _registry: new Map(),

  store(author) { this._registry.set(author.id, author); },

  init() {
    if (document.getElementById('author-panel')) return;
    const panel = document.createElement('div');
    panel.id = 'author-panel';
    panel.className = 'author-panel';
    panel.setAttribute('role', 'dialog');
    panel.setAttribute('aria-modal', 'true');
    panel.innerHTML = `
      <div class="author-panel-backdrop" id="author-panel-backdrop"></div>
      <div class="author-panel-drawer" id="author-panel-drawer">
        <button class="author-panel-close" id="author-panel-close" aria-label="Close">
          <span></span><span></span>
        </button>
        <div class="author-panel-inner" id="author-panel-inner"></div>
      </div>`;
    document.body.appendChild(panel);
    document.getElementById('author-panel-backdrop').addEventListener('click', () => this.close());
    document.getElementById('author-panel-close').addEventListener('click', () => this.close());
    document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && this.isOpen) this.close(); });
  },

  open(authorId) {
    const author = this._registry.get(authorId);
    if (!author) return;
    this.currentAuthor = author;
    this.render(author);
    const panel  = document.getElementById('author-panel');
    const drawer = document.getElementById('author-panel-drawer');
    panel.classList.add('active');
    document.body.style.overflow = 'hidden';
    this.isOpen = true;
    gsap.killTweensOf(drawer);
    gsap.fromTo(drawer, { x: '100%' }, { x: '0%', duration: 0.65, ease: 'power4.out' });
    gsap.fromTo('#author-panel-backdrop', { opacity: 0 }, { opacity: 1, duration: 0.4 });
    gsap.fromTo('.apanel-stagger', { y: 28, opacity: 0 },
      { y: 0, opacity: 1, duration: 0.55, stagger: 0.07, ease: 'power3.out', delay: 0.2 });
    this.loadFullAuthor(author);
  },

  close() {
    const panel  = document.getElementById('author-panel');
    const drawer = document.getElementById('author-panel-drawer');
    if (!panel || !this.isOpen) return;
    gsap.killTweensOf(drawer);
    gsap.to(drawer, { x: '100%', duration: 0.45, ease: 'power3.in' });
    gsap.to('#author-panel-backdrop', {
      opacity: 0, duration: 0.3, ease: 'power2.in',
      onComplete: () => { panel.classList.remove('active'); document.body.style.overflow = ''; this.isOpen = false; },
    });
  },

  render(author) {
    const inner    = document.getElementById('author-panel-inner');
    const imgSrc   = API.imgUrl(author.photo_url || author.photo);
    const name     = author.full_name || author.name || '';
    const initials = name.split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase();
    const socials  = [
      author.twitter   && { url: author.twitter,   label: '𝕏',  title: 'Twitter'   },
      author.linkedin  && { url: author.linkedin,  label: 'in', title: 'LinkedIn'  },
      author.instagram && { url: author.instagram, label: '◎',  title: 'Instagram' },
      author.website   && { url: author.website,   label: '↗',  title: 'Website'   },
    ].filter(Boolean);

    inner.innerHTML = `
      <div class="apanel-hero apanel-stagger">
        <div class="apanel-photo">
          ${author.photo_url || author.photo
            ? `<img src="${imgSrc}" alt="${name}">`
            : `<div class="apanel-initials">${initials}</div>`}
        </div>
        <div class="apanel-hero-info">
          ${author.role ? `<div class="apanel-role eyebrow">${author.role}</div>` : ''}
          <h2 class="apanel-name">${name}</h2>
          ${author.book_count > 0 ? `
            <div class="apanel-stat">
              <span class="apanel-stat-num">${author.book_count}</span>
              <span class="apanel-stat-label">Published Work${author.book_count !== 1 ? 's' : ''}</span>
            </div>` : ''}
          ${socials.length ? `
            <div class="apanel-socials">
              ${socials.map(s => `<a href="${s.url}" target="_blank" rel="noopener" class="apanel-social-btn" title="${s.title}">${s.label}</a>`).join('')}
            </div>` : ''}
        </div>
      </div>
      <div class="apanel-rule apanel-stagger"><div class="apanel-rule-line"></div></div>
      ${(author.bio || author.short_bio) ? `
        <div class="apanel-section apanel-stagger">
          <div class="apanel-section-label">About</div>
          <div class="apanel-bio">${author.bio || author.short_bio}</div>
        </div>` : ''}
      <div class="apanel-section apanel-stagger">
        <div class="apanel-section-label">Books</div>
        <div class="apanel-books-grid" id="apanel-books-grid">
          ${[1,2,3].map(() => `<div class="apanel-book-skeleton"><div class="skeleton apanel-book-cover-skel"></div><div class="skeleton skeleton-line w-60" style="margin-top:10px"></div></div>`).join('')}
        </div>
      </div>`;
  },

  async loadAuthorBooks(author) {
    const grid = document.getElementById('apanel-books-grid');
    if (!grid) return;
    try {
      const data      = await API.getBooks();
      const all       = toArray(data);
      const firstName = (author.full_name || author.name || '').toLowerCase().split(' ')[0];
      const books     = all.filter(b => (b.author_names || b.author || '').toLowerCase().includes(firstName));
      if (!books.length) { grid.innerHTML = `<p class="apanel-empty">No books listed yet.</p>`; return; }
      grid.innerHTML = books.map(b => {
        const cover = API.imgUrl(b.cover_url || b.image || b.cover);
        const genre = b.genre?.name || b.genre || '';
        return `
          <div class="apanel-book-card" style="cursor:pointer"
               onclick="AuthorPanel.close(); setTimeout(()=>window.location='book-detail.html?slug=${b.slug}',380)">
            <div class="apanel-book-cover">
              <img src="${cover}" alt="${b.title}" loading="lazy">
              <div class="apanel-book-hover">View →</div>
            </div>
            <div class="apanel-book-title">${b.title}</div>
            ${genre ? `<div class="apanel-book-genre">${genre}</div>` : ''}
          </div>`;
      }).join('');
      gsap.fromTo('#apanel-books-grid .apanel-book-card', { y: 16, opacity: 0 },
        { y: 0, opacity: 1, duration: 0.45, stagger: 0.08, ease: 'power2.out' });
    } catch (err) {
      if (grid) grid.innerHTML = `<p class="apanel-empty">Could not load books.</p>`;
    }
  },

  async loadFullAuthor(author) {
    if (!author.slug) { this.loadAuthorBooks(author); return; }
    try {
      const data       = await API.getAuthor(author.slug);
      const fullAuthor = data.data || data;
      this._registry.set(author.id, fullAuthor);
      this.currentAuthor = fullAuthor;
      this.render(fullAuthor);
      gsap.fromTo('.apanel-stagger', { y: 20, opacity: 0 },
        { y: 0, opacity: 1, duration: 0.45, stagger: 0.06, ease: 'power2.out' });
      this.loadAuthorBooks(fullAuthor);
    } catch {
      this.loadAuthorBooks(author);
    }
  },
};

/* ─────────────────────────────────────────────────────────────
   7. PAGE MODULES
   ───────────────────────────────────────────────────────────── */

/* Home */
const HomePage = {
  async init() {
    await Promise.all([this.loadFeaturedBooks(), this.loadLatestPosts(), this.loadServices()]);
  },
  async loadFeaturedBooks() {
    const el = document.getElementById('home-books-grid');
    if (!el) return;
    el.innerHTML = Skeleton.books(4);
    try {
      const books = toArray(await API.getBooks()).slice(0, 4);
      if (!books.length) { el.innerHTML = emptyState('No books yet', 'Check back soon.'); return; }
      el.innerHTML = books.map(b => renderBookCard(b)).join('');
      initCardHovers(el);
      GSAP.animateCards(el);
    } catch (err) { el.innerHTML = emptyState('Could not load books', err.message); }
  },
  async loadLatestPosts() {
    const el = document.getElementById('home-posts-grid');
    if (!el) return;
    el.innerHTML = Skeleton.blog(3);
    try {
      const posts = toArray(await API.getPosts()).slice(0, 3);
      if (!posts.length) { el.innerHTML = emptyState('No posts yet'); return; }
      el.innerHTML = posts.map(p => renderBlogCard(p)).join('');
      GSAP.animateCards(el);
    } catch (err) { el.innerHTML = emptyState('Could not load posts', err.message); }
  },
  async loadServices() {
    const el = document.getElementById('home-services-grid');
    if (!el) return;
    el.innerHTML = Skeleton.services(3);
    try {
      const services = toArray(await API.getServices()).slice(0, 3);
      if (!services.length) { el.innerHTML = emptyState('No services listed'); return; }
      el.innerHTML = services.map((s, i) => renderServiceCard(s, i)).join('');
      GSAP.animateCards(el);
    } catch (err) { el.innerHTML = emptyState('Could not load services', err.message); }
  },
};

/* Books */
const BooksPage = {
  allBooks: [],
  activeFilter: 'all',
  async init() {
    const el = document.getElementById('books-grid');
    if (!el) return;
    el.innerHTML = Skeleton.books(8);
    try {
      this.allBooks = toArray(await API.getBooks());
      this.renderFilters();
      this.render();
    } catch (err) { el.innerHTML = emptyState('Could not load books', err.message); }
  },
  renderFilters() {
    const bar = document.getElementById('books-filter-bar');
    if (!bar || !this.allBooks.length) return;
    const genres = [...new Set(this.allBooks.map(b => b.genre?.name || b.genre).filter(Boolean))];
    bar.innerHTML = ['All', ...genres].map(g => `
      <button class="filter-btn${g === 'All' ? ' active' : ''}"
        onclick="BooksPage.filterBy('${g.toLowerCase()}')">${g}</button>`).join('');
  },
  filterBy(genre) {
    this.activeFilter = genre;
    document.querySelectorAll('#books-filter-bar .filter-btn').forEach(b => {
      b.classList.toggle('active', b.textContent.toLowerCase() === genre);
    });
    this.render();
  },
  render() {
    const el = document.getElementById('books-grid');
    if (!el) return;
    const books = this.activeFilter === 'all'
      ? this.allBooks
      : this.allBooks.filter(b => (b.genre?.name || b.genre || '').toLowerCase() === this.activeFilter);
    if (!books.length) { el.innerHTML = emptyState('No books found', `No books in "${this.activeFilter}" genre.`); return; }
    el.innerHTML = books.map(b => renderBookCard(b)).join('');
    initCardHovers(el);
    GSAP.animateCards(el);
  },
};

/* Book Detail */
const BookDetailPage = {
  books: [],
  current: null,
  async init() {
    const slug = getParam('slug') || getParam('id');
    if (!slug) { this.showError('No book specified.'); return; }
    this.setLoading();
    try {
      const [bookData, allData] = await Promise.all([API.getBook(slug), API.getBooks()]);
      this.books   = toArray(allData);
      const book   = bookData.data || bookData;
      this.current = book;
      this.render(book);
    } catch (err) { this.showError(err.message); }
  },
  setLoading() {
    const main = document.getElementById('book-detail-main');
    if (!main) return;
    main.innerHTML = `
      <div class="bd-loading container" style="padding-top:9rem">
        <div class="bd-loading-cover skeleton"></div>
        <div class="bd-loading-info">
          <div class="skeleton skeleton-line w-40" style="height:12px;margin-bottom:2rem"></div>
          <div class="skeleton skeleton-line" style="height:56px;margin-bottom:1rem"></div>
          <div class="skeleton skeleton-line w-60" style="height:20px;margin-bottom:2.5rem"></div>
          <div class="skeleton skeleton-line" style="margin-bottom:0.75rem"></div>
          <div class="skeleton skeleton-line w-60"></div>
        </div>
      </div>`;
  },
  getRating(slug) { try { return parseInt(localStorage.getItem(`rating_${slug}`) || '0', 10); } catch { return 0; } },
  setRating(slug, val) { try { localStorage.setItem(`rating_${slug}`, val); } catch {} },
  renderStars(slug, current = 0) {
    return Array.from({ length: 5 }, (_, i) => `
      <button class="bd-star ${i < current ? 'active' : ''}"
        onclick="BookDetailPage.rate('${slug}', ${i + 1})"
        onmouseenter="BookDetailPage.hoverStars(${i + 1})"
        onmouseleave="BookDetailPage.resetStars('${slug}')"
        aria-label="Rate ${i + 1} star">★</button>`).join('');
  },
  rate(slug, val) {
    this.setRating(slug, val);
    document.querySelectorAll('.bd-star').forEach((s, i) => s.classList.toggle('active', i < val));
    const label = document.getElementById('bd-rating-label');
    const labels = ['','Poor','Fair','Good','Great','Excellent'];
    if (label) { label.textContent = labels[val]; label.classList.add('rated'); }
  },
  hoverStars(val) { document.querySelectorAll('.bd-star').forEach((s, i) => s.classList.toggle('hover', i < val)); },
  resetStars(slug) {
    const cur = this.getRating(slug);
    document.querySelectorAll('.bd-star').forEach((s, i) => { s.classList.remove('hover'); s.classList.toggle('active', i < cur); });
  },
  getRelated(book) {
    const genreName   = book.genre?.name || book.genre || '';
    const authorNames = book.author_names || book.author || '';
    return this.books.filter(b => {
      if (b.slug === book.slug) return false;
      const bGenre  = b.genre?.name || b.genre || '';
      const bAuthor = b.author_names || b.author || '';
      return bAuthor === authorNames || bGenre === genreName;
    }).slice(0, 4);
  },
  render(book) {
    const main = document.getElementById('book-detail-main');
    if (!main) return;
    const coverSrc = API.imgUrl(book.cover_url || book.image || book.cover);
    const idx      = this.books.findIndex(b => b.slug === book.slug);
    const prev     = this.books[idx - 1];
    const next     = this.books[idx + 1];
    const author   = book.author_names || book.author || 'Unknown';
    const genre    = book.genre?.name  || book.genre  || '';
    const rating   = this.getRating(book.slug);
    const related  = this.getRelated(book);
    const metaItems = [
      { label: 'Publisher', val: book.publisher },
      { label: 'Published', val: book.published_date ? formatDate(book.published_date) : null },
      { label: 'ISBN',      val: book.isbn },
      { label: 'Pages',     val: book.pages },
      { label: 'Language',  val: book.language },
      { label: 'Edition',   val: book.edition },
      { label: 'Genre',     val: genre },
    ].filter(m => m.val);

    main.innerHTML = `
      <div class="bd-hero">
        <div class="bd-hero-bg" style="background-image:url('${coverSrc}')"></div>
        <div class="bd-hero-overlay"></div>
        <div class="container bd-hero-inner">
          <div class="bd-cover-wrap" id="bd-cover">
            <img src="${coverSrc}" alt="${book.title}" class="bd-cover-img">
          </div>
          <div class="bd-hero-text" id="bd-hero-text">
            <a href="books.html" class="bd-breadcrumb">← Books${genre ? ` / ${genre}` : ''}</a>
            <h1 class="bd-title">${book.title}</h1>
            ${book.subtitle ? `<p class="bd-subtitle">${book.subtitle}</p>` : ''}
            <p class="bd-author">by <em>${author}</em></p>
            <div class="bd-rating-wrap">
              <div class="bd-stars" id="bd-stars">${this.renderStars(book.slug, rating)}</div>
              <span class="bd-rating-label ${rating ? 'rated' : ''}" id="bd-rating-label">
                ${rating ? ['','Poor','Fair','Good','Great','Excellent'][rating] : 'Rate this book'}
              </span>
            </div>
            <div class="bd-commerce">
              ${book.price ? `<span class="bd-price">$${parseFloat(book.price).toFixed(2)}</span>` : ''}
              ${book.buy_link ? `<a href="${book.buy_link}" target="_blank" rel="noopener" class="btn btn-primary">Get This Book ↗</a>` : ''}
            </div>
          </div>
        </div>
      </div>
      <div class="bd-body container">
        <div class="bd-main-col">
          ${book.excerpt ? `<div class="bd-excerpt-block" id="bd-excerpt"><span class="bd-excerpt-mark">"</span><p>${book.excerpt}</p></div>` : ''}
          <div class="bd-description prose-content" id="bd-desc">${book.description || ''}</div>
          ${metaItems.length ? `
            <div class="bd-meta-grid" id="bd-meta">
              ${metaItems.map(m => `<div class="bd-meta-item"><span class="bd-meta-label">${m.label}</span><span class="bd-meta-val">${m.val}</span></div>`).join('')}
            </div>` : ''}
          <div class="bd-nav" id="bd-nav">
            ${prev ? `<a href="book-detail.html?slug=${prev.slug}" class="bd-nav-btn"><span class="bd-nav-dir">← Previous</span><span class="bd-nav-title">${prev.title}</span></a>` : '<div></div>'}
            ${next ? `<a href="book-detail.html?slug=${next.slug}" class="bd-nav-btn bd-nav-btn--next"><span class="bd-nav-dir">Next →</span><span class="bd-nav-title">${next.title}</span></a>` : '<div></div>'}
          </div>
        </div>
        <div class="bd-sidebar">
          ${metaItems.length ? `
            <div class="bd-sidebar-card">
              <div class="bd-sidebar-label">Book Details</div>
              ${metaItems.map(m => `<div class="bd-sidebar-row"><span>${m.label}</span><span>${m.val}</span></div>`).join('')}
            </div>` : ''}
        </div>
      </div>
      ${related.length ? `
        <div class="bd-related">
          <div class="container">
            <div class="bd-related-header">
              <span class="eyebrow">You May Also Like</span>
              <h3 class="bd-related-title">Related <em>Titles</em></h3>
            </div>
            <div class="books-grid" id="bd-related-grid">${related.map(b => renderBookCard(b)).join('')}</div>
          </div>
        </div>` : ''}`;

    document.title = `${book.title} — A-D Kay Publications`;
    this.animateIn();
    if (related.length) {
      setTimeout(() => {
        const rg = document.getElementById('bd-related-grid');
        if (rg) { initCardHovers(rg); GSAP.animateCards(rg); }
      }, 400);
    }
  },
  animateIn() {
    const tl = gsap.timeline({ defaults: { ease: 'power3.out' } });
    tl.from('#bd-cover',      { x: -50, opacity: 0, duration: 0.9 }, 0.1)
      .from('.bd-breadcrumb', { y: 15,  opacity: 0, duration: 0.5 }, 0.2)
      .from('.bd-title',      { y: 40,  opacity: 0, duration: 0.8 }, 0.3)
      .from('.bd-author',     { y: 20,  opacity: 0, duration: 0.6 }, 0.5)
      .from('.bd-commerce',   { y: 15,  opacity: 0, duration: 0.5 }, 0.7);
    gsap.from('#bd-desc', { scrollTrigger: { trigger: '#bd-desc', start: 'top 85%', once: true }, y: 25, opacity: 0, duration: 0.7 });
    gsap.from('#bd-meta', { scrollTrigger: { trigger: '#bd-meta', start: 'top 88%', once: true }, y: 20, opacity: 0, duration: 0.6 });
  },
  showError(msg) {
    const main = document.getElementById('book-detail-main');
    if (main) main.innerHTML = `<div class="container" style="padding-top:9rem">${emptyState('Book not found', msg)}</div>`;
  },
};

/* Blog */
const BlogPage = {
  allPosts: [],
  activeCategory: 'all',
  async init() {
    const featuredEl = document.getElementById('blog-featured-container');
    const gridEl     = document.getElementById('blog-grid');
    if (!gridEl) return;
    gridEl.innerHTML = Skeleton.blog(6);
    try {
      this.allPosts = toArray(await API.getPosts());
      if (!this.allPosts.length) {
        if (featuredEl) featuredEl.innerHTML = '';
        gridEl.innerHTML = emptyState('No posts available');
        return;
      }
      const featured = this.allPosts.find(p => p.is_featured) || this.allPosts[0];
      if (featuredEl && featured) {
        featuredEl.innerHTML = renderFeaturedPost(featured);

        // ── FIX: animate the featured post directly since ScrollTrigger
        //         already ran before this element existed in the DOM ──
        const featuredEl2 = featuredEl.querySelector('.blog-featured');
        if (featuredEl2) {
          featuredEl2.style.opacity = '1';
          featuredEl2.style.transform = 'none';
          gsap.from(featuredEl2, { opacity: 0, y: 30, duration: 0.85, ease: 'power3.out' });
        }
      }

      const filterEl = document.getElementById('blog-filter-bar');
      if (filterEl) this.renderFilters(filterEl);
      this.render(featured?.slug);
    } catch (err) {
      if (featuredEl) featuredEl.innerHTML = '';
      gridEl.innerHTML = emptyState('Could not load posts', err.message);
    }
  },
  renderFilters(bar) {
    const cats = [...new Map(
      this.allPosts.filter(p => p.category?.name).map(p => [p.category.name, p.category])
    ).values()];
    if (!cats.length) return;
    bar.innerHTML = `<button class="filter-btn active" onclick="BlogPage.filterBy('all')">All</button>` +
      cats.map(c => `<button class="filter-btn" onclick="BlogPage.filterBy('${c.slug || c.name.toLowerCase()}')">${c.name}</button>`).join('');
  },
  filterBy(cat) {
    this.activeCategory = cat;
    document.querySelectorAll('#blog-filter-bar .filter-btn').forEach(b => {
      b.classList.toggle('active', b.textContent.trim().toLowerCase() === cat || (cat === 'all' && b.textContent.trim() === 'All'));
    });
    const featured = this.allPosts.find(p => p.is_featured) || this.allPosts[0];
    this.render(featured?.slug);
  },
  render(featuredSlug) {
    const gridEl = document.getElementById('blog-grid');
    if (!gridEl) return;
    let posts = this.allPosts.filter(p => p.slug !== featuredSlug);
    if (this.activeCategory !== 'all') {
      posts = posts.filter(p => (p.category?.slug || p.category?.name?.toLowerCase()) === this.activeCategory);
    }
    if (!posts.length) { gridEl.innerHTML = emptyState('No posts in this category'); return; }
    gridEl.innerHTML = posts.map(p => renderBlogCard(p)).join('');
    GSAP.animateCards(gridEl);
  },
};

/* Blog Detail */
const BlogDetailPage = {
  async init() {
    const slug = getParam('slug') || getParam('id');
    if (!slug) { this.showError('No post specified.'); return; }
    const main = document.getElementById('blog-detail-main');
    if (main) main.innerHTML = `
      <div class="container" style="padding-top:8rem">
        <div class="skeleton" style="aspect-ratio:21/9;margin-bottom:3rem;border-radius:4px"></div>
        <div class="skeleton skeleton-line" style="height:50px;margin-bottom:1rem;max-width:800px;margin-left:auto;margin-right:auto"></div>
        <div class="skeleton skeleton-line w-40" style="max-width:800px;margin:0 auto 2rem"></div>
      </div>`;
    try {
      const data = await API.getPost(slug);
      const post = data.data || data;
      this.render(post);
      API.fetch(`/api/blog/posts/${slug}/view/`, { method: 'POST' }).catch(() => {});
      this.loadRelated(post);
    } catch (err) { this.showError(err.message); }
  },
  render(post) {
    const main     = document.getElementById('blog-detail-main');
    if (!main) return;
    const imgSrc   = API.imgUrl(post.cover_url || post.image || post.cover);
    const author   = resolveAuthor(post);
    const initial  = author.charAt(0).toUpperCase();
    const catName  = post.category?.name || (typeof post.category === 'string' ? post.category : '') || '';
    const date     = formatDate(post.published_at || post.date || post.created_at);
    const tags     = Array.isArray(post.tags) ? post.tags : [];
    const hasImage = !!(post.cover_url || post.image || post.cover);
    const body     = post.body || post.content || post.description || '';

    main.innerHTML = `
      <div class="bdd-hero">
        ${hasImage
          ? `<div class="bdd-hero-image"><img src="${imgSrc}" alt="${post.title}"><div class="bdd-hero-image-overlay"></div></div>`
          : `<div class="bdd-hero-image bdd-hero-image--empty"></div>`}
        <div class="container bdd-hero-content">
          ${catName ? `<p class="blog-tag" style="margin-bottom:1.25rem">${catName}</p>` : ''}
          <h1 class="bdd-title">${post.title}</h1>
          ${post.subtitle ? `<p class="bdd-subtitle">${post.subtitle}</p>` : ''}
          <div class="bdd-meta">
            <span class="bdd-author"><span class="bdd-author-avatar">${initial}</span>${author}</span>
            ${date ? `<span>${date}</span>` : ''}
            ${post.reading_time ? `<span>${post.reading_time} min read</span>` : ''}
            ${post.views ? `<span>${Number(post.views).toLocaleString()} views</span>` : ''}
          </div>
        </div>
      </div>
      <div class="container bdd-layout">
        <article class="bdd-article">
          ${post.excerpt ? `<div class="bdd-excerpt"><p>${post.excerpt}</p></div>` : ''}
          <div class="bdd-body prose-content" id="bdd-body">${body}</div>
          ${tags.length ? `
            <div class="bdd-tags">
              <span class="bdd-tags-label">Tagged:</span>
              ${tags.map(t => `<span class="bdd-tag">${t.name || t}</span>`).join('')}
            </div>` : ''}
          <div class="bdd-back"><a href="blog.html" class="btn btn-outline">← Back to Journal</a></div>
        </article>
        <aside class="bdd-sidebar">
          <div class="bdd-sidebar-card">
            <div class="bdd-sidebar-label">About this article</div>
            <div class="bdd-sidebar-row"><span>Author</span><span>${author}</span></div>
            ${date ? `<div class="bdd-sidebar-row"><span>Published</span><span>${date}</span></div>` : ''}
            ${post.reading_time ? `<div class="bdd-sidebar-row"><span>Read time</span><span>${post.reading_time} min</span></div>` : ''}
            ${catName ? `<div class="bdd-sidebar-row"><span>Category</span><span>${catName}</span></div>` : ''}
          </div>
          <div class="bdd-related-posts" id="bdd-related">
            <div class="bdd-sidebar-label" style="margin-bottom:1rem">Related Posts</div>
            <div id="bdd-related-list">
              ${[1,2].map(() => `<div style="display:flex;gap:0.75rem;margin-bottom:1rem"><div class="skeleton" style="width:60px;height:60px;border-radius:4px;flex-shrink:0"></div><div style="flex:1"><div class="skeleton skeleton-line" style="margin:0 0 6px"></div><div class="skeleton skeleton-line w-60" style="margin:0"></div></div></div>`).join('')}
            </div>
          </div>
        </aside>
      </div>`;

    document.title = `${post.title} — A-D Kay Publications`;
    this.animateIn();
  },
  async loadRelated(post) {
    const listEl = document.getElementById('bdd-related-list');
    if (!listEl) return;
    try {
      const all        = toArray(await API.getPosts());
      const catName    = post.category?.name || '';
      const postAuthor = resolveAuthor(post);
      const related    = all.filter(p =>
        p.slug !== post.slug &&
        ((p.category?.name && p.category.name === catName) || resolveAuthor(p) === postAuthor)
      ).slice(0, 4);
      if (!related.length) { document.getElementById('bdd-related')?.remove(); return; }
      listEl.innerHTML = related.map(p => {
        const img = API.imgUrl(p.cover_url || p.image || p.cover);
        return `
          <div class="bdd-related-item" style="cursor:pointer"
               onclick="window.location='blog-detail.html?slug=${p.slug}'">
            <div class="bdd-related-thumb"><img src="${img}" alt="${p.title}" loading="lazy"></div>
            <div class="bdd-related-info">
              <div class="bdd-related-title">${p.title}</div>
              <div class="bdd-related-date">${formatDate(p.published_at || p.date || p.created_at)}</div>
            </div>
          </div>`;
      }).join('');
      gsap.fromTo('.bdd-related-item', { x: 20, opacity: 0 },
        { x: 0, opacity: 1, duration: 0.4, stagger: 0.08, ease: 'power2.out' });
    } catch { /* sidebar stays */ }
  },
  animateIn() {
    const tl = gsap.timeline({ defaults: { ease: 'power3.out' } });
    tl.from('.bdd-title',    { y: 40, opacity: 0, duration: 0.9 }, 0.1)
      .from('.bdd-subtitle', { y: 20, opacity: 0, duration: 0.7 }, 0.3)
      .from('.bdd-meta',     { y: 15, opacity: 0, duration: 0.6 }, 0.45);
    gsap.from('#bdd-body', { scrollTrigger: { trigger: '#bdd-body', start: 'top 85%', once: true }, y: 25, opacity: 0, duration: 0.7 });
  },
  showError(msg) {
    const main = document.getElementById('blog-detail-main');
    if (main) main.innerHTML = `<div class="container" style="padding-top:9rem">${emptyState('Post not found', msg)}</div>`;
  },
};

/* Team */
const TeamPage = {
  GROUPS: [
    { key: 'executive',  label: 'Leadership', keywords: ['ceo','founder','director','chief','president','executive','managing'] },
    { key: 'management', label: 'Management', keywords: ['manager','head','coordinator','supervisor','publisher'] },
    { key: 'author',     label: 'Authors',    keywords: ['author','writer','novelist','poet','journalist'] },
    { key: 'advisory',   label: 'Advisory',   keywords: ['advisor','advisory','board'] },
    { key: 'editorial',  label: 'Editorial',  keywords: ['editor','editorial','proofreader','copy','reviewer'] },
    { key: 'other',      label: 'Team',       keywords: [] },
  ],
  categorize(authors) {
    const groups = {};
    this.GROUPS.forEach(g => groups[g.key] = []);
    authors.forEach(a => {
      const roleStr = (a.role || '').toLowerCase();
      const matched = this.GROUPS.find(g => g.keywords.length && g.keywords.some(kw => roleStr.includes(kw)));
      groups[matched ? matched.key : 'other'].push(a);
    });
    return groups;
  },
  async init() {
    const el = document.getElementById('team-grid');
    if (!el) return;
    el.innerHTML = Skeleton.team(6);
    try {
      const authors = toArray(await API.getAuthors()).filter(a => a.is_active !== false);
      if (!authors.length) { el.innerHTML = emptyState('No team members found'); return; }
      const groups = this.categorize(authors);
      let html = '';
      this.GROUPS.forEach(({ key, label }) => {
        const members = groups[key];
        if (!members.length) return;
        html += `
          <section class="section ${key !== 'executive' ? 'section--alt' : ''}" style="${key !== 'executive' ? 'background:var(--off-white)' : ''}">
            <div class="section-inner">
              <div class="section-header">
                <div>
                  <p class="section-label">${label}</p>
                  <h2 class="section-title">${label} <em>Team</em></h2>
                </div>
              </div>
              <div class="team-grid" data-stagger>${members.map(a => renderTeamCard(a)).join('')}</div>
            </div>
          </section>`;
      });
      el.innerHTML = html;
      document.querySelectorAll('[data-stagger]').forEach(grid => GSAP.animateCards(grid));
    } catch (err) { el.innerHTML = emptyState('Could not load team', err.message); }
  },
};

/* Services */
const ServicesPage = {
  async init() {
    const el = document.getElementById('services-dynamic-grid');
    if (!el) return;
    el.innerHTML = Skeleton.services(4);
    try {
      const services = toArray(await API.getServices()).filter(s => s.is_active !== false);
      if (!services.length) { el.innerHTML = emptyState('No services listed'); return; }
      el.innerHTML = services.map((s, i) => renderServiceDetailCard(s, i)).join('');
      document.querySelectorAll('.svc-detail').forEach((card, i) => {
        gsap.from(card, {
          scrollTrigger: { trigger: card, start: 'top 82%', once: true },
          x: i % 2 === 0 ? -40 : 40, opacity: 0, duration: 0.8, ease: 'power3.out',
        });
      });
    } catch (err) { el.innerHTML = emptyState('Could not load services', err.message); }
  },
};

/* Contact */
const ContactPage = {
  init() {
    const form = document.getElementById('contact-form');
    if (!form) return;
    form.addEventListener('submit', (e) => { e.preventDefault(); this.submit(form); });
  },
  async submit(form) {
    const btn     = form.querySelector('[type="submit"]');
    const success = document.getElementById('contact-success');
    const error   = document.getElementById('contact-error');
    const data    = {
      name:    form.querySelector('#contact-name')?.value,
      email:   form.querySelector('#contact-email')?.value,
      subject: form.querySelector('#contact-subject')?.value,
      message: form.querySelector('#contact-message')?.value,
    };
    btn.textContent = 'Sending…'; btn.disabled = true;
    if (success) success.style.display = 'none';
    if (error)   error.style.display   = 'none';
    try {
      await API.postContact(data);
      form.reset();
      if (success) {
        success.textContent = "Your message has been sent. We'll be in touch shortly.";
        success.style.display = 'block';
      }
    } catch (err) {
      // Show the actual API error message if available
      const msg = err.message || 'Failed to send. Please try again.';
      if (error) { error.textContent = msg; error.style.display = 'block'; }
    } finally {
      btn.textContent = 'Send Message'; btn.disabled = false;
    }
  },
};

/* Newsletter */
const Newsletter = {
  init() {
    document.querySelectorAll('.newsletter-form').forEach(form => {
      form.addEventListener('submit', (e) => { e.preventDefault(); this.submit(form); });
    });
  },
  async submit(form) {
    const input = form.querySelector('.newsletter-input, input[type="email"]');
    const btn   = form.querySelector('.newsletter-btn, button[type="submit"]');
    if (!input || !input.value) return;
    const original = btn.textContent;
    btn.textContent = '…'; btn.disabled = true;
    try {
      await API.postNewsletter({ email: input.value });
      input.value = ''; btn.textContent = '✓ Subscribed';
      setTimeout(() => { btn.textContent = original; btn.disabled = false; }, 3000);
    } catch {
      btn.textContent = 'Try again';
      setTimeout(() => { btn.textContent = original; btn.disabled = false; }, 2500);
    }
  },
};

/* Search */
const Search = {
  debounceTimer: null,
  init() {
    const overlay  = document.getElementById('search-overlay');
    const input    = document.getElementById('search-input');
    const results  = document.getElementById('search-results');
    const triggers = document.querySelectorAll('[data-search-trigger]');
    const close    = document.getElementById('search-close');
    if (!overlay) return;
    triggers.forEach(t => t.addEventListener('click', () => { overlay.classList.add('active'); setTimeout(() => input?.focus(), 50); }));
    close?.addEventListener('click', () => overlay.classList.remove('active'));
    overlay.addEventListener('click', (e) => { if (e.target === overlay) overlay.classList.remove('active'); });
    document.addEventListener('keydown', (e) => { if (e.key === 'Escape') overlay.classList.remove('active'); });
    input?.addEventListener('input', () => {
      clearTimeout(this.debounceTimer);
      this.debounceTimer = setTimeout(() => this.query(input.value, results), 350);
    });
  },
  async query(q, resultsEl) {
    if (!resultsEl) return;

    if (!q || q.trim().length < 2) {
      resultsEl.innerHTML = '';
      return;
    }

    resultsEl.innerHTML = `<p style="font-size:0.8rem;color:var(--mid-grey)">Searching…</p>`;

    try {
      const raw = await API.search(q.trim());
      console.log("SEARCH RESPONSE:", raw);

      let results = [];

      if (raw?.data) {
        results = [
          ...(raw.data.books || []).map(b => ({ ...b, type: 'book' })),
          ...(raw.data.posts || []).map(p => ({ ...p, type: 'post' })),
          ...(raw.data.authors || []).map(a => ({ ...a, type: 'author' })),
        ];
      }

      if (!results.length) {
        resultsEl.innerHTML = `<p style="font-size:0.8rem;color:var(--mid-grey)">No results for "${q}"</p>`;
        return;
      }

      resultsEl.innerHTML = results
        .slice(0, 8)
        .map(r => renderSearchResult(r))
        .join('');

    } catch (err) {
      console.error("SEARCH ERROR:", err);
      resultsEl.innerHTML = `<p style="font-size:0.8rem;color:var(--mid-grey)">Search unavailable</p>`;
    }
  },
};

/* ─────────────────────────────────────────────────────────────
   8. GSAP MODULE — P1 animations preserved + P2 helpers added
   ───────────────────────────────────────────────────────────── */
const GSAP = {
  animateCards(container) {
    if (!container) return;
    const children = [...container.children].filter(c =>
      !c.classList.contains('skeleton-card') && !c.classList.contains('skeleton')
    );
    if (!children.length) return;
    gsap.from(children, { y: 30, opacity: 0, duration: 0.55, stagger: 0.08, ease: 'power2.out', clearProps: 'all' });
  },
  animateIn(el, opts = {}) {
    if (!el) return;
    gsap.from(el, { y: 20, opacity: 0, duration: 0.6, ease: 'power2.out', ...opts });
  },
  initScrollAnimations() {
    gsap.registerPlugin(ScrollTrigger);
    gsap.utils.toArray('.fade-up').forEach(el => {
      gsap.to(el, { opacity: 1, y: 0, duration: 0.85, ease: 'power3.out',
        scrollTrigger: { trigger: el, start: 'top 88%', once: true } });
    });
    gsap.utils.toArray('.fade-in').forEach(el => {
      gsap.to(el, { opacity: 1, duration: 1, ease: 'power2.out',
        scrollTrigger: { trigger: el, start: 'top 90%', once: true } });
    });
    gsap.utils.toArray('.slide-left').forEach(el => {
      gsap.to(el, { opacity: 1, x: 0, duration: 0.85, ease: 'power3.out',
        scrollTrigger: { trigger: el, start: 'top 88%', once: true } });
    });
    gsap.utils.toArray('.slide-right').forEach(el => {
      gsap.to(el, { opacity: 1, x: 0, duration: 0.85, ease: 'power3.out',
        scrollTrigger: { trigger: el, start: 'top 88%', once: true } });
    });
    gsap.utils.toArray('[data-stagger]').forEach(container => {
      const children = container.querySelectorAll('[data-stagger-item]');
      if (!children.length) return;
      gsap.fromTo(children, { opacity: 0, y: 30 }, {
        opacity: 1, y: 0, duration: 0.7, stagger: 0.12, ease: 'power3.out',
        scrollTrigger: { trigger: container, start: 'top 85%', once: true },
      });
    });
    gsap.utils.toArray('.section-title').forEach(el => {
      gsap.fromTo(el, { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.8, ease: 'power3.out',
        scrollTrigger: { trigger: el, start: 'top 88%', once: true } });
    });
    gsap.utils.toArray('.section-label').forEach(el => {
      gsap.fromTo(el, { opacity: 0, x: -15 }, { opacity: 1, x: 0, duration: 0.6, ease: 'power2.out',
        scrollTrigger: { trigger: el, start: 'top 92%', once: true } });
    });
    gsap.utils.toArray('[data-parallax]').forEach(img => {
      gsap.to(img, { yPercent: -12, ease: 'none',
        scrollTrigger: { trigger: img.parentElement, start: 'top bottom', end: 'bottom top', scrub: 1.5 } });
    });
    gsap.utils.toArray('.stat-number[data-count]').forEach(el => {
      const target = parseInt(el.getAttribute('data-count'));
      ScrollTrigger.create({
        trigger: el, start: 'top 85%', once: true,
        onEnter: () => gsap.fromTo({ val: 0 }, { val: target }, {
          duration: 1.8, ease: 'power2.out',
          onUpdate: function () {
            el.textContent = Math.round(this.targets()[0].val).toLocaleString() + (el.dataset.suffix || '');
          },
        }),
      });
    });
  },
  heroEntrance() {
    const hero = document.querySelector('.hero');
    if (!hero) return;
    const tl = gsap.timeline({ delay: 0.7 });
    tl.fromTo('.hero-eyebrow', { opacity: 0, x: -20 }, { opacity: 1, x: 0, duration: 0.6, ease: 'power2.out' })
      .fromTo('.hero-title',   { opacity: 0, y: 30  }, { opacity: 1, y: 0, duration: 0.9, ease: 'power3.out' }, '-=0.2')
      .fromTo('.hero-body',    { opacity: 0, y: 20  }, { opacity: 1, y: 0, duration: 0.7, ease: 'power2.out' }, '-=0.4')
      .fromTo('.hero-actions', { opacity: 0, y: 15  }, { opacity: 1, y: 0, duration: 0.6, ease: 'power2.out' }, '-=0.4')
      .fromTo('.hero-visual',  { opacity: 0, scale: 1.05 }, { opacity: 1, scale: 1, duration: 1.2, ease: 'power3.out' }, 0.3)
      .fromTo('.hero-scroll-hint', { opacity: 0 }, { opacity: 1, duration: 0.6 }, '-=0.3');
  },
};

/* ─────────────────────────────────────────────────────────────
   9. ORIGINAL P1 FUNCTIONS
   ───────────────────────────────────────────────────────────── */
function initHeader() {
  const header = document.querySelector('header');
  if (!header) return;
  ScrollTrigger.create({ start: 'top -80', end: 99999, toggleClass: { className: 'scrolled', targets: header } });
  const currentPage = window.location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('.nav-links a, .mobile-nav a').forEach(link => {
    const href = link.getAttribute('href');
    if (href === currentPage || (href === 'index.html' && currentPage === '')) link.classList.add('active');
  });
}

function initMobileNav() {
  const hamburger = document.querySelector('.hamburger');
  const mobileNav = document.querySelector('.mobile-nav');
  if (!hamburger || !mobileNav) return;
  let isOpen = false;
  hamburger.addEventListener('click', () => {
    isOpen = !isOpen;
    hamburger.classList.toggle('open', isOpen);
    if (isOpen) {
      mobileNav.classList.add('open');
      gsap.to(mobileNav, { opacity: 1, duration: 0.3, ease: 'power2.out' });
      gsap.fromTo(mobileNav.querySelectorAll('a'), { opacity: 0, y: 20 },
        { opacity: 1, y: 0, duration: 0.4, stagger: 0.06, ease: 'power2.out', delay: 0.15 });
      document.body.style.overflow = 'hidden';
    } else {
      gsap.to(mobileNav, { opacity: 0, duration: 0.25, ease: 'power2.in',
        onComplete: () => mobileNav.classList.remove('open') });
      document.body.style.overflow = '';
    }
  });
  mobileNav.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', () => {
      isOpen = false; hamburger.classList.remove('open');
      gsap.to(mobileNav, { opacity: 0, duration: 0.2, onComplete: () => mobileNav.classList.remove('open') });
      document.body.style.overflow = '';
    });
  });
}

function initLinkTransitions() {
  const overlay = document.getElementById('page-overlay');
  if (!overlay) return;
  document.querySelectorAll('a[href]').forEach(link => {
    const href = link.getAttribute('href');
    if (!href || href.startsWith('#') || href.startsWith('http') || href.startsWith('mailto')) return;
    link.addEventListener('click', (e) => {
      e.preventDefault();
      gsap.set(overlay, { scaleY: 0, transformOrigin: 'bottom' });
      gsap.to(overlay, { scaleY: 1, duration: 0.5, ease: 'power3.inOut',
        onComplete: () => { window.location.href = href; } });
    });
  });
}

function initCardHovers(container = document) {
  container.querySelectorAll('.book-card').forEach(card => {
    card.addEventListener('mouseenter', () => gsap.to(card, { y: -4, duration: 0.3, ease: 'power2.out' }));
    card.addEventListener('mouseleave', () => gsap.to(card, { y: 0,  duration: 0.3, ease: 'power2.out' }));
  });
  container.querySelectorAll('.service-card').forEach(card => {
    card.addEventListener('mouseenter', () => gsap.to(card, { y: -3, duration: 0.25, ease: 'power2.out' }));
    card.addEventListener('mouseleave', () => gsap.to(card, { y: 0,  duration: 0.25, ease: 'power2.out' }));
  });
  container.querySelectorAll('.blog-card, .blog-featured').forEach(card => {
    card.addEventListener('mouseenter', () => gsap.to(card, { y: -3, duration: 0.25, ease: 'power2.out' }));
    card.addEventListener('mouseleave', () => gsap.to(card, { y: 0,  duration: 0.25, ease: 'power2.out' }));
  });
}

function initMarquee() {
  const track = document.querySelector('.marquee-track');
  if (!track) return;
  track.addEventListener('mouseenter', () => track.style.animationPlayState = 'paused');
  track.addEventListener('mouseleave', () => track.style.animationPlayState = 'running');
}

function initTimeline() {
  document.querySelectorAll('.timeline-item').forEach((item, i) => {
    gsap.fromTo(item, { opacity: 0, x: -20 }, {
      opacity: 1, x: 0, duration: 0.65, ease: 'power2.out',
      scrollTrigger: { trigger: item, start: 'top 88%', once: true }, delay: i * 0.08,
    });
  });
}

/* ─────────────────────────────────────────────────────────────
   10. BOOTSTRAP
   ───────────────────────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  const overlay = document.getElementById('page-overlay');
  if (overlay) {
    gsap.set(overlay, { scaleY: 1, transformOrigin: 'top' });
    gsap.to(overlay, { scaleY: 0, duration: 0.85, ease: 'power3.inOut', delay: 0.1 });
  }

  gsap.registerPlugin(ScrollTrigger);
  initHeader();
  initMobileNav();
  GSAP.initScrollAnimations();
  initMarquee();
  initLinkTransitions();
  initCardHovers();
  AuthorPanel.init();
  Newsletter.init();
  Search.init();

  if (onPage('index'))           { GSAP.heroEntrance(); HomePage.init(); }
  if (onPage('books.html'))        BooksPage.init();
  if (onPage('book-detail.html'))  BookDetailPage.init();
  if (onPage('blog.html'))         BlogPage.init();
  if (onPage('blog-detail.html'))  BlogDetailPage.init();
  if (onPage('team.html'))         TeamPage.init();
  if (onPage('services.html'))     ServicesPage.init();
  if (onPage('contact.html') || onPage('about.html')) ContactPage.init();
  if (onPage('about.html'))        initTimeline();
});

/* ─────────────────────────────────────────────────────────────
   11. PUBLIC API (for inline onclick in rendered HTML)
   ───────────────────────────────────────────────────────────── */
window.BooksPage      = BooksPage;
window.BookDetailPage = BookDetailPage;
window.AuthorPanel    = AuthorPanel;
window.BlogPage       = BlogPage;
