import React from 'react';
import { Link } from 'react-router-dom';
import { Dog } from 'lucide-react';

const Footer: React.FC = () => {
  return (
    <footer className="bg-gray-900 text-white py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div>
            <Link to="/" className="flex items-center mb-4">
              <Dog className="h-6 w-6 text-blue-400 mr-2" />
              <span className="font-bold text-lg">Dogify</span>
            </Link>
            <p className="text-gray-400">Premium nutrition for your furry family members.</p>
          </div>
          
          <div>
            <h3 className="font-semibold mb-4">Shop</h3>
            <ul className="space-y-2 text-gray-400">
              <li><Link to="/shop?category=Dry Food" className="hover:text-white transition-colors">Dry Food</Link></li>
              <li><Link to="/shop?category=Wet Food" className="hover:text-white transition-colors">Wet Food</Link></li>
              <li><Link to="/shop?category=Treats" className="hover:text-white transition-colors">Treats</Link></li>
              <li><Link to="/shop" className="hover:text-white transition-colors">All Products</Link></li>
            </ul>
          </div>
          
          <div>
            <h3 className="font-semibold mb-4">Company</h3>
            <ul className="space-y-2 text-gray-400">
              <li><Link to="/about" className="hover:text-white transition-colors">About Us</Link></li>
              <li><Link to="/contact" className="hover:text-white transition-colors">Contact</Link></li>
              <li><a href="#" className="hover:text-white transition-colors">FAQ</a></li>
              <li><a href="#" className="hover:text-white transition-colors">Shipping Info</a></li>
            </ul>
          </div>
          
          <div>
            <h3 className="font-semibold mb-4">Newsletter</h3>
            <p className="text-gray-400 mb-4">Subscribe for updates and special offers.</p>
            <div className="space-y-2">
              <input
                type="email"
                placeholder="Your email"
                className="w-full p-3 rounded bg-gray-800 text-white border border-gray-700 focus:border-blue-500 focus:outline-none"
              />
              <button className="w-full bg-blue-600 text-white py-3 rounded hover:bg-blue-700 transition-colors">
                Subscribe
              </button>
            </div>
          </div>
        </div>
        
        <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400">
          <p>&copy; 2025 Dogify. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;