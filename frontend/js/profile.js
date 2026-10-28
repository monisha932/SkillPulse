/**
 * Career Profile & Self-Declared Skills Module (Workflow Steps 2 & 3)
 */
const Profile = {
  selectedRoleId: 'fullstack-dev',
  declaredSkills: [
    { skill_name: 'Python', self_rating: 'Intermediate' },
    { skill_name: 'JavaScript', self_rating: 'Intermediate' },
    { skill_name: 'SQL', self_rating: 'Beginner' },
  ],
  availableRoles: [],

  async init() {
    await this.fetchRoles();
    await this.loadProfile();
    this.bindEvents();
    this.renderDeclaredSkills();
  },

  bindEvents() {
    // Add custom skill button & enter key
    const addSkillBtn = document.getElementById('btn-add-custom-skill');
    const customSkillInput = document.getElementById('input-custom-skill');

    if (addSkillBtn && customSkillInput) {
      addSkillBtn.addEventListener('click', () => {
        this.addSkill(customSkillInput.value);
        customSkillInput.value = '';
      });

      customSkillInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
          e.preventDefault();
          this.addSkill(customSkillInput.value);
          customSkillInput.value = '';
        }
      });
    }

    // Preset chip clicks
    document.querySelectorAll('.preset-chip').forEach((chip) => {
      chip.addEventListener('click', (e) => {
        const skillName = e.currentTarget.dataset.skill;
        this.addSkill(skillName);
      });
    });

    // Save profile button
    const saveProfileBtn = document.getElementById('btn-save-profile');
    if (saveProfileBtn) {
      saveProfileBtn.addEventListener('click', () => this.saveProfile());
    }

    // Start assessment modal trigger
    const startAssessmentBtn = document.getElementById('btn-proceed-assessment');
    if (startAssessmentBtn) {
      startAssessmentBtn.addEventListener('click', () => {
        App.openAssessmentRulesModal();
      });
    }
  },

  async fetchRoles() {
    try {
      const data = await API.getMarketRoles();
      this.availableRoles = data.roles || [];
      this.renderRoleGrid();
    } catch (err) {
      App.showToast('Could not load market roles: ' + err.message, 'error');
    }
  },

  async loadProfile() {
    if (!API.getToken()) return;

    try {
      const res = await API.getProfile();
      if (res.has_profile && res.profile) {
        this.selectedRoleId = res.profile.target_role_id;
        this.declaredSkills = res.profile.declared_skills || [];
        this.verifiedSkills = res.profile.verified_skills || [];

        // Set inputs
        const expEl = document.getElementById('profile-experience');
        const eduEl = document.getElementById('profile-education');
        if (expEl) expEl.value = res.profile.experience_level || 'Fresher';
        if (eduEl) eduEl.value = res.profile.education || 'B.E. Computer Science & Engineering';

        this.highlightSelectedRole();
        this.renderDeclaredSkills();
      }
    } catch (err) {
      console.warn('Profile fetch error:', err);
    }
  },

  renderRoleGrid() {
    const grid = document.getElementById('role-selection-grid');
    if (!grid) return;

    grid.innerHTML = this.availableRoles
      .map((role) => {
        const isSelected = role.role_id === this.selectedRoleId;
        const demandBadgeClass =
          role.demand_status === 'Critical'
            ? 'badge-critical'
            : role.demand_status === 'Surging'
              ? 'badge-surging'
              : 'badge-primary';

        const topSkills = (role.skills || [])
          .slice(0, 4)
          .map((s) => `<span class="mini-skill-tag">${s.skill_name}</span>`)
          .join('');

        return `
        <div class="role-card ${isSelected ? 'selected' : ''}" data-role-id="${role.role_id}">
          <div>
            <div class="role-header">
              <div>
                <div class="role-title">${role.role_title}</div>
                <div class="role-domain">${role.domain}</div>
              </div>
              <span class="badge ${demandBadgeClass}">${role.demand_status} (${role.market_demand_index}%)</span>
            </div>
            <p style="font-size: 0.82rem; color: var(--text-muted); line-height: 1.5;">${role.description}</p>
          </div>
          <div>
            <div class="role-stats">
              <span>Avg Salary: <b>${role.avg_salary}</b></span>
              <span>•</span>
              <span>Global Trend: <b>High Growth</b></span>
            </div>
            <div class="role-skills-preview">
              ${topSkills}
            </div>
          </div>
        </div>
      `;
      })
      .join('');

    // Attach click listeners to role cards
    grid.querySelectorAll('.role-card').forEach((card) => {
      card.addEventListener('click', () => {
        this.selectedRoleId = card.dataset.roleId;
        this.highlightSelectedRole();
        App.showToast(`Target role selected: ${card.querySelector('.role-title').textContent}`, 'success');
      });
    });
  },

  highlightSelectedRole() {
    document.querySelectorAll('.role-card').forEach((card) => {
      if (card.dataset.roleId === this.selectedRoleId) {
        card.classList.add('selected');
      } else {
        card.classList.remove('selected');
      }
    });
  },

  addSkill(name) {
    if (!name || !name.trim()) return;
    const cleanName = name.trim();

    const exists = this.declaredSkills.some(
      (s) => s.skill_name.toLowerCase() === cleanName.toLowerCase()
    );

    if (exists) {
      App.showToast(`Skill "${cleanName}" is already declared.`, 'warning');
      return;
    }

    this.declaredSkills.push({
      skill_name: cleanName,
      self_rating: 'Intermediate',
    });

    this.renderDeclaredSkills();
    App.showToast(`Added "${cleanName}" to declared skills.`, 'success');
  },

  removeSkill(index) {
    const removed = this.declaredSkills[index];
    this.declaredSkills.splice(index, 1);
    this.renderDeclaredSkills();
    if (removed) {
      App.showToast(`Removed "${removed.skill_name}".`, 'info');
    }
  },

  setSkillLevel(index, level) {
    if (this.declaredSkills[index]) {
      this.declaredSkills[index].self_rating = level;
      this.renderDeclaredSkills();
    }
  },

  renderDeclaredSkills() {
    const deck = document.getElementById('declared-skills-deck');
    const countEl = document.getElementById('declared-skills-count');

    if (countEl) {
      countEl.textContent = `${this.declaredSkills.length} Skills Declared`;
    }

    if (!deck) return;

    if (this.declaredSkills.length === 0) {
      deck.innerHTML = `
        <div style="grid-column: 1 / -1; text-align: center; padding: 2rem; color: var(--text-dim);">
          No skills declared yet. Click the preset tags above or type your technical skills to get started.
        </div>
      `;
      return;
    }

    deck.innerHTML = this.declaredSkills
      .map((skill, index) => {
        const isBeg = skill.self_rating === 'Beginner';
        const isInt = skill.self_rating === 'Intermediate';
        const isAdv = skill.self_rating === 'Advanced';

        const verified = (this.verifiedSkills || []).find(
          (v) => v.skill_name.toLowerCase() === skill.skill_name.toLowerCase()
        );

        return `
        <div class="declared-skill-card" style="${verified ? 'border-color: rgba(16, 185, 129, 0.4); background: rgba(16, 185, 129, 0.04);' : ''}">
          <div class="declared-skill-info">
            <div style="display: flex; align-items: center; gap: 0.5rem;">
              <span class="declared-skill-name">${skill.skill_name}</span>
              ${verified ? `<span class="badge badge-success" style="font-size: 0.7rem; padding: 0.15rem 0.45rem;">✓ Verified: ${verified.proficiency_level} (${verified.score_pct}%)</span>` : ''}
            </div>
            <span style="font-size: 0.75rem; color: var(--text-dim); margin-top: 2px;">
              User-Declared: <b>${skill.self_rating}</b> ${verified ? `• Tested Score: <b>${verified.score_pct}%</b>` : '• Not Yet Verified'}
            </span>
          </div>

          <div style="display: flex; align-items: center; gap: 0.75rem;">
            ${verified ? `
              <button type="button" class="btn btn-secondary btn-sm" onclick="Assessment.loadVerifiedProfile('${skill.skill_name}'); App.goToStep(3);" style="font-size: 0.75rem; padding: 0.25rem 0.6rem; color: #38bdf8; border-color: rgba(56, 189, 248, 0.4);" title="View Module 3 verified skill profile">
                View Profile ➔
              </button>
              <button type="button" class="btn btn-secondary btn-sm" onclick="Assessment.launchForSkill('${skill.skill_name}')" style="font-size: 0.75rem; padding: 0.25rem 0.5rem;" title="Retake verification assessment">
                ↺
              </button>
            ` : `
              <button type="button" class="btn btn-secondary btn-sm" onclick="Assessment.launchForSkill('${skill.skill_name}')" style="font-size: 0.75rem; padding: 0.25rem 0.6rem; border-color: var(--primary);" title="Take Module 2 verification assessment for ${skill.skill_name}">
                Verify Skill ➔
              </button>
            `}
            <div class="level-toggle-group">
              <button type="button" class="level-btn ${isBeg ? 'active' : ''}" onclick="Profile.setSkillLevel(${index}, 'Beginner')">Beg</button>
              <button type="button" class="level-btn ${isInt ? 'active' : ''}" onclick="Profile.setSkillLevel(${index}, 'Intermediate')">Int</button>
              <button type="button" class="level-btn ${isAdv ? 'active' : ''}" onclick="Profile.setSkillLevel(${index}, 'Advanced')">Adv</button>
            </div>
            <button type="button" class="btn-remove-skill" onclick="Profile.removeSkill(${index})" title="Remove skill">&times;</button>
          </div>
        </div>
      `;
      })
      .join('');
  },

  async saveProfile() {
    if (!API.getToken()) {
      Auth.openModal();
      App.showToast('Please sign in first to save your profile.', 'warning');
      return;
    }

    if (!this.selectedRoleId) {
      App.showToast('Please select a target job role.', 'warning');
      return;
    }

    if (this.declaredSkills.length === 0) {
      App.showToast('Please declare at least 1 technical skill.', 'warning');
      return;
    }

    const expEl = document.getElementById('profile-experience');
    const eduEl = document.getElementById('profile-education');

    const profileData = {
      target_role_id: this.selectedRoleId,
      experience_level: expEl ? expEl.value : 'Fresher',
      education: eduEl ? eduEl.value : 'B.E. Computer Science & Engineering',
      declared_skills: this.declaredSkills,
    };

    try {
      const res = await API.saveProfile(profileData);
      App.showToast('Career profile & declared skills saved successfully!', 'success');

      // Update stepper
      App.markStepCompleted(1);

      // Open assessment prompt
      App.openAssessmentRulesModal();
    } catch (err) {
      App.showToast(err.message, 'error');
    }
  },
};

// Explicitly attach to window
window.Profile = Profile;
