/**
 * API Service Client for Micro-Credential Curriculum Platform
 */
const API = {
  BASE_URL: '', // Same-origin or empty string for relative paths

  getToken() {
    return localStorage.getItem('s5_auth_token') || '';
  },

  setToken(token) {
    localStorage.setItem('s5_auth_token', token);
  },

  clearToken() {
    localStorage.removeItem('s5_auth_token');
    localStorage.removeItem('s5_user_info');
  },

  getUser() {
    const raw = localStorage.getItem('s5_user_info');
    try {
      return raw ? JSON.parse(raw) : null;
    } catch (e) {
      return null;
    }
  },

  setUser(user) {
    localStorage.setItem('s5_user_info', JSON.stringify(user));
  },

  async request(endpoint, options = {}) {
    const url = `${this.BASE_URL}${endpoint}`;
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    const token = this.getToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers,
      });

      const data = await response.json().catch(() => ({}));

      if (!response.ok) {
        if (response.status === 401) {
          this.clearToken();
        }
        const errorMsg = data.detail || data.message || `Request failed (${response.status})`;
        throw new Error(errorMsg);
      }

      return data;
    } catch (err) {
      console.error(`API Error [${endpoint}]:`, err);
      throw err;
    }
  },

  // Auth Endpoints
  async register(name, email, password) {
    return this.request('/api/auth/register', {
      method: 'POST',
      body: JSON.stringify({ name, email, password }),
    });
  },

  async login(email, password) {
    return this.request('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
  },

  async getMe() {
    return this.request('/api/auth/me');
  },

  // Market & Profile Endpoints
  async getMarketRoles() {
    return this.request('/api/market/roles');
  },

  async saveProfile(profileData) {
    return this.request('/api/profile', {
      method: 'POST',
      body: JSON.stringify(profileData),
    });
  },

  async getProfile() {
    return this.request('/api/profile');
  },

  // Module 3: Verified Skill Profile
  async getVerifiedProfile(skillName = '') {
    const endpoint = skillName
      ? `/api/assessment/verified-profile?skill_name=${encodeURIComponent(skillName)}`
      : '/api/assessment/verified-profile';
    return this.request(endpoint);
  },

  // Module 4: Skill Gap Analysis & Market Benchmark Engine
  async getGapAnalysis(roleId = null) {
    const endpoint = roleId
      ? `/api/skills/gap-analysis?role_id=${encodeURIComponent(roleId)}`
      : '/api/skills/gap-analysis';
    return this.request(endpoint);
  },

  async triggerGapAnalysis(targetRoleId = null) {
    return this.request('/api/skills/gap-analysis', {
      method: 'POST',
      body: JSON.stringify({ target_role_id: targetRoleId }),
    });
  },

  // Module 4: Job-Market Skill Demand Analyzer
  async getJobMarketSkillDemand(targetRoleId = '', filters = {}) {
    const params = new URLSearchParams();
    if (targetRoleId) params.append('target_role_id', targetRoleId);
    if (filters.industry) params.append('industry', filters.industry);
    if (filters.location) params.append('location', filters.location);
    if (filters.experience_level) params.append('experience_level', filters.experience_level);
    const queryString = params.toString() ? `?${params.toString()}` : '';
    return this.request(`/api/market/skill-demand${queryString}`);
  },

  async getMarketFilters(targetRoleId = '') {
    const endpoint = targetRoleId
      ? `/api/market/filters?target_role_id=${encodeURIComponent(targetRoleId)}`
      : '/api/market/filters';
    return this.request(endpoint);
  },

  async createJobPosting(posting) {
    return this.request('/api/market/jobs', {
      method: 'POST',
      body: JSON.stringify(posting),
    });
  },

  async importMarketJobsJson(postings, dataSource = 'JSON Batch Import') {
    return this.request('/api/market/import-json', {
      method: 'POST',
      body: JSON.stringify({ postings, data_source: dataSource }),
    });
  },

  async importMarketJobsCsv(csvContent, dataSource = 'CSV Batch Import') {
    return this.request('/api/market/import-csv', {
      method: 'POST',
      body: JSON.stringify({ csv_content: csvContent, data_source: dataSource }),
    });
  },

  async uploadMarketDataFile(file, dataSource = '') {
    const formData = new FormData();
    formData.append('file', file);
    if (dataSource) {
      formData.append('data_source', dataSource);
    }
    const token = this.getToken();
    const headers = {};
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    const res = await fetch(`${this.BASE_URL}/api/market/upload`, {
      method: 'POST',
      headers,
      body: formData,
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      throw new Error(data.detail || 'File upload failed');
    }
    return data;
  },

  // Module 6: Personalized AI Curriculum Generator
  async getCurriculum(targetRoleId = null) {
    const endpoint = targetRoleId
      ? `/api/curriculum?target_role_id=${encodeURIComponent(targetRoleId)}`
      : '/api/curriculum';
    return this.request(endpoint);
  },

  async generateCurriculum(payload = {}) {
    return this.request('/api/curriculum/generate', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  async updateModuleProgress(moduleId, progressPct, status) {
    return this.request('/api/curriculum/module/progress', {
      method: 'POST',
      body: JSON.stringify({
        module_id: moduleId,
        progress_pct: progressPct,
        status: status,
      }),
    });
  },

  async adaptCurriculum(payload = {}) {
    return this.request('/api/curriculum/adapt', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  // Module 7: Micro-Credential Generation
  async getCredentials() {
    return this.request('/api/credentials');
  },

  async syncCredentials() {
    return this.request('/api/credentials/generate', {
      method: 'POST',
      body: JSON.stringify({}),
    });
  },

  async getCredentialDetails(credentialId) {
    return this.request(`/api/credentials/${encodeURIComponent(credentialId)}`);
  },

  async verifyCredentialPublic(credentialId) {
    return this.request(`/api/credentials/verify/${encodeURIComponent(credentialId)}`);
  },

  async claimCredential(credentialId) {
    return this.request(`/api/credentials/${encodeURIComponent(credentialId)}/claim`, {
      method: 'POST',
      body: JSON.stringify({}),
    });
  },

  // Module 8: Adaptive Learning Path & Reassessment Endpoints
  async getAdaptiveLearningPath(targetRoleId = null) {
    const url = targetRoleId ? `/api/adaptive/learning-path?target_role_id=${encodeURIComponent(targetRoleId)}` : '/api/adaptive/learning-path';
    return this.request(url);
  },

  async getAssessmentHistory() {
    return this.request('/api/adaptive/history');
  },

  async triggerAdaptation(payload = {}) {
    return this.request('/api/adaptive/trigger-adaptation', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  async startReassessment(skillName) {
    return this.request('/api/adaptive/reassess/start', {
      method: 'POST',
      body: JSON.stringify({ skill_name: skillName, force_new: true }),
    });
  },

  async simulateReassessment(skillName = 'Python', newScorePct = 78.0, newProficiencyLevel = null) {
    return this.request('/api/adaptive/simulate-reassessment', {
      method: 'POST',
      body: JSON.stringify({
        skill_name: skillName,
        new_score_pct: newScorePct,
        new_proficiency_level: newProficiencyLevel,
      }),
    });
  },

  async simulateMarketShift(roleId = 'fullstack-dev', newSkill = 'Docker', demandPercentage = 88.0) {
    return this.request('/api/adaptive/simulate-market-shift', {
      method: 'POST',
      body: JSON.stringify({
        role_id: roleId,
        new_skill: newSkill,
        demand_percentage: demandPercentage,
      }),
    });
  },

  // Module 9: Job Readiness Dashboard & Career Skill Profile Endpoints
  async getJobReadinessDashboard(targetRoleId = null) {
    const url = targetRoleId
      ? `/api/readiness/dashboard?target_role_id=${encodeURIComponent(targetRoleId)}`
      : '/api/readiness/dashboard';
    return this.request(url);
  },

  async getJobReadinessSummary(targetRoleId = null) {
    const url = targetRoleId
      ? `/api/readiness/summary?target_role_id=${encodeURIComponent(targetRoleId)}`
      : '/api/readiness/summary';
    return this.request(url);
  },

  async recalculateJobReadiness(targetRoleId = null) {
    return this.request('/api/readiness/recalculate', {
      method: 'POST',
      body: JSON.stringify({ target_role_id: targetRoleId }),
    });
  },
};

// Explicitly attach to window
window.API = API;
