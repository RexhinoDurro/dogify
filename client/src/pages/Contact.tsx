import React, { useState } from 'react';
import { Mail, Phone, MapPin, Clock, Send, MessageCircle, Headphones, Package, HelpCircle } from 'lucide-react';

const Contact: React.FC = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    subject: '',
    message: '',
    petName: '',
    petBreed: '',
    petAge: '',
    orderNumber: ''
  });

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitStatus, setSubmitStatus] = useState<'idle' | 'success' | 'error'>('idle');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    
    // Simulate form submission
    try {
      await new Promise(resolve => setTimeout(resolve, 2000));
      setSubmitStatus('success');
      setFormData({
        name: '',
        email: '',
        subject: '',
        message: '',
        petName: '',
        petBreed: '',
        petAge: '',
        orderNumber: ''
      });
    } catch (error) {
      setSubmitStatus('error');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    if (submitStatus !== 'idle') setSubmitStatus('idle');
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <section className="text-center mb-16">
        <h1 className="text-5xl font-bold text-gray-900 mb-6">Get in Touch</h1>
        <p className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
          Have questions about our products or need help finding the right nutrition for your dog? 
          We're here to help and would love to hear from you! Our team of pet nutrition experts 
          is ready to assist you and your furry friend.
        </p>
      </section>

      {/* Quick Contact Options */}
      <section className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-16">
        <div className="bg-gradient-to-br from-blue-50 to-blue-100 p-6 rounded-xl text-center hover:shadow-lg transition-shadow">
          <div className="bg-blue-600 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
            <MessageCircle className="w-8 h-8 text-white" />
          </div>
          <h3 className="font-bold text-lg mb-2">Live Chat</h3>
          <p className="text-gray-600 text-sm mb-4">Get instant help from our support team</p>
          <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors">
            Start Chat
          </button>
        </div>

        <div className="bg-gradient-to-br from-green-50 to-green-100 p-6 rounded-xl text-center hover:shadow-lg transition-shadow">
          <div className="bg-green-600 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
            <Phone className="w-8 h-8 text-white" />
          </div>
          <h3 className="font-bold text-lg mb-2">Call Us</h3>
          <p className="text-gray-600 text-sm mb-4">Speak directly with our experts</p>
          <a href="tel:1-800-364-4391" className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors inline-block">
            Call Now
          </a>
        </div>

        <div className="bg-gradient-to-br from-purple-50 to-purple-100 p-6 rounded-xl text-center hover:shadow-lg transition-shadow">
          <div className="bg-purple-600 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
            <Mail className="w-8 h-8 text-white" />
          </div>
          <h3 className="font-bold text-lg mb-2">Email Support</h3>
          <p className="text-gray-600 text-sm mb-4">Send us your questions anytime</p>
          <a href="mailto:support@dogify.com" className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 transition-colors inline-block">
            Send Email
          </a>
        </div>

        <div className="bg-gradient-to-br from-orange-50 to-orange-100 p-6 rounded-xl text-center hover:shadow-lg transition-shadow">
          <div className="bg-orange-600 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
            <HelpCircle className="w-8 h-8 text-white" />
          </div>
          <h3 className="font-bold text-lg mb-2">Help Center</h3>
          <p className="text-gray-600 text-sm mb-4">Browse our knowledge base</p>
          <button className="bg-orange-600 text-white px-4 py-2 rounded-lg hover:bg-orange-700 transition-colors">
            View FAQs
          </button>
        </div>
      </section>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
        {/* Contact Form */}
        <div className="bg-white p-8 rounded-2xl shadow-lg border">
          <h2 className="text-3xl font-bold text-gray-900 mb-2">Send us a Message</h2>
          <p className="text-gray-600 mb-8">Fill out the form below and we'll get back to you within 24 hours.</p>
          
          {submitStatus === 'success' && (
            <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg">
              <div className="flex items-center gap-3">
                <div className="bg-green-500 rounded-full p-1">
                  <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <div>
                  <h4 className="font-medium text-green-800">Message sent successfully!</h4>
                  <p className="text-green-600 text-sm">We'll get back to you soon.</p>
                </div>
              </div>
            </div>
          )}

          {submitStatus === 'error' && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
              <div className="flex items-center gap-3">
                <div className="bg-red-500 rounded-full p-1">
                  <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </div>
                <div>
                  <h4 className="font-medium text-red-800">Something went wrong</h4>
                  <p className="text-red-600 text-sm">Please try again or contact us directly.</p>
                </div>
              </div>
            </div>
          )}
          
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Personal Information */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label htmlFor="name" className="block text-sm font-semibold text-gray-700 mb-2">
                  Your Name *
                </label>
                <input
                  type="text"
                  id="name"
                  name="name"
                  required
                  value={formData.name}
                  onChange={handleInputChange}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                  placeholder="John Doe"
                />
              </div>
              
              <div>
                <label htmlFor="email" className="block text-sm font-semibold text-gray-700 mb-2">
                  Email Address *
                </label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  required
                  value={formData.email}
                  onChange={handleInputChange}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                  placeholder="john@example.com"
                />
              </div>
            </div>

            {/* Pet Information */}
            <div className="bg-blue-50 p-6 rounded-lg">
              <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <span>🐕</span>
                Tell us about your dog (optional)
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div>
                  <label htmlFor="petName" className="block text-sm font-medium text-gray-700 mb-2">
                    Dog's Name
                  </label>
                  <input
                    type="text"
                    id="petName"
                    name="petName"
                    value={formData.petName}
                    onChange={handleInputChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Buddy"
                  />
                </div>
                
                <div>
                  <label htmlFor="petBreed" className="block text-sm font-medium text-gray-700 mb-2">
                    Breed
                  </label>
                  <input
                    type="text"
                    id="petBreed"
                    name="petBreed"
                    value={formData.petBreed}
                    onChange={handleInputChange}
                    placeholder="Golden Retriever"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label htmlFor="petAge" className="block text-sm font-medium text-gray-700 mb-2">
                    Age
                  </label>
                  <select
                    id="petAge"
                    name="petAge"
                    value={formData.petAge}
                    onChange={handleInputChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="">Select age</option>
                    <option value="puppy">Puppy (0-1 year)</option>
                    <option value="young">Young (1-3 years)</option>
                    <option value="adult">Adult (3-7 years)</option>
                    <option value="senior">Senior (7+ years)</option>
                  </select>
                </div>
              </div>
            </div>

            {/* Subject and Order Info */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label htmlFor="subject" className="block text-sm font-semibold text-gray-700 mb-2">
                  Subject *
                </label>
                <select
                  id="subject"
                  name="subject"
                  required
                  value={formData.subject}
                  onChange={handleInputChange}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">Select a topic</option>
                  <option value="product-question">Product Question</option>
                  <option value="nutrition-advice">Nutrition Advice</option>
                  <option value="order-support">Order Support</option>
                  <option value="shipping">Shipping Inquiry</option>
                  <option value="return">Return/Exchange</option>
                  <option value="subscription">Subscription Help</option>
                  <option value="complaint">Complaint</option>
                  <option value="compliment">Compliment</option>
                  <option value="partnership">Partnership Inquiry</option>
                  <option value="other">Other</option>
                </select>
              </div>

              <div>
                <label htmlFor="orderNumber" className="block text-sm font-medium text-gray-700 mb-2">
                  Order Number (if applicable)
                </label>
                <input
                  type="text"
                  id="orderNumber"
                  name="orderNumber"
                  value={formData.orderNumber}
                  onChange={handleInputChange}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="#12345"
                />
              </div>
            </div>

            <div>
              <label htmlFor="message" className="block text-sm font-semibold text-gray-700 mb-2">
                Message *
              </label>
              <textarea
                id="message"
                name="message"
                required
                rows={6}
                value={formData.message}
                onChange={handleInputChange}
                placeholder="Tell us how we can help you and your furry friend. The more details you provide, the better we can assist you!"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-vertical"
              />
              <p className="text-sm text-gray-500 mt-1">Minimum 10 characters</p>
            </div>

            <button
              type="submit"
              disabled={isSubmitting}
              className={`w-full py-4 px-6 rounded-lg font-semibold transition-all duration-200 flex items-center justify-center gap-3 ${
                isSubmitting
                  ? 'bg-gray-400 cursor-not-allowed'
                  : 'bg-blue-600 hover:bg-blue-700 transform hover:scale-105'
              } text-white shadow-lg`}
            >
              {isSubmitting ? (
                <>
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Sending...
                </>
              ) : (
                <>
                  <Send className="w-5 h-5" />
                  Send Message
                </>
              )}
            </button>
          </form>
        </div>

        {/* Contact Information & Additional Sections */}
        <div className="space-y-8">
          {/* Contact Details */}
          <div className="bg-white p-8 rounded-2xl shadow-lg border">
            <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-2">
              <Headphones className="w-6 h-6 text-blue-600" />
              Contact Information
            </h2>
            
            <div className="space-y-6">
              <div className="flex items-start gap-4">
                <div className="bg-blue-100 p-3 rounded-lg">
                  <Mail className="w-6 h-6 text-blue-600" />
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900 mb-1">Email</h3>
                  <div className="space-y-1">
                    <p className="text-gray-600">
                      <span className="font-medium">General Support:</span>{' '}
                      <a href="mailto:support@dogify.com" className="text-blue-600 hover:underline">
                        support@dogify.com
                      </a>
                    </p>
                    <p className="text-gray-600">
                      <span className="font-medium">Orders:</span>{' '}
                      <a href="mailto:orders@dogify.com" className="text-blue-600 hover:underline">
                        orders@dogify.com
                      </a>
                    </p>
                    <p className="text-gray-600">
                      <span className="font-medium">Partnerships:</span>{' '}
                      <a href="mailto:partnerships@dogify.com" className="text-blue-600 hover:underline">
                        partnerships@dogify.com
                      </a>
                    </p>
                  </div>
                </div>
              </div>
              
              <div className="flex items-start gap-4">
                <div className="bg-green-100 p-3 rounded-lg">
                  <Phone className="w-6 h-6 text-green-600" />
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900 mb-1">Phone</h3>
                  <div className="space-y-1">
                    <p className="text-gray-600">
                      <span className="font-bold text-lg">1-800-DOGIFY-1</span><br />
                      <span className="text-sm">(1-800-364-4391)</span>
                    </p>
                    <p className="text-sm text-gray-500">Toll-free customer support</p>
                    <p className="text-sm text-green-600 font-medium">Average wait time: &lt; 2 minutes</p>
                  </div>
                </div>
              </div>
              
              <div className="flex items-start gap-4">
                <div className="bg-purple-100 p-3 rounded-lg">
                  <MapPin className="w-6 h-6 text-purple-600" />
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900 mb-1">Address</h3>
                  <div className="text-gray-600">
                    <p className="font-medium">Dogify Headquarters</p>
                    <p>123 Pet Paradise Lane<br />
                    Austin, TX 78701<br />
                    United States</p>
                  </div>
                </div>
              </div>
              
              <div className="flex items-start gap-4">
                <div className="bg-orange-100 p-3 rounded-lg">
                  <Clock className="w-6 h-6 text-orange-600" />
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900 mb-1">Business Hours</h3>
                  <div className="text-gray-600 space-y-1">
                    <div className="flex justify-between">
                      <span>Monday - Friday:</span>
                      <span className="font-medium">8:00 AM - 8:00 PM CST</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Saturday:</span>
                      <span className="font-medium">9:00 AM - 6:00 PM CST</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Sunday:</span>
                      <span className="font-medium">10:00 AM - 4:00 PM CST</span>
                    </div>
                    <p className="text-sm text-green-600 font-medium mt-2">
                      🟢 Currently open
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* FAQ Section */}
          <div className="bg-gradient-to-br from-blue-50 to-indigo-100 p-8 rounded-2xl border">
            <h3 className="text-xl font-bold text-gray-900 mb-6 flex items-center gap-2">
              <HelpCircle className="w-6 h-6 text-blue-600" />
              Frequently Asked Questions
            </h3>
            <div className="space-y-6">
              <div className="bg-white p-4 rounded-lg">
                <h4 className="font-semibold text-gray-900 mb-2">How do I choose the right food for my dog?</h4>
                <p className="text-gray-600 text-sm">
                  Consider your dog's age, size, activity level, and any dietary sensitivities. Our nutrition experts 
                  are happy to provide personalized recommendations based on your dog's specific needs.
                </p>
              </div>
              
              <div className="bg-white p-4 rounded-lg">
                <h4 className="font-semibold text-gray-900 mb-2">What's your return policy?</h4>
                <p className="text-gray-600 text-sm">
                  We offer a 30-day satisfaction guarantee. If your dog doesn't love our food, we'll provide 
                  a full refund or exchange. No questions asked!
                </p>
              </div>
              
              <div className="bg-white p-4 rounded-lg">
                <h4 className="font-semibold text-gray-900 mb-2">Do you offer subscription discounts?</h4>
                <p className="text-gray-600 text-sm">
                  Yes! Save 15% on recurring orders with our subscription service. You can modify, pause, 
                  or cancel anytime with no commitment.
                </p>
              </div>

              <div className="bg-white p-4 rounded-lg">
                <h4 className="font-semibold text-gray-900 mb-2">How fast is shipping?</h4>
                <p className="text-gray-600 text-sm">
                  Free standard shipping on orders over $50 (3-5 business days). Express shipping available 
                  for $12.99 (1-2 business days).
                </p>
              </div>
            </div>
            
            <div className="mt-6 text-center">
              <button className="bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors">
                View All FAQs
              </button>
            </div>
          </div>

          {/* Emergency Contact */}
          <div className="bg-red-50 p-6 rounded-2xl border-2 border-red-200">
            <h3 className="text-lg font-bold text-red-900 mb-3 flex items-center gap-2">
              🚨 Pet Emergency?
            </h3>
            <p className="text-red-700 mb-4">
              If your pet is experiencing a medical emergency, please contact your veterinarian 
              or animal emergency clinic immediately. Do not wait for our response.
            </p>
            <div className="space-y-2">
              <div className="bg-white p-3 rounded-lg">
                <p className="text-red-800 font-semibold">Pet Poison Helpline</p>
                <p className="text-red-600">1-855-764-7661 (24/7)</p>
              </div>
              <div className="bg-white p-3 rounded-lg">
                <p className="text-red-800 font-semibold">ASPCA Animal Poison Control</p>
                <p className="text-red-600">1-888-426-4435 (24/7)</p>
              </div>
            </div>
          </div>

          {/* Social Media */}
          <div className="bg-white p-8 rounded-2xl shadow-lg border text-center">
            <h3 className="text-xl font-bold text-gray-900 mb-4">Follow Us</h3>
            <p className="text-gray-600 mb-6">Stay connected for tips, updates, and adorable dog photos!</p>
            <div className="flex justify-center gap-4">
              <button className="bg-blue-600 hover:bg-blue-700 text-white p-3 rounded-full transition-colors">
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M24 4.557c-.883.392-1.832.656-2.828.775 1.017-.609 1.798-1.574 2.165-2.724-.951.564-2.005.974-3.127 1.195-.897-.957-2.178-1.555-3.594-1.555-3.179 0-5.515 2.966-4.797 6.045-4.091-.205-7.719-2.165-10.148-5.144-1.29 2.213-.669 5.108 1.523 6.574-.806-.026-1.566-.247-2.229-.616-.054 2.281 1.581 4.415 3.949 4.89-.693.188-1.452.232-2.224.084.626 1.956 2.444 3.379 4.6 3.419-2.07 1.623-4.678 2.348-7.29 2.04 2.179 1.397 4.768 2.212 7.548 2.212 9.142 0 14.307-7.721 13.995-14.646.962-.695 1.797-1.562 2.457-2.549z"/>
                </svg>
              </button>
              <button className="bg-pink-600 hover:bg-pink-700 text-white p-3 rounded-full transition-colors">
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12.017 0C5.396 0 .029 5.367.029 11.987c0 5.079 3.158 9.417 7.618 11.174-.105-.949-.199-2.403.041-3.439.219-.937 1.406-5.957 1.406-5.957s-.359-.72-.359-1.781c0-1.663.967-2.911 2.168-2.911 1.024 0 1.518.769 1.518 1.688 0 1.029-.653 2.567-.992 3.992-.285 1.193.6 2.165 1.775 2.165 2.128 0 3.768-2.245 3.768-5.487 0-2.861-2.063-4.869-5.008-4.869-3.41 0-5.409 2.562-5.409 5.199 0 1.033.394 2.143.889 2.741.099.12.112.225.085.345-.09.375-.293 1.199-.334 1.363-.053.225-.172.271-.402.165-1.495-.69-2.433-2.878-2.433-4.646 0-3.776 2.748-7.252 7.92-7.252 4.158 0 7.392 2.967 7.392 6.923 0 4.135-2.607 7.462-6.233 7.462-1.214 0-2.357-.629-2.750-1.378l-.748 2.853c-.271 1.043-1.002 2.35-1.492 3.146C9.57 23.812 10.763 24.009 12.017 24.009c6.624 0 11.99-5.367 11.99-11.988C24.007 5.367 18.641.001.012.001z"/>
                </svg>
              </button>
              <button className="bg-indigo-600 hover:bg-indigo-700 text-white p-3 rounded-full transition-colors">
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12.017 0C5.396 0 .029 5.367.029 11.987c0 5.079 3.158 9.417 7.618 11.174-.105-.949-.199-2.403.041-3.439.219-.937 1.406-5.957 1.406-5.957s-.359-.72-.359-1.781c0-1.663.967-2.911 2.168-2.911 1.024 0 1.518.769 1.518 1.688 0 1.029-.653 2.567-.992 3.992-.285 1.193.6 2.165 1.775 2.165 2.128 0 3.768-2.245 3.768-5.487 0-2.861-2.063-4.869-5.008-4.869-3.41 0-5.409 2.562-5.409 5.199 0 1.033.394 2.143.889 2.741.099.12.112.225.085.345-.09.375-.293 1.199-.334 1.363-.053.225-.172.271-.402.165-1.495-.69-2.433-2.878-2.433-4.646 0-3.776 2.748-7.252 7.92-7.252 4.158 0 7.392 2.967 7.392 6.923 0 4.135-2.607 7.462-6.233 7.462-1.214 0-2.357-.629-2.750-1.378l-.748 2.853c-.271 1.043-1.002 2.35-1.492 3.146C9.57 23.812 10.763 24.009 12.017 24.009c6.624 0 11.99-5.367 11.99-11.988C24.007 5.367 18.641.001.012.001z"/>
                </svg>
              </button>
              <button className="bg-red-600 hover:bg-red-700 text-white p-3 rounded-full transition-colors">
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Map Section */}
      <section className="mt-16">
        <h2 className="text-3xl font-bold text-gray-900 mb-8 text-center">Visit Our Store</h2>
        <div className="bg-white rounded-2xl shadow-lg overflow-hidden">
          <div className="bg-gradient-to-r from-blue-500 to-purple-600 h-96 flex items-center justify-center relative">
            <div className="text-center text-white">
              <MapPin className="w-16 h-16 mx-auto mb-4 opacity-80" />
              <h3 className="text-2xl font-bold mb-2">Interactive Map Coming Soon</h3>
              <p className="text-blue-100 mb-4">123 Pet Paradise Lane, Austin, TX 78701</p>
              <div className="flex flex-col sm:flex-row gap-3 justify-center">
                <button className="bg-white text-blue-600 px-6 py-2 rounded-lg font-semibold hover:bg-gray-100 transition-colors">
                  Get Directions
                </button>
                <button className="border-2 border-white text-white px-6 py-2 rounded-lg font-semibold hover:bg-white hover:text-blue-600 transition-colors">
                  Store Hours
                </button>
              </div>
            </div>
            
            {/* Decorative elements */}
            <div className="absolute top-4 left-4 w-20 h-20 bg-white bg-opacity-10 rounded-full"></div>
            <div className="absolute bottom-8 right-8 w-32 h-32 bg-white bg-opacity-5 rounded-full"></div>
            <div className="absolute top-1/2 right-4 w-16 h-16 bg-white bg-opacity-10 rounded-full"></div>
          </div>
          
          <div className="p-8">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="text-center">
                <div className="bg-green-100 w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-3">
                  <Clock className="w-6 h-6 text-green-600" />
                </div>
                <h4 className="font-semibold mb-1">Store Hours</h4>
                <p className="text-gray-600 text-sm">Mon-Fri: 9AM-8PM<br />Sat-Sun: 10AM-6PM</p>
              </div>
              
              <div className="text-center">
                <div className="bg-blue-100 w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-3">
                  <Package className="w-6 h-6 text-blue-600" />
                </div>
                <h4 className="font-semibold mb-1">Curbside Pickup</h4>
                <p className="text-gray-600 text-sm">Available during<br />all business hours</p>
              </div>
              
              <div className="text-center">
                <div className="bg-purple-100 w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-3">
                  <MapPin className="w-6 h-6 text-purple-600" />
                </div>
                <h4 className="font-semibold mb-1">Easy Parking</h4>
                <p className="text-gray-600 text-sm">Free parking lot<br />with 50+ spaces</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Newsletter CTA */}
      <section className="mt-16 bg-gradient-to-r from-blue-600 to-purple-700 rounded-2xl p-8 md:p-12 text-white text-center">
        <h2 className="text-3xl font-bold mb-4">Stay in the Loop</h2>
        <p className="text-xl mb-8 text-blue-100">
          Get the latest pet care tips, product updates, and exclusive offers delivered to your inbox.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 max-w-md mx-auto">
          <input
            type="email"
            placeholder="Your email address"
            className="flex-1 px-6 py-4 rounded-lg text-gray-900 focus:outline-none focus:ring-4 focus:ring-white focus:ring-opacity-30"
          />
          <button className="bg-white text-blue-600 px-8 py-4 rounded-lg font-semibold hover:bg-gray-100 transition-colors whitespace-nowrap">
            Subscribe
          </button>
        </div>
        <p className="text-blue-200 text-sm mt-4">
          Join 25,000+ dog parents who trust our advice
        </p>
      </section>
    </div>
  );
};

export default Contact;