
import requests
import os

def create_dummy_image(filename):
    # simple 1x1 pixel image
    # minimal valid jpeg binary
    # FFD8 FFDB 0043 0001 ...
    # Easier to use a simple text file renamed as .txt for non-image or just base64 dummy
    # But backend checks for file signature or extensive.
    # Let's try to send a real small image or just text files if the backend allows?
    # Backend checks mime type by extension and content for identification.
    # Using a minimal 1x1 GIF is easier: GIF89a encoded.
    
    # GIF89a header + 1x1 pixel
    data = b'GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;'
    with open(filename, 'wb') as f:
        f.write(data)

def verify():
    img1 = "test_img1.gif"
    img2 = "test_img2.gif"
    create_dummy_image(img1)
    create_dummy_image(img2)
    
    url = "http://localhost:8000/api/web/identify-product"
    
    files = [
        ('files', (img1, open(img1, 'rb'), 'image/gif')),
        ('files', (img2, open(img2, 'rb'), 'image/gif'))
    ]
    
    print(f"Sending request to {url} with 2 images...")
    try:
        response = requests.post(url, files=files, timeout=30)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Multi-image upload test passed!")
        else:
            print("❌ Test failed.")
    except Exception as e:
        print(f"❌ Exception: {e}")
    finally:
        # cleanup
        try:
            os.remove(img1)
            os.remove(img2)
        except:
            pass

if __name__ == "__main__":
    verify()
