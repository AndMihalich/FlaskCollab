document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.last-seen').forEach(function(el) {
        var dt = el.getAttribute('data-datetime');
        if (dt) {
            el.textContent = moment(dt).fromNow();
        }
    });
});

document.addEventListener('DOMContentLoaded', function() {
    var searchInput = document.querySelector('input[name="query"]');
    var resultsList = document.querySelector('.user-search-results');
    if (searchInput && resultsList) {
        let lastValue = '';
        searchInput.addEventListener('input', function() {
            const value = searchInput.value.trim();
            if (value.length < 1 || value === lastValue) {
                resultsList.innerHTML = '';
                return;
            }
            lastValue = value;
            fetch(`/UserDB_search?q=${encodeURIComponent(value)}`)
                .then(response => response.json())
                .then(data => {
                    resultsList.innerHTML = '';
                    if (data.users && data.users.length > 0) {
                        data.users.forEach(function(user) {
                            const li = document.createElement('li');
                            li.className = 'list-group-item d-flex justify-content-between align-items-center';
                            li.innerHTML = `<a href="/UserDB/${user.username}">${user.username}</a> <span class="text-muted small">${user.email}</span>`;
                            resultsList.appendChild(li);
                        });
                    }
                });
        });
    }
});