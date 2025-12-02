from flask import Flask, request, jsonify
from flask_cors import CORS
import re
from datetime import datetime
import hashlib

app = Flask(__name__)
CORS(app)

class EmailClassifier:
    def __init__(self):
        self.spam_keywords = {
            'winner', 'congratulations', 'claim', 'prize', 'free', 'urgent',
            'act now', 'limited time', 'click here', 'verify account', 'suspended',
            'confirm identity', 'nigerian prince', 'inheritance', 'lottery'
        }
        
        self.promotional_keywords = {
            'sale', 'discount', 'offer', 'deal', 'coupon', 'save', 'shop',
            'buy', 'order', 'purchase', 'unsubscribe', 'newsletter', 'promotion'
        }
        
        self.important_keywords = {
            'invoice', 'payment', 'urgent', 'deadline', 'meeting', 'interview',
            'contract', 'agreement', 'legal', 'tax', 'bank', 'security alert'
        }
        
        self.social_keywords = {
            'liked', 'commented', 'shared', 'followed', 'tagged', 'mentioned',
            'friend request', 'connection', 'notification', 'activity'
        }
    
    def extract_features(self, email_data):
        """Extract features from email"""
        subject = email_data.get('subject', '').lower()
        body = email_data.get('body', '').lower()
        sender = email_data.get('sender', '').lower()
        
        combined_text = f"{subject} {body}"
        
        # Count keywords
        spam_count = sum(1 for word in self.spam_keywords if word in combined_text)
        promo_count = sum(1 for word in self.promotional_keywords if word in combined_text)
        important_count = sum(1 for word in self.important_keywords if word in combined_text)
        social_count = sum(1 for word in self.social_keywords if word in combined_text)
        
        # Check for suspicious patterns
        has_multiple_links = len(re.findall(r'http[s]?://', body)) > 3
        has_all_caps = len(re.findall(r'\b[A-Z]{4,}\b', email_data.get('subject', ''))) > 0
        has_excessive_punctuation = len(re.findall(r'[!?]{2,}', subject)) > 0
        
        return {
            'spam_score': spam_count,
            'promo_score': promo_count,
            'important_score': important_count,
            'social_score': social_count,
            'has_multiple_links': has_multiple_links,
            'has_all_caps': has_all_caps,
            'has_excessive_punctuation': has_excessive_punctuation,
            'sender': sender
        }
    
    def calculate_priority(self, category, features):
        """Calculate email priority (1-10)"""
        base_priority = {
            'important': 9,
            'spam': 1,
            'promotional': 3,
            'social': 5,
            'general': 6
        }
        
        priority = base_priority.get(category, 5)
        
        # Adjust based on features
        if features['important_score'] > 2:
            priority = min(priority + 2, 10)
        if features['has_all_caps'] or features['has_excessive_punctuation']:
            priority = max(priority - 1, 1)
        
        return priority
    
    def classify(self, email_data):
        """Classify email into categories"""
        if not email_data or 'subject' not in email_data:
            return {'error': 'Missing required fields (subject)'}
        
        features = self.extract_features(email_data)
        
        # Determine category based on scores
        scores = {
            'spam': features['spam_score'] * 2 + (3 if features['has_multiple_links'] else 0),
            'promotional': features['promo_score'],
            'important': features['important_score'],
            'social': features['social_score']
        }
        
        # Get primary category
        if scores['spam'] > 3:
            category = 'spam'
            confidence = min(scores['spam'] * 10, 95)
        elif scores['important'] > 1:
            category = 'important'
            confidence = min(scores['important'] * 15, 90)
        elif scores['social'] > 1:
            category = 'social'
            confidence = min(scores['social'] * 12, 85)
        elif scores['promotional'] > 1:
            category = 'promotional'
            confidence = min(scores['promotional'] * 10, 80)
        else:
            category = 'general'
            confidence = 60
        
        priority = self.calculate_priority(category, features)
        
        # Generate email ID
        email_id = hashlib.md5(
            f"{email_data.get('sender', '')}{email_data.get('subject', '')}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:12]
        
        return {
            'email_id': email_id,
            'category': category,
            'confidence': round(confidence, 2),
            'priority': priority,
            'scores': scores,
            'features': {
                'has_multiple_links': features['has_multiple_links'],
                'has_all_caps': features['has_all_caps'],
                'suspicious_patterns': features['has_excessive_punctuation']
            },
            'recommendation': self.get_recommendation(category, priority),
            'timestamp': datetime.now().isoformat()
        }
    
    def get_recommendation(self, category, priority):
        """Get action recommendation"""
        if category == 'spam':
            return 'Move to spam folder'
        elif category == 'important' and priority >= 8:
            return 'Flag for immediate attention'
        elif category == 'promotional':
            return 'Move to promotions folder'
        elif category == 'social':
            return 'Move to social folder'
        else:
            return 'Keep in inbox'

classifier = EmailClassifier()

@app.route('/')
def home():
    return jsonify({
        'service': 'Smart Email Classifier API',
        'version': '1.0.0',
        'endpoints': {
            '/classify': 'POST - Classify email',
            '/batch-classify': 'POST - Classify multiple emails',
            '/health': 'GET - Health check'
        }
    })

@app.route('/classify', methods=['POST'])
def classify_email():
    """Classify single email"""
    try:
        data = request.get_json()
        result = classifier.classify(data)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/batch-classify', methods=['POST'])
def batch_classify():
    """Classify multiple emails"""
    try:
        data = request.get_json()
        emails = data.get('emails', [])
        
        if not emails:
            return jsonify({'error': 'No emails provided'}), 400
        
        results = [classifier.classify(email) for email in emails]
        
        return jsonify({
            'total': len(results),
            'results': results,
            'summary': {
                'spam': sum(1 for r in results if r.get('category') == 'spam'),
                'important': sum(1 for r in results if r.get('category') == 'important'),
                'promotional': sum(1 for r in results if r.get('category') == 'promotional'),
                'social': sum(1 for r in results if r.get('category') == 'social'),
                'general': sum(1 for r in results if r.get('category') == 'general')
            }
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'service': 'email-classifier'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
