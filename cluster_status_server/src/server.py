import flask
import glob
import json
import os
import subprocess
import threading
import time
import traceback
import umongo

# params
PORT = 80
DEBUG = True

# app and state
app = flask.Flask('API CLUSTER STATUS')

def get_mongo_collections():
    client = umongo.get_mongo_client()
    mc_cluster = client['cluster']['clusters']
    mc_cluster_status = client['cluster']['clusters_status']
    return mc_cluster, mc_cluster_status
MC_CLUSTER, MC_CLUSTER_STATUS = get_mongo_collections()

@app.route('/api/public/cluster/v1/clusters/')
def get_clusters():
    b = MC_CLUSTER.find({}, {'_id': False})
    return flask.jsonify(umongo.bson_to_json(b))

@app.route('/api/public/cluster/v1/clusters/<string:cluster_uuid>')
def get_cluster(cluster_uuid):
    b = MC_CLUSTER.find({'uuid': cluster_uuid}, {'_id': False})
    j = umongo.bson_to_json(b)
    if len(j) == 0:
        return flask.jsonify({'error': 'cluster not found'}), 404
    return flask.jsonify(j[0])

@app.route('/api/public/cluster/v1/clusters_status/')
def get_clusters_status():
    b = MC_CLUSTER_STATUS.find({}, {'_id': False})
    return flask.jsonify(umongo.bson_to_json(b))

@app.route('/api/public/cluster/v1/clusters_status/<string:cluster_uuid>')
def get_cluster_status(cluster_uuid):
    b = MC_CLUSTER_STATUS.find({'uuid': cluster_uuid}, {'_id': False})
    j = umongo.bson_to_json(b)
    if len(j) == 0:
        return flask.jsonify({'error': 'cluster not found'}), 404
    return flask.jsonify(j[0])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, debug=DEBUG)