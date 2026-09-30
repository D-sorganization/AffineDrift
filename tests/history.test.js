const { updateHistorySidebar, initArticleHistory, initCategoryHistory } = require('../js/history.js');

function setPath(pathname) {
  window.history.pushState(null, '', pathname);
}

describe('updateHistorySidebar', () => {
  beforeEach(() => {
    document.body.innerHTML = '';
    localStorage.clear();
    setPath('/index.html');
    document.title = 'AffineDrift';
  });

  test('does nothing when #history-list is absent', () => {
    expect(() => updateHistorySidebar()).not.toThrow();
    expect(localStorage.getItem('affinedrift_history')).toBeNull();
  });

  test('records the current page and shows the empty state on a first visit', () => {
    document.body.innerHTML = '<ul id="history-list"></ul>';
    document.title = 'Superposition - AffineDrift';
    setPath('/articles/superposition.html');

    updateHistorySidebar();

    const stored = JSON.parse(localStorage.getItem('affinedrift_history'));
    expect(stored).toEqual([
      expect.objectContaining({ title: 'Superposition', url: 'superposition.html' }),
    ]);

    // The current page is excluded from its own "recent" display.
    const list = document.getElementById('history-list');
    expect(list.querySelector('.history-empty')).not.toBeNull();
    expect(list.querySelector('a[href="/resources/articles.html"]').textContent).toBe(
      'Explore articles'
    );
  });

  test('lists a previously visited page, most recent first', () => {
    localStorage.setItem(
      'affinedrift_history',
      JSON.stringify([{ title: 'Old Page', url: 'old-page.html', fullUrl: 'https://example.com/old-page.html' }])
    );
    document.body.innerHTML = '<ul id="history-list"></ul>';
    document.title = 'New Page - AffineDrift';
    setPath('/new-page.html');

    updateHistorySidebar();

    const list = document.getElementById('history-list');
    const links = list.querySelectorAll('li a');
    expect(links).toHaveLength(1);
    expect(links[0].textContent).toBe('Old Page');

    const stored = JSON.parse(localStorage.getItem('affinedrift_history'));
    expect(stored.map((item) => item.url)).toEqual(['new-page.html', 'old-page.html']);
  });

  test('hides excluded hub pages from the display without dropping them from storage', () => {
    localStorage.setItem(
      'affinedrift_history',
      JSON.stringify([{ title: 'Home', url: 'index.html', fullUrl: 'https://example.com/index.html' }])
    );
    document.body.innerHTML = '<ul id="history-list"></ul>';
    document.title = 'New Page - AffineDrift';
    setPath('/new-page.html');

    updateHistorySidebar();

    const list = document.getElementById('history-list');
    expect(list.querySelector('.history-empty')).not.toBeNull();

    const stored = JSON.parse(localStorage.getItem('affinedrift_history'));
    expect(stored.some((item) => item.url === 'index.html')).toBe(true);
  });

  test('truncates long titles and sanitizes unsafe stored urls', () => {
    localStorage.setItem(
      'affinedrift_history',
      JSON.stringify([
        {
          title: 'A Very Long Chapter Title That Exceeds The Sidebar Limit',
          url: 'javascript:alert(1)',
        },
      ])
    );
    document.body.innerHTML = '<ul id="history-list"></ul>';
    document.title = 'New Page - AffineDrift';
    setPath('/new-page.html');

    updateHistorySidebar();

    const anchor = document.querySelector('#history-list li a');
    expect(anchor.textContent.endsWith('...')).toBe(true);
    expect(anchor.textContent.length).toBe(43); // 40 chars + "..."
    expect(anchor.getAttribute('href')).toBe('#');
  });

  test('recovers from corrupted stored history without throwing', () => {
    localStorage.setItem('affinedrift_history', 'not json');
    document.body.innerHTML = '<ul id="history-list"></ul>';
    setPath('/new-page.html');

    expect(() => updateHistorySidebar()).not.toThrow();
    expect(JSON.parse(localStorage.getItem('affinedrift_history'))).toHaveLength(1);
  });
});

