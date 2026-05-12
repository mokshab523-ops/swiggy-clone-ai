from database.db import Database
from bson.objectid import ObjectId
from datetime import datetime

class Restaurant:
    """Restaurant Model"""
    
    collection = Database.get_collection('restaurants')
    
    @staticmethod
    def create(restaurant_data):
        """Create new restaurant"""
        restaurant = {
            'owner_id': ObjectId(restaurant_data['owner_id']),
            'name': restaurant_data['name'],
            'description': restaurant_data.get('description', ''),
            'category': restaurant_data.get('category', 'Multi-Cuisine'),
            'cuisine_types': restaurant_data.get('cuisine_types', []),
            'image': restaurant_data.get('image'),
            'logo': restaurant_data.get('logo'),
            'rating': 4.5,
            'reviews_count': 0,
            'latitude': restaurant_data['latitude'],
            'longitude': restaurant_data['longitude'],
            'address': restaurant_data['address'],
            'phone': restaurant_data['phone'],
            'email': restaurant_data['email'],
            'opening_time': restaurant_data.get('opening_time', '10:00'),
            'closing_time': restaurant_data.get('closing_time', '23:00'),
            'is_open': True,
            'is_active': True,
            'delivery_time': restaurant_data.get('delivery_time', 30),
            'min_order_value': restaurant_data.get('min_order_value', 100),
            'delivery_charge': restaurant_data.get('delivery_charge', 50),
            'discount': restaurant_data.get('discount', 0),
            'offers': restaurant_data.get('offers', []),
            'menu_items': [],
            'popular_items': [],
            'total_orders': 0,
            'revenue': 0,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'bank_account': restaurant_data.get('bank_account'),
            'verification_status': 'pending',
            'documents': restaurant_data.get('documents', [])
        }
        
        result = Restaurant.collection.insert_one(restaurant)
        return {
            'success': True,
            'restaurant_id': str(result.inserted_id)
        }
    
    @staticmethod
    def find_by_id(restaurant_id):
        """Find restaurant by ID"""
        try:
            restaurant = Restaurant.collection.find_one({'_id': ObjectId(restaurant_id)})
            if restaurant:
                Restaurant._format_restaurant(restaurant)
            return restaurant
        except:
            return None
    
    @staticmethod
    def find_by_owner(owner_id):
        """Find restaurants by owner ID"""
        restaurants = list(Restaurant.collection.find({'owner_id': ObjectId(owner_id)}))
        for restaurant in restaurants:
            Restaurant._format_restaurant(restaurant)
        return restaurants
    
    @staticmethod
    def get_nearby_restaurants(latitude, longitude, radius=5):
        """Get restaurants near a location using geospatial query"""
        # Simple distance calculation (in production, use actual geospatial indexes)
        restaurants = list(Restaurant.collection.find({
            'is_active': True,
            'is_open': True
        }))
        
        nearby = []
        for restaurant in restaurants:
            # Calculate approximate distance
            distance = ((restaurant['latitude'] - latitude)**2 + 
                       (restaurant['longitude'] - longitude)**2)**0.5
            
            if distance <= radius * 0.01:  # Rough approximation
                restaurant['distance'] = round(distance * 111, 2)  # km
                nearby.append(restaurant)
        
        return sorted(nearby, key=lambda x: x['distance'])
    
    @staticmethod
    def get_all_restaurants(page=1, per_page=10):
        """Get all active restaurants with pagination"""
        skip = (page - 1) * per_page
        restaurants = list(Restaurant.collection.find(
            {'is_active': True}
        ).skip(skip).limit(per_page))
        
        for restaurant in restaurants:
            Restaurant._format_restaurant(restaurant)
        
        return restaurants
    
    @staticmethod
    def search_restaurants(query):
        """Search restaurants by name or cuisine"""
        restaurants = list(Restaurant.collection.find({
            '$or': [
                {'name': {'$regex': query, '$options': 'i'}},
                {'cuisine_types': {'$regex': query, '$options': 'i'}},
                {'category': {'$regex': query, '$options': 'i'}}
            ],
            'is_active': True
        }))
        
        for restaurant in restaurants:
            Restaurant._format_restaurant(restaurant)
        
        return restaurants
    
    @staticmethod
    def get_by_category(category):
        """Get restaurants by category"""
        restaurants = list(Restaurant.collection.find({
            'category': category,
            'is_active': True
        }))
        
        for restaurant in restaurants:
            Restaurant._format_restaurant(restaurant)
        
        return restaurants
    
    @staticmethod
    def add_menu_item(restaurant_id, item):
        """Add menu item to restaurant"""
        item['_id'] = ObjectId()
        item['created_at'] = datetime.utcnow()
        
        Restaurant.collection.update_one(
            {'_id': ObjectId(restaurant_id)},
            {'$push': {'menu_items': item}}
        )
        
        return str(item['_id'])
    
    @staticmethod
    def update_rating(restaurant_id, new_rating, review_count):
        """Update restaurant rating"""
        Restaurant.collection.update_one(
            {'_id': ObjectId(restaurant_id)},
            {'$set': {
                'rating': new_rating,
                'reviews_count': review_count
            }}
        )
    
    @staticmethod
    def update_total_orders_and_revenue(restaurant_id, amount):
        """Update total orders and revenue"""
        Restaurant.collection.update_one(
            {'_id': ObjectId(restaurant_id)},
            {'$inc': {
                'total_orders': 1,
                'revenue': amount
            }}
        )
    
    @staticmethod
    def add_offer(restaurant_id, offer):
        """Add special offer to restaurant"""
        offer['_id'] = ObjectId()
        offer['created_at'] = datetime.utcnow()
        
        Restaurant.collection.update_one(
            {'_id': ObjectId(restaurant_id)},
            {'$push': {'offers': offer}}
        )
    
    @staticmethod
    def toggle_restaurant_status(restaurant_id, is_open):
        """Toggle restaurant open/closed status"""
        Restaurant.collection.update_one(
            {'_id': ObjectId(restaurant_id)},
            {'$set': {'is_open': is_open}}
        )
    
    @staticmethod
    def _format_restaurant(restaurant):
        """Format restaurant for response"""
        restaurant['_id'] = str(restaurant['_id'])
        restaurant['owner_id'] = str(restaurant['owner_id'])
        return restaurant