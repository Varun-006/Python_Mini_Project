/**
 * NovaBank Web Client Application
 * Handles authentication, real-time balance updates, transactions,
 * inter-account transfers, and DOM interactions.
 */

// Application State
const state = {
  account: null,
  pin: null,
  balanceVisible: true,
  activeTxFilter: 'all',
  searchQuery: ''
};

// ============================================================================
// Initialization & Event Listeners
// ============================================================================

document.addEventListener('DOMContentLoaded', () => {
  setupAuthTabs();
  setupAuthForms();
  setupDashboardTabs();
  setupActionForms();
  setupUIInteractions();

  // Check if session exists in sessionStorage
  const savedAcc = sessionStorage.getItem('novabank_acc');
  const savedPin = sessionStorage.getItem('novabank_pin');
  if (savedAcc && savedPin) {
    performLogin(savedAcc, savedPin, true);
  }
});

// ============================================================================
// Toast Notification System
// ============================================================================

function showToast(message, type = 'info') {
  const container = document.getElementById('toastContainer');
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;

  const icon = type === 'success' ? '✓' : type === 'error' ? '⚠' : 'ℹ';
  toast.innerHTML = `
    <span style="font-weight: 800; font-size: 1.1rem;">${icon}</span>
    <span style="flex: 1;">${escapeHtml(message)}</span>
  `;

  container.appendChild(toast);

  setTimeout(() => {
    toast.remove();
  }, 4500);
}

// ============================================================================
// Authentication Flow (Create Account & Login)
// ============================================================================

function setupAuthTabs() {
  const tabCreate = document.getElementById('tabCreateAccountBtn');
  const tabLogin = document.getElementById('tabLoginBtn');
  const formCreate = document.getElementById('createAccountForm');
  const formLogin = document.getElementById('loginForm');
  const successBanner = document.getElementById('newAccountSuccessBanner');

  tabCreate.addEventListener('click', () => {
    tabCreate.classList.add('active');
    tabLogin.classList.remove('active');
    formCreate.style.display = 'block';
    formLogin.style.display = 'none';
  });

  tabLogin.addEventListener('click', () => {
    tabLogin.classList.add('active');
    tabCreate.classList.remove('active');
    formLogin.style.display = 'block';
    formCreate.style.display = 'none';
    successBanner.style.display = 'none';
  });

  // Demo credential fill helper
  const fillDemoBtn = document.getElementById('fillDemoCredsBtn');
  if (fillDemoBtn) {
    fillDemoBtn.addEventListener('click', () => {
      document.getElementById('loginAccNum').value = '595131';
      document.getElementById('loginPin').value = '2222';
      showToast('Filled credentials for Varuna (595131)', 'info');
    });
  }

  // Copy Account Number button
  const copyBtn = document.getElementById('copyAccNumBtn');
  if (copyBtn) {
    copyBtn.addEventListener('click', () => {
      const text = document.getElementById('createdAccountNumText').innerText;
      navigator.clipboard.writeText(text).then(() => {
        showToast('Account number copied to clipboard!', 'success');
      });
    });
  }
}