describe('initArticleHistory', () => {
  beforeEach(() => {
    document.body.innerHTML = '';
    localStorage.clear();
    setPath('/index.html');
    document.title = 'AffineDrift';
  });

  test('does nothing when neither the tracking nor the list target exist', () => {
    expect(() => initArticleHistory()).not.toThrow();
    expect(localStorage.getItem('affinedrift_articles_history')).toBeNull();
  });

  test('tracks a visit to a known article page', () => {
    document.title = 'Superposition - AffineDrift';
    setPath('/articles/superposition.html');

    initArticleHistory();

    const stored = JSON.parse(localStorage.getItem('affinedrift_articles_history'));
    expect(stored).toEqual([{ title: 'Superposition', url: 'articles/superposition.html' }]);
  });

  test('ignores an /articles/ page that is not in the known list', () => {
    document.title = 'Unlisted - AffineDrift';
    setPath('/articles/unlisted-page.html');

    initArticleHistory();

    expect(localStorage.getItem('affinedrift_articles_history')).toBeNull();
  });

  test('renders the empty state when no articles have been visited', () => {
    document.body.innerHTML = '<ul id="articles-history-list"></ul>';
    setPath('/index.html');

    initArticleHistory();

    const list = document.getElementById('articles-history-list');
    expect(list.querySelector('.history-empty')).not.toBeNull();
  });

  test('renders previously tracked articles without truncating titles', () => {
    const longTitle = 'A Very Long Chapter Title That Exceeds The Sidebar Limit';
    localStorage.setItem(
      'affinedrift_articles_history',
      JSON.stringify([{ title: longTitle, url: 'articles/superposition.html' }])
    );
    document.body.innerHTML = '<ul id="articles-history-list"></ul>';
    setPath('/index.html');

    initArticleHistory();

    const anchor = document.querySelector('#articles-history-list li a');
    expect(anchor.textContent).toBe(longTitle);
  });
});

describe('initCategoryHistory', () => {
  const config = {
    listElementId: 'models-history-list',
    storageKey: 'affinedrift_models_history',
    emptyMessage: 'No recent models yet',
    pages: ['models.html', 'models-drake.html', 'models-mujoco.html'],
    fallbackUrl: 'models-drake.html',
  };

  beforeEach(() => {
    document.body.innerHTML = '';
    localStorage.clear();
    setPath('/models/models-drake.html');
    document.title = 'Drake - AffineDrift';
  });

  test('does nothing when the list element is absent', () => {
    expect(() => initCategoryHistory(config)).not.toThrow();
    expect(localStorage.getItem(config.storageKey)).toBeNull();
  });

  test('records a tracked page and renders it', () => {
    document.body.innerHTML = '<ul id="models-history-list"></ul>';

    initCategoryHistory(config);

    const stored = JSON.parse(localStorage.getItem(config.storageKey));
    expect(stored).toEqual([{ title: 'Drake', url: 'models-drake.html' }]);

    const anchor = document.querySelector('#models-history-list li a');
    expect(anchor.textContent).toBe('Drake');
  });

  test('shows the empty message and skips storage for an untracked page', () => {
    document.title = 'Modeling Suite - AffineDrift';
    setPath('/models/models.html');
    document.body.innerHTML = '<ul id="models-history-list"></ul>';

    initCategoryHistory({ ...config, pages: ['models-drake.html', 'models-mujoco.html'] });

    expect(localStorage.getItem(config.storageKey)).toBeNull();
    const list = document.getElementById('models-history-list');
    expect(list.textContent).toBe(config.emptyMessage);
  });

  test('moves a revisited page to the front instead of duplicating it', () => {
    localStorage.setItem(
      config.storageKey,
      JSON.stringify([
        { title: 'MuJoCo', url: 'models-mujoco.html' },
        { title: 'Drake', url: 'models-drake.html' },
      ])
    );
    document.body.innerHTML = '<ul id="models-history-list"></ul>';

    initCategoryHistory(config);

    const stored = JSON.parse(localStorage.getItem(config.storageKey));
    expect(stored.map((item) => item.url)).toEqual(['models-drake.html', 'models-mujoco.html']);
  });

  test('caps stored history at 10 entries', () => {
    const seeded = Array.from({ length: 12 }, (_, i) => ({
      title: `Page ${i}`,
      url: `models-mujoco.html?${i}`,
    }));
    localStorage.setItem(config.storageKey, JSON.stringify(seeded));
    document.body.innerHTML = '<ul id="models-history-list"></ul>';

    initCategoryHistory(config);

    const stored = JSON.parse(localStorage.getItem(config.storageKey));
    expect(stored).toHaveLength(10);
    expect(stored[0].url).toBe('models-drake.html');
  });

  test('falls back to the configured url when the pathname has no filename', () => {
    setPath('/');
    document.body.innerHTML = '<ul id="models-history-list"></ul>';

    initCategoryHistory(config);

    const stored = JSON.parse(localStorage.getItem(config.storageKey));
    expect(stored[0].url).toBe(config.fallbackUrl);
  });

  test('sanitizes an unsafe stored url to "#"', () => {
    localStorage.setItem(
      config.storageKey,
      JSON.stringify([{ title: 'Bad', url: 'javascript:alert(1)' }])
    );
    document.title = 'Modeling Suite - AffineDrift';
    setPath('/models/models.html');
    document.body.innerHTML = '<ul id="models-history-list"></ul>';

    initCategoryHistory({ ...config, pages: ['models-drake.html'] });

    const anchor = document.querySelector('#models-history-list li a');
    expect(anchor.getAttribute('href')).toBe('#');
  });
});
