import lib__transformers
import os
from dotenv import load_dotenv
load_dotenv('.env')
from libs.lib__transformers import searchembedding
APP_PATH = os.environ['APP_PATH']

filename = APP_PATH + "datas/_contact@mikiane.com_outputsummary_20230521124159-29.txt"
lib__transformers.mailfile(filename,"michel@brightness.fr")

