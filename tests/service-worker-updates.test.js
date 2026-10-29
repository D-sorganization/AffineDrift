const {
  init,
  showBanner,
  removeBanner,
  UPDATE_MESSAGE_TYPE,
} = require('../js/service-worker-updates.js');

describe('service-worker-updates', () => {
  beforeEach(() => {
    document.body.innerHTML = '';
    Object.defineProperty(window.navigator, 'serviceWorker', {
      configurable: true,
      value: {
        addEventListener: jest.fn(),
        controller: { state: 'activated' },
      },
    });
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  test('registers a message listener when service workers are available', () => {
    expect(init()).toBe(true);
    expect(window.navigator.serviceWorker.addEventListener).toHaveBeenCalledWith(
      'message',
      expect.any(Function)
    );
  });

  test('renders a reloadable banner when an update message arrives', () => {
    init();
    const handler = window.navigator.serviceWorker.addEventListener.mock.calls[0][1];

    handler({ data: { type: UPDATE_MESSAGE_TYPE } });

    const banner = document.getElementById('service-worker-update-banner');
    expect(banner).not.toBeNull();
    expect(banner.textContent).toContain('New content is available');
    expect(banner.querySelectorAll('button')).toHaveLength(2);
    expect(banner.className).toBe('site-update-notice');
    expect(banner.getAttribute('style')).toBeNull();
    expect(banner.querySelector('.site-update-notice__actions')).not.toBeNull();
    for (const button of banner.querySelectorAll('button')) {
      expect(button.getAttribute('style')).toBeNull();
      expect(button.className).toMatch(/site-update-notice__button/);
    }
  });

  test('removeBanner clears the notice', () => {
    showBanner();
    expect(document.getElementById('service-worker-update-banner')).not.toBeNull();

    removeBanner();
    expect(document.getElementById('service-worker-update-banner')).toBeNull();
  });

  test('shows no banner on first install (no controller at page load) (#5167)', () => {
    window.navigator.serviceWorker.controller = null;
    init();
    const handler = window.navigator.serviceWorker.addEventListener.mock.calls[0][1];

    // clients.claim() makes a controller appear after the page loaded; the
    // broadcast that follows is still a first install, not an update.
    window.navigator.serviceWorker.controller = { state: 'activated' };
    handler({ data: { type: UPDATE_MESSAGE_TYPE } });

    expect(document.getElementById('service-worker-update-banner')).toBeNull();
  });

  test('ignores messages of other types', () => {
    init();
    const handler = window.navigator.serviceWorker.addEventListener.mock.calls[0][1];
    handler({ data: { type: 'something-else' } });
    expect(document.getElementById('service-worker-update-banner')).toBeNull();
  });
});
