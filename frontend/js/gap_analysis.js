/**
 * Module 5: Skill Gap Analysis
 * Compares strictly VERIFIED USER SKILLS (from Module 3) against
 * REQUIRED JOB-MARKET SKILLS (from Module 4).
 * Configurable 1–5 scale, gap categorization, multi-factor priority scoring,
 * visual progress bars, gap charts, and Module 6 navigation handoff.
 */
const GapAnalysis = {
  currentAnalysis: null,
  selectedRoleId: 'fullstack-dev',
  currentFilter: 'all',

  async init() {
    console.log("Initializing Skill Gap Analysis Engine...");
    await this.loadGapAnalysis();
  },

  async loadGapAnalysis(roleId = null) {
    const container = document.getElementById('gap-analysis-container');
    if (!container) return;

    if (roleId) {
      this.selectedRoleId = roleId;
    } else if (typeof Profile !== 'undefined' && Profile.selectedRoleId) {
      this.selectedRoleId = Profile.selectedRoleId;
    }

    container.innerHTML = `
      <div class="glass-card" style="text-align: center; padding: 4rem 2rem;">
        <div class="spinner" style="width: 44px; height: 44px; margin: 0 auto 1.25rem; border-width: 3px;"></div>
        <h3 style="color: #ffffff; margin-bottom: 0.5rem; font-family: var(--font-heading);">
          Computing Skill Gap Vectors...
        </h3>
        <p style="color: var(--text-muted); font-size: 0.92rem;">
          Cross-referencing verified assessment competencies with required job-market demand expectations.
        </p>
      </div>
    `;

    try {
      const data = await API.getGapAnalysis(this.selectedRoleId);
      if (data && data.success && data.gap_analysis) {
        this.currentAnalysis = data.gap_analysis;
        this.selectedRoleId = data.gap_analysis.target_role.role_id;
        this.renderDashboard(container, data.gap_analysis);
      } else {
        container.innerHTML = `
          <div class="glass-card" style="text-align: center; padding: 3rem 2rem;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">⚠️</div>
            <h3 style="color: #ffffff; margin-bottom: 0.5rem;">Skill Gap Analysis Unavailable</h3>
            <p style="color: var(--text-muted); margin-bottom: 1.5rem;">
              Please ensure your career profile is saved and at least one skill assessment has been completed.
            </p>
            <button class="btn btn-primary" onclick="App.goToStep(1)">Return to Career Profile ➔</button>
          </div>
        `;
      }
    } catch (err) {
      console.error("Error loading skill gap analysis:", err);
      container.innerHTML = `
        <div class="glass-card" style="text-align: center; padding: 3rem 2rem;">
          <div style="font-size: 3rem; margin-bottom: 1rem;">❌</div>
          <h3 style="color: #ef4444; margin-bottom: 0.5rem;">Error Computing Skill Gaps</h3>
          <p style="color: var(--text-muted); margin-bottom: 1.5rem;">${err.message || 'Unknown network error'}</p>
          <button class="btn btn-secondary" onclick="GapAnalysis.loadGapAnalysis()">Retry Analysis</button>
        </div>
      `;
    }
  },

  renderDashboard(container, analysis) {
    const role = analysis.target_role || {};
    const gaps = analysis.gaps || [];
    const matchPct = analysis.role_match_percentage || 0;
    const masteredCount = analysis.mastered_count || 0;
    const criticalCount = analysis.critical_gaps_count || 0;
    const highCount = analysis.high_gaps_count || 0;
    const mediumCount = analysis.medium_gaps_count || 0;

    // Filter gaps based on currentFilter
    const filteredGaps = gaps.filter(g => {
      if (this.currentFilter === 'gaps') return g.gap_num > 0;
      if (this.currentFilter === 'high') return g.priority === 'High' || g.priority === 'Critical';
      if (this.currentFilter === 'mastered') return g.gap_num === 0;
      return true;
    });

    container.innerHTML = `
      <!-- TOP BANNER & CONTEXT -->
      <div class="glass-card" style="background: linear-gradient(135deg, rgba(30, 41, 59, 0.75), rgba(15, 23, 42, 0.85));">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 1.5rem;">
          <div>
            <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.5rem;">
              <span class="badge badge-primary">Module 5: Skill Gap Engine</span>
              <span class="badge badge-success" style="background: rgba(16, 185, 129, 0.15); border-color: rgba(16, 185, 129, 0.3); color: #34d399;">
                ● Verified Assessment Driven
              </span>
            </div>
            <h2 style="font-family: var(--font-heading); font-size: 1.85rem; font-weight: 800; color: #ffffff;">
              SKILL GAP ANALYSIS
            </h2>
            <p style="color: var(--text-muted); max-width: 820px; margin-top: 0.35rem; font-size: 0.95rem;">
              Direct mathematical comparison between your <strong style="color: #38bdf8;">Verified User Skills</strong> (Module 3 proctored assessment)
              and the <strong style="color: #ffffff;">Required Job-Market Skills</strong> (Module 4 authentic demand) for
              <strong style="color: #ffffff;">${role.role_title || 'Target Role'}</strong>.
            </p>
            <div style="margin-top: 0.65rem; font-size: 0.8rem; color: var(--text-dim); display: flex; align-items: center; gap: 0.5rem;">
              <span>🔒 Strict Verification Rule:</span>
              <span style="color: #a5b4fc; font-weight: 500;">Self-declared skills without assessment verification are excluded from verified proficiency.</span>
            </div>
          </div>

          <div style="display: flex; gap: 0.75rem; flex-wrap: wrap;">
            <button class="btn btn-secondary" onclick="GapAnalysis.loadGapAnalysis()">
              🔄 Refresh Gaps
            </button>
            <button class="btn btn-primary" onclick="GapAnalysis.navigateToCurriculum()">
              Personalized Curriculum ➔
            </button>
          </div>
        </div>
      </div>

      <!-- ROLE SELECTOR BAR -->
      <div class="glass-card" style="padding: 1.25rem 1.75rem;">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;">
          <div style="display: flex; align-items: center; gap: 0.75rem; flex-wrap: wrap;">
            <span style="font-size: 0.85rem; font-weight: 700; color: #ffffff; text-transform: uppercase; letter-spacing: 0.05em;">
              Target Engineering Role:
            </span>
            <select id="gap-role-select" class="form-select" style="min-width: 240px; font-weight: 600;" onchange="GapAnalysis.changeRole(this.value)">
              <option value="fullstack-dev" ${this.selectedRoleId === 'fullstack-dev' ? 'selected' : ''}>Full Stack Developer</option>
              <option value="ai-ml-engineer" ${this.selectedRoleId === 'ai-ml-engineer' ? 'selected' : ''}>AI / ML Engineer</option>
              <option value="cloud-devops-eng" ${this.selectedRoleId === 'cloud-devops-eng' ? 'selected' : ''}>Cloud & DevOps Engineer</option>
              <option value="data-engineer" ${this.selectedRoleId === 'data-engineer' ? 'selected' : ''}>Data Engineer</option>
            </select>
          </div>

          <!-- FILTER BUTTONS -->
          <div style="display: flex; gap: 0.5rem; flex-wrap: wrap;">
            <button class="btn btn-sm ${this.currentFilter === 'all' ? 'btn-primary' : 'btn-secondary'}" onclick="GapAnalysis.setFilter('all')">
              All Skills (${gaps.length})
            </button>
            <button class="btn btn-sm ${this.currentFilter === 'gaps' ? 'btn-primary' : 'btn-secondary'}" onclick="GapAnalysis.setFilter('gaps')">
              Gaps Only (${gaps.filter(g => g.gap_num > 0).length})
            </button>
            <button class="btn btn-sm ${this.currentFilter === 'high' ? 'btn-primary' : 'btn-secondary'}" onclick="GapAnalysis.setFilter('high')">
              High Priority (${criticalCount + highCount})
            </button>
            <button class="btn btn-sm ${this.currentFilter === 'mastered' ? 'btn-primary' : 'btn-secondary'}" onclick="GapAnalysis.setFilter('mastered')">
              No Gap (${masteredCount})
            </button>
          </div>
        </div>
      </div>

      <!-- KEY METRICS 4-CARD ROW -->
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1.25rem; margin-bottom: 1.5rem;">
        <div class="glass-card" style="padding: 1.5rem;">
          <div style="font-size: 0.8rem; font-weight: 700; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em;">
            Role Match Readiness
          </div>
          <div style="font-size: 2.2rem; font-weight: 800; color: ${matchPct >= 70 ? '#10b981' : matchPct >= 40 ? '#f59e0b' : '#38bdf8'}; margin-top: 0.35rem; font-family: var(--font-heading);">
            ${matchPct}%
          </div>
          <div style="font-size: 0.8rem; color: var(--text-muted); margin-top: 0.25rem;">
            Weighted competency alignment
          </div>
        </div>

        <div class="glass-card" style="padding: 1.5rem;">
          <div style="font-size: 0.8rem; font-weight: 700; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em;">
            Critical & High Gaps
          </div>
          <div style="font-size: 2.2rem; font-weight: 800; color: #ef4444; margin-top: 0.35rem; font-family: var(--font-heading);">
            ${criticalCount + highCount}
          </div>
          <div style="font-size: 0.8rem; color: var(--text-muted); margin-top: 0.25rem;">
            Immediate curriculum focus
          </div>
        </div>

        <div class="glass-card" style="padding: 1.5rem;">
          <div style="font-size: 0.8rem; font-weight: 700; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em;">
            Medium Gaps
          </div>
          <div style="font-size: 2.2rem; font-weight: 800; color: #f59e0b; margin-top: 0.35rem; font-family: var(--font-heading);">
            ${mediumCount}
          </div>
          <div style="font-size: 0.8rem; color: var(--text-muted); margin-top: 0.25rem;">
            Moderate skill reinforcement
          </div>
        </div>

        <div class="glass-card" style="padding: 1.5rem;">
          <div style="font-size: 0.8rem; font-weight: 700; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em;">
            Proficiencies Met
          </div>
          <div style="font-size: 2.2rem; font-weight: 800; color: #10b981; margin-top: 0.35rem; font-family: var(--font-heading);">
            ${masteredCount}
          </div>
          <div style="font-size: 0.8rem; color: var(--text-muted); margin-top: 0.25rem;">
            No gap identified
          </div>
        </div>
      </div>

      <!-- MAIN CONTENT 2-COLUMN GRID -->
      <div style="display: grid; grid-template-columns: 1.6fr 1fr; gap: 1.5rem; align-items: start;">

        <!-- LEFT: COMPARISON TABLE WITH PROGRESS BARS -->
        <div class="glass-card">
          <div class="card-header" style="border-bottom: 1px solid var(--border-subtle); padding-bottom: 1rem; margin-bottom: 1.25rem;">
            <div>
              <h3 style="color: #ffffff; font-size: 1.25rem; font-family: var(--font-heading); display: flex; align-items: center; gap: 0.5rem;">
                <span>🎯</span> Verified Skills vs. Required Job-Market Skills
              </h3>
              <p style="color: var(--text-muted); font-size: 0.85rem; margin-top: 0.2rem;">
                Configurable scale: Beginner (1) ➔ Basic (2) ➔ Intermediate (3) ➔ Advanced (4) ➔ Expert (5).
              </p>
            </div>
            <span class="badge badge-primary">${filteredGaps.length} Competencies</span>
          </div>

          <!-- COMPARATIVE ITEMS LIST -->
          <div style="display: flex; flex-direction: column; gap: 1.25rem;">
            ${filteredGaps.map(g => {
              const gapClass = g.gap === 'No Gap'
                ? 'badge-success'
                : g.gap === 'Low Gap'
                  ? 'badge-primary'
                  : g.gap === 'Medium Gap'
                    ? 'badge-warning'
                    : 'badge-danger';

              const priorityColor = g.priority === 'Critical'
                ? '#ef4444'
                : g.priority === 'High'
                  ? '#f97316'
                  : g.priority === 'Medium'
                    ? '#6366f1'
                    : g.priority === 'Low'
                      ? '#38bdf8'
                      : '#64748b';

              const userPct = (g.verified_level_num / 5.0) * 100.0;
              const reqPct = (g.required_level_num / 5.0) * 100.0;

              return `
                <div style="padding: 1.15rem; background: rgba(15, 23, 42, 0.55); border-radius: var(--radius-md); border: 1px solid var(--border-subtle); display: flex; flex-direction: column; gap: 0.75rem;">
                  <!-- Row 1: Title, Category, Priority & Gap Badges -->
                  <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.5rem;">
                    <div>
                      <div style="display: flex; align-items: center; gap: 0.5rem;">
                        <span style="font-weight: 700; color: #ffffff; font-size: 1.05rem;">${g.skill_name}</span>
                        <span style="font-size: 0.72rem; padding: 0.15rem 0.45rem; border-radius: 4px; background: rgba(99, 102, 241, 0.15); color: #a5b4fc; font-weight: 500;">
                          ${g.category}
                        </span>
                        ${!g.is_verified ? `
                          <span style="font-size: 0.72rem; padding: 0.15rem 0.45rem; border-radius: 4px; background: rgba(245, 158, 11, 0.15); color: #fbbf24; font-weight: 600;">
                            ⚠️ Not Verified
                          </span>
                        ` : ''}
                      </div>
                    </div>

                    <div style="display: flex; align-items: center; gap: 0.65rem;">
                      <span class="badge ${gapClass}" style="font-size: 0.78rem; font-weight: 700;">
                        ${g.gap === 'No Gap' ? '✓ No Gap' : `${g.gap} (+${g.gap_num})`}
                      </span>
                      <div style="display: flex; align-items: center; gap: 0.35rem; padding: 0.25rem 0.65rem; border-radius: 999px; background: rgba(15, 23, 42, 0.8); border: 1px solid ${priorityColor}40;">
                        <span style="width: 8px; height: 8px; border-radius: 50%; background: ${priorityColor};"></span>
                        <span style="font-size: 0.75rem; font-weight: 700; color: ${priorityColor}; text-transform: uppercase;">
                          ${g.priority} Priority
                        </span>
                      </div>
                    </div>
                  </div>

                  <!-- Row 2: Dual Level Details & Progress Comparison -->
                  <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; font-size: 0.85rem; margin-top: 0.2rem;">
                    <!-- User Verified Level -->
                    <div>
                      <div style="display: flex; justify-content: space-between; margin-bottom: 0.25rem;">
                        <span style="color: var(--text-muted);">Verified Level:</span>
                        <span style="font-weight: 700; color: ${g.is_verified ? '#38bdf8' : '#94a3b8'};">
                          ${g.verified_level} (${g.verified_level_num}/5)
                        </span>
                      </div>
                      <div style="height: 8px; width: 100%; background: rgba(15, 23, 42, 0.9); border-radius: 999px; overflow: hidden; border: 1px solid rgba(255, 255, 255, 0.05);">
                        <div style="height: 100%; width: ${userPct}%; background: ${g.is_verified ? 'linear-gradient(90deg, #38bdf8, #6366f1)' : '#475569'}; border-radius: 999px; transition: width 0.6s ease;"></div>
                      </div>
                    </div>

                    <!-- Required Market Level -->
                    <div>
                      <div style="display: flex; justify-content: space-between; margin-bottom: 0.25rem;">
                        <span style="color: var(--text-muted);">Required Level:</span>
                        <span style="font-weight: 700; color: #ffffff;">
                          ${g.required_level} (${g.required_level_num}/5)
                        </span>
                      </div>
                      <div style="height: 8px; width: 100%; background: rgba(15, 23, 42, 0.9); border-radius: 999px; overflow: hidden; border: 1px solid rgba(255, 255, 255, 0.05);">
                        <div style="height: 100%; width: ${reqPct}%; background: linear-gradient(90deg, #10b981, #06b6d4); border-radius: 999px; transition: width 0.6s ease;"></div>
                      </div>
                    </div>
                  </div>

                  <!-- Row 3: Market Demand & Status Footer -->
                  <div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.78rem; color: var(--text-dim); border-top: 1px solid rgba(255, 255, 255, 0.04); padding-top: 0.5rem; margin-top: 0.2rem;">
                    <div style="display: flex; align-items: center; gap: 0.4rem;">
                      <span>📈 Job Demand:</span>
                      <span style="color: #34d399; font-weight: 600;">${g.job_demand_percentage}% of role postings</span>
                    </div>
                    <div>
                      <span>Status: </span>
                      <span style="color: ${g.gap_num === 0 ? '#10b981' : '#f59e0b'}; font-weight: 600;">${g.status}</span>
                    </div>
                  </div>
                </div>
              `;
            }).join('')}
          </div>
        </div>

        <!-- RIGHT: VISUAL GAP CHART & PRIORITY SUMMARY -->
        <div style="display: flex; flex-direction: column; gap: 1.5rem;">

          <!-- COMPARATIVE GAP CHART (SVG VISUALIZATION) -->
          <div class="glass-card">
            <h3 style="color: #ffffff; font-size: 1.15rem; font-family: var(--font-heading); margin-bottom: 0.35rem;">
              📊 Competency Gap Chart
            </h3>
            <p style="color: var(--text-muted); font-size: 0.82rem; margin-bottom: 1.25rem;">
              Visual level comparison (1 to 5 scale) between Required and Verified skills.
            </p>

            <div style="display: flex; flex-direction: column; gap: 1rem;">
              ${gaps.map(g => {
                const reqW = (g.required_level_num / 5.0) * 100.0;
                const verW = (g.verified_level_num / 5.0) * 100.0;

                return `
                  <div>
                    <div style="display: flex; justify-content: space-between; font-size: 0.82rem; margin-bottom: 0.25rem;">
                      <span style="color: #ffffff; font-weight: 600;">${g.skill_name}</span>
                      <span style="color: var(--text-muted); font-size: 0.75rem;">
                        User: <strong style="color: #38bdf8;">${g.verified_level_num}</strong> / Req: <strong style="color: #10b981;">${g.required_level_num}</strong>
                      </span>
                    </div>
                    <div style="position: relative; height: 12px; width: 100%; background: rgba(15, 23, 42, 0.8); border-radius: 6px; overflow: hidden; border: 1px solid rgba(255, 255, 255, 0.05);">
                      <!-- Required Bar (Behind) -->
                      <div style="position: absolute; top: 0; left: 0; height: 100%; width: ${reqW}%; background: rgba(16, 185, 129, 0.4); border-radius: 6px;"></div>
                      <!-- Verified Bar (Front) -->
                      <div style="position: absolute; top: 0; left: 0; height: 100%; width: ${verW}%; background: #38bdf8; border-radius: 6px; transition: width 0.5s ease;"></div>
                    </div>
                  </div>
                `;
              }).join('')}
            </div>

            <!-- Legend -->
            <div style="display: flex; justify-content: center; gap: 1.5rem; margin-top: 1.25rem; font-size: 0.78rem; border-top: 1px solid var(--border-subtle); padding-top: 0.75rem;">
              <div style="display: flex; align-items: center; gap: 0.4rem;">
                <span style="width: 12px; height: 8px; background: #38bdf8; border-radius: 2px;"></span>
                <span style="color: var(--text-muted);">Verified User Level</span>
              </div>
              <div style="display: flex; align-items: center; gap: 0.4rem;">
                <span style="width: 12px; height: 8px; background: rgba(16, 185, 129, 0.4); border-radius: 2px;"></span>
                <span style="color: var(--text-muted);">Required Market Level</span>
              </div>
            </div>
          </div>

          <!-- LEARNING PRIORITY SUMMARY -->
          <div class="glass-card">
            <h3 style="color: #ffffff; font-size: 1.15rem; font-family: var(--font-heading); margin-bottom: 0.35rem;">
              ⚡ Priority Learning Sequence
            </h3>
            <p style="color: var(--text-muted); font-size: 0.82rem; margin-bottom: 1rem;">
              Ranked by gap magnitude, job-market demand, and prerequisite dependencies.
            </p>

            <div style="display: flex; flex-direction: column; gap: 0.75rem;">
              ${gaps.filter(g => g.gap_num > 0).slice(0, 5).map((g, idx) => `
                <div style="display: flex; align-items: center; justify-content: space-between; padding: 0.65rem 0.85rem; background: rgba(15, 23, 42, 0.5); border-radius: 8px; border: 1px solid var(--border-subtle);">
                  <div style="display: flex; align-items: center; gap: 0.65rem;">
                    <span style="font-weight: 800; font-size: 0.85rem; color: var(--text-dim);">#${idx + 1}</span>
                    <div>
                      <div style="font-weight: 600; font-size: 0.9rem; color: #ffffff;">${g.skill_name}</div>
                      <div style="font-size: 0.75rem; color: var(--text-dim);">${g.gap} (+${g.gap_num}) • ${g.job_demand_percentage}% Demand</div>
                    </div>
                  </div>
                  <span class="badge ${g.priority_badge_class}" style="font-size: 0.72rem;">
                    ${g.priority}
                  </span>
                </div>
              `).join('')}
            </div>
          </div>

        </div>

      </div>

      <!-- BOTTOM CALL TO ACTION: NAVIGATE TO MODULE 6 -->
      <div class="glass-card" style="margin-top: 1.5rem; background: linear-gradient(135deg, rgba(30, 41, 59, 0.85), rgba(15, 23, 42, 0.95)); border: 1px solid rgba(99, 102, 241, 0.3); padding: 2rem;">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1.5rem;">
          <div>
            <span class="badge badge-primary" style="margin-bottom: 0.5rem;">Next: Module 6</span>
            <h3 style="color: #ffffff; font-family: var(--font-heading); font-size: 1.45rem; margin-bottom: 0.35rem;">
              Ready to Bridge Your Skill Gaps?
            </h3>
            <p style="color: var(--text-muted); max-width: 650px; font-size: 0.92rem;">
              Transform these identified gap vectors into stackable, micro-credential learning units tailored to your pace.
            </p>
          </div>

          <div style="display: flex; gap: 0.75rem; flex-wrap: wrap;">
            <button class="btn btn-secondary" onclick="App.goToStep(2)">
              ✍ Take Another Skill Assessment
            </button>
            <button class="btn btn-primary btn-lg" id="btn-generate-curriculum" onclick="GapAnalysis.navigateToCurriculum()" style="font-weight: 700; padding: 0.85rem 1.75rem;">
              GENERATE MY PERSONALIZED CURRICULUM ➔
            </button>
          </div>
        </div>
      </div>
    `;
  },

  changeRole(roleId) {
    this.selectedRoleId = roleId;
    this.loadGapAnalysis(roleId);
  },

  setFilter(filterName) {
    this.currentFilter = filterName;
    if (this.currentAnalysis) {
      const container = document.getElementById('gap-analysis-container');
      if (container) this.renderDashboard(container, this.currentAnalysis);
    }
  },

  navigateToCurriculum() {
    App.showToast("Navigating to Module 6: Micro-Credential Curriculum Generation...", "info");
    // Explicit requirement: Navigate to Module 6 without generating curriculum yet
    App.goToStep(6);
  }
};

// Explicitly attach to window
window.GapAnalysis = GapAnalysis;
