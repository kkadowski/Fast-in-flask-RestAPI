from flask import Blueprint, request, jsonify
import validators
import src.constants.http_status_codes as cds
from src.database import Bookmark, db
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended.view_decorators import jwt_required

bookmarks = Blueprint("bookmarks", __name__, url_prefix="/api/v1/bookmarks")

@bookmarks.route('/', methods=['POST', 'GET'])
@jwt_required()
def handle_bookmarks():
    current_user = get_jwt_identity()
    if request.method == 'POST':
        body = request.get_json().get('body', '')
        url = request.get_json().get('url', '')
        
        if not validators.url(url):
            return jsonify({
                'error':'Enter a valid url'
            }), cds.HTTP_400_BAD_REQUEST
            
        if Bookmark.query.filter_by(url=url).first():
            return jsonify({
                'error':'URL already exists.'
            }), cds.HTTP_409_CONFLICT
            
        bookmark = Bookmark(url=url, body = body, user_id=current_user)
        db.session.add(bookmark)
        db.session.commit()
        
        return jsonify({
            'id': bookmark.id,
            'url': bookmark.url,
            'short_url': bookmark.short_url,
            'visit':bookmark.visits,
            'body':bookmark.body,
            'createed_at':bookmark.created_at,
            'updated_at':bookmark.updated_at
        }), cds.HTTP_201_CREATED
        
    else:
        page = request.args.get('page', 1, type = int)
        per_page = request.args.get('page', 5, type=int)
        
        bookmarks = Bookmark.query.filter_by(user_id = current_user).paginate(page=page, per_page = per_page)
        
        data = []
        
        for bookmark  in bookmarks.items:
            data.append({
                'id': bookmark.id,
                'url': bookmark.url,
                'short_url': bookmark.short_url,
                'visit':bookmark.visits,
                'body':bookmark.body,
                'createed_at':bookmark.created_at,
                'updated_at':bookmark.updated_at
            })
            
        meta = {
            "page" : bookmarks.page,
            'pages' : bookmarks.pages,
            'total_count' : bookmarks.total,
            'prev' : bookmarks.prev_num,
            'next' : bookmarks.next_num,
            'has_next' : bookmarks.has_next,
            'has_prev' : bookmarks.has_prev
            
        }
        
        return jsonify({
            'data' : data,
            'meta' : meta
        }), cds.HTTP_200_OK
        
        
          
@bookmarks.get("/<int:id>")
@jwt_required()
def get_bookmark(id):
    current_user = get_jwt_identity()
    
    bookmark = Bookmark.query.filter_by(user_id=current_user, id = id).first()
    
    if not bookmark:
        return jsonify({
            "message": "Item not fount."
        }), cds.HTTP_404_NOT_FOUND
        
    return jsonify({
        'id': bookmark.id,
        'url': bookmark.url,
        'short_url': bookmark.short_url,
        'visit':bookmark.visits,
        'body':bookmark.body,
        'createed_at':bookmark.created_at,
        'updated_at':bookmark.updated_at
            
    }), cds.HTTP_200_OK
    

@bookmarks.put('/<int:id>')
@bookmarks.patch('/<int:id>')
@jwt_required()
def edit_bookmark(id):
    current_user = get_jwt_identity()
    
    bookmark = Bookmark.query.filter_by(user_id=current_user, id = id).first()
    
    if not bookmark:
        return jsonify({
            "message": "Item not found."
        }), cds.HTTP_404_NOT_FOUND
        
    body = request.get_json().get('body', '')
    url = request.get_json().get('url', '')
        
    if not validators.url(url):
        return jsonify({
            'error':'Enter a valid url'
        }), cds.HTTP_400_BAD_REQUEST    
    
    bookmark.url = url
    bookmark.body = body
    db.session.commit()
    
    return jsonify({
        'id': bookmark.id,
        'url': bookmark.url,
        'short_url': bookmark.short_url,
        'visit': bookmark.visits,
        'body': bookmark.body,
        'created_at': bookmark.created_at,
        'updated_at': bookmark.updated_at,
    }), cds.HTTP_200_OK
    
@bookmarks.delete('/<int:id>')
@jwt_required()
def delete_bookmark(id):
    current_user = get_jwt_identity()
    
    bookmark = Bookmark.query.filter_by(user_id=current_user, id = id).first()
    
    if not bookmark:
        return jsonify({
            "message": "Item not found."
        }), cds.HTTP_404_NOT_FOUND
    
    db.session.delete(bookmark)
    db.session.commit()
    
    return jsonify({
        "message": "Bookmark has been deleted."
    }), cds.HTTP_204_NO_CONTENT
    
    
    