function setupAuthForms() {
  // Create Account Form
  const createForm = document.getElementById('createAccountForm');
  createForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const name = document.getElementById('regName').value.trim();
    const phone = document.getElementById('regPhone').value.trim();
    const pin = document.getElementById('regPin').value.trim();
    const initialDeposit = parseFloat(document.getElementById('regDeposit').value) || 0;

    if (phone.length !== 10 || !/^\d+$/.test(phone)) {
      showToast('Phone number must be exactly 10 digits.', 'error');
      return;
    }

    if (pin.length !== 4 || !/^\d+$/.test(pin)) {
      showToast('PIN must be exactly 4 digits.', 'error');
      return;
    }

    const submitBtn = document.getElementById('submitCreateAccountBtn');
    submitBtn.disabled = true;
    submitBtn.innerText = 'Creating Account...';

    try {
      const res = await fetch('/api/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, phone, pin, initial_deposit: initialDeposit })
      });

      const data = await res.json();
      if (data.success) {
        showToast(data.message, 'success');
        createForm.reset();
        
        // Show success card with created account number
        const banner = document.getElementById('newAccountSuccessBanner');
        const numText = document.getElementById('createdAccountNumText');
        numText.innerText = data.account.account_number;
        banner.style.display = 'block';

        const quickLoginBtn = document.getElementById('quickLoginCreatedBtn');
        quickLoginBtn.onclick = () => {
          performLogin(data.account.account_number, pin);
        };
      } else {
        showToast(data.message || 'Account creation failed.', 'error');
      }
    } catch (err) {
      showToast('Network error while connecting to server.', 'error');
    } finally {
      submitBtn.disabled = false;
      submitBtn.innerText = 'Create Bank Account';
    }
  });

  // Login Form
  const loginForm = document.getElementById('loginForm');
  loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const accNum = document.getElementById('loginAccNum').value.trim();
    const pin = document.getElementById('loginPin').value.trim();

    if (!accNum || !pin) {
      showToast('Please enter both Account Number and PIN.', 'error');
      return;
    }

    const submitBtn = document.getElementById('submitLoginBtn');
    submitBtn.disabled = true;
    submitBtn.innerText = 'Authenticating...';

    await performLogin(accNum, pin);
    submitBtn.disabled = false;
    submitBtn.innerText = 'Sign In to Account';
  });
}

async function performLogin(accNum, pin, silent = false) {
  try {
    const res = await fetch('/api/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ account_number: accNum, pin })
    });

    const data = await res.json();
    if (data.success) {
      state.account = data.account;
      state.pin = pin;

      sessionStorage.setItem('novabank_acc', accNum);
      sessionStorage.setItem('novabank_pin', pin);

      if (!silent) {
        showToast(data.message, 'success');
      }

      transitionToDashboard();
    } else {
      showToast(data.message || 'Login failed.', 'error');
      sessionStorage.removeItem('novabank_acc');
      sessionStorage.removeItem('novabank_pin');
    }
  } catch (err) {
    showToast('Failed to connect to authentication server.', 'error');
  }
}

function transitionToDashboard() {
  document.getElementById('authView').style.display = 'none';
  document.getElementById('dashboardView').style.display = 'block';
  document.getElementById('userHeaderWidget').style.display = 'flex';

  renderDashboardData();
}

function logout() {
  state.account = null;
  state.pin = null;
  sessionStorage.removeItem('novabank_acc');
  sessionStorage.removeItem('novabank_pin');

  document.getElementById('dashboardView').style.display = 'none';
  document.getElementById('authView').style.display = 'block';
  document.getElementById('userHeaderWidget').style.display = 'none';
  document.getElementById('loginForm').reset();

  showToast('Logged out safely. See you soon!', 'info');
}

// ============================================================================
// Dashboard Rendering & Real-time Updates
// ============================================================================

function renderDashboardData() {
  if (!state.account) return;

  const acc = state.account;

  // Header user info
  document.getElementById('headerUserName').innerText = acc.name;
  document.getElementById('headerAvatar').innerText = acc.name.charAt(0).toUpperCase();

  // Debit Card
  document.getElementById('cardHolderNameDisplay').innerText = acc.name;
  document.getElementById('cardAccNumDisplay').innerText = formatCardNumber(acc.account_number);

  // Balance displays
  updateBalanceDisplay();

  // Overview box
  document.getElementById('infoAccNumber').innerText = acc.account_number;
  document.getElementById('infoPhoneNumber').innerText = acc.phone || '---';
  document.getElementById('infoTxCount').innerText = acc.transactions ? acc.transactions.length : 0;

  // Hints
  const formattedBalance = formatCurrency(acc.balance);
  document.getElementById('withdrawMaxHint').innerText = `Available Balance: ${formattedBalance}`;
  document.getElementById('transferMaxHint').innerText = `Available Balance: ${formattedBalance}`;

  // Render transactions
  renderTransactionHistory();
}

