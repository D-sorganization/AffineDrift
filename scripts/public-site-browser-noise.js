/** Filters browser noise that is not a first-party AffineDrift regression. */

function isActionableConsoleError(message) {
  return !message.includes('Permissions policy violation: compute-pressure');
}

function isActionablePageError(message) {
  return !message.includes("Failed to read the 'localStorage' property from 'Window'");
}

module.exports = {
  isActionableConsoleError,
  isActionablePageError,
};
