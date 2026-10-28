/**
 * MODULE 8: ADAPTIVE LEARNING PATH & REASSESSMENT DASHBOARD CONTROLLER
 * Handles:
 * 1. Dynamic learning path roadmap recalculation
 * 2. Before vs After reassessment comparisons (e.g. Python 45% -> 78%, SQL 60% -> 85%)
 * 3. Pruning unnecessary beginner modules upon verified proficiency
 * 4. Adding newly detected job-market skills
 * 5. Explanatory change logs ('Why your curriculum changed')
 * 6. Prominent 'YOUR LEARNING PATH HAS BEEN UPDATED' banner
 * 7. Interactive retake triggers and simulations
 */

const Adaptive = {
  activePath: null,
  historyData: null,
  isLoading: false,

  init() {
    console.log("Module 8 Adaptive Learning Path Controller initialized.");
  },

  async loadDashboard() {
    const container = document.getElementById('adaptive-container');
    if (!container) return;

    this.isLoading = true;
    container.innerHTML = `
      <div class="glass-card" style="text-align: center; padding: 4rem 2rem;">
        <div class="spinner" style="width: 44px; height: 44px; margin: 0 auto 1.25rem; border-width: 3px;"></div>
        <h3 style="color: #ffffff; margin-bottom: 0.5rem; font-family: var(--font-heading);">
          Recalibrating Adaptive Learning Path...
        </h3>
        <p style="color: var(--text-muted); font-size: 0.92rem;">
          Evaluating latest assessment milestones, unblocking prerequisites, and filtering redundant modules.
        </p>
      </div>
    `;

    try {
      const [pathRes, histRes] = await Promise.all([
        API.getAdaptiveLearningPath(),
        API.getAssessmentHistory()
      ]);

      this.activePath = pathRes.adaptive_path;
      this.historyData = histRes.comparisons || [];
      this.renderDashboard();
    } catch (err) {
      console.error("Error loading adaptive dashboard:", err);
      container.innerHTML = `
        <div class="glass-card" style="text-align: center; padding: 3rem;">
          <p style="color: #ef4444; font-size: 1.1rem; margin-bottom: 1rem;">
            Failed to load adaptive learning path: ${err.message || 'Unknown error'}
          </p>
          <button class="btn btn-primary" onclick="Adaptive.loadDashboard()">Try Again</button>
        </div>
      `;
    } finally {
      this.isLoading = false;
    }
  },

  renderDashboard() {
    const container = document.getElementById('adaptive-container');
    if (!container || !this.activePath) return;

    const path = this.activePath;
    const comparisons = this.historyData || [];
    const explanations = path.explanations || [];
    const pruned = path.pruned_modules || [];
    const added = path.added_modules || [];
    const completed = path.completed_skills || [];
    const recommended = path.recommended_next_skills || [];
    const modules = path.modules || [];

    const now = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });

    container.innerHTML = `
      <!-- TOP HERO NOTIFICATION BANNER -->
      <div class="adaptive-hero-banner">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 1rem;">
          <div>
            <div class="adaptive-pulse-badge">
              <span class="adaptive-pulse-dot"></span>
              <span>Dynamic Engine Active • Pathway Version ${path.adaptation_version || 1}</span>
            </div>
            <h2 class="adaptive-headline">
              ${path.banner_message || 'YOUR LEARNING PATH HAS BEEN UPDATED'}
            </h2>
            <p style="color: #e2e8f0; font-size: 0.95rem; max-width: 820px; margin-top: 0.35rem; line-height: 1.5;">
              Target Role: <strong style="color: #38bdf8;">${path.target_role_title || 'Full-Stack Developer'}</strong>.
              Your customized curriculum has dynamically adapted to reflect latest verified assessment proficiencies,
              completed learning modules, and real-time job market skill demands.
            </p>
          </div>
          <div style="text-align: right;">
            <span class="badge badge-primary" style="font-size: 0.82rem; padding: 0.4rem 0.8rem;">
              Updated at ${now}
            </span>
          </div>
        </div>
      </div>

      <!-- INTERACTIVE SIMULATION & REASSESSMENT TOOLBAR -->
      <div class="simulation-bar">
        <span class="simulation-bar-title">
          <span>⚡</span>
          <span>Simulation & Reassessment Triggers:</span>
        </span>
        <button type="button" class="btn btn-secondary btn-sm" onclick="Adaptive.triggerRecalculate()">
          🔄 Recalculate Path
        </button>
        <button type="button" class="btn btn-primary btn-sm" onclick="Adaptive.simulateReassessment('Python', 78.0, 'Advanced')">
          📈 Retake Python (Simulate 45% ➔ 78%)
        </button>
        <button type="button" class="btn btn-primary btn-sm" onclick="Adaptive.simulateReassessment('SQL', 85.0, 'Advanced')">
          📈 Retake SQL (Simulate 60% ➔ 85%)
        </button>
        <button type="button" class="btn btn-secondary btn-sm" onclick="Adaptive.simulateMarketShift('fullstack-dev', 'Docker', 88.0)">
          🌐 Simulate Market Shift (+88% Docker Demand)
        </button>
        <button type="button" class="btn btn-secondary btn-sm" onclick="App.goToStep(2)" style="margin-left: auto;">
          📝 Launch Timed Test ➔
        </button>
      </div>

      <!-- 2-COLUMN SECTION: WHY PATH CHANGED + RECOMMENDED NEXT SKILLS -->
      <div style="display: grid; grid-template-columns: 1.25fr 1fr; gap: 1.5rem; margin-bottom: 2rem;">
        
        <!-- WHY THE CURRICULUM CHANGED (EXPLANATION LOG) -->
        <div class="glass-card" style="margin-bottom: 0;">
          <div class="card-header" style="margin-bottom: 0.75rem;">
            <div>
              <h3 style="font-family: var(--font-heading); font-size: 1.15rem; color: #ffffff;">
                🔍 Why Your Learning Path Changed
              </h3>
              <p style="font-size: 0.85rem; color: var(--text-muted);">
                Algorithmic adjustments based on demonstrated competencies and market vectors
              </p>
            </div>
            <span class="badge badge-primary">${explanations.length} Factor${explanations.length > 1 ? 's' : ''}</span>
          </div>

          <ul class="explanation-list">
            ${explanations.map(exp => `
              <li class="explanation-list-item">
                <span class="icon">✨</span>
                <span>${exp}</span>
              </li>
            `).join('')}
          </ul>

          <!-- TAGS FOR PRUNED & ADDED MODULES -->
          <div style="margin-top: 1.25rem; padding-top: 1rem; border-top: 1px solid rgba(255, 255, 255, 0.06); display: flex; flex-direction: column; gap: 0.65rem;">
            ${pruned.length > 0 ? `
              <div>
                <span style="font-size: 0.78rem; text-transform: uppercase; color: var(--text-dim); font-weight: 700; margin-right: 0.5rem;">
                  Pruned Beginner Modules:
                </span>
                <div style="display: flex; flex-wrap: wrap; gap: 0.4rem; margin-top: 0.35rem;">
                  ${pruned.map(p => `
                    <span class="pruned-badge" title="${p.reason}">
                      ✕ ${p.module_title} (${p.skill_name})
                    </span>
                  `).join('')}
                </div>
              </div>
            ` : ''}

            ${added.length > 0 ? `
              <div>
                <span style="font-size: 0.78rem; text-transform: uppercase; color: var(--text-dim); font-weight: 700; margin-right: 0.5rem;">
                  Newly Added Market Skills:
                </span>
                <div style="display: flex; flex-wrap: wrap; gap: 0.4rem; margin-top: 0.35rem;">
                  ${added.map(a => `
                    <span class="added-badge" title="${a.reason}">
                      ＋ ${a.skill_name} (+${a.demand_pct}% Demand)
                    </span>
                  `).join('')}
                </div>
              </div>
            ` : ''}
          </div>
        </div>

        <!-- RECOMMENDED NEXT SKILLS -->
        <div class="glass-card" style="margin-bottom: 0;">
          <div class="card-header" style="margin-bottom: 0.75rem;">
            <div>
              <h3 style="font-family: var(--font-heading); font-size: 1.15rem; color: #ffffff;">
                🎯 Immediate Next Skills to Focus On
              </h3>
              <p style="font-size: 0.85rem; color: var(--text-muted);">
                Unblocked high-priority modules that maximize your job readiness
              </p>
            </div>
            <span class="badge badge-success">Top Priority</span>
          </div>

          <div style="display: flex; flex-direction: column; gap: 0.85rem;">
            ${recommended.length > 0 ? recommended.map((rec, idx) => `
              <div style="background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255, 255, 255, 0.06); border-radius: var(--radius-md); padding: 0.85rem 1rem; display: flex; justify-content: space-between; align-items: center; gap: 1rem;">
                <div>
                  <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <span style="font-weight: 700; color: #38bdf8; font-size: 0.85rem;">#${idx + 1}</span>
                    <strong style="color: #ffffff; font-size: 0.95rem;">${rec.title}</strong>
                    <span class="badge ${rec.priority === 'Critical' ? 'badge-danger' : 'badge-primary'}" style="font-size: 0.72rem;">
                      ${rec.priority} Priority
                    </span>
                  </div>
                  <p style="font-size: 0.8rem; color: var(--text-muted); margin-top: 0.25rem;">
                    Est. Duration: ${rec.hours} Hours • ${rec.skill_name}
                  </p>
                </div>
                <button type="button" class="btn btn-secondary btn-sm" onclick="App.goToStep(6)">
                  Study ➔
                </button>
              </div>
            `).join('') : `
              <div style="text-align: center; padding: 2rem; color: var(--text-muted); font-size: 0.9rem;">
                All foundational skills verified! Ready to proceed to Capstone Integration Project.
              </div>
            `}
          </div>
        </div>

      </div>

      <!-- BEFORE VS AFTER REASSESSMENT COMPARISON SECTION -->
      <div class="glass-card">
        <div class="card-header">
          <div>
            <h3 style="font-family: var(--font-heading); font-size: 1.25rem; color: #ffffff;">
              📊 Reassessment: Before vs. After Performance Tracking
            </h3>
            <p style="font-size: 0.88rem; color: var(--text-muted);">
              Empirical progression comparing candidate baseline assessment with subsequent retakes. Past results are permanently preserved.
            </p>
          </div>
          <span class="badge badge-primary">${comparisons.length} Skill${comparisons.length > 1 ? 's' : ''} Assessed</span>
        </div>

        <div class="reassessment-grid">
          ${comparisons.map(item => this.renderComparisonCard(item)).join('')}
        </div>
      </div>

      <!-- ADAPTED LEARNING PATH ROADMAP -->
      <div class="glass-card">
        <div class="card-header">
          <div>
            <h3 style="font-family: var(--font-heading); font-size: 1.25rem; color: #ffffff;">
              🗺️ Adapted Learning Pathway Roadmap
            </h3>
            <p style="font-size: 0.88rem; color: var(--text-muted);">
              Sequence dynamically aligned with your verified competencies and verified prerequisite ordering
            </p>
          </div>
          <div style="display: flex; gap: 0.75rem; align-items: center;">
            <span class="badge badge-success">${path.completed_modules || 0} / ${path.total_modules || modules.length} Completed</span>
          </div>
        </div>

        <div style="display: flex; flex-direction: column; gap: 0.85rem; margin-top: 1rem;">
          ${modules.map((m, idx) => `
            <div style="background: rgba(15, 23, 42, 0.55); border: 1px solid ${m.status === 'completed' ? 'rgba(34, 197, 94, 0.3)' : 'rgba(255, 255, 255, 0.05)'}; border-left: 4px solid ${m.status === 'completed' ? '#22c55e' : (m.is_unlocked ? '#6366f1' : '#64748b')}; border-radius: var(--radius-md); padding: 1rem 1.25rem; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;">
              <div style="display: flex; align-items: center; gap: 1rem;">
                <div style="width: 32px; height: 32px; border-radius: 50%; background: ${m.status === 'completed' ? 'rgba(34, 197, 94, 0.2)' : 'rgba(99, 102, 241, 0.15)'}; color: ${m.status === 'completed' ? '#4ade80' : '#818cf8'}; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 0.9rem;">
                  ${m.status === 'completed' ? '✓' : idx + 1}
                </div>
                <div>
                  <div style="display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap;">
                    <strong style="color: #ffffff; font-size: 1rem;">${m.title}</strong>
                    <span class="badge ${m.priority === 'Critical' ? 'badge-danger' : 'badge-primary'}" style="font-size: 0.7rem;">
                      ${m.priority || 'Standard'}
                    </span>
                    <span class="badge ${m.status === 'completed' ? 'badge-success' : (m.is_unlocked ? 'badge-primary' : 'badge-secondary')}" style="font-size: 0.7rem;">
                      ${m.status === 'completed' ? 'Mastered / Met' : (m.is_unlocked ? 'Unlocked' : 'Locked')}
                    </span>
                  </div>
                  <p style="font-size: 0.84rem; color: var(--text-muted); margin-top: 0.25rem; max-width: 650px;">
                    ${m.learning_objective || 'Core engineering competency bridge.'}
                  </p>
                </div>
              </div>
              <div style="display: flex; align-items: center; gap: 1rem;">
                <div style="text-align: right;">
                  <span style="font-size: 0.82rem; color: var(--text-dim); font-weight: 600;">${m.hours} Hours</span>
                  <div style="font-size: 0.76rem; color: ${m.status === 'completed' ? '#4ade80' : 'var(--text-muted)'};">
                    ${m.status === 'completed' ? '100% Progress' : `${m.progress_pct || 0}% Progress`}
                  </div>
                </div>
                <button type="button" class="btn ${m.status === 'completed' ? 'btn-secondary' : 'btn-primary'} btn-sm" onclick="App.goToStep(6)">
                  ${m.status === 'completed' ? 'Review' : 'Open Module'}
                </button>
              </div>
            </div>
          `).join('')}
        </div>
      </div>
    `;
  },

  renderComparisonCard(item) {
    const isRetaken = item.has_reassessment;
    const diff = item.score_change || 0;
    const isPositive = diff > 0;

    return `
      <div class="reassessment-card">
        <div class="reassessment-header">
          <div>
            <span class="badge badge-primary" style="font-size: 0.72rem; margin-bottom: 0.25rem;">Skill Assessment</span>
            <h4 style="font-family: var(--font-heading); font-size: 1.15rem; color: #ffffff; margin: 0;">
              ${item.skill_name}
            </h4>
          </div>
          <div>
            ${isRetaken ? `
              <span class="delta-badge ${isPositive ? 'delta-positive' : 'delta-neutral'}">
                ${isPositive ? `▲ +${diff}%` : `${diff}%`}
              </span>
            ` : `
              <span class="badge badge-secondary" style="font-size: 0.72rem;">1 Attempt</span>
            `}
          </div>
        </div>

        <!-- DUAL BEFORE VS AFTER PROGRESS BAR MATRIX -->
        <div class="reassessment-comparison-bar">
          <div class="metric-column">
            <span class="metric-label">Before Assessment</span>
            <div class="metric-value" style="color: ${isRetaken ? '#94a3b8' : '#ffffff'};">
              ${isRetaken ? `${item.before_score}%` : `${item.after_score}%`}
            </div>
            <span class="metric-sub">
              ${isRetaken ? item.before_level : 'Baseline Verified'}
            </span>
          </div>

          <div class="metric-column" style="text-align: right; border-left: 1px solid rgba(255, 255, 255, 0.06); padding-left: 1rem;">
            <span class="metric-label">After Assessment</span>
            <div class="metric-value" style="color: #4ade80;">
              ${item.after_score}%
            </div>
            <span class="metric-sub" style="color: #4ade80;">
              ${item.after_level}
            </span>
          </div>
        </div>

        <!-- VISUAL COMPARISON TRACK -->
        ${isRetaken ? `
          <div style="margin-bottom: 1rem;">
            <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: var(--text-muted); margin-bottom: 0.25rem;">
              <span>Progression: ${item.before_score}% ➔ ${item.after_score}%</span>
              <span style="font-weight: 700; color: #34d399;">${item.before_level} ➔ ${item.after_level}</span>
            </div>
            <div class="module-progress-bar-container" style="height: 8px;">
              <div class="module-progress-bar-fill" style="width: ${Math.min(100, item.after_score)}%;"></div>
            </div>
          </div>
        ` : `
          <div style="margin-bottom: 1rem;">
            <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: var(--text-muted); margin-bottom: 0.25rem;">
              <span>Baseline Level: ${item.after_level}</span>
              <span>${item.after_score}%</span>
            </div>
            <div class="module-progress-bar-container" style="height: 8px;">
              <div class="module-progress-bar-fill" style="width: ${item.after_score}%;"></div>
            </div>
          </div>
        `}

        <div style="display: flex; justify-content: space-between; align-items: center; border-top: 1px solid rgba(255, 255, 255, 0.05); padding-top: 0.85rem; margin-top: 0.5rem;">
          <span style="font-size: 0.78rem; color: var(--text-dim);">
            ${item.total_attempts} attempts logged
          </span>
          <button type="button" class="btn btn-secondary btn-sm" onclick="Adaptive.launchSkillRetake('${item.skill_name}')">
            🔄 Retake Assessment
          </button>
        </div>
      </div>
    `;
  },

  async triggerRecalculate() {
    App.showToast("Recalculating adaptive pathway and updating skill priorities...", "info");
    try {
      const res = await API.triggerAdaptation({ trigger_reason: "manual_refresh" });
      this.activePath = res.adaptive_path;
      this.renderDashboard();
      App.showToast("YOUR LEARNING PATH HAS BEEN UPDATED", "success");
    } catch (err) {
      App.showToast(`Recalculation error: ${err.message}`, "error");
    }
  },

  async simulateReassessment(skillName, scorePct, level) {
    App.showToast(`Simulating reassessment for ${skillName} (${scorePct}%)...`, "info");
    try {
      const res = await API.simulateReassessment(skillName, scorePct, level);
      this.activePath = res.adaptive_path;
      // Refresh history comparisons
      const histRes = await API.getAssessmentHistory();
      this.historyData = histRes.comparisons || [];
      this.renderDashboard();
      App.showToast("YOUR LEARNING PATH HAS BEEN UPDATED", "success");
    } catch (err) {
      App.showToast(`Simulation error: ${err.message}`, "error");
    }
  },

  async simulateMarketShift(roleId, newSkill, demandPct) {
    App.showToast(`Simulating market demand surge for ${newSkill} (+${demandPct}%)...`, "info");
    try {
      const res = await API.simulateMarketShift(roleId, newSkill, demandPct);
      this.activePath = res.adaptive_path;
      this.renderDashboard();
      App.showToast("YOUR LEARNING PATH HAS BEEN UPDATED", "success");
    } catch (err) {
      App.showToast(`Market shift error: ${err.message}`, "error");
    }
  },

  launchSkillRetake(skillName) {
    App.showToast(`Preparing 90-Minute Reassessment for ${skillName}...`, "info");
    const skillSelect = document.getElementById('select-assessment-skill');
    if (skillSelect) {
      skillSelect.value = skillName;
    }
    // Launch assessment view
    App.goToStep(2);
    if (typeof Assessment !== 'undefined' && typeof Assessment.startSession === 'function') {
      Assessment.startSession(skillName);
    }
  }
};

// Attach to window
window.Adaptive = Adaptive;