function updateBalanceDisplay() {
  const balance = state.account ? state.account.balance : 0;
  const balanceFormatted = formatCurrency(balance);
  const isVisible = state.balanceVisible;

  const cardBalance = document.getElementById('cardBalanceDisplay');
  const panelBalance = document.getElementById('panelBigBalanceDisplay');

  if (isVisible) {
    cardBalance.innerText = balanceFormatted;
    panelBalance.innerText = balanceFormatted;
  } else {
    cardBalance.innerText = '$••••••';
    panelBalance.innerText = '$••••••';
  }
}

function formatCardNumber(accNum) {
  if (!accNum) return '•••• ••';
  return `${accNum.slice(0, 4)} ${accNum.slice(4)}••`;
}

function formatCurrency(val) {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(val);
}

// ============================================================================
// Dashboard Navigation & Actions
// ============================================================================

function setupDashboardTabs() {
  const tabButtons = document.querySelectorAll('.d-nav-btn');
  const panels = document.querySelectorAll('.action-panel-card');

  tabButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      tabButtons.forEach(b => b.classList.remove('active'));
      panels.forEach(p => p.style.display = 'none');

      btn.classList.add('active');
      const targetId = btn.getAttribute('data-target');
      const targetPanel = document.getElementById(targetId);
      if (targetPanel) {
        targetPanel.style.display = 'block';
      }
    });
  });

  // Refresh balance button
  const refreshBtn = document.getElementById('refreshBalanceBtn');
  refreshBtn.addEventListener('click', async () => {
    refreshBtn.disabled = true;
    refreshBtn.innerText = 'Refreshing...';
    await refreshAccountData();
    refreshBtn.disabled = false;
    refreshBtn.innerText = '↻ Refresh Balance';
    showToast('Balance updated to latest status.', 'info');
  });

  // Logout button
  document.getElementById('headerLogoutBtn').addEventListener('click', logout);
}

async function refreshAccountData() {
  if (!state.account || !state.pin) return;

  try {
    const res = await fetch(`/api/account/${state.account.account_number}?pin=${state.pin}`);
    const data = await res.json();
    if (data.success) {
      state.account = data.account;
      renderDashboardData();
    }
  } catch (err) {
    console.error('Failed to refresh data', err);
  }
}

// ============================================================================
// Banking Operations: Deposit, Withdraw, Transfer, PIN Change
// ============================================================================

