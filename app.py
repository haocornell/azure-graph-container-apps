import os
import uuid
from datetime import datetime
import time

from flask import (Flask, redirect, render_template, request,
                   send_from_directory, url_for)
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from requests import RequestException

from azure.kusto.data import KustoClient, KustoConnectionStringBuilder
from azure.kusto.data.exceptions import KustoServiceError
from azure.kusto.data.helpers import dataframe_from_result_table
import pandas as pd

from azureproject.get_conn import get_conn

app = Flask(__name__, static_folder='static')
csrf = CSRFProtect(app)

# If RUNNING_IN_PRODUCTION is defined as an environment variable, then we're running on Azure
if not 'RUNNING_IN_PRODUCTION' in os.environ:
   # Local development, where we'll use environment variables.
   print("Loading config.development and environment variables from .env file.")
   app.config.from_object('azureproject.development')
else:
   # Production, we don't load environment variables from .env file but add them as environment variables in Azure.
   print("Loading config.production.")
   app.config.from_object('azureproject.production')

from azure.identity import DefaultAzureCredential

# Acquire a credential object
credential = DefaultAzureCredential()

from azure.kusto.data import KustoClient, KustoConnectionStringBuilder
from azure.identity import DefaultAzureCredential

from azure.kusto.data.helpers import dataframe_from_result_table
import pandas as pd

KUSTO_CLUSTER = "https://dtoa.eastus.kusto.windows.net/"
KUSTO_DATABASE = "Dev"
client_id = "f138a525-fc1e-467e-aacd-69b0532e5271"

kcsb = ''

if not 'RUNNING_IN_PRODUCTION' in os.environ:
   # Local development, where we'll use environment variables.
   print("Loading config.development and environment variables from .env file.")
   app.config.from_object('azureproject.development')
  
   kcsb = KustoConnectionStringBuilder.with_az_cli_authentication(KUSTO_CLUSTER)
else:
   kcsb = KustoConnectionStringBuilder.with_aad_managed_service_identity_authentication(KUSTO_CLUSTER, client_id=client_id)
#KCSB.authority_id = AAD_TENANT_ID

KUSTO_CLIENT = KustoClient(kcsb)
KUSTO_QUERY = "AzureArchLayers | take 10"

RESPONSE = KUSTO_CLIENT.execute(KUSTO_DATABASE, KUSTO_QUERY)

df = dataframe_from_result_table(RESPONSE.primary_results[0])

content = df.iloc[0].to_string()
print(content)

# Acquire a credential object
credential = DefaultAzureCredential()

authority_id = "72f988bf-86f1-41af-91ab-2d7cd011db47"
#with app.app_context():
#    app.config.update(
#        SQLALCHEMY_TRACK_MODIFICATIONS=False,
#        SQLALCHEMY_DATABASE_URI=get_conn(),
#    )

# Initialize the database connection
#db = SQLAlchemy(app)

# Enable Flask-Migrate commands "flask db init/migrate/upgrade" to work
migrate = Migrate(app)

# Create databases, if databases exists doesn't issue create
# For schema changes, run "flask db migrate"
from models import Restaurant

#with app.app_context():
#    db.create_all()
#    db.session.commit()

restaurant =  Restaurant(int(time.time()), 'Bob Grill', '1234 12th ST, Bellevue, WA', 'Nice bbq place.')

restaurants = {restaurant.id : restaurant}

@app.route('/', methods=['GET'])
def index():
    from models import Restaurant
    print('Request for index page received')
    return render_template('index.html', restaurants=restaurants.values())

@app.route('/<int:id>', methods=['GET'])
def details(id):
    return details(id,'')

def details(id, message):
    from models import Restaurant
    restaurant = restaurants[id]
    restaurant.description = ""
    return render_template('details.html', restaurant=restaurant, message=message)

@app.route('/create', methods=['GET'])
def create_restaurant():
    print('Request for add restaurant page received')
    return render_template('create_restaurant.html')

@app.route('/add', methods=['POST'])
@csrf.exempt
def add_restaurant():
    from models import Restaurant
    try:
        name = request.values.get('restaurant_name')
        street_address = request.values.get('street_address')
        description = request.values.get('description')
        if (name == "" or description == "" ):
            raise RequestException()
    except (KeyError, RequestException):
        # Redisplay the restaurant entry form.
        return render_template('create_restaurant.html', 
            message='Restaurant not added. Include at least a restaurant name and description.')
    else:

        from azure.ai.projects import AIProjectClient
	
        from azure.identity import DefaultAzureCredential

        project_connection_string = "eastus.api.azureml.ms;99b71b51-9458-4a6b-b7a2-9153eb360d42;AzureGraph;azure-dep-arch"

        project = AIProjectClient.from_connection_string(
            conn_str=project_connection_string, credential=DefaultAzureCredential()
        )

        chat = project.inference.get_chat_completions_client()
        response = chat.complete(
            model="gpt-4o",
            messages=[
              {
               "role": "system",
               "content": "You are an AI assistant that speaks like a techno punk rocker from 2350. Be cool but not too cool. Ya dig?",
              },
              {"role": "user", "content": description},
            ],
         )

        description = response.choices[0].message.content
        street_address = content
        restaurant = Restaurant(int(time.time()), name, street_address, description)
        restaurants[restaurant.id] = restaurant
        return redirect(url_for('details', id=restaurant.id))

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == '__main__':
   app.run()
