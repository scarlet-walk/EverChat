import os
import uuid
from flask import render_template, request, redirect, url_for, flash, jsonify, send_from_directory
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from app import app, db
from models import User, Post, Like, Comment, Message, AssistantConversation, OfflineMap, EmergencyContact, SOSAlert
import openai

# Initialize OpenAI client
openai.api_key = os.environ.get("OPENAI_API_KEY")

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template('index.html', posts=posts)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists')
            return redirect(url_for('register'))
        
        # Create new user
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        login_user(user)
        return redirect(url_for('index'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/create_post', methods=['POST'])
@login_required
def create_post():
    caption = request.form.get('caption', '')
    
    # Handle file upload
    file = request.files.get('image')
    filename = None
    
    if file and file.filename and allowed_file(file.filename):
        # Generate unique filename
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4().hex}.{file_extension}"
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    
    # Create new post
    post = Post(caption=caption, image_filename=filename, user_id=current_user.id)
    db.session.add(post)
    db.session.commit()
    
    flash('Post created successfully!')
    return redirect(url_for('index'))

@app.route('/like_post/<int:post_id>')
@login_required
def like_post(post_id):
    post = Post.query.get_or_404(post_id)
    existing_like = Like.query.filter_by(user_id=current_user.id, post_id=post_id).first()
    
    if existing_like:
        # Unlike the post
        db.session.delete(existing_like)
        action = 'unliked'
    else:
        # Like the post
        like = Like(user_id=current_user.id, post_id=post_id)
        db.session.add(like)
        action = 'liked'
    
    db.session.commit()
    
    return jsonify({
        'action': action,
        'like_count': post.like_count()
    })

@app.route('/add_comment/<int:post_id>', methods=['POST'])
@login_required
def add_comment(post_id):
    content = request.form.get('content')
    if content:
        comment = Comment(content=content, user_id=current_user.id, post_id=post_id)
        db.session.add(comment)
        db.session.commit()
    
    return redirect(url_for('index'))

@app.route('/profile/<username>')
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(user_id=user.id).order_by(Post.created_at.desc()).all()
    return render_template('profile.html', user=user, posts=posts)

@app.route('/chat')
@login_required
def chat():
    # Get all users for chat list
    users = User.query.filter(User.id != current_user.id).all()
    
    # Get recent conversations
    recent_messages = db.session.query(Message).filter(
        (Message.sender_id == current_user.id) | (Message.recipient_id == current_user.id)
    ).order_by(Message.created_at.desc()).limit(20).all()
    
    return render_template('chat.html', users=users, recent_messages=recent_messages)

@app.route('/send_message', methods=['POST'])
@login_required
def send_message():
    recipient_id = request.form.get('recipient_id')
    content = request.form.get('content')
    
    if recipient_id and content:
        message = Message(
            content=content,
            sender_id=current_user.id,
            recipient_id=int(recipient_id)
        )
        db.session.add(message)
        db.session.commit()
    
    return redirect(url_for('chat'))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/api/messages/<int:user_id>')
@login_required
def get_messages(user_id):
    messages = Message.query.filter(
        ((Message.sender_id == current_user.id) & (Message.recipient_id == user_id)) |
        ((Message.sender_id == user_id) & (Message.recipient_id == current_user.id))
    ).order_by(Message.created_at.asc()).all()
    
    # Mark messages as read
    Message.query.filter_by(sender_id=user_id, recipient_id=current_user.id, is_read=False).update({'is_read': True})
    db.session.commit()
    
    return jsonify([{
        'id': msg.id,
        'content': msg.content,
        'sender_id': msg.sender_id,
        'created_at': msg.created_at.isoformat(),
        'is_own': msg.sender_id == current_user.id
    } for msg in messages])

@app.route('/map')
@login_required
def map_view():
    return render_template('map.html')

@app.route('/assistant')
@login_required
def assistant():
    return render_template('assistant.html')

@app.route('/settings')
@login_required
def settings():
    return render_template('settings.html')

@app.route('/api/gpt-chat', methods=['POST'])
@login_required
def gpt_chat():
    try:
        data = request.get_json()
        message = data.get('message', '')
        mode = data.get('mode', 'general')
        
        # Define system prompts for different modes
        system_prompts = {
            'general': 'أنت مساعد ذكي مفيد وودود. تجيب باللغة العربية وتقدم إجابات واضحة ومفيدة.',
            'travel': 'أنت مساعد سفر متخصص. تساعد في التخطيط للرحلات والسياحة والطرق والفنادق. تجيب باللغة العربية.',
            'emergency': 'أنت مساعد طوارئ. تقدم مساعدة فورية وإرشادات واضحة للمواقف الطارئة. تجيب باللغة العربية وتؤكد على السلامة أولاً.'
        }
        
        system_prompt = system_prompts.get(mode, system_prompts['general'])
        
        # Create OpenAI chat completion
        from openai import OpenAI
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        ai_response = response.choices[0].message.content
        
        return jsonify({
            'success': True,
            'response': ai_response
        })
        
    except Exception as e:
        print(f"OpenAI API Error: {e}")
        # Fallback responses when API is unavailable
        fallback_responses = {
            'general': 'عذراً، المساعد الذكي غير متاح حالياً. يرجى المحاولة لاحقاً.',
            'travel': 'مساعد السفر غير متاح حالياً. يمكنك استخدام الوضع العام أو المحاولة لاحقاً.',
            'emergency': 'في حالات الطوارئ، اتصل مباشرة بالرقم 999 للحصول على المساعدة الفورية.'
        }
        
        return jsonify({
            'success': False,
            'response': fallback_responses.get(mode, fallback_responses['general'])
        })

@app.route('/api/process-gpt-command', methods=['POST'])
@login_required
def process_gpt_command():
    """Process @GPT commands in chat messages"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        
        # Check if message contains @GPT command
        if '@GPT' not in message.upper():
            return jsonify({'success': False, 'error': 'No @GPT command found'})
        
        # Extract the question after @GPT
        gpt_parts = message.upper().split('@GPT', 1)
        if len(gpt_parts) > 1:
            question = gpt_parts[1].strip()
        else:
            question = message
        
        # Use OpenAI to generate response
        from openai import OpenAI
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "أنت مساعد ذكي في تطبيق المحادثات. تجيب باختصار وبوضوح باللغة العربية."},
                {"role": "user", "content": question}
            ],
            max_tokens=300,
            temperature=0.7
        )
        
        ai_response = response.choices[0].message.content
        
        return jsonify({
            'success': True,
            'response': f"🤖 مساعد GPT: {ai_response}"
        })
        
    except Exception as e:
        print(f"OpenAI API Error: {e}")
        return jsonify({
            'success': False,
            'response': "🤖 مساعد GPT: عذراً، لا أستطيع الإجابة حالياً. يرجى المحاولة لاحقاً."
        })

@app.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    try:
        # Update user profile
        current_user.email = request.form.get('email', current_user.email)
        current_user.bio = request.form.get('bio', current_user.bio)
        
        # Handle profile picture upload
        file = request.files.get('profile_pic')
        if file and file.filename and allowed_file(file.filename):
            file_extension = file.filename.rsplit('.', 1)[1].lower()
            filename = f"profile_{current_user.id}_{uuid.uuid4().hex}.{file_extension}"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            current_user.profile_pic = filename
        
        db.session.commit()
        flash('تم تحديث الملف الشخصي بنجاح!')
        
    except Exception as e:
        print(f"Profile update error: {e}")
        flash('حدث خطأ أثناء تحديث الملف الشخصي')
    
    return redirect(url_for('settings'))

@app.route('/api/send-sos', methods=['POST'])
@login_required
def send_sos():
    try:
        data = request.get_json()
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        message = data.get('message', 'طلب مساعدة طارئة')
        
        # Create SOS alert
        sos_alert = SOSAlert(
            user_id=current_user.id,
            latitude=latitude,
            longitude=longitude,
            message=message
        )
        db.session.add(sos_alert)
        db.session.commit()
        
        # In a real app, this would broadcast to nearby devices
        # For now, we'll just log it
        print(f"SOS Alert from user {current_user.username} at {latitude}, {longitude}")
        
        return jsonify({
            'success': True,
            'message': 'تم إرسال إشارة SOS بنجاح'
        })
        
    except Exception as e:
        print(f"SOS Alert error: {e}")
        return jsonify({
            'success': False,
            'message': 'فشل في إرسال إشارة SOS'
        })
