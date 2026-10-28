/**
 * Module 9: Job Readiness Dashboard & Career Skill Profile Controller
 * Displays the final executive Career Skill Profile combining all project modules:
 * - Title: "CAREER SKILL PROFILE"
 * - User Information (Name, Target Job Role, Preferred Domain, Career Goal)
 * - Verified Skills (Skill, Verified Proficiency, Assessment Score)
 * - Required Job Skills (Skill, Required Level, Job-Market Demand)
 * - Skill Gaps (Skill, Current Level, Required Level, Gap, Priority)
 * - Curriculum Progress (Completed Modules, Current Module, Remaining Modules, Overall Progress)
 * - Micro-Credentials (Earned Credentials, In-Progress Credentials)
 * - Job Readiness / Skill Coverage ("Overall Skill Coverage: XX%" + transparent calculation + non-employment disclaimer)
 * - 6 Visualizations (Radar chart, Proficiency bars, Gap chart, Curriculum progress, Credential progress, Market demand chart)
 * - Final Actionable Recommendations (Top gaps, Highest-priority skills, Next module, Assessment retake)
 */

const Readiness = {
  profileData: null,
  activeRole: null,

  async loadDashboard(roleId = null) {
    const container = document.getElementById('readiness-dashboard-container');
    if (!container) return;

    // Render loading state
    container.innerHTML = `
      <div class="glass-card" style="text-align: center; padding: 4rem 2rem;">
        <div class="spinner" style="width: 48px; height: 48px; margin: 0 auto 1.5rem; border-width: 3px; border-color: rgba(56, 189, 248, 0.2); border-top-color: #38bdf8;"></div>
        <h3 style="color: #ffffff; margin-bottom: 0.5rem; font-family: var(--font-heading); font-size: 1.4rem;">
          Synthesizing Final Career Skill Profile...
        </h3>
        <p style="color: var(--text-muted); font-size: 0.92rem; max-width: 600px; margin: 0 auto;">
          Aggregating verified assessments, job-market demand vectors, skill gaps, curriculum pathways, and micro-credential milestones.
        </p>
      </div>
    `;

    try {
      const activeRoleId = roleId || this.activeRole || (typeof Profile !== 'undefined' && Profile.currentRoleId) || 'fullstack-dev';
      this.activeRole = activeRoleId;

      const res = await API.getJobReadinessDashboard(activeRoleId);
      if (res && res.success && res.profile) {
        this.profileData = res.profile;
        this.renderDashboard(this.profileData);
      } else {
        container.innerHTML = `
          <div class="glass-card" style="text-align: center; padding: 3rem;">
            <div style="font-size: 2.5rem; margin-bottom: 1rem;">⚠️</div>
            <h3 style="color: #ffffff;">Unable to Load Career Skill Profile</h3>
            <p style="color: var(--text-muted); margin-top: 0.5rem;">${res?.detail || 'An unexpected error occurred while loading readiness analytics.'}</p>
            <button class="btn btn-primary" style="margin-top: 1.5rem;" onclick="Readiness.loadDashboard()">🔄 Retry Loading</button>
          </div>
        `;
      }
    } catch (err) {
      console.error("Failed to load Career Skill Profile:", err);
      container.innerHTML = `
        <div class="glass-card" style="text-align: center; padding: 3rem;">
          <div style="font-size: 2.5rem; margin-bottom: 1rem;">⚠️</div>
          <h3 style="color: #ffffff;">Connection Error</h3>
          <p style="color: var(--text-muted); margin-top: 0.5rem;">${err.message || 'Please check FastAPI engine connectivity.'}</p>
          <button class="btn btn-primary" style="margin-top: 1.5rem;" onclick="Readiness.loadDashboard()">🔄 Retry Loading</button>
        </div>
      `;
    }
  },

  async recalculate() {
    App.showToast("Recalculating Career Skill Profile & Job Readiness metrics...", "info");
    try {
      const res = await API.recalculateJobReadiness(this.activeRole);
      if (res && res.success && res.profile) {
        this.profileData = res.profile;
        this.renderDashboard(this.profileData);
        App.showToast("Job Readiness & Skill Coverage recalculated successfully!", "success");
      }
    } catch (err) {
      console.error("Failed to recalculate:", err);
      App.showToast("Recalculation failed: " + err.message, "error");
    }
  },

  renderDashboard(data) {
    const container = document.getElementById('readiness-dashboard-container');
    if (!container) return;

    const userInfo = data.user_information || {};
    const jr = data.job_readiness || {};
    const verSkills = data.verified_skills || [];
    const reqSkills = data.required_job_skills || [];
    const gaps = data.skill_gaps || [];
    const curr = data.curriculum_progress || {};
    const creds = data.micro_credentials || {};
    const vis = data.visualizations || {};
    const recs = data.final_recommendations || {};

    const coveragePct = jr.overall_skill_coverage !== undefined ? jr.overall_skill_coverage : 0.0;
    const coverageDisplay = jr.overall_skill_coverage_display || `Overall Skill Coverage: ${coveragePct}%`;
    const coverageBand = jr.coverage_band || 'Foundational Alignment';
    const coverageColor = jr.coverage_color || '#38bdf8';

    container.innerHTML = `
      <div class="readiness-dashboard-wrapper" style="display: flex; flex-direction: column; gap: 1.75rem;">

        <!-- 1. TOP HERO: TITLE, ROLE SELECTOR & ACTION BUTTONS -->
        <div class="glass-card" style="background: linear-gradient(135deg, rgba(15, 23, 42, 0.95), rgba(30, 41, 59, 0.85)); border-color: rgba(56, 189, 248, 0.25); position: relative; overflow: hidden;">
          <div style="position: absolute; top: -50px; right: -50px; width: 220px; height: 220px; background: radial-gradient(circle, rgba(56, 189, 248, 0.12), transparent 70%); pointer-events: none;"></div>

          <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1.25rem;">
            <div>
              <div style="display: flex; align-items: center; gap: 0.6rem; margin-bottom: 0.5rem;">
                <span class="badge badge-primary" style="font-size: 0.75rem; letter-spacing: 0.05em; text-transform: uppercase;">
                  Module 9: Executive Dashboard
                </span>
                <span class="badge" style="background: rgba(16, 185, 129, 0.15); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.3);">
                  Multi-Module Synthesis
                </span>
              </div>
              <h1 id="readiness-main-title" style="font-family: var(--font-heading); font-size: 2.2rem; font-weight: 900; color: #ffffff; letter-spacing: -0.02em; margin: 0;">
                ${data.title || "CAREER SKILL PROFILE"}
              </h1>
              <p style="color: var(--text-muted); font-size: 0.95rem; margin-top: 0.4rem; max-width: 820px;">
                Comprehensive job readiness audit benchmarked against real-time industry demands. Synthesizes verified technical assessments, competency gap analytics, customized curriculum progression, and digital micro-credentials.
              </p>
            </div>

            <div style="display: flex; align-items: center; gap: 0.75rem; flex-wrap: wrap;">
              <select id="readiness-role-selector" class="form-select" style="min-width: 220px; background: #0f172a; border-color: var(--border-subtle); color: #ffffff;" onchange="Readiness.loadDashboard(this.value)">
                <option value="fullstack-dev" ${this.activeRole === 'fullstack-dev' ? 'selected' : ''}>Full-Stack Web Developer</option>
                <option value="data-scientist" ${this.activeRole === 'data-scientist' ? 'selected' : ''}>Data Scientist & Analyst</option>
                <option value="cloud-devops" ${this.activeRole === 'cloud-devops' ? 'selected' : ''}>Cloud & DevOps Engineer</option>
              </select>

              <button class="btn btn-secondary btn-sm" onclick="Readiness.recalculate()" title="Force recalculation across all modules">
                🔄 Recalculate
              </button>

              <button class="btn btn-primary btn-sm" onclick="window.print()" title="Export or print career skill profile">
                🖨️ Export / Print
              </button>
            </div>
          </div>
        </div>

        <!-- 2. JOB READINESS / OVERALL SKILL COVERAGE HERO CARD -->
        <div class="glass-card" style="background: linear-gradient(135deg, rgba(30, 41, 59, 0.7), rgba(15, 23, 42, 0.85)); border-left: 5px solid ${coverageColor};">
          <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1.75rem; align-items: center;">

            <!-- Left: Large Score Callout -->
            <div>
              <span style="font-size: 0.82rem; font-weight: 700; color: var(--text-dim); text-transform: uppercase; letter-spacing: 0.08em; display: block; margin-bottom: 0.35rem;">
                Target Role Competency Alignment
              </span>
              <div id="coverage-score-text" style="font-family: var(--font-heading); font-size: 2.3rem; font-weight: 900; color: #ffffff; line-height: 1.15; margin-bottom: 0.5rem;">
                ${coverageDisplay}
              </div>
              <div style="display: flex; align-items: center; gap: 0.6rem; flex-wrap: wrap; margin-bottom: 0.75rem;">
                <span class="badge" style="background: ${coverageColor}22; color: ${coverageColor}; border: 1px solid ${coverageColor}66; font-size: 0.85rem; font-weight: 700; padding: 0.35rem 0.75rem;">
                  ${coverageBand}
                </span>
                <span style="color: var(--text-muted); font-size: 0.85rem;">
                  Target Role: <strong style="color: #ffffff;">${userInfo.target_job_role || 'Target Role'}</strong>
                </span>
              </div>
              <p style="color: var(--text-dim); font-size: 0.85rem; line-height: 1.45; margin: 0;">
                Transparent calculation: <em>[Sum of min(Verified Level, Required Level) &times; Weight] &divide; [Total Required Weight] &times; 100%</em>
              </p>
            </div>

            <!-- Middle: Quick Progress Rings / KPI Metric Boxes -->
            <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 0.85rem;">
              <div style="background: rgba(15, 23, 42, 0.6); padding: 0.9rem; border-radius: var(--radius-md); border: 1px solid rgba(255, 255, 255, 0.06); text-align: center;">
                <div style="font-size: 1.5rem; font-weight: 800; color: #10b981;">
                  ${jr.skills_fully_met_count || 0} / ${jr.total_skills_evaluated || 0}
                </div>
                <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 0.2rem;">Skills Fully Met</div>
              </div>

              <div style="background: rgba(15, 23, 42, 0.6); padding: 0.9rem; border-radius: var(--radius-md); border: 1px solid rgba(255, 255, 255, 0.06); text-align: center;">
                <div style="font-size: 1.5rem; font-weight: 800; color: #f59e0b;">
                  ${jr.skills_with_gaps_count || 0}
                </div>
                <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 0.2rem;">Remaining Gaps</div>
              </div>

              <div style="background: rgba(15, 23, 42, 0.6); padding: 0.9rem; border-radius: var(--radius-md); border: 1px solid rgba(255, 255, 255, 0.06); text-align: center;">
                <div style="font-size: 1.5rem; font-weight: 800; color: #38bdf8;">
                  ${curr.overall_progress || 0}%
                </div>
                <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 0.2rem;">Curriculum Done</div>
              </div>

              <div style="background: rgba(15, 23, 42, 0.6); padding: 0.9rem; border-radius: var(--radius-md); border: 1px solid rgba(255, 255, 255, 0.06); text-align: center;">
                <div style="font-size: 1.5rem; font-weight: 800; color: #a855f7;">
                  ${creds.earned_count || 0}
                </div>
                <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 0.2rem;">Credentials Earned</div>
              </div>
            </div>

            <!-- Right: Disclaimer Alert Box -->
            <div style="background: rgba(15, 23, 42, 0.8); border: 1px solid rgba(245, 158, 11, 0.25); border-radius: var(--radius-md); padding: 1rem;">
              <div style="display: flex; align-items: flex-start; gap: 0.65rem;">
                <span style="font-size: 1.25rem;">⚖️</span>
                <div>
                  <div style="font-size: 0.8rem; font-weight: 700; color: #fbbf24; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.25rem;">
                    Non-Employment Guarantee Notice
                  </div>
                  <p style="font-size: 0.78rem; color: var(--text-muted); line-height: 1.45; margin: 0;">
                    ${jr.disclaimer || "Disclaimer: This metric represents an objective technical skill coverage percentage benchmarked against verified competencies and current job-market requirements. It is a technical readiness index and does NOT represent or guarantee a probability, promise, or offer of employment or job placement."}
                  </p>
                </div>
              </div>
            </div>

          </div>
        </div>

        <!-- 3. USER INFORMATION CARD -->
        <div class="glass-card">
          <div class="card-header" style="border-bottom: 1px solid var(--border-subtle); padding-bottom: 0.85rem; margin-bottom: 1.25rem;">
            <div>
              <h2 style="font-family: var(--font-heading); font-size: 1.25rem; font-weight: 800; color: #ffffff; margin: 0;">
                👤 User Information & Career Profile
              </h2>
              <p style="font-size: 0.85rem; color: var(--text-muted); margin: 0.25rem 0 0 0;">
                Candidate career trajectory and benchmark parameters
              </p>
            </div>
            <span class="badge badge-primary">Module 1 Baseline</span>
          </div>

          <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1.25rem;">
            <div style="background: rgba(15, 23, 42, 0.5); padding: 1rem; border-radius: var(--radius-md); border: 1px solid rgba(255, 255, 255, 0.04);">
              <div style="font-size: 0.75rem; text-transform: uppercase; color: var(--text-dim); font-weight: 700; margin-bottom: 0.35rem;">
                Candidate Name
              </div>
              <div style="font-size: 1.05rem; font-weight: 700; color: #ffffff; display: flex; align-items: center; gap: 0.4rem;">
                <span>🎓</span> ${userInfo.name || "Student"}
              </div>
              <div style="font-size: 0.8rem; color: var(--text-muted); margin-top: 0.25rem;">${userInfo.email || "student@example.com"}</div>
            </div>

            <div style="background: rgba(15, 23, 42, 0.5); padding: 1rem; border-radius: var(--radius-md); border: 1px solid rgba(255, 255, 255, 0.04);">
              <div style="font-size: 0.75rem; text-transform: uppercase; color: var(--text-dim); font-weight: 700; margin-bottom: 0.35rem;">
                Target Job Role
              </div>
              <div style="font-size: 1.05rem; font-weight: 700; color: #38bdf8; display: flex; align-items: center; gap: 0.4rem;">
                <span>🎯</span> ${userInfo.target_job_role || "Full-Stack Web Developer"}
              </div>
              <div style="font-size: 0.8rem; color: var(--text-muted); margin-top: 0.25rem;">Level: ${userInfo.experience_level || "Entry-Level"}</div>
            </div>

            <div style="background: rgba(15, 23, 42, 0.5); padding: 1rem; border-radius: var(--radius-md); border: 1px solid rgba(255, 255, 255, 0.04);">
              <div style="font-size: 0.75rem; text-transform: uppercase; color: var(--text-dim); font-weight: 700; margin-bottom: 0.35rem;">
                Preferred Domain
              </div>
              <div style="font-size: 1.05rem; font-weight: 700; color: #10b981; display: flex; align-items: center; gap: 0.4rem;">
                <span>🌐</span> ${userInfo.preferred_domain || "Web & Software Engineering"}
              </div>
              <div style="font-size: 0.8rem; color: var(--text-muted); margin-top: 0.25rem;">Education: ${userInfo.education || "Undergraduate"}</div>
            </div>

            <div style="background: rgba(15, 23, 42, 0.5); padding: 1rem; border-radius: var(--radius-md); border: 1px solid rgba(255, 255, 255, 0.04); grid-column: 1 / -1;">
              <div style="font-size: 0.75rem; text-transform: uppercase; color: var(--text-dim); font-weight: 700; margin-bottom: 0.35rem;">
                Career Goal
              </div>
              <div style="font-size: 0.95rem; font-style: italic; color: #ffffff; display: flex; align-items: center; gap: 0.5rem;">
                <span>🚀</span> "${userInfo.career_goal || "Achieve industry-grade competence in target engineering domain."}"
              </div>
            </div>
          </div>
        </div>

        <!-- 4. SIX VISUALIZATIONS SECTION -->
        <div>
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
            <div>
              <h2 style="font-family: var(--font-heading); font-size: 1.35rem; font-weight: 800; color: #ffffff; margin: 0;">
                📊 Comprehensive Visual Analytics Suite
              </h2>
              <p style="font-size: 0.85rem; color: var(--text-muted); margin-top: 0.2rem;">
                6 interactive visual models analyzing proficiency, market vectors, curriculum progression, and credentials
              </p>
            </div>
            <span class="badge badge-primary">6 Core Visuals</span>
          </div>

          <!-- GRID FOR VISUALIZATIONS -->
          <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(360px, 1fr)); gap: 1.5rem;">

            <!-- VISUAL 1: SKILL RADAR CHART -->
            <div class="glass-card" style="display: flex; flex-direction: column;">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                <h3 style="font-family: var(--font-heading); font-size: 1.1rem; color: #ffffff; margin: 0;">
                  🕸️ 1. Skill Radar Chart
                </h3>
                <span class="badge badge-secondary" style="font-size: 0.7rem;">Verified vs Required</span>
              </div>
              <p style="font-size: 0.8rem; color: var(--text-muted); margin-bottom: 1rem;">
                Multi-axis polygonal alignment across target role skill competencies (1 to 5 scale).
              </p>
              <div id="radar-chart-container" style="display: flex; justify-content: center; align-items: center; flex: 1; min-height: 280px;">
                ${this.renderRadarSVG(vis.skill_radar_chart)}
              </div>
              <div style="display: flex; justify-content: center; gap: 1.5rem; font-size: 0.75rem; border-top: 1px solid var(--border-subtle); padding-top: 0.75rem; margin-top: 0.75rem;">
                <div style="display: flex; align-items: center; gap: 0.4rem;">
                  <span style="width: 12px; height: 12px; background: rgba(56, 189, 248, 0.8); border-radius: 50%;"></span>
                  <span style="color: #ffffff;">Verified User Proficiency</span>
                </div>
                <div style="display: flex; align-items: center; gap: 0.4rem;">
                  <span style="width: 12px; height: 12px; border: 2px dashed #10b981; border-radius: 50%;"></span>
                  <span style="color: #ffffff;">Job Market Requirement</span>
                </div>
              </div>
            </div>

            <!-- VISUAL 2: SKILL PROFICIENCY BARS -->
            <div class="glass-card" style="display: flex; flex-direction: column;">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                <h3 style="font-family: var(--font-heading); font-size: 1.1rem; color: #ffffff; margin: 0;">
                  📈 2. Skill Proficiency Bars
                </h3>
                <span class="badge badge-secondary" style="font-size: 0.7rem;">Verified Assessment Scores</span>
              </div>
              <p style="font-size: 0.8rem; color: var(--text-muted); margin-bottom: 1rem;">
                Proctored assessment scores & verified proficiency tiers from Modules 2 & 3.
              </p>
              <div style="display: flex; flex-direction: column; gap: 1rem; flex: 1;">
                ${vis.skill_proficiency_bars && vis.skill_proficiency_bars.length > 0 ? vis.skill_proficiency_bars.map(s => `
                  <div>
                    <div style="display: flex; justify-content: space-between; font-size: 0.82rem; margin-bottom: 0.3rem;">
                      <span style="font-weight: 700; color: #ffffff;">${s.skill}</span>
                      <span style="color: var(--text-muted);">
                        <strong style="color: #38bdf8;">${s.score_pct}%</strong> (${s.proficiency_level})
                      </span>
                    </div>
                    <div style="position: relative; height: 10px; width: 100%; background: rgba(15, 23, 42, 0.8); border-radius: 5px; overflow: hidden; border: 1px solid rgba(255, 255, 255, 0.05);">
                      <div style="position: absolute; top: 0; left: 0; height: 100%; width: ${s.score_pct}%; background: linear-gradient(90deg, #38bdf8, #818cf8); border-radius: 5px;"></div>
                    </div>
                  </div>
                `).join('') : `
                  <div style="text-align: center; color: var(--text-dim); padding: 2rem;">
                    No assessed skills verified yet. Complete Step 2 assessment to populate bars.
                  </div>
                `}
              </div>
              <div style="margin-top: 1rem; border-top: 1px solid var(--border-subtle); padding-top: 0.75rem; text-align: right;">
                <button class="btn btn-secondary btn-sm" onclick="App.goToStep(2)">🎯 Take / Retake Assessment</button>
              </div>
            </div>

            <!-- VISUAL 3: SKILL GAP CHART -->
            <div class="glass-card" style="display: flex; flex-direction: column;">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                <h3 style="font-family: var(--font-heading); font-size: 1.1rem; color: #ffffff; margin: 0;">
                  ⚡ 3. Skill Gap Comparative Chart
                </h3>
                <span class="badge badge-secondary" style="font-size: 0.7rem;">Level Disparity (1–5)</span>
              </div>
              <p style="font-size: 0.8rem; color: var(--text-muted); margin-bottom: 1rem;">
                Granular gap comparison between Verified User Level and Required Market Level.
              </p>
              <div style="display: flex; flex-direction: column; gap: 0.85rem; flex: 1;">
                ${vis.skill_gap_chart && vis.skill_gap_chart.length > 0 ? vis.skill_gap_chart.map(g => {
                  const reqPct = (g.required_level_num / 5.0) * 100.0;
                  const verPct = (g.verified_level_num / 5.0) * 100.0;
                  const isMet = g.gap_num === 0;
                  return `
                    <div>
                      <div style="display: flex; justify-content: space-between; font-size: 0.82rem; margin-bottom: 0.25rem;">
                        <span style="font-weight: 700; color: #ffffff;">${g.skill}</span>
                        <span style="font-size: 0.75rem;">
                          ${isMet ? `<span class="badge" style="background: rgba(16, 185, 129, 0.15); color: #10b981; font-size: 0.7rem;">✓ Met</span>` : `<span class="badge badge-warning" style="font-size: 0.7rem;">Gap: +${g.gap_num} Level</span>`}
                          <span style="color: var(--text-muted); margin-left: 0.4rem;">${g.verified_level_num} / ${g.required_level_num}</span>
                        </span>
                      </div>
                      <div style="position: relative; height: 10px; width: 100%; background: rgba(15, 23, 42, 0.8); border-radius: 5px; overflow: hidden; border: 1px solid rgba(255, 255, 255, 0.05);">
                        <div style="position: absolute; top: 0; left: 0; height: 100%; width: ${reqPct}%; background: rgba(16, 185, 129, 0.3); border-radius: 5px;"></div>
                        <div style="position: absolute; top: 0; left: 0; height: 100%; width: ${verPct}%; background: #38bdf8; border-radius: 5px;"></div>
                      </div>
                    </div>
                  `;
                }).join('') : `
                  <div style="text-align: center; color: var(--text-dim); padding: 2rem;">No gap metrics available.</div>
                `}
              </div>
            </div>

            <!-- VISUAL 4: CURRICULUM PROGRESS -->
            <div class="glass-card" style="display: flex; flex-direction: column;">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                <h3 style="font-family: var(--font-heading); font-size: 1.1rem; color: #ffffff; margin: 0;">
                  🎓 4. Curriculum Progress
                </h3>
                <span class="badge badge-secondary" style="font-size: 0.7rem;">Module 6 Roadmap</span>
              </div>
              <p style="font-size: 0.8rem; color: var(--text-muted); margin-bottom: 1rem;">
                Completed, in-progress, and remaining micro-credential curriculum modules.
              </p>
              <div style="display: flex; align-items: center; justify-content: space-around; flex: 1; padding: 1rem 0;">
                <div style="position: relative; width: 140px; height: 140px; display: flex; align-items: center; justify-content: center;">
                  <svg width="140" height="140" viewBox="0 0 140 140">
                    <circle cx="70" cy="70" r="54" stroke="rgba(255, 255, 255, 0.08)" stroke-width="12" fill="transparent"/>
                    <circle cx="70" cy="70" r="54" stroke="#10b981" stroke-width="12" fill="transparent"
                      stroke-dasharray="${2 * Math.PI * 54}"
                      stroke-dashoffset="${2 * Math.PI * 54 * (1 - (curr.overall_progress || 0) / 100.0)}"
                      stroke-linecap="round"
                      style="transform: rotate(-90deg); transform-origin: 50% 50%; transition: stroke-dashoffset 1s ease;"/>
                  </svg>
                  <div style="position: absolute; text-align: center;">
                    <div style="font-size: 1.5rem; font-weight: 800; color: #ffffff;">${curr.overall_progress || 0}%</div>
                    <div style="font-size: 0.65rem; color: var(--text-dim); text-transform: uppercase;">Finished</div>
                  </div>
                </div>

                <div style="display: flex; flex-direction: column; gap: 0.6rem; font-size: 0.82rem;">
                  <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <span style="width: 10px; height: 10px; background: #10b981; border-radius: 2px;"></span>
                    <span style="color: var(--text-muted);">Completed:</span>
                    <strong style="color: #ffffff;">${curr.completed_count || 0} Modules</strong>
                  </div>
                  <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <span style="width: 10px; height: 10px; background: #38bdf8; border-radius: 2px;"></span>
                    <span style="color: var(--text-muted);">In Progress:</span>
                    <strong style="color: #ffffff;">${curr.current_module ? '1 Module' : '0 Modules'}</strong>
                  </div>
                  <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <span style="width: 10px; height: 10px; background: #64748b; border-radius: 2px;"></span>
                    <span style="color: var(--text-muted);">Remaining:</span>
                    <strong style="color: #ffffff;">${curr.remaining_count || 0} Modules</strong>
                  </div>
                  <div style="margin-top: 0.4rem;">
                    <button class="btn btn-secondary btn-sm" onclick="App.goToStep(6)">Open Curriculum ➔</button>
                  </div>
                </div>
              </div>
            </div>

            <!-- VISUAL 5: CREDENTIAL PROGRESS -->
            <div class="glass-card" style="display: flex; flex-direction: column;">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                <h3 style="font-family: var(--font-heading); font-size: 1.1rem; color: #ffffff; margin: 0;">
                  🏅 5. Credential Progress
                </h3>
                <span class="badge badge-secondary" style="font-size: 0.7rem;">Module 7 Milestone</span>
              </div>
              <p style="font-size: 0.8rem; color: var(--text-muted); margin-bottom: 1rem;">
                Earned vs in-progress platform micro-credentials and digital badges.
              </p>
              <div style="display: flex; flex-direction: column; gap: 1rem; flex: 1;">
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem;">
                  <div style="background: rgba(15, 23, 42, 0.6); padding: 0.85rem; border-radius: var(--radius-md); border: 1px solid rgba(16, 185, 129, 0.2); text-align: center;">
                    <div style="font-size: 1.6rem; font-weight: 800; color: #10b981;">${creds.earned_count || 0}</div>
                    <div style="font-size: 0.75rem; color: var(--text-muted);">Earned Badges</div>
                  </div>
                  <div style="background: rgba(15, 23, 42, 0.6); padding: 0.85rem; border-radius: var(--radius-md); border: 1px solid rgba(56, 189, 248, 0.2); text-align: center;">
                    <div style="font-size: 1.6rem; font-weight: 800; color: #38bdf8;">${creds.in_progress_count || 0}</div>
                    <div style="font-size: 0.75rem; color: var(--text-muted);">In Progress</div>
                  </div>
                </div>

                <div style="display: flex; flex-direction: column; gap: 0.5rem;">
                  ${creds.earned_credentials && creds.earned_credentials.length > 0 ? creds.earned_credentials.map(c => `
                    <div style="display: flex; align-items: center; justify-content: space-between; background: rgba(16, 185, 129, 0.08); padding: 0.5rem 0.75rem; border-radius: var(--radius-sm); border: 1px solid rgba(16, 185, 129, 0.2);">
                      <div style="display: flex; align-items: center; gap: 0.5rem;">
                        <span>🎖️</span>
                        <div>
                          <div style="font-size: 0.8rem; font-weight: 700; color: #ffffff;">${c.skill}</div>
                          <div style="font-size: 0.7rem; color: #10b981;">Verified (${c.level})</div>
                        </div>
                      </div>
                      <span class="badge" style="background: rgba(16, 185, 129, 0.2); color: #10b981; font-size: 0.7rem;">Earned</span>
                    </div>
                  `).join('') : `
                    <div style="font-size: 0.8rem; color: var(--text-dim); text-align: center; padding: 0.5rem;">No credentials claimed yet.</div>
                  `}
                </div>
              </div>
              <div style="margin-top: 1rem; border-top: 1px solid var(--border-subtle); padding-top: 0.75rem; text-align: right;">
                <button class="btn btn-secondary btn-sm" onclick="App.goToStep(7)">My Credentials ➔</button>
              </div>
            </div>

            <!-- VISUAL 6: JOB-MARKET DEMAND CHART -->
            <div class="glass-card" style="display: flex; flex-direction: column;">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                <h3 style="font-family: var(--font-heading); font-size: 1.1rem; color: #ffffff; margin: 0;">
                  💼 6. Job-Market Demand Chart
                </h3>
                <span class="badge badge-secondary" style="font-size: 0.7rem;">Module 4 Demand Index</span>
              </div>
              <p style="font-size: 0.8rem; color: var(--text-muted); margin-bottom: 1rem;">
                Live frequency percentage weights extracted from analyzed postings.
              </p>
              <div style="display: flex; flex-direction: column; gap: 0.85rem; flex: 1;">
                ${vis.job_market_demand_chart && vis.job_market_demand_chart.length > 0 ? vis.job_market_demand_chart.map(m => `
                  <div>
                    <div style="display: flex; justify-content: space-between; font-size: 0.82rem; margin-bottom: 0.25rem;">
                      <span style="font-weight: 700; color: #ffffff;">${m.skill}</span>
                      <span style="font-size: 0.75rem; color: #38bdf8;">
                        <strong>${m.demand_percentage}%</strong> Demand
                        <span class="badge badge-primary" style="font-size: 0.65rem; margin-left: 0.3rem;">${m.trend_status || 'stable'}</span>
                      </span>
                    </div>
                    <div style="position: relative; height: 8px; width: 100%; background: rgba(15, 23, 42, 0.8); border-radius: 4px; overflow: hidden; border: 1px solid rgba(255, 255, 255, 0.05);">
                      <div style="position: absolute; top: 0; left: 0; height: 100%; width: ${m.demand_percentage}%; background: linear-gradient(90deg, #10b981, #059669); border-radius: 4px;"></div>
                    </div>
                  </div>
                `).join('') : `
                  <div style="text-align: center; color: var(--text-dim); padding: 2rem;">No market demand data available.</div>
                `}
              </div>
            </div>

          </div>
        </div>

        <!-- 5. DETAILED DATA TABLES (VERIFIED SKILLS, REQUIRED JOB SKILLS, SKILL GAPS) -->
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(420px, 1fr)); gap: 1.5rem;">

          <!-- SECTION: VERIFIED SKILLS TABLE -->
          <div class="glass-card">
            <div class="card-header" style="border-bottom: 1px solid var(--border-subtle); padding-bottom: 0.85rem; margin-bottom: 1rem;">
              <div>
                <h3 style="font-family: var(--font-heading); font-size: 1.15rem; color: #ffffff; margin: 0;">
                  🏅 Verified Skills
                </h3>
                <p style="font-size: 0.8rem; color: var(--text-muted); margin-top: 0.2rem;">
                  Technical assessments evaluated and verified by platform engine
                </p>
              </div>
              <span class="badge badge-primary">Module 3</span>
            </div>

            <div style="overflow-x: auto;">
              <table style="width: 100%; border-collapse: collapse; font-size: 0.85rem;">
                <thead>
                  <tr style="border-bottom: 1px solid var(--border-subtle); color: var(--text-dim); text-align: left;">
                    <th style="padding: 0.6rem 0.5rem;">Skill</th>
                    <th style="padding: 0.6rem 0.5rem;">Verified Proficiency</th>
                    <th style="padding: 0.6rem 0.5rem; text-align: right;">Assessment Score</th>
                  </tr>
                </thead>
                <tbody>
                  ${verSkills.length > 0 ? verSkills.map(v => `
                    <tr style="border-bottom: 1px solid rgba(255, 255, 255, 0.04);">
                      <td style="padding: 0.75rem 0.5rem; font-weight: 700; color: #ffffff;">${v.skill}</td>
                      <td style="padding: 0.75rem 0.5rem;">
                        <span class="badge" style="background: rgba(56, 189, 248, 0.15); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.3);">
                          ${v.verified_proficiency}
                        </span>
                      </td>
                      <td style="padding: 0.75rem 0.5rem; text-align: right; font-weight: 700; color: #10b981;">
                        ${v.assessment_score}%
                      </td>
                    </tr>
                  `).join('') : `
                    <tr>
                      <td colspan="3" style="text-align: center; color: var(--text-dim); padding: 1.5rem;">
                        No skills verified yet. Complete timed assessment in Step 2.
                      </td>
                    </tr>
                  `}
                </tbody>
              </table>
            </div>
          </div>

          <!-- SECTION: REQUIRED JOB SKILLS TABLE -->
          <div class="glass-card">
            <div class="card-header" style="border-bottom: 1px solid var(--border-subtle); padding-bottom: 0.85rem; margin-bottom: 1rem;">
              <div>
                <h3 style="font-family: var(--font-heading); font-size: 1.15rem; color: #ffffff; margin: 0;">
                  💼 Required Job Skills
                </h3>
                <p style="font-size: 0.8rem; color: var(--text-muted); margin-top: 0.2rem;">
                  Industry-defined skill competencies for ${userInfo.target_job_role || 'Target Role'}
                </p>
              </div>
              <span class="badge badge-primary">Module 4</span>
            </div>

            <div style="overflow-x: auto;">
              <table style="width: 100%; border-collapse: collapse; font-size: 0.85rem;">
                <thead>
                  <tr style="border-bottom: 1px solid var(--border-subtle); color: var(--text-dim); text-align: left;">
                    <th style="padding: 0.6rem 0.5rem;">Skill</th>
                    <th style="padding: 0.6rem 0.5rem;">Required Level</th>
                    <th style="padding: 0.6rem 0.5rem; text-align: right;">Job-Market Demand</th>
                  </tr>
                </thead>
                <tbody>
                  ${reqSkills.length > 0 ? reqSkills.map(r => `
                    <tr style="border-bottom: 1px solid rgba(255, 255, 255, 0.04);">
                      <td style="padding: 0.75rem 0.5rem; font-weight: 700; color: #ffffff;">${r.skill}</td>
                      <td style="padding: 0.75rem 0.5rem;">
                        <span class="badge badge-secondary">${r.required_level}</span>
                      </td>
                      <td style="padding: 0.75rem 0.5rem; text-align: right; font-weight: 700; color: #38bdf8;">
                        ${r.job_market_demand}%
                      </td>
                    </tr>
                  `).join('') : `
                    <tr>
                      <td colspan="3" style="text-align: center; color: var(--text-dim); padding: 1.5rem;">No role requirements loaded.</td>
                    </tr>
                  `}
                </tbody>
              </table>
            </div>
          </div>

          <!-- SECTION: SKILL GAPS TABLE -->
          <div class="glass-card" style="grid-column: 1 / -1;">
            <div class="card-header" style="border-bottom: 1px solid var(--border-subtle); padding-bottom: 0.85rem; margin-bottom: 1rem;">
              <div>
                <h3 style="font-family: var(--font-heading); font-size: 1.15rem; color: #ffffff; margin: 0;">
                  🔍 Skill Gaps & Prioritization
                </h3>
                <p style="font-size: 0.8rem; color: var(--text-muted); margin-top: 0.2rem;">
                  Disparity between verified competency and target job-market benchmark
                </p>
              </div>
              <span class="badge badge-primary">Module 5</span>
            </div>

            <div style="overflow-x: auto;">
              <table style="width: 100%; border-collapse: collapse; font-size: 0.85rem;">
                <thead>
                  <tr style="border-bottom: 1px solid var(--border-subtle); color: var(--text-dim); text-align: left;">
                    <th style="padding: 0.65rem 0.5rem;">Skill</th>
                    <th style="padding: 0.65rem 0.5rem;">Current Level</th>
                    <th style="padding: 0.65rem 0.5rem;">Required Level</th>
                    <th style="padding: 0.65rem 0.5rem;">Gap Magnitude</th>
                    <th style="padding: 0.65rem 0.5rem; text-align: right;">Priority</th>
                  </tr>
                </thead>
                <tbody>
                  ${gaps.length > 0 ? gaps.map(g => {
                    const isMet = g.gap_num === 0;
                    return `
                      <tr style="border-bottom: 1px solid rgba(255, 255, 255, 0.04);">
                        <td style="padding: 0.75rem 0.5rem; font-weight: 700; color: #ffffff;">${g.skill}</td>
                        <td style="padding: 0.75rem 0.5rem; color: ${g.current_level === 'Not Assessed' ? 'var(--text-dim)' : '#38bdf8'}; font-weight: 600;">
                          ${g.current_level}
                        </td>
                        <td style="padding: 0.75rem 0.5rem; color: #10b981; font-weight: 600;">${g.required_level}</td>
                        <td style="padding: 0.75rem 0.5rem;">
                          ${isMet ? `<span class="badge" style="background: rgba(16, 185, 129, 0.15); color: #10b981;">No Gap (Met)</span>` : `<span class="badge badge-warning">${g.gap} (+${g.gap_num})</span>`}
                        </td>
                        <td style="padding: 0.75rem 0.5rem; text-align: right;">
                          <span class="badge ${g.priority_badge_class || (g.priority === 'Critical' ? 'badge-danger' : g.priority === 'High' ? 'badge-warning' : g.priority === 'Medium' ? 'badge-primary' : 'badge-secondary')}">
                            ${g.priority}
                          </span>
                        </td>
                      </tr>
                    `;
                  }).join('') : `
                    <tr>
                      <td colspan="5" style="text-align: center; color: var(--text-dim); padding: 1.5rem;">No gap metrics computed.</td>
                    </tr>
                  `}
                </tbody>
              </table>
            </div>
          </div>

        </div>

        <!-- 6. CURRICULUM PROGRESS & MICRO-CREDENTIALS STATUS (SECTIONS D & E) -->
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(380px, 1fr)); gap: 1.5rem;">

          <!-- SECTION: CURRICULUM PROGRESS BREAKDOWN -->
          <div class="glass-card">
            <div class="card-header" style="border-bottom: 1px solid var(--border-subtle); padding-bottom: 0.85rem; margin-bottom: 1rem;">
              <div>
                <h3 style="font-family: var(--font-heading); font-size: 1.15rem; color: #ffffff; margin: 0;">
                  📚 Curriculum Progress
                </h3>
                <p style="font-size: 0.8rem; color: var(--text-muted); margin-top: 0.2rem;">
                  Modular competency bridging roadmap (${curr.total_modules || 0} Total Modules)
                </p>
              </div>
              <span class="badge badge-primary">Module 6</span>
            </div>

            <!-- Current Active Module Callout -->
            ${curr.current_module ? `
              <div style="background: rgba(56, 189, 248, 0.08); border: 1px solid rgba(56, 189, 248, 0.25); border-radius: var(--radius-md); padding: 1rem; margin-bottom: 1rem;">
                <div style="font-size: 0.72rem; text-transform: uppercase; color: #38bdf8; font-weight: 700; margin-bottom: 0.25rem;">
                  Current Module In Progress
                </div>
                <div style="font-size: 1rem; font-weight: 800; color: #ffffff;">${curr.current_module.title}</div>
                <div style="font-size: 0.8rem; color: var(--text-muted); margin-top: 0.35rem;">
                  Target Skill: <strong style="color: #ffffff;">${curr.current_module.skill_name}</strong> &bull; Duration: ${curr.current_module.hours} Hours
                </div>
                <div style="margin-top: 0.75rem;">
                  <button class="btn btn-primary btn-sm" onclick="App.goToStep(6)">🚀 Continue Module Workspace</button>
                </div>
              </div>
            ` : `
              <div style="background: rgba(16, 185, 129, 0.08); border: 1px solid rgba(16, 185, 129, 0.25); border-radius: var(--radius-md); padding: 1rem; margin-bottom: 1rem;">
                <div style="color: #10b981; font-weight: 700; font-size: 0.95rem;">🎉 All Curriculum Modules Completed!</div>
                <div style="color: var(--text-muted); font-size: 0.8rem; margin-top: 0.25rem;">You have finished all required modules for this role.</div>
              </div>
            `}

            <!-- Completed & Remaining Modules Counts -->
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; margin-top: 0.5rem;">
              <div style="background: rgba(15, 23, 42, 0.5); padding: 0.85rem; border-radius: var(--radius-md); border: 1px solid rgba(255, 255, 255, 0.04);">
                <div style="font-size: 0.75rem; color: var(--text-muted); margin-bottom: 0.2rem;">Completed Modules</div>
                <div style="font-size: 1.35rem; font-weight: 800; color: #10b981;">${curr.completed_count || 0}</div>
                <div style="font-size: 0.7rem; color: var(--text-dim); margin-top: 0.2rem;">100% Verified</div>
              </div>
              <div style="background: rgba(15, 23, 42, 0.5); padding: 0.85rem; border-radius: var(--radius-md); border: 1px solid rgba(255, 255, 255, 0.04);">
                <div style="font-size: 0.75rem; color: var(--text-muted); margin-bottom: 0.2rem;">Remaining Modules</div>
                <div style="font-size: 1.35rem; font-weight: 800; color: #f59e0b;">${curr.remaining_count || 0}</div>
                <div style="font-size: 0.7rem; color: var(--text-dim); margin-top: 0.2rem;">To Be Completed</div>
              </div>
            </div>
          </div>

          <!-- SECTION: MICRO-CREDENTIALS STATUS -->
          <div class="glass-card">
            <div class="card-header" style="border-bottom: 1px solid var(--border-subtle); padding-bottom: 0.85rem; margin-bottom: 1rem;">
              <div>
                <h3 style="font-family: var(--font-heading); font-size: 1.15rem; color: #ffffff; margin: 0;">
                  🎖️ Micro-Credentials
                </h3>
                <p style="font-size: 0.8rem; color: var(--text-muted); margin-top: 0.2rem;">
                  Earned milestones and in-progress micro-credentials
                </p>
              </div>
              <span class="badge badge-primary">Module 7</span>
            </div>

            <!-- Earned Credentials Cards -->
            <div style="margin-bottom: 1rem;">
              <div style="font-size: 0.75rem; text-transform: uppercase; color: var(--text-dim); font-weight: 700; margin-bottom: 0.5rem;">
                Earned Credentials (${creds.earned_count || 0})
              </div>
              <div style="display: flex; flex-direction: column; gap: 0.5rem;">
                ${creds.earned_credentials && creds.earned_credentials.length > 0 ? creds.earned_credentials.map(c => `
                  <div style="background: rgba(15, 23, 42, 0.6); padding: 0.75rem; border-radius: var(--radius-sm); border-left: 3px solid #10b981; display: flex; justify-content: space-between; align-items: center;">
                    <div>
                      <div style="font-size: 0.85rem; font-weight: 700; color: #ffffff;">${c.title}</div>
                      <div style="font-size: 0.72rem; color: var(--text-muted); margin-top: 0.15rem;">
                        ID: <code style="color: #38bdf8;">${c.credential_id}</code> &bull; Issued: ${c.issue_date || '2026-10-10'}
                      </div>
                    </div>
                    <span class="badge" style="background: rgba(16, 185, 129, 0.2); color: #10b981; font-size: 0.7rem;">Verified</span>
                  </div>
                `).join('') : `
                  <div style="font-size: 0.8rem; color: var(--text-dim); padding: 0.5rem 0;">No credentials earned yet. Complete curriculum modules and assessments to claim.</div>
                `}
              </div>
            </div>

            <!-- In-Progress Credentials Cards -->
            <div>
              <div style="font-size: 0.75rem; text-transform: uppercase; color: var(--text-dim); font-weight: 700; margin-bottom: 0.5rem;">
                In-Progress Credentials (${creds.in_progress_count || 0})
              </div>
              <div style="display: flex; flex-direction: column; gap: 0.5rem;">
                ${creds.in_progress_credentials && creds.in_progress_credentials.length > 0 ? creds.in_progress_credentials.map(c => `
                  <div style="background: rgba(15, 23, 42, 0.6); padding: 0.75rem; border-radius: var(--radius-sm); border-left: 3px solid #38bdf8; display: flex; justify-content: space-between; align-items: center;">
                    <div>
                      <div style="font-size: 0.85rem; font-weight: 700; color: #ffffff;">${c.title}</div>
                      <div style="font-size: 0.72rem; color: var(--text-muted); margin-top: 0.15rem;">
                        Completion: ${c.completion_pct}% &bull; Level: ${c.level}
                      </div>
                    </div>
                    <span class="badge badge-warning" style="font-size: 0.7rem;">In Progress</span>
                  </div>
                `).join('') : `
                  <div style="font-size: 0.8rem; color: var(--text-dim); padding: 0.5rem 0;">No active in-progress credentials.</div>
                `}
              </div>
            </div>

          </div>

        </div>

        <!-- 7. FINAL ACTIONABLE RECOMMENDATIONS -->
        <div class="glass-card" style="background: linear-gradient(135deg, rgba(15, 23, 42, 0.9), rgba(30, 41, 59, 0.75)); border-color: rgba(56, 189, 248, 0.2);">
          <div class="card-header" style="border-bottom: 1px solid var(--border-subtle); padding-bottom: 0.85rem; margin-bottom: 1.25rem;">
            <div>
              <h2 style="font-family: var(--font-heading); font-size: 1.3rem; font-weight: 800; color: #ffffff; margin: 0;">
                🎯 Final Actionable Recommendations
              </h2>
              <p style="font-size: 0.85rem; color: var(--text-muted); margin-top: 0.25rem;">
                Data-driven strategic actions to maximize your technical readiness and bridge remaining gaps
              </p>
            </div>
            <span class="badge badge-primary">Next Steps</span>
          </div>

          <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1.25rem;">

            <!-- Rec 1: Top Remaining Skill Gaps -->
            <div style="background: rgba(15, 23, 42, 0.7); padding: 1.15rem; border-radius: var(--radius-md); border: 1px solid rgba(239, 68, 68, 0.2);">
              <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                <span style="font-size: 1.2rem;">⚠️</span>
                <h4 style="color: #ffffff; margin: 0; font-size: 0.95rem; font-weight: 800;">Top Remaining Skill Gaps</h4>
              </div>
              <p style="font-size: 0.78rem; color: var(--text-muted); margin-bottom: 0.75rem;">
                Skills requiring the largest competency leap to satisfy role requirements:
              </p>
              <div style="display: flex; flex-direction: column; gap: 0.5rem;">
                ${recs.top_remaining_skill_gaps && recs.top_remaining_skill_gaps.length > 0 ? recs.top_remaining_skill_gaps.map(g => `
                  <div style="background: rgba(239, 68, 68, 0.08); padding: 0.5rem 0.65rem; border-radius: var(--radius-sm); border-left: 2px solid #ef4444;">
                    <div style="font-size: 0.82rem; font-weight: 700; color: #ffffff;">${g.skill} (${g.priority} Priority)</div>
                    <div style="font-size: 0.72rem; color: var(--text-muted); margin-top: 0.15rem;">
                      Current: <strong style="color: #f87171;">${g.current_level}</strong> ➔ Target: <strong style="color: #10b981;">${g.required_level}</strong>
                    </div>
                  </div>
                `).join('') : `
                  <div style="color: #10b981; font-size: 0.82rem;">No critical gaps remaining!</div>
                `}
              </div>
            </div>

            <!-- Rec 2: Highest-Priority Skills -->
            <div style="background: rgba(15, 23, 42, 0.7); padding: 1.15rem; border-radius: var(--radius-md); border: 1px solid rgba(245, 158, 11, 0.2);">
              <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                <span style="font-size: 1.2rem;">⚡</span>
                <h4 style="color: #ffffff; margin: 0; font-size: 0.95rem; font-weight: 800;">Highest-Priority Skills</h4>
              </div>
              <p style="font-size: 0.78rem; color: var(--text-muted); margin-bottom: 0.75rem;">
                Skills with highest market demand and prerequisite importance:
              </p>
              <div style="display: flex; flex-direction: column; gap: 0.5rem;">
                ${recs.highest_priority_skills && recs.highest_priority_skills.length > 0 ? recs.highest_priority_skills.map(s => `
                  <div style="background: rgba(245, 158, 11, 0.08); padding: 0.5rem 0.65rem; border-radius: var(--radius-sm); border-left: 2px solid #f59e0b;">
                    <div style="font-size: 0.82rem; font-weight: 700; color: #ffffff;">${s.skill}</div>
                    <div style="font-size: 0.72rem; color: var(--text-muted); margin-top: 0.15rem;">
                      ${s.action}
                    </div>
                  </div>
                `).join('') : `
                  <div style="color: #10b981; font-size: 0.82rem;">All high priority skills mastered!</div>
                `}
              </div>
            </div>

            <!-- Rec 3: Recommended Next Module -->
            <div style="background: rgba(15, 23, 42, 0.7); padding: 1.15rem; border-radius: var(--radius-md); border: 1px solid rgba(56, 189, 248, 0.2);">
              <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                <span style="font-size: 1.2rem;">🚀</span>
                <h4 style="color: #ffffff; margin: 0; font-size: 0.95rem; font-weight: 800;">Recommended Next Module</h4>
              </div>
              <p style="font-size: 0.78rem; color: var(--text-muted); margin-bottom: 0.75rem;">
                Immediate learning step on your personalized pathway:
              </p>
              ${recs.recommended_next_module ? `
                <div style="background: rgba(56, 189, 248, 0.08); padding: 0.75rem; border-radius: var(--radius-sm); border-left: 2px solid #38bdf8;">
                  <div style="font-size: 0.88rem; font-weight: 800; color: #ffffff;">${recs.recommended_next_module.title}</div>
                  <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 0.25rem;">
                    Skill: ${recs.recommended_next_module.skill} &bull; ${recs.recommended_next_module.duration}
                  </div>
                  <div style="font-size: 0.72rem; color: var(--text-dim); margin-top: 0.35rem;">
                    ${recs.recommended_next_module.learning_objective || 'Master targeted competency to unlock micro-credential.'}
                  </div>
                  <button class="btn btn-primary btn-sm" style="margin-top: 0.75rem; width: 100%;" onclick="App.goToStep(6)">
                    🚀 Start / Resume Module
                  </button>
                </div>
              ` : `
                <div style="color: #10b981; font-size: 0.82rem;">All core modules completed!</div>
              `}
            </div>

            <!-- Rec 4: Recommended Assessment / Retake -->
            <div style="background: rgba(15, 23, 42, 0.7); padding: 1.15rem; border-radius: var(--radius-md); border: 1px solid rgba(16, 185, 129, 0.2);">
              <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                <span style="font-size: 1.2rem;">🎯</span>
                <h4 style="color: #ffffff; margin: 0; font-size: 0.95rem; font-weight: 800;">Recommended Assessment / Retake</h4>
              </div>
              <p style="font-size: 0.78rem; color: var(--text-muted); margin-bottom: 0.75rem;">
                Targeted evaluation to elevate verified proficiency:
              </p>
              ${recs.recommended_assessment_retake ? `
                <div style="background: rgba(16, 185, 129, 0.08); padding: 0.75rem; border-radius: var(--radius-sm); border-left: 2px solid #10b981;">
                  <div style="font-size: 0.88rem; font-weight: 800; color: #ffffff;">${recs.recommended_assessment_retake.skill} (${recs.recommended_assessment_retake.type})</div>
                  <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 0.25rem;">
                    Current: ${recs.recommended_assessment_retake.current_status} ➔ Goal: ${recs.recommended_assessment_retake.target_level}
                  </div>
                  <div style="font-size: 0.72rem; color: var(--text-dim); margin-top: 0.35rem;">
                    ${recs.recommended_assessment_retake.rationale}
                  </div>
                  <button class="btn btn-primary btn-sm" style="margin-top: 0.75rem; width: 100%;" onclick="App.goToStep(2)">
                    🎯 Launch Timed Assessment
                  </button>
                </div>
              ` : `
                <div style="color: #10b981; font-size: 0.82rem;">All competencies verified at optimal levels!</div>
              `}
            </div>

          </div>
        </div>

      </div>
    `;
  },

  /**
   * Generates a rich, responsive SVG Radar Chart comparing Verified vs Required profiles.
   */
  renderRadarSVG(radarData) {
    if (!radarData || !radarData.labels || radarData.labels.length < 3) {
      return `<div style="color: var(--text-dim); font-size: 0.85rem; text-align: center;">Minimum 3 skills required for radar projection.</div>`;
    }

    const labels = radarData.labels;
    const verified = radarData.verified_series || [];
    const required = radarData.required_series || [];
    const numPoints = labels.length;
    const maxVal = radarData.max_scale || 5.0;

    const width = 340;
    const height = 300;
    const centerX = width / 2;
    const centerY = height / 2;
    const radius = 100;

    // Helper to calculate (x, y) coordinates for angle and value
    const getCoords = (index, value) => {
      const angle = (Math.PI * 2 / numPoints) * index - Math.PI / 2;
      const r = (value / maxVal) * radius;
      const x = centerX + r * Math.cos(angle);
      const y = centerY + r * Math.sin(angle);
      return { x, y, angle };
    };

    // Concentric grid polygons (levels 1, 2, 3, 4, 5)
    let gridPolygons = '';
    for (let level = 1; level <= 5; level++) {
      let points = [];
      for (let i = 0; i < numPoints; i++) {
        const pt = getCoords(i, level);
        points.push(`${pt.x.toFixed(1)},${pt.y.toFixed(1)}`);
      }
      gridPolygons += `
        <polygon points="${points.join(' ')}"
          fill="none"
          stroke="rgba(255, 255, 255, 0.08)"
          stroke-width="1" />
      `;
    }

    // Radial spokes and skill labels
    let spokes = '';
    let labelTags = '';
    for (let i = 0; i < numPoints; i++) {
      const outerPt = getCoords(i, maxVal);
      spokes += `
        <line x1="${centerX}" y1="${centerY}" x2="${outerPt.x.toFixed(1)}" y2="${outerPt.y.toFixed(1)}"
          stroke="rgba(255, 255, 255, 0.12)" stroke-width="1" />
      `;

      // Text label position (pushed slightly beyond radius)
      const angle = (Math.PI * 2 / numPoints) * i - Math.PI / 2;
      const labelRadius = radius + 24;
      const lx = centerX + labelRadius * Math.cos(angle);
      const ly = centerY + labelRadius * Math.sin(angle) + 4;
      const anchor = Math.abs(Math.cos(angle)) < 0.2 ? 'middle' : Math.cos(angle) > 0 ? 'start' : 'end';

      labelTags += `
        <text x="${lx.toFixed(1)}" y="${ly.toFixed(1)}"
          fill="#cbd5e1" font-size="10" font-weight="600"
          text-anchor="${anchor}">${labels[i]}</text>
      `;
    }

    // Required polygon points (green dashed)
    const reqPoints = required.map((val, idx) => {
      const pt = getCoords(idx, val || 0);
      return `${pt.x.toFixed(1)},${pt.y.toFixed(1)}`;
    }).join(' ');

    // Verified polygon points (cyan glowing fill)
    const verPoints = verified.map((val, idx) => {
      const pt = getCoords(idx, val || 0);
      return `${pt.x.toFixed(1)},${pt.y.toFixed(1)}`;
    }).join(' ');

    // Verified vertex dots
    const verDots = verified.map((val, idx) => {
      const pt = getCoords(idx, val || 0);
      return `<circle cx="${pt.x.toFixed(1)}" cy="${pt.y.toFixed(1)}" r="3.5" fill="#38bdf8" stroke="#ffffff" stroke-width="1.5" />`;
    }).join('');

    return `
      <svg width="${width}" height="${height}" viewBox="0 0 ${width} ${height}" style="overflow: visible;">
        <defs>
          <linearGradient id="verGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="#38bdf8" stop-opacity="0.45" />
            <stop offset="100%" stop-color="#818cf8" stop-opacity="0.25" />
          </linearGradient>
        </defs>

        <!-- Concentric Grids -->
        ${gridPolygons}

        <!-- Radial Spokes -->
        ${spokes}

        <!-- Required Polygon (Target Benchmark) -->
        <polygon points="${reqPoints}"
          fill="rgba(16, 185, 129, 0.15)"
          stroke="#10b981"
          stroke-width="2"
          stroke-dasharray="4,3" />

        <!-- Verified Polygon (Candidate Competency) -->
        <polygon points="${verPoints}"
          fill="url(#verGradient)"
          stroke="#38bdf8"
          stroke-width="2.5" />

        <!-- Verified Vertices -->
        ${verDots}

        <!-- Skill Labels -->
        ${labelTags}
      </svg>
    `;
  }
};

// Explicitly attach to window
window.Readiness = Readiness;
