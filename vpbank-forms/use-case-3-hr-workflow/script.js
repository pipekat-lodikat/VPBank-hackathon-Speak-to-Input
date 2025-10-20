// Use Case 3 - HR Workflow Form Script

document.addEventListener('DOMContentLoaded', function() {
  const form = document.getElementById('hrWorkflowForm');
  const clearBtn = document.getElementById('clearBtn');
  const aiTestBtn = document.getElementById('aiTestBtn');
  
  // Initialize common features
  initializeCommonFeatures(form);
  
  // Initialize AI Integration
  const formAI = new FormAI('hrWorkflowForm');
  
  // Set default submission date to today
  const submissionDateField = document.getElementById('submissionDate');
  submissionDateField.value = new Date().toISOString().split('T')[0];
  
  // Form submission
  form.addEventListener('submit', function(e) {
    e.preventDefault();
    
    if (!validateForm(form)) {
      showAlert('Vui lòng kiểm tra lại thông tin đã nhập', 'error');
      return;
    }
    
    const formData = getFormData(form);
    
    showModal(
      'Xác Nhận Gửi Đơn',
      'Bạn có chắc chắn muốn gửi đơn này không?',
      () => {
        // Simulate submission
        console.log('Submitting HR request:', formData);
        showAlert('Đơn đã được gửi thành công!', 'success');
        clearFormDraft('hrWorkflowForm');
        form.reset();
        submissionDateField.value = new Date().toISOString().split('T')[0];
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
        submissionDateField.value = new Date().toISOString().split('T')[0];
        showAlert('Form đã được xóa', 'info');
      }
    );
  });
  
  // AI Test button - simulates AI filling the form
  aiTestBtn.addEventListener('click', async function() {
    // Example: "Tạo đơn nghỉ phép từ 22 đến 24 tháng 10, lý do cá nhân"
    const today = new Date();
    const testData = {
      employeeName: 'Nguyễn Văn Cường',
      employeeId: 'EMP12345',
      department: 'customer-service',
      position: 'Chuyên viên CSKH',
      email: 'nguyen.cuong@vpbank.com.vn',
      phoneNumber: '0923456789',
      requestType: 'leave',
      leaveType: 'personal',
      startDate: `${today.getFullYear()}-10-22`,
      endDate: `${today.getFullYear()}-10-24`,
      reason: 'Lý do cá nhân',
      managerName: 'Trần Thị Lan',
      managerEmail: 'tran.lan@vpbank.com.vn',
      approvalStatus: 'pending',
      submissionDate: new Date().toISOString().split('T')[0]
    };
    
    const result = formAI.fillForm(testData);
    
    if (result.success) {
      showAlert(`AI đã điền thành công ${result.filledFields.length} trường`, 'success');
      calculateDuration(); // Calculate duration after filling dates
    } else {
      showAlert('Có lỗi khi AI điền form', 'error');
      console.error('AI Fill errors:', result.errors);
    }
  });
  
  // Request type change handler
  const requestType = document.getElementById('requestType');
  const leaveTypeGroup = document.getElementById('leaveTypeGroup');
  const leaveType = document.getElementById('leaveType');
  
  requestType.addEventListener('change', function() {
    if (this.value === 'leave') {
      leaveTypeGroup.style.display = 'block';
      leaveType.required = true;
    } else {
      leaveTypeGroup.style.display = 'none';
      leaveType.required = false;
      leaveType.value = '';
    }
  });
  
  // Approval status change handler
  const approvalStatus = document.getElementById('approvalStatus');
  const rejectionReasonGroup = document.getElementById('rejectionReasonGroup');
  const rejectionReason = document.getElementById('rejectionReason');
  
  approvalStatus.addEventListener('change', function() {
    if (this.value === 'rejected') {
      rejectionReasonGroup.style.display = 'block';
      rejectionReason.required = true;
    } else {
      rejectionReasonGroup.style.display = 'none';
      rejectionReason.required = false;
      rejectionReason.value = '';
    }
  });
  
  // Calculate duration between start and end dates
  const startDate = document.getElementById('startDate');
  const endDate = document.getElementById('endDate');
  const duration = document.getElementById('duration');
  
  function calculateDuration() {
    if (startDate.value && endDate.value) {
      const start = new Date(startDate.value);
      const end = new Date(endDate.value);
      
      if (end >= start) {
        const diffTime = Math.abs(end - start);
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1;
        duration.value = diffDays;
      } else {
        duration.value = '';
        showAlert('Ngày kết thúc phải sau ngày bắt đầu', 'error');
      }
    }
  }
  
  startDate.addEventListener('change', calculateDuration);
  endDate.addEventListener('change', calculateDuration);
  
  // Validate end date is after start date
  endDate.addEventListener('change', function() {
    if (startDate.value && endDate.value) {
      const start = new Date(startDate.value);
      const end = new Date(endDate.value);
      
      if (end < start) {
        const formGroup = endDate.closest('.form-group');
        formGroup.classList.add('error');
        const errorMessage = formGroup.querySelector('.error-message');
        errorMessage.textContent = 'Ngày kết thúc phải sau ngày bắt đầu';
      }
    }
  });
});

// Expose FormAI instance for external AI service integration
window.hrFormAI = null;
document.addEventListener('DOMContentLoaded', function() {
  window.hrFormAI = new FormAI('hrWorkflowForm');
});
