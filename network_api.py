from flask import Flask, request, jsonify
import whitelist_handler as whitelist

app = Flask(__name__)

@app.route('/whitelist/add', methods=['POST'])
def add_whitelisted():
	data = request.get_json()
	uuid = data.get("uuid")
	filename = data.get("filename")
	
	if not filename or not uuid:
		return jsonify({"status": "failure", "message": "Missing filename or uuid"}), 400
	
	user = whitelist.create_user("N/A", "N/A", uuid, whitelist.get_minecraft_username_by_uuid(uuid))
	
	if whitelist.add_user(user, filename):
		print(f"Whitelisted {uuid} in {filename}")
		return jsonify({"status": "success", "message": f"User {uuid} added to {filename} whitelist"}), 200
	return jsonify({"status": "failure", "message": f"User {uuid} is already whitelisted in {filename}"}), 400

@app.route('/whitelist/remove', methods=['POST'])
def remove_whitelisted():
	data = request.get_json()
	uuid = data.get("uuid")
	filename = data.get("filename")
	
	if not filename or not uuid:
		return jsonify({"status": "failure", "message": "Missing filename or uuid"}), 400

	if whitelist.remove_user(uuid, filename):
		print(f"Unwhitelisted {uuid} from {filename}")
		return jsonify({"status": "success", "message": f"User {uuid} removed from {filename} whitelist"}), 200
	return jsonify({"status": "failure", "message": f"User {uuid} is not in the {filename} whitelist"}), 400

@app.route('/whitelist/check', methods=['GET'])
def check_whitelisted():
	uuid = request.args.get("uuid")
	filename = request.args.get("filename")
	
	if not filename or not uuid:
		return jsonify({"status": "failure", "message": "Missing filename or uuid"}), 400
	
	if whitelist.check_if_whitelisted(uuid, filename):
		print(f"Checked {uuid} in {filename}")
		return jsonify({"status": "success", "message": f"User {uuid} is whitelisted in {filename}"}), 200
	return jsonify({"status": "failure", "message": f"User {uuid} is not whitelisted in {filename}"}), 404

if __name__ == "__main__":
	app.run(host="0.0.0.0", port=5000)