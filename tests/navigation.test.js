const { generateTableOfContents } = require('../js/navigation.js');


describe('generated table of contents', () => {
  beforeEach(() => {
    document.body.innerHTML = '';
  });

  test('does not duplicate an authored table of contents', () => {
    document.body.innerHTML = `
      <aside class="left-sidebar">
        <nav class="toc-nav"><ul><li><a href="#overview">Overview</a></li></ul></nav>
      </aside>
      <main><section id="overview"><h2>Overview</h2></section></main>
    `;

    generateTableOfContents();

    expect(document.querySelectorAll('.toc-nav')).toHaveLength(1);
    expect(document.querySelectorAll('.sidebar-toc')).toHaveLength(0);
  });
});
