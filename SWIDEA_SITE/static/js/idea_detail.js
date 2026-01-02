function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');

document.addEventListener('DOMContentLoaded', function() {
    const starBadge = document.getElementById('star-badge');
    if (starBadge) {
        starBadge.addEventListener('click', function() {
            const ideaId = this.getAttribute('data-idea-id');
            toggleStar(ideaId, this);
        });
    }
});

function toggleStar(ideaId, starElement) {
    fetch(`/idea/${ideaId}/toggle-star/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
            'Content-Type': 'application/json',
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.is_starred) {
            starElement.classList.remove('unstarred');
            starElement.classList.add('starred');
        } else {
            starElement.classList.remove('starred');
            starElement.classList.add('unstarred');
        }
    })
    .catch(error => console.error('Error:', error));
}