document.addEventListener('DOMContentLoaded', () => {
  const alerts = document.querySelectorAll('.alert-dismissible');

  alerts.forEach((alert) => {
    const bsAlert = new bootstrap.Alert(alert);

    setTimeout(() => {
      if (alert.classList.contains('show')) {
        bsAlert.close();
      }
    }, 6000);
  });

  // Debounced search submit for book list
  const searchInput = document.querySelector('#book-filters input[name="q"]');
  const form = document.querySelector('#book-filters');
  if (searchInput && form) {
    let debounceTimer;
    let lastSubmitted = searchInput.value;

    const debounce = (fn, wait = 400) => (...args) => {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(() => fn(...args), wait);
    };

    const triggerSubmit = () => {
      const current = searchInput.value.trim();
      // Submit only when cleared or at least 2 chars and value changed
      if (current === lastSubmitted) return;
      if (current === '' || current.length >= 2) {
        lastSubmitted = current;
        form.requestSubmit();
      }
    };

    searchInput.addEventListener('input', debounce(triggerSubmit, 450));

    // Keep filters when changing selects
    form.querySelectorAll('select').forEach((select) => {
      select.addEventListener('change', () => form.requestSubmit());
    });
  }
});
