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
    banner.setAttribute('role', 'status');
    banner.setAttribute('aria-live', 'polite');

    Object.assign(banner.style, {
      position: 'fixed',
      left: '16px',
      right: '16px',
      bottom: '16px',
      zIndex: '9999',
      display: 'flex',
      gap: '12px',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '12px 14px',
      border: '1px solid rgba(255, 255, 255, 0.2)',
      borderRadius: '8px',
      background: '#111827',
      color: '#f9fafb',
      boxShadow: '0 10px 24px rgba(0, 0, 0, 0.24)',
      fontSize: '0.95rem',
      lineHeight: '1.4',
      fontFamily: 'inherit',
    });

    const message = document.createElement('span');
    message.textContent = 'New content is available.';

    const actions = document.createElement('div');
    Object.assign(actions.style, {
      display: 'flex',
      gap: '8px',
      flexShrink: '0',
    });

    const reloadButton = document.createElement('button');
    reloadButton.type = 'button';
    reloadButton.textContent = 'Reload';
    reloadButton.setAttribute('aria-label', 'Reload to load the latest content');
    Object.assign(reloadButton.style, {
      border: '1px solid rgba(255, 255, 255, 0.2)',
      borderRadius: '8px',
      background: '#f9fafb',
      color: '#111827',
      padding: '8px 12px',
      cursor: 'pointer',
      font: 'inherit',
    });
    reloadButton.addEventListener('click', () => {
      window.location.reload();
    });

    const dismissButton = document.createElement('button');
    dismissButton.type = 'button';
    dismissButton.textContent = 'Dismiss';
    dismissButton.setAttribute('aria-label', 'Dismiss the update notice');
    Object.assign(dismissButton.style, {
      border: '1px solid rgba(255, 255, 255, 0.2)',
      borderRadius: '8px',
      background: 'transparent',
      color: '#f9fafb',
      padding: '8px 12px',
      cursor: 'pointer',
      font: 'inherit',
    });
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
