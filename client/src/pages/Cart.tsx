import React from 'react';
import { Link } from 'react-router-dom';
import { Plus, Minus, X, ArrowLeft, ShoppingBag } from 'lucide-react';
import { useCart } from '../contexts/CartContext';

const Cart: React.FC = () => {
  const { cart, updateQuantity, removeFromCart, cartTotal, cartItemCount } = useCart();

  const shippingThreshold = 50;
  const shippingCost = cartTotal >= shippingThreshold ? 0 : 9.99;
  const tax = cartTotal * 0.08; // 8% tax
  const finalTotal = cartTotal + shippingCost + tax;

  if (cart.length === 0) {
    return (
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="text-center">
          <ShoppingBag className="h-24 w-24 text-gray-400 mx-auto mb-6" />
          <h1 className="text-3xl font-bold text-gray-900 mb-4">Your Cart is Empty</h1>
          <p className="text-gray-600 mb-8">
            Looks like you haven't added any products to your cart yet.
          </p>
          <Link
            to="/shop"
            className="bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors inline-flex items-center gap-2"
          >
            <ArrowLeft className="w-5 h-5" />
            Continue Shopping
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex items-center gap-4 mb-8">
        <Link
          to="/shop"
          className="text-blue-600 hover:text-blue-700 flex items-center gap-2"
        >
          <ArrowLeft className="w-4 h-4" />
          Continue Shopping
        </Link>
        <h1 className="text-3xl font-bold text-gray-900">
          Shopping Cart ({cartItemCount} {cartItemCount === 1 ? 'item' : 'items'})
        </h1>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Cart Items */}
        <div className="lg:col-span-2 space-y-4">
          {cart.map(item => (
            <div key={item.id} className="bg-white p-6 rounded-lg shadow-sm border">
              <div className="flex items-center gap-4">
                <Link to={`/product/${item.id}`} className="flex-shrink-0">
                  <img
                    src={item.image}
                    alt={item.name}
                    className="w-20 h-20 object-cover rounded-lg hover:opacity-75 transition-opacity"
                  />
                </Link>
                
                <div className="flex-1 min-w-0">
                  <Link 
                    to={`/product/${item.id}`}
                    className="text-lg font-semibold text-gray-900 hover:text-blue-600 transition-colors block truncate"
                  >
                    {item.name}
                  </Link>
                  <p className="text-gray-600 text-sm truncate">{item.description}</p>
                  <div className="flex items-center gap-2 mt-1">
                    <span className="text-green-600 font-bold">${item.price}</span>
                    <span className="text-gray-500">• {item.weight}</span>
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  {/* Quantity Controls */}
                  <div className="flex items-center border border-gray-300 rounded-lg">
                    <button
                      onClick={() => updateQuantity(item.id, item.quantity - 1)}
                      className="p-2 hover:bg-gray-100 transition-colors"
                      aria-label="Decrease quantity"
                    >
                      <Minus className="w-4 h-4" />
                    </button>
                    <span className="px-4 py-2 font-medium min-w-[3rem] text-center">
                      {item.quantity}
                    </span>
                    <button
                      onClick={() => updateQuantity(item.id, item.quantity + 1)}
                      className="p-2 hover:bg-gray-100 transition-colors"
                      aria-label="Increase quantity"
                    >
                      <Plus className="w-4 h-4" />
                    </button>
                  </div>

                  {/* Item Total */}
                  <div className="text-right min-w-[4rem]">
                    <p className="font-semibold text-gray-900">
                      ${(item.price * item.quantity).toFixed(2)}
                    </p>
                  </div>

                  {/* Remove Button */}
                  <button
                    onClick={() => removeFromCart(item.id)}
                    className="p-2 text-red-500 hover:text-red-700 hover:bg-red-50 rounded-lg transition-colors"
                    aria-label="Remove item"
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Order Summary */}
        <div className="lg:col-span-1">
          <div className="bg-white p-6 rounded-lg shadow-sm border sticky top-8">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Order Summary</h2>
            
            <div className="space-y-3 mb-4">
              <div className="flex justify-between">
                <span className="text-gray-600">Subtotal</span>
                <span className="font-medium">${cartTotal.toFixed(2)}</span>
              </div>
              
              <div className="flex justify-between">
                <span className="text-gray-600">Shipping</span>
                <span className="font-medium">
                  {shippingCost === 0 ? 'Free' : `$${shippingCost.toFixed(2)}`}
                </span>
              </div>
              
              {cartTotal < shippingThreshold && (
                <div className="text-sm text-amber-600 bg-amber-50 p-3 rounded-lg">
                  Add ${(shippingThreshold - cartTotal).toFixed(2)} more for free shipping!
                </div>
              )}
              
              <div className="flex justify-between">
                <span className="text-gray-600">Tax</span>
                <span className="font-medium">${tax.toFixed(2)}</span>
              </div>
              
              <div className="border-t pt-3">
                <div className="flex justify-between">
                  <span className="text-lg font-semibold text-gray-900">Total</span>
                  <span className="text-lg font-semibold text-gray-900">
                    ${finalTotal.toFixed(2)}
                  </span>
                </div>
              </div>
            </div>

            <Link
              to="/checkout"
              className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg font-semibold hover:bg-blue-700 transition-colors text-center block"
            >
              Proceed to Checkout
            </Link>

            <div className="mt-4 space-y-2 text-sm text-gray-600">
              <div className="flex items-center gap-2">
                <span>🚚</span>
                <span>Free shipping on orders over $50</span>
              </div>
              <div className="flex items-center gap-2">
                <span>🔒</span>
                <span>Secure checkout guaranteed</span>
              </div>
              <div className="flex items-center gap-2">
                <span>↩️</span>
                <span>30-day return policy</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Continue Shopping CTA */}
      <div className="mt-12 text-center">
        <Link
          to="/shop"
          className="text-blue-600 hover:text-blue-700 font-medium inline-flex items-center gap-2"
        >
          <ArrowLeft className="w-4 h-4" />
          Continue Shopping for More Products
        </Link>
      </div>
    </div>
  );
};

export default Cart;