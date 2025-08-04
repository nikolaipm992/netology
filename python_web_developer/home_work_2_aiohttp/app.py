from aiohttp import web
import json
import base64
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from database import engine, Base, get_db
from models import User, Advertisement
import asyncio

app = web.Application()

# Middleware для CORS
@web.middleware
async def cors_middleware(request, handler):
    response = await handler(request)
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response

app.middlewares.append(cors_middleware)

# Обработка OPTIONS запросов
async def handle_options(request):
    return web.Response(status=200)

# Аутентификация
async def authenticate(request):
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Basic '):
        raise web.HTTPUnauthorized(reason='Authentication required')
    
    try:
        encoded_credentials = auth_header.split(' ')[1]
        decoded_credentials = base64.b64decode(encoded_credentials).decode('utf-8')
        email, password = decoded_credentials.split(':', 1)
    except Exception:
        raise web.HTTPUnauthorized(reason='Invalid authentication credentials')
    
    async for db in get_db():
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        if user and user.check_password(password):
            return user
        break
    
    raise web.HTTPUnauthorized(reason='Invalid email or password')

# Роуты для пользователей
async def create_user(request):
    try:
        data = await request.json()
    except json.JSONDecodeError:
        return web.json_response({'error': 'Invalid JSON'}, status=400)
    
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return web.json_response({'error': 'Email and password are required'}, status=400)
    
    user = User(email=email)
    user.set_password(password)
    
    async for db in get_db():
        try:
            db.add(user)
            await db.commit()
            await db.refresh(user)
            break
        except IntegrityError:
            await db.rollback()
            return web.json_response({'error': 'User already exists'}, status=400)
        except Exception as e:
            await db.rollback()
            return web.json_response({'error': 'Internal server error'}, status=500)
    
    return web.json_response(user.to_dict(), status=201)

# Роуты для объявлений
async def create_advertisement(request):
    try:
        user = await authenticate(request)
    except web.HTTPException as e:
        return web.json_response({'error': e.reason}, status=e.status)
    
    try:
        data = await request.json()
    except json.JSONDecodeError:
        return web.json_response({'error': 'Invalid JSON'}, status=400)
    
    title = data.get('title')
    description = data.get('description')
    
    if not title or not description:
        return web.json_response({'error': 'Title and description are required'}, status=400)
    
    advertisement = Advertisement(
        title=title,
        description=description,
        owner_id=user.id
    )
    
    async for db in get_db():
        try:
            db.add(advertisement)
            await db.commit()
            await db.refresh(advertisement)
            break
        except Exception as e:
            await db.rollback()
            return web.json_response({'error': 'Internal server error'}, status=500)
    
    return web.json_response(advertisement.to_dict(), status=201)

async def get_advertisement(request):
    ad_id = int(request.match_info['ad_id'])
    
    async for db in get_db():
        try:
            result = await db.execute(select(Advertisement).where(Advertisement.id == ad_id))
            advertisement = result.scalar_one_or_none()
            if not advertisement:
                return web.json_response({'error': 'Advertisement not found'}, status=404)
            break
        except Exception as e:
            return web.json_response({'error': 'Internal server error'}, status=500)
    
    return web.json_response(advertisement.to_dict())

async def get_all_advertisements(request):
    page = int(request.query.get('page', 1))
    per_page = int(request.query.get('per_page', 10))
    
    async for db in get_db():
        try:
            offset = (page - 1) * per_page
            result = await db.execute(
                select(Advertisement).offset(offset).limit(per_page)
            )
            advertisements = result.scalars().all()
            
            # Получаем общее количество
            count_result = await db.execute(select(func.count(Advertisement.id)))
            total = count_result.scalar()
            
            break
        except Exception as e:
            return web.json_response({'error': 'Internal server error'}, status=500)
    
    return web.json_response({
        'advertisements': [ad.to_dict() for ad in advertisements],
        'total': total,
        'pages': (total + per_page - 1) // per_page,
        'current_page': page
    })

async def update_advertisement(request):
    try:
        user = await authenticate(request)
    except web.HTTPException as e:
        return web.json_response({'error': e.reason}, status=e.status)
    
    ad_id = int(request.match_info['ad_id'])
    
    async for db in get_db():
        try:
            result = await db.execute(
                select(Advertisement).where(Advertisement.id == ad_id)
            )
            advertisement = result.scalar_one_or_none()
            if not advertisement:
                return web.json_response({'error': 'Advertisement not found'}, status=404)
            
            # Проверяем права доступа
            if advertisement.owner_id != user.id:
                return web.json_response({'error': 'Permission denied'}, status=403)
            
            data = await request.json()
            if not data:
                return web.json_response({'error': 'No data provided'}, status=400)
            
            if 'title' in data:
                advertisement.title = data['title']
            if 'description' in data:
                advertisement.description = data['description']
            
            await db.commit()
            await db.refresh(advertisement)
            break
        except web.HTTPException:
            raise
        except Exception as e:
            await db.rollback()
            return web.json_response({'error': 'Internal server error'}, status=500)
    
    return web.json_response(advertisement.to_dict())

async def delete_advertisement(request):
    try:
        user = await authenticate(request)
    except web.HTTPException as e:
        return web.json_response({'error': e.reason}, status=e.status)
    
    ad_id = int(request.match_info['ad_id'])
    
    async for db in get_db():
        try:
            result = await db.execute(
                select(Advertisement).where(Advertisement.id == ad_id)
            )
            advertisement = result.scalar_one_or_none()
            if not advertisement:
                return web.json_response({'error': 'Advertisement not found'}, status=404)
            
            # Проверяем права доступа
            if advertisement.owner_id != user.id:
                return web.json_response({'error': 'Permission denied'}, status=403)
            
            await db.delete(advertisement)
            await db.commit()
            break
        except web.HTTPException:
            raise
        except Exception as e:
            await db.rollback()
            return web.json_response({'error': 'Internal server error'}, status=500)
    
    return web.json_response({'message': 'Advertisement deleted successfully'})

# Добавляем роуты
app.router.add_post('/api/users', create_user)
app.router.add_post('/api/advertisements', create_advertisement)
app.router.add_get('/api/advertisements/{ad_id:\d+}', get_advertisement)
app.router.add_get('/api/advertisements', get_all_advertisements)
app.router.add_put('/api/advertisements/{ad_id:\d+}', update_advertisement)
app.router.add_delete('/api/advertisements/{ad_id:\d+}', delete_advertisement)

# OPTIONS роуты для CORS
app.router.add_options('/api/users', handle_options)
app.router.add_options('/api/advertisements', handle_options)
app.router.add_options('/api/advertisements/{ad_id:\d+}', handle_options)

# Создание таблиц
async def init_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

if __name__ == '__main__':
    # Создаем таблицы
    asyncio.run(init_tables())
    
    # Запускаем сервер на другом порту
    web.run_app(app, host='localhost', port=8081)