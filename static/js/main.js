document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('clipForm');
    const processBtn = document.getElementById('processBtn');
    const loader = document.getElementById('loader');
    const resultsArea = document.getElementById('resultsArea');
    const videoGrid = document.getElementById('videoGrid');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const url = document.getElementById('videoUrl').value;
        if (!url) return;

        // UI State: Loading
        processBtn.disabled = true;
        processBtn.classList.add('hidden');
        loader.classList.remove('hidden');
        resultsArea.classList.add('hidden');
        videoGrid.innerHTML = ''; // Clear previous results

        const formData = new FormData();
        formData.append('url', url);

        try {
            const response = await fetch('/api/process', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (data.status === 'success') {
                // Populate results
                data.videos.forEach((videoFile, index) => {
                    const card = document.createElement('div');
                    card.className = 'video-card';
                    card.innerHTML = `
                        <h4><i class="fa-solid fa-film"></i> Short #${index + 1}</h4>
                        <div style="aspect-ratio: 9/16; background: #000; margin-bottom: 10px; border-radius: 8px; display: flex; align-items: center; justify-content: center;">
                             <i class="fa-regular fa-circle-play" style="font-size: 2rem; opacity: 0.5;"></i>
                        </div>
                        <a href="/downloads/${videoFile}" class="download-btn" download>
                            <i class="fa-solid fa-download"></i> Download Video
                        </a>
                    `;
                    videoGrid.appendChild(card);
                });
                resultsArea.classList.remove('hidden');
            } else {
                alert('Error: ' + data.message);
            }

        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred during processing.');
        } finally {
            // UI State: Reset
            processBtn.disabled = false;
            processBtn.classList.remove('hidden');
            loader.classList.add('hidden');
        }
    });
});
