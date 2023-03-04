import pandas as pd
from pymerkle import *
from hashlib import sha256
from PIL import Image, ImageDraw, ImageFont
import qrcode
from pyzbar.pyzbar import decode
from pymongo import MongoClient

client = MongoClient()
db = client.userdata.users
df = pd.read_excel('Students.xlsx')

z = []
arr = []
rem = len(df)
for i in range(len(df)):
    rem -= 1
    for j in range(len(list(df))):
        z.append(df.iloc[i, j])
    c = z
    z = []
    c[3] = str(c[3])
    a = "+".join(c)

    a_hash = sha256(a.encode()).hexdigest()

    if len(arr) < 3:
        arr.append(c)
    else:
        arr = []
        arr.append(c)
    if len(arr) == 3:
        Mktree = MerkleTree(security=False, raw_bytes=False)
        for a in arr:
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
        for a in arr:
            #             print('')
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
        with open('structure', 'w') as f:
            f.write(Mktree.__repr__())
        Mktree.export('uploads/trees/' + Mktree.get_commitment().decode("utf-8") + '.json')
if rem < 2:
    Mktree = MerkleTree(security=False, raw_bytes=False)
    for a in arr:
        print(a)
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
    with open('structure', 'w') as f:
        f.write(Mktree.__repr__())
    Mktree.export('uploads/trees/' + Mktree.get_commitment().decode("utf-8") + '.json')
    print(Mktree)


# img = Image.open('Cert_template.png')
#
# I1 = ImageDraw.Draw(img)
#
# font = ImageFont.truetype('font.ttf', 30)
# I1.text((248, 156), "Adedokun Praise", font=font,  fill=(0, 0, 0))
# I1.text((288, 246), "17/52HA013", font=font,  fill=(0, 0, 0))
# I1.text((268, 326), "Computer Science", font=font,  fill=(0, 0, 0))
# I1.text((348, 416), "2021", font=font,  fill=(0, 0, 0))
#
# img.show()

# import xlsxwriter
#
# # Create a workbook and add a worksheet.
# workbook = xlsxwriter.Workbook('Students.xlsx')
# worksheet = workbook.add_worksheet()
#
# # Some data we want to write to the worksheet.
# expenses = (
#     ['Name', 'Matric No', 'Department', 'Year'],
#     ['John Doe', '17/52HA001', 'Computer Science', '2021'],
#     ['Jane Doe',   '17/52HA002', 'Computer Science', '2021'],
#     ['Jim Doe',  '17/52HA003', 'Computer Science', '2021'],
#     ['Juliet Doe', '17/52HA004', 'Computer Science', '2021'],
#     ['Tim Cook', '17/52HA005', 'Computer Science', '2021'],
#     ['Tom Hanks',   '17/52HA006', 'Computer Science', '2021'],
#     ['Amy Tyler',  '17/52HA007', 'Computer Science', '2021'],
#     ['Rob Banks', '17/52HA008', 'Computer Science', '2021'],
# )
#
# # Start from the first cell. Rows and columns are zero indexed.
# row = 0
# col = 0
#
# # Iterate over the data and write it out row by row.
# for item, cost, c,v in (expenses):
#     worksheet.write(row, col,     item)
#     worksheet.write(row, col + 1, cost)
#     worksheet.write(row, col + 2, c)
#     worksheet.write(row, col + 3, str(v))
#     row += 1
#
#
# workbook.close()

# import pandas as pd
#
# df = pd.read_excel('Students.xlsx')
#
# z = []
# for i in range(len(df)):
#     for j in range(len(list(df))):
#         z.append(df.iloc[i,j])
#     c = z
#     z = []
#     # print(c)
#     img = Image.open('Cert_template.png')
#
#     I1 = ImageDraw.Draw(img)
#
#     font = ImageFont.truetype('font.ttf', 30)
#     I1.text((248, 156), c[0], font=font,  fill=(0, 0, 0))
#     I1.text((288, 246), c[1], font=font,  fill=(0, 0, 0))
#     I1.text((268, 326), c[2], font=font,  fill=(0, 0, 0))
#     I1.text((348, 416), str(c[3]), font=font,  fill=(0, 0, 0))
#
#     # img.save(c[1] + '.png')
#     img.show()
#     c = []


# img = Image.open('Cert_template.png')
#
# I1 = ImageDraw.Draw(img)
#
# font = ImageFont.truetype('font.ttf', 30)
# I1.text((248, 156), z[0], font=font,  fill=(0, 0, 0))
# I1.text((288, 246), z[1], font=font,  fill=(0, 0, 0))
# I1.text((268, 326), z[2], font=font,  fill=(0, 0, 0))
# I1.text((348, 416), z[3], font=font,  fill=(0, 0, 0))
#
# img.show()
