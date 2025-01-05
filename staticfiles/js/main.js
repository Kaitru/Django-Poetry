document.addEventListener('DOMContentLoaded', function() {
    const timeRange = document.getElementById('timeRange');
    if (timeRange) {
        timeRange.addEventListener('change', function() {
            fetch(`/api/top-authors/?period=${this.value}`)
                .then(response => response.json())
                .then(data => {
                    const topAuthors = document.getElementById('topAuthors');
                    topAuthors.innerHTML = data.authors.map(author => `
                        <div class="d-flex justify-content-between align-items-center mb-2">
                            <a href="${author.url}">${author.username}</a>
                            <span class="badge bg-success">${author.rating.toFixed(2)}</span>
                        </div>
                    `).join('');
                });
        });
    }
}); 