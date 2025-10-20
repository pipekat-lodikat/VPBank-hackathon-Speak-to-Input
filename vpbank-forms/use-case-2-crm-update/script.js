// Use Case 2 - CRM Update Form Script

document.addEventListener('DOMContentLoaded', function() {
  const form = document.getElementById('crmUpdateForm');
  const clearBtn = document.getElementById('clearBtn');
  const aiTestBtn = document.getElementById('aiTestBtn');
  
  // Initialize common features
  initializeCommonFeatures(form);
  
  // Initialize AI Integration
  const formAI = new FormAI('crmUpdateForm');
  
  // Set default interaction date to today
  const interactionDateField = document.getElementById('interactionDate');
  interactionDateField.value = new Date().toISOString().split('T')[0];
  
  // Set default interaction time to now
  const interactionTimeField = document.getElementById('interactionTime');
  const now = new Date();
  interactionTimeField.value = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`;
  
  // Form submission
  form.addEventListener('submit', function(e) {
    e.preventDefault();
    
    if (!validateForm(form)) {
      showAlert('Vui lòng kiểm tra lại thông tin đã nhập', 'error');
      return;
    }
    
    const formData = getFormData(form);
    
    showModal(
      'Xác Nhận Cập Nhật',
      'Bạn có chắc chắn muốn cập nhật thông tin CRM này không?',
      () => {
        // Simulate CRM update
        console.log('Updating CRM:', formData);
        showAlert('Thông tin CRM đã được cập nhật thành công!', 'success');
        clearFormDraft('crmUpdateForm');
        form.reset();
        interactionDateField.value = new Date().toISOString().split('T')[0];
        const now = new Date();
        interactionTimeField.value = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`;
      }
    );
  });
  
  // Clear button
  clearBtn.addEventListener('click', function() {
    showModal(
      'Xác Nhận Xóa',
      'Bạn có chắc chắn muốn xóa toàn bộ thông tin đã nhập không?',
      () => {
        formAI.resetForm();
        interactionDateField.value = new Date().toISOString().split('T')[0];
        const now = new Date();
        interactionTimeField.value = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`;
        showAlert('Form đã được xóa', 'info');
      }
    );
  });
  
  // AI Test button - simulates AI filling the form
  aiTestBtn.addEventListener('click', async function() {
    // Example: "Cập nhật địa chỉ khách Nguyễn Văn Bình thành 25A Nguyễn Trãi"
    const testData = {
      customerName: 'Nguyễn Văn Bình',
      customerId: 'CUS987654',
      phoneNumber: '0912345678',
      email: 'nguyenvanbinh@example.com',
      address: '25A Nguyễn Trãi, Phường Bến Thành, Quận 1, TP.HCM',
      interactionType: 'call',
      interactionDate: new Date().toISOString().split('T')[0],
      interactionTime: new Date().toTimeString().slice(0, 5),
      duration: '5',
      agentName: 'Trần Thị Mai',
      issueCategory: 'account',
      issueDescription: 'Khách hàng yêu cầu cập nhật địa chỉ mới',
      resolutionStatus: 'resolved',
      resolutionDetails: 'Đã cập nhật địa chỉ mới vào hệ thống CRM',
      satisfactionRating: '5',
      followUpRequired: 'no'
    };
    
    const result = formAI.fillForm(testData);
    
    if (result.success) {
      showAlert(`AI đã điền thành công ${result.filledFields.length} trường`, 'success');
    } else {
      showAlert('Có lỗi khi AI điền form', 'error');
      console.error('AI Fill errors:', result.errors);
    }
  });
  
  // Follow-up logic
  const followUpRequired = document.getElementById('followUpRequired');
  const followUpDate = document.getElementById('followUpDate');
  
  followUpRequired.addEventListener('change', function() {
    if (this.value === 'yes') {
      followUpDate.required = true;
      // Set default follow-up date to 7 days from now
      const nextWeek = new Date();
      nextWeek.setDate(nextWeek.getDate() + 7);
      followUpDate.value = nextWeek.toISOString().split('T')[0];
    } else {
      followUpDate.required = false;
      followUpDate.value = '';
    }
  });
  
  // Resolution status logic
  const resolutionStatus = document.getElementById('resolutionStatus');
  const resolutionDetails = document.getElementById('resolutionDetails');
  
  resolutionStatus.addEventListener('change', function() {
    if (this.value === 'resolved') {
      resolutionDetails.placeholder = 'Mô tả cách đã giải quyết vấn đề...';
    } else if (this.value === 'escalated') {
      resolutionDetails.placeholder = 'Mô tả lý do chuyển lên cấp trên và bước tiếp theo...';
    } else {
      resolutionDetails.placeholder = 'Mô tả cách giải quyết hoặc bước tiếp theo...';
    }
  });
});

// Expose FormAI instance for external AI service integration
window.crmFormAI = null;
document.addEventListener('DOMContentLoaded', function() {
  window.crmFormAI = new FormAI('crmUpdateForm');
});
