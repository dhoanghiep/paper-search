import { api } from '../api.js';

const PAGE_SIZE = 20;
let currentOffset = 0;
let currentSearch = '';
let currentCategory = '';

async function fetchAndRender() {
    const tbody = document.getElementById('papersTable');
    const totalEl = document.getElementById('papersTotalInfo');
    if (!tbody) return;

    const params = new URLSearchParams({
        limit: PAGE_SIZE,
        offset: currentOffset,
    });
    if (currentSearch) params.set('search', currentSearch);
    if (currentCategory) params.set('category', currentCategory);

    try {
        const data = await api.get(`/papers?${params}`);
        const papers = data.papers || [];
        const total = data.total || 0;

        if (totalEl) {
            const start = currentOffset + 1;
            const end = Math.min(currentOffset + papers.length, total);
            totalEl.textContent = total > 0 ? `Showing ${start}–${end} of ${total}` : 'No papers found';
        }

        tbody.innerHTML = papers.map(p => `
            <tr>
                <td><a href="#paper/${p.id}">${p.title}</a></td>
                <td>${Array.isArray(p.authors) ? p.authors.slice(0, 2).join(', ') : (p.authors ? p.authors.split(',').slice(0, 2).join(', ') : 'N/A')}</td>
                <td>${p.categories && p.categories.length > 0 ? p.categories.map(c => `<span class="badge">${c.name}</span>`).join(' ') : 'Uncategorized'}</td>
                <td>${p.published_date ? new Date(p.published_date).toLocaleDateString() : 'N/A'}</td>
                <td><button class="btn btn-primary" onclick="window.viewPaper('${p.id}')">View</button></td>
            </tr>
        `).join('') || '<tr><td colspan="5" style="text-align:center">No papers found</td></tr>';

        // Pagination buttons
        const prevBtn = document.getElementById('prevPageBtn');
        const nextBtn = document.getElementById('nextPageBtn');
        if (prevBtn) prevBtn.disabled = currentOffset === 0;
        if (nextBtn) nextBtn.disabled = currentOffset + PAGE_SIZE >= total;
    } catch (error) {
        tbody.innerHTML = `<tr><td colspan="5">Error loading papers: ${error.message}</td></tr>`;
    }
}

export async function PapersList() {
    // Reset state on each fresh render
    currentOffset = 0;
    currentSearch = '';
    currentCategory = '';

    const html = `
        <h2>Papers</h2>
        <div class="search-bar" style="display:flex;gap:8px;margin-bottom:12px">
            <input type="text" id="searchInput" placeholder="Search papers..." style="flex:1">
            <button class="btn" id="searchBtn">Search</button>
            <button class="btn" id="clearSearchBtn">Clear</button>
        </div>
        <div class="card">
            <div id="papersTotalInfo" style="margin-bottom:8px;color:#666"></div>
            <table>
                <thead>
                    <tr>
                        <th>Title</th>
                        <th>Authors</th>
                        <th>Category</th>
                        <th>Published</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody id="papersTable">
                    <tr><td colspan="5" style="text-align:center">Loading…</td></tr>
                </tbody>
            </table>
            <div style="display:flex;gap:8px;margin-top:12px;align-items:center">
                <button class="btn" id="prevPageBtn" disabled>← Prev</button>
                <button class="btn" id="nextPageBtn">Next →</button>
            </div>
        </div>
    `;

    // Defer wiring until after DOM insertion
    setTimeout(() => {
        const searchInput = document.getElementById('searchInput');
        const searchBtn = document.getElementById('searchBtn');
        const clearBtn = document.getElementById('clearSearchBtn');
        const prevBtn = document.getElementById('prevPageBtn');
        const nextBtn = document.getElementById('nextPageBtn');

        const doSearch = () => {
            currentSearch = searchInput ? searchInput.value.trim() : '';
            currentOffset = 0;
            fetchAndRender();
        };

        if (searchBtn) searchBtn.addEventListener('click', doSearch);
        if (searchInput) searchInput.addEventListener('keydown', e => { if (e.key === 'Enter') doSearch(); });
        if (clearBtn) clearBtn.addEventListener('click', () => {
            if (searchInput) searchInput.value = '';
            currentSearch = '';
            currentOffset = 0;
            fetchAndRender();
        });
        if (prevBtn) prevBtn.addEventListener('click', () => {
            currentOffset = Math.max(0, currentOffset - PAGE_SIZE);
            fetchAndRender();
        });
        if (nextBtn) nextBtn.addEventListener('click', () => {
            currentOffset += PAGE_SIZE;
            fetchAndRender();
        });

        fetchAndRender();
    }, 0);

    return html;
}
