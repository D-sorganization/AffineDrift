/** Filters browser noise that is not a first-party AffineDrift regression. */

const TRANSIENT_SUBRESOURCE_CONSOLE_RE =
  /Failed to load resource: the server responded with a status of (502|503|504)\b/;

function isTransientSubresourceLoadConsoleError(message) {
  return TRANSIENT_SUBRESOURCE_CONSOLE_RE.test(message);
}

function failuresAreOnlyRetriableSubresourceNoise(failures) {
  return failures.length > 0 && failures.every((failure) => {
    if (!failure.startsWith('console: ')) return false;
    return isTransientSubresourceLoadConsoleError(failure.slice('console: '.length));
  });
}

function isActionableConsoleError(message) {
  if (message.includes('Permissions policy violation: compute-pressure')) return false;
  if (message.includes('Failed to load resource: net::ERR_')) return false;
  return true;
}

function isActionablePageError(message) {
  return !message.includes("Failed to read the 'localStorage' property from 'Window'");
}

module.exports = {
  failuresAreOnlyRetriableSubresourceNoise,
  isActionableConsoleError,
  isActionablePageError,
  isTransientSubresourceLoadConsoleError,
};
