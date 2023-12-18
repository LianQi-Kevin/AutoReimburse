import logging

from flask import Flask
from flask_cors import CORS

from apis.tax_info import info_bp
from tools.logging_utils import log_set

# init flask & CORS
app = Flask(__name__)
CORS(app)

# logging
log_set(log_level=logging.INFO, log_save=True)

# register BP
app.register_blueprint(info_bp)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
    # log_set(logging.INFO)
    #
    # for index, msg_dict in enumerate(decode_from_path("examples/发票/")):
    #     get_verify_img(msg_dict)
