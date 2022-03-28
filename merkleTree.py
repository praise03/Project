# import merkletools
#
# mt - MerkleTools()
#
# hex_data = '05ae04314577b2783b4be98211d1b72476c59e9c413cfb2afa2f0c68e0d93911'
# list_data = ['Some text data', 'perhaps']
#
# mt.add_leaf(hex_data)
# mt.add_leaf(list_data, True)
# print(mt.get_leaf_count())
from PIL import Image, ImageDraw, ImageFont
import qrcode
from pyzbar.pyzbar import decode
import os, secrets
from flask import Flask

app = Flask(__name__)
try:
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext('test.py')
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, picture_fn)
    i = Image.open('test.py')
    i.save(picture_path)
    # i = Image.open(form.picture.data)
    decocdeQR = decode(Image.open(picture_fn))
    decodedCert = decocdeQR[0].data.decode('ascii')
    certhash = decodedCert[2:66]
    roothash = decodedCert[70:134]
except:
    print('index error')

# if (blockchain_db.count_documents({'root_hash': roothash})):
#     loaded_tree = MerkleTree.loadFromFile('uploads/trees/' + roothash + '.json')
#     challenge = {'checksum': certhash}
#     merkle_proof = loaded_tree.merkleProof(challenge)
#
#     if (validateProof(merkle_proof)):
#         flash("Credentials Exists!!!", "success")
#         for i in database.find({'Hash': certhash}):
#             info = i
# else:
#     flash("Credentials Not Found", "danger")