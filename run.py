import os

from app import create_app
from config import OpenGaussConfig, SQLiteConfig

use_opengauss = os.getenv("USE_OPENGauss", "true").lower() == "true"
config_class = OpenGaussConfig if use_opengauss else SQLiteConfig
app = create_app(config_class)

if __name__ == "__main__":
    host = os.getenv("FLASK_RUN_HOST", "0.0.0.0")
    port = int(os.getenv("FLASK_RUN_PORT", "5000"))
    debug = os.getenv("FLASK_DEBUG", "1") == "1"
    app.run(host=host, port=port, debug=debug, threaded=True)
