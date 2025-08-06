# -*- coding: utf-8 -*-
import os
from flask import Flask, render_template, request, send_from_directory, flash, redirect, url_for
from werkzeug.utils import secure_filename
from steganographer import hide_message, extract_message

# 업로드 폴더 및 허용 확장자 설정
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = 'supersecretkey' # 실제 운영 환경에서는 강력한 키를 사용해야 합니다.
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

# 업로드 폴더가 없으면 생성
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    """파일 확장자가 허용되는지 확인합니다."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """메인 페이지를 렌더링합니다."""
    return render_template('index.html')

@app.route('/hide', methods=['POST'])
def handle_hide():
    """메시지 숨기기 요청을 처리합니다."""
    if 'image' not in request.files or 'message' not in request.form:
        flash('필수 항목(이미지, 메시지)이 누락되었습니다.', 'error')
        return redirect(url_for('index'))

    file = request.files['image']
    message = request.form['message']

    if file.filename == '' or message == '':
        flash('파일을 선택하거나 메시지를 입력해주세요.', 'error')
        return redirect(url_for('index'))

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        output_filename = 'secret_' + filename
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
        
        file.save(input_path)

        try:
            hide_message(input_path, output_path, message)
            return send_from_directory(app.config['UPLOAD_FOLDER'], output_filename, as_attachment=True)
        except (ValueError, FileNotFoundError) as e:
            flash(str(e), 'error')
            return redirect(url_for('index'))
        finally:
            # 작업 후 원본 파일 삭제
            if os.path.exists(input_path):
                os.remove(input_path)
    else:
        flash('허용되지 않는 파일 형식입니다. PNG 파일만 업로드 가능합니다.', 'error')
        return redirect(url_for('index'))

@app.route('/extract', methods=['POST'])
def handle_extract():
    """메시지 추출 요청을 처리합니다."""
    if 'image' not in request.files:
        flash('이미지 파일이 누락되었습니다.', 'error')
        return redirect(url_for('index'))

    file = request.files['image']

    if file.filename == '':
        flash('파일을 선택해주세요.', 'error')
        return redirect(url_for('index'))

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(input_path)

        try:
            secret_message = extract_message(input_path)
            return render_template('index.html', extracted_message=secret_message)
        except FileNotFoundError as e:
            flash(str(e), 'error')
            return redirect(url_for('index'))
        finally:
            # 작업 후 파일 삭제
            if os.path.exists(input_path):
                os.remove(input_path)
    else:
        flash('허용되지 않는 파일 형식입니다. PNG 파일만 업로드 가능합니다.', 'error')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
