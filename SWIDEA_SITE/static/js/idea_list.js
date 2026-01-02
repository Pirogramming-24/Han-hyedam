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
    document.querySelectorAll('.star-icon').forEach(function(star) {
        star.addEventListener('click', function() {
            const ideaId = this.getAttribute('data-idea-id');
            toggleStar(ideaId, this);
        });
    });
    
    document.querySelectorAll('.interest-btn').forEach(function(btn) {
        btn.addEventListener('click', function() {
            const control = this.closest('.interest-control');
            const ideaId = control.getAttribute('data-idea-id');
            const action = this.getAttribute('data-action');
            const valueSpan = control.querySelector('.interest-value');
            changeInterest(ideaId, action, valueSpan);
        });
    });
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

function changeInterest(ideaId, action, valueSpan) {
    fetch(`/idea/${ideaId}/change-interest/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `action=${action}`
    })
    .then(response => response.json())
    .then(data => {
        valueSpan.textContent = data.interest;
    })
    .catch(error => console.error('Error:', error));
}