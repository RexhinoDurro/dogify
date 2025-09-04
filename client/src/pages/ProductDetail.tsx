import React, { useState } from 'react';
import { useParams, Link, Navigate } from 'react-router-dom';
import { Star, Heart, ShoppingCart, Plus, Minus, ArrowLeft, Truck, Shield, RotateCcw } from 'lucide-react';
import { getProductById, products } from '../data/products';
import { useCart } from '../contexts/CartContext';
import { useWishlist } from '../contexts/WishlistContext';
import ProductCard from '../components/ProductCard';

const ProductDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [quantity, setQuantity] = useState(1);
  const [activeTab, setActiveTab] = useState('description');
  
  const { addToCart } = useCart();
  const { toggleWishlist, isInWishlist } = useWishlist();

  if (!id) return <Navigate to="/shop" />;
  
  const product = getProductById(parseInt(id));
  
  if (!product) return <Navigate to="/shop" />;

  const relatedProducts = products
    .filter(p => p.category === product.category && p.id !== product.id)
    .slice(0, 4);

  const handleAddToCart = () => {
    for (let i = 0; i < quantity; i++) {
      addToCart(product);
    }
  };

  const adjustQuantity = (change: number) => {
    setQuantity(prev => Math.max(1, prev + change));
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-sm text-gray-600 mb-8">
        <Link to="/" className="hover:text-blue-600">Home</Link>
        <span>/</span>
        <Link to="/shop" className="hover:text-blue-600">Shop</Link>
        <span>/</span>
        <span className="text-gray-900">{product.name}</span>
      </div>

      {/* Back Button */}
      <Link
        to="/shop"
        className="inline-flex items-center gap-2 text-blue-600 hover:text-blue-700 mb-6"
      >
        <ArrowLeft className="w-4 h-4" />
        Back to Shop
      </Link>

      {/* Product Details */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 mb-12">
        {/* Product Image */}
        <div className="relative">
          <img
            src={product.image}
            alt={product.name}
            className="w-full h-96 lg:h-[500px] object-cover rounded-2xl"
          />
          {product.originalPrice && (
            <div className="absolute top-4 left-4 bg-red-500 text-white px-3 py-1 rounded-full text-sm font-bold">
              Save ${(product.originalPrice - product.price).toFixed(2)}
            </div>
          )}
          {!product.inStock && (
            <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center rounded-2xl">
              <span className="text-white font-bold text-xl">Out of Stock</span>
            </div>
          )}
        </div>

        {/* Product Info */}
        <div className="space-y-6">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <div className="flex items-center">
                {[...Array(5)].map((_, i) => (
                  <Star
                    key={i}
                    className={`w-5 h-5 ${i < Math.floor(product.rating) ? 'fill-yellow-400 text-yellow-400' : 'text-gray-300'}`}
                  />
                ))}
              </div>
              <span className="text-gray-600">({product.reviews} reviews)</span>
            </div>
            
            <h1 className="text-3xl font-bold text-gray-900 mb-2">{product.name}</h1>
            
            <div className="flex items-center gap-4 mb-4">
              <span className="text-3xl font-bold text-green-600">${product.price}</span>
              {product.originalPrice && (
                <span className="text-xl text-gray-400 line-through">${product.originalPrice}</span>
              )}
              <span className="text-gray-600">{product.weight}</span>
            </div>
            
            <p className="text-gray-700 text-lg">{product.description}</p>
          </div>

          {/* Quantity and Add to Cart */}
          {product.inStock && (
            <div className="space-y-4">
              <div className="flex items-center gap-4">
                <span className="text-gray-700 font-medium">Quantity:</span>
                <div className="flex items-center border border-gray-300 rounded-lg">
                  <button
                    onClick={() => adjustQuantity(-1)}
                    className="p-2 hover:bg-gray-100 transition-colors"
                  >
                    <Minus className="w-4 h-4" />
                  </button>
                  <span className="px-4 py-2 font-medium">{quantity}</span>
                  <button
                    onClick={() => adjustQuantity(1)}
                    className="p-2 hover:bg-gray-100 transition-colors"
                  >
                    <Plus className="w-4 h-4" />
                  </button>
                </div>
              </div>

              <div className="flex gap-3">
                <button
                  onClick={handleAddToCart}
                  className="flex-1 bg-blue-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-blue-700 transition-colors flex items-center justify-center gap-2"
                >
                  <ShoppingCart className="w-5 h-5" />
                  Add to Cart - ${(product.price * quantity).toFixed(2)}
                </button>
                
                <button
                  onClick={() => toggleWishlist(product.id)}
                  className={`p-3 rounded-lg border-2 transition-colors ${
                    isInWishlist(product.id)
                      ? 'border-red-500 bg-red-50 text-red-500'
                      : 'border-gray-300 hover:border-red-500 hover:text-red-500'
                  }`}
                >
                  <Heart className={`w-6 h-6 ${isInWishlist(product.id) ? 'fill-current' : ''}`} />
                </button>
              </div>
            </div>
          )}

          {/* Benefits */}
          <div className="grid grid-cols-3 gap-4 pt-6 border-t border-gray-200">
            <div className="text-center">
              <Truck className="w-8 h-8 text-blue-600 mx-auto mb-2" />
              <p className="text-sm font-medium">Free Shipping</p>
              <p className="text-xs text-gray-600">On orders $50+</p>
            </div>
            <div className="text-center">
              <Shield className="w-8 h-8 text-green-600 mx-auto mb-2" />
              <p className="text-sm font-medium">Quality Guarantee</p>
              <p className="text-xs text-gray-600">Premium ingredients</p>
            </div>
            <div className="text-center">
              <RotateCcw className="w-8 h-8 text-purple-600 mx-auto mb-2" />
              <p className="text-sm font-medium">Easy Returns</p>
              <p className="text-xs text-gray-600">30-day policy</p>
            </div>
          </div>
        </div>
      </div>

      {/* Product Tabs */}
      <div className="bg-white rounded-lg shadow-sm mb-12">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8 px-6">
            {['description', 'ingredients', 'reviews'].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`py-4 px-1 border-b-2 font-medium text-sm capitalize transition-colors ${
                  activeTab === tab
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                {tab}
              </button>
            ))}
          </nav>
        </div>

        <div className="p-6">
          {activeTab === 'description' && (
            <div>
              <h3 className="text-lg font-semibold mb-3">Product Description</h3>
              <p className="text-gray-700 mb-4">{product.description}</p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-medium mb-2">Product Details</h4>
                  <ul className="text-gray-600 space-y-1">
                    <li><strong>Weight:</strong> {product.weight}</li>
                    <li><strong>Category:</strong> {product.category}</li>
                    <li><strong>Rating:</strong> {product.rating}/5 stars</li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-medium mb-2">Key Benefits</h4>
                  <ul className="text-gray-600 space-y-1">
                    <li>• High-quality nutrition</li>
                    <li>• Carefully selected ingredients</li>
                    <li>• Supports overall health</li>
                    <li>• Great taste dogs love</li>
                  </ul>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'ingredients' && (
            <div>
              <h3 className="text-lg font-semibold mb-3">Ingredients</h3>
              <div className="flex flex-wrap gap-2">
                {product.ingredients.map((ingredient, index) => (
                  <span
                    key={index}
                    className="bg-gray-100 px-3 py-1 rounded-full text-sm text-gray-700"
                  >
                    {ingredient}
                  </span>
                ))}
              </div>
              <p className="text-gray-600 mt-4">
                All ingredients are carefully sourced and meet our high-quality standards for pet nutrition.
              </p>
            </div>
          )}

          {activeTab === 'reviews' && (
            <div>
              <h3 className="text-lg font-semibold mb-3">Customer Reviews</h3>
              <div className="space-y-4">
                <div className="flex items-center gap-4 mb-6">
                  <div className="text-3xl font-bold">{product.rating}</div>
                  <div>
                    <div className="flex items-center mb-1">
                      {[...Array(5)].map((_, i) => (
                        <Star
                          key={i}
                          className={`w-5 h-5 ${i < Math.floor(product.rating) ? 'fill-yellow-400 text-yellow-400' : 'text-gray-300'}`}
                        />
                      ))}
                    </div>
                    <p className="text-gray-600">{product.reviews} reviews</p>
                  </div>
                </div>

                {/* Sample Reviews */}
                <div className="space-y-4">
                  <div className="border-b border-gray-200 pb-4">
                    <div className="flex items-center gap-2 mb-2">
                      <div className="flex items-center">
                        {[...Array(5)].map((_, i) => (
                          <Star key={i} className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                        ))}
                      </div>
                      <span className="font-medium">Amazing quality!</span>
                      <span className="text-gray-500 text-sm">- Sarah K.</span>
                    </div>
                    <p className="text-gray-700">
                      My dog absolutely loves this food. Great ingredients and you can really see the difference in his energy levels.
                    </p>
                  </div>

                  <div className="border-b border-gray-200 pb-4">
                    <div className="flex items-center gap-2 mb-2">
                      <div className="flex items-center">
                        {[...Array(4)].map((_, i) => (
                          <Star key={i} className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                        ))}
                        <Star className="w-4 h-4 text-gray-300" />
                      </div>
                      <span className="font-medium">Very satisfied</span>
                      <span className="text-gray-500 text-sm">- Mike R.</span>
                    </div>
                    <p className="text-gray-700">
                      Fast delivery and great packaging. My picky eater actually finished her bowl!
                    </p>
                  </div>

                  <div>
                    <div className="flex items-center gap-2 mb-2">
                      <div className="flex items-center">
                        {[...Array(5)].map((_, i) => (
                          <Star key={i} className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                        ))}
                      </div>
                      <span className="font-medium">Highly recommend</span>
                      <span className="text-gray-500 text-sm">- Jennifer L.</span>
                    </div>
                    <p className="text-gray-700">
                      Excellent value for money. Will definitely be ordering again.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Related Products */}
      {relatedProducts.length > 0 && (
        <div>
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Related Products</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {relatedProducts.map(relatedProduct => (
              <ProductCard key={relatedProduct.id} product={relatedProduct} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default ProductDetail;