function setupActionForms() {
  // 1. ➕ Deposit Money
  const depForm = document.getElementById('depositForm');
  depForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const amount = parseFloat(document.getElementById('depositAmount').value);

    if (isNaN(amount) || amount <= 0) {
      showToast('Please enter a valid deposit amount greater than $0.', 'error');
      return;
    }

    const btn = document.getElementById('submitDepositBtn');
    btn.disabled = true;
    btn.innerText = 'Processing Deposit...';

    try {
      const res = await fetch('/api/deposit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          account_number: state.account.account_number,
          pin: state.pin,
          amount
        })
      });

      const data = await res.json();
      if (data.success) {
        state.account.balance = data.balance;
        state.account.transactions = data.transactions;
        renderDashboardData();
        depForm.reset();
        showToast(data.message, 'success');
      } else {
        showToast(data.message || 'Deposit failed.', 'error');
      }
    } catch (err) {
      showToast('Network error during deposit.', 'error');
    } finally {
      btn.disabled = false;
      btn.innerText = 'Confirm & Add to Balance';
    }
  });

  // 2. ➖ Withdraw Money
  const withForm = document.getElementById('withdrawForm');
  withForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const amount = parseFloat(document.getElementById('withdrawAmount').value);

    if (isNaN(amount) || amount <= 0) {
      showToast('Please enter a valid withdrawal amount.', 'error');
      return;
    }

    if (amount > state.account.balance) {
      showToast(`Insufficient funds! Available: ${formatCurrency(state.account.balance)}`, 'error');
      return;
    }

    const btn = document.getElementById('submitWithdrawBtn');
    btn.disabled = true;
    btn.innerText = 'Processing Withdrawal...';

    try {
      const res = await fetch('/api/withdraw', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          account_number: state.account.account_number,
          pin: state.pin,
          amount
        })
      });

      const data = await res.json();
      if (data.success) {
        state.account.balance = data.balance;
        state.account.transactions = data.transactions;
        renderDashboardData();
        withForm.reset();
        showToast(data.message, 'success');
      } else {
        showToast(data.message || 'Withdrawal failed.', 'error');
      }
    } catch (err) {
      showToast('Network error during withdrawal.', 'error');
    } finally {
      btn.disabled = false;
      btn.innerText = 'Authorize Withdrawal';
    }
  });

  // 3. ⇄ Transfer Money
  const transForm = document.getElementById('transferForm');
  const receiverInput = document.getElementById('transferReceiverAcc');
  const lookupStatus = document.getElementById('receiverLookupStatus');

  // Live receiver verification
  let lookupTimeout = null;
  receiverInput.addEventListener('input', () => {
    const receiverAcc = receiverInput.value.trim();
    clearTimeout(lookupTimeout);

    if (receiverAcc.length !== 6) {
      lookupStatus.style.display = 'none';
      return;
    }

    if (receiverAcc === state.account.account_number) {
      lookupStatus.className = 'recipient-lookup-box recipient-not-found';
      lookupStatus.innerHTML = '⚠ You cannot transfer money to your own account.';
      lookupStatus.style.display = 'flex';
      return;
    }

    lookupTimeout = setTimeout(async () => {
      try {
        const res = await fetch(`/api/lookup/${receiverAcc}`);
        const data = await res.json();
        if (data.exists) {
          lookupStatus.className = 'recipient-lookup-box recipient-found';
          lookupStatus.innerHTML = `✓ Recipient Verified: <strong>${escapeHtml(data.name)}</strong>`;
        } else {
          lookupStatus.className = 'recipient-lookup-box recipient-not-found';
          lookupStatus.innerHTML = '⚠ Account number not found in bank ledger.';
        }
        lookupStatus.style.display = 'flex';
      } catch (e) {
        lookupStatus.style.display = 'none';
      }
    }, 300);
  });

  transForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const receiverAcc = receiverInput.value.trim();
    const amount = parseFloat(document.getElementById('transferAmount').value);

    if (receiverAcc === state.account.account_number) {
      showToast('Cannot transfer to your own account.', 'error');
      return;
    }

    if (isNaN(amount) || amount <= 0) {
      showToast('Please enter a valid transfer amount.', 'error');
      return;
    }

    if (amount > state.account.balance) {
      showToast(`Insufficient funds! Available: ${formatCurrency(state.account.balance)}`, 'error');
      return;
    }

    const btn = document.getElementById('submitTransferBtn');
    btn.disabled = true;
    btn.innerText = 'Sending Funds...';

    try {
      const res = await fetch('/api/transfer', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          sender_account: state.account.account_number,
          receiver_account: receiverAcc,
          pin: state.pin,
          amount
        })
      });

      const data = await res.json();
      if (data.success) {
        state.account.balance = data.balance;
        state.account.transactions = data.transactions;
        renderDashboardData();
        transForm.reset();
        lookupStatus.style.display = 'none';
        showToast(data.message, 'success');
      } else {
        showToast(data.message || 'Transfer failed.', 'error');
      }
    } catch (err) {
      showToast('Network error during transfer.', 'error');
    } finally {
      btn.disabled = false;
      btn.innerText = 'Execute Funds Transfer';
    }
  });

  // 4. 🔑 Change PIN
  const pinForm = document.getElementById('changePinForm');
  pinForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const oldPin = document.getElementById('oldPinInput').value.trim();
    const newPin = document.getElementById('newPinInput').value.trim();
    const confirmPin = document.getElementById('confirmPinInput').value.trim();

    if (oldPin !== state.pin) {
      showToast('Old PIN is incorrect. Verification failed.', 'error');
      return;
    }

    if (newPin.length !== 4 || !/^\d+$/.test(newPin)) {
      showToast('New PIN must be exactly 4 digits.', 'error');
      return;
    }

    if (newPin === oldPin) {
      showToast('New PIN cannot be the same as old PIN.', 'error');
      return;
    }

    if (newPin !== confirmPin) {
      showToast('PIN confirmation does not match.', 'error');
      return;
    }

    const btn = document.getElementById('submitPinChangeBtn');
    btn.disabled = true;
    btn.innerText = 'Updating PIN...';

    try {
      const res = await fetch('/api/change-pin', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          account_number: state.account.account_number,
          old_pin: oldPin,
          new_pin: newPin
        })
      });

      const data = await res.json();
      if (data.success) {
        state.pin = newPin;
        sessionStorage.setItem('novabank_pin', newPin);
        pinForm.reset();
        showToast(data.message, 'success');
      } else {
        showToast(data.message || 'Failed to update PIN.', 'error');
      }
    } catch (err) {
      showToast('Network error while changing PIN.', 'error');
    } finally {
      btn.disabled = false;
      btn.innerText = 'Update Security PIN';
    }
  });
}

