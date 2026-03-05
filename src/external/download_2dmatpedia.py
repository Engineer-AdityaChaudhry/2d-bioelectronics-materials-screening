import os
import urllib.request

OUT = "data/external/2dmatpedia.json.gz"

# Direct source file link exposed by ColabFit (Figshare ndownloader)
URL = "https://ndownloader.figshare.com/files/26789006"

def main():
    os.makedirs("data/external", exist_ok=True)
    print(f"Downloading:\n  {URL}\n-> {OUT}")
    urllib.request.urlretrieve(URL, OUT)
    print("Done.")

if __name__ == "__main__":
    main()
