// Use Case 4 - Compliance Reporting Form Script

document.addEventListener('DOMContentLoaded', function() {
  const form = document.getElementById('complianceForm');
  const clearBtn = document.getElementById('clearBtn');
  const aiTestBtn = document.getElementById('aiTestBtn');
  
  // Initialize common features
  initializeCommonFeatures(form);
  
  // Initialize AI Integration
  const formAI = new FormAI('complianceForm');
  
  // Set default submission date to today
  const submissionDateField = document.getElementById('submissionDate');
  submissionDateField.value = new Date().toISOString().split('T')[0];
  
  // Set default reporting period to current month
  const reportingPeriod = document.getElementById('reportingPeriod');
  const today = new Date();
  const currentMonth = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}`;
  reportingPeriod.value = currentMonth;
  
  // Auto-generate report ID
  const reportId = document.getElementById('reportId');
  const generateReportId = () => {
    const date = new Date();
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const random = String(Math.floor(Math.random() * 1000)).padStart(3, '0');
    reportId.value = `BC-${year}${month}-${random}`;
  };
  if (!reportId.value) {
    generateReportId();
  }
  
  // Form submission
  form.addEventListener('submit', function(e) {
    e.preventDefault();
    
    if (!validateForm(form)) {
      showAlert('Vui lòng kiểm tra lại thông tin đã nhập', 'error');
      return;
    }
    
    const formData = getFormData(form);
    
    showModal(
      'Xác Nhận Gửi Báo Cáo',
      'Bạn có chắc chắn muốn gửi báo cáo tuân thủ này không?',
      () => {
        // Simulate submission
        console.log('Submitting compliance report:', formData);
        showAlert('Báo cáo đã được gửi thành công!', 'success');
        clearFormDraft('complianceForm');
        form.reset();
        submissionDateField.value = new Date().toISOString().split('T')[0];
        reportingPeriod.value = currentMonth;
        generateReportId();
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
        reportingPeriod.value = currentMonth;
        generateReportId();
        showAlert('Form đã được xóa', 'info');
      }
    );
  });
  
  // AI Test button - simulates AI filling the form
  aiTestBtn.addEventListener('click', async function() {
    // Example: "Điền báo cáo AML tháng 9, trạng thái hoàn thành, không vi phạm"
    const testData = {
      reportId: 'BC-202409-123',
      reportType: 'aml',
      reportingPeriod: '2024-09',
      submissionDate: new Date().toISOString().split('T')[0],
      reportTitle: 'Báo cáo AML tháng 9/2024',
      complianceOfficer: 'Lê Thị Hương',
      officerEmail: 'le.huong@vpbank.com.vn',
      officerPosition: 'Chuyên viên tuân thủ cao cấp',
      department: 'Risk & Compliance',
      status: 'completed',
      casesReviewed: '150',
      highRiskCases: '5',
      violationsFound: 'none',
      actionsTaken: 'Đã xem xét và phân tích toàn bộ 150 trường hợp. Thực hiện kiểm tra chuyên sâu 5 trường hợp rủi ro cao. Tất cả đều đạt yêu cầu tuân thủ.',
      preventiveMeasures: 'Tăng cường đào tạo nhân viên về quy định AML. Cập nhật hệ thống cảnh báo tự động.',
      followUpRequired: 'no',
      overallRisk: 'low',
      riskAnalysis: 'Mức độ rủi ro tổng thể trong tháng 9 ở mức thấp, không phát hiện hoạt động bất thường.',
      executiveSummary: 'Báo cáo AML tháng 9/2024 đã hoàn thành. Không phát hiện vi phạm. Tất cả giao dịch tuân thủ quy định.'
    };
    
    const result = formAI.fillForm(testData);
    
    if (result.success) {
      showAlert(`AI đã điền thành công ${result.filledFields.length} trường`, 'success');
    } else {
      showAlert('Có lỗi khi AI điền form', 'error');
      console.error('AI Fill errors:', result.errors);
    }
  });
  
  // Violations found change handler
  const violationsFound = document.getElementById('violationsFound');
  const violationDetailsGroup = document.getElementById('violationDetailsGroup');
  const violationDetails = document.getElementById('violationDetails');
  
  violationsFound.addEventListener('change', function() {
    if (this.value === 'minor' || this.value === 'major') {
      violationDetailsGroup.style.display = 'block';
      violationDetails.required = true;
    } else {
      violationDetailsGroup.style.display = 'none';
      violationDetails.required = false;
      violationDetails.value = '';
    }
  });
  
  // Follow-up required change handler
  const followUpRequired = document.getElementById('followUpRequired');
  const followUpDateGroup = document.getElementById('followUpDateGroup');
  const followUpDate = document.getElementById('followUpDate');
  
  followUpRequired.addEventListener('change', function() {
    if (this.value === 'yes') {
      followUpDateGroup.style.display = 'block';
      followUpDate.required = true;
      // Set default follow-up date to 30 days from now
      const nextMonth = new Date();
      nextMonth.setDate(nextMonth.getDate() + 30);
      followUpDate.value = nextMonth.toISOString().split('T')[0];
    } else {
      followUpDateGroup.style.display = 'none';
      followUpDate.required = false;
      followUpDate.value = '';
    }
  });
  
  // Calculate high-risk percentage
  const casesReviewed = document.getElementById('casesReviewed');
  const highRiskCases = document.getElementById('highRiskCases');
  
  function updateRiskPercentage() {
    if (casesReviewed.value && highRiskCases.value) {
      const total = parseInt(casesReviewed.value);
      const high = parseInt(highRiskCases.value);
      
      if (high > total) {
        showAlert('Số trường hợp rủi ro cao không thể lớn hơn tổng số trường hợp', 'error');
        highRiskCases.value = total;
      }
      
      const percentage = ((high / total) * 100).toFixed(2);
      console.log(`High risk percentage: ${percentage}%`);
    }
  }
  
  casesReviewed.addEventListener('change', updateRiskPercentage);
  highRiskCases.addEventListener('change', updateRiskPercentage);
  
  // Report type change handler - auto-update title
  const reportType = document.getElementById('reportType');
  const reportTitle = document.getElementById('reportTitle');
  
  reportType.addEventListener('change', function() {
    if (this.value && reportingPeriod.value) {
      const period = new Date(reportingPeriod.value);
      const month = period.getMonth() + 1;
      const year = period.getFullYear();
      
      const typeNames = {
        'aml': 'AML',
        'kyc': 'KYC',
        'risk-assessment': 'Đánh giá rủi ro',
        'audit': 'Kiểm toán nội bộ',
        'regulatory': 'Báo cáo định kỳ NHNN',
        'fraud': 'Phát hiện gian lận'
      };
      
      const typeName = typeNames[this.value] || this.value;
      reportTitle.value = `Báo cáo ${typeName} tháng ${month}/${year}`;
    }
  });
  
  reportingPeriod.addEventListener('change', function() {
    // Trigger report title update
    if (reportType.value) {
      reportType.dispatchEvent(new Event('change'));
    }
  });
});

// Expose FormAI instance for external AI service integration
window.complianceFormAI = null;
document.addEventListener('DOMContentLoaded', function() {
  window.complianceFormAI = new FormAI('complianceForm');
});
