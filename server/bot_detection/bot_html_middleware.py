# server/bot_detection/bot_html_middleware.py
from django.http import HttpResponse
from django.template import Template, Context
from django.conf import settings
import re
import os

class BotHTMLMiddleware:
    """Serve static HTML to bots while allowing React for humans"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Enhanced bot patterns
        self.bot_patterns = [
            # Search engines
            r'googlebot|google|bingbot|slurp|duckduckbot|baiduspider',
            # Social media
            r'facebookexternalhit|facebot|twitterbot|linkedinbot',
            # Other crawlers
            r'crawler|spider|scraper|bot|archiver|indexer',
            # Specific tools
            r'wget|curl|postman|insomnia'
        ]
        
        self.bot_regex = re.compile('|'.join(self.bot_patterns), re.IGNORECASE)
    
    def __call__(self, request):
        # Check if this is a bot request
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        is_bot = self.bot_regex.search(user_agent)
        
        # Only serve HTML to bots for main site routes
        if is_bot and not request.path.startswith('/api/'):
            return self.serve_bot_html(request)
        
        # Normal processing for humans
        return self.get_response(request)
    
    def serve_bot_html(self, request):
        """Generate HTML content for bots"""
        path = request.path
        
        # Route to appropriate HTML generator
        if path == '/':
            return self.generate_home_html(request)
        elif path == '/shop':
            return self.generate_shop_html(request)
        elif path == '/about':
            return self.generate_about_html(request)
        elif path == '/contact':
            return self.generate_contact_html(request)
        elif path.startswith('/product/'):
            product_id = path.split('/')[-1]
            return self.generate_product_html(request, product_id)
        else:
            # Default HTML for unknown routes
            return self.generate_default_html(request)
    
    def generate_home_html(self, request):
        """Generate SEO-friendly home page HTML"""
        html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Dogify - Premium Dog Food & Nutrition | Best Dog Treats</title>
            <meta name="description" content="Premium nutrition for your furry friends. Shop high-quality dog food, treats, and wellness products. Free shipping on orders over $50.">
            <meta name="keywords" content="dog food, premium dog nutrition, dog treats, pet supplies, healthy dog food">
            
            <!-- Open Graph / Facebook -->
            <meta property="og:type" content="website">
            <meta property="og:url" content="{{ request.build_absolute_uri }}">
            <meta property="og:title" content="Dogify - Premium Dog Food & Nutrition">
            <meta property="og:description" content="Premium nutrition for your furry friends. Shop high-quality dog food, treats, and wellness products.">
            <meta property="og:image" content="{{ request.scheme }}://{{ request.get_host }}/static/og-image.jpg">
            
            <!-- Twitter -->
            <meta property="twitter:card" content="summary_large_image">
            <meta property="twitter:url" content="{{ request.build_absolute_uri }}">
            <meta property="twitter:title" content="Dogify - Premium Dog Food & Nutrition">
            <meta property="twitter:description" content="Premium nutrition for your furry friends. Shop high-quality dog food, treats, and wellness products.">
            
            <link rel="canonical" href="{{ request.build_absolute_uri }}">
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 0; }
                .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
                .hero { background: linear-gradient(135deg, #3B82F6 0%, #8B5CF6 100%); color: white; padding: 60px 0; text-align: center; }
                .products { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin: 40px 0; }
                .product { border: 1px solid #e2e8f0; border-radius: 8px; padding: 20px; }
                .price { color: #059669; font-weight: bold; font-size: 1.2em; }
            </style>
        </head>
        <body data-testid="content-loaded">
            <!-- Header -->
            <header>
                <nav class="container">
                    <h1>🐕 Dogify</h1>
                    <ul style="list-style: none; display: flex; gap: 20px;">
                        <li><a href="/">Home</a></li>
                        <li><a href="/shop">Shop</a></li>
                        <li><a href="/about">About</a></li>
                        <li><a href="/contact">Contact</a></li>
                    </ul>
                </nav>
            </header>
            
            <!-- Hero Section -->
            <section class="hero">
                <div class="container">
                    <h1>Premium Nutrition for Your Best Friend</h1>
                    <p>Discover our carefully curated selection of premium dog food, treats, and wellness products that keep your furry family members healthy and happy.</p>
                    <a href="/shop" style="background: white; color: #3B82F6; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block; margin-top: 20px;">Shop Now</a>
                </div>
            </section>
            
            <!-- Featured Products -->
            <section class="container">
                <h2>Featured Products</h2>
                <div class="products">
                    <article class="product">
                        <h3>Premium Grain-Free Adult Dog Food</h3>
                        <p>High-quality, grain-free nutrition for adult dogs with real chicken as the first ingredient.</p>
                        <p class="price">$49.99 <span style="text-decoration: line-through; color: #6b7280;">$59.99</span></p>
                        <p><strong>Weight:</strong> 15 lbs</p>
                        <p><strong>Rating:</strong> ⭐⭐⭐⭐⭐ (4.8/5)</p>
                        <a href="/product/1">View Details</a>
                    </article>
                    
                    <article class="product">
                        <h3>Puppy Training Treats</h3>
                        <p>Small, soft training treats perfect for puppies and small dogs. Made with real beef.</p>
                        <p class="price">$12.99</p>
                        <p><strong>Weight:</strong> 6 oz</p>
                        <p><strong>Rating:</strong> ⭐⭐⭐⭐⭐ (4.9/5)</p>
                        <a href="/product/2">View Details</a>
                    </article>
                    
                    <article class="product">
                        <h3>Senior Dog Wellness Formula</h3>
                        <p>Specially formulated for senior dogs with joint support and easy digestion.</p>
                        <p class="price">$44.99</p>
                        <p><strong>Weight:</strong> 12 lbs</p>
                        <p><strong>Rating:</strong> ⭐⭐⭐⭐⭐ (4.7/5)</p>
                        <a href="/product/3">View Details</a>
                    </article>
                </div>
            </section>
            
            <!-- Why Choose Us -->
            <section class="container">
                <h2>Why Choose Dogify?</h2>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px;">
                    <div style="text-align: center; padding: 20px;">
                        <h3>🛡️ Premium Quality</h3>
                        <p>All our products are sourced from trusted suppliers and undergo rigorous quality testing.</p>
                    </div>
                    <div style="text-align: center; padding: 20px;">
                        <h3>🚚 Fast Delivery</h3>
                        <p>Free shipping on orders over $50 with fast, reliable delivery to your doorstep.</p>
                    </div>
                    <div style="text-align: center; padding: 20px;">
                        <h3>❤️ Made with Love</h3>
                        <p>Every product is selected with care, keeping your pet's health and happiness in mind.</p>
                    </div>
                </div>
            </section>
            
            <!-- Footer -->
            <footer style="background: #1f2937; color: white; padding: 40px 0; margin-top: 40px;">
                <div class="container">
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px;">
                        <div>
                            <h3>🐕 Dogify</h3>
                            <p>Premium nutrition for your furry family members.</p>
                        </div>
                        <div>
                            <h3>Shop</h3>
                            <ul style="list-style: none; padding: 0;">
                                <li><a href="/shop?category=Dry Food" style="color: #d1d5db;">Dry Food</a></li>
                                <li><a href="/shop?category=Wet Food" style="color: #d1d5db;">Wet Food</a></li>
                                <li><a href="/shop?category=Treats" style="color: #d1d5db;">Treats</a></li>
                            </ul>
                        </div>
                        <div>
                            <h3>Company</h3>
                            <ul style="list-style: none; padding: 0;">
                                <li><a href="/about" style="color: #d1d5db;">About Us</a></li>
                                <li><a href="/contact" style="color: #d1d5db;">Contact</a></li>
                            </ul>
                        </div>
                    </div>
                    <div style="text-align: center; margin-top: 20px; border-top: 1px solid #374151; padding-top: 20px;">
                        <p>&copy; 2025 Dogify. All rights reserved.</p>
                    </div>
                </div>
            </footer>
        </body>
        </html>
        """
        
        template = Template(html)
        context = Context({'request': request})
        return HttpResponse(template.render(context)) = Context({'request': request})
        return HttpResponse(template.render(context))
    
    def generate_shop_html(self, request):
        """Generate shop page HTML with product listings"""
        # Get products from your data (you might want to import from your React data)
        products_html = ""
        
        # Sample products - in real implementation, import from your React data
        products = [
            {"id": 1, "name": "Premium Grain-Free Adult Dog Food", "price": 49.99, "description": "High-quality nutrition"},
            {"id": 2, "name": "Puppy Training Treats", "price": 12.99, "description": "Perfect for training"},
            {"id": 3, "name": "Senior Dog Wellness Formula", "price": 44.99, "description": "Joint support formula"},
        ]
        
        for product in products:
            products_html += f"""
            <article class="product" itemscope itemtype="http://schema.org/Product">
                <h3 itemprop="name">{product['name']}</h3>
                <p itemprop="description">{product['description']}</p>
                <span itemprop="price" content="{product['price']}">${product['price']}</span>
                <meta itemprop="priceCurrency" content="USD">
                <a href="/product/{product['id']}" itemprop="url">View Details</a>
            </article>
            """
        
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Shop Premium Dog Food & Treats | Dogify</title>
            <meta name="description" content="Shop our complete selection of premium dog food, healthy treats, and wellness products. Free shipping on orders over $50.">
            <link rel="canonical" href="{{ request.build_absolute_uri }}">
        </head>
        <body data-testid="content-loaded">
            <header>
                <nav>
                    <h1>🐕 Dogify</h1>
                    <ul style="list-style: none; display: flex; gap: 20px;">
                        <li><a href="/">Home</a></li>
                        <li><a href="/shop">Shop</a></li>
                        <li><a href="/about">About</a></li>
                        <li><a href="/contact">Contact</a></li>
                    </ul>
                </nav>
            </header>
            
            <main style="max-width: 1200px; margin: 0 auto; padding: 20px;">
                <h1>Shop All Products</h1>
                <p>Find the perfect nutrition for your furry friend</p>
                
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px;">
                    {products_html}
                </div>
            </main>
        </body>
        </html>
        """
        
        template = Template(html)
        context = Context({'request': request})
        return HttpResponse(template.render(context))
    
    def generate_product_html(self, request, product_id):
        """Generate individual product page HTML"""
        # You'd fetch product data here - for demo purposes, using static data
        product_data = {
            "1": {"name": "Premium Grain-Free Adult Dog Food", "price": 49.99, "description": "High-quality, grain-free nutrition for adult dogs with real chicken as the first ingredient."},
            "2": {"name": "Puppy Training Treats", "price": 12.99, "description": "Small, soft training treats perfect for puppies and small dogs."},
            "3": {"name": "Senior Dog Wellness Formula", "price": 44.99, "description": "Specially formulated for senior dogs with joint support."}
        }
        
        product = product_data.get(product_id, product_data["1"])
        
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{product['name']} | Dogify</title>
            <meta name="description" content="{product['description']} Premium dog nutrition at ${product['price']}.">
            <link rel="canonical" href="{{ request.build_absolute_uri }}">
            
            <!-- Product Schema Markup -->
            <script type="application/ld+json">
            {{
                "@context": "http://schema.org",
                "@type": "Product",
                "name": "{product['name']}",
                "description": "{product['description']}",
                "offers": {{
                    "@type": "Offer",
                    "price": "{product['price']}",
                    "priceCurrency": "USD",
                    "availability": "http://schema.org/InStock"
                }},
                "brand": {{
                    "@type": "Brand",
                    "name": "Dogify"
                }}
            }}
            </script>
        </head>
        <body data-testid="content-loaded">
            <header>
                <nav>
                    <h1>🐕 Dogify</h1>
                    <ul style="list-style: none; display: flex; gap: 20px;">
                        <li><a href="/">Home</a></li>
                        <li><a href="/shop">Shop</a></li>
                        <li><a href="/about">About</a></li>
                        <li><a href="/contact">Contact</a></li>
                    </ul>
                </nav>
            </header>
            
            <main style="max-width: 1200px; margin: 0 auto; padding: 20px;">
                <nav aria-label="breadcrumb">
                    <a href="/">Home</a> > <a href="/shop">Shop</a> > {product['name']}
                </nav>
                
                <article itemscope itemtype="http://schema.org/Product">
                    <h1 itemprop="name">{product['name']}</h1>
                    <p itemprop="description">{product['description']}</p>
                    <div itemprop="offers" itemscope itemtype="http://schema.org/Offer">
                        <span itemprop="price" content="{product['price']}">${product['price']}</span>
                        <meta itemprop="priceCurrency" content="USD">
                        <meta itemprop="availability" content="http://schema.org/InStock">
                    </div>
                    
                    <div>
                        <h2>Product Features</h2>
                        <ul>
                            <li>Premium quality ingredients</li>
                            <li>Veterinarian recommended</li>
                            <li>Made in USA</li>
                            <li>Free shipping on orders over $50</li>
                        </ul>
                    </div>
                </article>
            </main>
        </body>
        </html>
        """
        
        template = Template(html)
        context = Context({'request': request})
        return HttpResponse(template.render(context))
    
    def generate_about_html(self, request):
        """Generate about page HTML"""
        html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>About Dogify - Premium Pet Nutrition Company</title>
            <meta name="description" content="Learn about Dogify's mission to provide premium nutrition for dogs. Founded by pet lovers, we're committed to quality and transparency.">
            <link rel="canonical" href="{{ request.build_absolute_uri }}">
        </head>
        <body data-testid="content-loaded">
            <header>
                <nav>
                    <h1>🐕 Dogify</h1>
                    <ul style="list-style: none; display: flex; gap: 20px;">
                        <li><a href="/">Home</a></li>
                        <li><a href="/shop">Shop</a></li>
                        <li><a href="/about">About</a></li>
                        <li><a href="/contact">Contact</a></li>
                    </ul>
                </nav>
            </header>
            
            <main style="max-width: 1200px; margin: 0 auto; padding: 20px;">
                <h1>About Dogify</h1>
                
                <section>
                    <p>We're passionate about providing premium nutrition and care products that keep your furry family members healthy, happy, and thriving. Since our founding, we've been committed to quality, transparency, and the wellbeing of dogs everywhere.</p>
                </section>
                
                <section>
                    <h2>Our Story</h2>
                    <p>Dogify was founded in 2018 by a team of dog lovers who were frustrated by the lack of transparency and quality in the pet food industry. After struggling to find nutritious, honest food options for our own dogs, we decided to create the solution ourselves.</p>
                    
                    <p>We started with a simple mission: to provide dog owners with premium, transparent nutrition that they can trust. Every product we offer is carefully vetted for quality, sourced from reputable suppliers, and tested to meet our high standards.</p>
                </section>
                
                <section>
                    <h2>Our Values</h2>
                    <ul>
                        <li><strong>Quality First:</strong> We never compromise on quality. Every product undergoes rigorous testing.</li>
                        <li><strong>Natural Ingredients:</strong> We believe in the power of natural, wholesome ingredients.</li>
                        <li><strong>Made with Love:</strong> Every decision is guided by our love for dogs.</li>
                        <li><strong>Transparency:</strong> Full ingredient transparency, always.</li>
                    </ul>
                </section>
                
                <section>
                    <h2>Contact Us</h2>
                    <p>Have questions? We'd love to hear from you!</p>
                    <ul>
                        <li>Email: support@dogify.com</li>
                        <li>Phone: 1-800-DOGIFY-1</li>
                        <li>Address: 123 Pet Paradise Lane, Austin, TX 78701</li>
                    </ul>
                </section>
            </main>
        </body>
        </html>
        """
        
        template = Template(html)
        context = Context({'request': request})
        return HttpResponse(template.render(context))
    
    def generate_contact_html(self, request):
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
        </head>
        <body data-testid="content-loaded">
            <header>
                <nav>
                    <h1>🐕 Dogify</h1>
                    <ul style="list-style: none; display: flex; gap: 20px;">
                        <li><a href="/">Home</a></li>
                        <li><a href="/shop">Shop</a></li>
                        <li><a href="/about">About</a></li>
                        <li><a href="/contact">Contact</a></li>
                    </ul>
                </nav>
            </header>
            
            <main style="max-width: 1200px; margin: 0 auto; padding: 20px;">
                <h1>Get in Touch</h1>
                <p>Have questions about our products or need help finding the right nutrition for your dog? We're here to help and would love to hear from you!</p>
                
                <section style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 40px 0;">
                    <div style="text-align: center; padding: 20px; border: 1px solid #e2e8f0; border-radius: 8px;">
                        <h3>💬 Live Chat</h3>
                        <p>Get instant help from our support team</p>
                    </div>
                    <div style="text-align: center; padding: 20px; border: 1px solid #e2e8f0; border-radius: 8px;">
                        <h3>📞 Call Us</h3>
                        <p>1-800-DOGIFY-1 (1-800-364-4391)</p>
                        <p>Mon-Fri: 8AM-8PM CST</p>
                    </div>
                    <div style="text-align: center; padding: 20px; border: 1px solid #e2e8f0; border-radius: 8px;">
                        <h3>✉️ Email Support</h3>
                        <p>support@dogify.com</p>
                        <p>Response within 24 hours</p>
                    </div>
                </section>
                
                <section>
                    <h2>Contact Information</h2>
                    <div>
                        <h3>📍 Address</h3>
                        <address>
                            Dogify Headquarters<br>
                            123 Pet Paradise Lane<br>
                            Austin, TX 78701<br>
                            United States
                        </address>
                    </div>
                    
                    <div>
                        <h3>🕐 Business Hours</h3>
                        <ul>
                            <li>Monday - Friday: 8:00 AM - 8:00 PM CST</li>
                            <li>Saturday: 9:00 AM - 6:00 PM CST</li>
                            <li>Sunday: 10:00 AM - 4:00 PM CST</li>
                        </ul>
                    </div>
                </section>
                
                <section>
                    <h2>Frequently Asked Questions</h2>
                    <details>
                        <summary>How do I choose the right food for my dog?</summary>
                        <p>Consider your dog's age, size, activity level, and any dietary sensitivities. Our nutrition experts are happy to provide personalized recommendations.</p>
                    </details>
                    <details>
                        <summary>What's your return policy?</summary>
                        <p>We offer a 30-day satisfaction guarantee. If your dog doesn't love our food, we'll provide a full refund or exchange.</p>
                    </details>
                    <details>
                        <summary>Do you offer subscription discounts?</summary>
                        <p>Yes! Save 15% on recurring orders with our subscription service. You can modify, pause, or cancel anytime.</p>
                    </details>
                </section>
            </main>
        </body>
        </html>
        """
        
        template = Template(html)
        context = Context({'request': request})
        return HttpResponse(template.render(context))
    
    def generate_default_html(self, request):
        """Generate default HTML for unknown routes"""
        html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Dogify - Premium Dog Food & Nutrition</title>
            <meta name="description" content="Premium nutrition for your furry friends. Shop high-quality dog food, treats, and wellness products.">
        </head>
        <body data-testid="content-loaded">
            <header>
                <h1>🐕 Dogify</h1>
                <nav>
                    <ul style="list-style: none; display: flex; gap: 20px;">
                        <li><a href="/">Home</a></li>
                        <li><a href="/shop">Shop</a></li>
                        <li><a href="/about">About</a></li>
                        <li><a href="/contact">Contact</a></li>
                    </ul>
                </nav>
            </header>
            <main style="max-width: 1200px; margin: 0 auto; padding: 20px;">
                <h1>Welcome to Dogify</h1>
                <p>Premium nutrition for your furry family members.</p>
                <a href="/shop">Shop Now</a>
            </main>
        </body>
        </html>
        """
        
        template = Template(html)
        context