"""huj"""


import os


"""saved songs will be stored here:"""
save_audio_path = r'./.data/audio'

"""database with songs info will be saved under:"""
database_path = r'./.data/database'

"""host under which the webserver will run"""
host = '0.0.0.0'

"""port"""
port = os.environ['PYTIFY_PORT']

