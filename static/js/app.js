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

  // Rating star coloring with half increments
  document.querySelectorAll('[data-rating-group]').forEach((group) => {
    const starsInput = group.closest('form')?.querySelector('input[name="stars"]') || group.querySelector('input[name="stars"]');
    const icons = group.querySelectorAll('.star-icon i');

    const paint = (val) => {
      icons.forEach((icon, idx) => {
        const n = idx + 1;
        icon.classList.remove('bi-star', 'bi-star-fill', 'bi-star-half', 'text-warning', 'text-secondary');
        if (val >= n) {
          icon.classList.add('bi-star-fill', 'text-warning');
        } else if (val >= n - 0.5) {
          icon.classList.add('bi-star-half', 'text-warning');
        } else {
          icon.classList.add('bi-star', 'text-secondary');
        }
      });
    };

    paint(parseFloat(starsInput?.value || group.dataset.current || '0'));

    group.querySelectorAll('.star-icon').forEach((btn) => {
      btn.addEventListener('click', (e) => {
        const rect = btn.getBoundingClientRect();
        const clickX = e.clientX - rect.left;
        const valBase = parseInt(btn.dataset.index, 10);
        const val = clickX < rect.width / 2 ? valBase - 0.5 : valBase;
        if (starsInput) starsInput.value = val.toFixed(1);
        paint(val);
      });
    });
  });
});
