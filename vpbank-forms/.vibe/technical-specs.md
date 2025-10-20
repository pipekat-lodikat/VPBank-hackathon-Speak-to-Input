# Technical Specifications - VPBank Forms

## Architecture Overview

### Frontend Architecture
```
┌─────────────────────────────────────┐
│         Browser (Client)            │
├─────────────────────────────────────┤
│  HTML Forms (5 Use Cases)           │
│  ├─ Semantic HTML5                  │
│  ├─ Responsive CSS3                 │
│  └─ Vanilla JavaScript              │
├─────────────────────────────────────┤
│  AI Integration Layer               │
│  ├─ Form Data Extraction            │
│  ├─ Field Mapping                   │
│  ├─ Validation Engine               │
│  └─ Submission Handler              │
├─────────────────────────────────────┤
│  AI Service (External)              │
│  ├─ NLP Parser                      │
│  ├─ Form Filler                     │
│  └─ Confirmation Manager            │
└─────────────────────────────────────┘
```

## Technology Stack

### Core Technologies
- **HTML5**: Semantic markup, form elements, data attributes
- **CSS3**: Flexbox, Grid, Media Queries, CSS Variables
- **JavaScript (ES6+)**: Vanilla JS, no frameworks required

### Browser APIs Used
- Form Validation API
- Local Storage API (for form drafts)
- Fetch API (for future backend integration)
- Custom Events (for AI integration)

## Form Structure

### Standard Form Template
```html
<form id="form-name" class="vpbank-form">
  <div class="form-header">
    <h1>Form Title</h1>
    <p>Form Description</p>
  </div>
  
  <div class="form-section">
    <h2>Section Title</h2>
    <div class="form-group">
      <label for="field-id">Field Label</label>
      <input type="text" id="field-id" name="field-name" required>
      <span class="error-message"></span>
    </div>
  </div>
  
  <div class="form-actions">
    <button type="button" class="btn-secondary">Clear</button>
    <button type="submit" class="btn-primary">Submit</button>
  </div>
</form>
```

## CSS Architecture

### Naming Convention
- BEM methodology for CSS classes
- Utility classes for common styles
- CSS variables for theming

### Color Scheme (VPBank Brand)
```css
:root {
  --primary-color: #00B14F;      /* VPBank Green */
  --secondary-color: #0066CC;    /* VPBank Blue */
  --accent-color: #FF6B00;       /* Warning Orange */
  --text-color: #333333;
  --text-secondary: #666666;
  --background: #FFFFFF;
  --background-alt: #F5F5F5;
  --border-color: #DDDDDD;
  --error-color: #DC3545;
  --success-color: #28A745;
}
```

## JavaScript Architecture

### Core Functions

#### Form Initialization
```javascript
function initializeForm(formId) {
  // Set up event listeners
  // Initialize validation
  // Load saved draft if exists
}
```

#### AI Integration API
```javascript
class FormAI {
  // Fill form with AI-provided data
  fillForm(data) { }
  
  // Validate current form state
  validateForm() { }
  
  // Get form data as JSON
  getFormData() { }
  
  // Submit form programmatically
  submitForm() { }
  
  // Reset form
  resetForm() { }
}
```

#### Validation Rules
```javascript
const validationRules = {
  required: (value) => value.trim() !== '',
  email: (value) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value),
  phone: (value) => /^[0-9]{10}$/.test(value),
  number: (value) => !isNaN(value) && value >= 0,
  date: (value) => !isNaN(Date.parse(value))
};
```

## Form Fields Specification

### Input Types
1. **Text Input**: Name, ID, Phone, Email
2. **Number Input**: Amount, Income, Count
3. **Date Input**: Application Date, Transaction Date
4. **Select Dropdown**: Loan Term, Status, Type
5. **Textarea**: Address, Notes, Reason
6. **Radio Buttons**: Yes/No options
7. **Checkboxes**: Terms acceptance

### Validation Requirements
- All required fields marked with asterisk (*)
- Real-time validation on blur
- Form-level validation on submit
- Clear error messages in Vietnamese
- Success feedback after submission

## Responsive Breakpoints
```css
/* Mobile First Approach */
/* Base styles: 320px - 767px */

/* Tablet: 768px - 1023px */
@media (min-width: 768px) { }

/* Desktop: 1024px+ */
@media (min-width: 1024px) { }

/* Large Desktop: 1440px+ */
@media (min-width: 1440px) { }
```

## Performance Targets
- First Contentful Paint: < 1.0s
- Time to Interactive: < 2.0s
- Lighthouse Score: > 90
- Form Submission: < 500ms

## Security Considerations
1. **Input Sanitization**: All user inputs sanitized before display
2. **XSS Prevention**: Use textContent instead of innerHTML where possible
3. **CSRF Protection**: Token-based (for future backend)
4. **Data Validation**: Both client and server-side (future)

## Accessibility Standards
- WCAG 2.1 Level AA compliance
- Semantic HTML elements
- ARIA labels where needed
- Keyboard navigation support
- Screen reader friendly
- High contrast support
- Focus indicators visible

## Error Handling
```javascript
try {
  // Form operation
} catch (error) {
  console.error('Form error:', error);
  showErrorMessage('Đã xảy ra lỗi. Vui lòng thử lại.');
}
```

## Future Enhancements
1. Backend API integration
2. Real-time collaboration
3. Form analytics
4. Advanced AI features
5. Multi-language support
6. Dark mode
7. Offline support with Service Workers
