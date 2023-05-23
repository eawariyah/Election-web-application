from flask import Flask, request, jsonify
import json
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

app = Flask(__name__) 

# Initializing and getting reference to Firestore database.
cred = credentials.Certificate("public/key.json")
firebase_admin.initialize_app(cred)

# Get a reference to the Firestore database
db = firestore.client()

# # create a dictionary to store voter and election data
# voters = {}
# elections = {}


# create a reference to the 'voters' and 'elections' collections in Firestore
voters_ref = db.collection('voters')
elections_ref = db.collection('elections')


# route to register a new voter
@app.route('/voters', methods=['POST'])
def register_voter():
    voter_data = request.get_json()
    voter_id = len(voters_ref.get()) + 1
    voter_data["id"] = voter_id
    voters_ref.document(str(voter_id)).set(voter_data)
    return jsonify({'message': 'New voter registered successfully', 'voter_id': voter_id})

# route to deregister a voter
@app.route('/voters/<int:voter_id>', methods=['DELETE'])
def deregister_voter(voter_id):
    voter_doc = voters_ref.document(str(voter_id))
    if voter_doc.get().exists:
        voter_doc.delete()
        return jsonify({'message': 'Voter deregistered successfully'})
    else:
        return jsonify({'error': 'Voter not found'})

# route to update voter information
@app.route('/voters/<int:voter_id>', methods=['PUT'])
def update_voter(voter_id):
    voter_doc = voters_ref.document(str(voter_id))
    if voter_doc.get().exists:
        voter_data = request.get_json()
        voter_doc.update(voter_data)
        return jsonify({'message': 'Voter information updated successfully'})
    else:
        return jsonify({'error': 'Voter not found'})

# route to get voter information
@app.route('/voters/<int:voter_id>', methods=['GET'])
def get_voter(voter_id):
    voter_doc = voters_ref.document(str(voter_id))
    if voter_doc.get().exists:
        return jsonify(voter_doc.get().to_dict())
    else:
        return jsonify({'error': 'Voter not found'})

# route to create a new election
@app.route('/elections', methods=['POST'])
def create_election():
    election_data = request.get_json()
    election_id = len(elections_ref.get()) + 1
    election_data["id"] = election_id
    elections_ref.document(str(election_id)).set(election_data)
    return jsonify({'message': 'New election created successfully', 'election_id': election_id})

# route to get election information
@app.route('/elections/<int:election_id>', methods=['GET'])
def get_election(election_id):
    election_doc = elections_ref.document(str(election_id))
    if election_doc.get().exists:
        return jsonify(election_doc.get().to_dict())
    else:
        return jsonify({'error': 'Election not found'})

# route to delete an election
@app.route('/elections/<int:election_id>', methods=['DELETE'])
def delete_election(election_id):
    election_doc = elections_ref.document(str(election_id))
    if election_doc.get().exists:
        election_doc.delete()
        return jsonify({'message': 'Election deleted successfully'})
    else:
        return jsonify({'error': 'Election not found'})

# route to cast a vote in an election
@app.route('/elections/<int:election_id>/vote', methods=['POST'])
def cast_vote(election_id):
    # get the election document from Firestore
    election_doc = elections_ref.document(str(election_id))
    if election_doc.get().exists:
        election_data = election_doc.get().to_dict()
        vote_data = request.get_json()
        voter_id = vote_data["voter_id"]
        candidate_id = vote_data["candidate_id"]
        
        # check if voter has already voted in this election
        if "voted" in election_data and voter_id in election_data["voted"]:
            return jsonify({'error': 'You have already voted in this election'})
        
        # add the vote to the election data
        if "votes" not in election_data:
            election_data["votes"] = {}
        if candidate_id not in election_data["votes"]:
            election_data["votes"][candidate_id] = 0
        election_data["votes"][candidate_id] += 1
        
        # update the 'voted' list for the voter
        if "voted" not in election_data:
            election_data["voted"] = []
        election_data["voted"].append(voter_id)
        
        # save updated election data to Firestore
        election_doc.set(election_data)
        return jsonify({'message': 'Vote cast successfully'})
    else:
        return jsonify({'error': 'Election not found'})


if __name__ == '__main__':
    app.run(debug=True)