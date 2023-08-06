import requests

url = 'http://localhost:5000/api/classify'
image_file_path = 'static/uploads/download (2).jfif'

with open(image_file_path, 'rb') as f:
    files = {'image': f}
    response = requests.post(url, files=files)

if response.ok:
    result = response.json()
    print("Predicted class:", result['class'])
else:
    print("Error:", response.json())

