import seaborn as sns
import numpy as np
from flask import send_file, Flask, jsonify, request
from flask_cors import CORS
import pyodbc
from ML_japan import make_chart
from pairplot_generator import pairplot
from pairplot_generator import make_chartML
from pairplot_generator import summary_describe
from pairplot_generator import fetch_data
from pairplot_generator import get_parameters
from pairplot_generator import get_model
from pairplot_generator import get_line 
from pairplot_generator import BinKPOV_Auto 
from pairplot_generator import BIN_KPOV 

from pairplot_generator import data_bin 

from pairplot_generator import BIN_KPIV 
from Data import get_ranking 


app = Flask(__name__)
cors = CORS(app)

app.add_url_rule('/api/data/<start>/<end>', 'make_tilt_plot', make_chart)
app.add_url_rule('/api/make_chartML/<model>/<line>/<start>/<end>/<selecteKPOV>/<selecteKPIV>', 'generate_heatmap', make_chartML)
app.add_url_rule('/api/pairplot/<model>/<line>/<start>/<end>/<selecteKPOV>/<selecteKPIV>', 'generate_pairplot', pairplot)
app.add_url_rule('/api/data/<model>/<line>/<start>/<end>/<selecteKPOV>/<selecteKPIV>', 'fetch_data', fetch_data)
app.add_url_rule('/api/get_ranking/<model>/<line>/<start>/<end>/<selecteKPOV>/<selecteKPIV>', 'get_ranking', get_ranking)
app.add_url_rule('/api/summary_describe/<model>/<line>/<start>/<end>/<selecteKPOV>/<selecteKPIV>', 'summary_json', summary_describe)
app.add_url_rule('/api/model', 'get_model', get_model)
app.add_url_rule('/api/line/<model>', 'get_line', get_line)
app.add_url_rule('/api/parameters', 'get_parameters', get_parameters)
app.add_url_rule('/api/BinKPOV_Auto/<model>/<selecteKPOV>', 'BinKPOV_Auto', BinKPOV_Auto)
app.add_url_rule('/api/BIN_KPOV/<model>/<line>/<start>/<end>/<selecteKPOV>/<selecteKPIV>/<minKPOV>/<maxKPOV>', 'BIN_KPOV', BIN_KPOV)
app.add_url_rule('/api/data_bin/<model>/<selecteKPIV>', 'data_bin', data_bin)
app.add_url_rule('/api/BIN_KPIV/<model>/<line>/<start>/<end>/<selecteKPOV>/<selecteKPIV>/<minKPOV>/<maxKPOV>/<support>/<confidence>', 'BIN_KPIV', BIN_KPIV)




if __name__ == '__main__':

    app.run(port=2023)
