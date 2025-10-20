// VPBank Forms - Shared Utilities

// Validation Functions
const Validators = {
  required: (value) => {
    return value.trim() !== '';
  },

  email: (value) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(value);
  },

  phone: (value) => {
    const phoneRegex = /^[0-9]{10}$/;
    return phoneRegex.test(value.replace(/[\s-]/g, ''));
  },

  number: (value) => {
    return !isNaN(value) && value >= 0;
  },

  date: (value) => {
    return !isNaN(Date.parse(value));
  },

  minLength: (value, min) => {
    return value.length >= min;
  },

  maxLength: (value, max) => {
    return value.length <= max;
  }
};

// Format Numbers (Vietnamese format)
function formatCurrency(amount) {
  return new Intl.NumberFormat('vi-VN', {
    style: 'currency',
    currency: 'VND'
  }).format(amount);
}

function formatNumber(number) {
  return new Intl.NumberFormat('vi-VN').format(number);
}

// Date Formatting
function formatDate(date) {
  return new Intl.DateFormat('vi-VN').format(new Date(date));
}

// Show/Hide Elements
function showElement(element) {
  element.classList.add('show');
}

function hideElement(element) {
  element.classList.remove('show');
}

// Alert Functions
function showAlert(message, type = 'info') {
  const alertDiv = document.createElement('div');
  alertDiv.className = `alert alert-${type} show`;
  alertDiv.textContent = message;
  
  const container = document.querySelector('.container');
  container.insertBefore(alertDiv, container.firstChild);
  
  setTimeout(() => {
    alertDiv.classList.remove('show');
    setTimeout(() => alertDiv.remove(), 300);
  }, 5000);
}

// Modal Functions
function showModal(title, message, onConfirm, onCancel) {
  const modal = document.getElementById('confirmModal');
  const modalTitle = modal.querySelector('.modal-header h3');
  const modalBody = modal.querySelector('.modal-body');
  const confirmBtn = modal.querySelector('.btn-confirm');
  const cancelBtn = modal.querySelector('.btn-cancel');
  
  modalTitle.textContent = title;
  modalBody.textContent = message;
  
  modal.classList.add('show');
  
  confirmBtn.onclick = () => {
    modal.classList.remove('show');
    if (onConfirm) onConfirm();
  };
  
  cancelBtn.onclick = () => {
    modal.classList.remove('show');
    if (onCancel) onCancel();
  };
  
  // Close on outside click
  modal.onclick = (e) => {
    if (e.target === modal) {
      modal.classList.remove('show');
      if (onCancel) onCancel();
    }
  };
}

function hideModal() {
  const modal = document.getElementById('confirmModal');
  modal.classList.remove('show');
}

// Form Validation
function validateField(field) {
  const value = field.value.trim();
  const formGroup = field.closest('.form-group');
  const errorMessage = formGroup.querySelector('.error-message');
  
  // Clear previous error
  formGroup.classList.remove('error', 'success');
  
  // Check required
  if (field.hasAttribute('required') && !Validators.required(value)) {
    formGroup.classList.add('error');
    errorMessage.textContent = 'Trường này là bắt buộc';
    return false;
  }
  
  // Check email
  if (field.type === 'email' && value && !Validators.email(value)) {
    formGroup.classList.add('error');
    errorMessage.textContent = 'Email không hợp lệ';
    return false;
  }
  
  // Check phone
  if (field.type === 'tel' && value && !Validators.phone(value)) {
    formGroup.classList.add('error');
    errorMessage.textContent = 'Số điện thoại phải có 10 chữ số';
    return false;
  }
  
  // Check number
  if (field.type === 'number' && value && !Validators.number(value)) {
    formGroup.classList.add('error');
    errorMessage.textContent = 'Số không hợp lệ';
    return false;
  }
  
  // Success
  formGroup.classList.add('success');
  return true;
}

function validateForm(form) {
  let isValid = true;
  const fields = form.querySelectorAll('input, select, textarea');
  
  fields.forEach(field => {
    if (!validateField(field)) {
      isValid = false;
    }
  });
  
  return isValid;
}

// Form Data Extraction
function getFormData(form) {
  const formData = {};
  const fields = form.querySelectorAll('input, select, textarea');
  
  fields.forEach(field => {
    if (field.name) {
      formData[field.name] = field.value;
    }
  });
  
  return formData;
}

// Local Storage Functions
function saveFormDraft(formId, data) {
  try {
    localStorage.setItem(`vpbank_form_draft_${formId}`, JSON.stringify(data));
  } catch (e) {
    console.error('Error saving form draft:', e);
  }
}

function loadFormDraft(formId) {
  try {
    const data = localStorage.getItem(`vpbank_form_draft_${formId}`);
    return data ? JSON.parse(data) : null;
  } catch (e) {
    console.error('Error loading form draft:', e);
    return null;
  }
}

function clearFormDraft(formId) {
  try {
    localStorage.removeItem(`vpbank_form_draft_${formId}`);
  } catch (e) {
    console.error('Error clearing form draft:', e);
  }
}

// Debounce Function
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

// Initialize Common Features
function initializeCommonFeatures(form) {
  // Add validation on blur
  const fields = form.querySelectorAll('input, select, textarea');
  fields.forEach(field => {
    field.addEventListener('blur', () => validateField(field));
    
    // Auto-save draft
    field.addEventListener('input', debounce(() => {
      const formData = getFormData(form);
      saveFormDraft(form.id, formData);
    }, 1000));
  });
  
  // Load draft on page load
  const draft = loadFormDraft(form.id);
  if (draft) {
    const shouldLoad = confirm('Bạn có muốn tải bản nháp đã lưu không?');
    if (shouldLoad) {
      Object.keys(draft).forEach(key => {
        const field = form.querySelector(`[name="${key}"]`);
        if (field) {
          field.value = draft[key];
        }
      });
    }
  }
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    Validators,
    formatCurrency,
    formatNumber,
    formatDate,
    showAlert,
    showModal,
    hideModal,
    validateField,
    validateForm,
    getFormData,
    saveFormDraft,
    loadFormDraft,
    clearFormDraft,
    initializeCommonFeatures
  };
}
