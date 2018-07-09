import bluetooth
import os, random
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
import sqlite3

def findbluetooth():
	print("SEARCHING.....")
	try:
		nearby_devices = bluetooth.discover_devices(lookup_names=True)
		for i in range (len(nearby_devices)):
			print("  %s - %s" % (i+1,nearby_devices[i][1]))
	except:
		print("no device found")
	j=int(input("Select Your Bluetooth Device Or press zero to Search again..."))
	if(j==0):
		return findbluetooth()
	else:
		return nearby_devices[j-1][0]

def encrypt(key, filename):
	chunksize = 64*1024
	outputFile = "(encrypted)"+filename
	filesize = str(os.path.getsize(filename)).zfill(16)
	IV = ''

	for i in range(16):
		IV += chr(random.randint(0, 0xFF))

	encryptor = AES.new(key, AES.MODE_CBC, IV)

	with open(filename, 'rb') as infile:
		with open(outputFile, 'wb') as outfile:
			outfile.write(filesize)
			outfile.write(IV)

			while True:
				chunk = infile.read(chunksize)

				if len(chunk) == 0:
					break
				elif len(chunk) % 16 != 0:
					chunk += ' ' * (16 - (len(chunk) % 16))

				outfile.write(encryptor.encrypt(chunk))

def decrypt(key, filename):
	chunksize = 64*1024
	outputFile = filename[11:]

	with open(filename, 'rb') as infile:
		filesize = long(infile.read(16))
		IV = infile.read(16)

		decryptor = AES.new(key, AES.MODE_CBC, IV)

		with open(outputFile, 'wb') as outfile:
			while True:
				chunk = infile.read(chunksize)

				if len(chunk) == 0:
					break

				outfile.write(decryptor.decrypt(chunk))
			outfile.truncate(filesize)



def getKey(password):
	hasher = SHA256.new(password)
	return hasher.digest()


def Main():
	con = sqlite3.connect('Credentials.db')
	con.text_factory = str
	cursor = con.cursor()
	cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
	try:
		cursor.execute('''CREATE TABLE CREDENTIALS
		(ID INTEGER PRIMARY KEY    AUTOINCREMENT,
		FILENAME CHAR    NOT NULL,
		KEY      CHAR    NOT NULL);''')
	except:
		pass
	choice = raw_input("Would you like to (E)ncrypt or (D)ecrypt?: ")
	if choice == 'E':
		filename = raw_input("File to encrypt: ")
		device_mac = findbluetooth()
	 	password = raw_input("Password: ")+device_mac
		password = getKey(password)
		cursor.execute("INSERT INTO CREDENTIALS (FILENAME,KEY) \
		VALUES ( ?,? )",(filename,password,));
		con.commit()
		con.close()
		encrypt(password, filename)
		os.popen('attrib +h (encrypted)' + filename)
		os.remove(filename)
	elif choice == 'D':
	  	device_mac = findbluetooth()
		password = raw_input("Password: ")+device_mac
		password = getKey(password)
		files = cursor.execute("SELECT FILENAME FROM CREDENTIALS WHERE KEY = ?",(password,));
		files = list(files)
		for i in range(len(files)):
			print(str(i+1)+"-"+str(files[i][0]))
		fileindex = int(input())
		filename = "(encrypted)"+files[fileindex-1][0]
		con.close()
		decrypt(password, filename)
	 	os.remove(filename)
	else:
		print "No Option selected, closing..."

if __name__ == '__main__':
	Main()
