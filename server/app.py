import os
from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename
from flask import send_from_directory
from PIL import Image
import redis
from redis import Redis
from rq import Queue
import time
from flask import render_template
from flask import send_from_directory

UPLOAD_FOLDER = '/var/lib/photos/'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

queue = redis.StrictRedis(host='redis')
#queue = redis.StrictRedis(host='localhost', port=1234, db=0)
channel = queue.pubsub()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        # TODO save the format and send it to redis queue
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        f = open(os.path.join(app.config['UPLOAD_FOLDER'], filename), 'r')
        print(filename)

        queue.publish("image", 'start')
        filter = int(request.form.get('filter'))

        queue.publish("image", filter)
      
        for i in range(0, len(filename)):
            queue.publish("image", filename[i])

        queue.publish("image", 'stop')
        print("FINISH")
        #return redirect(url_for('uploaded_file',
        #                        filename=filename))
        if filter == 1:
            result_filename = "blur-" + filename
        elif filter == 2:
            result_filename = "sharp-" + filename
        else:
            result_filename = "sobel-" + filename

        time.sleep(4)
        return redirect(url_for('uploaded_file', filename=result_filename))

    return render_template('index.html')
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

