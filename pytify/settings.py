"""huj"""


import os


"""saved songs will be stored here:"""
save_audio_path = r'/var/data/audio'

"""database with songs info will be saved under:"""
database_path = r'/var/data/database'

"""host under which the webserver will run"""
host = '0.0.0.0'

"""port"""
port = os.environ.get('PYTIFY_PORT', 5001)

