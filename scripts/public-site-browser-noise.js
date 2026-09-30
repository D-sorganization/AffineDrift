/** Filters browser noise that is not a first-party AffineDrift regression. */

function isActionableConsoleError(message) {
  if (message.includes('Permissions policy violation: compute-pressure')) return false;
  if (message.includes('Failed to load resource: net::ERR_')) return false;
  return true;
}

function isActionablePageError(message) {
  return !message.includes("Failed to read the 'localStorage' property from 'Window'");
}

function fixedElementCanObscureHeading(style) {
  const zIndex = Number.parseInt(style.zIndex, 10);
  return style.pointerEvents !== 'none' && (Number.isNaN(zIndex) || zIndex >= 0);
}

function headingBeginsWithinViewport(rect, viewport) {
  return Boolean(
    rect &&
    rect.width > 0 &&
    rect.height > 0 &&
    rect.top < viewport.height &&
    rect.bottom > 0 &&
    rect.left < viewport.width &&
    rect.right > 0
  );
}

module.exports = {
  fixedElementCanObscureHeading,
  headingBeginsWithinViewport,
  isActionableConsoleError,
  isActionablePageError,
};
