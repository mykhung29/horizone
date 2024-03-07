import pandas as pd
from Crypto.Cipher import DES
import base64

url = "https://github.com/umpirsky/country-list/raw/master/data/en/country.csv"
data = pd.read_csv(url)

filtered_data = data[data['value'].str.len() == 8]['value']

def unpad(s):
    return s.rstrip()

def giaima():
    txt = "LsmDvf9t1pLPn+NZ99+cVx+V1ROl2/9KNqk9PLTe5uRii/aNc/X3tw=="
    txt = base64.b64decode(txt)
    for key in filtered_data:
        keyy = key.encode("utf8")[:8]
        cipher = DES.new(keyy, DES.MODE_ECB)
        detxt = unpad(cipher.decrypt(txt))
        print("Key:", key, " Decrypted Text:", detxt)

giaima()
