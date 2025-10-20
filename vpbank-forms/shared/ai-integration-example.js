// AI Integration Example - How to connect your AI service with VPBank Forms

/**
 * EXAMPLE 1: Basic AI Integration
 * Connect your AI service to auto-fill forms
 */

class VPBankAIService {
  constructor() {
    this.forms = {
      loan: new FormAI('loanOriginationForm'),
      crm: new FormAI('crmUpdateForm'),
      hr: new FormAI('hrWorkflowForm'),
      compliance: new FormAI('complianceForm'),
      operations: new FormAI('operationsForm')
    };
  }

  /**
   * Process voice command in Vietnamese
   * @param {string} voiceInput - Voice command from user
   * @param {string} formType - Type of form (loan, crm, hr, compliance, operations)
   */
  async processVoiceCommand(voiceInput, formType) {
    console.log(`Processing: "${voiceInput}" for ${formType} form`);
    
    try {
      // Step 1: Call your AI service to parse the command
      const parsedData = await this.callAIParsingService(voiceInput);
      
      // Step 2: Get the appropriate form
      const formAI = this.forms[formType];
      if (!formAI) {
        throw new Error(`Unknown form type: ${formType}`);
      }
      
      // Step 3: Fill the form
      const fillResult = formAI.fillForm(parsedData);
      
      if (!fillResult.success) {
        console.error('Failed to fill some fields:', fillResult.errors);
        return {
          success: false,
          message: 'Không thể điền một số trường',
          errors: fillResult.errors
        };
      }
      
      // Step 4: Validate
      const validation = formAI.validateForm();
      
      if (!validation.isValid) {
        return {
          success: false,
          message: 'Dữ liệu không hợp lệ',
          errors: validation.errors
        };
      }
      
      // Step 5: Ask for confirmation
      const confirmed = await this.askForConfirmation(parsedData);
      
      if (!confirmed) {
        return {
          success: false,
          message: 'Người dùng hủy'
        };
      }
      
      // Step 6: Submit
      const submitResult = await formAI.submitForm(true);
      
      return {
        success: true,
        message: 'Form đã được gửi thành công',
        data: submitResult.data
      };
      
    } catch (error) {
      console.error('AI Processing error:', error);
      return {
        success: false,
        message: 'Lỗi xử lý AI',
        error: error.message
      };
    }
  }

  /**
   * Call your AI parsing service
   * Replace this with actual API call to your AI service
   */
  async callAIParsingService(input) {
    // TODO: Replace with actual API call
    // const response = await fetch('https://your-ai-service.com/parse', {
    //   method: 'POST',
    //   headers: { 'Content-Type': 'application/json' },
    //   body: JSON.stringify({ input, language: 'vi' })
    // });
    // return response.json();
    
    // For now, use the built-in parser
    return this.parseVietnamese(input);
  }

  /**
   * Simple Vietnamese parser (replace with your AI)
   */
  parseVietnamese(input) {
    const data = {};
    
    // Name extraction
    const nameMatch = input.match(/(?:khách hàng|tên|nhân viên)\s+([A-ZÀ-Ỹ][a-zà-ỹ]+(?:\s+[A-ZÀ-Ỹ][a-zà-ỹ]+)+)/i);
    if (nameMatch) {
      data.customerName = nameMatch[1].trim();
      data.employeeName = nameMatch[1].trim();
    }
    
    // Amount extraction
    const amountMatch = input.match(/(\d+(?:\.\d+)?)\s*(?:triệu|tr|million)/i);
    if (amountMatch) {
      data.loanAmount = parseFloat(amountMatch[1]) * 1000000;
      data.transactionAmount = parseFloat(amountMatch[1]) * 1000000;
    }
    
    // Term extraction
    const termMatch = input.match(/(?:kỳ hạn|thời hạn)\s*(\d+)\s*tháng/i);
    if (termMatch) {
      data.loanTerm = termMatch[1];
    }
    
    // Date extraction
    const dateMatch = input.match(/ngày\s*(\d+)\s*tháng\s*(\d+)/i);
    if (dateMatch) {
      const year = new Date().getFullYear();
      const month = dateMatch[2].padStart(2, '0');
      const day = dateMatch[1].padStart(2, '0');
      data.transactionDate = `${year}-${month}-${day}`;
      data.startDate = `${year}-${month}-${day}`;
    }
    
    // Address extraction
    const addressMatch = input.match(/(?:địa chỉ|address)\s+(.+?)(?:\.|,|$)/i);
    if (addressMatch) {
      data.address = addressMatch[1].trim();
    }
    
    return data;
  }

