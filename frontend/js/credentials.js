/**
 * Module 7: Micro-Credential Generation Dashboard
 * Converts completed learning modules and verified skills into structured micro-credentials.
 * Manages Earned Credentials, In-Progress Credentials, Credential Details,
 * and Public Digital Verification.
 */
const Credentials = {
  currentData: null,
  activeFilter: 'all', // 'all', 'earned', 'in_progress'

  init() {
    console.log("Initializing Module 7 Micro-Credentials Component...");
  },

  async loadCredentials() {
    const container = document.getElementById('credentials-container');
    if (!container) return;

    container.innerHTML = `
      <div class="glass-card" style="text-align: center; padding: 4rem 2rem;">
        <div class="spinner" style="margin: 0 auto 1.5rem;"></div>
        <h3 style="color: #ffffff; font-family: var(--font-heading); margin-bottom: 0.5rem;">
          Loading Micro-Credential Registry...
        </h3>
        <p style="color: var(--text-muted); font-size: 0.95rem; max-width: 520px; margin: 0 auto;">
          Synchronizing completed learning modules, practical projects, and verified assessment scores into structured digital achievements.
        </p>
      </div>
    `;

    try {
      const res = await API.getCredentials();
      if (res.success && res.data) {
        this.currentData = res.data;
        this.renderCredentials(res.data);
      } else {
        container.innerHTML = `
          <div class="glass-card" style="text-align: center; padding: 3rem;">
            <div style="font-size: 2.5rem; margin-bottom: 1rem;">⚠️</div>
            <h3 style="color: #ffffff;">Unable to load credentials</h3>
            <p style="color: var(--text-muted); margin-bottom: 1.5rem;">${res.detail || 'An unexpected error occurred.'}</p>
            <button class="btn btn-primary" onclick="Credentials.syncCredentials()">Synchronize Now</button>
          </div>
        `;
      }
    } catch (err) {
      console.error("Error loading credentials:", err);
      container.innerHTML = `
        <div class="glass-card" style="text-align: center; padding: 3rem;">
          <div style="font-size: 2.5rem; margin-bottom: 1rem;">⚠️</div>
          <h3 style="color: #ffffff;">Failed to fetch micro-credentials</h3>
          <p style="color: var(--text-muted); margin-bottom: 1.5rem;">${err.message}</p>
          <button class="btn btn-primary" onclick="Credentials.loadCredentials()">Retry</button>
        </div>
      `;
    }
  },

  async syncCredentials() {
    App.showToast("Synchronizing micro-credentials from completed curriculum modules...", "info");
    try {
      const res = await API.syncCredentials();
      if (res.success && res.data) {
        this.currentData = res.data;
        this.renderCredentials(res.data);
        App.showToast("Micro-credentials registry successfully updated!", "success");
      }
    } catch (err) {
      App.showToast(`Synchronization failed: ${err.message}`, "error");
    }
  },

  renderCredentials(data) {
    const container = document.getElementById('credentials-container');
    if (!container) return;

    const earned = data.earned_credentials || [];
    const inProgress = data.in_progress_credentials || [];
    const totalEarned = earned.length;
    const totalInProgress = inProgress.length;

    // Filter display
    let displayList = [];
    if (this.activeFilter === 'earned') displayList = earned;
    else if (this.activeFilter === 'in_progress') displayList = inProgress;
    else displayList = [...earned, ...inProgress];

    const getLevelBadgeClass = (lvl) => {
      const l = (lvl || '').toLowerCase();
      if (l === 'advanced') return 'badge-danger';
      if (l === 'intermediate') return 'badge-warning';
      if (l === 'basic') return 'badge-info';
      return 'badge-success'; // Beginner
    };

    container.innerHTML = `
      <!-- 1. HEADER BANNER -->
      <div class="glass-card" style="background: linear-gradient(135deg, rgba(30, 41, 59, 0.9), rgba(15, 23, 42, 0.95)); border: 1px solid rgba(234, 179, 8, 0.35); margin-bottom: 1.5rem;">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 1.5rem;">
          <div>
            <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.5rem; flex-wrap: wrap;">
              <span class="badge badge-warning" style="font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.05em;">
                MODULE 7: MICRO-CREDENTIAL GENERATION
              </span>
              <span class="badge badge-info" style="font-size: 0.8rem;">
                Candidate: ${data.user_name || 'Student'}
              </span>
              <span class="badge badge-secondary" style="font-size: 0.8rem;">
                Platform-Generated Milestones (Non-Accredited)
              </span>
            </div>
            <h2 style="font-family: var(--font-heading); font-size: 1.95rem; font-weight: 800; color: #ffffff; margin-bottom: 0.4rem; letter-spacing: -0.02em;">
              MY CREDENTIALS
            </h2>
            <p style="color: var(--text-muted); font-size: 0.95rem; max-width: 820px; line-height: 1.55;">
              Convert completed technical learning modules, practical engineering tasks, and verified assessment scores into
              verifiable digital micro-credentials. Designed for technical portfolio evidence across 4 distinct levels.
            </p>
          </div>

          <div style="display: flex; gap: 0.75rem; flex-wrap: wrap;">
            <button class="btn btn-primary" onclick="Credentials.syncCredentials()">
              ⚡ Sync Completed Modules
            </button>
            <button class="btn btn-secondary" onclick="App.goToStep(6)">
              ← Back to Curriculum
            </button>
          </div>
        </div>

        <!-- KPI SUMMARY BAR -->
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1rem; margin-top: 1.75rem;">
          <div style="background: rgba(15, 23, 42, 0.65); padding: 1rem 1.2rem; border-radius: var(--radius-md); border: 1px solid rgba(34, 197, 94, 0.3);">
            <div style="font-size: 0.75rem; color: var(--text-dim); text-transform: uppercase; letter-spacing: 0.05em;">Earned Credentials</div>
            <div style="font-size: 1.6rem; font-weight: 800; color: #4ade80; margin-top: 0.25rem;">${totalEarned}</div>
            <div style="font-size: 0.8rem; color: var(--text-muted); margin-top: 0.2rem;">Fully Issued & Verified</div>
          </div>

          <div style="background: rgba(15, 23, 42, 0.65); padding: 1rem 1.2rem; border-radius: var(--radius-md); border: 1px solid rgba(234, 179, 8, 0.3);">
            <div style="font-size: 0.75rem; color: var(--text-dim); text-transform: uppercase; letter-spacing: 0.05em;">In-Progress Credentials</div>
            <div style="font-size: 1.6rem; font-weight: 800; color: #facc15; margin-top: 0.25rem;">${totalInProgress}</div>
            <div style="font-size: 0.8rem; color: var(--text-muted); margin-top: 0.2rem;">Active Module Tracks</div>
          </div>

          <div style="background: rgba(15, 23, 42, 0.65); padding: 1rem 1.2rem; border-radius: var(--radius-md); border: 1px solid var(--border-subtle);">
            <div style="font-size: 0.75rem; color: var(--text-dim); text-transform: uppercase; letter-spacing: 0.05em;">Credential Levels</div>
            <div style="font-size: 1.2rem; font-weight: 700; color: #38bdf8; margin-top: 0.35rem;">4 Tier System</div>
            <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 0.2rem;">Beginner • Basic • Inter • Adv</div>
          </div>

          <div style="background: rgba(15, 23, 42, 0.65); padding: 1rem 1.2rem; border-radius: var(--radius-md); border: 1px solid var(--border-subtle);">
            <div style="font-size: 0.75rem; color: var(--text-dim); text-transform: uppercase; letter-spacing: 0.05em;">Digital Verification</div>
            <div style="font-size: 1.2rem; font-weight: 700; color: #a78bfa; margin-top: 0.35rem;">Active Registry</div>
            <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 0.2rem;">Public URL Validation</div>
          </div>
        </div>

        <!-- FILTER TABS BAR -->
        <div style="margin-top: 1.5rem; padding-top: 1.25rem; border-top: 1px solid rgba(255, 255, 255, 0.08); display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;">
          <div style="display: flex; gap: 0.5rem; flex-wrap: wrap;">
            <button type="button" class="btn btn-sm ${this.activeFilter === 'all' ? 'btn-primary' : 'btn-secondary'}" onclick="Credentials.setFilter('all')">
              All Credentials (${totalEarned + totalInProgress})
            </button>
            <button type="button" class="btn btn-sm ${this.activeFilter === 'earned' ? 'btn-primary' : 'btn-secondary'}" onclick="Credentials.setFilter('earned')">
              🏆 Earned (${totalEarned})
            </button>
            <button type="button" class="btn btn-sm ${this.activeFilter === 'in_progress' ? 'btn-primary' : 'btn-secondary'}" onclick="Credentials.setFilter('in_progress')">
              ⚡ In-Progress (${totalInProgress})
            </button>
          </div>

          <div style="font-size: 0.8rem; color: var(--text-muted);">
            Showing <b style="color: #ffffff;">${displayList.length}</b> digital records
          </div>
        </div>
      </div>

      <!-- 2. CREDENTIALS CARDS GRID -->
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(360px, 1fr)); gap: 1.5rem; margin-bottom: 2rem;">
        ${displayList.map(c => {
          const isEarned = c.status === 'earned';
          const isPyExample = c.title.includes("Python for Data Analytics");
          return `
            <div class="glass-card" style="position: relative; border: 1px solid ${isEarned ? 'rgba(34, 197, 94, 0.45)' : isPyExample ? 'rgba(234, 179, 8, 0.45)' : 'var(--border-subtle)'}; background: ${isEarned ? 'linear-gradient(135deg, rgba(30, 41, 59, 0.8), rgba(20, 40, 25, 0.85))' : 'rgba(30, 41, 59, 0.7)'}; display: flex; flex-direction: column; justify-content: space-between;">

              <div>
                <!-- Top Badge & Level Row -->
                <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 0.5rem; margin-bottom: 0.75rem;">
                  <div>
                    <span style="font-size: 0.75rem; font-weight: 800; color: var(--primary); font-family: monospace;">${c.credential_id}</span>
                    <div style="display: flex; align-items: center; gap: 0.4rem; margin-top: 0.2rem;">
                      <span class="badge ${getLevelBadgeClass(c.level)}">${c.level}</span>
                      <span class="badge ${isEarned ? 'badge-success' : 'badge-warning'}">${isEarned ? '✓ EARNED' : 'IN PROGRESS'}</span>
                    </div>
                  </div>
                  <div style="width: 44px; height: 44px; border-radius: 12px; background: ${isEarned ? 'linear-gradient(135deg, #16a34a, #22c55e)' : 'rgba(51, 65, 85, 0.6)'}; display: flex; align-items: center; justify-content: center; font-size: 1.4rem; flex-shrink: 0; box-shadow: ${isEarned ? '0 0 15px rgba(34, 197, 94, 0.4)' : 'none'};">
                    ${isEarned ? '🏆' : '⚡'}
                  </div>
                </div>

                <!-- Title & Associated Skill -->
                <h3 style="font-family: var(--font-heading); font-size: 1.25rem; font-weight: 800; color: #ffffff; margin-bottom: 0.35rem; line-height: 1.3;">
                  ${c.title}
                </h3>
                <div style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 0.85rem;">
                  Skill: <b style="color: #ffffff;">${c.skill}</b> • Domain: <b style="color: var(--primary);">${c.domain}</b>
                </div>

                <!-- Completion Progress Bar -->
                <div style="background: rgba(15, 23, 42, 0.6); padding: 0.85rem 1rem; border-radius: var(--radius-md); border: 1px solid var(--border-subtle); margin-bottom: 1rem;">
                  <div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.82rem; margin-bottom: 0.35rem;">
                    <span style="color: var(--text-muted); font-weight: 600;">Completion Progress:</span>
                    <span style="font-weight: 800; color: ${isEarned ? '#4ade80' : '#facc15'};">${c.completion_pct}%</span>
                  </div>
                  <div class="module-progress-bar-container" style="height: 6px;">
                    <div class="module-progress-bar-fill" style="width: ${c.completion_pct}%; background: ${isEarned ? 'linear-gradient(90deg, #16a34a, #22c55e)' : 'linear-gradient(90deg, #6366f1, #eab308)'};"></div>
                  </div>
                  <div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.75rem; color: var(--text-dim); margin-top: 0.4rem;">
                    <span>Verified Assessment Score: <b style="color: #ffffff;">${c.assessment_score}%</b></span>
                    <span>${isEarned ? `Issued: ${c.issue_date}` : 'Target: 80%+ to issue'}</span>
                  </div>
                </div>

                <!-- Requirements Checklist Accordion / Items -->
                <div style="margin-bottom: 1rem;">
                  <div style="font-size: 0.78rem; text-transform: uppercase; font-weight: 700; color: var(--text-dim); margin-bottom: 0.4rem;">
                    Competency Requirements (${c.requirements.length} Components):
                  </div>
                  <ul style="margin: 0; padding-left: 1.2rem; font-size: 0.82rem; color: #cbd5e1; line-height: 1.45;">
                    ${c.requirements.map(req => {
                      const isDone = isEarned || (c.modules_completed && c.modules_completed.some(mc => mc.toLowerCase().includes(req.toLowerCase().split(' ')[0])));
                      return `
                        <li style="margin-bottom: 0.2rem;">
                          <span style="color: ${isDone ? '#4ade80' : '#94a3b8'};">
                            ${isDone ? '✓' : '○'} ${req}
                          </span>
                        </li>
                      `;
                    }).join('')}
                  </ul>
                </div>

                <!-- Practical Project Task Deliverable -->
                <div style="background: rgba(15, 23, 42, 0.4); padding: 0.75rem; border-radius: var(--radius-sm); border: 1px solid rgba(255, 255, 255, 0.05); font-size: 0.8rem; margin-bottom: 1rem;">
                  <span style="color: var(--warning); font-weight: 700;">Practical Project:</span>
                  <span style="color: var(--text-muted); display: block; margin-top: 0.2rem; line-height: 1.4;">
                    ${c.practical_task}
                  </span>
                </div>
              </div>

              <!-- Footer Actions -->
              <div style="padding-top: 0.75rem; border-top: 1px solid rgba(255, 255, 255, 0.08); display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.5rem;">
                <button type="button" class="btn ${isEarned ? 'btn-success' : 'btn-secondary'} btn-sm" onclick="Credentials.openCredentialModal('${c.credential_id}')">
                  ${isEarned ? '📜 View Credential' : '🔍 Inspect Details'}
                </button>

                <div style="display: flex; gap: 0.4rem;">
                  <button type="button" class="btn btn-secondary btn-sm" onclick="Credentials.verifyPublicOnline('${c.credential_id}')" title="Verify online status">
                    Verify ↗
                  </button>
                  ${!isEarned && c.completion_pct >= 80 ? `
                    <button type="button" class="btn btn-primary btn-sm" onclick="Credentials.claimCredential('${c.credential_id}')">
                      Claim Credential
                    </button>
                  ` : ''}
                </div>
              </div>

            </div>
          `;
        }).join('')}
      </div>

      <!-- 3. NON-ACCREDITATION NOTICE (Mandatory Policy Disclosure) -->
      <div class="glass-card" style="border: 1px solid rgba(234, 179, 8, 0.35); background: rgba(42, 30, 15, 0.65);">
        <div style="display: flex; gap: 1rem; align-items: flex-start;">
          <div style="font-size: 2rem; flex-shrink: 0;">⚖️</div>
          <div>
            <h4 style="font-size: 1.05rem; font-weight: 700; color: #facc15; margin-bottom: 0.35rem;">
              Digital Micro-Credential Accreditation & Milestone Disclosure
            </h4>
            <p style="font-size: 0.88rem; color: #cbd5e1; line-height: 1.55; margin: 0;">
              ${data.disclaimer || 'Non-Accreditation Notice: This digital micro-credential is an internal platform-generated milestone verifying technical module completion and skills assessment for candidate portfolio presentation. It does not claim or represent government, university, or third-party accredited academic status.'}
            </p>
            <div style="font-size: 0.78rem; color: var(--text-dim); margin-top: 0.4rem;">
              Regulatory Note: These records serve as transparent competency proof for portfolio reviews and hiring evaluations. No claim of official degree accreditation is made.
            </div>
          </div>
        </div>
      </div>
    `;
  },

  setFilter(filterMode) {
    this.activeFilter = filterMode;
    if (this.currentData) {
      this.renderCredentials(this.currentData);
    }
  },

  openCredentialModal(credId) {
    if (!this.currentData) return;
    const all = [...(this.currentData.earned_credentials || []), ...(this.currentData.in_progress_credentials || [])];
    const c = all.find(item => item.credential_id === credId);
    if (!c) {
      App.showToast("Credential record not found.", "error");
      return;
    }

    const modal = document.getElementById('credential-certificate-modal');
    if (!modal) return;

    const modalContent = document.getElementById('credential-certificate-content');
    if (!modalContent) return;

    modalContent.innerHTML = `
      <!-- Certificate Header Ribbon -->
      <div style="text-align: center; border-bottom: 2px dashed rgba(234, 179, 8, 0.4); padding-bottom: 1.5rem; margin-bottom: 1.5rem;">
        <div style="width: 64px; height: 64px; border-radius: 50%; background: linear-gradient(135deg, #eab308, #ca8a04); margin: 0 auto 0.75rem; display: flex; align-items: center; justify-content: center; font-size: 2rem; box-shadow: 0 0 20px rgba(234, 179, 8, 0.4);">
          🎓
        </div>
        <div style="font-size: 0.8rem; font-weight: 800; color: #facc15; text-transform: uppercase; letter-spacing: 0.15em; margin-bottom: 0.25rem;">
          SKILLPULSE PLATFORM MILESTONE
        </div>
        <h2 style="font-family: var(--font-heading); font-size: 1.85rem; font-weight: 800; color: #ffffff; margin: 0;">
          MICRO-CREDENTIAL ACHIEVEMENT
        </h2>
        <div style="font-size: 0.85rem; color: var(--text-dim); margin-top: 0.25rem;">
          Unique Credential ID: <b style="color: var(--primary); font-family: monospace;">${c.credential_id}</b>
        </div>
      </div>

      <!-- Recipient Presentation -->
      <div style="text-align: center; margin-bottom: 1.5rem;">
        <div style="font-size: 0.85rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em;">This is presented to</div>
        <h3 style="font-family: var(--font-heading); font-size: 1.65rem; font-weight: 800; color: #ffffff; margin: 0.35rem 0 0.2rem 0;">
          ${c.user_name}
        </h3>
        <p style="font-size: 0.9rem; color: #cbd5e1; max-width: 620px; margin: 0 auto;">
          for demonstrating verified technical competency in
        </p>
        <div style="display: inline-block; background: rgba(99, 102, 241, 0.15); border: 1px solid rgba(99, 102, 241, 0.4); padding: 0.5rem 1.25rem; border-radius: 999px; margin-top: 0.6rem;">
          <span style="font-size: 1.15rem; font-weight: 800; color: #ffffff;">${c.title}</span>
        </div>
      </div>

      <!-- Credential Breakdown Grid -->
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; background: rgba(15, 23, 42, 0.7); padding: 1.25rem; border-radius: var(--radius-md); border: 1px solid var(--border-subtle); margin-bottom: 1.5rem;">
        <div>
          <div style="font-size: 0.75rem; color: var(--text-dim); text-transform: uppercase;">Associated Skill</div>
          <div style="font-size: 0.95rem; font-weight: 700; color: #ffffff; margin-top: 0.2rem;">${c.skill}</div>
        </div>
        <div>
          <div style="font-size: 0.75rem; color: var(--text-dim); text-transform: uppercase;">Credential Level</div>
          <div style="font-size: 0.95rem; font-weight: 700; color: #38bdf8; margin-top: 0.2rem;">${c.level}</div>
        </div>
        <div>
          <div style="font-size: 0.75rem; color: var(--text-dim); text-transform: uppercase;">Assessment Score</div>
          <div style="font-size: 0.95rem; font-weight: 700; color: #4ade80; margin-top: 0.2rem;">${c.assessment_score}% Verified</div>
        </div>
        <div>
          <div style="font-size: 0.75rem; color: var(--text-dim); text-transform: uppercase;">Completion Date</div>
          <div style="font-size: 0.95rem; font-weight: 700; color: #facc15; margin-top: 0.2rem;">${c.issue_date || 'In Progress'}</div>
        </div>
      </div>

      <!-- Practical Project Deliverable -->
      <div style="background: rgba(15, 23, 42, 0.5); padding: 1rem 1.25rem; border-radius: var(--radius-md); border: 1px solid var(--border-subtle); margin-bottom: 1.5rem;">
        <h5 style="font-size: 0.85rem; font-weight: 700; color: #ffffff; margin: 0 0 0.35rem 0;">Verified Practical Project Deliverable:</h5>
        <p style="font-size: 0.85rem; color: var(--text-muted); line-height: 1.5; margin: 0;">
          ${c.practical_task}
        </p>
      </div>

      <!-- Mandatory Non-Accreditation Notice on Certificate -->
      <div style="background: rgba(42, 30, 15, 0.6); border: 1px solid rgba(234, 179, 8, 0.3); border-radius: var(--radius-md); padding: 0.85rem 1rem; margin-bottom: 1.5rem;">
        <div style="font-size: 0.78rem; font-weight: 700; color: #facc15; margin-bottom: 0.2rem;">
          ⚖️ Platform-Generated Non-Accredited Milestone:
        </div>
        <div style="font-size: 0.78rem; color: #cbd5e1; line-height: 1.45;">
          ${c.accreditation_disclaimer}
        </div>
      </div>

      <!-- Public Verification Bar & Actions -->
      <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;">
        <div style="font-size: 0.8rem; color: var(--text-dim);">
          Status: <b style="color: #4ade80;">${c.verification_status}</b>
        </div>
        <div style="display: flex; gap: 0.6rem;">
          <button type="button" class="btn btn-secondary btn-sm" onclick="Credentials.verifyPublicOnline('${c.credential_id}')">
            Verify Online ↗
          </button>
          <button type="button" class="btn btn-primary btn-sm" onclick="window.print()">
            Print / Save Evidence
          </button>
          <button type="button" class="btn btn-secondary btn-sm" onclick="Credentials.closeCredentialModal()">
            Close
          </button>
        </div>
      </div>
    `;

    modal.classList.add('show');
  },

  closeCredentialModal() {
    const modal = document.getElementById('credential-certificate-modal');
    if (modal) modal.classList.remove('show');
  },

  async verifyPublicOnline(credId) {
    App.showToast(`Verifying digital record ${credId} against public registry...`, "info");
    try {
      const res = await API.verifyCredentialPublic(credId);
      if (res.success && res.verification && res.verification.verified) {
        const v = res.verification;
        App.showToast(`✓ VERIFIED: ${v.credential_title} issued to ${v.recipient_name} (${v.status})`, "success");
      } else {
        App.showToast(`Verification failed: ${res.verification?.message || 'Invalid record'}`, "error");
      }
    } catch (err) {
      App.showToast(`Verification error: ${err.message}`, "error");
    }
  },

  async claimCredential(credId) {
    App.showToast(`Claiming digital micro-credential ${credId}...`, "info");
    try {
      const res = await API.claimCredential(credId);
      if (res.success) {
        App.showToast(res.message || "Micro-credential successfully earned!", "success");
        await this.loadCredentials();
      }
    } catch (err) {
      App.showToast(`Claim failed: ${err.message}`, "error");
    }
  }
};

// Explicitly attach to window
window.Credentials = Credentials;
