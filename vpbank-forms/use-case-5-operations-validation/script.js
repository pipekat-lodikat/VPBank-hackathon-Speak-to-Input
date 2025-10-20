// Use Case 5 - Operations Validation Form Script

document.addEventListener('DOMContentLoaded', function() {
  const form = document.getElementById('operationsForm');
  const clearBtn = document.getElementById('clearBtn');
  const aiTestBtn = document.getElementById('aiTestBtn');
  
  // Initialize common features
  initializeCommonFeatures(form);
  
  // Initialize AI Integration
  const formAI = new FormAI('operationsForm');
  
  // Set default review date to today
  const reviewDateField = document.getElementById('reviewDate');
  reviewDateField.value = new Date().toISOString().split('T')[0];
  
  // Form submission
  form.addEventListener('submit', function(e) {
    e.preventDefault();
    
    if (!validateForm(form)) {
      showAlert('Vui lòng kiểm tra lại thông tin đã nhập', 'error');
      return;
    }
    
    const formData = getFormData(form);
    
    showModal(
      'Xác Nhận Kiểm Tra',
      'Bạn có chắc chắn muốn xác nhận kết quả kiểm tra giao dịch này không?',
      () => {
        // Simulate submission
        console.log('Submitting transaction validation:', formData);
        showAlert('Kết quả kiểm tra đã được lưu thành công!', 'success');
        clearFormDraft('operationsForm');
        form.reset();
        reviewDateField.value = new Date().toISOString().split('T')[0];
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
        reviewDateField.value = new Date().toISOString().split('T')[0];
        showAlert('Form đã được xóa', 'info');
      }
    );
  });
  
  // AI Test button - simulates AI filling the form
  aiTestBtn.addEventListener('click', async function() {
    // Example: "Kiểm tra giao dịch khách Nguyễn Thị Hoa ngày 17 tháng 10, số tiền 350 triệu"
    const testData = {
      customerName: 'Nguyễn Thị Hoa',
      customerId: 'CUS456789',
      accountNumber: '1234567890',
      phoneNumber: '0934567890',
      transactionId: 'TXN20241017-001',
      transactionDate: '2024-10-17',
      transactionTime: '14:30',
      transactionAmount: '350000000',
      transactionType: 'transfer',
      channel: 'online',
      transactionDescription: 'Chuyển khoản thanh toán',
      beneficiaryName: 'Công ty ABC',
      beneficiaryAccount: '9876543210',
      beneficiaryBank: 'VPBank',
      status: 'completed',
      processingSystem: 'core-banking',
      validationResult: 'valid',
      reviewerName: 'Phạm Văn Đức',
      reviewDate: new Date().toISOString().split('T')[0],
      balanceBefore: '500000000',
      balanceAfter: '150000000',
      balanceStatus: 'matched',
      fraudScore: '15',
      fraudIndicators: 'none'
    };
    
    const result = formAI.fillForm(testData);
    
    if (result.success) {
      showAlert(`AI đã điền thành công ${result.filledFields.length} trường`, 'success');
      calculateBalanceDifference(); // Calculate balance after filling
    } else {
      showAlert('Có lỗi khi AI điền form', 'error');
      console.error('AI Fill errors:', result.errors);
    }
  });
  
  // Transaction type change handler - show/hide beneficiary section
  const transactionType = document.getElementById('transactionType');
  const beneficiarySection = document.getElementById('beneficiarySection');
  
  transactionType.addEventListener('change', function() {
    if (this.value === 'transfer') {
      beneficiarySection.style.display = 'block';
    } else {
      beneficiarySection.style.display = 'none';
    }
  });
  
  // Status change handler - show/hide failure reason
  const status = document.getElementById('status');
  const failureReasonGroup = document.getElementById('failureReasonGroup');
  const failureReason = document.getElementById('failureReason');
  
  status.addEventListener('change', function() {
    if (this.value === 'failed' || this.value === 'cancelled') {
      failureReasonGroup.style.display = 'block';
      failureReason.required = true;
    } else {
      failureReasonGroup.style.display = 'none';
      failureReason.required = false;
      failureReason.value = '';
    }
  });
  
  // Validation result change handler
  const validationResult = document.getElementById('validationResult');
  const validationIssuesGroup = document.getElementById('validationIssuesGroup');
  const validationIssues = document.getElementById('validationIssues');
  
  validationResult.addEventListener('change', function() {
    if (this.value === 'invalid' || this.value === 'needs-review' || this.value === 'suspicious') {
      validationIssuesGroup.style.display = 'block';
      validationIssues.required = true;
    } else {
      validationIssuesGroup.style.display = 'none';
      validationIssues.required = false;
      validationIssues.value = '';
    }
  });
  
  // Fraud indicators change handler
  const fraudIndicators = document.getElementById('fraudIndicators');
  const fraudDetailsGroup = document.getElementById('fraudDetailsGroup');
  const fraudDetails = document.getElementById('fraudDetails');
  
  fraudIndicators.addEventListener('change', function() {
    if (this.value !== '' && this.value !== 'none') {
      fraudDetailsGroup.style.display = 'block';
      fraudDetails.required = true;
    } else {
      fraudDetailsGroup.style.display = 'none';
      fraudDetails.required = false;
      fraudDetails.value = '';
    }
  });
  
  // Calculate balance difference and verify
  const balanceBefore = document.getElementById('balanceBefore');
  const balanceAfter = document.getElementById('balanceAfter');
  const transactionAmount = document.getElementById('transactionAmount');
  const balanceStatus = document.getElementById('balanceStatus');
  
  function calculateBalanceDifference() {
    if (balanceBefore.value && balanceAfter.value && transactionAmount.value) {
      const before = parseFloat(balanceBefore.value);
      const after = parseFloat(balanceAfter.value);
      const amount = parseFloat(transactionAmount.value);
      const type = transactionType.value;
      
      let expectedAfter = before;
      
      // Calculate expected balance based on transaction type
      if (type === 'deposit' || type === 'refund' || type === 'loan-disbursement') {
        expectedAfter = before + amount;
      } else if (type === 'withdrawal' || type === 'transfer' || type === 'payment' || type === 'loan-payment' || type === 'fee') {
        expectedAfter = before - amount;
      }
      
      // Check if balances match
      if (Math.abs(after - expectedAfter) < 1) {
        balanceStatus.value = 'matched';
        console.log('Balance matched');
      } else {
        balanceStatus.value = 'mismatched';
        showAlert('Cảnh báo: Số dư không khớp với giao dịch', 'error');
      }
    }
  }
  
  balanceBefore.addEventListener('change', calculateBalanceDifference);
  balanceAfter.addEventListener('change', calculateBalanceDifference);
  transactionAmount.addEventListener('change', calculateBalanceDifference);
  transactionType.addEventListener('change', calculateBalanceDifference);
  
  // Fraud score color coding
  const fraudScore = document.getElementById('fraudScore');
  
  fraudScore.addEventListener('input', function() {
    const score = parseInt(this.value);
    const formGroup = this.closest('.form-group');
    
    formGroup.classList.remove('low-risk', 'medium-risk', 'high-risk');
    
    if (score < 30) {
      formGroup.classList.add('low-risk');
    } else if (score < 70) {
      formGroup.classList.add('medium-risk');
    } else {
      formGroup.classList.add('high-risk');
    }
  });
  
  // Format amount display
  const amountFields = [transactionAmount, balanceBefore, balanceAfter];
  amountFields.forEach(field => {
    field.addEventListener('blur', function() {
      if (this.value) {
        console.log(`Amount: ${formatCurrency(this.value)}`);
      }
    });
  });
});

// Expose FormAI instance for external AI service integration
window.operationsFormAI = null;
document.addEventListener('DOMContentLoaded', function() {
  window.operationsFormAI = new FormAI('operationsForm');
});

// Add CSS for risk levels
const style = document.createElement('style');
style.textContent = `
  .form-group.low-risk input {
    border-color: #28a745;
  }
  
  .form-group.medium-risk input {
    border-color: #ffc107;
  }
  
  .form-group.high-risk input {
    border-color: #dc3545;
  }
`;
document.head.appendChild(style);
