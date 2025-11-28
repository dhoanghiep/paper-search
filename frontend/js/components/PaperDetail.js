import { api } from '../api.js';

export async function PaperDetail(id) {
    try {
        const paper = await api.get(`/papers/${id}`);

        return `
            <div class="card">
                <h2>${paper.title}</h2>
                <p><strong>Authors:</strong> ${Array.isArray(paper.authors) ? paper.authors.join(', ') : (paper.authors || 'N/A')}</p>
                <p><strong>Published:</strong> ${new Date(paper.published_date).toLocaleDateString()}</p>
                <p><strong>Categories:</strong> ${paper.categories && paper.categories.length > 0 ? paper.categories.map(c => c.name).join(', ') : 'Uncategorized'}</p>
                <p><strong>PDF URL:</strong> <a href="${paper.pdf_url || '#'}" target="_blank">${paper.pdf_url || 'Not available'}</a></p>
                
                <h3>Summary</h3>
                <p>${paper.summary || 'No summary available'}</p>
                
                <h3>Abstract</h3>
                <p>${paper.abstract || 'No abstract available'}</p>
                
                <button class="btn btn-secondary" onclick="history.back()">Back</button>
            </div>
        `;
    } catch (error) {
        return `<div class="card">Error loading paper: ${error.message}</div>`;
    }
}
