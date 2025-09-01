import React from 'react';
import { Heart, Shield, Truck, Users, Award, Leaf } from 'lucide-react';

const About: React.FC = () => {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Hero Section */}
      <section className="text-center mb-16">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">About Dogify</h1>
        <p className="text-xl text-gray-600 max-w-3xl mx-auto">
          We're passionate about providing premium nutrition and care products that keep your furry family members 
          healthy, happy, and thriving. Since our founding, we've been committed to quality, transparency, and the 
          wellbeing of dogs everywhere.
        </p>
      </section>

      {/* Story Section */}
      <section className="grid grid-cols-1 lg:grid-cols-2 gap-12 mb-16">
        <div className="order-2 lg:order-1">
          <h2 className="text-3xl font-bold text-gray-900 mb-6">Our Story</h2>
          <div className="space-y-4 text-gray-700">
            <p>
              Dogify was founded in 2018 by a team of dog lovers who were frustrated by the lack of transparency 
              and quality in the pet food industry. After struggling to find nutritious, honest food options for 
              our own dogs, we decided to create the solution ourselves.
            </p>
            <p>
              We started with a simple mission: to provide dog owners with premium, transparent nutrition that 
              they can trust. Every product we offer is carefully vetted for quality, sourced from reputable 
              suppliers, and tested to meet our high standards.
            </p>
            <p>
              Today, we're proud to serve thousands of dog families across the country, helping pets live 
              healthier, happier lives through better nutrition. But our mission remains the same – to be 
              your trusted partner in your dog's health journey.
            </p>
          </div>
        </div>
        <div className="order-1 lg:order-2">
          <img
            src="https://images.unsplash.com/photo-1601758228006-78bb32e815be?w=600&h=400&fit=crop"
            alt="Happy dogs playing"
            className="w-full h-80 object-cover rounded-lg shadow-lg"
          />
        </div>
      </section>

      {/* Values Section */}
      <section className="mb-16">
        <h2 className="text-3xl font-bold text-gray-900 text-center mb-12">Our Values</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          <div className="text-center p-6">
            <div className="bg-blue-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
              <Shield className="w-8 h-8 text-blue-600" />
            </div>
            <h3 className="text-xl font-semibold mb-3">Quality First</h3>
            <p className="text-gray-600">
              We never compromise on quality. Every product undergoes rigorous testing and meets our strict 
              standards before reaching your dog.
            </p>
          </div>
          
          <div className="text-center p-6">
            <div className="bg-green-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
              <Leaf className="w-8 h-8 text-green-600" />
            </div>
            <h3 className="text-xl font-semibold mb-3">Natural Ingredients</h3>
            <p className="text-gray-600">
              We believe in the power of natural, wholesome ingredients. No unnecessary fillers, 
              artificial colors, or harmful preservatives.
            </p>
          </div>
          
          <div className="text-center p-6">
            <div className="bg-purple-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
              <Heart className="w-8 h-8 text-purple-600" />
            </div>
            <h3 className="text-xl font-semibold mb-3">Made with Love</h3>
            <p className="text-gray-600">
              Every decision we make is guided by our love for dogs. We treat every customer's pet 
              like our own family member.
            </p>
          </div>
          
          <div className="text-center p-6">
            <div className="bg-yellow-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
              <Award className="w-8 h-8 text-yellow-600" />
            </div>
            <h3 className="text-xl font-semibold mb-3">Transparency</h3>
            <p className="text-gray-600">
              We believe you have the right to know exactly what you're feeding your dog. 
              Full ingredient transparency, always.
            </p>
          </div>
          
          <div className="text-center p-6">
            <div className="bg-red-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
              <Users className="w-8 h-8 text-red-600" />
            </div>
            <h3 className="text-xl font-semibold mb-3">Community</h3>
            <p className="text-gray-600">
              We're more than a business – we're a community of dog lovers supporting each other 
              in providing the best care for our pets.
            </p>
          </div>
          
          <div className="text-center p-6">
            <div className="bg-indigo-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
              <Truck className="w-8 h-8 text-indigo-600" />
            </div>
            <h3 className="text-xl font-semibold mb-3">Reliable Service</h3>
            <p className="text-gray-600">
              Fast, reliable delivery and exceptional customer service. We're here when you need us, 
              with support that actually helps.
            </p>
          </div>
        </div>
      </section>

      {/* Team Section */}
      <section className="mb-16">
        <h2 className="text-3xl font-bold text-gray-900 text-center mb-12">Meet Our Team</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="text-center">
            <img
              src="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200&h=200&fit=crop&crop=face"
              alt="Sarah Johnson"
              className="w-32 h-32 rounded-full mx-auto mb-4 object-cover"
            />
            <h3 className="text-xl font-semibold mb-2">Sarah Johnson</h3>
            <p className="text-blue-600 font-medium mb-2">Founder & CEO</p>
            <p className="text-gray-600 text-sm">
              Former veterinary nutritionist with 15 years of experience in pet health and nutrition.
            </p>
          </div>
          
          <div className="text-center">
            <img
              src="https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=200&h=200&fit=crop&crop=face"
              alt="Mike Chen"
              className="w-32 h-32 rounded-full mx-auto mb-4 object-cover"
            />
            <h3 className="text-xl font-semibold mb-2">Mike Chen</h3>
            <p className="text-blue-600 font-medium mb-2">Head of Quality</p>
            <p className="text-gray-600 text-sm">
              Ensures every product meets our strict quality standards through comprehensive testing and oversight.
            </p>
          </div>
          
          <div className="text-center">
            <img
              src="https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=200&h=200&fit=crop&crop=face"
              alt="Emma Rodriguez"
              className="w-32 h-32 rounded-full mx-auto mb-4 object-cover"
            />
            <h3 className="text-xl font-semibold mb-2">Emma Rodriguez</h3>
            <p className="text-blue-600 font-medium mb-2">Customer Success</p>
            <p className="text-gray-600 text-sm">
              Dedicated to ensuring every customer and their furry friend has an amazing experience with Dogify.
            </p>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="bg-blue-600 text-white py-16 px-8 rounded-2xl mb-16">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12">Our Impact</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
            <div>
              <div className="text-4xl font-bold mb-2">50K+</div>
              <div className="text-blue-100">Happy Dogs</div>
            </div>
            <div>
              <div className="text-4xl font-bold mb-2">25K+</div>
              <div className="text-blue-100">Families Served</div>
            </div>
            <div>
              <div className="text-4xl font-bold mb-2">98%</div>
              <div className="text-blue-100">Satisfaction Rate</div>
            </div>
            <div>
              <div className="text-4xl font-bold mb-2">5</div>
              <div className="text-blue-100">Years of Service</div>
            </div>
          </div>
        </div>
      </section>

      {/* Contact CTA */}
      <section className="text-center">
        <h2 className="text-3xl font-bold text-gray-900 mb-4">Have Questions?</h2>
        <p className="text-gray-600 mb-8 max-w-2xl mx-auto">
          We'd love to hear from you! Whether you have questions about our products, need help choosing 
          the right food for your dog, or just want to chat about your furry friend, we're here to help.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <a
            href="/contact"
            className="bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
          >
            Contact Us
          </a>
          <a
            href="mailto:hello@dogify.com"
            className="border-2 border-blue-600 text-blue-600 px-8 py-3 rounded-lg font-semibold hover:bg-blue-600 hover:text-white transition-colors"
          >
            Email Us
          </a>
        </div>
      </section>
    </div>
  );
};

export default About;