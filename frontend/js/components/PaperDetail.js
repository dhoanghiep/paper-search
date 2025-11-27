import { api } from '../api.js';

export async function PaperDetail(id) {
    try {
        const paper = await api.get(`/papers/${id}`);

        return `
            <div class="card">
                <h2>${paper.title}</h2>
                <p><strong>Authors:</strong> ${paper.authors?.join(', ') || 'N/A'}</p>
                <p><strong>Published:</strong> ${new Date(paper.published_date).toLocaleDateString()}</p>
                <p><strong>Category:</strong> ${paper.category || 'Uncategorized'}</p>
                <p><strong>URL:</strong> <a href="${paper.url}" target="_blank">${paper.url}</a></p>
                
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
