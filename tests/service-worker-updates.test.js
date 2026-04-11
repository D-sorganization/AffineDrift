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
  });

  test('removeBanner clears the notice', () => {
    showBanner();
    expect(document.getElementById('service-worker-update-banner')).not.toBeNull();

    removeBanner();
    expect(document.getElementById('service-worker-update-banner')).toBeNull();
  });
});
