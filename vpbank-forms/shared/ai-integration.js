// VPBank Forms - AI Integration Library

class FormAI {
  constructor(formId) {
    this.formId = formId;
    this.form = document.getElementById(formId);
    if (!this.form) {
      throw new Error(`Form with id "${formId}" not found`);
    }
  }

  /**
   * Fill form with AI-provided data
   * @param {Object} data - Key-value pairs where key is field name
   * @returns {Object} - Result with success status and filled fields
   */
  fillForm(data) {
    const results = {
      success: true,
      filledFields: [],
      failedFields: [],
      errors: []
    };

    try {
      Object.keys(data).forEach(fieldName => {
        const field = this.form.querySelector(`[name="${fieldName}"]`);
        
        if (!field) {
          results.failedFields.push(fieldName);
          results.errors.push(`Field "${fieldName}" not found`);
          return;
        }

        // Fill the field based on type
        try {
          if (field.type === 'checkbox') {
            field.checked = Boolean(data[fieldName]);
          } else if (field.type === 'radio') {
            const radio = this.form.querySelector(`[name="${fieldName}"][value="${data[fieldName]}"]`);
            if (radio) radio.checked = true;
          } else {
            field.value = data[fieldName];
          }

          // Trigger input event for validation
          field.dispatchEvent(new Event('input', { bubbles: true }));
          field.dispatchEvent(new Event('change', { bubbles: true }));

          results.filledFields.push(fieldName);
        } catch (error) {
          results.failedFields.push(fieldName);
          results.errors.push(`Error filling "${fieldName}": ${error.message}`);
        }
      });

      results.success = results.failedFields.length === 0;
      
      // Highlight filled fields
      this.highlightFilledFields(results.filledFields);

      return results;
    } catch (error) {
      results.success = false;
      results.errors.push(`General error: ${error.message}`);
      return results;
    }
  }

  /**
   * Validate the current form state
   * @returns {Object} - Validation result
   */
  validateForm() {
    const results = {
      isValid: true,
      errors: [],
      invalidFields: []
    };

    const fields = this.form.querySelectorAll('input, select, textarea');
    
    fields.forEach(field => {
      if (!validateField(field)) {
        results.isValid = false;
        results.invalidFields.push(field.name);
        
        const formGroup = field.closest('.form-group');
        const errorMessage = formGroup.querySelector('.error-message');
        if (errorMessage) {
          results.errors.push({
            field: field.name,
            message: errorMessage.textContent
          });
        }
      }
    });

    return results;
  }

  /**
   * Get form data as JSON
   * @returns {Object} - Form data
   */
  getFormData() {
    return getFormData(this.form);
  }

  /**
   * Submit form programmatically
   * @param {Boolean} skipConfirmation - Skip confirmation dialog
   * @returns {Promise} - Submission result
   */
  async submitForm(skipConfirmation = false) {
    // Validate first
    const validation = this.validateForm();
    
    if (!validation.isValid) {
      return {
        success: false,
        message: 'Form validation failed',
        errors: validation.errors
      };
    }

    // Get form data
    const formData = this.getFormData();

    return new Promise((resolve) => {
      const doSubmit = () => {
        // Simulate submission (replace with actual API call)
        console.log('Submitting form data:', formData);
        
        // Show success message
        showAlert('Form submitted successfully!', 'success');
        
        // Clear draft
        clearFormDraft(this.formId);
        
        // Reset form
        this.form.reset();
        
        resolve({
          success: true,
          message: 'Form submitted successfully',
          data: formData
        });
      };

      if (skipConfirmation) {
        doSubmit();
      } else {
        showModal(
          'Xác nhận gửi',
          'Bạn có chắc chắn muốn gửi biểu mẫu này không?',
          doSubmit,
          () => {
            resolve({
              success: false,
              message: 'Submission cancelled by user'
            });
          }
        );
      }
    });
  }