  /**
   * Ask user for confirmation
   */
  async askForConfirmation(data) {
    return new Promise((resolve) => {
      const message = `Xác nhận thông tin:\n${JSON.stringify(data, null, 2)}`;
      showModal(
        'Xác Nhận Dữ Liệu',
        message,
        () => resolve(true),
        () => resolve(false)
      );
    });
  }
}

/**
 * EXAMPLE 2: Real-time Voice Recognition
 */

class VoiceAIIntegration {
  constructor() {
    this.aiService = new VPBankAIService();
    this.recognition = null;
    this.isListening = false;
  }

  /**
   * Start listening for voice commands
   */
  startListening(formType) {
    if (!('webkitSpeechRecognition' in window)) {
      alert('Trình duyệt không hỗ trợ nhận dạng giọng nói');
      return;
    }

    this.recognition = new webkitSpeechRecognition();
    this.recognition.lang = 'vi-VN';
    this.recognition.continuous = false;
    this.recognition.interimResults = false;

    this.recognition.onstart = () => {
      this.isListening = true;
      console.log('🎤 Đang nghe...');
      showAlert('Đang nghe... Hãy nói lệnh của bạn', 'info');
    };

    this.recognition.onresult = async (event) => {
      const transcript = event.results[0][0].transcript;
      console.log('📝 Nhận được:', transcript);
      
      showAlert(`Đang xử lý: "${transcript}"`, 'info');
      
      const result = await this.aiService.processVoiceCommand(transcript, formType);
      
      if (result.success) {
        showAlert('✅ ' + result.message, 'success');
      } else {
        showAlert('❌ ' + result.message, 'error');
      }
    };

    this.recognition.onerror = (event) => {
      console.error('Speech recognition error:', event.error);
      showAlert('Lỗi nhận dạng giọng nói: ' + event.error, 'error');
      this.isListening = false;
    };

    this.recognition.onend = () => {
      this.isListening = false;
      console.log('🔇 Dừng nghe');
    };

    this.recognition.start();
  }

  stopListening() {
    if (this.recognition && this.isListening) {
      this.recognition.stop();
    }
  }
}

/**
 * EXAMPLE 3: Real-world Usage Scenarios
 */

// Scenario 1: Loan Application
async function handleLoanApplication() {
  const ai = new VPBankAIService();
  
  // Voice command from RM
  const command = "Điền khách hàng Nguyễn Văn An vay 500 triệu, kỳ hạn 24 tháng, mục đích mua nhà";
  
  const result = await ai.processVoiceCommand(command, 'loan');
  
  if (result.success) {
    console.log('✅ Loan application submitted:', result.data);
  }
}

// Scenario 2: CRM Update
async function handleCRMUpdate() {
  const ai = new VPBankAIService();
  
  const command = "Cập nhật địa chỉ khách Nguyễn Văn Bình thành 25A Nguyễn Trãi, Quận 1";
  
  const result = await ai.processVoiceCommand(command, 'crm');
  
  if (result.success) {
    console.log('✅ CRM updated:', result.data);
  }
}

// Scenario 3: HR Leave Request
async function handleLeaveRequest() {
  const ai = new VPBankAIService();
  
  const command = "Tạo đơn nghỉ phép từ 22 đến 24 tháng 10, lý do cá nhân";
  
  const result = await ai.processVoiceCommand(command, 'hr');
  
  if (result.success) {
    console.log('✅ Leave request submitted:', result.data);
  }
}

