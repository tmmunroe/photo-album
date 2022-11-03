echo "Installing external packages..."
pip install --upgrade -t layer/python -r requirements-lambda.txt

echo "Installing photo_album_models..."
cp -r photo_album_models layer/python
