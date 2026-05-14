#!/usr/bin/env python3
# Electrum Seed XOR Splitter (minified) — Python 3.10+, stdlib only
# Splits Electrum segwit seed into 2 BIP-39 XOR shares (one-time pad via os.urandom)
# Requires bip39_wordlist_english.txt in same folder
# Usage: python3 electrum_seed_xor_split_mini.py
import hashlib,hmac,os,sys,unicodedata
from datetime import datetime,timezone;from pathlib import Path
H="2f5eed53a4727b4bf8880d8f3f199efc90e58503646d9ff8eff3a2ed3b24dbda"
W=[]
def lw():
 p=Path(__file__).parent/"bip39_wordlist_english.txt"
 if not p.exists():print(f"ERROR: {p} not found");sys.exit(1)
 d=p.read_text("utf-8")
 if hashlib.sha256(d.encode()).hexdigest()!=H:print("ERROR: hash mismatch");sys.exit(1)
 w=d.strip().splitlines()
 if len(w)!=2048:print("ERROR: bad wordlist");sys.exit(1)
 return w
def e2m(e):
 h=hashlib.sha256(e).digest();cs=len(e)*8//32;b=[]
 for x in e:
  for i in range(7,-1,-1):b.append((x>>i)&1)
 for i in range(7,7-cs,-1):b.append((h[0]>>i)&1)
 r=[]
 for i in range(0,len(b),11):
  v=0
  for x in b[i:i+11]:v=(v<<1)|x
  r.append(W[v])
 return r
def m2e(m):
 b=[]
 for w in m:
  idx=W.index(w)
  for i in range(10,-1,-1):b.append((idx>>i)&1)
 cs=len(m)//3;eb=b[:len(b)-cs];r=bytearray()
 for i in range(0,len(eb),8):
  v=0
  for x in eb[i:i+8]:v=(v<<1)|x
  r.append(v)
 return bytes(r)
def chk(s):
 n=unicodedata.normalize("NFKD",s)
 return hmac.digest(b"Seed version",n.encode(),hashlib.sha512).hex().startswith("100")
def xor(a,b):return bytes(x^y for x,y in zip(a,b))
def split(m):
 oe=m2e(m);ae=os.urandom(len(oe));be=xor(oe,ae)
 return e2m(ae),e2m(be)
def main():
 global W;W[:]=lw()
 print("="*60+"\n  Electrum Seed XOR Splitter\n"+"="*60)
 print("\nEnter your Electrum native segwit seed (12 or 24 words):\n")
 while True:
  raw=input("Seed: ").strip()
  if not raw:continue
  w=raw.lower().split()
  if len(w) not in(12,24):print(f"  Need 12 or 24 words, got {len(w)}");continue
  bad=[x for x in w if x not in W]
  if bad:print(f"  Unknown: {', '.join(bad)}");continue
  if not chk(" ".join(w)):
   if input("  Not Electrum segwit. Continue? (y/n): ").strip().lower()!="y":continue
  break
 a,b=split(w)
 oe=m2e(w);re=xor(m2e(a),m2e(b))
 if re!=oe:print("FATAL: verification failed");sys.exit(1)
 f=f"xor_shares_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.txt"
 with open(f,"w") as fh:
  fh.write(f"SHARE A: {' '.join(a)}\nSHARE B: {' '.join(b)}\n")
 print(f"\nShare A: {' '.join(a)}\nShare B: {' '.join(b)}")
 print(f"\nVerified. Written to: {f}")
if __name__=="__main__":main()
