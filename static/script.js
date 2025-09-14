// ==========================================================================
// Core Application Logic
// ==========================================================================

// === Utility: Toast Notification ===
function showToast(message, type = 'success') {
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.textContent = message;
  document.body.appendChild(toast);

  setTimeout(() => {
    toast.classList.add('show');
  }, 100);

  setTimeout(() => {
    toast.classList.remove('show');
    setTimeout(() => toast.remove(), 300);
  }, 2500);
}

// === Utility: Confirmation Dialog ===
function confirmAction(message) {
  return new Promise((resolve) => {
    const overlay = document.createElement('div');
    overlay.className = 'overlay';

    const dialog = document.createElement('div');
    dialog.className = 'dialog';

    dialog.innerHTML = `
      <p>${message}</p>
      <div class="dialog-buttons">
        <button class="confirm-yes btn">Yes</button>
        <button class="confirm-no btn">Cancel</button>
      </div>
    `;

    overlay.appendChild(dialog);
    document.body.appendChild(overlay);

    const yesBtn = dialog.querySelector('.confirm-yes');
    const noBtn = dialog.querySelector('.confirm-no');

    yesBtn.addEventListener('click', () => {
      overlay.remove();
      resolve(true);
    });

    noBtn.addEventListener('click', () => {
      overlay.remove();
      resolve(false);
    });
  });
}

// === Password Visibility Toggle ===
function setupPasswordToggle() {
  const passwordFields = document.querySelectorAll('input[type="password"]');

  passwordFields.forEach(passwordInput => {
    const wrapper = document.createElement('div');
    wrapper.className = 'input-wrap';
    passwordInput.parentNode.insertBefore(wrapper, passwordInput);
    wrapper.appendChild(passwordInput);

    const toggleBtn = document.createElement('button');
    toggleBtn.className = 'toggle-password';
    toggleBtn.setAttribute('type', 'button');
    toggleBtn.innerHTML = '<i class="fas fa-eye"></i>';

    wrapper.appendChild(toggleBtn);

    toggleBtn.addEventListener('click', () => {
      const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
      passwordInput.setAttribute('type', type);
      toggleBtn.innerHTML = type === 'password' ? '<i class="fas fa-eye"></i>' : '<i class="fas fa-eye-slash"></i>';
    });
  });
}

// ---
// ## Dynamic Background Functionality
const backgrounds = [
  'bg.jpg',
  'bg1.jpg',
  'bg2.jpg',
  'bg3.jpg'
];

function getRandomBackground() {
  const randomIndex = Math.floor(Math.random() * backgrounds.length);
  return backgrounds[randomIndex];
}

function setRandomBackground() {
  const randomBackground = getRandomBackground();
  const imageUrl = `/static/${randomBackground}`;
  document.body.style.backgroundImage = `url('${imageUrl}')`;
}
// ---

// === Main DOM Ready ===
document.addEventListener('DOMContentLoaded', () => {
  // Call the function to set a random background on page load
  setRandomBackground();

  // Setup password toggle on Login and Signup pages
  setupPasswordToggle();

  // Handle delete button
  document.querySelectorAll('.delete-btn').forEach(button => {
    button.addEventListener('click', async () => {
      const id = button.dataset.id;

      const confirmed = await confirmAction('Do you really want to delete this task?');
      if (!confirmed) return;

      fetch(`/delete/${id}`, { method: 'POST' })
        .then(res => res.json())
        .then(data => {
          if (data.success) {
            // Fade out row before removing
            const row = button.closest('tr');
            row.style.transition = 'opacity 0.5s ease';
            row.style.opacity = '0';
            setTimeout(() => row.remove(), 500);
            showToast('Task deleted successfully', 'danger');
          }
        });
    });
  });

  // Handle toggle status button
  document.querySelectorAll('.toggle-btn').forEach(button => {
    button.addEventListener('click', () => {
      const id = button.dataset.id;
      fetch(`/toggle/${id}`, { method: 'POST' })
        .then(res => res.json())
        .then(data => {
          if (data.success) {
            button.textContent = data.status === 'Completed' ? 'Mark Pending' : 'Mark Completed';

            // Add a little animation to the row
            const row = button.closest('tr');
            row.classList.toggle('completed');
            row.style.transition = 'background 0.5s ease, transform 0.2s ease';
            row.style.transform = 'scale(1.02)';
            setTimeout(() => (row.style.transform = 'scale(1)'), 200);

            showToast(`Task marked as ${data.status}`, 'success');
          }
        });
    });
  });
});