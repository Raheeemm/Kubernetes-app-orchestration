import os
import sqlite3
import random
import string
from flask import Flask, render_template, request, redirect, jsonify, abort, url_for
import validators

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-for-url-shortener')
DATABASE_PATH = os.getenv("DATABASE_PATH","database.db")
DATABASE = os.path.join(os.path.abspath(os.path.dirname(__file__)),DATABASE_PATH)

SHORT_CODE_LENGTH = int(os.getenv("SHORT_CODE_LENGTH","6"))

def get_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db

def init_db():
    # We always check if the tables exist, or if database.db file is missing.
    # To be safe, let's inspect the sqlite_master for table presence.
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='urls';")
    if not cursor.fetchone():
        schema_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'schema.sql')
        with open(schema_path, 'r') as f:
            cursor.executescript(f.read())
        db.commit()
    db.close()

# Initialize DB at startup
init_db()

def generate_short_code(length=SHORT_CODE_LENGTH):
    characters = string.ascii_letters + string.digits
    while True:
        code = ''.join(random.choices(characters, k=length))
        # Verify uniqueness
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT 1 FROM urls WHERE short_code = ?', (code,))
        exists = cursor.fetchone()
        db.close()
        if not exists:
            return code

def format_url(url):
    url = url.strip()
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    return url

@app.route('/')
def index():
    db = get_db()
    cursor = db.cursor()
    # Fetch recent URLs with click counts
    query = """
        SELECT u.id, u.original_url, u.short_code, u.created_at, COUNT(c.id) as click_count
        FROM urls u
        LEFT JOIN clicks c ON u.id = c.url_id
        GROUP BY u.id
        ORDER BY u.created_at DESC
        LIMIT 10
    """
    cursor.execute(query)
    recent_urls = cursor.fetchall()
    db.close()
    return render_template('index.html', recent_urls=recent_urls)

@app.route('/shorten', methods=['POST'])
def shorten():
    original_url = request.form.get('url', '').strip()
    custom_code = request.form.get('custom_code', '').strip()

    if not original_url:
        return jsonify({'success': False, 'message': 'URL is required.'}), 400

    formatted_url = format_url(original_url)

    # Validate URL
    if not validators.url(formatted_url):
        return jsonify({'success': False, 'message': 'Please enter a valid URL.'}), 400

    db = get_db()
    cursor = db.cursor()

    # If custom code is provided
    if custom_code:
        # Check custom code format (alphanumeric and dashes only)
        if not all(c.isalnum() or c in '-_' for c in custom_code):
            db.close()
            return jsonify({'success': False, 'message': 'Custom alias can only contain letters, numbers, dashes, and underscores.'}), 400
        
        if len(custom_code) < 3 or len(custom_code) > 15:
            db.close()
            return jsonify({'success': False, 'message': 'Custom alias must be between 3 and 15 characters.'}), 400

        # Check if custom code already exists
        cursor.execute('SELECT 1 FROM urls WHERE short_code = ?', (custom_code,))
        if cursor.fetchone():
            db.close()
            return jsonify({'success': False, 'message': 'Custom alias is already taken.'}), 400
        
        short_code = custom_code
    else:
        # Check if this URL was already shortened (and didn't use a custom code)
        cursor.execute('SELECT short_code FROM urls WHERE original_url = ? LIMIT 1', (formatted_url,))
        existing = cursor.fetchone()
        if existing:
            short_code = existing['short_code']
            db.close()
            short_url = request.host_url + short_code
            return jsonify({
                'success': True,
                'short_code': short_code,
                'short_url': short_url,
                'original_url': formatted_url,
                'is_existing': True
            })
        
        short_code = generate_short_code()

    # Insert new URL
    cursor.execute('INSERT INTO urls (original_url, short_code) VALUES (?, ?)', (formatted_url, short_code))
    db.commit()
    db.close()

    short_url = request.host_url + short_code
    return jsonify({
        'success': True,
        'short_code': short_code,
        'short_url': short_url,
        'original_url': formatted_url,
        'is_existing': False
    })

