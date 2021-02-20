from urllib.request import Request, urlopen
import uuid
import io
import re
from flask import request
from flask import Flask

app = Flask(__name__)
TOKEN = <your slack token>
CHANNELS = <your channels>


@app.route("/upload", methods=['POST'])
def get_frame():
    upload_file = request.files['file']
    filename = upload_file.filename
    # img = upload_file.stream.read().strip(b"\xef\xbf\xbd")
    img = re.sub(b"\xef\xbf\xbd", b'', upload_file.stream.read())
    # img = upload_file.stream.read().decode("utf-8-sig")
    print(img)
    socket_send(filename, img)
    return "success"


def socket_send(filename, img_body):
    boundary = f"--------------{uuid.uuid4()}"
    sep_boundary = b"\r\n--" + boundary.encode("ascii")
    end_boundary = sep_boundary + b"--\r\n"
    body = io.BytesIO()

    png = (
            f'\r\nContent-Disposition: form-data; name="file"; filename="{filename}"\r\n'
            + f"Content-Type: image/png\r\n\r\n"
    )
    body.write(sep_boundary)
    body.write(png.encode('ascii') + img_body)
    body.write(sep_boundary)
    title = f'\r\nContent-Disposition: form-data; name="channels"\r\n\r\n' + CHANNELS
    body.write(title.encode('ascii'))
    body.write(end_boundary)
    body = body.getvalue()

    headers = {"Content-Type": f"multipart/form-data; boundary={boundary}", "Content-Length": len(body),
               "Authorization": f"Bearer {TOKEN}", "Host": "slack.com"}

    req = Request(method="POST", url="https://slack.com/api/files.upload", data=body, headers=headers)
    # print(req.data)

    with urlopen(req) as f:
        print('Status:', f.status, f.reason)
        for k, v in f.getheaders():
            print('%s: %s' % (k, v))
        # print('Data:', f.read().decode('utf-8'))