// Quick chip amount helpers
window.setDepositQuick = function(amt) {
  document.getElementById('depositAmount').value = amt;
};

window.setWithdrawQuick = function(amt) {
  document.getElementById('withdrawAmount').value = amt;
};

// ============================================================================
// Transaction History Rendering & Search/Filter
// ============================================================================

function setupUIInteractions() {
  // Eye icon to toggle balance visibility
  const eyeBtn = document.getElementById('toggleBalanceVisibilityBtn');
  eyeBtn.addEventListener('click', () => {
    state.balanceVisible = !state.balanceVisible;
    eyeBtn.innerText = state.balanceVisible ? '👁️' : '🙈';
    updateBalanceDisplay();
  });

  // Transaction filter pills
  const pills = document.querySelectorAll('.tx-pill');
  pills.forEach(pill => {
    pill.addEventListener('click', () => {
      pills.forEach(p => p.classList.remove('active'));
      pill.classList.add('active');
      state.activeTxFilter = pill.getAttribute('data-filter');
      renderTransactionHistory();
    });
  });

  // Transaction search input
  const searchInput = document.getElementById('searchTxInput');
  searchInput.addEventListener('input', (e) => {
    state.searchQuery = e.target.value.toLowerCase().trim();
    renderTransactionHistory();
  });
}

function renderTransactionHistory() {
  const tbody = document.getElementById('txTableBody');
  const emptyState = document.getElementById('txEmptyState');
  tbody.innerHTML = '';

  const transactions = state.account ? (state.account.transactions || []) : [];

  // Filter
  let filtered = [...transactions].reverse(); // Most recent first

  if (state.activeTxFilter !== 'all') {
    filtered = filtered.filter(tx => tx.type.toLowerCase().includes(state.activeTxFilter.toLowerCase()));
  }

  if (state.searchQuery) {
    filtered = filtered.filter(tx =>
      tx.type.toLowerCase().includes(state.searchQuery) ||
      (tx.details && tx.details.toLowerCase().includes(state.searchQuery)) ||
      tx.timestamp.includes(state.searchQuery) ||
      tx.amount.toString().includes(state.searchQuery)
    );
  }

  if (filtered.length === 0) {
    emptyState.style.display = 'block';
    return;
  }

  emptyState.style.display = 'none';

  filtered.forEach(tx => {
    const tr = document.createElement('tr');
    const isCredit = tx.type.includes('Deposit') || tx.type.includes('Received');
    const badgeClass = isCredit ? 'tx-badge-deposit' : 'tx-badge-withdrawal';
    const amountClass = isCredit ? 'amount-credit' : 'amount-debit';
    const sign = isCredit ? '+' : '-';

    tr.innerHTML = `
      <td style="font-family: var(--font-mono); font-size: 0.8rem; color: #94a3b8;">${escapeHtml(tx.timestamp)}</td>
      <td>
        <span class="tx-badge ${badgeClass}">${escapeHtml(tx.type)}</span>
      </td>
      <td style="color: #cbd5e1;">${escapeHtml(tx.details || '-')}</td>
      <td class="${amountClass}">${sign}${formatCurrency(tx.amount)}</td>
      <td style="font-family: var(--font-mono);">${formatCurrency(tx.balance_after)}</td>
    `;

    tbody.appendChild(tr);
  });
}

function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}
