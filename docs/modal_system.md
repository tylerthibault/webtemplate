# Custom Modal System Documentation

## Overview

The custom modal system provides a lightweight, accessible, and highly customizable modal implementation that doesn't depend on Bootstrap. It features keyboard navigation, focus management, ARIA compliance, and support for multiple modal types.

## Features

- **Lightweight**: No external dependencies beyond basic CSS and JavaScript
- **Accessible**: Full ARIA support, keyboard navigation, focus management
- **Responsive**: Works on all screen sizes with mobile-optimized layouts
- **Themeable**: Uses CSS custom properties for easy theming and dark mode support
- **Flexible**: Multiple modal types, sizes, and configuration options
- **Event-driven**: Custom events for integration with application logic
- **Form-friendly**: Built-in form handling and validation support

## File Structure

```
src/
├── templates/
│   └── 00_app_components/
│       └── modal_macro.html         # Jinja2 macros for modal creation
├── static/
│   ├── css/
│   │   └── main.css                 # Modal CSS styles (added to existing file)
│   └── js/
│       └── main.js                  # Modal JavaScript functionality
└── controllers/
    └── main.py                      # Route for modal demo page
```

## Usage

### 1. Basic Modal with Jinja2 Macro

```html
{% from '00_app_components/modal_macro.html' import modal %}

{{ modal(
    id='myModal',
    title='Modal Title',
    body='<p>Modal content goes here</p>',
    size='md',
    type='primary',
    footer_buttons=[
        {'text': 'Cancel', 'type': 'secondary', 'action': 'close'},
        {'text': 'Save', 'type': 'primary', 'action': 'submit'}
    ]
) }}
```

### 2. Quick Confirmation Modal

```html
{% from '00_app_components/modal_macro.html' import quick_modal %}

{{ quick_modal(
    id='confirmDelete',
    title='Confirm Delete',
    message='Are you sure you want to delete this item?',
    confirm_text='Delete',
    confirm_type='danger'
) }}
```

### 3. Form Modal

```html
{% from '00_app_components/modal_macro.html' import form_modal %}

{% set form_content %}
<div class="form-group">
    <label for="userName">Name</label>
    <input type="text" id="userName" name="name" class="form-control" required>
</div>
{% endset %}

{{ form_modal(
    id='userForm',
    title='Add User',
    form_content=form_content,
    submit_text='Save User'
) }}
```

### 4. Loading Modal

```html
{% from '00_app_components/modal_macro.html' import loading_modal %}

{{ loading_modal(
    id='loadingModal',
    message='Processing your request...'
) }}
```

## JavaScript API

### Opening Modals

```javascript
// Using data attributes (HTML)
<button data-modal-target="myModal">Open Modal</button>

// Using JavaScript API
ModalManager.open('myModal');

// Getting a modal instance
const modal = AppModal.getModal('myModal');
modal.open();
```

### Closing Modals

```javascript
// Close specific modal
ModalManager.close('myModal');

// Close all open modals
ModalManager.close();

// Using instance
modal.close();
```

### Creating Dynamic Modals

```javascript
const modal = ModalManager.create({
    id: 'dynamicModal',
    title: 'Dynamic Modal',
    body: '<p>This modal was created with JavaScript</p>',
    size: 'md',
    type: 'primary',
    footerButtons: [
        { text: 'Close', type: 'secondary', action: 'close' },
        { text: 'Submit', type: 'primary', action: 'submit' }
    ]
});

modal.open();
```

## Configuration Options

### Modal Macro Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `id` | string | required | Unique identifier for the modal |
| `title` | string | '' | Modal title text |
| `body` | string | '' | Modal body content (HTML allowed) |
| `size` | string | 'md' | Modal size: 'sm', 'md', 'lg', 'xl', 'full' |
| `type` | string | 'primary' | Modal type: 'primary', 'secondary', 'success', 'warning', 'danger' |
| `show_close` | boolean | true | Show close button in header |
| `footer_buttons` | array | none | Array of button configurations |
| `backdrop_close` | boolean | true | Allow closing by clicking backdrop |
| `escape_close` | boolean | true | Allow closing with Escape key |
| `animation` | boolean | true | Enable open/close animations |
| `custom_classes` | string | '' | Additional CSS classes |
| `data_attributes` | dict | {} | Custom data attributes |

### Button Configuration

```javascript
{
    text: 'Button Text',      // Button label
    type: 'primary',          // Button style: 'primary', 'secondary', 'success', 'warning', 'danger'
    action: 'close',          // Button action: 'close', 'submit', or custom
    id: 'button-id',          // Optional button ID
    disabled: false,          // Disable button
    data: {                   // Custom data attributes
        'custom-attr': 'value'
    }
}
```

## Events

The modal system emits custom events that you can listen to:

### Event Types

