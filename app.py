from flask import Flask
from flask import request
import requests
import logging
from flask import jsonify
from requests.api import get
from flask_cors import CORS, cross_origin

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'



# User credentials
email = "utb@ormuco.com"
password = "ILOVEUTB2021"

# ID and API endpoints
project_id = "2ee7b627f154414f83ffdbbf6c78999f"
identity_endpoint_url = "https://api-acloud.ormuco.com:5000/v3"
compute_endpoint_url = "https://api-acloud.ormuco.com:8774/v2.1/2ee7b627f154414f83ffdbbf6c78999f"
image_api_url="https://api-acloud.ormuco.com:9292"
network_api_url="https://api-acloud.ormuco.com:9696"

# Global parameters
network_name = "default-network"  # Enter a valid network name
image_name = "ubuntu-18.04-amd64"  # Enter a valid image name
instance_name = "test_instanceRicardo"  # Name of the instance
key_name = None  # Enter a valid key pair name
flavor_id = 100  # Enter a valid flavor ID

logging.captureWarnings(True)


def authenticate(email, password, project_id, identity_endpoint_url):
    """
    :param username: email of the user
    :param password: password of the user
    :param project_id: ID of the user project
    :param identity_endpoint_url: url for identity endpoint
    :return: an authentication token scoped to the project
    """
    url = "{}/auth/tokens".format(identity_endpoint_url)
    headers = {"Content-Type": "application/json"}
    data = {
        "auth": {
            "identity": {
                "methods": [
                    "password"
                ],
                "password": {
                    "user": {
                        "name": email,
                        "password": password
                    }
                }
            },
            "scope": {
                "project": {
                    "id": project_id
                }
            }
        }
    }
    response = requests.post(url=url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()


def list_instances(token, compute_endpoint_url):
    """
    :param token: valid authentication token
    :param compute_endpoint_url: url of OpenStack compute endpoint
    :return: list of project instances
    """
    url = "{}/servers/detail".format(compute_endpoint_url)
    headers = {"Content-Type": "application/json",
               "X-Auth-Token": token}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


logging.captureWarnings(True)


def get_network_id(network_name, token, network_endpoint_url):
    """
    :param network_name: name of the network
    :param token: valid authentication token
    :param network_endpoint_url: url of the OpenStack network endpoint
    :return: ID of the corresponding network
    """
    url = "{}/v2.0/networks".format(network_endpoint_url)
    headers = {"Content-Type": "application/json",
               "X-Auth-Token": token}
    data = {"name": network_name}
    response = requests.get(url, headers=headers, params=data)
    response.raise_for_status()
    return response.json()["networks"][0]["id"]


def get_image_id(image_name, token, image_endpoint_url):
    """
    :param image_name: name of the image
    :param token: valid authentication token
    :param image_endpoint_url: url of the OpenStack image endpoint
    :return: ID of the corresponding image
    """
    url = "{}/v2/images".format(image_endpoint_url)
    headers = {"Content-Type": "application/json",
               "X-Auth-Token": token}
    data = {"name": image_name}
    response = requests.get(url, headers=headers, params=data)
    response.raise_for_status()
    return response.json()["images"][0]["id"]

@app.route('/server',methods=['POST'])
def create_instance():
    """
    :param token: authentication token
    :param instance_name: name of the instance to create
    :param image_id: ID of the image to use for the instance
    :param flavor_id: ID of the flavor to use for the new instance
    :param network_id: ID of the network to use for the new instance
    :param compute_endpoint_url: url of the compute API endpoint
    :return: instance created based on the given image, flavor, and network
    """

    instance_name = "test_instanceRicardo"  # Name of the instance
    key_name = "Ricardo-UTB"  # Enter a valid key pair name
    flavor_id = 100  # Enter a valid flavor ID
    authentication = authenticate(email, password, project_id, identity_endpoint_url)
    imageID=mainImages()
    networkID=mainNetwork()

    token = authentication["token"]
    url = "{}/servers".format(compute_endpoint_url)
    headers = {"Content-Type": "application/json",
               "X-Auth-Token": token["id"]}

        
    if request.method == 'POST':
        json_body =request.json
        print(json_body["name"])
        data = {
            "server" :{
                "name": json_body['name'],
                "imageRef": imageID,
                "flavorRef": flavor_id,
                "networks": [{"uuid": networkID}],
                "min_count": 1,
                "max_count": 1,
               "config_drive": True,
                "block_device_mapping_v2": [
                    {"uuid": imageID, "source_type": "image", "boot_index": 0,
                     "delete_on_termination": True}],
                "metadata": {"source_image": imageID}
            }
        }
        print(data)
        if key_name:
            data["server"]["key_name"] = key_name

        response = requests.post(url=url, headers=headers, json=data)

        response.raise_for_status()
        return response.json()["server"]

        # name =request.form['name']
    

    # key_nameF = requests.form['key_nameF']




@app.route('/images')
def mainImages():
     authentication = authenticate(email, password, project_id, identity_endpoint_url)
     token = authentication["token"]
     image = get_image_id(image_name,token["id"], image_api_url)

     return image

@app.route('/networks')
def mainNetwork():
     authentication = authenticate(email, password, project_id, identity_endpoint_url)
     token = authentication["token"]
     network = get_network_id(network_name,token["id"], network_api_url)

     return network
@app.route('/')
def main():
     authentication = authenticate(email, password, project_id, identity_endpoint_url)
     token = authentication["token"]
     instances = list_instances(token["id"], compute_endpoint_url)
     return jsonify(instances)

if __name__ == "__main__":
    try:
        app.run(debug=True)
    except:
        logging.exception("An error occured while listing instances.")
