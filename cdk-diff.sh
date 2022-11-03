echo "Generating lambda layer..."
./gen-lambda-layer.sh

echo "Running 'cdk diff'"
cdk diff