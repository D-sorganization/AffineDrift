;(function (root, factory) {
  const api = factory(root);
  root.AffineDriftServiceWorkerUpdates = api;

  if (typeof module !== 'undefined' && module.exports) {
    module.exports = api;
  }
})(typeof window !== 'undefined' ? window : globalThis, function (root) {
  const BANNER_ID = 'service-worker-update-banner';
  const UPDATE_MESSAGE_TYPE =
    root.AffineDriftServiceWorkerUtils?.UPDATE_MESSAGE_TYPE ??
    'affinedrift:sw-update-available';

  function removeBanner() {
    const existing = document.getElementById(BANNER_ID);
    if (existing) {
      existing.remove();
    }
  }

  function showBanner() {
    if (document.getElementById(BANNER_ID)) {
      return;
    }

    const banner = document.createElement('div');
    banner.id = BANNER_ID;
    banner.className = 'site-update-notice';
    banner.setAttribute('role', 'status');
    banner.setAttribute('aria-live', 'polite');

    const message = document.createElement('span');
    message.textContent = 'New content is available.';

    const actions = document.createElement('div');
    actions.className = 'site-update-notice__actions';

    const reloadButton = document.createElement('button');
    reloadButton.type = 'button';
    reloadButton.className =
      'site-update-notice__button site-update-notice__button--primary';
    reloadButton.textContent = 'Reload';
    reloadButton.setAttribute('aria-label', 'Reload to load the latest content');
    reloadButton.title = 'Reload to load the latest content';
    reloadButton.addEventListener('click', () => {
      window.location.reload();
    });

    const dismissButton = document.createElement('button');
    dismissButton.type = 'button';
    dismissButton.className = 'site-update-notice__button';
    dismissButton.textContent = 'Dismiss';
    dismissButton.setAttribute('aria-label', 'Dismiss the update notice');
    dismissButton.title = 'Dismiss the update notice';
    dismissButton.addEventListener('click', removeBanner);

    actions.appendChild(reloadButton);
    actions.appendChild(dismissButton);
    banner.appendChild(message);
    banner.appendChild(actions);
    document.body.appendChild(banner);
  }

  function init() {
    if (!('serviceWorker' in navigator)) {
      return false;
    }

    const controller = navigator.serviceWorker;
    if (typeof controller.addEventListener !== 'function') {
      return false;
    }

    controller.addEventListener('message', (event) => {
      if (event?.data?.type === UPDATE_MESSAGE_TYPE) {
        showBanner();
      }
    });

    return true;
  }

  return {
    init,
    showBanner,
    removeBanner,
    UPDATE_MESSAGE_TYPE,
  };
});
