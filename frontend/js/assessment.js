/**
 * Module 2: User Skill Assessment & Verification Subsystem Controller
 */
const Assessment = {
  sessionToken: null,
  currentSkill: 'Python',
  totalSecondsRemaining: 90 * 60, // 90 minutes
  timerInterval: null,

  questions: [], // 50 MCQs + 2 Coding = 52 total
  currentIndex: 0,
  answers: {}, // question_num -> { selected_option: int, submitted_code: str }
  flaggedQuestions: new Set(),
  activeFilter: 'all', // 'all', 'mcq', 'coding', 'flagged'

  launchForSkill(skillName) {
    this.currentSkill = skillName || 'Python';
    const skillSelect = document.getElementById('select-assessment-skill');
    if (skillSelect) skillSelect.value = this.currentSkill;
    App.goToStep(2);
    this.startSession(this.currentSkill);
  },

  async startSession(skillName = null) {
    if (!API.getToken()) {
      Auth.openModal();
      App.showToast("Please sign in first to launch your assessment.", "warning");
      const container = document.getElementById('question-detail-container');
      if (container) {
        container.innerHTML = `
          <div style="text-align: center; padding: 3rem;">
            <div style="font-size: 2.5rem; margin-bottom: 0.75rem;">🔒</div>
            <h3 style="margin-bottom: 0.5rem;">Authentication Required</h3>
            <p style="color: var(--text-muted); margin-bottom: 1.25rem;">Please sign in to take the 90-minute skill verification assessment.</p>
            <button type="button" class="btn btn-primary" onclick="Auth.openModal()">Sign In ➔</button>
          </div>
        `;
      }
      return;
    }

    const skillToTest = skillName || this.currentSkill || (document.getElementById('select-assessment-skill')?.value) || 'Python';
    this.currentSkill = skillToTest;

    const container = document.getElementById('question-detail-container');
    if (container) {
      container.innerHTML = `
        <div style="text-align: center; padding: 3rem; color: var(--text-muted);">
          <div style="font-size: 2rem; margin-bottom: 0.5rem;">⏳</div>
          <p>Loading assessment questions for ${skillToTest}...</p>
        </div>
      `;
    }

    try {
      App.showToast(`Provisioning 90-Minute Assessment for ${skillToTest}...`, "info");
      const data = await API.request('/api/assessment/start', {
        method: 'POST',
        body: JSON.stringify({ skill_name: skillToTest })
      });

      this.sessionToken = data.session_token;
      this.currentSkill = data.skill_name || skillToTest;

      // Exactly 50 MCQs + 2 Coding questions = 52 total
      const mcqs = Array.isArray(data.mcqs) ? data.mcqs : [];
      const coding = Array.isArray(data.coding_questions) ? data.coding_questions : [];
      this.questions = [...mcqs, ...coding].sort((a, b) => a.question_num - b.question_num);
      this.answers = data.saved_answers || {};
      this.currentIndex = 0;
      this.flaggedQuestions.clear();

      // Update skill badge in UI
      const skillBadge = document.getElementById('assessment-skill-badge');
      if (skillBadge) {
        skillBadge.textContent = `Skill: ${this.currentSkill}`;
      }

      // Start 90-minute Countdown Timer (persisting across MCQ & Coding)
      const durationSecs = (data.duration_minutes || 90) * 60;
      this.startTimer(durationSecs);

      // Activate Anti-Cheating Integrity Monitor
      if (window.IntegrityMonitor && typeof IntegrityMonitor.start === 'function') {
        IntegrityMonitor.start(this.sessionToken);
      }

      // Render Matrix & Current Question (Question 1)
      this.renderQuestionMatrix();
      this.renderCurrentQuestion();
      this.updateProgressCounter();

      App.showToast(`Assessment started! 90-minute timer running for ${this.currentSkill}.`, "success");
    } catch (err) {
      console.error("Failed to start assessment:", err);
      App.showToast("Failed to start assessment: " + err.message, "error");
      if (container) {
        container.innerHTML = `
          <div style="text-align: center; padding: 3rem;">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">⚠️</div>
            <h4 style="color: #ef4444; margin-bottom: 0.5rem;">Failed to load questions</h4>
            <p style="color: var(--text-muted); font-size: 0.85rem; margin-bottom: 1.25rem;">${err.message}</p>
            <button type="button" class="btn btn-primary" onclick="Assessment.startSession('${skillToTest}')">
              ↺ Retry Loading
            </button>
          </div>
        `;
      }
    }
  },

  startTimer(totalSeconds) {
    if (this.timerInterval) clearInterval(this.timerInterval);
    this.totalSecondsRemaining = totalSeconds;

    const updateClock = () => {
      if (this.totalSecondsRemaining <= 0) {
        clearInterval(this.timerInterval);
        this.onTimerExpired();
        return;
      }

      this.totalSecondsRemaining--;

      const hrs = Math.floor(this.totalSecondsRemaining / 3600);
      const mins = Math.floor((this.totalSecondsRemaining % 3600) / 60);
      const secs = this.totalSecondsRemaining % 60;

      const pad = (n) => String(n).padStart(2, '0');
      const timeStr = `${pad(hrs)}:${pad(mins)}:${pad(secs)}`;

      const timerEl = document.getElementById('assessment-timer');
      const timerBox = document.getElementById('timer-box-container');

      if (timerEl) timerEl.textContent = timeStr;

      if (timerBox) {
        if (this.totalSecondsRemaining <= 300) { // < 5 mins
          timerBox.className = 'timer-box timer-critical';
        } else if (this.totalSecondsRemaining <= 900) { // < 15 mins
          timerBox.className = 'timer-box timer-warning';
        } else {
          timerBox.className = 'timer-box';
        }
      }
    };

    updateClock();
    this.timerInterval = setInterval(updateClock, 1000);
  },

  onTimerExpired() {
    App.showToast("⏰ 90-Minute time limit reached! Automatically submitting and evaluating your assessment...", "warning");
    this.submitAssessment(true);
  },

  renderQuestionMatrix() {
    const matrixEl = document.getElementById('question-matrix-grid');
    if (!matrixEl) return;

    matrixEl.innerHTML = this.questions.map((q, idx) => {
      const qNum = q.question_num;
      const isCoding = q.type === 'coding';
      const isAnswered = this.isAnswered(qNum);
      const isActive = idx === this.currentIndex;
      const isFlagged = this.flaggedQuestions.has(qNum);

      let classes = ['matrix-btn'];
      if (isCoding) classes.push('coding');
      if (isAnswered) classes.push('answered');
      if (isActive) classes.push('active');
      if (isFlagged) classes.push('flagged');

      let isVisible = true;
      if (this.activeFilter === 'mcq' && isCoding) isVisible = false;
      if (this.activeFilter === 'coding' && !isCoding) isVisible = false;
      if (this.activeFilter === 'flagged' && !isFlagged) isVisible = false;

      return `
        <button type="button" 
          class="${classes.join(' ')}" 
          style="${isVisible ? '' : 'display: none;'}"
          onclick="Assessment.goToQuestion(${idx})"
          title="Question ${qNum} (${q.topic || q.skill})">
          ${qNum}
        </button>
      `;
    }).join('');
  },

  setFilter(filterName) {
    this.activeFilter = filterName;
    document.querySelectorAll('.nav-tab-btn').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.filter === filterName);
    });
    this.renderQuestionMatrix();
  },

  isAnswered(qNum) {
    const ans = this.answers[String(qNum)];
    if (!ans) return false;
    if (ans.selected_option !== undefined && ans.selected_option !== null) return true;
    if (ans.submitted_code && ans.submitted_code.trim()) return true;
    return false;
  },

  goToQuestion(index) {
    if (index < 0 || index >= this.questions.length) return;
    this.currentIndex = index;
    this.renderCurrentQuestion();
    this.renderQuestionMatrix();
  },

  renderCurrentQuestion() {
    const container = document.getElementById('question-detail-container');
    if (!container) return;

    const q = this.questions[this.currentIndex];
    if (!q) {
      container.innerHTML = `
        <div style="text-align: center; padding: 3rem; color: var(--text-muted);">
          <div style="font-size: 2rem; margin-bottom: 0.5rem;">📝</div>
          <h4>No questions loaded</h4>
          <p style="font-size: 0.85rem; margin-top: 0.4rem;">Please start the assessment to load questions.</p>
          <button type="button" class="btn btn-primary" style="margin-top: 1rem;" onclick="Assessment.startSession()">
            Start Assessment ➔
          </button>
        </div>
      `;
      return;
    }

    const isCoding = q.type === 'coding';
    const qNum = q.question_num;
    const currentAnswer = this.answers[String(qNum)] || {};
    const isFlagged = this.flaggedQuestions.has(qNum);

    const difficultyBadgeClass =
      q.difficulty === 'Hard' ? 'badge-critical' :
        q.difficulty === 'Medium' ? 'badge-surging' : 'badge-primary';

    let contentHtml = '';

    if (!isCoding) {
      // 50 MCQs Render (Options A, B, C, D)
      const optionsHtml = (q.options || []).map((opt, optIdx) => {
        const isSelected = currentAnswer.selected_option === optIdx;
        const letter = String.fromCharCode(65 + optIdx); // A, B, C, D
        return `
          <div class="mcq-option-card ${isSelected ? 'selected' : ''}" onclick="Assessment.selectMCQOption(${qNum}, ${optIdx})">
            <div class="mcq-key-pill">${letter}</div>
            <div class="mcq-text">${opt}</div>
          </div>
        `;
      }).join('');

      contentHtml = `
        <div class="mcq-options-container">
          ${optionsHtml}
        </div>
      `;
    } else {
      // 2 Programming Challenges Render
      const userCode = currentAnswer.submitted_code || q.code_template;
      const visibleTestCasesHtml = (q.visible_test_cases || []).map((tc, tcIdx) => {
        return `
          <div class="test-case-item">
            <span>Sample #${tcIdx + 1} Input: <code>${JSON.stringify(tc.input)}</code></span>
            <span>Expected: <code>${JSON.stringify(tc.expected)}</code></span>
          </div>
        `;
      }).join('');

      contentHtml = `
        <div class="coding-ide-container">
          <div class="problem-statement-box" style="white-space: pre-wrap; font-size: 0.92rem; line-height: 1.6; color: #e2e8f0; background: rgba(15, 23, 42, 0.6); padding: 1.25rem; border-radius: var(--radius-md); border: 1px solid var(--border-subtle);">
<b>Problem Statement:</b>
${q.problem_statement}

${q.input_format ? `<b>Input Format:</b>\n${q.input_format}\n` : ''}
${q.output_format ? `<b>Output Format:</b>\n${q.output_format}\n` : ''}
${q.constraints ? `<b>Constraints:</b>\n${q.constraints}` : ''}
          </div>
          
          <div style="margin-top: 1rem;">
            <div style="font-size: 0.82rem; font-weight: 600; color: var(--text-muted); margin-bottom: 0.4rem;">
              Sample Test Cases (Visible in Test Suite):
            </div>
            ${visibleTestCasesHtml}
          </div>

          <div style="margin-top: 1rem;">
            <div class="code-editor-header">
              <span><b>${this.currentSkill}</b> • Function: <code>${q.function_name || 'solution'}</code></span>
              <span>Sandboxed Execution Engine</span>
            </div>
            <textarea id="code-editor" class="code-editor-textarea" spellcheck="false">${userCode}</textarea>
          </div>

          <div class="code-actions-bar" style="display: flex; justify-content: space-between; align-items: center; margin-top: 0.85rem;">
            <button type="button" class="btn btn-secondary btn-sm" onclick="Assessment.resetCodeToTemplate()">
              ↺ Reset Starter Code
            </button>
            <div style="display: flex; gap: 0.75rem;">
              <button type="button" id="btn-run-code" class="btn btn-secondary" onclick="Assessment.runCode()">
                ▶ Run Code (Visible Tests)
              </button>
              <button type="button" class="btn btn-primary" onclick="Assessment.saveAndContinue(${qNum})">
                Save Code & Next ➔
              </button>
            </div>
          </div>

          <div id="test-output-panel" style="display: none; margin-top: 1rem;" class="test-cases-output-panel"></div>
        </div>
      `;
    }

    container.innerHTML = `
      <div class="q-header-meta">
        <div style="display: flex; align-items: center; gap: 0.6rem; flex-wrap: wrap;">
          <span class="badge badge-primary">${this.currentSkill}</span>
          <span class="q-domain-pill">${q.topic || 'Core'}</span>
          <span class="badge ${difficultyBadgeClass}">${q.difficulty}</span>
        </div>
        <span style="font-size: 0.85rem; font-weight: 600; color: var(--text-muted);">
          Question <b>${this.currentIndex + 1}</b> of <b>${this.questions.length}</b>
        </span>
      </div>

      <div class="q-text" style="user-select: none;">
        ${isCoding ? `<b>Challenge ${qNum - 50}: ${q.title || ''}</b>` : `<b>Q${qNum}.</b> ${q.question_text}`}
      </div>

      ${contentHtml}

      <div class="q-footer-actions">
        <div style="display: flex; gap: 0.6rem;">
          <button type="button" class="btn btn-secondary btn-sm" onclick="Assessment.toggleFlag(${qNum})">
            ${isFlagged ? '★ Flagged' : '☆ Flag for Review'}
          </button>
          ${!isCoding ? `
            <button type="button" class="btn btn-secondary btn-sm" onclick="Assessment.clearAnswer(${qNum})">
              Clear Choice
            </button>
          ` : ''}
        </div>

        <div style="display: flex; gap: 0.75rem;">
          <button type="button" class="btn btn-secondary" onclick="Assessment.previousQuestion()" ${this.currentIndex === 0 ? 'disabled' : ''}>
            ◀ Previous
          </button>
          <button type="button" class="btn btn-primary" onclick="Assessment.nextQuestion()" ${this.currentIndex === this.questions.length - 1 ? 'disabled' : ''}>
            Next ▶
          </button>
        </div>
      </div>
    `;

    // Enable Tab key inside textarea
    if (isCoding) {
      const codeEditor = document.getElementById('code-editor');
      if (codeEditor) {
        codeEditor.addEventListener('keydown', function (e) {
          if (e.key === 'Tab') {
            e.preventDefault();
            const start = this.selectionStart;
            const end = this.selectionEnd;
            this.value = this.value.substring(0, start) + "    " + this.value.substring(end);
            this.selectionStart = this.selectionEnd = start + 4;
          }
        });

        codeEditor.addEventListener('input', () => {
          this.saveCodingAnswer(qNum, codeEditor.value);
        });
      }
    }
  },

  async selectMCQOption(qNum, optionIdx) {
    if (!this.answers[String(qNum)]) {
      this.answers[String(qNum)] = {};
    }
    this.answers[String(qNum)].selected_option = optionIdx;

    this.renderCurrentQuestion();
    this.renderQuestionMatrix();
    this.updateProgressCounter();

    // Asynchronously save to backend
    try {
      await API.request('/api/assessment/save-answer', {
        method: 'POST',
        body: JSON.stringify({
          session_token: this.sessionToken,
          question_num: qNum,
          selected_option: optionIdx
        })
      });
    } catch (err) {
      console.warn("Could not save MCQ answer:", err);
    }
  },

  saveCodingAnswer(qNum, code) {
    if (!this.answers[String(qNum)]) {
      this.answers[String(qNum)] = {};
    }
    this.answers[String(qNum)].submitted_code = code;
    this.renderQuestionMatrix();
    this.updateProgressCounter();

    clearTimeout(this.codeSaveTimeout);
    this.codeSaveTimeout = setTimeout(async () => {
      try {
        await API.request('/api/assessment/save-answer', {
          method: 'POST',
          body: JSON.stringify({
            session_token: this.sessionToken,
            question_num: qNum,
            submitted_code: code
          })
        });
      } catch (err) {
        console.warn("Could not save coding answer:", err);
      }
    }, 800);
  },

  async saveAndContinue(qNum) {
    const codeEditor = document.getElementById('code-editor');
    if (codeEditor) {
      this.saveCodingAnswer(qNum, codeEditor.value);
    }
    App.showToast("Code saved successfully!", "success");
    this.nextQuestion();
  },

  async runCode() {
    const q = this.questions[this.currentIndex];
    if (q.type !== 'coding') return;

    const codeEditor = document.getElementById('code-editor');
    const code = codeEditor ? codeEditor.value : '';
    const outputPanel = document.getElementById('test-output-panel');
    const runBtn = document.getElementById('btn-run-code');

    if (runBtn) runBtn.textContent = '⏳ Executing in Sandbox...';
    if (outputPanel) {
      outputPanel.style.display = 'block';
      outputPanel.innerHTML = `<div style="color: #38bdf8;">Running visible test cases against ${this.currentSkill} sandbox...</div>`;
    }

    try {
      const res = await API.request('/api/assessment/run-code', {
        method: 'POST',
        body: JSON.stringify({
          session_token: this.sessionToken,
          question_num: q.question_num,
          code: code
        })
      });

      if (res.error) {
        outputPanel.innerHTML = `
          <div style="color: #f87171; font-weight: 600; margin-bottom: 0.4rem;">Execution Error:</div>
          <pre style="color: #fca5a5; font-size: 0.8rem; white-space: pre-wrap;">${res.error}</pre>
        `;
      } else {
        const testsHtml = (res.results || []).map(r => `
          <div class="test-case-item ${r.passed ? 'pass' : 'fail'}" style="margin-bottom: 0.4rem; padding: 0.6rem; border-radius: var(--radius-sm); background: ${r.passed ? 'rgba(16, 185, 129, 0.1)' : 'rgba(239, 68, 68, 0.1)'}; border: 1px solid ${r.passed ? 'rgba(16, 185, 129, 0.3)' : 'rgba(239, 68, 68, 0.3)'};">
            <div style="font-weight: 700; color: ${r.passed ? '#34d399' : '#f87171'};">
              Sample #${r.test_index}: ${r.passed ? '✓ PASSED' : '✕ FAILED'}
            </div>
            <div style="font-size: 0.78rem; color: var(--text-dim); margin-top: 0.2rem;">
              Input: <code>${JSON.stringify(r.input)}</code> | Expected: <code>${JSON.stringify(r.expected)}</code>
              ${!r.passed ? ` | Actual: <code>${JSON.stringify(r.actual)}</code>` : ''}
              ${r.error ? ` | <span style="color: #fca5a5;">${r.error}</span>` : ''}
            </div>
          </div>
        `).join('');

        outputPanel.innerHTML = `
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.6rem;">
            <span style="font-weight: 700; color: ${res.all_passed ? '#34d399' : '#f87171'};">
              ${res.all_passed ? '✓ All Visible Tests Passed!' : `Passed ${res.passed_count} of ${res.total_count} Tests`}
            </span>
            <span style="font-size: 0.75rem; color: var(--text-dim);">Execution Time: ${res.execution_time_ms}ms</span>
          </div>
          ${testsHtml}
        `;
      }
    } catch (err) {
      if (outputPanel) {
        outputPanel.innerHTML = `<div style="color: #f87171;">Execution failed: ${err.message}</div>`;
      }
    } finally {
      if (runBtn) runBtn.textContent = '▶ Run Code (Visible Tests)';
    }
  },

  resetCodeToTemplate() {
    const q = this.questions[this.currentIndex];
    if (q.type === 'coding') {
      const codeEditor = document.getElementById('code-editor');
      if (codeEditor) {
        codeEditor.value = q.code_template;
        this.saveCodingAnswer(q.question_num, q.code_template);
        App.showToast("Starter code reset to template.", "info");
      }
    }
  },

  toggleFlag(qNum) {
    if (this.flaggedQuestions.has(qNum)) {
      this.flaggedQuestions.delete(qNum);
      App.showToast(`Removed flag from Q${qNum}.`, "info");
    } else {
      this.flaggedQuestions.add(qNum);
      App.showToast(`Flagged Q${qNum} for review.`, "info");
    }
    this.renderCurrentQuestion();
    this.renderQuestionMatrix();
  },

  clearAnswer(qNum) {
    if (this.answers[String(qNum)]) {
      delete this.answers[String(qNum)].selected_option;
    }
    this.renderCurrentQuestion();
    this.renderQuestionMatrix();
    this.updateProgressCounter();
  },

  nextQuestion() {
    if (this.currentIndex < this.questions.length - 1) {
      this.goToQuestion(this.currentIndex + 1);
    }
  },

  previousQuestion() {
    if (this.currentIndex > 0) {
      this.goToQuestion(this.currentIndex - 1);
    }
  },

  updateProgressCounter() {
    const count = Object.keys(this.answers).filter(k => this.isAnswered(k)).length;
    const progressEl = document.getElementById('assessment-progress-count');
    if (progressEl) {
      progressEl.textContent = `${count} / ${this.questions.length}`;
    }
  },

  async submitAssessment(forced = false) {
    const answeredCount = Object.keys(this.answers).filter(k => this.isAnswered(k)).length;
    const totalCount = this.questions.length;

    if (!forced) {
      const confirmMsg = `Are you sure you want to finish your assessment?\n\nAnswered: ${answeredCount} / ${totalCount} questions.\nYour score will be securely graded on the backend and your Verified Skill Profile generated.`;
      if (!confirm(confirmMsg)) return;
    }

    clearInterval(this.timerInterval);
    IntegrityMonitor.stop();

    App.showToast("Securely evaluating 50 MCQs & running coding test suites...", "info");

    try {
      const res = await API.request('/api/assessment/complete', {
        method: 'POST',
        body: JSON.stringify({
          session_token: this.sessionToken,
        }),
      });

      App.showToast("Module 2 Assessment evaluated successfully!", "success");
      App.markStepCompleted(2);

      // Cache results and render Step 3: Verified Skill Profile with complete breakdown
      this.lastVerifiedResults = res.results;
      this.renderVerifiedSkillProfile(res.results);

      // Transition view to Step 3
      App.goToStep(3);
    } catch (err) {
      App.showToast("Error completing assessment: " + err.message, "error");
    }
  },

  async loadVerifiedProfile(skillName = null) {
    const container = document.getElementById('verified-profile-container');
    if (!container) return;

    if (skillName) {
      this.currentSkill = skillName;
    }

    const targetSkill = skillName || this.currentSkill || '';

    if (this.lastVerifiedResults && (!targetSkill || (this.lastVerifiedResults.skill_name && this.lastVerifiedResults.skill_name.toLowerCase() === targetSkill.toLowerCase()))) {
      this.renderVerifiedSkillProfile(this.lastVerifiedResults);
      return;
    }

    try {
      const data = await API.getVerifiedProfile(targetSkill);
      if (data && data.has_verified_profile && data.profile) {
        this.lastVerifiedResults = data.profile;
        this.renderVerifiedSkillProfile(data.profile);
      } else {
        container.innerHTML = `
          <div class="glass-card" style="text-align: center; padding: 3.5rem 2rem;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">🏅</div>
            <h3 style="font-family: var(--font-heading); font-size: 1.5rem; color: #ffffff; margin-bottom: 0.5rem;">
              No Verified Skill Profile Yet
            </h3>
            <p style="color: var(--text-muted); max-width: 540px; margin: 0 auto 1.5rem; font-size: 0.92rem; line-height: 1.6;">
              Please complete your 90-minute assessment (50 MCQs + 2 Coding Problems) to empirically verify your declared technical skills.
            </p>
            <button type="button" class="btn btn-primary" onclick="App.goToStep(1)">
              Review Declared Skills in Career Profile ➔
            </button>
          </div>
        `;
      }
    } catch (err) {
      console.warn("Could not load verified profile:", err);
    }
  },

  renderVerifiedSkillProfile(results) {
    const container = document.getElementById('verified-profile-container');
    if (!container) return;

    const skillName = results.skill_name || this.currentSkill || 'Python';
    const overallScore = results.overall_total_pct !== undefined ? results.overall_total_pct : (results.overall_score_pct || 0);
    const profLevel = results.proficiency_level || 'Beginner';
    const declaredLvl = results.declared_skill?.declared_level || results.declared_level || 'Not Declared';
    const comparison = results.comparison || {
      declared_level: declaredLvl,
      verified_level: profLevel,
      status: 'unrated',
      label: `Verified as ${profLevel}`
    };

    // 5-Tier Proficiency Badge Styles:
    // 0-39: Beginner, 40-59: Basic, 60-74: Intermediate, 75-89: Advanced, 90-100: Expert
    const profBadge =
      profLevel === 'Expert' ? 'badge-critical' :
        profLevel === 'Advanced' ? 'badge-primary' :
          profLevel === 'Intermediate' ? 'badge-surging' :
            profLevel === 'Basic' ? 'badge-warning' : 'badge-secondary';

    // Build Topic-wise Score Bars
    const topicScores = results.topic_scores || {};
    const topicHtml = Object.keys(topicScores).map(topicName => {
      const stat = topicScores[topicName];
      const isGood = stat.percentage >= 70;
      return `
        <div style="margin-bottom: 0.85rem;">
          <div style="display: flex; justify-content: space-between; font-size: 0.85rem; margin-bottom: 0.3rem;">
            <span style="font-weight: 600; color: #ffffff;">${topicName}</span>
            <span style="color: var(--text-dim);">${stat.correct} / ${stat.total} (${stat.percentage}%)</span>
          </div>
          <div style="height: 6px; background: rgba(255, 255, 255, 0.08); border-radius: 999px; overflow: hidden;">
            <div style="width: ${stat.percentage}%; height: 100%; background: ${isGood ? 'linear-gradient(90deg, #10b981, #38bdf8)' : 'linear-gradient(90deg, #f59e0b, #ef4444)'}; border-radius: 999px;"></div>
          </div>
        </div>
      `;
    }).join('');

    // Build Strengths & Weaknesses Pill Lists
    const strengths = results.strengths || [];
    const weaknesses = results.weaknesses || [];

    const strengthsHtml = strengths.length > 0 ? strengths.map(s => `
      <div style="display: flex; align-items: center; justify-content: space-between; padding: 0.6rem 0.85rem; background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.25); border-radius: var(--radius-sm); margin-bottom: 0.4rem;">
        <div style="display: flex; align-items: center; gap: 0.5rem;">
          <span style="color: #10b981;">✓</span>
          <span style="font-weight: 600; font-size: 0.85rem; color: #ffffff;">${s.topic}</span>
        </div>
        <span style="font-size: 0.8rem; color: #6ee7b7; font-weight: 700;">${s.correct}/${s.total} (${s.percentage}%)</span>
      </div>
    `).join('') : '<p style="color: var(--text-dim); font-size: 0.85rem; margin: 0.5rem 0;">No topics reached the 70% threshold yet. Focus on foundational practice.</p>';

    const weaknessesHtml = weaknesses.length > 0 ? weaknesses.map(w => `
      <div style="display: flex; align-items: center; justify-content: space-between; padding: 0.6rem 0.85rem; background: rgba(239, 68, 68, 0.08); border: 1px solid rgba(239, 68, 68, 0.2); border-radius: var(--radius-sm); margin-bottom: 0.4rem;">
        <div style="display: flex; align-items: center; gap: 0.5rem;">
          <span style="color: #ef4444;">⚠</span>
          <span style="font-weight: 600; font-size: 0.85rem; color: #ffffff;">${w.topic}</span>
        </div>
        <span style="font-size: 0.8rem; color: #fca5a5; font-weight: 700;">${w.correct}/${w.total} (${w.percentage}%)</span>
      </div>
    `).join('') : '<p style="color: var(--text-dim); font-size: 0.85rem; margin: 0.5rem 0;">Outstanding! All evaluated topics achieved &ge; 70% mastery.</p>';

    // Build Difficulty-wise Breakdown
    const diffScores = results.difficulty_scores || {};
    const diffHtml = ['Easy', 'Medium', 'Hard'].filter(d => diffScores[d]).map(diff => {
      const stat = diffScores[diff];
      const color = diff === 'Easy' ? '#10b981' : diff === 'Medium' ? '#f59e0b' : '#ef4444';
      return `
        <div class="glass-card" style="text-align: center; padding: 1rem;">
          <div style="font-size: 0.78rem; text-transform: uppercase; color: ${color}; font-weight: 700;">${diff} Difficulty</div>
          <div style="font-size: 1.6rem; font-weight: 800; color: #ffffff; margin: 0.25rem 0;">${stat.percentage}%</div>
          <div style="font-size: 0.72rem; color: var(--text-dim);">${stat.correct} of ${stat.total} Correct</div>
        </div>
      `;
    }).join('');

    // Build Programming Details Breakdown
    const progDetails = results.programming_details || results.programming_performance?.challenges || [];
    const progHtml = progDetails.map(pd => {
      return `
        <div class="glass-card" style="margin-bottom: 0.75rem; padding: 1rem; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;">
          <div>
            <div style="font-weight: 700; font-size: 0.95rem; color: #ffffff;">Challenge #${pd.question_num ? pd.question_num - 50 : 1}: ${pd.title}</div>
            <div style="font-size: 0.75rem; color: var(--text-dim); margin-top: 0.2rem;">
              Test Cases: <b>${pd.test_cases_passed} / ${pd.total_test_cases} passed</b> • Execution: ${pd.execution_time_ms || 0}ms
            </div>
          </div>
          <div style="display: flex; align-items: center; gap: 0.75rem;">
            <div style="font-family: var(--font-mono); font-size: 1.1rem; font-weight: 700; color: #38bdf8;">
              ${pd.score_awarded} / ${pd.max_score || 10.0} pts
            </div>
            <span class="badge ${pd.all_passed ? 'badge-success' : 'badge-secondary'}">
              ${pd.all_passed ? 'All Passed' : 'Partial'}
            </span>
          </div>
        </div>
      `;
    }).join('');

    const mcqScore = results.mcq_score !== undefined ? results.mcq_score : (results.mcq_performance?.score || 0);
    const mcqTotal = results.mcq_total !== undefined ? results.mcq_total : (results.mcq_performance?.total || 50);
    const mcqPct = results.mcq_score_pct !== undefined ? results.mcq_score_pct : (results.mcq_performance?.percentage || 0);

    const progScore = results.programming_score !== undefined ? results.programming_score : (results.programming_performance?.score || 0);
    const progMax = results.programming_max !== undefined ? results.programming_max : (results.programming_performance?.total || 20.0);
    const progPct = results.programming_score_pct !== undefined ? results.programming_score_pct : (results.programming_performance?.percentage || 0);

    container.innerHTML = `
      <!-- Top Banner Card -->
      <div class="glass-card" style="background: linear-gradient(135deg, rgba(30, 41, 59, 0.75), rgba(15, 23, 42, 0.85)); margin-bottom: 1.5rem;">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1.5rem;">
          <div>
            <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
              <span class="badge badge-success">MODULE 3: VERIFIED SKILL PROFILE</span>
              <span class="badge ${profBadge}">${profLevel} Level</span>
            </div>
            <h2 style="font-family: var(--font-heading); font-size: 1.85rem; font-weight: 800; color: #ffffff; margin: 0;">
              Verified Skill: ${skillName}
            </h2>
            <p style="color: var(--text-muted); max-width: 780px; margin-top: 0.35rem; font-size: 0.92rem;">
              Empirically evaluated through 50 technical MCQs and 2 sandboxed programming test suites.
              Stored in database for downstream curriculum synthesis.
            </p>
          </div>
          <div style="display: flex; gap: 0.75rem; flex-wrap: wrap;">
            <button class="btn btn-secondary" onclick="Assessment.startSession('${skillName}')">
              Retake Assessment ↺
            </button>
            <button class="btn btn-secondary" onclick="App.goToStep(1)">
              Career Profile
            </button>
            <button class="btn btn-primary" onclick="App.goToStep(4)">
              Proceed to Step 4: Gap Analysis ➔
            </button>
          </div>
        </div>
      </div>

      <!-- User-Declared vs. Assessment-Verified Distinction Cards -->
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1.25rem; margin-bottom: 1.5rem;">
        <!-- Card 1: User-Declared Skill -->
        <div class="glass-card" style="border-left: 4px solid var(--accent-purple); padding: 1.25rem;">
          <div style="font-size: 0.72rem; text-transform: uppercase; color: var(--text-dim); font-weight: 700; letter-spacing: 0.05em; margin-bottom: 0.4rem;">
            👤 User-Declared Skill
          </div>
          <div style="font-size: 1.35rem; font-weight: 800; color: #ffffff;">
            ${skillName}
          </div>
          <div style="margin-top: 0.5rem; display: flex; align-items: center; gap: 0.5rem;">
            <span style="font-size: 0.82rem; color: var(--text-muted);">Self-Rating:</span>
            <span class="badge badge-primary" style="font-size: 0.82rem;">${declaredLvl}</span>
          </div>
          <p style="font-size: 0.75rem; color: var(--text-dim); margin-top: 0.5rem; margin-bottom: 0;">
            Captured from candidate self-declaration in Career Profile.
          </p>
        </div>

        <!-- Card 2: Assessment-Verified Skill -->
        <div class="glass-card" style="border-left: 4px solid var(--accent-cyan); padding: 1.25rem;">
          <div style="font-size: 0.72rem; text-transform: uppercase; color: var(--text-dim); font-weight: 700; letter-spacing: 0.05em; margin-bottom: 0.4rem;">
            🏅 Assessment-Verified Skill
          </div>
          <div style="font-size: 1.35rem; font-weight: 800; color: #38bdf8;">
            ${overallScore}% Score
          </div>
          <div style="margin-top: 0.5rem; display: flex; align-items: center; gap: 0.5rem;">
            <span style="font-size: 0.82rem; color: var(--text-muted);">Verified Tier:</span>
            <span class="badge ${profBadge}" style="font-size: 0.82rem;">${profLevel}</span>
          </div>
          <p style="font-size: 0.75rem; color: var(--text-dim); margin-top: 0.5rem; margin-bottom: 0;">
            Objectively graded from 50 MCQs & 2 coding challenges.
          </p>
        </div>

        <!-- Card 3: Alignment & Delta -->
        <div class="glass-card" style="border-left: 4px solid #10b981; padding: 1.25rem;">
          <div style="font-size: 0.72rem; text-transform: uppercase; color: var(--text-dim); font-weight: 700; letter-spacing: 0.05em; margin-bottom: 0.4rem;">
            ⚖️ Self-Declaration vs. Verification
          </div>
          <div style="font-size: 1.1rem; font-weight: 700; color: #ffffff; margin-top: 0.25rem;">
            ${comparison.label}
          </div>
          <div style="margin-top: 0.6rem;">
            <span class="badge ${comparison.status === 'exceeded' ? 'badge-success' : comparison.status === 'matched' ? 'badge-primary' : 'badge-secondary'}">
              ${comparison.status === 'exceeded' ? '✓ Outperformed Declared Rating' : comparison.status === 'matched' ? '✓ Accurately Self-Assessed' : '⚠ Skill Gap Identified'}
            </span>
          </div>
        </div>
      </div>

      <!-- Core Score Summary Cards -->
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1.25rem; margin-bottom: 1.5rem;">
        <div class="glass-card" style="text-align: center; padding: 1.5rem;">
          <div style="font-size: 0.82rem; color: var(--text-muted); text-transform: uppercase;">Overall Verified Score</div>
          <div style="font-family: var(--font-heading); font-size: 2.2rem; font-weight: 800; color: #38bdf8; margin: 0.25rem 0;">
            ${overallScore}%
          </div>
          <div><span class="badge ${profBadge}" style="font-size: 0.82rem;">${profLevel}</span></div>
          <div style="font-size: 0.72rem; color: var(--text-dim); margin-top: 0.35rem;">70% MCQ + 30% Coding</div>
        </div>

        <div class="glass-card" style="text-align: center; padding: 1.5rem;">
          <div style="font-size: 0.82rem; color: var(--text-muted); text-transform: uppercase;">MCQ Proficiency (70%)</div>
          <div style="font-family: var(--font-heading); font-size: 2.2rem; font-weight: 800; color: #a5b4fc; margin: 0.25rem 0;">
            ${mcqScore} / ${mcqTotal}
          </div>
          <div style="font-size: 0.75rem; color: var(--text-dim);">${mcqPct}% Accuracy</div>
        </div>

        <div class="glass-card" style="text-align: center; padding: 1.5rem;">
          <div style="font-size: 0.82rem; color: var(--text-muted); text-transform: uppercase;">Programming (30%)</div>
          <div style="font-family: var(--font-heading); font-size: 2.2rem; font-weight: 800; color: #c4b5fd; margin: 0.25rem 0;">
            ${progScore} / ${progMax}
          </div>
          <div style="font-size: 0.75rem; color: var(--text-dim);">${progPct}% Test Suites Passed</div>
        </div>

        <div class="glass-card" style="text-align: center; padding: 1.5rem;">
          <div style="font-size: 0.82rem; color: var(--text-muted); text-transform: uppercase;">Integrity Score</div>
          <div style="font-family: var(--font-heading); font-size: 2.2rem; font-weight: 800; color: ${results.is_flagged ? '#ef4444' : '#10b981'}; margin: 0.25rem 0;">
            ${results.integrity_score !== undefined ? Math.round(results.integrity_score) : 100}%
          </div>
          <div style="font-size: 0.75rem; color: var(--text-dim);">
            ${results.is_flagged ? 'FLAGGED FOR REVIEW' : 'Assessment Clean'}
          </div>
        </div>
      </div>

      <!-- Topic-wise Strengths & Weaknesses Diagnostics -->
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(340px, 1fr)); gap: 1.5rem; margin-bottom: 1.5rem;">
        <!-- Strengths Card -->
        <div class="glass-card" style="background: rgba(16, 185, 129, 0.05); border-color: rgba(16, 185, 129, 0.25);">
          <div class="card-header" style="margin-bottom: 1rem;">
            <h3 style="color: #6ee7b7; margin: 0; font-size: 1.05rem;">🌟 Verified Strengths (&ge; 70%)</h3>
            <span class="badge badge-success">${strengths.length} Topic${strengths.length === 1 ? '' : 's'}</span>
          </div>
          <div>
            ${strengthsHtml}
          </div>
        </div>

        <!-- Weaknesses / Growth Areas Card -->
        <div class="glass-card" style="background: rgba(239, 68, 68, 0.05); border-color: rgba(239, 68, 68, 0.25);">
          <div class="card-header" style="margin-bottom: 1rem;">
            <h3 style="color: #fca5a5; margin: 0; font-size: 1.05rem;">🎯 Growth Areas / Weaknesses (&lt; 70%)</h3>
            <span class="badge" style="background: rgba(239, 68, 68, 0.2); color: #fca5a5; border: 1px solid rgba(239, 68, 68, 0.4);">${weaknesses.length} Topic${weaknesses.length === 1 ? '' : 's'}</span>
          </div>
          <div>
            ${weaknessesHtml}
          </div>
        </div>
      </div>

      <!-- Full Topic-wise Breakdown & Programming Challenge Breakdown -->
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 1.5rem; margin-bottom: 1.5rem;">
        <!-- All Topics -->
        <div class="glass-card">
          <div class="card-header" style="margin-bottom: 1rem;">
            <h3>📊 Comprehensive Topic Breakdown</h3>
            <span class="badge badge-primary">${Object.keys(topicScores).length} Topics</span>
          </div>
          ${topicHtml}
        </div>

        <!-- Difficulty & Programming -->
        <div style="display: flex; flex-direction: column; gap: 1.5rem;">
          <!-- Difficulty Breakdown -->
          <div class="glass-card">
            <div class="card-header" style="margin-bottom: 0.75rem;">
              <h3>🎯 Difficulty-wise Performance</h3>
            </div>
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.75rem;">
              ${diffHtml}
            </div>
          </div>

          <!-- Programming Challenge Breakdown -->
          <div class="glass-card">
            <div class="card-header" style="margin-bottom: 0.75rem;">
              <h3>💻 Programming Challenge Test-Case Metrics</h3>
              <span class="badge badge-primary">${progDetails.length} Challenges</span>
            </div>
            ${progHtml}
          </div>
        </div>
      </div>

      <!-- Database Persistence Verification Card -->
      <div class="glass-card" style="background: rgba(16, 185, 129, 0.08); border-color: rgba(16, 185, 129, 0.3);">
        <div style="display: flex; align-items: center; gap: 1rem;">
          <div style="font-size: 2rem;">💾</div>
          <div>
            <h4 style="color: #6ee7b7; margin-bottom: 0.2rem;">Verified Result Persisted in Database</h4>
            <p style="font-size: 0.85rem; color: var(--text-muted); margin: 0;">
              Verified profile for <b>${skillName}</b> (${overallScore}%, ${profLevel}) has been saved in the <code>verified_skills</code> database table.
              Ready for downstream Module 4 Skill Gap Analysis.
            </p>
          </div>
        </div>
      </div>
    `;
  }
};

// Explicitly attach to window
window.Assessment = Assessment;
