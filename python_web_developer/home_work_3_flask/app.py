from flask import Flask, request, jsonify
from flask_httpauth import HTTPBasicAuth
from models import db, User, Advertisement
from config import Config
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)

# Инициализация базы данных
db.init_app(app)

# Инициализация аутентификации
auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(email, password):
    user = User.query.filter_by(email=email).first()
    if user and user.check_password(password):
        return user

# Создание таблиц при запуске приложения
with app.app_context():
    db.create_all()

# Роуты для пользователей
@app.route('/api/users', methods=['POST'])
def create_user():
    """Создание нового пользователя"""
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password are required'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'User already exists'}), 400
    
    user = User(email=data['email'])
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify(user.to_dict()), 201

# Роуты для объявлений
@app.route('/api/advertisements', methods=['POST'])
@auth.login_required
def create_advertisement():
    """Создание нового объявления"""
    data = request.get_json()
    
    if not data or not data.get('title') or not data.get('description'):
        return jsonify({'error': 'Title and description are required'}), 400
    
    advertisement = Advertisement(
        title=data['title'],
        description=data['description'],
        owner_id=auth.current_user().id
    )
    
    db.session.add(advertisement)
    db.session.commit()
    
    return jsonify(advertisement.to_dict()), 201

@app.route('/api/advertisements/<int:ad_id>', methods=['GET'])
def get_advertisement(ad_id):
    """Получение объявления по ID"""
    advertisement = Advertisement.query.get_or_404(ad_id)
    return jsonify(advertisement.to_dict())

@app.route('/api/advertisements', methods=['GET'])
def get_all_advertisements():
    """Получение всех объявлений"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    advertisements = Advertisement.query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'advertisements': [ad.to_dict() for ad in advertisements.items],
        'total': advertisements.total,
        'pages': advertisements.pages,
        'current_page': page
    })

@app.route('/api/advertisements/<int:ad_id>', methods=['PUT'])
@auth.login_required
def update_advertisement(ad_id):
    """Обновление объявления"""
    advertisement = Advertisement.query.get_or_404(ad_id)
    
    # Проверяем, что пользователь является владельцем объявления
    if advertisement.owner_id != auth.current_user().id:
        return jsonify({'error': 'Permission denied'}), 403
    
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    if 'title' in data:
        advertisement.title = data['title']
    if 'description' in data:
        advertisement.description = data['description']
    
    advertisement.created_at = datetime.utcnow()  # Обновляем дату
    
    db.session.commit()
    
    return jsonify(advertisement.to_dict())

@app.route('/api/advertisements/<int:ad_id>', methods=['DELETE'])
@auth.login_required
def delete_advertisement(ad_id):
    """Удаление объявления"""
    advertisement = Advertisement.query.get_or_404(ad_id)
    
    # Проверяем, что пользователь является владельцем объявления
    if advertisement.owner_id != auth.current_user().id:
        return jsonify({'error': 'Permission denied'}), 403
    
    db.session.delete(advertisement)
    db.session.commit()
    
    return jsonify({'message': 'Advertisement deleted successfully'})

# Обработчики ошибок
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad request'}), 400

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True)