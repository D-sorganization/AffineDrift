/** Filters browser noise that is not a first-party AffineDrift regression. */

function isActionableConsoleError(message) {
  if (message.includes('Permissions policy violation: compute-pressure')) return false;
  if (message.includes('Failed to load resource: net::ERR_')) return false;
  return true;
}

function isActionablePageError(message) {
  return !message.includes("Failed to read the 'localStorage' property from 'Window'");
}

module.exports = {
  isActionableConsoleError,
  isActionablePageError,
};
