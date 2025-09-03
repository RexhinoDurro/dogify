# server/bot_detection/enhanced_bot_middleware.py
from django.http import HttpResponse
from django.template import Template, Context
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import re
import os
import json
from .bot_detection_service import AdvancedBotDetectionService
from .models import BotDetection, SecurityLog
from .middleware import get_client_ip

class EnhancedBotHTMLMiddleware:
    """Enhanced middleware that serves static HTML to bots and allows React for humans"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.bot_service = AdvancedBotDetectionService()
        
        # Enhanced bot patterns with Facebook focus
        self.bot_patterns = [
            # Facebook crawlers (highest priority)
            r'facebookexternalhit|facebot|facebookcatalog|facebook.*bot',
            # Search engines
            r'googlebot|google.*bot|bingbot|slurp|duckduckbot|baiduspider|yandexbot',
            # Social media
            r'twitterbot|linkedinbot|instagrambot|pinterestbot|whatsapp',
            # Other crawlers
            r'crawler|spider|scraper|bot|archiver|indexer',
            # Automation tools
            r'selenium|puppeteer|playwright|headless|phantom',
            # API clients
            r'wget|curl|postman|insomnia|python-requests|node.*fetch'
        ]
        
        self.bot_regex = re.compile('|'.join(self.bot_patterns), re.IGNORECASE)
        
        # Routes that should serve HTML to bots
        self.html_routes = ['/', '/shop', '/about', '/contact', '/product/']
    
    def __call__(self, request):
        # Skip API endpoints - let them handle their own logic
        if request.path.startswith('/api/') or request.path.startswith('/admin/'):
            return self.get_response(request)
        
        # Quick bot detection
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        client_ip = get_client_ip(request)
        is_bot = self._is_bot_request(user_agent)
        
        # For bot requests to main routes, serve static HTML
        if is_bot and self._should_serve_html(request.path):
            print(f"🤖 Serving static HTML to bot: {user_agent[:100]}")
            return self._serve_bot_html(request, user_agent, client_ip)
        
        # For human requests, let React handle it
        return self.get_response(request)
    
    def _is_bot_request(self, user_agent):
        """Quick bot detection"""
        if not user_agent:
            return True
        return bool(self.bot_regex.search(user_agent))
    
    def _should_serve_html(self, path):
        """Check if path should serve HTML to bots"""
        return any(path.startswith(route) for route in self.html_routes)
    
    def _serve_bot_html(self, request, user_agent, client_ip):
        """Generate and serve HTML content for bots"""
        try:
            # Log bot visit
            self._log_bot_visit(client_ip, user_agent, request.path)
            
            # Route to appropriate HTML generator
            path = request.path.rstrip('/')
            if path == '' or path == '/':
                return self._generate_home_html(request)
            elif path == '/shop':
                return self._generate_shop_html(request)
            elif path == '/about':
                return self._generate_about_html(request)
            elif path == '/contact':
                return self._generate_contact_html(request)
            elif path.startswith('/product/'):
                product_id = path.split('/')[-1]
                return self._generate_product_html(request, product_id)
            else:
                return self._generate_default_html(request)
                
        except Exception as e:
            print(f"❌ Error serving bot HTML: {e}")
            return self._generate_default_html(request)
    
    def _log_bot_visit(self, client_ip, user_agent, path):
        """Log bot visit for analytics"""
        try:
            # Check if it's a Facebook bot
            is_facebook = 'facebook' in user_agent.lower()
            
            BotDetection.objects.create(
                ip_address=client_ip,
                user_agent=user_agent[:1000],
                fingerprint='',
                is_bot=True,
                confidence_score=0.95,
                url_path=path[:500],
                http_method='GET',
                referrer='',
                country_code='',
                city='',
                status='bot'
            )
            
            # Log as info (not critical)
            SecurityLog.log_event(
                event_type='bot_detected',
                ip_address=client_ip,
                description=f'Bot served HTML content: {path}',
                severity='low',  # Bots are legitimate
                user_agent=user_agent[:500],
                details={
                    'served_html': True,
                    'path': path,
                    'facebook_bot': is_facebook,
                    'legitimate_crawler': True
                }
            )
            
        except Exception as e:
            print(f"❌ Failed to log bot visit: {e}")
    
    def _generate_home_html(self, request):
        """Generate SEO-friendly home page HTML"""
        html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Dogify - Premium Dog Food & Nutrition | Best Dog Treats</title>
            <meta name="description" content="Premium nutrition for your furry friends. Shop high-quality dog food, treats, and wellness products. Free shipping on orders over $50.">
            <meta name="keywords" content="dog food, premium dog nutrition, dog treats, pet supplies, healthy dog food, grain-free dog food">
            
            <!-- Open Graph / Facebook -->
            <meta property="og:type" content="website">
            <meta property="og:url" content="{{ request.build_absolute_uri }}">
            <meta property="og:title" content="Dogify - Premium Dog Food & Nutrition">
            <meta property="og:description" content="Premium nutrition for your furry friends. Shop high-quality dog food, treats, and wellness products.">
            <meta property="og:image" content="{{ request.scheme }}://{{ request.get_host }}/static/dogify-og-image.jpg">
            
            <!-- Twitter -->
            <meta property="twitter:card" content="summary_large_image">
            <meta property="twitter:url" content="{{ request.build_absolute_uri }}">
            <meta property="twitter:title" content="Dogify - Premium Dog Food & Nutrition">
            <meta property="twitter:description" content="Premium nutrition for your furry friends.">
            
            <!-- Schema.org markup for Google -->
            <script type="application/ld+json">
            {
                "@context": "http://schema.org",
                "@type": "WebSite",
                "name": "Dogify",
                "url": "{{ request.build_absolute_uri }}",
                "description": "Premium dog food and nutrition products",
                "potentialAction": {
                    "@type": "SearchAction",
                    "target": "{{ request.build_absolute_uri }}/shop?search={search_term_string}",
                    "query-input": "required name=search_term_string"
                }
            }
            </script>
            
            <link rel="canonical" href="{{ request.build_absolute_uri }}">
            <style>
                body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; margin: 0; padding: 0; color: #333; }
                .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
                .header { background: #fff; border-bottom: 1px solid #e2e8f0; padding: 1rem 0; }
                .nav { display: flex; justify-content: space-between; align-items: center; }
                .logo { font-size: 1.5rem; font-weight: bold; color: #3B82F6; text-decoration: none; }
                .nav-links { display: flex; gap: 2rem; list-style: none; margin: 0; padding: 0; }
                .nav-links a { color: #374151; text-decoration: none; font-weight: 500; }
                .nav-links a:hover { color: #3B82F6; }
                .hero { background: linear-gradient(135deg, #3B82F6 0%, #8B5CF6 100%); color: white; padding: 80px 0; text-align: center; }
                .hero h1 { font-size: 3rem; margin-bottom: 1rem; font-weight: bold; }
                .hero p { font-size: 1.2rem; margin-bottom: 2rem; max-width: 600px; margin-left: auto; margin-right: auto; }
                .btn { display: inline-block; background: white; color: #3B82F6; padding: 12px 24px; text-decoration: none; border-radius: 8px; font-weight: 600; margin: 0 10px; }
                .btn:hover { background: #f8fafc; }
                .btn-outline { background: transparent; color: white; border: 2px solid white; }
                .btn-outline:hover { background: white; color: #3B82F6; }
                .features { padding: 60px 0; background: #f8fafc; }
                .features-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 40px; }
                .feature { text-align: center; padding: 30px; background: white; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); }
                .feature-icon { font-size: 3rem; margin-bottom: 1rem; }
                .products { padding: 60px 0; }
                .products-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 30px; margin: 40px 0; }
                .product { background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); transition: transform 0.2s; }
                .product:hover { transform: translateY(-4px); }
                .product-content { padding: 24px; }
                .product h3 { font-size: 1.25rem; font-weight: 600; margin-bottom: 0.5rem; }
                .product p { color: #6b7280; margin-bottom: 1rem; }
                .price { color: #059669; font-weight: bold; font-size: 1.25rem; }
                .price-original { color: #9ca3af; text-decoration: line-through; margin-left: 0.5rem; }
                .rating { color: #fbbf24; margin-bottom: 0.5rem; }
                .footer { background: #1f2937; color: white; padding: 60px 0 30px; }
                .footer-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 40px; }
                .footer h3 { margin-bottom: 1rem; }
                .footer ul { list-style: none; padding: 0; }
                .footer li { margin-bottom: 0.5rem; }
                .footer a { color: #d1d5db; text-decoration: none; }
                .footer a:hover { color: white; }
                .footer-bottom { border-top: 1px solid #374151; margin-top: 40px; padding-top: 20px; text-align: center; color: #9ca3af; }
                @media (max-width: 768px) {
                    .hero h1 { font-size: 2rem; }
                    .hero p { font-size: 1rem; }
                    .features-grid, .products-grid { grid-template-columns: 1fr; }
                }
            </style>
        </head>
        <body data-testid="bot-content-loaded">
            <!-- Header -->
            <header class="header">
                <div class="container">
                    <nav class="nav">
                        <a href="/" class="logo">🐕 Dogify</a>
                        <ul class="nav-links">
                            <li><a href="/">Home</a></li>
                            <li><a href="/shop">Shop</a></li>
                            <li><a href="/about">About</a></li>
                            <li><a href="/contact">Contact</a></li>
                        </ul>
                    </nav>
                </div>
            </header>
            
            <!-- Hero Section -->
            <section class="hero">
                <div class="container">
                    <h1>Premium Nutrition for Your Best Friend</h1>
                    <p>Discover our carefully curated selection of premium dog food, treats, and wellness products that keep your furry family members healthy and happy.</p>
                    <a href="/shop" class="btn">Shop Now</a>
                    <a href="/about" class="btn btn-outline">Learn More</a>
                </div>
            </section>
            
            <!-- Features Section -->
            <section class="features">
                <div class="container">
                    <h2 style="text-align: center; font-size: 2.5rem; margin-bottom: 3rem; color: #1f2937;">Why Choose Dogify?</h2>
                    <div class="features-grid">
                        <div class="feature">
                            <div class="feature-icon">🛡️</div>
                            <h3>Premium Quality</h3>
                            <p>All our products are sourced from trusted suppliers and undergo rigorous quality testing to ensure the best nutrition for your pet.</p>
                        </div>
                        <div class="feature">
                            <div class="feature-icon">🚚</div>
                            <h3>Fast Delivery</h3>
                            <p>Free shipping on orders over $50 with fast, reliable delivery to your doorstep. Most orders arrive within 2-3 business days.</p>
                        </div>
                        <div class="feature">
                            <div class="feature-icon">❤️</div>
                            <h3>Made with Love</h3>
                            <p>Every product is selected with care, keeping your pet's health and happiness in mind. We treat every customer's pet like family.</p>
                        </div>
                    </div>
                </div>
            </section>
            
            <!-- Featured Products -->
            <section class="products">
                <div class="container">
                    <h2 style="text-align: center; font-size: 2.5rem; margin-bottom: 1rem; color: #1f2937;">Featured Products</h2>
                    <p style="text-align: center; color: #6b7280; margin-bottom: 3rem;">Check out our most popular products that pet parents love</p>
                    
                    <div class="products-grid">
                        <article class="product" itemscope itemtype="http://schema.org/Product">
                            <div class="product-content">
                                <div class="rating">⭐⭐⭐⭐⭐ (4.8/5) • 234 reviews</div>
                                <h3 itemprop="name">Premium Grain-Free Adult Dog Food</h3>
                                <p itemprop="description">High-quality, grain-free nutrition for adult dogs with real chicken as the first ingredient. Perfect for dogs with sensitive stomachs.</p>
                                <div itemprop="offers" itemscope itemtype="http://schema.org/Offer">
                                    <span class="price" itemprop="price" content="49.99">$49.99</span>
                                    <span class="price-original">$59.99</span>
                                    <meta itemprop="priceCurrency" content="USD">
                                    <meta itemprop="availability" content="http://schema.org/InStock">
                                </div>
                                <p><strong>Weight:</strong> 15 lbs | <strong>Category:</strong> Dry Food</p>
                                <a href="/product/1" itemprop="url">View Details</a>
                            </div>
                        </article>
                        
                        <article class="product" itemscope itemtype="http://schema.org/Product">
                            <div class="product-content">
                                <div class="rating">⭐⭐⭐⭐⭐ (4.9/5) • 156 reviews</div>
                                <h3 itemprop="name">Puppy Training Treats</h3>
                                <p itemprop="description">Small, soft training treats perfect for puppies and small dogs. Made with real beef and easy to digest ingredients.</p>
                                <div itemprop="offers" itemscope itemtype="http://schema.org/Offer">
                                    <span class="price" itemprop="price" content="12.99">$12.99</span>
                                    <meta itemprop="priceCurrency" content="USD">
                                    <meta itemprop="availability" content="http://schema.org/InStock">
                                </div>
                                <p><strong>Weight:</strong> 6 oz | <strong>Category:</strong> Treats</p>
                                <a href="/product/2" itemprop="url">View Details</a>
                            </div>
                        </article>
                        
                        <article class="product" itemscope itemtype="http://schema.org/Product">
                            <div class="product-content">
                                <div class="rating">⭐⭐⭐⭐⭐ (4.7/5) • 89 reviews</div>
                                <h3 itemprop="name">Senior Dog Wellness Formula</h3>
                                <p itemprop="description">Specially formulated for senior dogs with joint support and easy digestion. Contains glucosamine and chondroitin.</p>
                                <div itemprop="offers" itemscope itemtype="http://schema.org/Offer">
                                    <span class="price" itemprop="price" content="44.99">$44.99</span>
                                    <meta itemprop="priceCurrency" content="USD">
                                    <meta itemprop="availability" content="http://schema.org/InStock">
                                </div>
                                <p><strong>Weight:</strong> 12 lbs | <strong>Category:</strong> Dry Food</p>
                                <a href="/product/3" itemprop="url">View Details</a>
                            </div>
                        </article>
                    </div>
                    
                    <div style="text-align: center; margin-top: 3rem;">
                        <a href="/shop" class="btn" style="color: #3B82F6; background: white; border: 2px solid #3B82F6;">View All Products</a>
                    </div>
                </div>
            </section>
            
            <!-- Footer -->
            <footer class="footer">
                <div class="container">
                    <div class="footer-grid">
                        <div>
                            <h3>🐕 Dogify</h3>
                            <p>Premium nutrition for your furry family members. We're committed to providing the highest quality dog food and treats.</p>
                            <p><strong>Customer Service:</strong> 1-800-DOGIFY-1</p>
                            <p><strong>Email:</strong> support@dogify.com</p>
                        </div>
                        <div>
                            <h3>Shop</h3>
                            <ul>
                                <li><a href="/shop?category=Dry Food">Dry Food</a></li>
                                <li><a href="/shop?category=Wet Food">Wet Food</a></li>
                                <li><a href="/shop?category=Treats">Treats</a></li>
                                <li><a href="/shop?category=Supplements">Supplements</a></li>
                                <li><a href="/shop">All Products</a></li>
                            </ul>
                        </div>
                        <div>
                            <h3>Company</h3>
                            <ul>
                                <li><a href="/about">About Us</a></li>
                                <li><a href="/contact">Contact</a></li>
                                <li><a href="/about#team">Our Team</a></li>
                                <li><a href="/about#values">Our Values</a></li>
                                <li><a href="/contact#faq">FAQ</a></li>
                            </ul>
                        </div>
                        <div>
                            <h3>Support</h3>
                            <ul>
                                <li><a href="/contact">Customer Support</a></li>
                                <li><a href="/contact#shipping">Shipping Info</a></li>
                                <li><a href="/contact#returns">Returns & Exchanges</a></li>
                                <li><a href="/contact#nutrition">Nutrition Advice</a></li>
                                <li><a href="/contact#emergency">Pet Emergency Resources</a></li>
                            </ul>
                        </div>
                    </div>
                    <div class="footer-bottom">
                        <p>&copy; 2025 Dogify. All rights reserved. | Made with ❤️ for dogs and their humans.</p>
                    </div>
                </div>
            </footer>
        </body>
        </html>
        """
        
        template = Template(html)
        context = Context({'request': request})
        response = HttpResponse(template.render(context))
        response['Cache-Control'] = 'public, max-age=3600'  # Cache for 1 hour
        return response
    
    def _generate_shop_html(self, request):
        """Generate shop page HTML"""
        # Sample products - in production, you'd import from your data
        products = [
            {"id": 1, "name": "Premium Grain-Free Adult Dog Food", "price": 49.99, "original_price": 59.99, "rating": 4.8, "reviews": 234, "description": "High-quality nutrition for adult dogs", "weight": "15 lbs", "category": "Dry Food"},
            {"id": 2, "name": "Puppy Training Treats", "price": 12.99, "rating": 4.9, "reviews": 156, "description": "Perfect for training sessions", "weight": "6 oz", "category": "Treats"},
            {"id": 3, "name": "Senior Dog Wellness Formula", "price": 44.99, "rating": 4.7, "reviews": 89, "description": "Joint support for senior dogs", "weight": "12 lbs", "category": "Dry Food"},
            {"id": 4, "name": "Organic Wet Food Variety Pack", "price": 32.99, "original_price": 39.99, "rating": 4.6, "reviews": 67, "description": "12-pack organic wet food", "weight": "12 x 12.5 oz", "category": "Wet Food"},
            {"id": 5, "name": "Dental Health Chews", "price": 18.99, "rating": 4.5, "reviews": 203, "description": "Daily dental care chews", "weight": "30 count", "category": "Treats"},
            {"id": 6, "name": "High-Protein Active Dog Formula", "price": 54.99, "rating": 4.9, "reviews": 145, "description": "For active and working dogs", "weight": "18 lbs", "category": "Dry Food"},
        ]
        
        # Build products HTML string
        products_html = ""
        for product in products:
            original_price_html = f'<span class="price-original">${product["original_price"]}</span>' if product.get("original_price") else ""
            stars = "⭐" * int(product["rating"])
            
            products_html += f"""
            <article class="product" itemscope itemtype="http://schema.org/Product">
                <div class="product-content">
                    <div class="rating">{stars} ({product["rating"]}/5) • {product["reviews"]} reviews</div>
                    <h3 itemprop="name">{product['name']}</h3>
                    <p itemprop="description">{product['description']}</p>
                    <div itemprop="offers" itemscope itemtype="http://schema.org/Offer">
                        <span class="price" itemprop="price" content="{product['price']}">${product['price']}</span>
                        {original_price_html}
                        <meta itemprop="priceCurrency" content="USD">
                        <meta itemprop="availability" content="http://schema.org/InStock">
                    </div>
                    <p><strong>Weight:</strong> {product['weight']} | <strong>Category:</strong> {product['category']}</p>
                    <a href="/product/{product['id']}" itemprop="url">View Details</a>
                </div>
            </article>
            """
        
        # Create JSON-LD schema data from products
        schema_products = [f'''{{
            "@type": "Offer",
            "itemOffered": {{
                "@type": "Product",
                "name": "{p['name']}",
                "description": "{p['description']}",
                "category": "{p['category']}",
                "offers": {{
                    "@type": "Offer",
                    "price": "{p['price']}",
                    "priceCurrency": "USD"
                }}
            }}
        }}''' for p in products[:3]]
        
        schema_json = ','.join(schema_products)
        
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Shop Premium Dog Food & Treats | Dogify</title>
            <meta name="description" content="Shop our complete selection of premium dog food, healthy treats, and wellness products. Free shipping on orders over $50. Grain-free, organic, and specialty formulas available.">
            <meta name="keywords" content="dog food shop, buy dog food online, premium dog treats, grain-free dog food, organic dog food, puppy food, senior dog food">
            
            <!-- Open Graph -->
            <meta property="og:title" content="Shop Premium Dog Food & Treats | Dogify">
            <meta property="og:description" content="Shop our complete selection of premium dog food and treats. Free shipping on orders over $50.">
            <meta property="og:type" content="website">
            <meta property="og:url" content="{{ request.build_absolute_uri }}">
            
            <link rel="canonical" href="{{ request.build_absolute_uri }}">
            
            <!-- JSON-LD Schema -->
            <script type="application/ld+json">
            {{
                "@context": "http://schema.org",
                "@type": "Store",
                "name": "Dogify",
                "description": "Premium dog food and treats online store",
                "url": "{{ request.build_absolute_uri }}",
                "hasOfferCatalog": {{
                    "@type": "OfferCatalog",
                    "name": "Dog Food and Treats",
                    "itemListElement": [{schema_json}]
                }}
            }}
            </script>
            
            <style>
                /* Your existing CSS styles here */
            </style>
        </head>
        <body data-testid="bot-content-loaded">
            <!-- Header and navigation -->
            <header class="header">
                <!-- Your header content -->
            </header>
            
            <main class="container">
                <div class="products-grid">
                    {products_html}
                </div>
            </main>
        </body>
        </html>
        """
        
        template = Template(html)
        context = Context({'request': request})
        return HttpResponse(template.render(context))
    
    def _generate_default_html(self, request):
        """Generate default HTML for unknown routes"""
        html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Dogify - Premium Dog Food & Nutrition</title>
            <meta name="description" content="Premium nutrition for your furry friends. Shop high-quality dog food, treats, and wellness products.">
            <style>
                body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; margin: 0; padding: 0; }
                .container { max-width: 800px; margin: 0 auto; padding: 40px 20px; text-align: center; }
                .header { margin-bottom: 3rem; }
                .logo { font-size: 3rem; margin-bottom: 1rem; }
                .nav-links { display: flex; justify-content: center; gap: 2rem; margin-top: 2rem; }
                .nav-links a { color: #3B82F6; text-decoration: none; font-weight: 500; padding: 0.5rem 1rem; border-radius: 6px; border: 2px solid #3B82F6; }
                .nav-links a:hover { background: #3B82F6; color: white; }
            </style>
        </head>
        <body data-testid="bot-content-loaded">
            <div class="container">
                <header class="header">
                    <div class="logo">🐕 Dogify</div>
                    <h1>Welcome to Dogify</h1>
                    <p>Premium nutrition for your furry family members. We provide high-quality dog food, treats, and wellness products to keep your pet healthy and happy.</p>
                </header>
                
                <main>
                    <div class="nav-links">
                        <a href="/">Home</a>
                        <a href="/shop">Shop</a>
                        <a href="/about">About</a>
                        <a href="/contact">Contact</a>
                    </div>
                    
                    <section style="margin-top: 3rem; padding: 2rem; background: #f8fafc; border-radius: 12px;">
                        <h2>Why Choose Dogify?</h2>
                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 2rem; margin-top: 2rem;">
                            <div>
                                <div style="font-size: 2rem; margin-bottom: 1rem;">🛡️</div>
                                <h3>Premium Quality</h3>
                                <p>Rigorously tested, high-quality ingredients</p>
                            </div>
                            <div>
                                <div style="font-size: 2rem; margin-bottom: 1rem;">🚚</div>
                                <h3>Fast Delivery</h3>
                                <p>Free shipping on orders over $50</p>
                            </div>
                            <div>
                                <div style="font-size: 2rem; margin-bottom: 1rem;">❤️</div>
                                <h3>Made with Love</h3>
                                <p>Every product selected with care</p>
                            </div>
                        </div>
                    </section>
                </main>
            </div>
        </body>
        </html>
        """
        
        template = Template(html)
        context = Context({'request': request})
        return HttpResponse(template.render(context))
    def _generate_default_header(self, request):
        html = """
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Shop Premium Dog Food & Treats | Dogify</title>
            <meta name="description" content="Shop our complete selection of premium dog food, healthy treats, and wellness products. Free shipping on orders over $50. Grain-free, organic, and specialty formulas available.">
            <meta name="keywords" content="dog food shop, buy dog food online, premium dog treats, grain-free dog food, organic dog food, puppy food, senior dog food">
            
            <!-- Open Graph -->
            <meta property="og:title" content="Shop Premium Dog Food & Treats | Dogify">
            <meta property="og:description" content="Shop our complete selection of premium dog food and treats. Free shipping on orders over $50.">
            <meta property="og:type" content="website">
            <meta property="og:url" content="{{ request.build_absolute_uri }}">
            
            <link rel="canonical" href="{{ request.build_absolute_uri }}">
            
            <!-- JSON-LD Schema -->
            <script type="application/ld+json">
            {{
                "@context": "http://schema.org",
                "@type": "Store",
                "name": "Dogify",
                "description": "Premium dog food and treats online store",
                "url": "{{ request.build_absolute_uri }}",
                "hasOfferCatalog": {{
                    "@type": "OfferCatalog",
                    "name": "Dog Food and Treats",
                    "itemListElement": [
                        {', '.join([f'''{{
                            "@type": "Offer",
                            "itemOffered": {{
                                "@type": "Product",
                                "name": "{p['name']}",
                                "description": "{p['description']}",
                                "category": "{p['category']}",
                                "offers": {{
                                    "@type": "Offer",
                                    "price": "{p['price']}",
                                    "priceCurrency": "USD"
                                }}
                            }}
                        }}''' for p in products[:3]])}
                    ]
                }}
            }}
            </script>
            
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; margin: 0; padding: 0; }}
                .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #fff; border-bottom: 1px solid #e2e8f0; padding: 1rem 0; }}
                .nav {{ display: flex; justify-content: space-between; align-items: center; }}
                .logo {{ font-size: 1.5rem; font-weight: bold; color: #3B82F6; text-decoration: none; }}
                .nav-links {{ display: flex; gap: 2rem; list-style: none; margin: 0; padding: 0; }}
                .nav-links a {{ color: #374151; text-decoration: none; font-weight: 500; }}
                .breadcrumb {{ margin: 2rem 0; color: #6b7280; }}
                .breadcrumb a {{ color: #3B82F6; text-decoration: none; }}
                .page-title {{ font-size: 2.5rem; font-weight: bold; margin-bottom: 1rem; }}
                .page-description {{ font-size: 1.1rem; color: #6b7280; margin-bottom: 3rem; }}
                .filters {{ background: #f8fafc; padding: 2rem; border-radius: 12px; margin-bottom: 3rem; }}
                .filter-section {{ margin-bottom: 1.5rem; }}
                .filter-section h3 {{ margin-bottom: 0.5rem; color: #374151; }}
                .filter-buttons {{ display: flex; flex-wrap: wrap; gap: 0.5rem; }}
                .filter-btn {{ padding: 0.5rem 1rem; background: white; border: 2px solid #e5e7eb; border-radius: 6px; text-decoration: none; color: #374151; }}
                .filter-btn:hover {{ border-color: #3B82F6; color: #3B82F6; }}
                .products-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 30px; }}
                .product {{ background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); transition: transform 0.2s; }}
                .product:hover {{ transform: translateY(-4px); box-shadow: 0 10px 25px -3px rgba(0, 0, 0, 0.1); }}
                .product-content {{ padding: 24px; }}
                .product h3 {{ font-size: 1.25rem; font-weight: 600; margin-bottom: 0.5rem; color: #1f2937; }}
                .product p {{ color: #6b7280; margin-bottom: 1rem; }}
                .price {{ color: #059669; font-weight: bold; font-size: 1.25rem; }}
                .price-original { color: #9ca3af; text-decoration: line-through; margin-left: 0.5rem; }
                .rating { color: #fbbf24; margin-bottom: 0.5rem; font-size: 0.9rem; }
                .product a { color: #3B82F6; text-decoration: none; font-weight: 500; }
                .product a:hover { text-decoration: underline; }
            </style>
        </head>
        <body data-testid="bot-content-loaded">
            <!-- Header -->
            <header class="header">
                <div class="container">
                    <nav class="nav">
                        <a href="/" class="logo">🐕 Dogify</a>
                        <ul class="nav-links">
                            <li><a href="/">Home</a></li>
                            <li><a href="/shop">Shop</a></li>
                            <li><a href="/about">About</a></li>
                            <li><a href="/contact">Contact</a></li>
                        </ul>
                    </nav>
                </div>
            </header>
            
            <main class="container">
                <nav class="breadcrumb" aria-label="breadcrumb">
                    <a href="/">Home</a> › Shop
                </nav>
                
                <h1 class="page-title">Shop All Products</h1>
                <p class="page-description">Find the perfect nutrition for your furry friend from our premium selection of dog food, treats, and wellness products.</p>
                
                <!-- Filters -->
                <div class="filters">
                    <div class="filter-section">
                        <h3>Categories</h3>
                        <div class="filter-buttons">
                            <a href="/shop" class="filter-btn">All Products</a>
                            <a href="/shop?category=Dry+Food" class="filter-btn">Dry Food</a>
                            <a href="/shop?category=Wet+Food" class="filter-btn">Wet Food</a>
                            <a href="/shop?category=Treats" class="filter-btn">Treats</a>
                            <a href="/shop?category=Supplements" class="filter-btn">Supplements</a>
                        </div>
                    </div>
                    
                    <div class="filter-section">
                        <h3>Dog Size</h3>
                        <div class="filter-buttons">
                            <a href="/shop?size=small" class="filter-btn">Small Dogs</a>
                            <a href="/shop?size=medium" class="filter-btn">Medium Dogs</a>
                            <a href="/shop?size=large" class="filter-btn">Large Dogs</a>
                        </div>
                    </div>
                    
                    <div class="filter-section">
                        <h3>Life Stage</h3>
                        <div class="filter-buttons">
                            <a href="/shop?age=puppy" class="filter-btn">Puppy</a>
                            <a href="/shop?age=adult" class="filter-btn">Adult</a>
                            <a href="/shop?age=senior" class="filter-btn">Senior</a>
                        </div>
                    </div>
                </div>
                
                <div class="products-grid">
                    {products_html}
                </div>
                
                <!-- Additional Product Info -->
                <section style="margin-top: 4rem; padding: 2rem; background: #f8fafc; border-radius: 12px;">
                    <h2>Why Choose Dogify Products?</h2>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 2rem; margin-top: 2rem;">
                        <div>
                            <h3>🌿 Natural Ingredients</h3>
                            <p>All our products are made with premium, natural ingredients with no artificial preservatives, colors, or flavors.</p>
                        </div>
                        <div>
                            <h3>🥼 Veterinarian Approved</h3>
                            <p>Our formulas are developed with veterinary nutritionists to ensure optimal health and nutrition.</p>
                        </div>
                        <div>
                            <h3>🚚 Free Shipping</h3>
                            <p>Enjoy free shipping on all orders over $50. Most orders arrive within 2-3 business days.</p>
                        </div>
                        <div>
                            <h3>💯 Satisfaction Guarantee</h3>
                            <p>30-day money-back guarantee. If your dog doesn't love it, we'll make it right.</p>
                        </div>
                    </div>
                </section>
            </main>
        </body>
        </html>
        """
    
    def _generate_about_html(self, request):
        """Generate about page HTML"""
        html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>About Dogify - Premium Pet Nutrition Company</title>
            <meta name="description" content="Learn about Dogify's mission to provide premium nutrition for dogs. Founded by pet lovers, we're committed to quality, transparency, and the wellbeing of dogs everywhere.">
            <link rel="canonical" href="{{ request.build_absolute_uri }}">
            
            <style>
                body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; margin: 0; padding: 0; }
                .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
                .header { background: #fff; border-bottom: 1px solid #e2e8f0; padding: 1rem 0; }
                .nav { display: flex; justify-content: space-between; align-items: center; }
                .logo { font-size: 1.5rem; font-weight: bold; color: #3B82F6; text-decoration: none; }
                .nav-links { display: flex; gap: 2rem; list-style: none; margin: 0; padding: 0; }
                .nav-links a { color: #374151; text-decoration: none; font-weight: 500; }
                .hero-section { text-align: center; padding: 4rem 0; background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%); }
                .hero-section h1 { font-size: 3rem; margin-bottom: 1rem; color: #1f2937; }
                .content-section { padding: 3rem 0; }
                .content-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 3rem; align-items: center; }
                .values-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 2rem; margin: 3rem 0; }
                .value-card { text-align: center; padding: 2rem; background: white; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); }
                .team-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 2rem; }
                .team-member { text-align: center; padding: 2rem; background: white; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); }
            </style>
        </head>
        <body data-testid="bot-content-loaded">
            <header class="header">
                <div class="container">
                    <nav class="nav">
                        <a href="/" class="logo">🐕 Dogify</a>
                        <ul class="nav-links">
                            <li><a href="/">Home</a></li>
                            <li><a href="/shop">Shop</a></li>
                            <li><a href="/about">About</a></li>
                            <li><a href="/contact">Contact</a></li>
                        </ul>
                    </nav>
                </div>
            </header>
            
            <main>
                <section class="hero-section">
                    <div class="container">
                        <h1>About Dogify</h1>
                        <p style="font-size: 1.2rem; color: #6b7280; max-width: 600px; margin: 0 auto;">We're passionate about providing premium nutrition and care products that keep your furry family members healthy, happy, and thriving.</p>
                    </div>
                </section>
                
                <section class="content-section">
                    <div class="container">
                        <div class="content-grid">
                            <div>
                                <h2 style="font-size: 2.5rem; margin-bottom: 1.5rem;">Our Story</h2>
                                <p style="margin-bottom: 1rem;">Dogify was founded in 2018 by a team of dog lovers who were frustrated by the lack of transparency and quality in the pet food industry. After struggling to find nutritious, honest food options for our own dogs, we decided to create the solution ourselves.</p>
                                <p style="margin-bottom: 1rem;">We started with a simple mission: to provide dog owners with premium, transparent nutrition that they can trust. Every product we offer is carefully vetted for quality, sourced from reputable suppliers, and tested to meet our high standards.</p>
                                <p>Today, we're proud to serve thousands of dog families across the country, helping pets live healthier, happier lives through better nutrition. But our mission remains the same – to be your trusted partner in your dog's health journey.</p>
                            </div>
                            <div style="text-align: center;">
                                <div style="width: 300px; height: 200px; background: linear-gradient(135deg, #3B82F6, #8B5CF6); border-radius: 12px; display: flex; align-items: center; justify-content: center; margin: 0 auto;">
                                    <span style="font-size: 4rem;">🐕❤️</span>
                                </div>
                                <p style="margin-top: 1rem; font-style: italic; color: #6b7280;">Founded by dog lovers, for dog lovers</p>
                            </div>
                        </div>
                    </div>
                </section>
                
                <section class="content-section" style="background: #f8fafc;">
                    <div class="container">
                        <h2 style="text-align: center; font-size: 2.5rem; margin-bottom: 3rem;">Our Values</h2>
                        <div class="values-grid">
                            <div class="value-card">
                                <div style="font-size: 3rem; margin-bottom: 1rem;">🛡️</div>
                                <h3>Quality First</h3>
                                <p>We never compromise on quality. Every product undergoes rigorous testing and meets our strict standards before reaching your dog.</p>
                            </div>
                            <div class="value-card">
                                <div style="font-size: 3rem; margin-bottom: 1rem;">🌿</div>
                                <h3>Natural Ingredients</h3>
                                <p>We believe in the power of natural, wholesome ingredients. No unnecessary fillers, artificial colors, or harmful preservatives.</p>
                            </div>
                            <div class="value-card">
                                <div style="font-size: 3rem; margin-bottom: 1rem;">❤️</div>
                                <h3>Made with Love</h3>
                                <p>Every decision we make is guided by our love for dogs. We treat every customer's pet like our own family member.</p>
                            </div>
                            <div class="value-card">
                                <div style="font-size: 3rem; margin-bottom: 1rem;">🔍</div>
                                <h3>Transparency</h3>
                                <p>We believe you have the right to know exactly what you're feeding your dog. Full ingredient transparency, always.</p>
                            </div>
                        </div>
                    </div>
                </section>
                
                <section class="content-section">
                    <div class="container">
                        <h2 style="text-align: center; font-size: 2.5rem; margin-bottom: 3rem;">Meet Our Team</h2>
                        <div class="team-grid">
                            <div class="team-member">
                                <div style="width: 100px; height: 100px; background: linear-gradient(135deg, #3B82F6, #8B5CF6); border-radius: 50%; margin: 0 auto 1rem; display: flex; align-items: center; justify-content: center;">
                                    <span style="font-size: 2rem; color: white;">SJ</span>
                                </div>
                                <h3>Sarah Johnson</h3>
                                <p style="color: #3B82F6; font-weight: 600;">Founder & CEO</p>
                                <p style="font-size: 0.9rem; color: #6b7280;">Former veterinary nutritionist with 15 years of experience in pet health and nutrition.</p>
                            </div>
                            <div class="team-member">
                                <div style="width: 100px; height: 100px; background: linear-gradient(135deg, #059669, #10b981); border-radius: 50%; margin: 0 auto 1rem; display: flex; align-items: center; justify-content: center;">
                                    <span style="font-size: 2rem; color: white;">MC</span>
                                </div>
                                <h3>Mike Chen</h3>
                                <p style="color: #059669; font-weight: 600;">Head of Quality</p>
                                <p style="font-size: 0.9rem; color: #6b7280;">Ensures every product meets our strict quality standards through comprehensive testing and oversight.</p>
                            </div>
                            <div class="team-member">
                                <div style="width: 100px; height: 100px; background: linear-gradient(135deg, #dc2626, #f87171); border-radius: 50%; margin: 0 auto 1rem; display: flex; align-items: center; justify-content: center;">
                                    <span style="font-size: 2rem; color: white;">ER</span>
                                </div>
                                <h3>Emma Rodriguez</h3>
                                <p style="color: #dc2626; font-weight: 600;">Customer Success</p>
                                <p style="font-size: 0.9rem; color: #6b7280;">Dedicated to ensuring every customer and their furry friend has an amazing experience with Dogify.</p>
                            </div>
                        </div>
                    </div>
                </section>
                
                <section class="content-section" style="background: #3B82F6; color: white; text-align: center;">
                    <div class="container">
                        <h2 style="font-size: 2.5rem; margin-bottom: 2rem;">Our Impact</h2>
                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 2rem;">
                            <div>
                                <div style="font-size: 3rem; font-weight: bold; margin-bottom: 0.5rem;">50K+</div>
                                <div>Happy Dogs</div>
                            </div>
                            <div>
                                <div style="font-size: 3rem; font-weight: bold; margin-bottom: 0.5rem;">25K+</div>
                                <div>Families Served</div>
                            </div>
                            <div>
                                <div style="font-size: 3rem; font-weight: bold; margin-bottom: 0.5rem;">98%</div>
                                <div>Satisfaction Rate</div>
                            </div>
                            <div>
                                <div style="font-size: 3rem; font-weight: bold; margin-bottom: 0.5rem;">7</div>
                                <div>Years of Service</div>
                            </div>
                        </div>
                    </div>
                </section>
            </main>
        </body>
        </html>
        """
        
        template = Template(html)
        context = Context({'request': request})
        return HttpResponse(template.render(context))
    
    def _generate_contact_html(self, request):
        """Generate contact page HTML"""
        html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Contact Dogify - Customer Support & Information</title>
            <meta name="description" content="Get in touch with Dogify. Customer support, product questions, and pet nutrition advice. We're here to help you and your furry friend.">
            <link rel="canonical" href="{{ request.build_absolute_uri }}">
            
            <style>
                body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; margin: 0; padding: 0; }
                .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
                .header { background: #fff; border-bottom: 1px solid #e2e8f0; padding: 1rem 0; }
                .nav { display: flex; justify-content: space-between; align-items: center; }
                .logo { font-size: 1.5rem; font-weight: bold; color: #3B82F6; text-decoration: none; }
                .nav-links { display: flex; gap: 2rem; list-style: none; margin: 0; padding: 0; }
                .nav-links a { color: #374151; text-decoration: none; font-weight: 500; }
                .hero-section { text-align: center; padding: 4rem 0; background: linear-gradient(135deg, #3B82F6, #8B5CF6); color: white; }
                .contact-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 2rem; margin: 3rem 0; }
                .contact-card { text-align: center; padding: 2rem; background: white; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); }
                .contact-info { background: #f8fafc; padding: 3rem; border-radius: 12px; margin: 3rem 0; }
                .faq-section { margin: 3rem 0; }
                .faq-item { background: white; border-radius: 8px; margin-bottom: 1rem; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); }
                .faq-question { padding: 1.5rem; font-weight: 600; color: #1f2937; border-bottom: 1px solid #e5e7eb; }
                .faq-answer { padding: 1.5rem; color: #6b7280; }
            </style>
        </head>
        <body data-testid="bot-content-loaded">
            <header class="header">
                <div class="container">
                    <nav class="nav">
                        <a href="/" class="logo">🐕 Dogify</a>
                        <ul class="nav-links">
                            <li><a href="/">Home</a></li>
                            <li><a href="/shop">Shop</a></li>
                            <li><a href="/about">About</a></li>
                            <li><a href="/contact">Contact</a></li>
                        </ul>
                    </nav>
                </div>
            </header>
            
            <section class="hero-section">
                <div class="container">
                    <h1 style="font-size: 3rem; margin-bottom: 1rem;">Get in Touch</h1>
                    <p style="font-size: 1.2rem;">Have questions about our products or need help finding the right nutrition for your dog? We're here to help and would love to hear from you!</p>
                </div>
            </section>
            
            <main class="container">
                <div class="contact-grid">
                    <div class="contact-card">
                        <div style="font-size: 3rem; margin-bottom: 1rem;">💬</div>
                        <h3>Live Chat</h3>
                        <p>Get instant help from our support team</p>
                        <p style="font-weight: 600; color: #3B82F6;">Available 24/7</p>
                    </div>
                    <div class="contact-card">
                        <div style="font-size: 3rem; margin-bottom: 1rem;">📞</div>
                        <h3>Call Us</h3>
                        <p style="font-weight: 600; font-size: 1.2rem;">1-800-DOGIFY-1</p>
                        <p>(1-800-364-4391)</p>
                        <p>Mon-Fri: 8AM-8PM CST<br>Sat-Sun: 9AM-6PM CST</p>
                    </div>
                    <div class="contact-card">
                        <div style="font-size: 3rem; margin-bottom: 1rem;">✉️</div>
                        <h3>Email Support</h3>
                        <p><strong>support@dogify.com</strong></p>
                        <p>Response within 24 hours</p>
                    </div>
                    <div class="contact-card">
                        <div style="font-size: 3rem; margin-bottom: 1rem;">❓</div>
                        <h3>Help Center</h3>
                        <p>Browse our knowledge base for instant answers</p>
                        <p style="font-weight: 600; color: #3B82F6;">Self-service support</p>
                    </div>
                </div>
                
                <div class="contact-info">
                    <h2 style="text-align: center; margin-bottom: 2rem;">Contact Information</h2>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 2rem;">
                        <div>
                            <h3>📍 Address</h3>
                            <address style="not-italic;">
                                <strong>Dogify Headquarters</strong><br>
                                123 Pet Paradise Lane<br>
                                Austin, TX 78701<br>
                                United States
                            </address>
                        </div>
                        <div>
                            <h3>🕐 Business Hours</h3>
                            <ul style="list-style: none; padding: 0;">
                                <li><strong>Monday - Friday:</strong> 8:00 AM - 8:00 PM CST</li>
                                <li><strong>Saturday:</strong> 9:00 AM - 6:00 PM CST</li>
                                <li><strong>Sunday:</strong> 10:00 AM - 4:00 PM CST</li>
                            </ul>
                            <p style="color: #059669; font-weight: 600;">🟢 Currently Open</p>
                        </div>
                        <div>
                            <h3>🏪 Store Services</h3>
                            <ul style="list-style: none; padding: 0;">
                                <li>✅ Curbside Pickup Available</li>
                                <li>✅ Free Parking (50+ spaces)</li>
                                <li>✅ Nutrition Consultations</li>
                                <li>✅ Product Samples Available</li>
                            </ul>
                        </div>
                    </div>
                </div>
                
                <section class="faq-section">
                    <h2 style="text-align: center; margin-bottom: 2rem;">Frequently Asked Questions</h2>
                    
                    <div class="faq-item">
                        <div class="faq-question">How do I choose the right food for my dog?</div>
                        <div class="faq-answer">Consider your dog's age, size, activity level, and any dietary sensitivities. Our nutrition experts are happy to provide personalized recommendations based on your dog's specific needs. You can reach us at 1-800-DOGIFY-1 for a free consultation.</div>
                    </div>
                    
                    <div class="faq-item">
                        <div class="faq-question">What's your return policy?</div>
                        <div class="faq-answer">We offer a 30-day satisfaction guarantee. If your dog doesn't love our food, we'll provide a full refund or exchange. No questions asked! Simply contact our customer service team to initiate a return.</div>
                    </div>
                    
                    <div class="faq-item">
                        <div class="faq-question">Do you offer subscription discounts?</div>
                        <div class="faq-answer">Yes! Save 15% on recurring orders with our subscription service. You can modify, pause, or cancel anytime with no commitment. Plus, subscribers get early access to new products and special promotions.</div>
                    </div>
                    
                    <div class="faq-item">
                        <div class="faq-question">How fast is shipping?</div>
                        <div class="faq-answer">We offer free standard shipping on orders over $50 (3-5 business days). Express shipping is available for $12.99 (1-2 business days). Orders placed before 2 PM CST ship the same day.</div>
                    </div>
                    
                    <div class="faq-item">
                        <div class="faq-question">Are your products made in the USA?</div>
                        <div class="faq-answer">Yes! All our dry food products are manufactured in USDA-certified facilities in the United States. We source ingredients from trusted suppliers and maintain strict quality control standards.</div>
                    </div>
                </section>
                
                <!-- Emergency Contact Section -->
                <section style="background: #fee2e2; padding: 2rem; border-radius: 12px; border-left: 4px solid #dc2626; margin: 3rem 0;">
                    <h3 style="color: #dc2626; margin-bottom: 1rem;">🚨 Pet Emergency Resources</h3>
                    <p style="color: #7f1d1d;">If your pet is experiencing a medical emergency, please contact your veterinarian or animal emergency clinic immediately. Do not wait for our response.</p>
                    
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem; margin-top: 1rem;">
                        <div style="background: white; padding: 1rem; border-radius: 6px;">
                            <strong style="color: #dc2626;">Pet Poison Helpline</strong><br>
                            <span style="font-size: 1.1rem; font-weight: 600;">1-855-764-7661</span><br>
                            <small>24/7 Emergency Service</small>
                        </div>
                        <div style="background: white; padding: 1rem; border-radius: 6px;">
                            <strong style="color: #dc2626;">ASPCA Poison Control</strong><br>
                            <span style="font-size: 1.1rem; font-weight: 600;">1-888-426-4435</span><br>
                            <small>24/7 Emergency Hotline</small>
                        </div>
                    </div>
                </section>
            </main>
        </body>
        </html>
        """
        
        template = Template(html)
        context = Context({'request': request})
        return HttpResponse(template.render(context))
    
    def _generate_product_html(self, request, product_id):
        """Generate individual product page HTML"""
        # Sample product data - in production, you'd fetch from database
        products_data = {
            "1": {
                "name": "Premium Grain-Free Adult Dog Food",
                "price": 49.99,
                "original_price": 59.99,
                "description": "High-quality, grain-free nutrition for adult dogs with real chicken as the first ingredient. Perfect for dogs with sensitive stomachs and designed to support overall health and vitality.",
                "weight": "15 lbs",
                "rating": 4.8,
                "reviews": 234,
                "category": "Dry Food",
                "ingredients": ["Chicken", "Sweet Potato", "Peas", "Chicken Fat", "Natural Flavors", "Vitamins", "Minerals"],
                "benefits": ["High Protein", "Grain-Free", "No Artificial Preservatives", "Supports Digestive Health"]
            },
            "2": {
                "name": "Puppy Training Treats", 
                "price": 12.99,
                "description": "Small, soft training treats perfect for puppies and small dogs. Made with real beef and easy to digest ingredients.",
                "weight": "6 oz",
                "rating": 4.9,
                "reviews": 156,
                "category": "Treats",
                "ingredients": ["Beef", "Rice Flour", "Glycerin", "Natural Flavors", "Vitamins"],
                "benefits": ["Perfect Size for Training", "Soft Texture", "High-Value Reward", "Easy to Digest"]
            },
            "3": {
                "name": "Senior Dog Wellness Formula",
                "price": 44.99,
                "description": "Specially formulated for senior dogs with joint support and easy digestion. Contains glucosamine and chondroitin for healthy joints.",
                "weight": "12 lbs", 
                "rating": 4.7,
                "reviews": 89,
                "category": "Dry Food",
                "ingredients": ["Lamb", "Brown Rice", "Glucosamine", "Chondroitin", "Omega-3", "Antioxidants"],
                "benefits": ["Joint Support", "Easy Digestion", "Antioxidant Rich", "Senior-Specific Nutrition"]
            }
        }
        
        product = products_data.get(product_id, products_data["1"])
        stars = "⭐" * int(product["rating"])
        original_price_html = f'<span style="color: #9ca3af; text-decoration: line-through; margin-left: 0.5rem;">${product["original_price"]}</span>' if product.get("original_price") else ""
        
        ingredients_html = ", ".join(product["ingredients"])
        benefits_html = "</li><li>".join(product["benefits"])
        
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        """
        