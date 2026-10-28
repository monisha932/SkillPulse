/**
 * Assessment Integrity & Anti-Cheating Monitor (Workflow Step 7)
 */
const IntegrityMonitor = {
  isActive: false,
  tabSwitches: 0,
  blurs: 0,
  copyAttempts: 0,
  sessionToken: null,

  start(sessionToken) {
    this.sessionToken = sessionToken;
    this.isActive = true;
    this.tabSwitches = 0;
    this.blurs = 0;
    this.copyAttempts = 0;
    console.log("🛡️ Assessment Integrity Monitor Activated.");

    this.bindIntegrityControls();
    this.updateDisplay(100.0, 0);
  },

  stop() {
    this.isActive = false;
    this.unbindIntegrityControls();
    console.log("🛡️ Assessment Integrity Monitor Deactivated.");
  },

  bindIntegrityControls() {
    // 1. Prevent Copy, Cut, and Paste
    this.onCopyPaste = (e) => {
      if (!this.isActive) return;
      // Allow copy/paste only inside code editor textarea for ergonomics if user wants
      if (e.target && e.target.classList.contains('code-editor-textarea')) {
        return;
      }
      e.preventDefault();
      this.copyAttempts++;
      App.showToast("⚠️ Integrity Alert: Copy & Paste is disabled during assessment.", "warning");
      this.reportInfraction("copy_attempt", "Attempted clipboard interaction on test content");
    };
    document.addEventListener('copy', this.onCopyPaste);
    document.addEventListener('cut', this.onCopyPaste);
    document.addEventListener('paste', this.onCopyPaste);

    // 2. Prevent Right-Click Context Menu & Text Selection
    this.onContextMenu = (e) => {
      if (!this.isActive) return;
      e.preventDefault();
      App.showToast("⚠️ Integrity Alert: Right-click context menu is restricted.", "warning");
      this.reportInfraction("context_menu", "Attempted right-click during assessment");
    };
    document.addEventListener('contextmenu', this.onContextMenu);

    this.onSelectStart = (e) => {
      if (!this.isActive) return;
      if (e.target && e.target.classList.contains('code-editor-textarea')) return;
      e.preventDefault();
    };
    document.addEventListener('selectstart', this.onSelectStart);

    // 3. Detect Tab Switching / Page Visibility Change
    this.onVisibilityChange = () => {
      if (!this.isActive) return;
      if (document.hidden) {
        this.tabSwitches++;
        App.showToast(`🚨 Warning: Tab switch detected! Infraction #${this.tabSwitches} logged.`, "error");
        this.reportInfraction("tab_switch", `Tab visibility lost at ${new Date().toLocaleTimeString()}`);

        if (this.tabSwitches >= 5) {
          alert("🚨 CRITICAL WARNING: You have exceeded the maximum allowed tab switches (5). Your assessment has been flagged for supervisor review.");
        }
      }
    };
    document.addEventListener('visibilitychange', this.onVisibilityChange);

    // 4. Detect Window Blur (Focus loss outside browser)
    this.onBlur = () => {
      if (!this.isActive) return;
      this.blurs++;
      this.reportInfraction("window_blur", "Window lost focus");
    };
    window.addEventListener('blur', this.onBlur);

    // 5. Restrict Developer Tools Shortcuts
    this.onKeyDown = (e) => {
      if (!this.isActive) return;
      // F12 or Ctrl+Shift+I / Ctrl+Shift+J / Ctrl+U
      if (
        e.key === 'F12' ||
        (e.ctrlKey && e.shiftKey && (e.key === 'I' || e.key === 'i' || e.key === 'J' || e.key === 'j')) ||
        (e.ctrlKey && (e.key === 'U' || e.key === 'u'))
      ) {
        e.preventDefault();
        App.showToast("⚠️ Integrity Alert: Developer shortcuts are restricted during testing.", "warning");
        this.reportInfraction("context_menu", `Blocked shortcut: ${e.key}`);
      }
    };
    document.addEventListener('keydown', this.onKeyDown);
  },

  unbindIntegrityControls() {
    if (this.onCopyPaste) {
      document.removeEventListener('copy', this.onCopyPaste);
      document.removeEventListener('cut', this.onCopyPaste);
      document.removeEventListener('paste', this.onCopyPaste);
    }
    if (this.onContextMenu) document.removeEventListener('contextmenu', this.onContextMenu);
    if (this.onSelectStart) document.removeEventListener('selectstart', this.onSelectStart);
    if (this.onVisibilityChange) document.removeEventListener('visibilitychange', this.onVisibilityChange);
    if (this.onBlur) window.removeEventListener('blur', this.onBlur);
    if (this.onKeyDown) document.removeEventListener('keydown', this.onKeyDown);
  },

  async reportInfraction(type, details) {
    if (!this.sessionToken) return;

    try {
      const res = await API.request('/api/assessment/violation', {
        method: 'POST',
        body: JSON.stringify({
          session_token: this.sessionToken,
          violation_type: type,
          details: details
        })
      });
      this.updateDisplay(res.integrity_score, res.tab_switch_count);
    } catch (err) {
      console.warn("Could not log violation:", err);
    }
  },

  updateDisplay(integrityScore, tabSwitchCount) {
    const scoreEl = document.getElementById('integrity-score-display');
    const badgeEl = document.getElementById('integrity-badge');
    const tabCountEl = document.getElementById('tab-switch-counter');

    if (scoreEl) scoreEl.textContent = `${Math.round(integrityScore)}%`;
    if (tabCountEl) tabCountEl.textContent = `${tabSwitchCount}/5`;

    if (badgeEl) {
      if (tabSwitchCount === 0) {
        badgeEl.className = 'integrity-indicator clean';
        badgeEl.innerHTML = `<span>🛡️</span> <span>Integrity: Clean (100%)</span>`;
      } else if (tabSwitchCount < 5) {
        badgeEl.className = 'integrity-indicator';
        badgeEl.innerHTML = `<span>⚠️</span> <span>Tab Switches: ${tabSwitchCount}/5</span>`;
      } else {
        badgeEl.className = 'integrity-indicator';
        badgeEl.style.background = 'rgba(239, 68, 68, 0.3)';
        badgeEl.innerHTML = `<span>🚨</span> <span>FLAGGED (${tabSwitchCount} switches)</span>`;
      }
    }
  }
};

// Explicitly attach to window
window.IntegrityMonitor = IntegrityMonitor;
