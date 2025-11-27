import { api } from '../api.js';

export async function PapersList() {
    try {
        const papers = await api.get('/papers');

        return `
            <h2>Papers</h2>
            <div class="search-bar">
                <input type="text" id="searchInput" placeholder="Search papers...">
            </div>
            <div class="card">
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
                        ${papers.map(p => `
                            <tr>
                                <td><a href="#paper/${p.id}">${p.title}</a></td>
                                <td>${Array.isArray(p.authors) ? p.authors.slice(0, 2).join(', ') : (p.authors ? p.authors.split(',').slice(0, 2).join(', ') : 'N/A')}</td>
                                <td>${p.category || 'Uncategorized'}</td>
                                <td>${new Date(p.published_date).toLocaleDateString()}</td>
                                <td><button class="btn btn-primary" onclick="window.viewPaper('${p.id}')">View</button></td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
    } catch (error) {
        return `<div class="card">Error loading papers: ${error.message}</div>`;
    }
}
