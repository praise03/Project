def createCert(a):
    a[3] = str(a[3])
    ar = "+".join(a)
    ar_hash = sha256(ar.encode()).hexdigest()
    newuser = ({
        "name": a[0],
        "Matric No": a[1],
        "Course": a[2],
        "Year": a[3],
        "Hash": ar_hash
    })
    db.insert_one(newuser)
    Mktree.encryptRecord(ar)
    img = Image.open('Cert_template.png')
    qr = qrcode.QRCode(box_size=2)
    qr.add_data([str(ar_hash), Mktree.get_commitment().decode("utf-8")], optimize=0)
    qr.make()
    test = qr.make_image(fill_color="black", back_color="white").convert('RGB')

    img.paste(test, (330, 460))

    I1 = ImageDraw.Draw(img)
    font = ImageFont.truetype('font.ttf', 30)
    I1.text((288, 156), a[0], font=font, fill=(0, 0, 0))
    I1.text((288, 246), a[1], font=font, fill=(0, 0, 0))
    I1.text((268, 326), a[2], font=font, fill=(0, 0, 0))
    I1.text((348, 416), a[3], font=font, fill=(0, 0, 0))

    img.save('uploads/certs/' + a[0] + '.png')


def validateCert(roothash, certhash):
    loaded_tree = MerkleTree.loadFromFile(roothash)
    challenge = {
                    'checksum' : certhash
                }
    merkle_proof = loaded_tree.merkleProof(challenge)

    validateProof(merkle_proof)