/**
 * Main Application Orchestrator & View Controller
 */
const App = {
  currentStep: 1,

  init() {
    console.log("Initializing Micro-Credential Curriculum Platform UI...");
    Auth.init();
    Profile.init();
    this.bindGlobalEvents();
  },

  bindGlobalEvents() {
    // Stepper click handlers
    document.querySelectorAll('.step-item').forEach((step) => {
      step.addEventListener('click', (e) => {
        const stepNum = parseInt(e.currentTarget.dataset.step);
        this.goToStep(stepNum);
      });
    });

    // Sidebar navigation click handlers
    document.querySelectorAll('.sidebar-nav-item').forEach((item) => {
      item.addEventListener('click', (e) => {
        e.preventDefault();
        const stepNum = parseInt(e.currentTarget.dataset.step);
        if (!isNaN(stepNum)) {
          this.goToStep(stepNum);
          this.closeMobileSidebar();
        }
      });
    });

    // Mobile sidebar toggle button
    const toggleBtn = document.getElementById('btn-sidebar-toggle');
    if (toggleBtn) {
      toggleBtn.addEventListener('click', () => {
        this.toggleSidebar();
      });
    }

    // Sidebar backdrop overlay click to close drawer
    const backdrop = document.getElementById('sidebar-backdrop');
    if (backdrop) {
      backdrop.addEventListener('click', () => {
        this.closeMobileSidebar();
      });
    }

    // Close assessment rules modal
    const closeRulesBtn = document.getElementById('btn-close-rules');
    if (closeRulesBtn) {
      closeRulesBtn.addEventListener('click', () => {
        this.closeAssessmentRulesModal();
      });
    }

    // Launch assessment button inside modal
    const launchAssessmentBtn = document.getElementById('btn-launch-test');
    if (launchAssessmentBtn) {
      launchAssessmentBtn.addEventListener('click', () => {
        this.closeAssessmentRulesModal();
        this.startAssessmentFlow();
      });
    }
  },

  toggleSidebar() {
    const sidebar = document.getElementById('app-sidebar');
    const backdrop = document.getElementById('sidebar-backdrop');
    if (sidebar && backdrop) {
      const isOpen = sidebar.classList.toggle('open');
      backdrop.classList.toggle('show', isOpen);
    }
  },

  closeMobileSidebar() {
    const sidebar = document.getElementById('app-sidebar');
    const backdrop = document.getElementById('sidebar-backdrop');
    if (sidebar) sidebar.classList.remove('open');
    if (backdrop) backdrop.classList.remove('show');
  },

  goToStep(stepNum) {
    this.currentStep = stepNum;

    // Update Stepper UI
    document.querySelectorAll('.step-item').forEach((item) => {
      const s = parseInt(item.dataset.step);
      if (s === stepNum) {
        item.classList.add('active');
      } else {
        item.classList.remove('active');
      }
    });

    // Update Sidebar Navigation UI
    document.querySelectorAll('.sidebar-nav-item').forEach((item) => {
      const s = parseInt(item.dataset.step);
      if (s === stepNum) {
        item.classList.add('active');
      } else {
        item.classList.remove('active');
      }
    });

    // Automatically close mobile sidebar when navigating
    this.closeMobileSidebar();

    // Update View Containers
    document.querySelectorAll('.app-view').forEach((view) => {
      const v = parseInt(view.dataset.view);
      if (v === stepNum) {
        view.style.display = 'block';
      } else {
        view.style.display = 'none';
      }
    });

    // When navigating to Step 2 (Assessment), automatically load questions if not loaded
    if (stepNum === 2) {
      if (typeof Assessment !== 'undefined') {
        if (!Assessment.questions || Assessment.questions.length === 0) {
          const skill = Assessment.currentSkill || document.getElementById('select-assessment-skill')?.value || 'Python';
          Assessment.startSession(skill);
        } else {
          Assessment.renderCurrentQuestion();
          Assessment.renderQuestionMatrix();
        }
      }
    }

    // When navigating to Step 3 (Verified Skill Profile), load latest verified profile
    if (stepNum === 3) {
      if (typeof Assessment !== 'undefined' && typeof Assessment.loadVerifiedProfile === 'function') {
        Assessment.loadVerifiedProfile();
      }
    }

    // When navigating to Step 4 (Job Market Skill Demand Analyzer), load market demand dashboard
    if (stepNum === 4) {
      if (typeof MarketDemand !== 'undefined' && typeof MarketDemand.loadSkillDemand === 'function') {
        MarketDemand.loadSkillDemand();
      }
    }

    // When navigating to Step 5 (Skill Gap Analysis), load skill gap dashboard
    if (stepNum === 5) {
      if (typeof GapAnalysis !== 'undefined' && typeof GapAnalysis.loadGapAnalysis === 'function') {
        GapAnalysis.loadGapAnalysis();
      }
    }

    // When navigating to Step 6 (Micro-Credential Curriculum), load personalized curriculum
    if (stepNum === 6) {
      if (typeof Curriculum !== 'undefined' && typeof Curriculum.loadCurriculum === 'function') {
        Curriculum.loadCurriculum();
      }
    }

    // When navigating to Step 7 (My Micro-Credentials Dashboard), load digital credentials
    if (stepNum === 7) {
      if (typeof Credentials !== 'undefined' && typeof Credentials.loadCredentials === 'function') {
        Credentials.loadCredentials();
      }
    }

    // When navigating to Step 8 (Adaptive Learning Path & Reassessment), load adaptive dashboard
    if (stepNum === 8) {
      if (typeof Adaptive !== 'undefined' && typeof Adaptive.loadDashboard === 'function') {
        Adaptive.loadDashboard();
      }
    }

    // When navigating to Step 9 (Job Readiness Dashboard), load final career skill profile
    if (stepNum === 9) {
      if (typeof Readiness !== 'undefined' && typeof Readiness.loadDashboard === 'function') {
        Readiness.loadDashboard();
      }
    }

    window.scrollTo({ top: 0, behavior: 'smooth' });
  },

  markStepCompleted(stepNum) {
    const stepItem = document.querySelector(`.step-item[data-step="${stepNum}"]`);
    if (stepItem) {
      stepItem.classList.add('completed');
    }
  },

  openAssessmentRulesModal() {
    const modal = document.getElementById('assessment-rules-modal');
    if (modal) modal.classList.add('show');
  },

  closeAssessmentRulesModal() {
    const modal = document.getElementById('assessment-rules-modal');
    if (modal) modal.classList.remove('show');
  },

  startAssessmentFlow() {
    const selectedSkill = document.getElementById('select-assessment-skill')?.value || 'Python';
    this.showToast(`Initiating 90-Minute Assessment Engine for ${selectedSkill}...`, "success");
    // Switch to step 2 view
    this.goToStep(2);
    if (typeof Assessment !== 'undefined' && typeof Assessment.startSession === 'function') {
      Assessment.startSession(selectedSkill);
    }
  },

  showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;

    const icon = type === 'success' ? '✓' : type === 'error' ? '✕' : 'ℹ';
    toast.innerHTML = `<span><b>${icon}</b></span> <span>${message}</span>`;

    container.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(10px)';
      setTimeout(() => toast.remove(), 300);
    }, 3800);
  }
};

// Explicitly attach to window
window.App = App;

document.addEventListener('DOMContentLoaded', () => {
  App.init();
});