```javascript
// Modal opened
document.addEventListener('modalOpen', function(e) {
    console.log('Modal opened:', e.detail.modalId);
});

// Modal closed
document.addEventListener('modalClose', function(e) {
    console.log('Modal closed:', e.detail.modalId);
});

// Modal submit button clicked
document.addEventListener('modalSubmit', function(e) {
    console.log('Modal submitted:', e.detail);
    // e.detail contains: { modal, button, modalId }
});

// Form submission in modal
document.addEventListener('modalFormSubmit', function(e) {
    console.log('Form submitted:', e.detail);
    // e.detail contains: { modal, form, button, modalId }
    
    // Prevent default form submission
    e.preventDefault();
    
    // Handle form data
    const formData = new FormData(e.detail.form);
    // ... process form data
});
```

## Styling and Theming

The modal system uses CSS custom properties for theming, making it easy to customize colors and appearance:

### CSS Custom Properties

```css
/* Modal-specific properties */
--bg-overlay: rgba(0, 0, 0, 0.5);     /* Backdrop color */
--shadow-lg: 0 10px 15px -3px ...;    /* Modal shadow */

/* Color system (inherited from main theme) */
--color-primary: #2563eb;
--color-danger: #dc2626;
--bg-primary: #ffffff;
--text-primary: #1e293b;
--border-primary: #e2e8f0;
```

### Dark Mode Support

The modal automatically adapts to dark mode when using the `[data-theme="dark"]` attribute or `prefers-color-scheme: dark`.

### Custom Styling

```css
/* Custom modal variant */
.app-modal-custom {
    border-color: #purple;
}

.app-modal-custom .app-modal-header {
    background: linear-gradient(135deg, #purple, #pink);
}

/* Custom button style */
.app-modal-btn-custom {
    background-color: #purple;
    color: white;
}
```

## Accessibility Features

- **ARIA Compliance**: Proper `role`, `aria-labelledby`, `aria-describedby` attributes
- **Keyboard Navigation**: Tab trapping, Escape key support
- **Focus Management**: Automatic focus on open, restore on close
- **Screen Reader Support**: Proper labeling and descriptions
- **High Contrast Support**: Enhanced borders and colors
- **Reduced Motion**: Respects `prefers-reduced-motion` setting

## Browser Support

- **Modern Browsers**: Chrome 60+, Firefox 55+, Safari 11+, Edge 79+
- **Features Used**: CSS Custom Properties, ES6 Classes, Custom Events
- **Graceful Degradation**: Works without JavaScript (modals won't open but content is accessible)

## Performance Considerations

- **Lightweight**: ~15KB CSS + ~20KB JavaScript (unminified)
- **No Dependencies**: No external libraries required
- **Lazy Loading**: Only initialize modals when needed
- **Memory Management**: Proper event cleanup and garbage collection

## Integration Examples

### Flask Route Integration

```python
@main_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
def delete_user(user_id):
    """Handle user deletion from modal form."""
    
    # Validate CSRF token
    csrf_token = request.form.get('csrf_token', '')
    if not validate_csrf_token(csrf_token):
        return jsonify({'error': 'Invalid CSRF token'}), 400
    
    # Delete user logic
    success = user_service.delete_user(user_id)
    
    if success:
        return jsonify({'message': 'User deleted successfully'})
    else:
        return jsonify({'error': 'Failed to delete user'}), 500
```

### AJAX Form Submission

```javascript
document.addEventListener('modalFormSubmit', function(e) {
    e.preventDefault();
    
    const form = e.detail.form;
    const formData = new FormData(form);
    
    fetch(form.action, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert('Error: ' + data.error);
        } else {
            alert('Success: ' + data.message);
            ModalManager.close(e.detail.modalId);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while processing your request.');
    });
});
```

## Best Practices

1. **Unique IDs**: Always use unique IDs for modals to avoid conflicts
2. **Semantic HTML**: Use proper form elements and labels in modal content
3. **Error Handling**: Always handle form submission errors gracefully
4. **Loading States**: Show loading indicators for async operations
5. **Validation**: Validate forms both client-side and server-side
6. **CSRF Protection**: Include CSRF tokens in all forms
7. **Mobile UX**: Test modals on mobile devices for usability
8. **Performance**: Avoid creating too many modals simultaneously

## Troubleshooting

### Common Issues

1. **Modal not opening**: Check that the modal ID matches the trigger's `data-modal-target`
2. **Styles not applied**: Ensure `main.css` is properly loaded
3. **JavaScript errors**: Check browser console for initialization errors
4. **Focus issues**: Verify that focusable elements are not disabled or hidden
5. **Z-index conflicts**: Adjust CSS z-index values if modals appear behind other elements

### Debug Mode

Enable debug logging:

```javascript
// Add to your JavaScript console
AppModal.debug = true;
```

This will log all modal events and state changes to the console.