  /**
   * Reset form to initial state
   */
  resetForm() {
    this.form.reset();
    
    // Clear all validation states
    const formGroups = this.form.querySelectorAll('.form-group');
    formGroups.forEach(group => {
      group.classList.remove('error', 'success', 'ai-filled');
    });

    // Clear draft
    clearFormDraft(this.formId);
  }

  /**
   * Highlight fields filled by AI
   * @param {Array} fieldNames - Array of field names
   */
  highlightFilledFields(fieldNames) {
    // Remove previous highlights
    const previousHighlights = this.form.querySelectorAll('.ai-filled');
    previousHighlights.forEach(el => el.classList.remove('ai-filled'));

    // Add new highlights
    fieldNames.forEach(fieldName => {
      const field = this.form.querySelector(`[name="${fieldName}"]`);
      if (field) {
        const formGroup = field.closest('.form-group');
        if (formGroup) {
          formGroup.classList.add('ai-filled');
        }
      }
    });
  }

  /**
   * Parse Vietnamese natural language input to form data
   * This is a simple example - real implementation would use AI service
   * @param {String} input - Natural language input
   * @returns {Object} - Parsed data
   */
  parseNaturalLanguage(input) {
    // This is a placeholder - in production, this would call your AI service
    console.log('Parsing natural language input:', input);
    
    // Example implementation for demonstration
    const data = {};
    
    // Simple pattern matching (replace with actual AI parsing)
    const patterns = {
      name: /(?:khách hàng|tên)\s+([A-Za-zÀ-ỹ\s]+?)(?:\s+vay|\s+ID|,|$)/i,
      amount: /(\d+(?:\.\d+)?)\s*(?:triệu|tr|million)/i,
      term: /(?:kỳ hạn|thời hạn)\s*(\d+)\s*tháng/i,
      date: /ngày\s*(\d+)\s*tháng\s*(\d+)/i
    };

    // Extract name
    const nameMatch = input.match(patterns.name);
    if (nameMatch) data.customerName = nameMatch[1].trim();

    // Extract amount
    const amountMatch = input.match(patterns.amount);
    if (amountMatch) data.loanAmount = parseFloat(amountMatch[1]) * 1000000;

    // Extract term
    const termMatch = input.match(patterns.term);
    if (termMatch) data.loanTerm = termMatch[1];

    // Extract date
    const dateMatch = input.match(patterns.date);
    if (dateMatch) {
      const day = dateMatch[1];
      const month = dateMatch[2];
      const year = new Date().getFullYear();
      data.applicationDate = `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`;
    }

    return data;
  }

  /**
   * Process AI command
   * @param {String} command - Natural language command
   * @returns {Promise} - Processing result
   */
  async processAICommand(command) {
    try {
      // Parse the command
      const parsedData = this.parseNaturalLanguage(command);
      
      // Fill the form
      const fillResult = this.fillForm(parsedData);
      
      if (!fillResult.success) {
        return {
          success: false,
          message: 'Failed to fill some fields',
          errors: fillResult.errors
        };
      }

      // Validate the filled form
      const validation = this.validateForm();
      
      return {
        success: true,
        message: 'Form filled successfully',
        filledFields: fillResult.filledFields,
        validation: validation
      };
    } catch (error) {
      return {
        success: false,
        message: 'Error processing AI command',
        error: error.message
      };
    }
  }
}

// Add CSS for AI-filled fields
const style = document.createElement('style');
style.textContent = `
  .form-group.ai-filled {
    position: relative;
  }
  
  .form-group.ai-filled::before {
    content: 'AI';
    position: absolute;
    top: 8px;
    right: 8px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    font-size: 10px;
    font-weight: bold;
    padding: 2px 6px;
    border-radius: 3px;
    z-index: 10;
  }
  
  .form-group.ai-filled input,
  .form-group.ai-filled select,
  .form-group.ai-filled textarea {
    background-color: #f0f4ff;
    border-color: #667eea;
  }
`;
document.head.appendChild(style);

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
  module.exports = FormAI;
}