// Scenario 4: Compliance Report
async function handleComplianceReport() {
  const ai = new VPBankAIService();
  
  const command = "Điền báo cáo AML tháng 9, trạng thái hoàn thành, không vi phạm";
  
  const result = await ai.processVoiceCommand(command, 'compliance');
  
  if (result.success) {
    console.log('✅ Compliance report submitted:', result.data);
  }
}

// Scenario 5: Transaction Validation
async function handleTransactionValidation() {
  const ai = new VPBankAIService();
  
  const command = "Kiểm tra giao dịch khách Nguyễn Thị Hoa ngày 17 tháng 10, số tiền 350 triệu";
  
  const result = await ai.processVoiceCommand(command, 'operations');
  
  if (result.success) {
    console.log('✅ Transaction validated:', result.data);
  }
}

/**
 * EXAMPLE 4: Add Voice Button to Forms
 */

function addVoiceButtonToForms() {
  // Add voice button to each form
  const forms = document.querySelectorAll('.vpbank-form');
  
  forms.forEach(form => {
    const formActions = form.querySelector('.form-actions');
    
    // Create voice button
    const voiceBtn = document.createElement('button');
    voiceBtn.type = 'button';
    voiceBtn.className = 'btn-secondary';
    voiceBtn.innerHTML = '🎤 Điền Bằng Giọng Nói';
    voiceBtn.id = 'voiceBtn';
    
    // Add to form
    formActions.insertBefore(voiceBtn, formActions.firstChild);
    
    // Get form type
    const formId = form.id;
    let formType = 'loan';
    if (formId.includes('crm')) formType = 'crm';
    if (formId.includes('hr')) formType = 'hr';
    if (formId.includes('compliance')) formType = 'compliance';
    if (formId.includes('operations')) formType = 'operations';
    
    // Add click handler
    const voiceAI = new VoiceAIIntegration();
    voiceBtn.addEventListener('click', () => {
      voiceAI.startListening(formType);
    });
  });
}

/**
 * EXAMPLE 5: Batch Processing
 */

async function processBatchCommands(commands) {
  const ai = new VPBankAIService();
  const results = [];
  
  for (const cmd of commands) {
    const result = await ai.processVoiceCommand(cmd.text, cmd.formType);
    results.push({
      command: cmd.text,
      result: result
    });
  }
  
  return results;
}

// Usage example
const batchCommands = [
  { text: "Điền khách hàng A vay 100 triệu", formType: 'loan' },
  { text: "Điền khách hàng B vay 200 triệu", formType: 'loan' },
  { text: "Cập nhật địa chỉ khách C", formType: 'crm' }
];

// processBatchCommands(batchCommands).then(results => {
//   console.log('Batch processing completed:', results);
// });

/**
 * EXAMPLE 6: Export for use in your application
 */

// Export classes for use in your app
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    VPBankAIService,
    VoiceAIIntegration,
    addVoiceButtonToForms,
    processBatchCommands
  };
}

// Make available globally
window.VPBankAIService = VPBankAIService;
window.VoiceAIIntegration = VoiceAIIntegration;

/**
 * USAGE INSTRUCTIONS:
 * 
 * 1. Include this file after the form scripts:
 *    <script src="ai-integration-example.js"></script>
 * 
 * 2. Initialize the AI service:
 *    const ai = new VPBankAIService();
 * 
 * 3. Process voice commands:
 *    await ai.processVoiceCommand(command, formType);
 * 
 * 4. Add voice buttons to forms:
 *    addVoiceButtonToForms();
 * 
 * 5. Use voice recognition:
 *    const voice = new VoiceAIIntegration();
 *    voice.startListening('loan');
 */

console.log('✅ AI Integration Example loaded');
console.log('📝 See comments in ai-integration-example.js for usage instructions');
