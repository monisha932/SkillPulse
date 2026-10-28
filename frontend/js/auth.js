/**
 * Authentication Module
 */
const Auth = {
  currentUser: null,

  init() {
    this.currentUser = API.getUser();
    this.updateUI();
    this.bindEvents();
  },

  bindEvents() {
    // Demo login button
    const demoBtn = document.getElementById('btn-demo-login');
    if (demoBtn) {
      demoBtn.addEventListener('click', () => this.handleDemoLogin());
    }

    // Auth modal submit
    const authForm = document.getElementById('auth-form');
    if (authForm) {
      authForm.addEventListener('submit', (e) => this.handleAuthSubmit(e));
    }

    // Switch between login and register tabs
    document.querySelectorAll('.auth-tab').forEach((tab) => {
      tab.addEventListener('click', (e) => {
        const mode = e.target.dataset.mode;
        this.switchTab(mode);
      });
    });

    // Logout button
    const logoutBtn = document.getElementById('btn-logout');
    if (logoutBtn) {
      logoutBtn.addEventListener('click', () => this.logout());
    }
  },

  switchTab(mode) {
    document.querySelectorAll('.auth-tab').forEach((t) => t.classList.remove('active'));
    document.querySelector(`.auth-tab[data-mode="${mode}"]`)?.classList.add('active');

    const nameGroup = document.getElementById('group-register-name');
    const submitBtn = document.getElementById('btn-auth-submit');

    if (mode === 'register') {
      nameGroup.style.display = 'flex';
      submitBtn.textContent = 'Create Student Account';
    } else {
      nameGroup.style.display = 'none';
      submitBtn.textContent = 'Sign In to Platform';
    }
  },

  async handleAuthSubmit(e) {
    e.preventDefault();
    const activeTab = document.querySelector('.auth-tab.active');
    const mode = activeTab ? activeTab.dataset.mode : 'login';

    const email = document.getElementById('auth-email').value.trim();
    const password = document.getElementById('auth-password').value;
    const nameInput = document.getElementById('auth-name');
    const name = nameInput ? nameInput.value.trim() : '';

    try {
      let res;
      if (mode === 'register') {
        if (!name) {
          App.showToast('Please enter your full name', 'warning');
          return;
        }
        res = await API.register(name, email, password);
        App.showToast('Account created successfully! Welcome!', 'success');
      } else {
        res = await API.login(email, password);
        App.showToast('Signed in successfully!', 'success');
      }

      API.setToken(res.token);
      API.setUser(res.user);
      this.currentUser = res.user;
      this.updateUI();
      this.closeModal();

      // Load profile
      Profile.loadProfile();
    } catch (err) {
      App.showToast(err.message, 'error');
    }
  },

  async handleDemoLogin() {
    try {
      const res = await API.login('student@example.com', 'password123');
      API.setToken(res.token);
      API.setUser(res.user);
      this.currentUser = res.user;
      this.updateUI();
      this.closeModal();
      App.showToast('Logged in as Demo Student (Monisha & Pooja)!', 'success');

      // Refresh career profile
      Profile.loadProfile();
    } catch (err) {
      App.showToast('Demo login failed: ' + err.message, 'error');
    }
  },

  logout() {
    API.clearToken();
    this.currentUser = null;
    this.updateUI();
    this.openModal();
    App.showToast('Logged out of platform.', 'success');
  },

  openModal() {
    const modal = document.getElementById('auth-modal');
    if (modal) modal.classList.add('show');
  },

  closeModal() {
    const modal = document.getElementById('auth-modal');
    if (modal) modal.classList.remove('show');
  },

  updateUI() {
    const userInfoEl = document.getElementById('user-profile-widget');
    const userNameEl = document.getElementById('nav-user-name');
    const userAvatarEl = document.getElementById('nav-user-avatar');

    if (this.currentUser) {
      userInfoEl.style.display = 'flex';
      userNameEl.textContent = this.currentUser.name;
      userAvatarEl.textContent = this.currentUser.name.charAt(0).toUpperCase();
      this.closeModal();
    } else {
      userInfoEl.style.display = 'none';
      this.openModal();
    }
  },
};

// Explicitly attach to window
window.Auth = Auth;
