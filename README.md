# Diaspora Enterprise Website

A modern Django-based website for Diaspora Enterprise, showcasing real estate investments and short-term rental services with a contemporary blue gradient design aesthetic.

## Features

- Modern, responsive design with mobile-first approach
- Blue gradient color scheme aligned with brand identity
- Geometric design elements inspired by the company logo
- Smooth animations and transitions
- Sticky navigation header
- Service showcase with interactive cards
- SEO-friendly semantic HTML
- Fast static file serving with WhiteNoise

## Technology Stack

- **Backend**: Django 5.x
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Static Files**: WhiteNoise for production-ready static file serving
- **Database**: SQLite (development)
- **Python**: 3.11+

## Project Structure

```
diaspora-enterprise/
├── diaspora_enterprise/        # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── website/                    # Main website app
│   ├── static/
│   │   └── website/
│   │       ├── css/
│   │       │   └── style.css  # Main stylesheet
│   │       ├── js/
│   │       │   └── main.js    # JavaScript for interactions
│   │       └── images/        # Images and media
│   ├── templates/
│   │   └── website/
│   │       ├── base.html      # Base template
│   │       └── home.html      # Homepage
│   ├── views.py
│   └── urls.py
├── requirements.txt            # Python dependencies
├── manage.py
└── README.md
```

## Installation & Setup

### Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- Virtual environment tool (venv)

### Step 1: Clone or Navigate to the Project

```bash
cd diaspora-enterprise
```

### Step 2: Create a Virtual Environment

```bash
python3 -m venv venv
```

### Step 3: Activate the Virtual Environment

**On macOS/Linux:**
```bash
source venv/bin/activate
```

**On Windows:**
```bash
venv\Scripts\activate
```

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 5: Run Database Migrations

```bash
python manage.py migrate
```

### Step 6: Collect Static Files

```bash
python manage.py collectstatic --noinput
```

### Step 7: Create a Superuser (Optional)

```bash
python manage.py createsuperuser
```

### Step 8: Run the Development Server

```bash
python manage.py runserver
```

The website will be available at: `http://127.0.0.1:8000/`

## Configuration

### Environment Variables

For production deployment, you should use environment variables for sensitive settings. Create a `.env` file in the project root:

```env
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

Update `settings.py` to use these variables with `python-decouple`.

### Static Files in Production

The project is configured to use WhiteNoise for serving static files in production. After deploying:

```bash
python manage.py collectstatic
```

## Design System

### Color Palette

- **Primary Cyan**: `#2BA0D8`
- **Primary Blue**: `#2196F3`
- **Secondary Navy**: `#1E5A8E`
- **Secondary Dark Blue**: `#1565C0`
- **Accent Light Blue**: `#64B5F6`
- **Neutral White**: `#FFFFFF`
- **Neutral Light Grey**: `#F5F5F5`

### Typography

- **Font Family**: Inter (via Google Fonts)
- **Weights**: 300 (Light), 400 (Regular), 500 (Medium), 600 (Semibold), 700 (Bold), 800 (Extrabold)

### Design Features

- Geometric shapes with floating animations
- Blue gradient backgrounds
- Smooth hover transitions
- Card-based layouts with depth
- Mobile-responsive navigation
- Intersection Observer animations

## Customization

### Updating the Logo

Replace the SVG placeholder in `base.html` with your actual logo:

```html
<!-- In templates/website/base.html -->
<div class="logo-placeholder">
    <img src="{% static 'website/images/logo.png' %}" alt="Diaspora Enterprise Logo" width="40" height="40">
</div>
```

### Adding New Pages

1. Create a new template in `website/templates/website/`
2. Add a view function in `website/views.py`
3. Add a URL pattern in `website/urls.py`
4. Update navigation in `base.html`

### Modifying Colors

Update CSS variables in `style.css`:

```css
:root {
    --primary-cyan: #2BA0D8;
    --primary-blue: #2196F3;
    /* ... other colors */
}
```

## Deployment

### Production Checklist

1. Set `DEBUG = False` in settings.py
2. Configure `ALLOWED_HOSTS`
3. Use environment variables for secret keys
4. Run `python manage.py collectstatic`
5. Set up a production database (PostgreSQL recommended)
6. Configure a web server (Nginx/Apache)
7. Use a WSGI server (Gunicorn/uWSGI)
8. Set up SSL certificates for HTTPS

### Deployment Platforms

This Django application can be deployed to:
- Heroku
- DigitalOcean
- AWS (EC2, Elastic Beanstalk)
- Google Cloud Platform
- PythonAnywhere
- Vercel (with adaptations)

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## Performance

- Optimized CSS with CSS variables
- Compressed static files with WhiteNoise
- Lazy loading ready for images
- Minimal JavaScript for fast page loads
- Mobile-first responsive design

## Contributing

1. Create a feature branch
2. Make your changes
3. Test thoroughly on mobile and desktop
4. Submit a pull request

## License

© 2025 Diaspora Enterprise. All rights reserved.

## Support

For issues or questions, contact: info@diasporaenterprise.com

## Future Enhancements

- Contact form with email functionality
- Property listing pages
- Image gallery
- Testimonials section
- Blog/News section
- Admin dashboard for content management
- Multi-language support
- Advanced analytics integration
