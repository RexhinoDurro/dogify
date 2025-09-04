import type { Product } from '../contexts/CartContext';

export const products: Product[] = [
  {
    id: 1,
    name: "Premium Grain-Free Adult Dog Food",
    price: 49.99,
    originalPrice: 59.99,
    image: "https://images.unsplash.com/photo-1589941013453-ec89f33b5e95?w=400&h=400&fit=crop&crop=center",
    rating: 4.8,
    reviews: 234,
    description: "High-quality, grain-free nutrition for adult dogs with real chicken as the first ingredient. Perfect for dogs with sensitive stomachs.",
    category: "Dry Food",
    weight: "15 lbs",
    ingredients: ["Chicken", "Sweet Potato", "Peas", "Chicken Fat", "Natural Flavors", "Vitamins", "Minerals"],
    inStock: true
  },
  {
    id: 2,
    name: "Puppy Training Treats",
    price: 12.99,
    image: "https://images.unsplash.com/photo-1605568427561-40dd23c2acea?w=400&h=400&fit=crop&crop=center",
    rating: 4.9,
    reviews: 156,
    description: "Small, soft training treats perfect for puppies and small dogs. Made with real beef and easy to digest ingredients.",
    category: "Treats",
    weight: "6 oz",
    ingredients: ["Beef", "Rice Flour", "Glycerin", "Natural Flavors", "Vitamins"],
    inStock: true
  },
  {
    id: 3,
    name: "Senior Dog Wellness Formula",
    price: 44.99,
    image: "https://images.unsplash.com/photo-1583337130417-3346a1be7dee?w=400&h=400&fit=crop&crop=center",
    rating: 4.7,
    reviews: 89,
    description: "Specially formulated for senior dogs with joint support and easy digestion. Contains glucosamine and chondroitin for healthy joints.",
    category: "Dry Food",
    weight: "12 lbs",
    ingredients: ["Lamb", "Brown Rice", "Glucosamine", "Chondroitin", "Omega-3", "Antioxidants"],
    inStock: true
  },
  {
    id: 4,
    name: "Organic Wet Food Variety Pack",
    price: 32.99,
    originalPrice: 39.99,
    image: "https://images.unsplash.com/photo-1581888227599-779811939961?w=400&h=400&fit=crop&crop=center",
    rating: 4.6,
    reviews: 67,
    description: "12-pack of organic wet food with chicken, beef, and lamb flavors. Made with premium organic ingredients.",
    category: "Wet Food",
    weight: "12 x 12.5 oz",
    ingredients: ["Organic Chicken", "Organic Beef", "Organic Lamb", "Carrots", "Spinach", "Organic Broth"],
    inStock: false
  },
  {
    id: 5,
    name: "Dental Health Chews",
    price: 18.99,
    image: "https://images.unsplash.com/photo-1601758228041-f3b2795255f1?w=400&h=400&fit=crop&crop=center",
    rating: 4.5,
    reviews: 203,
    description: "Daily dental chews that help reduce tartar and freshen breath. Veterinarian recommended for oral health.",
    category: "Treats",
    weight: "30 count",
    ingredients: ["Wheat Protein", "Rice Starch", "Glycerin", "Natural Mint", "Calcium"],
    inStock: true
  },
  {
    id: 6,
    name: "High-Protein Active Dog Formula",
    price: 54.99,
    image: "https://images.unsplash.com/photo-1587300003388-59208cc962cb?w=400&h=400&fit=crop&crop=center",
    rating: 4.9,
    reviews: 145,
    description: "High-protein formula for active and working dogs with real salmon. Provides sustained energy for active lifestyles.",
    category: "Dry Food",
    weight: "18 lbs",
    ingredients: ["Salmon", "Turkey Meal", "Sweet Potato", "Pea Protein", "Fish Oil", "Probiotics"],
    inStock: true
  },
  {
    id: 7,
    name: "Small Breed Adult Formula",
    price: 38.99,
    image: "https://images.unsplash.com/photo-1552053831-71594a27632d?w=400&h=400&fit=crop&crop=center",
    rating: 4.7,
    reviews: 112,
    description: "Specially sized kibble for small breed dogs with balanced nutrition. Perfect bite size for little mouths.",
    category: "Dry Food",
    weight: "10 lbs",
    ingredients: ["Chicken", "Rice", "Corn", "Chicken Fat", "Natural Flavors", "Vitamins"],
    inStock: true
  },
  {
    id: 8,
    name: "Freeze-Dried Raw Treats",
    price: 24.99,
    originalPrice: 29.99,
    image: "https://images.unsplash.com/photo-1601758125946-6ec2ef64daf8?w=400&h=400&fit=crop&crop=center",
    rating: 4.8,
    reviews: 78,
    description: "Premium freeze-dried raw beef liver treats. Single ingredient, high-value training rewards.",
    category: "Treats",
    weight: "4 oz",
    ingredients: ["Beef Liver"],
    inStock: true
  },
  {
    id: 9,
    name: "Grain-Free Wet Food - Chicken",
    price: 28.99,
    image: "https://images.unsplash.com/photo-1583337130417-3346a1be7dee?w=400&h=400&fit=crop&crop=center",
    rating: 4.6,
    reviews: 95,
    description: "Grain-free wet food with real chicken and vegetables. Perfect for dogs with food sensitivities.",
    category: "Wet Food",
    weight: "12 x 13 oz",
    ingredients: ["Chicken", "Sweet Potato", "Carrots", "Peas", "Chicken Broth", "Vitamins"],
    inStock: true
  },
  {
    id: 10,
    name: "Joint Support Supplements",
    price: 34.99,
    image: "https://images.unsplash.com/photo-1584464491033-06628f3a6b7b?w=400&h=400&fit=crop&crop=center",
    rating: 4.4,
    reviews: 67,
    description: "Daily joint support supplements with glucosamine and chondroitin. Helps maintain healthy joints and mobility.",
    category: "Supplements",
    weight: "60 tablets",
    ingredients: ["Glucosamine", "Chondroitin", "MSM", "Turmeric", "Green-Lipped Mussel"],
    inStock: true
  }
];

export const getProductById = (id: number): Product | undefined => {
  return products.find(product => product.id === id);
};

export const getProductsByCategory = (category: string): Product[] => {
  if (category === 'All') return products;
  return products.filter(product => product.category === category);
};

export const searchProducts = (searchTerm: string): Product[] => {
  const term = searchTerm.toLowerCase();
  return products.filter(product =>
    product.name.toLowerCase().includes(term) ||
    product.description.toLowerCase().includes(term) ||
    product.category.toLowerCase().includes(term) ||
    product.ingredients.some(ingredient => ingredient.toLowerCase().includes(term))
  );
};

export const categories = ['All', 'Dry Food', 'Wet Food', 'Treats', 'Supplements'];