def parse_user_agent(ua_string):
    if not ua_string:
        return 'Unknown', 'Unknown'
    
    ua_lower = ua_string.lower()
    
    # Platform / OS detection
    if 'windows' in ua_lower:
        platform = 'Windows'
    elif 'ipad' in ua_lower:
        platform = 'iPad'
    elif 'iphone' in ua_lower:
        platform = 'iPhone'
    elif 'android' in ua_lower:
        platform = 'Android'
    elif 'macintosh' in ua_lower or 'mac os x' in ua_lower:
        platform = 'macOS'
    elif 'linux' in ua_lower:
        platform = 'Linux'
    else:
        platform = 'Unknown'
        
    # Browser detection
    if 'edg/' in ua_lower or 'edge' in ua_lower:
        browser = 'Edge'
    elif 'opera' in ua_lower or 'opr/' in ua_lower:
        browser = 'Opera'
    elif 'chrome' in ua_lower:
        # Chrome strings often contain Safari, so check Chrome first
        browser = 'Chrome'
    elif 'safari' in ua_lower:
        browser = 'Safari'
    elif 'firefox' in ua_lower:
        browser = 'Firefox'
    else:
        browser = 'Unknown'
        
    return browser, platform

@app.route('/<short_code>')
def redirect_to_url(short_code):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT id, original_url FROM urls WHERE short_code = ?', (short_code,))
    row = cursor.fetchone()
    
    if not row:
        db.close()
        abort(404)
        
    url_id = row['id']
    original_url = row['original_url']

    # Record click analytics
    ua_string = request.headers.get('User-Agent', '')
    browser, platform = parse_user_agent(ua_string)
    
    # Get referrer domain
    referrer_url = request.referrer
    referrer = 'Direct'
    if referrer_url:
        from urllib.parse import urlparse
        parsed_uri = urlparse(referrer_url)
        referrer = parsed_uri.netloc if parsed_uri.netloc else 'Unknown'

    cursor.execute(
        'INSERT INTO clicks (url_id, referrer, browser, platform) VALUES (?, ?, ?, ?)',
        (url_id, referrer, browser, platform)
    )
    db.commit()
    db.close()

    return redirect(original_url)

@app.route('/health')
def health():
    return {"status":"healthy"}, 200


@app.route('/analytics/<short_code>')
def analytics(short_code):
    db = get_db()
    cursor = db.cursor()
    
    # Get original url details
    cursor.execute('SELECT id, original_url, short_code, created_at FROM urls WHERE short_code = ?', (short_code,))
    url_details = cursor.fetchone()
    
    if not url_details:
        db.close()
        abort(404)
        
    url_id = url_details['id']

    # Total clicks
    cursor.execute('SELECT COUNT(*) as total FROM clicks WHERE url_id = ?', (url_id,))
    total_clicks = cursor.fetchone()['total']

    # Clicks by browser
    cursor.execute(
        'SELECT browser, COUNT(*) as count FROM clicks WHERE url_id = ? GROUP BY browser ORDER BY count DESC',
        (url_id,)
    )
    browsers_data = cursor.fetchall()

    # Clicks by platform
    cursor.execute(
        'SELECT platform, COUNT(*) as count FROM clicks WHERE url_id = ? GROUP BY platform ORDER BY count DESC',
        (url_id,)
    )
    platforms_data = cursor.fetchall()

    # Clicks by referrer
    cursor.execute(
        'SELECT referrer, COUNT(*) as count FROM clicks WHERE url_id = ? GROUP BY referrer ORDER BY count DESC',
        (url_id,)
    )
    referrers_data = cursor.fetchall()

    # Recent clicks history (last 10)
    cursor.execute(
        'SELECT clicked_at, referrer, browser, platform FROM clicks WHERE url_id = ? ORDER BY clicked_at DESC LIMIT 10',
        (url_id,)
    )
    clicks_history = cursor.fetchall()

    db.close()

    return render_template(
        'analytics.html',
        url=url_details,
        total_clicks=total_clicks,
        browsers=browsers_data,
        platforms=platforms_data,
        referrers=referrers_data,
        history=clicks_history
    )

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
