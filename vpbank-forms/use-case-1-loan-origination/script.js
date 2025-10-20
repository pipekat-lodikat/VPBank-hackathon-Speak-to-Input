// Use Case 1 - Loan Origination Form Script

document.addEventListener('DOMContentLoaded', function() {
  const form = document.getElementById('loanOriginationForm');
  const clearBtn = document.getElementById('clearBtn');
  const aiTestBtn = document.getElementById('aiTestBtn');
  
  // Initialize common features
  initializeCommonFeatures(form);
  
  // Initialize AI Integration
  const formAI = new FormAI('loanOriginationForm');
  
  // Set default application date to today
  const applicationDateField = document.getElementById('applicationDate');
  applicationDateField.value = new Date().toISOString().split('T')[0];
  
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
      'Bạn có chắc chắn muốn gửi đơn vay vốn này không?',
      () => {
        // Simulate submission
        console.log('Submitting loan application:', formData);
        showAlert('Đơn vay đã được gửi thành công!', 'success');
        clearFormDraft('loanOriginationForm');
        form.reset();
        applicationDateField.value = new Date().toISOString().split('T')[0];
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
        applicationDateField.value = new Date().toISOString().split('T')[0];
        showAlert('Form đã được xóa', 'info');
      }
    );
  });
  
  // AI Test button - simulates AI filling the form
  aiTestBtn.addEventListener('click', async function() {
    // Example: "Điền khách hàng Nguyễn Văn An vay 500 triệu, kỳ hạn 24 tháng"
    const testData = {
      customerName: 'Nguyễn Văn An',
      customerId: '001234567890',
      phoneNumber: '0901234567',
      email: 'nguyenvanan@example.com',
      address: '123 Nguyễn Trãi, Phường Bến Thành, Quận 1, TP.HCM',
      dateOfBirth: '1990-05-15',
      gender: 'male',
      loanAmount: '500000000',
      loanTerm: '24',
      loanPurpose: 'personal',
      applicationDate: new Date().toISOString().split('T')[0],
      employmentStatus: 'employed',
      companyName: 'Công ty ABC',
      monthlyIncome: '25000000',
      workAddress: '456 Lê Lợi, Quận 1, TP.HCM',
      collateralType: 'real-estate',
      collateralValue: '800000000',
      collateralDescription: 'Căn hộ chung cư 80m2 tại Quận 1'
    };
    
    const result = formAI.fillForm(testData);
    
    if (result.success) {
      showAlert(`AI đã điền thành công ${result.filledFields.length} trường`, 'success');
    } else {
      showAlert('Có lỗi khi AI điền form', 'error');
      console.error('AI Fill errors:', result.errors);
    }
  });
  
  // Format currency inputs on blur
  const currencyInputs = ['loanAmount', 'monthlyIncome', 'collateralValue'];
  currencyInputs.forEach(inputId => {
    const input = document.getElementById(inputId);
    input.addEventListener('blur', function() {
      if (this.value) {
        // Could add formatting here if needed
        console.log(`Amount entered: ${formatCurrency(this.value)}`);
      }
    });
  });
  
  // Update collateral fields based on type
  const collateralType = document.getElementById('collateralType');
  const collateralValue = document.getElementById('collateralValue');
  const collateralDescription = document.getElementById('collateralDescription');
  
  collateralType.addEventListener('change', function() {
    if (this.value === 'none') {
      collateralValue.required = false;
      collateralDescription.required = false;
      collateralValue.value = '';
      collateralDescription.value = '';
    } else {
      collateralValue.required = true;
    }
  });
});

// Expose FormAI instance for external AI service integration
window.loanFormAI = null;
document.addEventListener('DOMContentLoaded', function() {
  window.loanFormAI = new FormAI('loanOriginationForm');
});
