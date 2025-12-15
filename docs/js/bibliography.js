document.addEventListener('DOMContentLoaded', async function() {
    const bibList = document.getElementById('bib-list');
    const bibSearch = document.getElementById('bib-search');
    const bibDetails = document.getElementById('bib-details');

    let references = [];
    let readingPaths = [];

    try {
        const response = await fetch('data/bibliography.json');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        references = await response.json();

        try {
            const pathResp = await fetch('data/reading_paths.json');
            if (pathResp.ok) {
                readingPaths = await pathResp.json();
                renderPaths(readingPaths);
            }
        } catch (e) {
            console.log("No reading paths found or error loading.");
        }

        renderList(references);
    } catch (e) {
        console.error("Failed to load bibliography:", e);
        if (bibList) {
            bibList.innerHTML = `<p style="color: red;">Failed to load bibliography data. Please try again later.</p>`;
        }
    }

    if (bibSearch) {
        bibSearch.addEventListener('input', (e) => {
            const query = e.target.value.toLowerCase();
            const filtered = references.filter(ref => {
                const searchStr = `${ref.title} ${ref.authors.join(' ')} ${ref.concepts.join(' ')} ${ref.year}`.toLowerCase();
                return searchStr.includes(query);
            });
            renderList(filtered);
        });
    }

    function renderPaths(paths) {
        const container = document.createElement('div');
        container.className = 'reading-paths-container';
        container.style.marginBottom = '2rem';

        const pathsHtml = paths.map((path, index) => `
            <div class="reading-path-card" data-index="${index}" style="background: var(--bg-secondary); padding: 1rem; border-radius: 8px; flex: 1; min-width: 250px; cursor: pointer; border: 1px solid var(--border-color); transition: transform 0.2s;">
                <h4 style="margin-bottom: 0.5rem; color: var(--accent-blue);">${path.title}</h4>
                <p style="font-size: 0.9rem; margin-bottom: 0;">${path.description}</p>
            </div>
        `).join('');

        container.innerHTML = `
            <h3 class="section-heading" style="font-size: 1.2rem; margin-bottom: 1rem;">Recommended Reading Paths</h3>
            <div style="display: flex; gap: 1rem; flex-wrap: wrap;">
                ${pathsHtml}
                <div class="reading-path-card show-all-btn" style="background: var(--bg-secondary); padding: 1rem; border-radius: 8px; flex: 0 0 auto; cursor: pointer; border: 1px solid var(--border-color); display: flex; align-items: center; transition: transform 0.2s;">
                    <span style="font-weight: 500;">Show All</span>
                </div>
            </div>
        `;

        if (bibSearch && bibSearch.parentNode) {
            bibSearch.parentNode.insertBefore(container, bibSearch);
        }

        container.querySelectorAll('.reading-path-card[data-index]').forEach(card => {
            card.addEventListener('click', () => {
                const index = card.getAttribute('data-index');
                const path = paths[index];
                const filtered = references.filter(r => path.items.includes(r.id));
                renderList(filtered);
                // Visual feedback
                container.querySelectorAll('.reading-path-card').forEach(c => c.style.borderColor = 'var(--border-color)');
                card.style.borderColor = 'var(--accent-blue)';
            });
        });

        container.querySelector('.show-all-btn').addEventListener('click', () => {
            renderList(references);
            container.querySelectorAll('.reading-path-card').forEach(c => c.style.borderColor = 'var(--border-color)');
        });
    }

    function renderList(items) {
        if (!bibList) return;

        if (items.length === 0) {
            bibList.innerHTML = '<p>No matching references found.</p>';
            return;
        }

        bibList.innerHTML = items.map(ref => `
            <div class="resource-card bib-item" data-id="${ref.id}" style="cursor: pointer; transition: transform 0.2s;">
                <h3 style="margin-bottom: 0.5rem; font-size: 1.1rem;">${ref.title}</h3>
                <p style="margin-bottom: 0.5rem; color: var(--text-light);">${ref.authors.join(', ')} (${ref.year})</p>
                <div class="tags" style="display: flex; flex-wrap: wrap; gap: 0.5rem;">
                    ${ref.concepts.slice(0, 3).map(c => `<span style="background: var(--bg-tertiary); padding: 2px 6px; border-radius: 4px; font-size: 0.8rem;">${c}</span>`).join('')}
                </div>
            </div>
        `).join('');

        // Add click listeners
        document.querySelectorAll('.bib-item').forEach(item => {
            item.addEventListener('click', () => {
                const id = item.getAttribute('data-id');
                const ref = references.find(r => r.id === id);
                if (ref) showDetails(ref);
            });
        });
    }

    function showDetails(ref) {
        if (!bibDetails) return;

        bibDetails.innerHTML = `
            <h3 class="sidebar-heading">Reference Details</h3>
            <div style="background: var(--bg-secondary); padding: 1rem; border-radius: 8px;">
                <h4 style="font-size: 1.1rem; margin-bottom: 0.5rem;">${ref.title}</h4>
                <p style="margin-bottom: 0.5rem;"><strong>Authors:</strong> ${ref.authors.join(', ')}</p>
                <p style="margin-bottom: 0.5rem;"><strong>Year:</strong> ${ref.year}</p>
                <p style="margin-bottom: 0.5rem;"><strong>Venue:</strong> ${ref.venue || 'N/A'}</p>
                <p style="margin-bottom: 1rem;">${ref.description}</p>

                <div style="margin-bottom: 1rem;">
                    <strong>Concepts:</strong>
                    <ul style="padding-left: 1rem; margin-top: 0.5rem;">
                        ${ref.concepts.map(c => `<li>${c}</li>`).join('')}
                    </ul>
                </div>

                <a href="${ref.scholar_url}" target="_blank" rel="noopener noreferrer" class="resource-link" style="display: block; margin-bottom: 0.5rem;">
                    Google Scholar Query →
                </a>

                ${ref.related_ids && ref.related_ids.length > 0 ? `
                    <div style="margin-top: 1rem;">
                        <strong>Related:</strong>
                        <ul style="padding-left: 1rem; margin-top: 0.5rem;">
                             ${ref.related_ids.map(rid => {
                                 const related = references.find(r => r.id === rid);
                                 return related ? `<li><button class="text-button related-ref-btn" data-id="${rid}" style="background:none; border:none; padding:0; color:var(--accent-blue); text-decoration:underline; cursor:pointer;">${related.title}</button></li>` : '';
                             }).join('')}
                        </ul>
                    </div>
                ` : ''}
            </div>
        `;

        // Add listeners for related links
        bibDetails.querySelectorAll('.related-ref-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const id = btn.getAttribute('data-id');
                const relatedRef = references.find(r => r.id === id);
                if (relatedRef) showDetails(relatedRef);
            });
        });

        // Mobile support: scroll to details
        if (window.innerWidth < 768) {
             bibDetails.scrollIntoView({ behavior: 'smooth' });
        }
    }
});
