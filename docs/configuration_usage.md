# Configuration Usage Examples

## 1. Using in Python Code (Controllers/Logic)

```python
from flask import current_app

# In your controllers or logic layer
def some_function():
    app_name = current_app.config['APP_NAME']
    version = current_app.config['VERSION']
    max_attempts = current_app.config['MAX_LOGIN_ATTEMPTS']
    
    # Example: Check if feature is enabled
    if current_app.config['ENABLE_USER_REGISTRATION']:
        # Allow user registration
        pass
```

## 2. Using in Jinja Templates

```html
<!-- In any template file -->
<!DOCTYPE html>
<html>
<head>
    <title>{{ app_name }} - Home</title>
    <meta name="description" content="{{ description }}">
</head>
<body>
    <header>
        <h1>{{ app_name }}</h1>
        <span class="version">v{{ version }}</span>
    </header>
    
    <footer>
        <p>&copy; 2025 {{ author }}. All rights reserved.</p>
        <p>{{ app_name }} v{{ version }}</p>
    </footer>
    
    <!-- Conditional features -->
    {% if enable_user_registration %}
        <a href="/register">Sign Up</a>
    {% endif %}
    
    {% if enable_password_reset %}
        <a href="/forgot-password">Forgot Password?</a>
    {% endif %}
</body>
</html>
```

## 3. Available Template Variables

- `{{ app_name }}` - Flask MVC Base Template
- `{{ version }}` - 1.2.0
- `{{ author }}` - Tyler Thibault
- `{{ description }}` - App description
- `{{ enable_user_registration }}` - True/False
- `{{ enable_password_reset }}` - True/False
- `{{ default_theme }}` - light

## 4. Configuration Access Methods

### Via Flask Config (Python)
```python
app.config['APP_NAME']  # "Flask MVC Base Template"
```

### Via Current App (Python)
```python
from flask import current_app
current_app.config['VERSION']  # "1.2.0"
```

### Via Template Globals (Jinja)
```html
{{ app_name }}  <!-- Flask MVC Base Template -->
```