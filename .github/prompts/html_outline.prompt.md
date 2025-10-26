---
mode: agent
---

# HTML Prototype Generator Prompt

## Objective
Generate simple, basic HTML files for quick prototyping using the existing CSS framework and Jinja2 template structure. Focus on clean, semantic HTML with minimal styling requirements.

## Template Structure Requirements

### Base Template Inheritance
All HTML files must extend either:
- `bases/public.html` - For unauthenticated pages
- `bases/private.html` - For authenticated pages

Both extend `bases/main.html` which provides the core structure with these blocks:
- `{% block head_content %}` - Additional meta tags, page-specific head content
- `{% block styles %}` - CSS links and style declarations
- `{% block header %}` - Navigation and header content
- `{% block content %}` - Main page content (PRIMARY BLOCK)
- `{% block footer %}` - Footer content
- `{% block scripts %}` - JavaScript includes and scripts

### Required File Structure
```jinja2
{% extends 'bases/public.html' %}
<!-- OR -->
{% extends 'bases/private.html' %}

{% block content %}
    <!-- Your HTML content here -->
{% endblock content %}
```

## CSS Framework Available

### Available CSS Files
- `{{ url_for('static', filename='css/main.css') }}` - Primary stylesheet with variables and utilities
- `{{ url_for('static', filename='css/bootstrap-overide.css') }}` - Bootstrap customizations
- Bootstrap CSS files in `css/bootstrapcss/` directory (bootstrap.min.css, etc.)

### CSS Variables Available (from main.css)
```css
/* Color Scheme Variables */
--color-primary: #2563eb
--color-secondary: #64748b  
--color-accent: #059669
--color-warning: #d97706
--color-danger: #dc2626
--color-success: #16a34a

/* Background/Text Colors */
--bg-primary, --bg-secondary, --bg-accent
--text-primary, --text-secondary, --text-muted
--border-color, --shadow-color
```

### Bootstrap Classes Available
Standard Bootstrap 5 classes are available through the included Bootstrap CSS files.

## Styling Guidelines

### DO Include CSS This Way:
```jinja2
{% block styles %}
    <link rel="stylesheet" href="{{ url_for('static', filename='css/main.css') }}">
    <!-- Add Bootstrap if needed -->
    <link rel="stylesheet" href="{{ url_for('static', filename='css/bootstrapcss/bootstrap.min.css') }}">
    
    <!-- If additional styles needed, use a <style> block -->
    <style>
        .custom-class {
            color: var(--color-primary);
            background: var(--bg-secondary);
        }
    </style>
{% endblock styles %}
```

### DO NOT:
- Use inline styles (`style=""` attributes)
- Create extensive custom CSS for prototypes
- Override core Bootstrap or main.css extensively
- Use hardcoded colors (use CSS variables instead)

## HTML Content Guidelines

### Keep It Simple
- Use semantic HTML5 elements (`<main>`, `<section>`, `<article>`, `<header>`, `<nav>`)
- Leverage Bootstrap grid system for layout (`container`, `row`, `col`)
- Use Bootstrap utility classes for spacing (`mb-3`, `p-4`, `text-center`)
- Minimal custom classes - rely on existing framework

### Common Bootstrap Patterns
```html
<!-- Standard page layout -->
<div class="container">
    <div class="row">
        <div class="col-md-8 offset-md-2">
            <h1 class="text-center mb-4">Page Title</h1>
            <!-- Content -->
        </div>
    </div>
</div>

<!-- Card component -->
<div class="card">
    <div class="card-header">
        <h5 class="card-title">Title</h5>
    </div>
    <div class="card-body">
        <!-- Content -->
    </div>
</div>
```

## JavaScript Integration
```jinja2
{% block scripts %}
    <!-- Bootstrap JS if needed -->
    <script src="{{ url_for('static', filename='js/bootstrapjs/bootstrap.bundle.min.js') }}"></script>
    
    <!-- Custom JS -->
    <script src="{{ url_for('static', filename='js/main.js') }}"></script>
    
    <!-- Inline scripts if minimal -->
    <script>
        // Minimal prototype functionality only
    </script>
{% endblock scripts %}
```

## Example Output Template
```jinja2
{% extends 'bases/public.html' %}

{% block styles %}
    <link rel="stylesheet" href="{{ url_for('static', filename='css/main.css') }}">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/bootstrapcss/bootstrap.min.css') }}">
{% endblock styles %}

{% block content %}
<div class="container mt-5">
    <div class="row">
        <div class="col-md-8 offset-md-2">
            <h1 class="text-center mb-4">{{ page_title|default('Prototype Page') }}</h1>
            
            <div class="card">
                <div class="card-body">
                    <p class="lead">Your prototype content goes here.</p>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock content %}

{% block scripts %}
    <script src="{{ url_for('static', filename='js/bootstrapjs/bootstrap.bundle.min.js') }}"></script>
{% endblock scripts %}
```

## Key Principles
1. **Template Inheritance First** - Always extend base templates
2. **Use Existing CSS** - Leverage main.css variables and Bootstrap classes
3. **Minimal Custom Styling** - Only add styles in `<style>` blocks if absolutely necessary
4. **Semantic HTML** - Use proper HTML5 semantic elements
5. **Bootstrap Grid** - Use Bootstrap's responsive grid system
6. **Jinja2 Variables** - Use template variables for dynamic content (`{{ variable_name }}`)
7. **Clean Structure** - Keep HTML simple and readable for quick prototyping

Remember: This is for rapid prototyping. Focus on structure and functionality over visual polish.